import pandas as pd

RFM_COLUMNS = ['customer_id','customer_name','recency','frequency','monetary']

def calculate_rfm(df):
    required = {'customer_id','customer_name','order_id','order_date','revenue'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f'Missing columns: {sorted(missing)}')
    if df.empty:
        return pd.DataFrame(columns=RFM_COLUMNS)
    data = df.copy()
    data['order_date'] = pd.to_datetime(data['order_date'])
    data['revenue'] = pd.to_numeric(data['revenue'])
    reference = data['order_date'].max() + pd.Timedelta(days=1)
    rfm = data.groupby(['customer_id','customer_name'],as_index=False).agg(last_purchase=('order_date','max'),frequency=('order_id','nunique'),monetary=('revenue','sum'))
    rfm['recency'] = (reference-rfm['last_purchase']).dt.days
    return rfm[RFM_COLUMNS]

def segment_customers(rfm):
    result = rfm.copy()
    for score in ['r_score','f_score','m_score']:
        result[score] = pd.Series(dtype=int) if result.empty else 0
    if result.empty:
        result['segment'] = pd.Series(dtype=str)
        return result
    # Percentile ranks avoid qcut failures with small filtered samples.
    for metric,score,ascending in [('recency','r_score',False),('frequency','f_score',True),('monetary','m_score',True)]:
        ranks = result[metric].rank(pct=True,method='average',ascending=ascending)
        result[score] = ((ranks * 5).apply(lambda x: max(1,min(5,int(__import__('math').ceil(x)))))).astype(int)
    def classify(row):
        r,f,m = row['r_score'],row['f_score'],row['m_score']
        if r>=4 and f>=4 and m>=4: return 'Champions'
        if r<=2 and f>=3: return 'At Risk'
        if f>=4: return 'Loyal Customers'
        if r>=4: return 'Recent Customers'
        return 'Needs Attention'
    result['segment'] = result.apply(classify,axis=1)
    return result
