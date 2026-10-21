import pandas as pd


def clean_employee_id(ids: pd.Series) -> pd.Series:
    """Standardize employee IDs to the roster's form, e.g. ' e77' -> 'E077'.

    Strips whitespace, uppercases, drops the first character (assumed to be
    the letter prefix), zero-pads the remaining digits to at least three,
    and puts an 'E' back on the front.
    """
    ids = ids.str.strip()
    ids = ids.str.upper()
    ids = ids.str[1:].str.zfill(3)
    return "E" + ids


def clean_number(values: pd.Series) -> pd.Series:
    """Convert text amounts like ' $1,234.50' to floats.

    Removes dollar signs, commas and surrounding whitespace before parsing.
    Anything that still can't be read as a number, including blanks,
    becomes 0.0.
    """
    values = values.str.replace("$", "", regex=False)
    values = values.str.replace(",", "", regex=False)
    values = values.str.strip()
    values = pd.to_numeric(values, errors="coerce")
    return values.fillna(0.0)


def parse_pay_date(values: pd.Series) -> pd.Series:
    """Parse pay dates written as either MM/DD/YYYY or YYYY-MM-DD.

    Tries the US format first and falls back to ISO for any value that
    didn't match. Dates in neither format become NaT.
    """
    us = pd.to_datetime(values, format="%m/%d/%Y", errors="coerce")
    iso = pd.to_datetime(values, format="%Y-%m-%d", errors="coerce")
    return us.fillna(iso)


def combine_exports(exports: list) -> pd.DataFrame:
    """Stack a list of weekly export DataFrames into one, with a fresh index."""
    return pd.concat(exports, ignore_index=True)


def add_clean_columns(history: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the raw history with cleaned, typed columns added.

    Adds employee_id, pay_date, hours_worked, rate_usd and gross_pay
    alongside the original export columns, which are kept as typed
    (the app uses the raw employeeid to name unmatched IDs).
    """
    out = history.copy()
    out["employee_id"] = clean_employee_id(out["employeeid"])
    out["pay_date"] = parse_pay_date(out["payrolldate"])
    out["hours_worked"] = clean_number(out["hours"])
    out["rate_usd"] = clean_number(out["rate"])
    out["gross_pay"] = clean_number(out["total"])
    return out


def add_date_parts(history: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with week_ending (YYYY-MM-DD) and month (YYYY-MM) text columns.

    Both are derived from pay_date, so run add_clean_columns first.
    """
    out = history.copy()
    out["week_ending"] = out["pay_date"].dt.strftime("%Y-%m-%d")
    out["month"] = out["pay_date"].dt.strftime("%Y-%m")
    return out
