import pandas as pd
from .history import add_clean_columns, add_date_parts, combine_exports


def format_name(names: pd.Series) -> pd.Series:
    """Turn roster names written 'Last, First' into 'First Last'.

    A name with no comma comes back as NaN, since there's no first name
    to split off.
    """
    names = names.str.split(",")
    last = names.str[0].str.strip()
    first = names.str[1].str.strip()
    return first + " " + last


def add_roster(history: pd.DataFrame, employees: pd.DataFrame) -> pd.DataFrame:
    """Attach each row's display_name and department from the roster.

    Left-joins on employee_id, so every history row is kept. Rows whose
    employee_id isn't on the roster get NaN for display_name and
    department, which is how the app spots unmatched IDs.
    """
    roster = employees.copy()
    roster["display_name"] = format_name(roster["name"])
    roster = roster[["employee_id", "display_name", "department"]]
    out = history.merge(roster, how="left", on="employee_id")
    return out


def build_history(exports: list, employees: pd.DataFrame) -> pd.DataFrame:
    """Run the whole cleaning pipeline: weekly exports in, one tidy history out.

    Stacks the exports, adds cleaned columns (employee_id, pay_date,
    hours_worked, rate_usd, gross_pay), adds week_ending and month, then
    joins the roster for display_name and department. The original export
    columns are kept alongside the cleaned ones.
    """
    exports = combine_exports(exports)
    exports = add_clean_columns(exports)
    exports = add_date_parts(exports)
    exports = add_roster(exports, employees)
    return exports


def summarize_employees(history: pd.DataFrame) -> pd.DataFrame:
    """Summarize each employee's quarter: one row per employee.

    Columns are weeks_paid (distinct week_ending dates), total_hours,
    total_pay (rounded to cents), avg_hours and overtime_weeks (rows over
    40 hours). avg_hours and overtime_weeks are computed per row, so they
    match per-week figures only when each employee has one row per week.
    Rows with no department (IDs not on the roster) are left out, because
    groupby drops missing keys.
    """
    return history.groupby(["employee_id", "display_name", "department"]).agg(
        weeks_paid=("week_ending", "nunique"),
        total_hours=("hours_worked", "sum"),
        total_pay=("gross_pay", "sum"),
        avg_hours=("hours_worked", "mean"),
        overtime_weeks=("hours_worked", lambda x: (x > 40.0).sum())
    ).round({"total_pay": 2}).reset_index()