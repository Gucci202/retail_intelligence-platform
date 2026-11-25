from pathlib import Path
import pandas as pd
from src.database import get_connection

ROOT = Path(__file__).resolve().parents[1]

def load_transactions():
    """Use local MySQL when configured; otherwise use reproducible CSV demo data."""
    import os
    if os.getenv('DB_PASSWORD'):
        connection = get_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute('''SELECT o.order_id, o.order_date, c.customer_id, c.customer_name,
                       c.region, p.product_name, p.category, o.quantity, o.revenue
                       FROM orders o JOIN customers c ON o.customer_id=c.customer_id
                       JOIN products p ON o.product_id=p.product_id''')
                rows = cursor.fetchall()
            finally:
                cursor.close()
        finally:
            connection.close()
        data = pd.DataFrame(rows)
    else:
        paths = [ROOT/'data'/f'{name}.csv' for name in ('customers','products','orders')]
        missing = [str(path) for path in paths if not path.exists()]
        if missing:
            raise FileNotFoundError('Demo data is missing: '+', '.join(missing))
        customers, products, orders = (pd.read_csv(path) for path in paths)
        data = orders.merge(customers[['customer_id','customer_name','region']],on='customer_id',validate='many_to_one').merge(products[['product_id','product_name','category']],on='product_id',validate='many_to_one')
    if data.empty:
        return pd.DataFrame(columns=['order_id','order_date','customer_id','customer_name','region','product_name','category','quantity','revenue'])
    data['order_date'] = pd.to_datetime(data['order_date'],errors='raise')
    data['revenue'] = pd.to_numeric(data['revenue'],errors='raise')
    data['quantity'] = pd.to_numeric(data['quantity'],errors='raise')
    return data
