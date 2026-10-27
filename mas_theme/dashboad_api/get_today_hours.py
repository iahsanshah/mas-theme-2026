# import frappe
# from frappe.utils import now_datetime, getdate, get_first_day, get_last_day

# @frappe.whitelist()
# def get_today_hours():
#     user = frappe.session.user
#     employee = frappe.db.get_value("Employee", {"user_id": user}, "name")

#     if not employee:
#         return {"hours": 0, "late_count": 0}

#     today = getdate()
#     shift_start = "09:00:00"

#     shift_assignment = frappe.db.sql("""
#         SELECT shift_type
#         FROM `tabShift Assignment`
#         WHERE employee = %s
#         AND %s BETWEEN start_date AND end_date
#         LIMIT 1
#     """, (employee, today), as_dict=True)

#     if shift_assignment:
#         shift_type = shift_assignment[0].shift_type
#         shift_start = frappe.db.get_value("Shift Type", shift_type, "start_time") or "09:00:00"

#     # ------------------------------------
#     # 2) FETCH TODAY CHECKINS (Datetime field)
#     # ------------------------------------
#     logs = frappe.db.sql("""
#         SELECT time, log_type
#         FROM `tabEmployee Checkin`
#         WHERE employee = %s
#         AND DATE(time) = %s
#         ORDER BY time ASC
#     """, (employee, today), as_dict=True)

#     total_seconds = 0
#     last_in = None

#     for log in logs:
#         if log.log_type == "IN":
#             last_in = log.time
#         elif log.log_type == "OUT" and last_in:
#             diff = (log.time - last_in).total_seconds()
#             if diff > 0:
#                 total_seconds += diff
#             last_in = None

#     # Last IN without OUT = count until now
#     if last_in:
#         diff = (now_datetime() - last_in).total_seconds()
#         if diff > 0:
#             total_seconds += diff

#     hours = round(total_seconds / 3600, 2)

#     # ------------------------------------
#     # 3) COUNT MONTHLY LATE MARKS
#     # ------------------------------------
#     month_start = get_first_day(today)
#     month_end = get_last_day(today)

#     late_logs = frappe.db.sql("""
#         SELECT time
#         FROM `tabEmployee Checkin`
#         WHERE employee = %s
#         AND log_type = 'IN'
#         AND DATE(time) BETWEEN %s AND %s
#         ORDER BY time ASC
#     """, (employee, month_start, month_end), as_dict=True)

#     late_count = 0
#     for log in late_logs:
#         if str(log.time.time()) > str(shift_start):
#             late_count += 1

#     return {
#         "hours": hours,
#         "late_count": late_count,
#         "shift_start": str(shift_start)
#     }

import frappe
from frappe.utils import now_datetime, getdate, get_first_day, get_last_day

@frappe.whitelist()
def get_today_hours():
    user = frappe.session.user
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")

    if not employee:
        return {"hours": 0, "late_count": 0}

    today = getdate()
    shift_start = "09:00:00"

    # ----------------------------
    # SHIFT START TIME
    # ----------------------------
    shift_assignment = frappe.db.sql("""
        SELECT shift_type
        FROM `tabShift Assignment`
        WHERE employee = %s
        AND start_date <= %s
        AND (end_date IS NULL OR end_date >= %s)
        LIMIT 1
    """, (employee, today, today), as_dict=True)

    if shift_assignment:
        shift_type = shift_assignment[0].shift_type
        shift_start = frappe.db.get_value("Shift Type", shift_type, "start_time") or "09:00:00"

    # ----------------------------
    # TODAY CHECKINS (time field!)
    # ----------------------------
    logs = frappe.db.sql("""
        SELECT time, log_type
        FROM `tabEmployee Checkin`
        WHERE employee = %s
        AND DATE(time) = %s
        ORDER BY time ASC
    """, (employee, today), as_dict=True)

    total_seconds = 0
    last_in = None

    for log in logs:
        log_type = log.log_type.strip().lower()

        if log_type in ["in", "check-in"]:
            last_in = log.time

        elif log_type in ["out", "check-out"] and last_in:
            diff = (log.time - last_in).total_seconds()
            if diff > 0:
                total_seconds += diff
            last_in = None

    # Count until NOW if last check-in only
    if last_in:
        diff = (now_datetime() - last_in).total_seconds()
        if diff > 0:
            total_seconds += diff

    hours = round(total_seconds / 3600, 2)

    # ----------------------------
    # MONTHLY LATE COUNT
    # ----------------------------
    month_start = get_first_day(today)
    month_end = get_last_day(today)

    late_logs = frappe.db.sql("""
        SELECT time
        FROM `tabEmployee Checkin`
        WHERE employee = %s
        AND LOWER(log_type) IN ('in', 'check-in')
        AND DATE(time) BETWEEN %s AND %s
        ORDER BY time ASC
    """, (employee, month_start, month_end), as_dict=True)

    late_count = 0
    for log in late_logs:
        if str(log.time.time()) > str(shift_start):
            late_count += 1

    return {
        "hours": hours,
        "late_count": late_count,
        "shift_start": str(shift_start)
    }
