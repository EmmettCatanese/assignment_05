import pandas as pd


def hours_grid(history: pd.DataFrame) -> pd.DataFrame:
    """Lay out hours worked as one row per employee and one column per week.

    Rows are keyed by employee_id and display_name; columns are the
    week_ending dates found in history. A week with no row for an employee
    shows 0. If an employee has more than one row in the same week, the
    cell is the average of those rows (pivot_table's default), not the sum.
    """
    return history.pivot_table(
        index=["employee_id", "display_name"],
        columns="week_ending",
        values="hours_worked",
        fill_value=0
    ).reset_index()


def missed_weeks(grid: pd.DataFrame) -> pd.DataFrame:
    """List every employee-week with zero hours in a grid from hours_grid.

    Unpivots the grid back to one row per employee per week and keeps only
    the weeks with 0 hours, sorted by employee_id and then week_ending.
    Only weeks that appear as columns in the grid are checked.
    """
    long = grid.melt(
        id_vars=["employee_id", "display_name"],
        var_name="week_ending",
        value_name="hours_worked"
    )
    return long[long["hours_worked"] == 0].sort_values(
        by=["employee_id", "week_ending"]
    ).reset_index(drop=True)


def pay_by_month(history: pd.DataFrame) -> pd.DataFrame:
    """Total gross pay as one row per month and one column per department.

    The month column holds YYYY-MM text; each department column holds that
    department's summed gross_pay for the month, or 0.0 if it had none.
    """
    return history.pivot_table(
        index="month",
        columns="department",
        values="gross_pay",
        aggfunc="sum",
        fill_value=0.0
    ).reset_index()