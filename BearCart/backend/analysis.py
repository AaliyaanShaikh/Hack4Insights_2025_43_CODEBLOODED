"""
Analysis functions for BearCart analytics dashboard.
Provides aggregated data for visualizations.
"""
import pandas as pd
from typing import Optional, Dict, List
from .utils import load_data


def get_sessions_by_channel(sessions_df: Optional[pd.DataFrame] = None,
                           date_filter: Optional[tuple] = None) -> pd.DataFrame:
    """
    Get session counts by marketing channel.
    
    Args:
        sessions_df: Sessions DataFrame
        date_filter: Tuple of (start_date, end_date) for filtering
        
    Returns:
        DataFrame with channel and session_count
    """
    if sessions_df is None:
        sessions_df = load_data('sessions.csv')
    
    df = sessions_df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    if date_filter:
        start_date, end_date = date_filter
        df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
    
    result = df.groupby('channel', as_index=False).agg(
        session_count=('session_id', 'count')
    ).sort_values('session_count', ascending=False)
    
    return result


def get_sessions_by_device(sessions_df: Optional[pd.DataFrame] = None,
                          date_filter: Optional[tuple] = None) -> pd.DataFrame:
    """
    Get session counts by device type.
    
    Args:
        sessions_df: Sessions DataFrame
        date_filter: Tuple of (start_date, end_date) for filtering
        
    Returns:
        DataFrame with device and session_count
    """
    if sessions_df is None:
        sessions_df = load_data('sessions.csv')
    
    df = sessions_df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    if date_filter:
        start_date, end_date = date_filter
        df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
    
    result = df.groupby('device', as_index=False).agg(
        session_count=('session_id', 'count')
    ).sort_values('session_count', ascending=False)
    
    return result


def get_sessions_time_trend(sessions_df: Optional[pd.DataFrame] = None,
                           date_filter: Optional[tuple] = None,
                           freq: str = 'D') -> pd.DataFrame:
    """
    Get session counts over time.
    
    Args:
        sessions_df: Sessions DataFrame
        date_filter: Tuple of (start_date, end_date) for filtering
        freq: Frequency for grouping ('D' for daily, 'W' for weekly, 'M' for monthly)
        
    Returns:
        DataFrame with date and session_count
    """
    if sessions_df is None:
        sessions_df = load_data('sessions.csv')
    
    df = sessions_df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    
    if date_filter:
        start_date, end_date = date_filter
        df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
    
    # Group by date
    daily = df.groupby('date', as_index=False).agg(
        session_count=('session_id', 'count')
    )
    daily['date'] = pd.to_datetime(daily['date'])
    
    # Resample if needed
    if freq != 'D':
        daily = daily.set_index('date').resample(freq).sum().reset_index()
    
    return daily.sort_values('date')


def get_conversion_funnel(sessions_df: Optional[pd.DataFrame] = None,
                         orders_df: Optional[pd.DataFrame] = None,
                         date_filter: Optional[tuple] = None) -> pd.DataFrame:
    """
    Get conversion funnel data (sessions -> orders).
    
    Args:
        sessions_df: Sessions DataFrame
        orders_df: Orders DataFrame
        date_filter: Tuple of (start_date, end_date) for filtering
        
    Returns:
        DataFrame with funnel stage and count
    """
    if sessions_df is None:
        sessions_df = load_data('sessions.csv')
    if orders_df is None:
        orders_df = load_data('orders.csv')
    
    sessions_df = sessions_df.copy()
    orders_df = orders_df.copy()
    
    sessions_df['timestamp'] = pd.to_datetime(sessions_df['timestamp'])
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
    
    if date_filter:
        start_date, end_date = date_filter
        sessions_df = sessions_df[
            (sessions_df['timestamp'] >= start_date) & 
            (sessions_df['timestamp'] <= end_date)
        ]
        orders_df = orders_df[
            (orders_df['order_date'] >= start_date) & 
            (orders_df['order_date'] <= end_date)
        ]
    
    total_sessions = len(sessions_df)
    converting_sessions = set(orders_df['session_id'].unique())
    total_orders = len(orders_df)
    
    funnel_data = pd.DataFrame({
        'stage': ['Sessions', 'Orders'],
        'count': [total_sessions, total_orders]
    })
    
    return funnel_data


def get_conversion_by_channel(sessions_df: Optional[pd.DataFrame] = None,
                              orders_df: Optional[pd.DataFrame] = None,
                              date_filter: Optional[tuple] = None) -> pd.DataFrame:
    """
    Get conversion rate by marketing channel.
    
    Args:
        sessions_df: Sessions DataFrame
        orders_df: Orders DataFrame
        date_filter: Tuple of (start_date, end_date) for filtering
        
    Returns:
        DataFrame with channel, sessions, orders, and conversion_rate
    """
    if sessions_df is None:
        sessions_df = load_data('sessions.csv')
    if orders_df is None:
        orders_df = load_data('orders.csv')
    
    sessions_df = sessions_df.copy()
    orders_df = orders_df.copy()
    
    sessions_df['timestamp'] = pd.to_datetime(sessions_df['timestamp'])
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
    
    if date_filter:
        start_date, end_date = date_filter
        sessions_df = sessions_df[
            (sessions_df['timestamp'] >= start_date) & 
            (sessions_df['timestamp'] <= end_date)
        ]
        orders_df = orders_df[
            (orders_df['order_date'] >= start_date) & 
            (orders_df['order_date'] <= end_date)
        ]
    
    # Get sessions by channel
    sessions_by_channel = sessions_df.groupby('channel', as_index=False).agg(
        sessions=('session_id', 'count')
    )
    
    # Get orders by channel (via session_id)
    orders_by_channel = orders_df.merge(
        sessions_df[['session_id', 'channel']],
        on='session_id',
        how='left'
    )
    orders_by_channel = orders_by_channel.groupby('channel', as_index=False).agg(
        orders=('order_id', 'count')
    )
    
    # Merge and calculate conversion rate
    result = sessions_by_channel.merge(orders_by_channel, on='channel', how='left')
    result['orders'] = result['orders'].fillna(0)
    result['conversion_rate'] = (result['orders'] / result['sessions'] * 100).round(2)
    result = result.sort_values('conversion_rate', ascending=False)
    
    return result


def get_conversion_by_device(sessions_df: Optional[pd.DataFrame] = None,
                            orders_df: Optional[pd.DataFrame] = None,
                            date_filter: Optional[tuple] = None) -> pd.DataFrame:
    """
    Get conversion rate by device type.
    
    Args:
        sessions_df: Sessions DataFrame
        orders_df: Orders DataFrame
        date_filter: Tuple of (start_date, end_date) for filtering
        
    Returns:
        DataFrame with device, sessions, orders, and conversion_rate
    """
    if sessions_df is None:
        sessions_df = load_data('sessions.csv')
    if orders_df is None:
        orders_df = load_data('orders.csv')
    
    sessions_df = sessions_df.copy()
    orders_df = orders_df.copy()
    
    sessions_df['timestamp'] = pd.to_datetime(sessions_df['timestamp'])
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
    
    if date_filter:
        start_date, end_date = date_filter
        sessions_df = sessions_df[
            (sessions_df['timestamp'] >= start_date) & 
            (sessions_df['timestamp'] <= end_date)
        ]
        orders_df = orders_df[
            (orders_df['order_date'] >= start_date) & 
            (orders_df['order_date'] <= end_date)
        ]
    
    # Get sessions by device
    sessions_by_device = sessions_df.groupby('device', as_index=False).agg(
        sessions=('session_id', 'count')
    )
    
    # Get orders by device (via session_id)
    orders_by_device = orders_df.merge(
        sessions_df[['session_id', 'device']],
        on='session_id',
        how='left'
    )
    orders_by_device = orders_by_device.groupby('device', as_index=False).agg(
        orders=('order_id', 'count')
    )
    
    # Merge and calculate conversion rate
    result = sessions_by_device.merge(orders_by_device, on='device', how='left')
    result['orders'] = result['orders'].fillna(0)
    result['conversion_rate'] = (result['orders'] / result['sessions'] * 100).round(2)
    result = result.sort_values('conversion_rate', ascending=False)
    
    return result


def get_revenue_trends(orders_df: Optional[pd.DataFrame] = None,
                      date_filter: Optional[tuple] = None,
                      freq: str = 'D') -> pd.DataFrame:
    """
    Get revenue trends over time.
    
    Args:
        orders_df: Orders DataFrame
        date_filter: Tuple of (start_date, end_date) for filtering
        freq: Frequency for grouping ('D' for daily, 'W' for weekly, 'M' for monthly)
        
    Returns:
        DataFrame with date and revenue
    """
    if orders_df is None:
        orders_df = load_data('orders.csv')
    
    df = orders_df.copy()
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['date'] = df['order_date'].dt.date
    
    if date_filter:
        start_date, end_date = date_filter
        df = df[(df['order_date'] >= start_date) & (df['order_date'] <= end_date)]
    
    # Group by date
    daily = df.groupby('date', as_index=False).agg(
        revenue=('total_amount', 'sum'),
        orders=('order_id', 'count')
    )
    daily['date'] = pd.to_datetime(daily['date'])
    
    # Resample if needed
    if freq != 'D':
        daily = daily.set_index('date').resample(freq).agg({
            'revenue': 'sum',
            'orders': 'sum'
        }).reset_index()
    
    return daily.sort_values('date')


def get_aov_by_category(orders_df: Optional[pd.DataFrame] = None,
                        products_df: Optional[pd.DataFrame] = None,
                        date_filter: Optional[tuple] = None) -> pd.DataFrame:
    """
    Get Average Order Value by product category.
    Note: This requires order_items data. For now, we'll use a simplified approach.
    
    Args:
        orders_df: Orders DataFrame
        products_df: Products DataFrame
        date_filter: Tuple of (start_date, end_date) for filtering
        
    Returns:
        DataFrame with category and aov
    """
    if orders_df is None:
        orders_df = load_data('orders.csv')
    
    # Since we don't have order_items, we'll calculate overall AOV
    # In a real scenario, you'd join orders -> order_items -> products
    df = orders_df.copy()
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    if date_filter:
        start_date, end_date = date_filter
        df = df[(df['order_date'] >= start_date) & (df['order_date'] <= end_date)]
    
    # For this simplified version, return overall AOV
    # In production, you'd join with order_items and products
    overall_aov = df['total_amount'].mean()
    
    result = pd.DataFrame({
        'category': ['All Categories'],
        'aov': [overall_aov]
    })
    
    return result


def get_refund_analysis(refunds_df: Optional[pd.DataFrame] = None,
                        orders_df: Optional[pd.DataFrame] = None,
                        products_df: Optional[pd.DataFrame] = None,
                        date_filter: Optional[tuple] = None) -> Dict:
    """
    Get comprehensive refund analysis.
    
    Args:
        refunds_df: Refunds DataFrame
        orders_df: Orders DataFrame
        products_df: Products DataFrame
        date_filter: Tuple of (start_date, end_date) for filtering
        
    Returns:
        Dictionary with refund statistics
    """
    if refunds_df is None:
        refunds_df = load_data('refunds.csv')
    if orders_df is None:
        orders_df = load_data('orders.csv')
    
    refunds_df = refunds_df.copy()
    orders_df = orders_df.copy()
    
    refunds_df['refund_date'] = pd.to_datetime(refunds_df['refund_date'])
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
    
    if date_filter:
        start_date, end_date = date_filter
        refunds_df = refunds_df[
            (refunds_df['refund_date'] >= start_date) & 
            (refunds_df['refund_date'] <= end_date)
        ]
        orders_df = orders_df[
            (orders_df['order_date'] >= start_date) & 
            (orders_df['order_date'] <= end_date)
        ]
    
    # Refunds by reason
    refunds_by_reason = refunds_df.groupby('reason', as_index=False).agg(
        refund_count=('refund_id', 'count'),
        refund_value=('refund_amount', 'sum')
    ).sort_values('refund_value', ascending=False)
    
    # Refund trend over time
    refunds_df['date'] = refunds_df['refund_date'].dt.date
    refund_trend = refunds_df.groupby('date', as_index=False).agg(
        refund_count=('refund_id', 'count'),
        refund_value=('refund_amount', 'sum')
    )
    refund_trend['date'] = pd.to_datetime(refund_trend['date'])
    refund_trend = refund_trend.sort_values('date')
    
    return {
        'by_reason': refunds_by_reason,
        'trend': refund_trend
    }

