
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# Allow app.py to import our existing backend
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from database import get_connection


st.set_page_config(
    page_title="Retail Intelligence Platform",
    page_icon="📊",
    layout="wide"
)


@st.cache_data(ttl=60)
def load_data():
    connection = get_connection()

    try:
        query = """
            SELECT
                transaction_id,
                product,
                category,
                unit_price,
                quantity,
                revenue
            FROM sales
        """

        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(query)
            rows = cursor.fetchall()
        finally:
            cursor.close()

        return pd.DataFrame(rows)

    finally:
        connection.close()


st.title("Retail Sales & Customer Intelligence")
st.caption("Business intelligence dashboard powered by Python and MySQL")

try:
    df = load_data()
except Exception as error:
    st.error("Unable to load sales data from MySQL.")
    st.exception(error)
    st.stop()

if df.empty:
    st.warning(
        "No transactions found. Run python src/main.py "
        "to load sales data into MySQL."
    )
    st.stop()

# Convert MySQL Decimal values for charts
df["revenue"] = pd.to_numeric(df["revenue"])
df["unit_price"] = pd.to_numeric(df["unit_price"])
df["quantity"] = pd.to_numeric(df["quantity"])

# Sidebar filters
st.sidebar.header("Dashboard Filters")

categories = st.sidebar.multiselect(
    "Select categories",
    options=sorted(df["category"].unique()),
    default=sorted(df["category"].unique())
)

filtered_df = df[df["category"].isin(categories)]

products = st.sidebar.multiselect(
    "Select products",
    options=sorted(filtered_df["product"].unique()),
    default=sorted(filtered_df["product"].unique())
)

filtered_df = filtered_df[
    filtered_df["product"].isin(products)
]

# KPI calculations
total_revenue = filtered_df["revenue"].sum()
total_transactions = len(filtered_df)
total_units = filtered_df["quantity"].sum()

average_order = (
    total_revenue / total_transactions
    if total_transactions else 0
)

st.subheader("Business Performance")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Transactions", f"{total_transactions:,}")
col3.metric("Units Sold", f"{total_units:,}")
col4.metric("Average Transaction", f"${average_order:,.2f}")

st.divider()

# Product revenue
product_sales = (
    filtered_df.groupby("product", as_index=False)["revenue"]
    .sum()
    .sort_values("revenue", ascending=False)
)

# Category revenue
category_sales = (
    filtered_df.groupby("category", as_index=False)["revenue"]
    .sum()
)

left, right = st.columns(2)

with left:
    st.subheader("Revenue by Product")

    fig_products = px.bar(
        product_sales,
        x="product",
        y="revenue",
        color="product",
        title="Product Performance"
    )

    st.plotly_chart(fig_products, width="stretch")

with right:
    st.subheader("Revenue by Category")

    fig_categories = px.pie(
        category_sales,
        names="category",
        values="revenue",
        title="Category Distribution",
        hole=0.4
    )

    st.plotly_chart(fig_categories, width="stretch")

st.divider()

# Transaction table
st.subheader("Sales Transactions")

st.dataframe(
    filtered_df,
    width="stretch",
    hide_index=True
)

# Export filtered records
csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Sales Report",
    data=csv_data,
    file_name="retail_sales_report.csv",
    mime="text/csv"
)

st.caption("Retail Intelligence Platform | Built with Python, MySQL & Streamlit")
