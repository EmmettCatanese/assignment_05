import pandas as pd


def hours_grid(history: pd.DataFrame) -> pd.DataFrame:
    return history.pivot_table(
        index=["employee_id", "display_name"],
        columns="week_ending",
        values="hours_worked",
        fill_value=0
    ).reset_index()


def missed_weeks(grid: pd.DataFrame) -> pd.DataFrame:
    long = grid.melt(
        id_vars=["employee_id", "display_name"],
        var_name="week_ending",
        value_name="hours_worked"
    )
    return long[long["hours_worked"] == 0].sort_values(
        by=["employee_id", "week_ending"]
    ).reset_index(drop=True)


def pay_by_month(history: pd.DataFrame) -> pd.DataFrame:
    return history.pivot_table(
        index="month",
        columns="department",
        values="gross_pay",
        aggfunc="sum",
        fill_value=0.0
    ).reset_index()
