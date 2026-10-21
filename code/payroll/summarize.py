import pandas as pd
from .history import add_clean_columns, add_date_parts, combine_exports


def format_name(names: pd.Series) -> pd.Series:
    names = names.str.split(",")
    last = names.str[0].str.strip()
    first = names.str[1].str.strip()
    return first + " " + last


def add_roster(history: pd.DataFrame, employees: pd.DataFrame) -> pd.DataFrame:
    roster = employees.copy()
    roster["display_name"] = format_name(roster["name"])
    roster = roster[["employee_id", "display_name", "department"]]
    out = history.merge(roster, how="left", on="employee_id")
    return out


def build_history(exports: list, employees: pd.DataFrame) -> pd.DataFrame:
    exports = combine_exports(exports)
    exports = add_clean_columns(exports)
    exports = add_date_parts(exports)
    exports = add_roster(exports, employees)
    return exports


def summarize_employees(history: pd.DataFrame) -> pd.DataFrame:
    return history.groupby(["employee_id", "display_name", "department"]).agg(
        weeks_paid=("week_ending", "nunique"),
        total_hours=("hours_worked", "sum"),
        total_pay=("gross_pay", "sum"),
        avg_hours=("hours_worked", "mean"),
        overtime_weeks=("hours_worked", lambda x: (x > 40.0).sum())
    ).round({"total_pay": 2}).reset_index()