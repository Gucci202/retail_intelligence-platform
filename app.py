import pandas as pd
import plotly.express as px
import streamlit as st
from src.customer_analytics import calculate_rfm, segment_customers
from src.data_access import load_transactions

st.set_page_config(page_title='Retail Intelligence Platform',page_icon='📊',layout='wide')
st.title('Retail Sales & Customer Intelligence')
st.caption('Portfolio demonstration · synthetic retail data · Python, MySQL, Pandas & Streamlit')

@st.cache_data(ttl=300)
def get_data():
    return load_transactions()

try:
    df = get_data()
except Exception as exc:
    st.error(f'Unable to load retail data: {exc}')
    st.info('For local MySQL, set DB_PASSWORD in this terminal. For demo mode, include the three CSV files in data/.')
    st.stop()
if df.empty:
    st.warning('No orders found.')
    st.stop()

st.sidebar.header('Filters')
regions = st.sidebar.multiselect('Regions',sorted(df.region.dropna().unique()),default=sorted(df.region.dropna().unique()))
categories = st.sidebar.multiselect('Categories',sorted(df.category.dropna().unique()),default=sorted(df.category.dropna().unique()))
start, end = df.order_date.min().date(),df.order_date.max().date()
dates = st.sidebar.date_input('Order dates',value=(start,end),min_value=start,max_value=end)
filtered = df[df.region.isin(regions)&df.category.isin(categories)].copy()
if isinstance(dates,(tuple,list)) and len(dates)==2:
    filtered = filtered[filtered.order_date.dt.date.between(*dates)]
if filtered.empty:
    st.warning('No transactions match your filters. Change your selection to continue.')
    st.stop()

sales_tab,customer_tab,forecast_tab,data_tab = st.tabs(['Overview','Customers','Forecast','Transactions'])
with sales_tab:
    revenue = filtered.revenue.sum()
    orders = filtered.order_id.nunique()
    cols = st.columns(5)
    for col,label,value in zip(cols,['Revenue','Orders','Units','Customers','Avg. order value'],[f'${revenue:,.2f}',f'{orders:,}',f'{filtered.quantity.sum():,}',f'{filtered.customer_id.nunique():,}',f'${revenue/orders:,.2f}' if orders else '$0.00']):
        col.metric(label,value)
    monthly = filtered.assign(month=filtered.order_date.dt.to_period('M').dt.to_timestamp()).groupby('month',as_index=False).revenue.sum()
    st.plotly_chart(px.line(monthly,x='month',y='revenue',markers=True,title='Monthly revenue'),width='stretch')
    left,right=st.columns(2)
    with left:
        products=filtered.groupby('product_name',as_index=False).revenue.sum().nlargest(10,'revenue').sort_values('revenue')
        st.plotly_chart(px.bar(products,x='revenue',y='product_name',orientation='h',title='Top products'),width='stretch')
    with right:
        regions_df=filtered.groupby('region',as_index=False).revenue.sum()
        st.plotly_chart(px.bar(regions_df,x='region',y='revenue',title='Revenue by region'),width='stretch')
    categories_df=filtered.groupby('category',as_index=False).revenue.sum()
    st.plotly_chart(px.pie(categories_df,names='category',values='revenue',hole=.45,title='Category mix'),width='stretch')
with customer_tab:
    rfm=segment_customers(calculate_rfm(filtered))
    if not rfm.empty:
        a,b,c=st.columns(3)
        a.metric('Customers analyzed',f'{len(rfm):,}')
        b.metric('Avg. customer spend',f'${rfm.monetary.mean():,.2f}')
        c.metric('Champions',f'{(rfm.segment=="Champions").sum():,}')
        counts=rfm.groupby('segment',as_index=False).agg(customers=('customer_id','count'),revenue=('monetary','sum'))
        left,right=st.columns(2)
        with left:
            st.plotly_chart(px.bar(counts,x='segment',y='customers',color='segment',title='Customers by segment'),width='stretch')
        with right:
            st.plotly_chart(px.bar(counts,x='segment',y='revenue',color='segment',title='Revenue by segment'),width='stretch')
        selected=st.selectbox('Inspect a customer segment',['All']+sorted(rfm.segment.unique()))
        view=rfm if selected=='All' else rfm[rfm.segment==selected]
        st.dataframe(view.sort_values('monetary',ascending=False),width='stretch',hide_index=True)
        st.download_button('Download customer segments',rfm.to_csv(index=False),'customer_segments.csv','text/csv')
        st.caption('RFM is calculated within the current filters. Monetary is historical observed spend, not predicted lifetime value. Segments are rule-based, not ML.')
with forecast_tab:
    st.subheader('Illustrative revenue projection')
    st.caption('Simple linear trend on monthly sales, for demonstration only. This is not a validated production forecast.')
    monthly=filtered.assign(month=filtered.order_date.dt.to_period('M').dt.to_timestamp()).groupby('month',as_index=False).revenue.sum().sort_values('month')
    if len(monthly)>=3:
        import numpy as np
        x=np.arange(len(monthly),dtype=float)
        slope,intercept=np.polyfit(x,monthly.revenue.to_numpy(dtype=float),1)
        future=pd.date_range(monthly.month.iloc[-1]+pd.offsets.MonthBegin(1),periods=3,freq='MS')
        predicted=np.maximum(0,intercept+slope*np.arange(len(monthly),len(monthly)+3))
        future_df=pd.DataFrame({'month':future,'revenue':predicted,'series':'Projected'})
        historical=monthly.assign(series='Actual')
        st.plotly_chart(px.line(pd.concat([historical,future_df]),x='month',y='revenue',color='series',markers=True),width='stretch')
        st.dataframe(future_df.rename(columns={'month':'Month','revenue':'Projected revenue'}),hide_index=True,width='stretch')
    else:
        st.info('Select at least three months of transactions to see the trend projection.')
with data_tab:
    st.dataframe(filtered.sort_values('order_date',ascending=False),width='stretch',hide_index=True)
    st.download_button('Download filtered transactions',filtered.to_csv(index=False),'retail_transactions.csv','text/csv')
