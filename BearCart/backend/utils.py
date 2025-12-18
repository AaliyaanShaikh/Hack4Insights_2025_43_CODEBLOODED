"""
Utility functions for BearCart analytics backend.
"""
import pandas as pd
from pathlib import Path
from typing import Optional


def get_project_root() -> Path:
    """Get the BearCart project root directory."""
    # Get the directory containing this file (backend/)
    current_file = Path(__file__).resolve()
    # Go up one level to get BearCart/
    return current_file.parent.parent


def load_data(file_name: str, data_dir: str = 'data/cleaned') -> pd.DataFrame:
    """
    Load cleaned data from CSV file.
    
    Args:
        file_name: Name of the CSV file (e.g., 'sessions.csv')
        data_dir: Directory containing the data files (relative to project root)
        
    Returns:
        DataFrame with the loaded data
    """
    project_root = get_project_root()
    file_path = project_root / data_dir / file_name
    
    if not file_path.exists():
        # Fallback to raw data if cleaned doesn't exist
        file_path = project_root / 'data/raw' / file_name
    
    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    return pd.read_csv(file_path)


def format_currency(value: float) -> str:
    """Format a number as currency."""
    return f"${value:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format a number as percentage."""
    return f"{value:.{decimals}f}%"


def format_number(value: float, decimals: int = 0) -> str:
    """Format a number with thousand separators."""
    return f"{value:,.{decimals}f}"


def get_date_range(df: pd.DataFrame, date_column: str) -> tuple:
    """
    Get min and max dates from a DataFrame.
    
    Args:
        df: DataFrame containing date column
        date_column: Name of the date column
        
    Returns:
        Tuple of (min_date, max_date)
    """
    df[date_column] = pd.to_datetime(df[date_column])
    return df[date_column].min(), df[date_column].max()

