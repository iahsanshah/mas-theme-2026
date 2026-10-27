import frappe
from frappe.utils import add_days, nowdate, getdate

# @frappe.whitelist()
# def get_fuel_sum(from_date=None, to_date=None):
#     conditions = ""
#     values = {}

#     if from_date and to_date or tehsil:
#         conditions = "WHERE date BETWEEN %(from_date)s AND %(to_date)s"
#         values = {"from_date": from_date, "to_date": to_date}

#     total = frappe.db.sql(f"""
#         SELECT SUM(fuel_qty)
#         FROM `tabDaily Fuel Log`
#         {conditions}
#     """, values)[0][0] or 0

#     return total
@frappe.whitelist()
def get_fuel_sum(from_date=None, to_date=None, tehsil=None):
    conditions = []
    values = {}

    if from_date and to_date:
        conditions.append("date BETWEEN %(from_date)s AND %(to_date)s")
        values.update({"from_date": from_date, "to_date": to_date})

    if tehsil:
        conditions.append("tehsil = %(tehsil)s")
        values["tehsil"] = tehsil

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    total = frappe.db.sql(f"""
        SELECT COALESCE(SUM(fuel_qty), 0)
        FROM `tabDaily Fuel Log`
        {where_clause}
    """, values)[0][0]

    return total


@frappe.whitelist()
def get_external_em(from_date=None, to_date=None):
    """Return total fuel_qty from Daily Fuel Log with optional date filters."""
    conditions = ""
    values = {}

    if from_date and to_date:
        conditions = "WHERE date BETWEEN %(from_date)s AND %(to_date)s"
        values = {"from_date": from_date, "to_date": to_date}

    total = frappe.db.sql(f"""
        SELECT SUM(present)
        FROM `tabExternal Employee Attendance`
        {conditions}
    """, values)[0][0] or 0

    return total





@frappe.whitelist()
def get_total_waste(from_date=None, to_date=None, tehsil=None):
    conditions = []
    values = {}

    # Apply date filter
    if from_date and to_date:
        conditions.append("date BETWEEN %(from_date)s AND %(to_date)s")
        values.update({"from_date": from_date, "to_date": to_date})

    # Apply tehsil filter
    if tehsil:
        conditions.append("tehsil = %(tehsil)s")
        values["tehsil"] = tehsil

    # Join conditions properly
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    total = frappe.db.sql(f"""
        SELECT COALESCE(SUM(net_weight) / 1000, 0)
        FROM `tabVehicle Visit Details`
        {where_clause}
    """, values)[0][0]

    return total




@frappe.whitelist()
def total_get_vehicle(from_date=None, to_date=None):
    """Return total fuel_qty from Daily Fuel Log with optional date filters."""
    conditions = ""
    values = {}

    if from_date and to_date:
        conditions = "WHERE date BETWEEN %(from_date)s AND %(to_date)s"
        values = {"from_date": from_date, "to_date": to_date}

    total = frappe.db.sql(f"""
        SELECT COUNT(name)
        FROM `tabVehicle`
        
    """, values)[0][0] or 0

    return total


# @frappe.whitelist()
# def total_target_tonange(from_date=None, to_date=None):
#     yesterday = add_days(nowdate(), -1)
#     from_date = getdate(from_date or yesterday)
#     to_date = getdate(to_date or yesterday)

#     total_tonnage = frappe.db.sql("""
#         SELECT SUM(custom_tonnage)
#         FROM `tabLocation`
#     """)[0][0] or 0

#     working_days = 0
#     current_date = from_date
#     while current_date <= to_date:
#         if current_date.weekday() != 6:
#             working_days += 1
#         current_date = add_days(current_date, 1)

#     total_target = total_tonnage * working_days

#     return total_target
@frappe.whitelist()
def total_target_tonange(from_date=None, to_date=None, tehsil=None):
    from frappe.utils import add_days, nowdate, getdate
    import frappe

    # Default date setup
    yesterday = add_days(nowdate(), -1)
    from_date = getdate(from_date or yesterday)
    to_date = getdate(to_date or yesterday)

    # Filter by tehsil (Location.name)
    conditions = ""
    values = {}

    if tehsil:
        conditions = "WHERE name = %(tehsil)s"
        values["tehsil"] = tehsil

    # Get total daily target tonnage from Location
    total_tonnage = frappe.db.sql(f"""
        SELECT COALESCE(SUM(custom_tonnage), 0)
        FROM `tabLocation`
        {conditions}
    """, values)[0][0] or 0

    # Count working days (excluding Sundays)
    working_days = 0
    current_date = from_date
    while current_date <= to_date:
        if current_date.weekday() != 6:  # 6 = Sunday
            working_days += 1
        current_date = add_days(current_date, 1)

    total_target = total_tonnage * working_days

    return total_target





@frappe.whitelist()
def get_net_target_tonange(from_date=None, to_date=None, tehsil=None):
    total_target = total_target_tonange(from_date, to_date,tehsil)
    total_waste = get_total_waste(from_date, to_date,tehsil)
    net_total =   total_waste - total_target

    return net_total






@frappe.whitelist()
def get_active_vehicles(from_date=None, to_date=None):
    conditions = ""
    values = {}

    if from_date and to_date:
        conditions = "WHERE date BETWEEN %(from_date)s AND %(to_date)s"
        values = {"from_date": from_date, "to_date": to_date}

    total = frappe.db.sql(f"""
        SELECT COUNT(*) 
        FROM (
            SELECT DISTINCT registration_number, date
            FROM `tabVehicle Live State`
            {conditions}
        ) AS unique_visits
    """, values)[0][0] or 0

    return total





@frappe.whitelist()
def get_inactive(from_date=None, to_date=None):
    conditions = ""
    values = {}

    if from_date and to_date:
        conditions = "WHERE date BETWEEN %(from_date)s AND %(to_date)s"
        values = {"from_date": from_date, "to_date": to_date}

    total_inactive = frappe.db.sql(f"""
        SELECT COUNT(v.name)
        FROM `tabVehicle` v
        WHERE v.name NOT IN (
            SELECT DISTINCT registration_number
            FROM `tabVehicle Live State`
            {conditions}
        )
    """, values)[0][0] or 0

    return total_inactive



@frappe.whitelist()
def get_diesel(from_date=None, to_date=None, tehsil=None):
    conditions = ["fuel_type IN ('Diesel')"]
    values = {}

    if from_date and to_date:
        conditions.append("date BETWEEN %(from_date)s AND %(to_date)s")
        values.update({"from_date": from_date, "to_date": to_date})

    if tehsil:
        conditions.append("tehsil = %(tehsil)s")
        values["tehsil"] = tehsil

    where_clause = "WHERE " + " AND ".join(conditions)

    total = frappe.db.sql(f"""
        SELECT SUM(fuel_qty)
        FROM `tabDaily Fuel Log`
        {where_clause}
    """, values)[0][0] or 0

    return total


@frappe.whitelist()
def get_petrol(from_date=None, to_date=None , tehsil=None):
    conditions = ["fuel_type IN ('Petrol')"]
    values = {}

    if from_date and to_date:
        conditions.append("date BETWEEN %(from_date)s AND %(to_date)s")
        values.update({"from_date": from_date, "to_date": to_date})

    if tehsil:
        conditions.append("tehsil = %(tehsil)s")
        values["tehsil"] = tehsil

    where_clause = "WHERE " + " AND ".join(conditions)

    total = frappe.db.sql(f"""
        SELECT SUM(fuel_qty)
        FROM `tabDaily Fuel Log`
        {where_clause}
    """, values)[0][0] or 0

    return total

@frappe.whitelist()
def get_fuel(from_date=None, to_date=None,tehsil=None):
    conditions = ["fuel_type IN ('Fuel')"]
    values = {}

    if from_date and to_date:
        conditions.append("date BETWEEN %(from_date)s AND %(to_date)s")
        values.update({"from_date": from_date, "to_date": to_date})

    if tehsil:
        conditions.append("tehsil = %(tehsil)s")
        values["tehsil"] = tehsil

    where_clause = "WHERE " + " AND ".join(conditions)

    total = frappe.db.sql(f"""
        SELECT SUM(fuel_qty)
        FROM `tabDaily Fuel Log`
        {where_clause}
    """, values)[0][0] or 0

    return total


@frappe.whitelist()
def get_milage(from_date=None, to_date=None):
    conditions = ""
    values = {}

    if from_date and to_date:
        conditions = "WHERE date BETWEEN %(from_date)s AND %(to_date)s"
        values = {"from_date": from_date, "to_date": to_date}

    total = frappe.db.sql(f"""
        SELECT 
            SUM(max_mileage) AS total_mileage
        FROM (
            SELECT 
                vehicle, 
                date, 
                MAX(mileage) AS max_mileage
            FROM `tabVehicle Live State`
            {conditions}
            GROUP BY vehicle, date
        ) AS t
    """, values)[0][0] or 0

    return total


# @frappe.whitelist()
# def get_milage(from_date=None, to_date=None):
#     conditions = ""
#     values = {}

#     if from_date and to_date:
#         conditions = "WHERE date BETWEEN %(from_date)s AND %(to_date)s"
#         values = {"from_date": from_date, "to_date": to_date}

#     total = frappe.db.sql(f"""
#         SELECT SUM(mileage)
#         FROM `tabVehicle Live State`
#         {conditions}
#     """, values)[0][0] or 0

#     return total

@frappe.whitelist()
def get_working_hours(from_date=None, to_date=None):
    """Return total fuel_qty from Daily Fuel Log with optional date filters."""
    conditions = ""
    values = {}

    if from_date and to_date:
        conditions = "WHERE date BETWEEN %(from_date)s AND %(to_date)s"
        values = {"from_date": from_date, "to_date": to_date}

    total = frappe.db.sql(f"""
        SELECT SUM(working_hours)/60
        FROM `tabVehicle Live State`
        {conditions}
    """, values)[0][0] or 0

    return total



@frappe.whitelist()
def get_fuel_comparison(from_date=None, to_date=None):
    diesel = frappe.db.sql("""
        SELECT SUM(fuel_qty) FROM `tabDaily Fuel Log`
        WHERE fuel_type='Diesel' AND date BETWEEN %s AND %s
    """, (from_date, to_date))[0][0] or 0

    petrol = frappe.db.sql("""
        SELECT SUM(fuel_qty) FROM `tabDaily Fuel Log`
        WHERE fuel_type='Petrol' AND date BETWEEN %s AND %s
    """, (from_date, to_date))[0][0] or 0

    total = diesel + petrol
    return {"diesel": diesel, "petrol": petrol, "total": total}



# @frappe.whitelist(allow_guest=True)
# def get_dashboard_data(from_date=None, to_date=None):
#     if from_date:
#         from_date = frappe.utils.getdate(from_date)
#     if to_date:
#         to_date = frappe.utils.getdate(to_date)

#     conditions = ""
#     values = {}

#     if from_date and to_date:
#         conditions = "WHERE date BETWEEN %(from_date)s AND %(to_date)s"
#         values = {"from_date": from_date, "to_date": to_date}

#     data = frappe.db.sql(f"""
#         SELECT 
#             date,
#             SUM(fuel_qty) AS total_fuel
#         FROM `tabDaily Fuel Log`
#         {conditions}
#         GROUP BY date
#         ORDER BY date
#     """, values, as_dict=True)

#     total_fuel = sum(d.get("total_fuel", 0) for d in data)

#     # Return response
#     return {
#         "fuel_by_date": data,
#         "total_fuel_qty": total_fuel
#     }
# import frappe
# from frappe.utils import getdate, add_days, nowdate

# @frappe.whitelist(allow_guest=True)
# def get_dashboard_data(from_date=None, to_date=None,tehsil=None):
#     """Return complete dashboard data (totals + date-wise breakdowns)."""

#     # ------------------ Parse Dates ------------------
#     if from_date:
#         from_date = getdate(from_date)
#     if to_date:
#         to_date = getdate(to_date)

#     # Helper to build date filter dynamically
#     def date_filter(field="date"):
#         if from_date and to_date:
#             return f"WHERE {field} BETWEEN %(from_date)s AND %(to_date)s", {
#                 "from_date": from_date,
#                 "to_date": to_date,
#             }
#         return "", {}

#     # ------------------ Fuel Data ------------------
#     conditions, values = date_filter("date")
#     fuel_by_date = frappe.db.sql(f"""
#         SELECT date, SUM(fuel_qty) AS total_fuel
#         FROM `tabDaily Fuel Log`
#         {conditions}
#         GROUP BY date
#         ORDER BY date
#     """, values, as_dict=True)

#     total_fuel_qty = sum(d.get("total_fuel", 0) for d in fuel_by_date)

#     # ------------------ Waste Data ------------------
#     waste_conditions, waste_values = date_filter("date")
#     waste_by_date = frappe.db.sql(f"""
#         SELECT date, SUM(net_weight) / 1000 AS waste_total
#         FROM `tabVehicle Visit Details`
#         {waste_conditions}
#         GROUP BY date
#         ORDER BY date
#     """, waste_values, as_dict=True)

#     total_waste_tons = sum(d.get("waste_total", 0) for d in waste_by_date)

#     # ------------------ External Employee Attendance ------------------
#     emp_conditions, emp_values = date_filter("date")
#     external_by_date = frappe.db.sql(f"""
#         SELECT date, SUM(present) AS total_present
#         FROM `tabExternal Employee Attendance`
#         {emp_conditions}
#         GROUP BY date
#         ORDER BY date
#     """, emp_values, as_dict=True)

#     external_employees_present = sum(d.get("total_present", 0) for d in external_by_date)

#     # ------------------ Mileage Data ------------------
#     mil_conditions, mil_values = date_filter("date")
#     mileage_by_date = frappe.db.sql(f"""
#         SELECT date, SUM(mileage) AS total_mileage
#         FROM `tabVehicle Live State`
#         {mil_conditions}
#         GROUP BY date
#         ORDER BY date
#     """, mil_values, as_dict=True)

#     mileage_total = sum(d.get("total_mileage", 0) for d in mileage_by_date)

#     # ------------------ Working Hours ------------------
#     hours_by_date = frappe.db.sql(f"""
#         SELECT date, SUM(working_hours) AS total_hours
#         FROM `tabVehicle Live State`
#         {mil_conditions}
#         GROUP BY date
#         ORDER BY date
#     """, mil_values, as_dict=True)

#     working_hours_total = sum(d.get("total_hours", 0) for d in hours_by_date)

#     # ------------------ Vehicle Counts ------------------
#     total_vehicles = frappe.db.count("Vehicle")

#     active_count = frappe.db.sql(f"""
#         SELECT COUNT(DISTINCT registration_number)
#         FROM `tabVehicle Live State`
#         {mil_conditions}
#     """, mil_values)[0][0] or 0

#     inactive_count = total_vehicles - active_count

#     # ------------------ Fuel Breakdown ------------------
#     def fuel_sum(ftype):
#         f_cond = "WHERE fuel_type=%(fuel_type)s"
#         params = {"fuel_type": ftype}
#         if from_date and to_date:
#             f_cond += " AND date BETWEEN %(from_date)s AND %(to_date)s"
#             params.update({"from_date": from_date, "to_date": to_date})
#         return frappe.db.sql(f"""
#             SELECT SUM(fuel_qty)
#             FROM `tabDaily Fuel Log`
#             {f_cond}
#         """, params)[0][0] or 0

#     diesel = fuel_sum("Diesel")
#     petrol = fuel_sum("Petrol")
#     fuel_other = fuel_sum("Fuel")
#     total_fuel_breakdown = diesel + petrol + fuel_other

#     # ------------------ Target & Net Tonnage ------------------
#     yesterday = add_days(nowdate(), -1)
#     from_d = getdate(from_date or yesterday)
#     to_d = getdate(to_date or yesterday)

#     tonnage = frappe.db.sql("SELECT SUM(custom_tonnage) FROM `tabLocation`")[0][0] or 0

#     # Calculate working days (exclude Sundays)
#     working_days = 0
#     current = from_d
#     while current <= to_d:
#         if current.weekday() != 6:
#             working_days += 1
#         current = add_days(current, 1)

#     target_tonnage = tonnage * working_days
#     net_target_tonnage = target_tonnage - total_waste_tons

#     # ------------------ Final Response ------------------
#     return {
#         # Date-wise charts
#         "fuel_by_date": fuel_by_date,
#         "waste_by_date": waste_by_date,
#         "external_by_date": external_by_date,
#         "mileage_by_date": mileage_by_date,
#         "hours_by_date": hours_by_date,

#         # Totals
#         "total_fuel_qty": total_fuel_qty,
#         "total_waste_tons": total_waste_tons,
#         "external_employees_present": external_employees_present,
#         "mileage_total": mileage_total,
#         "working_hours_total": working_hours_total,
#         "total_vehicles": total_vehicles,
#         "active_vehicles": active_count,
#         "inactive_vehicles": inactive_count,
#         "diesel": diesel,
#         "petrol": petrol,
#         "fuel_other": fuel_other,
#         "total_fuel_breakdown": total_fuel_breakdown,
#         "target_tonnage": target_tonnage,
#         "net_target_tonnage": net_target_tonnage,
#     }
import frappe
from frappe.utils import getdate, add_days, nowdate

@frappe.whitelist()
def get_dashboard_data(from_date=None, to_date=None, tehsil=None):
    def make_conditions(date_field="date"):
        conditions = []
        params = {}

        if from_date and to_date:
            conditions.append(f"{date_field} BETWEEN %(from_date)s AND %(to_date)s")
            params["from_date"] = from_date
            params["to_date"] = to_date

        if tehsil:
            conditions.append("tehsil = %(tehsil)s")  # Adjust if field is custom_tehsil
            params["tehsil"] = tehsil

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        return where_clause, params

    # ------------------ Fuel Data ------------------
    fuel_where, fuel_params = make_conditions("date")
    fuel_by_date = frappe.db.sql(f"""
        SELECT
            date,
            tehsil,
            SUM(fuel_qty) AS total_fuel
        FROM `tabDaily Fuel Log`
        {fuel_where}
        GROUP BY date, tehsil
        ORDER BY date
    """, fuel_params, as_dict=True)

    # ------------------ Waste Data ------------------
    waste_where, waste_params = make_conditions("date")
    waste_by_date = frappe.db.sql(f"""
        SELECT date, SUM(net_weight)/1000 AS waste_total
        FROM `tabVehicle Visit Details`
        {waste_where}
        GROUP BY date
        ORDER BY date
    """, waste_params, as_dict=True)
    total_waste_tons = sum(d.get("waste_total", 0) for d in waste_by_date)

    # ------------------ External Employee Attendance ------------------
    # emp_where, emp_params = make_conditions("date")
    # external_by_date = frappe.db.sql(f"""
    #     SELECT date, SUM(present) AS total_present
    #     FROM `tabExternal Employee Attendance`
    #     {emp_where}
    #     GROUP BY date
    #     ORDER BY date
    # """, emp_params, as_dict=True)
    # external_employees_present = sum(d.get("total_present", 0) for d in external_by_date)

    # ------------------ Mileage Data ------------------
    mil_where, mil_params = make_conditions("date")
    mileage_by_date = frappe.db.sql(f"""
        SELECT date, SUM(mileage) AS total_mileage
        FROM `tabVehicle Live State`
        {mil_where}
        GROUP BY date
        ORDER BY date
    """, mil_params, as_dict=True)
    mileage_total = sum(d.get("total_mileage", 0) for d in mileage_by_date)

    # ------------------ Working Hours ------------------
    hours_by_date = frappe.db.sql(f"""
        SELECT date, SUM(working_hours)/60 AS total_hours
        FROM `tabVehicle Live State`
        {mil_where}
        GROUP BY date
        ORDER BY date
    """, mil_params, as_dict=True)
    working_hours_total = sum(d.get("total_hours", 0) for d in hours_by_date)

    # ------------------ Vehicle Counts ------------------
    total_vehicles = frappe.db.count("Vehicle")
    active_count = frappe.db.sql(f"""
        SELECT COUNT(DISTINCT registration_number)
        FROM `tabVehicle Live State`
        {mil_where}
    """, mil_params)[0][0] or 0
    inactive_count = total_vehicles - active_count

    # ------------------ Fuel Breakdown ------------------
    def fuel_sum(ftype):
        cond, vals = make_conditions("date")
        cond = f"{cond} AND fuel_type = %(fuel_type)s" if cond else "WHERE fuel_type = %(fuel_type)s"
        vals["fuel_type"] = ftype
        return frappe.db.sql(f"""
            SELECT SUM(fuel_qty)
            FROM `tabDaily Fuel Log`
            {cond}
        """, vals)[0][0] or 0

    diesel = fuel_sum("Diesel")
    petrol = fuel_sum("Petrol")
    fuel_other = fuel_sum("Fuel")
    total_fuel_breakdown = diesel + petrol + fuel_other

    # ------------------ Target & Net Tonnage ------------------
    yesterday = add_days(nowdate(), -1)
    from_d = getdate(from_date or yesterday)
    to_d = getdate(to_date or yesterday)

    tonnage = frappe.db.sql("SELECT SUM(custom_tonnage) FROM `tabLocation`")[0][0] or 0

    working_days = 0
    current = from_d
    while current <= to_d:
        if current.weekday() != 6:
            working_days += 1
        current = add_days(current, 1)

    target_tonnage = tonnage * working_days
    net_target_tonnage = target_tonnage - total_waste_tons

    # ------------------ Final Response ------------------
    return {
        "fuel_by_date": fuel_by_date,
        "waste_by_date": waste_by_date,
        # "external_by_date": external_by_date,
        "mileage_by_date": mileage_by_date,
        "hours_by_date": hours_by_date,
        "total_waste_tons": total_waste_tons,
        # "external_employees_present": external_employees_present,
        "mileage_total": mileage_total,
        "working_hours_total": working_hours_total,
        "total_vehicles": total_vehicles,
        "active_vehicles": active_count,
        "inactive_vehicles": inactive_count,
        "diesel": diesel,
        "petrol": petrol,
        "fuel_other": fuel_other,
        "total_fuel_breakdown": total_fuel_breakdown,
        "target_tonnage": target_tonnage,
        "net_target_tonnage": net_target_tonnage,
    }


# # finance-dashboard
# import frappe
# from frappe.utils import flt

# @frappe.whitelist(allow_guest=True)
# def get_pnl_by_heads(from_date=None, to_date=None):
#     if not from_date or not to_date:
#         frappe.throw("Please provide from_date and to_date")

#     # Get all Income accounts
#     income_accounts = frappe.db.sql("""
#         SELECT name, parent_account
#         FROM `tabAccount`
#         WHERE account_type='Income' AND is_group=0
#     """, as_dict=1)

#     # Get all Expense accounts
#     expense_accounts = frappe.db.sql("""
#         SELECT name, parent_account
#         FROM `tabAccount`
#         WHERE account_type='Expense' AND is_group=0
#     """, as_dict=1)

#     income_summary = []
#     for acc in income_accounts:
#         total = flt(frappe.db.sql("""
#             SELECT SUM(credit - debit) 
#             FROM `tabGL Entry`
#             WHERE account=%s AND posting_date BETWEEN %s AND %s
#         """, (acc.name, from_date, to_date))[0][0] or 0)
#         if total != 0:
#             income_summary.append({
#                 "account": acc.name,
#                 "parent_account": acc.parent_account,
#                 "amount": total
#             })

#     expense_summary = []
#     for acc in expense_accounts:
#         total = flt(frappe.db.sql("""
#             SELECT SUM(debit - credit) 
#             FROM `tabGL Entry`
#             WHERE account=%s AND posting_date BETWEEN %s AND %s
#         """, (acc.name, from_date, to_date))[0][0] or 0)
#         if total != 0:
#             expense_summary.append({
#                 "account": acc.name,
#                 "parent_account": acc.parent_account,
#                 "amount": total
#             })

#     return {"income": income_summary, "expense": expense_summary}
# File: fleet_igl/api.py
import frappe
from erpnext.accounts.report.profit_and_loss_statement.profit_and_loss_statement import execute
from erpnext.accounts.utils import get_fiscal_year

@frappe.whitelist()
def get_expense_dashboard(company=None, tehsil=None, fiscal_year=None):
    if not company:
        return {"error": "Company is required"}

    # Default fiscal year
    if not fiscal_year:
        fiscal_year = "2025-2026"

    # Compute fiscal year start and end dates
    fy_start_year = fiscal_year.split("-")[0]
    fy_start, fy_end = get_fiscal_year(f"{fy_start_year}-01-01", company=company)[1:3]

    # Build filters including mandatory from_date and to_date
    filters = frappe._dict({
        "company": company,
        "from_fiscal_year": fy_start_year,
        "to_fiscal_year": fy_start_year,
        "periodicity": "Monthly",
        "from_date": fy_start,  # Mandatory
        "to_date": fy_end,      # Mandatory
        "cost_center": tehsil if tehsil else None
    })

    # Call ERPNext P&L execute
    columns, data, message, chart = execute(filters)

    expense_list = []
    income_list = []

    for row in data:
        if row.get("account_type") == "Expense":
            expense_list.append({
                "account": row.get("account"),
                "amount": row.get("total", 0)
            })
        if row.get("account_type") == "Income":
            income_list.append({
                "account": row.get("account"),
                "amount": row.get("total", 0)
            })

    return {
        "income": income_list,
        "expense": expense_list
    }



