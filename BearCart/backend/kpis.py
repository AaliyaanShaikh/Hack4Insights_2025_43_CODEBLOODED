"""
KPI calculation functions for BearCart analytics.
All calculations use Pandas - no hardcoded values.
"""
import pandas as pd
from typing import Optional
from .utils import load_data


def calculate_total_sessions(sessions_df: Optional[pd.DataFrame] = None, 
                            date_filter: Optional[tuple] = None,
                            channel_filter: Optional[str] = None,
                            device_filter: Optional[str] = None) -> int:
    """
    Calculate total number of sessions.
    
    Args:
        sessions_df: Sessions DataFrame (if None, loads from file)
        date_filter: Tuple of (start_date, end_date) for filtering
        channel_filter: Filter by channel name
        device_filter: Filter by device type
        
    Returns:
        Total number of sessions
    """
    if sessions_df is None:
        sessions_df = load_data('sessions.csv')
    
    df = sessions_df.copy()
    
    # Apply filters
    if date_filter:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        start_date, end_date = date_filter
        df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
    
    if channel_filter:
        df = df[df['channel'] == channel_filter]
    
    if device_filter:
        df = df[df['device'] == device_filter]
    
    return len(df)


def calculate_total_orders(orders_df: Optional[pd.DataFrame] = None,
                          date_filter: Optional[tuple] = None) -> int:
    """
    Calculate total number of orders.
    
    Args:
        orders_df: Orders DataFrame (if None, loads from file)
        date_filter: Tuple of (start_date, end_date) for filtering
        
    Returns:
        Total number of orders
    """
    if orders_df is None:
        orders_df = load_data('orders.csv')
    
    df = orders_df.copy()
    
    if date_filter:
        df['order_date'] = pd.to_datetime(df['order_date'])
        start_date, end_date = date_filter
        df = df[(df['order_date'] >= start_date) & (df['order_date'] <= end_date)]
    
    return len(df)


def calculate_conversion_rate(sessions_df: Optional[pd.DataFrame] = None,
                             orders_df: Optional[pd.DataFrame] = None,
                             date_filter: Optional[tuple] = None,
                             channel_filter: Optional[str] = None,
                             device_filter: Optional[str] = None) -> float:
    """
    Calculate session-to-order conversion rate.
    
    Args:
        sessions_df: Sessions DataFrame
        orders_df: Orders DataFrame
        date_filter: Tuple of (start_date, end_date) for filtering
        channel_filter: Filter by channel name
        device_filter: Filter by device type
        
    Returns:
        Conversion rate as percentage (0-100)
    """
    if sessions_df is None:
        sessions_df = load_data('sessions.csv')
    if orders_df is None:
        orders_df = load_data('orders.csv')
    
    # Get filtered sessions
    sessions_count = calculate_total_sessions(sessions_df, date_filter, channel_filter, device_filter)
    
    if sessions_count == 0:
        return 0.0
    
    # Get orders from sessions that match filters
    orders_df = orders_df.copy()
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
    
    # Merge orders with sessions to get channel/device info
    sessions_filtered = sessions_df.copy()
    sessions_filtered['timestamp'] = pd.to_datetime(sessions_filtered['timestamp'])
    
    if date_filter:
        start_date, end_date = date_filter
        sessions_filtered = sessions_filtered[
            (sessions_filtered['timestamp'] >= start_date) & 
            (sessions_filtered['timestamp'] <= end_date)
        ]
        orders_df = orders_df[
            (orders_df['order_date'] >= start_date) & 
            (orders_df['order_date'] <= end_date)
        ]
    
    if channel_filter:
        sessions_filtered = sessions_filtered[sessions_filtered['channel'] == channel_filter]
    
    if device_filter:
        sessions_filtered = sessions_filtered[sessions_filtered['device'] == device_filter]
    
    # Count orders from filtered sessions
    valid_sessions = set(sessions_filtered['session_id'])
    orders_count = len(orders_df[orders_df['session_id'].isin(valid_sessions)])
    
    return (orders_count / sessions_count) * 100 if sessions_count > 0 else 0.0


def calculate_revenue(orders_df: Optional[pd.DataFrame] = None,
                     date_filter: Optional[tuple] = None) -> float:
    """
    Calculate total revenue.
    
    Args:
        orders_df: Orders DataFrame (if None, loads from file)
        date_filter: Tuple of (start_date, end_date) for filtering
        
    Returns:
        Total revenue
    """
    if orders_df is None:
        orders_df = load_data('orders.csv')
    
    df = orders_df.copy()
    
    if date_filter:
        df['order_date'] = pd.to_datetime(df['order_date'])
        start_date, end_date = date_filter
        df = df[(df['order_date'] >= start_date) & (df['order_date'] <= end_date)]
    
    return float(df['total_amount'].sum())


def calculate_average_order_value(orders_df: Optional[pd.DataFrame] = None,
                                 date_filter: Optional[tuple] = None) -> float:
    """
    Calculate Average Order Value (AOV).
    
    Args:
        orders_df: Orders DataFrame (if None, loads from file)
        date_filter: Tuple of (start_date, end_date) for filtering
        
    Returns:
        Average order value
    """
    if orders_df is None:
        orders_df = load_data('orders.csv')
    
    df = orders_df.copy()
    
    if date_filter:
        df['order_date'] = pd.to_datetime(df['order_date'])
        start_date, end_date = date_filter
        df = df[(df['order_date'] >= start_date) & (df['order_date'] <= end_date)]
    
    if len(df) == 0:
        return 0.0
    
    return float(df['total_amount'].mean())


def calculate_revenue_per_session(sessions_df: Optional[pd.DataFrame] = None,
                                 orders_df: Optional[pd.DataFrame] = None,
                                 date_filter: Optional[tuple] = None,
                                 channel_filter: Optional[str] = None,
                                 device_filter: Optional[str] = None) -> float:
    """
    Calculate revenue per session.
    
    Args:
        sessions_df: Sessions DataFrame
        orders_df: Orders DataFrame
        date_filter: Tuple of (start_date, end_date) for filtering
        channel_filter: Filter by channel name
        device_filter: Filter by device type
        
    Returns:
        Revenue per session
    """
    revenue = calculate_revenue(orders_df, date_filter)
    sessions = calculate_total_sessions(sessions_df, date_filter, channel_filter, device_filter)
    
    return revenue / sessions if sessions > 0 else 0.0


def calculate_refund_rate(orders_df: Optional[pd.DataFrame] = None,
                         refunds_df: Optional[pd.DataFrame] = None,
                         date_filter: Optional[tuple] = None) -> float:
    """
    Calculate refund rate (percentage of orders refunded).
    
    Args:
        orders_df: Orders DataFrame
        refunds_df: Refunds DataFrame
        date_filter: Tuple of (start_date, end_date) for filtering
        
    Returns:
        Refund rate as percentage (0-100)
    """
    if orders_df is None:
        orders_df = load_data('orders.csv')
    if refunds_df is None:
        refunds_df = load_data('refunds.csv')
    
    orders_df = orders_df.copy()
    refunds_df = refunds_df.copy()
    
    if date_filter:
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
        refunds_df['refund_date'] = pd.to_datetime(refunds_df['refund_date'])
        start_date, end_date = date_filter
        orders_df = orders_df[
            (orders_df['order_date'] >= start_date) & 
            (orders_df['order_date'] <= end_date)
        ]
        refunds_df = refunds_df[
            (refunds_df['refund_date'] >= start_date) & 
            (refunds_df['refund_date'] <= end_date)
        ]
    
    total_orders = len(orders_df)
    if total_orders == 0:
        return 0.0
    
    refunded_orders = len(refunds_df['order_id'].unique())
    return (refunded_orders / total_orders) * 100


def calculate_refund_value(refunds_df: Optional[pd.DataFrame] = None,
                          date_filter: Optional[tuple] = None) -> float:
    """
    Calculate total refund value.
    
    Args:
        refunds_df: Refunds DataFrame (if None, loads from file)
        date_filter: Tuple of (start_date, end_date) for filtering
        
    Returns:
        Total refund value
    """
    if refunds_df is None:
        refunds_df = load_data('refunds.csv')
    
    df = refunds_df.copy()
    
    if date_filter:
        df['refund_date'] = pd.to_datetime(df['refund_date'])
        start_date, end_date = date_filter
        df = df[(df['refund_date'] >= start_date) & (df['refund_date'] <= end_date)]
    
    return float(df['refund_amount'].sum())

