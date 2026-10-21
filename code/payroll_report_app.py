import streamlit as st

from payroll import (
    build_history,
    hours_grid,
    load_employees,
    load_export,
    missed_weeks,
    pay_by_month,
    summarize_employees,
)

st.title("Salt City Coffee — Quarterly Payroll Report")
st.text("Upload this quarter's payroll exports to see hours, pay, and missed shifts.")

roster = load_employees()

uploads = st.file_uploader(
    "Upload payroll exports (CSV) for the quarter",
    type="csv",
    accept_multiple_files=True,
    key="exports",
)

if uploads:
    history = build_history([load_export(u) for u in uploads], roster)

    # Anyone with no department wasn't on the roster; name them as typed
    unmatched = history.loc[history["department"].isna(), "employeeid"]
    if not unmatched.empty:
        as_typed = sorted(unmatched.str.strip().unique())
        st.warning(
            f"Not on the roster: {', '.join(as_typed)}. "
            "Their rows are left out of the reports below."
        )
    matched = history[history["department"].notna()]

    department = st.selectbox(
        "Department to report on",
        ["All"] + sorted(matched["department"].unique()),
        key="department",
    )

    first_day = matched["pay_date"].min().date()
    last_day = matched["pay_date"].max().date()
    dates = st.date_input(
        "Date range to report on",
        value=(first_day, last_day),
        key="dates",
    )
    if len(dates) != 2:
        st.info("Pick an end date to finish the range.")
        st.stop()
    start, end = dates

    pay_days = matched["pay_date"].dt.date
    selected = matched[(pay_days >= start) & (pay_days <= end)]
    if department != "All":
        selected = selected[selected["department"] == department]

    st.subheader(f"{department} from {start} to {end}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Weeks", selected["week_ending"].nunique())
    col2.metric("Employees", selected["employee_id"].nunique())
    col3.metric("Total hours", f"{selected['hours_worked'].sum():,.2f}")
    col4.metric("Total gross pay", f"${selected['gross_pay'].sum():,.2f}")

    monthly = pay_by_month(selected)
    st.subheader("Gross pay by month and department")
    st.bar_chart(monthly, x="month")

    st.subheader("Pay by employee")
    st.dataframe(summarize_employees(selected))

    grid = hours_grid(selected)
    st.subheader("Hours by week")
    st.dataframe(grid)

    st.subheader("Missed weeks")
    st.dataframe(missed_weeks(grid))

    st.download_button(
        "Download pay by month (CSV)",
        monthly.to_csv(index=False),
        file_name="pay_by_month.csv",
        mime="text/csv",
        key="download",
    )
