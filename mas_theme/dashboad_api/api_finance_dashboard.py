import frappe
from frappe.utils import getdate, flt, add_months
from dateutil.relativedelta import relativedelta

@frappe.whitelist()
def get_bank_accounts(company):
    """
    Get all bank accounts with their current balance
    """
    try:
        # Get bank accounts from Account table with type 'Bank'
        bank_accounts = frappe.db.sql("""
            SELECT
                name as account_name,
                account_number
            FROM `tabAccount`
            WHERE company = %(company)s
            AND account_type = 'Bank'
            AND is_group = 0
            AND (disabled = 0 OR disabled IS NULL)
            ORDER BY name ASC
        """, {"company": company}, as_dict=1)

        # Calculate balance for each account
        result = []
        for account in bank_accounts:
            balance = frappe.db.sql("""
                SELECT SUM(debit - credit) as balance
                FROM `tabGL Entry`
                WHERE account = %(account)s
                AND company = %(company)s
            """, {"account": account.account_name, "company": company}, as_dict=1)

            account['balance'] = flt(balance[0].balance) if balance and balance[0].balance else 0
            account['bank_name'] = account.get('account_name', 'Bank Account')

            # Only include accounts with non-zero balance
            if account['balance'] != 0:
                result.append(account)

        return result
    except Exception as e:
        frappe.log_error(f"Error fetching bank accounts: {str(e)}", "Bank Accounts Error")
        return []

@frappe.whitelist()
def get_expense_accounts(company):
    """
    Get all expense accounts with their current balance from Account table
    """
    try:
        expense_accounts = frappe.db.sql("""
            SELECT
                name as account_name,
                account_number
            FROM `tabAccount`
            WHERE company = %(company)s
            AND root_type = 'Expense'
            AND is_group = 0
            AND (disabled = 0 OR disabled IS NULL)
            ORDER BY name ASC
        """, {"company": company}, as_dict=1)

        # Calculate balance for each account
        result = []
        for account in expense_accounts:
            balance = frappe.db.sql("""
                SELECT SUM(debit - credit) as balance
                FROM `tabGL Entry`
                WHERE account = %(account)s
                AND company = %(company)s
            """, {"account": account.account_name, "company": company}, as_dict=1)

            account['balance'] = flt(balance[0].balance) if balance and balance[0].balance else 0

            # Only include accounts with non-zero balance
            if account['balance'] != 0:
                result.append(account)

        return result
    except Exception as e:
        frappe.log_error(f"Error fetching expense accounts: {str(e)}", "Expense Accounts Error")
        return []

@frappe.whitelist()
def get_cash_accounts(company):
    """
    Get all cash accounts with their current balance
    """
    try:
        cash_accounts = frappe.db.sql("""
            SELECT
                name as account_name,
                account_number
            FROM `tabAccount`
            WHERE company = %(company)s
            AND account_type = 'Cash'
            AND is_group = 0
            AND disabled = 0
            ORDER BY creation DESC
        """, {"company": company}, as_dict=1)

        # Calculate balance for each account
        result = []
        for account in cash_accounts:
            balance = frappe.db.sql("""
                SELECT SUM(debit - credit) as balance
                FROM `tabGL Entry`
                WHERE account = %(account)s
                AND company = %(company)s
            """, {"account": account.account_name, "company": company}, as_dict=1)

            account['balance'] = flt(balance[0].balance) if balance and balance[0].balance else 0

            # Only include accounts with non-zero balance
            if account['balance'] != 0:
                result.append(account)

        return result
    except Exception as e:
        frappe.log_error(f"Error fetching cash accounts: {str(e)}", "Cash Accounts Error")
        return []

# Copyright (c) 2025, Ahsan Shah and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, today, flt


def _empty_aging_result():
    return {
        "not_due": 0,
        "0-30": 0,
        "31-60": 0,
        "61-90": 0,
        "91-120": 0,
        "120+": 0,
        "total": 0
    }


@frappe.whitelist()
def get_accounts_payable(company):
    """
    Accounts Payable Aging (Purchase Invoices)
    """
    try:
        invoices = frappe.db.sql("""
            SELECT
                supplier AS party_name,
                outstanding_amount AS outstanding,
                due_date
            FROM `tabPurchase Invoice`
            WHERE company = %(company)s
              AND docstatus = 1
              AND outstanding_amount > 0
        """, {"company": company}, as_dict=True)

        result = _empty_aging_result()
        today_date = getdate(today())

        for inv in invoices:
            outstanding = flt(inv.outstanding)
            result["total"] += outstanding

            if not inv.due_date:
                result["not_due"] += outstanding
                continue

            due_date = getdate(inv.due_date)
            days_overdue = (today_date - due_date).days

            if days_overdue < 0:
                result["not_due"] += outstanding
            elif days_overdue <= 30:
                result["0-30"] += outstanding
            elif days_overdue <= 60:
                result["31-60"] += outstanding
            elif days_overdue <= 90:
                result["61-90"] += outstanding
            elif days_overdue <= 120:
                result["91-120"] += outstanding
            else:
                result["120+"] += outstanding

        return result

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "Accounts Payable Aging Error"
        )
        return _empty_aging_result()


@frappe.whitelist()
def get_accounts_receivable(company):
    """
    Accounts Receivable Aging (Sales Invoices)
    """
    try:
        invoices = frappe.db.sql("""
            SELECT
                customer AS party_name,
                outstanding_amount AS outstanding,
                due_date
            FROM `tabSales Invoice`
            WHERE company = %(company)s
              AND docstatus = 1
              AND outstanding_amount > 0
        """, {"company": company}, as_dict=True)

        result = _empty_aging_result()
        today_date = getdate(today())

        for inv in invoices:
            outstanding = flt(inv.outstanding)
            result["total"] += outstanding

            if not inv.due_date:
                result["not_due"] += outstanding
                continue

            due_date = getdate(inv.due_date)
            days_overdue = (today_date - due_date).days

            if days_overdue < 0:
                result["not_due"] += outstanding
            elif days_overdue <= 30:
                result["0-30"] += outstanding
            elif days_overdue <= 60:
                result["31-60"] += outstanding
            elif days_overdue <= 90:
                result["61-90"] += outstanding
            elif days_overdue <= 120:
                result["91-120"] += outstanding
            else:
                result["120+"] += outstanding

        return result

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            "Accounts Receivable Aging Error"
        )
        return _empty_aging_result()

@frappe.whitelist()
def get_quarterly_pnl(company, from_date, to_date):
    """
    Quarter-wise Profit & Loss using date range (NO fiscal year)
    Calculate directly from GL Entries
    """

    from_date = getdate(from_date)
    to_date = getdate(to_date)

    results = []

    # Calculate quarters dynamically based on the date range
    current_date = frappe.utils.get_first_day(from_date)
    quarter_num = 1

    while current_date <= to_date:
        # Each quarter is 3 months
        q_from = current_date
        q_to = frappe.utils.get_last_day(add_months(current_date, 2))

        # Adjust to not exceed the to_date
        if q_to > to_date:
            q_to = to_date

        # Calculate actual date range
        actual_from = max(q_from, from_date)
        actual_to = min(q_to, to_date)

        try:
            # Get monthly data for this quarter
            monthly_data = []
            month_date = frappe.utils.get_first_day(actual_from)

            while month_date <= actual_to:
                month_start = month_date
                month_end = frappe.utils.get_last_day(month_date)

                # Adjust to quarter boundaries
                if month_start < actual_from:
                    month_start = actual_from
                if month_end > actual_to:
                    month_end = actual_to

                # Get Income for this month
                month_income = frappe.db.sql("""
                    SELECT SUM(credit - debit) as total
                    FROM `tabGL Entry`
                    WHERE company = %(company)s
                    AND posting_date BETWEEN %(from_date)s AND %(to_date)s
                    AND account IN (
                        SELECT name FROM `tabAccount`
                        WHERE company = %(company)s
                        AND root_type = 'Income'
                        AND is_group = 0
                    )
                """, {
                    "company": company,
                    "from_date": month_start,
                    "to_date": month_end
                }, as_dict=1)

                # Get Expenses for this month
                month_expenses = frappe.db.sql("""
                    SELECT SUM(debit - credit) as total
                    FROM `tabGL Entry`
                    WHERE company = %(company)s
                    AND posting_date BETWEEN %(from_date)s AND %(to_date)s
                    AND account IN (
                        SELECT name FROM `tabAccount`
                        WHERE company = %(company)s
                        AND root_type = 'Expense'
                        AND is_group = 0
                    )
                """, {
                    "company": company,
                    "from_date": month_start,
                    "to_date": month_end
                }, as_dict=1)

                month_income_total = flt(month_income[0].get('total')) if month_income and month_income[0].get('total') else 0
                month_expenses_total = flt(month_expenses[0].get('total')) if month_expenses and month_expenses[0].get('total') else 0

                monthly_data.append({
                    "month": month_start.strftime('%b %Y'),
                    "income": month_income_total,
                    "expenses": month_expenses_total
                })

                # Move to next month
                month_date = add_months(month_start, 1)

            # Calculate quarter totals
            total_income = sum([m['income'] for m in monthly_data])
            total_expenses = sum([m['expenses'] for m in monthly_data])
            net_profit = total_income - total_expenses

            # Format quarter label with date range
            quarter_label = f"Q{quarter_num} ({actual_from.strftime('%b %Y')} - {actual_to.strftime('%b %Y')})"

            results.append({
                "quarter": quarter_label,
                "profit": net_profit,
                "income": total_income,
                "expenses": total_expenses,
                "monthly_data": monthly_data
            })
        except Exception as e:
            frappe.log_error(f"Error processing Q{quarter_num}: {str(e)}", "PnL Calculation Error")
            quarter_label = f"Q{quarter_num}"
            results.append({
                "quarter": quarter_label,
                "profit": 0,
                "income": 0,
                "expenses": 0,
                "monthly_data": []
            })

        # Move to next quarter (3 months forward)
        current_date = add_months(current_date, 3)
        quarter_num += 1

        # Safety check to avoid infinite loop
        if quarter_num > 20:
            break

    return results
