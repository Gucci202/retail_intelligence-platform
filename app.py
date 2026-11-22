
import streamlit as st
import pandas as pd
import plotly.express as px
from src.database import get_connection

# Configure webpage
st.set_page_config(
    page_title="Retail Intelligence Platform",
    page_icon="📊",
    layout="wide"
)

st.title("Retail Sales & Customer Intelligence")
st.caption("Interactive retail analytics powered by Python and MySQL")


# Load data from MySQL
@st.cache_data(ttl=60)
def load_data():
    connection = get_connection()

    query = """
        SELECT
            o.order_id,
            o.order_date,
            c.customer_id,
            c.customer_name,
            c.region,
            p.product_name,
            p.category,
            o.quantity,
            o.revenue
        FROM orders o
        JOIN customers c
            ON o.customer_id = c.customer_id
        JOIN products p
            ON o.product_id = p.product_id
    """

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
    finally:
        connection.close()

    df = pd.DataFrame(records)

    if not df.empty:
        df["order_date"] = pd.to_datetime(df["order_date"])
        df["revenue"] = pd.to_numeric(df["revenue"])
        df["quantity"] = pd.to_numeric(df["quantity"])

    return df


try:
    df = load_data()
except Exception as error:
    st.error(f"Database connection failed: {error}")
    st.stop()

if df.empty:
    st.warning("No orders found in the database.")
    st.stop()


# Sidebar filters
st.sidebar.header("Dashboard Filters")

regions = st.sidebar.multiselect(
    "Select Regions",
    options=sorted(df["region"].unique()),
    default=sorted(df["region"].unique())
)

categories = st.sidebar.multiselect(
    "Select Categories",
    options=sorted(df["category"].unique()),
    default=sorted(df["category"].unique())
)

date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(
        df["order_date"].min().date(),
        df["order_date"].max().date()
    ),
    min_value=df["order_date"].min().date(),
    max_value=df["order_date"].max().date()
)

filtered_df = df[
    df["region"].isin(regions)
    & df["category"].isin(categories)
].copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range

    filtered_df = filtered_df[
        filtered_df["order_date"].dt.date.between(
            start_date, end_date
        )
    ]


# KPI calculations
total_revenue = filtered_df["revenue"].sum()
total_orders = filtered_df["order_id"].nunique()
total_units = filtered_df["quantity"].sum()
total_customers = filtered_df["customer_id"].nunique()

average_order_value = (
    total_revenue / total_orders
    if total_orders > 0 else 0
)

st.subheader("Business Overview")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Orders", f"{total_orders:,}")
col3.metric("Units Sold", f"{total_units:,}")
col4.metric("Customers", f"{total_customers:,}")
col5.metric("Average Order", f"${average_order_value:,.2f}")

st.divider()

# Monthly revenue
st.subheader("Monthly Revenue Trends")

monthly_sales = (
    filtered_df.assign(
        month=filtered_df["order_date"].dt.to_period("M").dt.to_timestamp()
    )
    .groupby("month", as_index=False)["revenue"]
    .sum()
)

fig_monthly = px.line(
    monthly_sales,
    x="month",
    y="revenue",
    markers=True,
    title="Revenue Over Time"
)

st.plotly_chart(fig_monthly, use_container_width=True)

# Product and regional performance
left, right = st.columns(2)

with left:
    st.subheader("Top 10 Products")

    product_sales = (
        filtered_df.groupby("product_name", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
        .head(10)
    )

    fig_products = px.bar(
        product_sales,
        x="revenue",
        y="product_name",
        orientation="h",
        title="Best Performing Products"
    )

    st.plotly_chart(fig_products, use_container_width=True)

with right:
    st.subheader("Revenue by Region")

    regional_sales = (
        filtered_df.groupby("region", as_index=False)["revenue"]
        .sum()
    )

    fig_regions = px.bar(
        regional_sales,
        x="region",
        y="revenue",
        title="Regional Revenue Comparison"
    )

    st.plotly_chart(fig_regions, use_container_width=True)


# Category performance
st.subheader("Revenue by Category")

category_sales = (
    filtered_df.groupby("category", as_index=False)["revenue"]
    .sum()
)

fig_categories = px.pie(
    category_sales,
    names="category",
    values="revenue",
    hole=0.4
)

st.plotly_chart(fig_categories, use_container_width=True)


# Customer intelligence
st.subheader("Top 10 Customers")

customer_sales = (
    filtered_df.groupby(
        ["customer_id", "customer_name"],
        as_index=False
    )["revenue"]
    .sum()
    .sort_values("revenue", ascending=False)
    .head(10)
)

st.dataframe(
    customer_sales,
    use_container_width=True,
    hide_index=True
)


# Transaction explorer
st.subheader("Transaction Explorer")

st.dataframe(
    filtered_df.sort_values("order_date", ascending=False),
    use_container_width=True,
    hide_index=True
)

csv_data = filtered_df.to_csv(index=False)

st.download_button(
    label="Download Filtered Transactions",
    data=csv_data,
    file_name="retail_transactions.csv",
    mime="text/csv"
)
