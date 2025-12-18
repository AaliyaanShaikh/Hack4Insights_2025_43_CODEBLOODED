import pandas as pd
import numpy as np
from datetime import datetime
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BearCartDataCleaner:
    """Production-grade data cleaning for BearCart hackathon"""
    
    def __init__(self):
        self.cleaning_report = {}
        
    def load_and_profile(self, filepath):
        """Load data and create initial profile"""
        if not os.path.exists(filepath):
             logger.error(f"File not found: {filepath}")
             return None, {}

        df = pd.read_csv(filepath)
        profile = {
            'rows_initial': len(df),
            'columns': len(df.columns),
            'missing_pct': (df.isnull().sum() / len(df) * 100).to_dict(),
            'duplicates': df.duplicated().sum()
        }
        logger.info(f"Loaded {filepath}: {profile['rows_initial']} rows")
        return df, profile
    
    def clean_sessions(self, df_sessions):
        """Clean sessions table"""
        logger.info("🔍 Cleaning sessions table...")
        
        # Rename columns for consistency
        df_sessions = df_sessions.rename(columns={
            'website_session_id': 'session_id',
            'created_at': 'session_date',
            'utm_source': 'traffic_source'
        })
        
        # Remove duplicates
        duplicates = df_sessions.duplicated(subset=['session_id']).sum()
        df_sessions = df_sessions.drop_duplicates(subset=['session_id'])
        logger.info(f"  ✓ Removed {duplicates} duplicate sessions")
        
        # Fix date columns
        df_sessions['session_date'] = pd.to_datetime(df_sessions['session_date'], errors='coerce')
        
        # Handle traffic source nulls
        if 'traffic_source' in df_sessions.columns:
            df_sessions['traffic_source'] = df_sessions['traffic_source'].fillna('Direct')
        
        # Identify bots (time based logic requires session end time which we might not have, 
        # but we can check if there are multiple sessions from same IP/User in split second - not avail here)
        # For this dataset, we might not have 'session_duration' directly in raw. 
        # If raw doesn't have it, we skip bot filtering based on duration OR calculate it if we had pageviews.
        # Check if 'session_duration' exists? It was in the template but not in raw headers I saw.
        # I saw 'website_pageviews.csv' in the file list. Maybe duration comes from there? 
        # For now, I'll skip duration-based bot filtering if column missing.
        
        if 'session_duration' in df_sessions.columns:
             df_sessions['session_duration'] = pd.to_numeric(df_sessions['session_duration'], errors='coerce')
             bot_mask = (df_sessions['session_duration'] < 1) | (df_sessions['session_duration'] > 28800)
             bots_removed = bot_mask.sum()
             df_sessions = df_sessions[~bot_mask]
             logger.info(f"  ✓ Removed {bots_removed} suspected bot sessions")
             self.cleaning_report['sessions_removed_bots'] = int(bots_removed)
        else:
             logger.warning("  ⚠ 'session_duration' not found. Skipping bot filter.")
             self.cleaning_report['sessions_removed_bots'] = 0

        self.cleaning_report['sessions_duplicates'] = int(duplicates)
        return df_sessions
    
    def clean_orders(self, df_orders, df_sessions):
        """Clean orders table and validate against sessions"""
        logger.info("🔍 Cleaning orders table...")
        
        # Rename columns
        df_orders = df_orders.rename(columns={
            'created_at': 'order_date',
            'website_session_id': 'session_id',
            'price_usd': 'order_value'
        })

        # Remove orders with null IDs
        df_orders = df_orders[df_orders['order_id'].notna()]
        
        # Fix dates
        df_orders['order_date'] = pd.to_datetime(df_orders['order_date'], errors='coerce')
        
        # Ensure session_date is datetime
        if 'session_date' in df_sessions.columns:
             df_sessions['session_date'] = pd.to_datetime(df_sessions['session_date'])
        
             # Validate order_date >= session_date (merge required)
             df_merged = df_orders.merge(
                df_sessions[['session_id', 'session_date']], 
                on='session_id', 
                how='left'
             )
             
             # Filter where order is BEFORE session (impossible)
             # We allow some small buffer or exact match.
             invalid_dates = (df_merged['order_date'] < df_merged['session_date']).sum()
             # Only keep valid ones
             # Note: if session not found, we keep the order (left join gives NaT for session_date)
             # df_merged['session_date'].notna() logic?? 
             # Let's keep orders even if session missing for now, but filter invalid timestamps if both exist
             valid_date_mask = ~(df_merged['order_date'] < df_merged['session_date'])
             df_orders = df_orders[valid_date_mask]
             logger.info(f"  ✓ Removed {invalid_dates} orders with invalid timestamps")
        else:
             invalid_dates = 0

        # Clean order_value
        df_orders['order_value'] = pd.to_numeric(df_orders['order_value'], errors='coerce')
        
        # Remove negative orders
        negative_orders = (df_orders['order_value'] < 0).sum()
        df_orders = df_orders[df_orders['order_value'] >= 0]
        logger.info(f"  ✓ Removed {negative_orders} orders with negative values")
        
        # Create features
        df_orders['order_value_log'] = np.log1p(df_orders['order_value'])
        df_orders['high_value_order'] = (df_orders['order_value'] > 
                                         df_orders['order_value'].quantile(0.75)).astype(int)
        
        self.cleaning_report['orders_removed_date'] = int(invalid_dates)
        self.cleaning_report['orders_removed_negative'] = int(negative_orders)
        return df_orders
    
    def clean_refunds(self, df_refunds, df_orders):
        """Clean refunds and validate logic"""
        logger.info("🔍 Cleaning refunds table...")
        
        # Headers: order_item_refund_id, created_at, order_item_id, order_id, refund_amount_usd
        df_refunds = df_refunds.rename(columns={
            'created_at': 'refund_date'
        })

        # Validate refund_date >= order_date
        df_refunds['refund_date'] = pd.to_datetime(df_refunds['refund_date'])
        
        if 'order_date' in df_orders.columns:
            df_orders['order_date'] = pd.to_datetime(df_orders['order_date'])
            
            df_merged = df_refunds.merge(
                df_orders[['order_id', 'order_date']], 
                on='order_id', 
                how='left'
            )
            
            invalid_refunds = (df_merged['refund_date'] < df_merged['order_date']).sum()
            df_refunds = df_refunds[~(df_merged['refund_date'] < df_merged['order_date'])]
            logger.info(f"  ✓ Removed {invalid_refunds} invalid refunds (date mismatch)")
        else:
            invalid_refunds = 0
            
        # Group by order_id if multiple refunds per order exist (item level refunds)
        # We want to know if an ORDER was refunded.
        
        self.cleaning_report['refunds_removed'] = int(invalid_refunds)
        return df_refunds
    
    def clean_products(self, df_products):
        """Clean products tables"""
        logger.info("🔍 Cleaning products table...")
        
        # Standardize names
        df_products = df_products.rename(columns={
            'created_at': 'product_launch_date'
        })
        
        # Ensure ID format
        df_products['product_id'] = pd.to_numeric(df_products['product_id'], errors='coerce')
        df_products = df_products.dropna(subset=['product_id'])
        
        # Log count
        logger.info(f"  ✓ Processed {len(df_products)} products")
        return df_products

    def clean_order_items(self, df_items, df_orders, df_products):
        """Clean order items and enrich with product details"""
        logger.info("🔍 Cleaning order items...")
        
        # Basic Type Conversion
        df_items['price_usd'] = pd.to_numeric(df_items['price_usd'], errors='coerce').fillna(0)
        df_items['cogs_usd'] = pd.to_numeric(df_items['cogs_usd'], errors='coerce').fillna(0)
        
        # Calculate Margin
        df_items['margin_usd'] = df_items['price_usd'] - df_items['cogs_usd']
        
        # Join with Products to get Names
        df_items = df_items.merge(df_products[['product_id', 'product_name']], on='product_id', how='left')
        df_items['product_name'] = df_items['product_name'].fillna('Unknown Product')
        
        # Check against valid orders
        valid_orders = df_orders['order_id'].unique()
        original_len = len(df_items)
        df_items = df_items[df_items['order_id'].isin(valid_orders)]
        removed = original_len - len(df_items)
        
        if removed > 0:
            logger.info(f"  ✓ Removed {removed} orphan items (no matching order)")
            
        return df_items

    def clean_pageviews(self, df_pageviews):
        """Clean pageviews and pivot to session-level funnel flags"""
        logger.info("🔍 Cleaning pageviews...")
        
        # Drop nulls
        df_pageviews = df_pageviews.dropna(subset=['website_session_id', 'pageview_url'])
        
        # Identify Key Pages
        # Simple string matching for now based on typical urls
        # URLs from head: /home, /products, /the-original-mr-fuzzy, /cart, /shipping, /billing, /thank-you-for-your-order
        
        df_pageviews['is_home'] = df_pageviews['pageview_url'].apply(lambda x: 1 if x == '/home' else 0)
        df_pageviews['is_products'] = df_pageviews['pageview_url'].apply(lambda x: 1 if '/products' in str(x) else 0)
        df_pageviews['is_product_page'] = df_pageviews['pageview_url'].apply(lambda x: 1 if x not in ['/home', '/products', '/cart', '/shipping', '/billing', '/thank-you-for-your-order'] and '/products' not in str(x) else 0) # Rough logic for specific product pages if URL structure varies, but let's be specific for 'the-original-mr-fuzzy'
        
        # Better: Specific mapping if consistent
        df_pageviews['step_home'] = (df_pageviews['pageview_url'] == '/home').astype(int)
        df_pageviews['step_product'] = (df_pageviews['pageview_url'].str.contains('/the-original-mr-fuzzy') | df_pageviews['pageview_url'].str.contains('/products')).astype(int) # Treating generic products page as step? Or just specific items? Let's generic products list + item page as "Product Browsing"
        df_pageviews['step_cart'] = (df_pageviews['pageview_url'] == '/cart').astype(int)
        df_pageviews['step_shipping'] = (df_pageviews['pageview_url'] == '/shipping').astype(int)
        df_pageviews['step_billing'] = (df_pageviews['pageview_url'] == '/billing').astype(int)
        df_pageviews['step_thankyou'] = (df_pageviews['pageview_url'] == '/thank-you-for-your-order').astype(int)
        
        # Aggregate to Session
        df_funnel = df_pageviews.groupby('website_session_id').agg({
            'website_pageview_id': 'count', # Total views
            'step_home': 'max',
            'step_product': 'max',
            'step_cart': 'max',
            'step_shipping': 'max',
            'step_billing': 'max',
            'step_thankyou': 'max'
        }).reset_index()
        
        df_funnel = df_funnel.rename(columns={'website_pageview_id': 'total_pageviews', 'website_session_id': 'session_id'})
        
        logger.info(f"  ✓ Processed {len(df_funnel)} session funnel profiles")
        return df_funnel

    def create_master_dataset(self, df_sessions, df_orders, df_refunds, df_pageviews_agg=None):
        """Create unified master table for analysis
           args:
             df_sessions, df_orders, df_refunds
             df_pageviews_agg: (Optional) Pre-aggregated funnel data
        """
        logger.info("🔨 Creating master dataset...")
        
        # Sessions → Orders join
        df_master = df_sessions.copy()
        
        # Aggregating orders by session
        df_order_agg = df_orders.groupby('session_id').agg({
            'order_id': 'count',
            'order_value': ['sum', 'mean'],
            'order_date': 'first'
        }).reset_index()
        
        # Flatten MultiIndex columns
        df_order_agg.columns = ['session_id', 'orders_in_session', 'total_order_value', 
                               'avg_order_value', 'first_order_date']
        
        df_master = df_master.merge(df_order_agg, on='session_id', how='left')
        
        # Converison Flags
        df_master['converted'] = df_master['orders_in_session'].fillna(0) > 0
        df_master['conversion_flag'] = df_master['converted'].astype(int)
        
        # Funnel Data Integration
        if df_pageviews_agg is not None:
            df_master = df_master.merge(df_pageviews_agg, on='session_id', how='left')
            # Fill funnel steps with 0 for missing (means no pageviews recorded? unlikely if clean, but safest)
            funnel_cols = ['total_pageviews', 'step_home', 'step_product', 'step_cart', 'step_shipping', 'step_billing', 'step_thankyou']
            df_master[funnel_cols] = df_master[funnel_cols].fillna(0).astype(int)
        
        # Refunds join
        # Helper: Get refund status per order
        refund_order_ids = df_refunds['order_id'].unique()
        df_orders['was_refunded'] = df_orders['order_id'].isin(refund_order_ids).astype(int)
        
        # Now aggregate this back to session
        df_refund_agg = df_orders.groupby('session_id')['was_refunded'].max().reset_index()
        
        df_master = df_master.merge(df_refund_agg, on='session_id', how='left')
        df_master['was_refunded'] = df_master['was_refunded'].fillna(0).astype(int)
        
        # Fill numeric nulls
        df_master['orders_in_session'] = df_master['orders_in_session'].fillna(0)
        df_master['total_order_value'] = df_master['total_order_value'].fillna(0.0)
        
        logger.info(f"  ✓ Master dataset: {len(df_master)} sessions")
        return df_master
