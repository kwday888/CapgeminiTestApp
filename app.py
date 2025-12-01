import streamlit as st
import pandas as pd
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



# ___________________________ Streamlit App _____________________________

st.set_page_config(page_title="Simple Expense Tracker", layout="wide")
st.title("Simple Expense Tracker")
tab_view, tab_add = st.tabs(["View Expenses", "Add Expense"])


# _______ View Expenses Tab ______
with tab_view:
    st.subheader("All Expenses")
    df = load_expenses()
  
    if df.empty:
        st.info("No expenses found yet. Add some on the 'Add Expense' tab.")
    else:
        df_sorted = df.sort_values(COL_TIME_ID, ascending=False)
        st.dataframe(df_sorted, use_container_width=True)

        # Quick summary
        total_spent = df_sorted[COL_AMOUNT].sum()
        st.metric("Total Expense", f"${total_spent:,.2f}")

        # Show by category table
        by_cat = (
            df_sorted.groupby(COL_CATEGORY)[COL_AMOUNT]
            .sum()
            .reset_index()
            .rename(columns={COL_AMOUNT: "total_amount"})
            .sort_values("total_amount", ascending=False)
        )
        st.markdown("**Total by Category**")
        st.dataframe(by_cat, use_container_width=True)


# ---------- Add Expense Tab ----------
with tab_add:
    st.subheader("Add a New Expense")
    with st.form("add_expense_form"):
        col1, col2 = st.columns(2)
        with col1:
            category = st.text_input("Category", placeholder="e.g. human_labor, rent, inventory")
        with col2:
            amount = st.number_input(
                "Amount",
                min_value=0.0,
                step=0.01,
                format="%.2f",
            )

        description = st.text_input("Description (data column)", placeholder="e.g. Shift payment - J. Lopez")
        submitted = st.form_submit_button("Save Expense")

    if submitted:
        if not category.strip():
            st.error("Category cannot be empty.")
        elif amount <= 0:
            st.error("Amount must be greater than 0.")
        else:
            add_expense(category, amount, description)
            st.success("Expense saved successfully!")
            st.rerun()

