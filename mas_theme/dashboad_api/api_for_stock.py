import frappe

@frappe.whitelist()
def get_pending_complete_counts(from_date=None, to_date=None):
    conditions_se = []
    conditions_mr = []
    values = {}

    # ---------- Date filters ----------
    if from_date:
        conditions_se.append("posting_date >= %(from_date)s")
        conditions_mr.append("transaction_date >= %(from_date)s")
        values["from_date"] = from_date

    if to_date:
        conditions_se.append("posting_date <= %(to_date)s")
        conditions_mr.append("transaction_date <= %(to_date)s")
        values["to_date"] = to_date

    se_condition_sql = " AND ".join(conditions_se)
    mr_condition_sql = " AND ".join(conditions_mr)

    se_where = f" AND {se_condition_sql}" if se_condition_sql else ""
    mr_where = f" AND {mr_condition_sql}" if mr_condition_sql else ""

    # ---------- Stock Entry (Material Issue) ----------
    se = frappe.db.sql(f"""
        SELECT
            SUM(CASE WHEN docstatus = 0 THEN 1 ELSE 0 END) AS pending,
            SUM(CASE WHEN docstatus = 1 THEN 1 ELSE 0 END) AS complete,
            SUM(CASE WHEN docstatus != 2 THEN 1 ELSE 0 END) AS not_cancelled
        FROM `tabStock Entry`
        WHERE purpose = 'Material Issue'
        {se_where}
    """, values, as_dict=True)[0]

    # ---------- Material Request (Purchase) ----------
    mr = frappe.db.sql(f"""
        SELECT
            SUM(CASE WHEN docstatus = 0 THEN 1 ELSE 0 END) AS pending,
            SUM(CASE WHEN docstatus = 1 THEN 1 ELSE 0 END) AS complete,
            SUM(CASE WHEN docstatus != 2 THEN 1 ELSE 0 END) AS not_cancelled
        FROM `tabMaterial Request`
        WHERE material_request_type = 'Purchase'
        {mr_where}
    """, values, as_dict=True)[0]

    # ---------- Combine values ----------
    return {
        "pending": (se.pending or 0) + (mr.pending or 0),
        "complete": (se.complete or 0) + (mr.complete or 0),
        "not_cancelled": (se.not_cancelled or 0) + (mr.not_cancelled or 0),
        "se": se,
        "mr": mr
    }



@frappe.whitelist()
def get_material_issue_vehicle_avg(from_date=None, to_date=None):
    conditions = ""
    values = {}

    if from_date:
        conditions += " AND se.posting_date >= %(from_date)s"
        values["from_date"] = from_date

    if to_date:
        conditions += " AND se.posting_date <= %(to_date)s"
        values["to_date"] = to_date

    query = f"""
        SELECT
            SUM(sed.amount) AS total_amount,
            SUM(sed.amount) / COUNT(DISTINCT sed.custom_vehicle) AS amount_per_vehicle
        FROM `tabStock Entry` se
        JOIN `tabStock Entry Detail` sed
            ON se.name = sed.parent
        WHERE se.purpose = 'Material Issue'
        AND se.docstatus = 1
        AND sed.custom_vehicle IS NOT NULL
        AND sed.custom_vehicle != ''
        {conditions}
    """

    data = frappe.db.sql(query, values, as_dict=True)

    return data[0] if data else {
        "total_amount": 0,
        "amount_per_vehicle": 0
    }



@frappe.whitelist()
def get_pending_complete_counts_datewise(from_date=None, to_date=None):
    conditions = []
    values = {}

    if from_date:
        conditions.append("date >= %(from_date)s")
        values["from_date"] = from_date

    if to_date:
        conditions.append("date <= %(to_date)s")
        values["to_date"] = to_date

    where_clause = " AND " + " AND ".join(conditions) if conditions else ""

    query = f"""
        SELECT
            date,
            SUM(pending) AS pending,
            SUM(complete) AS complete,
            SUM(not_cancelled) AS not_cancelled
        FROM (
            -- Stock Entry (Material Issue)
            SELECT
                posting_date AS date,
                SUM(CASE WHEN docstatus = 0 THEN 1 ELSE 0 END) AS pending,
                SUM(CASE WHEN docstatus = 1 THEN 1 ELSE 0 END) AS complete,
                SUM(CASE WHEN docstatus != 2 THEN 1 ELSE 0 END) AS not_cancelled
            FROM `tabStock Entry`
            WHERE purpose = 'Material Issue'
            GROUP BY posting_date

            UNION ALL

            -- Material Request (Purchase)
            SELECT
                transaction_date AS date,
                SUM(CASE WHEN docstatus = 0 THEN 1 ELSE 0 END) AS pending,
                SUM(CASE WHEN docstatus = 1 THEN 1 ELSE 0 END) AS complete,
                SUM(CASE WHEN docstatus != 2 THEN 1 ELSE 0 END) AS not_cancelled
            FROM `tabMaterial Request`
            WHERE material_request_type = 'Purchase'
            GROUP BY transaction_date
        ) t
        WHERE 1=1
        {where_clause}
        GROUP BY date
        ORDER BY date
    """

    return frappe.db.sql(query, values, as_dict=True)





@frappe.whitelist()
def get_item_shortage_summary():
    query = """
        SELECT
            mri.item_code,
            i.item_name,
            SUM(mri.qty) AS required_qty,
            IFNULL(SUM(b.actual_qty), 0) AS stock_in_hand,
            (SUM(mri.qty) - IFNULL(SUM(b.actual_qty),0)) AS shortage_qty
        FROM `tabMaterial Request Item` mri
        JOIN `tabMaterial Request` mr ON mr.name = mri.parent
        JOIN `tabItem` i ON i.item_code = mri.item_code
        LEFT JOIN `tabBin` b ON b.item_code = mri.item_code
        WHERE mr.docstatus = 1
        AND mr.status != 'Stopped'
        GROUP BY mri.item_code
        HAVING shortage_qty > 0
        ORDER BY shortage_qty DESC
    """
    return frappe.db.sql(query, as_dict=True)


@frappe.whitelist()
def get_material_transfer_scrap_draft():
    """
    Returns Material Transfer Stock Entries with:
    - Draft status (docstatus=0)
    - Custom vehicle not null
    - Target warehouse 'Scrap - IVKJV'
    """

    query = """
        SELECT
            sed.description,
            se.remarks,
            se.posting_date,
            se.owner,
            sed.amount
        FROM `tabStock Entry` se
        JOIN `tabStock Entry Detail` sed
            ON se.name = sed.parent
        WHERE se.purpose = 'Material Transfer'
        AND se.docstatus = 0
        AND sed.custom_vehicle IS NOT NULL
        AND sed.custom_vehicle != ''
        AND sed.t_warehouse = 'Scrap - IVKJV'
        ORDER BY se.posting_date DESC
    """

    return frappe.db.sql(query, as_dict=True)
