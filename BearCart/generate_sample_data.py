"""
Script to generate sample e-commerce data for BearCart project.
Run this once to create the initial data files.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Get project root directory
script_dir = Path(__file__).parent
raw_data_dir = script_dir / 'data' / 'raw'
raw_data_dir.mkdir(parents=True, exist_ok=True)

# Generate date range (last 90 days)
end_date = datetime.now()
start_date = end_date - timedelta(days=90)
dates = pd.date_range(start_date, end_date, freq='D')

# Channels and devices
channels = ['Organic Search', 'Paid Search', 'Social Media', 'Email', 'Direct', 'Referral']
devices = ['Desktop', 'Mobile', 'Tablet']

# Generate sessions.csv
n_sessions = 5000
sessions_data = {
    'session_id': [f'SES_{i:06d}' for i in range(1, n_sessions + 1)],
    'user_id': [f'USER_{random.randint(1, 2000):06d}' for _ in range(n_sessions)],
    'timestamp': [random.choice(dates) + timedelta(
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    ) for _ in range(n_sessions)],
    'channel': [random.choice(channels) for _ in range(n_sessions)],
    'device': [random.choice(devices) for _ in range(n_sessions)],
    'session_duration': np.random.exponential(180, n_sessions).astype(int),  # seconds
    'page_views': np.random.poisson(5, n_sessions) + 1,
}

# Add some missing values and duplicates
sessions_df = pd.DataFrame(sessions_data)
sessions_df.loc[random.sample(range(n_sessions), 50), 'channel'] = None
sessions_df.loc[random.sample(range(n_sessions), 30), 'device'] = None
# Add duplicates
sessions_df = pd.concat([sessions_df, sessions_df.sample(100)], ignore_index=True)

sessions_df.to_csv(raw_data_dir / 'sessions.csv', index=False)

# Generate orders.csv (subset of sessions convert)
n_orders = int(n_sessions * 0.15)  # ~15% conversion rate
order_sessions = random.sample(range(n_sessions), n_orders)

orders_data = {
    'order_id': [f'ORD_{i:06d}' for i in range(1, n_orders + 1)],
    'session_id': [sessions_data['session_id'][i] for i in order_sessions],
    'user_id': [sessions_data['user_id'][i] for i in order_sessions],
    'order_date': [sessions_data['timestamp'][i] + timedelta(minutes=random.randint(1, 30)) for i in order_sessions],
    'total_amount': np.round(np.random.lognormal(4, 0.8, n_orders), 2),
    'items_count': np.random.poisson(2, n_orders) + 1,
}

orders_df = pd.DataFrame(orders_data)
# Add some missing values
orders_df.loc[random.sample(range(n_orders), 20), 'items_count'] = None
orders_df.to_csv(raw_data_dir / 'orders.csv', index=False)

# Generate products.csv
categories = ['Electronics', 'Clothing', 'Home & Garden', 'Books', 'Sports', 'Toys']
n_products = 200

products_data = {
    'product_id': [f'PROD_{i:04d}' for i in range(1, n_products + 1)],
    'product_name': [f'Product {i}' for i in range(1, n_products + 1)],
    'category': [random.choice(categories) for _ in range(n_products)],
    'price': np.round(np.random.uniform(10, 500, n_products), 2),
    'stock_quantity': np.random.randint(0, 1000, n_products),
}

products_df = pd.DataFrame(products_data)
products_df.loc[random.sample(range(n_products), 15), 'category'] = None
products_df.to_csv(raw_data_dir / 'products.csv', index=False)

# Generate refunds.csv (subset of orders)
n_refunds = int(n_orders * 0.08)  # ~8% refund rate
refund_orders = random.sample(range(n_orders), n_refunds)

refunds_data = {
    'refund_id': [f'REF_{i:05d}' for i in range(1, n_refunds + 1)],
    'order_id': [orders_data['order_id'][i] for i in refund_orders],
    'refund_date': [orders_data['order_date'][i] + timedelta(days=random.randint(1, 14)) for i in refund_orders],
    'refund_amount': [min(orders_data['total_amount'][i], np.random.uniform(5, orders_data['total_amount'][i])) for i in refund_orders],
    'reason': [random.choice(['Defective', 'Wrong Item', 'Not as Described', 'Customer Request', 'Late Delivery']) for _ in range(n_refunds)],
}

refunds_df = pd.DataFrame(refunds_data)
refunds_df['refund_amount'] = np.round(refunds_df['refund_amount'], 2)
# Add some invalid refunds (refund > order amount) for data cleaning to catch
refunds_df.loc[random.sample(range(n_refunds), 5), 'refund_amount'] = refunds_df.loc[random.sample(range(n_refunds), 5), 'refund_amount'] * 1.5
refunds_df.to_csv(raw_data_dir / 'refunds.csv', index=False)

print("Sample data files generated successfully!")
print(f"- Sessions: {n_sessions} records")
print(f"- Orders: {n_orders} records")
print(f"- Products: {n_products} records")
print(f"- Refunds: {n_refunds} records")

