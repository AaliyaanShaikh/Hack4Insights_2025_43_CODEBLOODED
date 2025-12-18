"""
Data cleaning module for BearCart e-commerce data (Maven Fuzzy Factory schema).

This module reads the raw CSVs from the Maven Fuzzy Factory dataset and:
- Cleans each raw table (sessions, pageviews, orders, order_items, refunds, products)
- Builds *normalized* analytical tables:
  - `sessions.csv`   (session-level, with marketing channel & device)
  - `orders.csv`     (order-level, with revenue and items)
  - `products.csv`   (product lookup)
  - `refunds.csv`    (order-level refunds)

The normalized tables are written to `data/cleaned/` and are what the
rest of the backend/frontend code consumes.
"""
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _derive_channel(row: pd.Series) -> str:
    """
    Derive a business-friendly marketing channel from Maven Fuzzy Factory fields.

    Business logic (simplified and explainable for executives):
    - Paid Search: utm_source in {gsearch, bing} (nonbrand/brand)
    - Email: utm_source == 'email'
    - Social: utm_source in {facebook, twitter}
    - Direct: no utm_source and no external http_referer
    - Referral: everything else with a non-null http_referer
    """
    utm_source = str(row.get("utm_source") or "").lower()
    utm_campaign = str(row.get("utm_campaign") or "").lower()
    http_referer = str(row.get("http_referer") or "")

    if utm_source in {"gsearch", "bing"}:
        return "Paid Search"
    if utm_source == "email":
        return "Email"
    if utm_source in {"facebook", "twitter"}:
        return "Social"

    # No UTM parameters – check referrer
    if not utm_source:
        if http_referer and "mavenfuzzyfactory" not in http_referer:
            return "Referral"
        return "Direct"

    # Fallback
    return utm_source.title() or "Other"


def clean_website_sessions(df: pd.DataFrame) -> pd.DataFrame:
    """Clean `website_sessions` raw table."""
    logger.info(f"Cleaning website_sessions: {len(df)} records")

    # Drop duplicate sessions
    initial = len(df)
    df = df.drop_duplicates(subset=["website_session_id"], keep="first")
    if len(df) != initial:
        logger.info(f"Removed {initial - len(df)} duplicate website sessions")

    # Parse timestamps
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df = df.dropna(subset=["created_at"])

    # Ensure basic types
    df["user_id"] = pd.to_numeric(df["user_id"], errors="coerce")
    df = df.dropna(subset=["user_id"])
    df["user_id"] = df["user_id"].astype(int)

    # Device type
    df["device_type"] = df["device_type"].fillna("unknown").str.title()

    # Derive high-level marketing channel
    df["channel"] = df.apply(_derive_channel, axis=1)

    # Flag repeat sessions as boolean
    if "is_repeat_session" in df.columns:
        df["is_repeat_session"] = df["is_repeat_session"].astype(int)

    logger.info(f"Cleaned website_sessions: {len(df)} records")
    return df


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Clean `orders` raw table."""
    logger.info(f"Cleaning orders: {len(df)} records")

    initial = len(df)
    df = df.drop_duplicates(subset=["order_id"], keep="first")
    if len(df) != initial:
        logger.info(f"Removed {initial - len(df)} duplicate orders")

    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df = df.dropna(subset=["created_at"])

    # Coerce numeric fields
    for col in ["price_usd", "cogs_usd"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["items_purchased"] = pd.to_numeric(df["items_purchased"], errors="coerce")

    # Drop records without revenue
    df = df.dropna(subset=["price_usd"])
    df["items_purchased"] = df["items_purchased"].fillna(1).clip(lower=1)

    # Ensure positive values
    df["price_usd"] = df["price_usd"].clip(lower=0)
    df["cogs_usd"] = df["cogs_usd"].clip(lower=0)

    logger.info(f"Cleaned orders: {len(df)} records")
    return df


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    """Clean `products` lookup table."""
    logger.info(f"Cleaning products: {len(df)} records")

    initial = len(df)
    df = df.drop_duplicates(subset=["product_id"], keep="first")
    if len(df) != initial:
        logger.info(f"Removed {initial - len(df)} duplicate products")

    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

    return df


def clean_order_items(df: pd.DataFrame) -> pd.DataFrame:
    """Clean `order_items` line-item table."""
    logger.info(f"Cleaning order_items: {len(df)} records")

    initial = len(df)
    df = df.drop_duplicates(subset=["order_item_id"], keep="first")
    if len(df) != initial:
        logger.info(f"Removed {initial - len(df)} duplicate order_items")

    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

    for col in ["price_usd", "cogs_usd"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).clip(lower=0)

    return df


def clean_order_item_refunds(df: pd.DataFrame) -> pd.DataFrame:
    """Clean `order_item_refunds` table."""
    logger.info(f"Cleaning order_item_refunds: {len(df)} records")

    initial = len(df)
    df = df.drop_duplicates(subset=["order_item_refund_id"], keep="first")
    if len(df) != initial:
        logger.info(f"Removed {initial - len(df)} duplicate order_item_refunds")

    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df = df.dropna(subset=["created_at"])

    df["refund_amount_usd"] = pd.to_numeric(df["refund_amount_usd"], errors="coerce")
    df = df.dropna(subset=["refund_amount_usd"])
    df["refund_amount_usd"] = df["refund_amount_usd"].clip(lower=0)

    return df


def build_normalized_sessions(website_sessions: pd.DataFrame) -> pd.DataFrame:
    """
    Build normalized `sessions` analytical table expected by the rest of the app.

    Output columns:
    - session_id
    - user_id
    - timestamp
    - channel
    - device
    - is_repeat_session
    """
    sessions = website_sessions.rename(
        columns={
            "website_session_id": "session_id",
            "created_at": "timestamp",
            "device_type": "device",
        }
    )[["session_id", "user_id", "timestamp", "channel", "device", "is_repeat_session"]]

    return sessions


def build_normalized_orders(orders: pd.DataFrame) -> pd.DataFrame:
    """
    Build normalized `orders` analytical table.

    Output columns:
    - order_id
    - session_id
    - user_id
    - order_date
    - total_amount
    - items_count
    """
    orders_norm = orders.rename(
        columns={
            "created_at": "order_date",
            "price_usd": "total_amount",
            "items_purchased": "items_count",
            "website_session_id": "session_id",
        }
    )

    # Some Maven exports store user_id as float – coerce to int where possible
    orders_norm["user_id"] = pd.to_numeric(orders_norm["user_id"], errors="coerce")
    orders_norm = orders_norm.dropna(subset=["user_id"])
    orders_norm["user_id"] = orders_norm["user_id"].astype(int)

    return orders_norm[
        ["order_id", "session_id", "user_id", "order_date", "total_amount", "items_count"]
    ]


def build_normalized_refunds(
    order_item_refunds: pd.DataFrame, orders: pd.DataFrame
) -> pd.DataFrame:
    """
    Build normalized `refunds` analytical table at the order level.

    We aggregate multiple item-level refunds per order into a single refund value.

    Output columns:
    - refund_id
    - order_id
    - refund_date
    - refund_amount
    - reason  (synthetic, always 'Refund')
    """
    # Sum refunds per order and use earliest refund date
    agg = (
        order_item_refunds.groupby("order_id", as_index=False)
        .agg(
            refund_amount=("refund_amount_usd", "sum"),
            refund_date=("created_at", "min"),
        )
        .reset_index(drop=True)
    )

    # Validate against order revenue: refund <= order value
    order_amounts = orders[["order_id", "price_usd"]].rename(
        columns={"price_usd": "order_amount"}
    )
    agg = agg.merge(order_amounts, on="order_id", how="left")

    invalid = agg[agg["refund_amount"] > agg["order_amount"]]
    if len(invalid) > 0:
        logger.warning(
            f"Removing {len(invalid)} refunds where refund_amount > order_amount"
        )
        agg = agg[agg["refund_amount"] <= agg["order_amount"]]

    agg["refund_id"] = agg["order_id"].astype(str)
    agg["reason"] = "Refund"

    return agg[["refund_id", "order_id", "refund_date", "refund_amount", "reason"]]


def clean_all_data(raw_data_dir: str = "data/raw", cleaned_data_dir: str = "data/cleaned"):
    """
    End-to-end cleaning + normalization pipeline.

    Reads Maven Fuzzy Factory raw tables from `data/raw/` and writes:
    - cleaned/raw-like tables (optional)
    - normalized analytical tables (sessions, orders, products, refunds) to `data/cleaned/`
    """
    project_root = Path(__file__).parent.parent
    raw_path = project_root / raw_data_dir
    cleaned_path = project_root / cleaned_data_dir
    cleaned_path.mkdir(parents=True, exist_ok=True)

    logger.info("Starting data cleaning & normalization for Maven Fuzzy Factory...")

    # --- Load raw tables ---
    website_sessions_raw = pd.read_csv(raw_path / "website_sessions.csv")
    website_pageviews_raw = pd.read_csv(raw_path / "website_pageviews.csv")
    orders_raw = pd.read_csv(raw_path / "orders.csv")
    order_items_raw = pd.read_csv(raw_path / "order_items.csv")
    order_item_refunds_raw = pd.read_csv(raw_path / "order_item_refunds.csv")
    products_raw = pd.read_csv(raw_path / "products.csv")

    # --- Clean raw tables ---
    website_sessions_clean = clean_website_sessions(website_sessions_raw)
    orders_clean = clean_orders(orders_raw)
    products_clean = clean_products(products_raw)
    order_items_clean = clean_order_items(order_items_raw)
    order_item_refunds_clean = clean_order_item_refunds(order_item_refunds_raw)

    # Optional: save cleaned raw-style tables for debugging
    website_sessions_clean.to_csv(cleaned_path / "website_sessions_clean.csv", index=False)
    website_pageviews_raw.to_csv(cleaned_path / "website_pageviews_clean.csv", index=False)
    orders_clean.to_csv(cleaned_path / "orders_raw_clean.csv", index=False)
    order_items_clean.to_csv(cleaned_path / "order_items_clean.csv", index=False)
    order_item_refunds_clean.to_csv(
        cleaned_path / "order_item_refunds_clean.csv", index=False
    )
    products_clean.to_csv(cleaned_path / "products_clean.csv", index=False)

    # --- Build normalized analytical tables expected by the dashboard ---
    sessions_norm = build_normalized_sessions(website_sessions_clean)
    orders_norm = build_normalized_orders(orders_clean)
    refunds_norm = build_normalized_refunds(order_item_refunds_clean, orders_clean)

    # Save normalized tables with the names expected by the rest of the codebase
    sessions_norm.to_csv(cleaned_path / "sessions.csv", index=False)
    orders_norm.to_csv(cleaned_path / "orders.csv", index=False)
    products_clean.to_csv(cleaned_path / "products.csv", index=False)
    refunds_norm.to_csv(cleaned_path / "refunds.csv", index=False)

    logger.info("Data cleaning & normalization completed successfully.")


if __name__ == "__main__":
    clean_all_data()

