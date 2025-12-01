import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from pathlib import Path
from datetime import datetime


# ___________________________ Init _____________________________

CSV_PATH = Path("expense_data.csv")
COL_CATEGORY = "category"
COL_AMOUNT = "amount"
COL_DATA = "data"
COL_TIME_ID = "time_id"


def get_empty_df() -> pd.DataFrame:
    return pd.DataFrame(columns=[COL_CATEGORY, COL_AMOUNT, COL_DATA, COL_TIME_ID])


def load_expenses() -> pd.DataFrame:
    if not CSV_PATH.exists():
        return get_empty_df()

    df = pd.read_csv(CSV_PATH)
    for col in [COL_CATEGORY, COL_AMOUNT, COL_DATA, COL_TIME_ID]:
        if col not in df.columns:
            df[col] = pd.NA

    df[COL_AMOUNT] = pd.to_numeric(df[COL_AMOUNT], errors="coerce").fillna(0.0)
    return df


def save_expenses(df: pd.DataFrame) -> None:
    df.to_csv(CSV_PATH, index=False)


def add_expense(category: str, amount: float, description: str) -> None:
    df = load_expenses()
    new_row = {
        COL_CATEGORY: category.strip(),
        COL_AMOUNT: float(amount),
        COL_DATA: description.strip(),
        COL_TIME_ID: datetime.utcnow().isoformat(timespec="seconds"),
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_expenses(df)


def get_highest_and_lowest_category(df: pd.DataFrame):
    if df.empty:
        return None, None

    by_cat = (df.groupby("category")["amount"].sum().reset_index().rename(columns={"amount": "total_amount"}).sort_values("total_amount", ascending=False))
    highest = by_cat.iloc[0]["category"]
    lowest = by_cat.iloc[-1]["category"]
    return highest, lowest


def get_daily_totals(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["date", "total_amount"])

    tmp = df.copy()
    tmp["date"] = pd.to_datetime(tmp[COL_TIME_ID], errors="coerce").dt.date
    tmp = tmp.dropna(subset=["date"])
    daily = (tmp.groupby("date")[COL_AMOUNT].sum().reset_index().rename(columns={COL_AMOUNT: "total_amount"}).sort_values("date"))
    return daily


def add_prediction_line(daily: pd.DataFrame, days_ahead: int = 7) -> pd.DataFrame:
    if daily.empty or len(daily) < 2:
        return daily.assign(type="actual") 

    daily = daily.copy()
    daily["date"] = pd.to_datetime(daily["date"])
    x = (daily["date"] - daily["date"].min()).dt.days.values.astype(float)
    y = daily["total_amount"].values.astype(float)

    m, b = np.polyfit(x, y, 1)

    last_day_index = int(x[-1])
    future_indices = np.arange(last_day_index + 1, last_day_index + 1 + days_ahead)
    future_dates = daily["date"].min() + pd.to_timedelta(future_indices, unit="D")
    future_amounts = m * future_indices + b

    actual = daily.copy()
    actual["type"] = "actual"

    future = pd.DataFrame({"date": future_dates,"total_amount": future_amounts,"type": "predicted",})
    combined = pd.concat([actual, future], ignore_index=True)
    return combined


# ___________________________ Streamlit App _____________________________

st.set_page_config(page_title="Simple Expense Tracker", layout="wide")
st.title("Simple Expense Tracker")

if "page" not in st.session_state:
    st.session_state["page"] = "View Expenses"

if "extra_categories" not in st.session_state:
    st.session_state["extra_categories"] = []

page = st.sidebar.radio("Navigate",["View Expenses", "Add Expense", "Expense Trends"],
    index=["View Expenses", "Add Expense", "Expense Trends"].index(st.session_state["page"]),)

st.session_state["page"] = page
df = load_expenses()

# _______ View Expenses Tab ______
if page == "View Expenses":
    st.subheader("All Expenses")

    if df.empty:
        st.info("No expenses found yet. Add some on the 'Add Expense' page.")
    else:
        df_sorted = df.sort_values(COL_TIME_ID, ascending=False)
        total_spent = df_sorted[COL_AMOUNT].sum()
        highest, lowest = get_highest_and_lowest_category(df_sorted)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Expense", f"${total_spent:,.2f}")
        col2.metric("Highest Spend Category", highest if highest else "N/A")
        col3.metric("Lowest Spend Category", lowest if lowest else "N/A")
        st.dataframe(df_sorted, use_container_width=True)

        # Show by category
        by_cat = (
            df_sorted.groupby(COL_CATEGORY)[COL_AMOUNT].sum().reset_index().rename(columns={COL_AMOUNT: "total_amount"}).sort_values("total_amount", ascending=False))
        st.markdown("**Total by Category**")
        st.dataframe(by_cat, use_container_width=True)


# ______ Add Expense Tab _______
elif page == "Add Expense":
    st.subheader("Add a New Expense")
    df_all = load_expenses()
    base_categories = []

    if not df_all.empty:
        base_categories = [str(c).strip()for c in df_all[COL_CATEGORY].dropna().unique().tolist()if str(c).strip() != ""]
    extra_categories = st.session_state.get("extra_categories", [])
    category_options = sorted(set(base_categories + extra_categories))

    # ____ Main expense form ___
    with st.form("add_expense_form"):
        col1, col2 = st.columns(2)
        with col1:
            if category_options:
                category = st.selectbox("Category",options=category_options,index=0,help="Select an existing category.",)
            else:
                category = st.text_input("Category",placeholder="e.g. human_labor, rent, inventory",help="No categories yet. Enter a new one.",)
        with col2:
            amount = st.number_input("Amount",min_value=0.0,step=0.01,format="%.2f",)

        description = st.text_input("Description (data column)",placeholder="e.g. Shift payment - J. Lopez",)
        submitted = st.form_submit_button("Save Expense")

    if submitted:
        if not category or not str(category).strip():
            st.error("Category cannot be empty.")
        elif amount <= 0:
            st.error("Amount must be greater than 0.")
        else:
            add_expense(str(category), amount, description)
            st.success("Expense saved successfully!")

            cat_clean = str(category).strip()
            if cat_clean and cat_clean not in st.session_state["extra_categories"]:
                st.session_state["extra_categories"].append(cat_clean)

            st.session_state["page"] = "View Expenses"
            st.rerun()

    st.markdown("---")
    st.markdown("### Manage Categories")

    # ---- New category form ----
    with st.form("add_category_form"):
        new_category = st.text_input("Add a new category",placeholder="e.g. utilities, advertising, equipment",)
        add_cat_submitted = st.form_submit_button("Add Category")

    if add_cat_submitted:
        cat_clean = new_category.strip()
        if not cat_clean:
            st.error("Category name cannot be empty.")
        else:
            all_existing = set(base_categories + st.session_state["extra_categories"])
            if cat_clean in all_existing:
                st.warning(f"Category '{cat_clean}' already exists.")
            else:
                st.session_state["extra_categories"].append(cat_clean)
                st.success(f"Category '{cat_clean}' added. It is now available in the dropdown above.")
                st.rerun()

# ______ Expense Trends Tab ______

elif page == "Expense Trends":
    st.subheader("Expense Trends")

    if df.empty:
        st.info("No expenses available to analyze yet.")
    else:
        st.markdown("### Distribution of Expenses by Category (Box Plot)")
        box_data = df[[COL_CATEGORY, COL_AMOUNT]].copy()
        box_chart = (
            alt.Chart(box_data)
            .mark_boxplot()
            .encode(
                x=alt.X(f"{COL_CATEGORY}:N", title="Category"),
                y=alt.Y(f"{COL_AMOUNT}:Q", title="Amount"),
            )
            .properties(height=400)
        )
        st.altair_chart(box_chart, use_container_width=True)

        
        st.markdown("### Expenses Over Time with Simple Prediction")
        daily = get_daily_totals(df)
        combined = add_prediction_line(daily, days_ahead=7)
        if combined.empty:
            st.info("Not enough valid dates in the data to compute a trend.")
        else:
            combined["date"] = pd.to_datetime(combined["date"])
            line_chart = (alt.Chart(combined).mark_line(point=True).encode(x=alt.X("date:T", title="Date"),
                    y=alt.Y("total_amount:Q", title="Total Amount"),
                    color=alt.Color("type:N", title="Series"),
                )
                .properties(height=400)
            )
            st.altair_chart(line_chart, use_container_width=True)
