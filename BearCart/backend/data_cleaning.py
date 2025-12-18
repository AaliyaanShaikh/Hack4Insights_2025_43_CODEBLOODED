"""
Data cleaning module for BearCart e-commerce data.
Handles duplicates, missing values, data type conversions, and validation.
"""
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_sessions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean sessions data.
    
    Args:
        df: Raw sessions DataFrame
        
    Returns:
        Cleaned sessions DataFrame
    """
    logger.info(f"Cleaning sessions data: {len(df)} records")
    
    # Remove duplicates
    initial_count = len(df)
    df = df.drop_duplicates(subset=['session_id'], keep='first')
    duplicates_removed = initial_count - len(df)
    if duplicates_removed > 0:
        logger.info(f"Removed {duplicates_removed} duplicate sessions")
    
    # Handle missing values
    # Fill missing channel with 'Unknown'
    df['channel'] = df['channel'].fillna('Unknown')
    
    # Fill missing device with 'Unknown'
    df['device'] = df['device'].fillna('Unknown')
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    # Remove rows with invalid timestamps
    df = df.dropna(subset=['timestamp'])
    
    # Ensure numeric columns are correct type
    df['session_duration'] = pd.to_numeric(df['session_duration'], errors='coerce')
    df['page_views'] = pd.to_numeric(df['page_views'], errors='coerce')
    
    # Fill missing numeric values with 0
    df['session_duration'] = df['session_duration'].fillna(0)
    df['page_views'] = df['page_views'].fillna(0)
    
    # Ensure positive values
    df['session_duration'] = df['session_duration'].clip(lower=0)
    df['page_views'] = df['page_views'].clip(lower=0)
    
    logger.info(f"Cleaned sessions data: {len(df)} records")
    return df


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean orders data.
    
    Args:
        df: Raw orders DataFrame
        
    Returns:
        Cleaned orders DataFrame
    """
    logger.info(f"Cleaning orders data: {len(df)} records")
    
    # Remove duplicates
    initial_count = len(df)
    df = df.drop_duplicates(subset=['order_id'], keep='first')
    duplicates_removed = initial_count - len(df)
    if duplicates_removed > 0:
        logger.info(f"Removed {duplicates_removed} duplicate orders")
    
    # Convert order_date to datetime
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    df = df.dropna(subset=['order_date'])
    
    # Ensure numeric columns
    df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce')
    df['items_count'] = pd.to_numeric(df['items_count'], errors='coerce')
    
    # Fill missing items_count with 1 (minimum)
    df['items_count'] = df['items_count'].fillna(1)
    
    # Remove orders with invalid amounts
    df = df.dropna(subset=['total_amount'])
    
    # Ensure positive values
    df['total_amount'] = df['total_amount'].clip(lower=0)
    df['items_count'] = df['items_count'].clip(lower=1)
    
    logger.info(f"Cleaned orders data: {len(df)} records")
    return df


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean products data.
    
    Args:
        df: Raw products DataFrame
        
    Returns:
        Cleaned products DataFrame
    """
    logger.info(f"Cleaning products data: {len(df)} records")
    
    # Remove duplicates
    initial_count = len(df)
    df = df.drop_duplicates(subset=['product_id'], keep='first')
    duplicates_removed = initial_count - len(df)
    if duplicates_removed > 0:
        logger.info(f"Removed {duplicates_removed} duplicate products")
    
    # Fill missing category with 'Uncategorized'
    df['category'] = df['category'].fillna('Uncategorized')
    
    # Ensure numeric columns
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['stock_quantity'] = pd.to_numeric(df['stock_quantity'], errors='coerce')
    
    # Fill missing values
    df['price'] = df['price'].fillna(0)
    df['stock_quantity'] = df['stock_quantity'].fillna(0)
    
    # Ensure positive values
    df['price'] = df['price'].clip(lower=0)
    df['stock_quantity'] = df['stock_quantity'].clip(lower=0)
    
    logger.info(f"Cleaned products data: {len(df)} records")
    return df


def clean_refunds(df: pd.DataFrame, orders_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean refunds data and validate against orders.
    
    Args:
        df: Raw refunds DataFrame
        orders_df: Cleaned orders DataFrame for validation
        
    Returns:
        Cleaned refunds DataFrame
    """
    logger.info(f"Cleaning refunds data: {len(df)} records")
    
    # Remove duplicates
    initial_count = len(df)
    df = df.drop_duplicates(subset=['refund_id'], keep='first')
    duplicates_removed = initial_count - len(df)
    if duplicates_removed > 0:
        logger.info(f"Removed {duplicates_removed} duplicate refunds")
    
    # Convert refund_date to datetime
    df['refund_date'] = pd.to_datetime(df['refund_date'], errors='coerce')
    df = df.dropna(subset=['refund_date'])
    
    # Ensure numeric column
    df['refund_amount'] = pd.to_numeric(df['refund_amount'], errors='coerce')
    df = df.dropna(subset=['refund_amount'])
    
    # Validate refund amount <= order amount
    # Merge with orders to get order amounts
    order_amounts = orders_df[['order_id', 'total_amount']].set_index('order_id')
    df = df.merge(order_amounts, left_on='order_id', right_index=True, how='left')
    
    # Filter out refunds where refund_amount > total_amount
    invalid_refunds = df[df['refund_amount'] > df['total_amount']]
    if len(invalid_refunds) > 0:
        logger.warning(f"Removing {len(invalid_refunds)} refunds with amount > order amount")
        df = df[df['refund_amount'] <= df['total_amount']]
    
    # Ensure positive values
    df['refund_amount'] = df['refund_amount'].clip(lower=0)
    
    # Drop the temporary total_amount column
    df = df.drop(columns=['total_amount'], errors='ignore')
    
    # Fill missing reason with 'Other'
    df['reason'] = df['reason'].fillna('Other')
    
    logger.info(f"Cleaned refunds data: {len(df)} records")
    return df


def clean_all_data(raw_data_dir: str = 'data/raw', cleaned_data_dir: str = 'data/cleaned'):
    """
    Clean all data files and save to cleaned directory.
    
    Args:
        raw_data_dir: Directory containing raw data files (relative to project root)
        cleaned_data_dir: Directory to save cleaned data files (relative to project root)
    """
    # Get project root (BearCart directory)
    project_root = Path(__file__).parent.parent
    raw_path = project_root / raw_data_dir
    cleaned_path = project_root / cleaned_data_dir
    cleaned_path.mkdir(parents=True, exist_ok=True)
    
    logger.info("Starting data cleaning process...")
    
    # Clean sessions
    sessions_df = pd.read_csv(raw_path / 'sessions.csv')
    sessions_cleaned = clean_sessions(sessions_df)
    sessions_cleaned.to_csv(cleaned_path / 'sessions.csv', index=False)
    
    # Clean orders
    orders_df = pd.read_csv(raw_path / 'orders.csv')
    orders_cleaned = clean_orders(orders_df)
    orders_cleaned.to_csv(cleaned_path / 'orders.csv', index=False)
    
    # Clean products
    products_df = pd.read_csv(raw_path / 'products.csv')
    products_cleaned = clean_products(products_df)
    products_cleaned.to_csv(cleaned_path / 'products.csv', index=False)
    
    # Clean refunds (needs orders for validation)
    refunds_df = pd.read_csv(raw_path / 'refunds.csv')
    refunds_cleaned = clean_refunds(refunds_df, orders_cleaned)
    refunds_cleaned.to_csv(cleaned_path / 'refunds.csv', index=False)
    
    logger.info("Data cleaning completed successfully!")


if __name__ == '__main__':
    clean_all_data()

