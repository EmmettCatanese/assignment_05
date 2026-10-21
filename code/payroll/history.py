import pandas as pd


def clean_employee_id(ids: pd.Series) -> pd.Series:
    ids = ids.str.strip()
    ids = ids.str.upper()
    ids = ids.str[1:].str.zfill(3)
    return "E" + ids


def clean_number(values: pd.Series) -> pd.Series:
    values = values.str.replace("$", "", regex=False)
    values = values.str.replace(",", "", regex=False)
    values = values.str.strip()
    values = pd.to_numeric(values, errors="coerce")
    return values.fillna(0.0)


def parse_pay_date(values: pd.Series) -> pd.Series:
    us = pd.to_datetime(values, format="%m/%d/%Y", errors="coerce")
    iso = pd.to_datetime(values, format="%Y-%m-%d", errors="coerce")
    return us.fillna(iso)


def combine_exports(exports: list) -> pd.DataFrame:
    return pd.concat(exports, ignore_index=True)


def add_clean_columns(history: pd.DataFrame) -> pd.DataFrame:
    out = history.copy()
    out["employee_id"] = clean_employee_id(out["employeeid"])
    out["pay_date"] = parse_pay_date(out["payrolldate"])
    out["hours_worked"] = clean_number(out["hours"])
    out["rate_usd"] = clean_number(out["rate"])
    out["gross_pay"] = clean_number(out["total"])
    return out


def add_date_parts(history: pd.DataFrame) -> pd.DataFrame:
    out = history.copy()
    out["week_ending"] = out["pay_date"].dt.strftime("%Y-%m-%d")
    out["month"] = out["pay_date"].dt.strftime("%Y-%m")
    return out
