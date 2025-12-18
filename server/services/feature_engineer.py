import pandas as pd
import numpy as np
import logging
import os

logger = logging.getLogger(__name__)

class BearCartFeatureEngineer:
    """Feature engineering for BearCart"""
    
    def __init__(self):
        self.feature_report = {}

    def load_data(self, processed_dir, raw_dir):
        """Load necessary datasets"""
        df_master = pd.read_csv(os.path.join(processed_dir, 'master_dataset.csv'))
        df_sessions = pd.read_csv(os.path.join(processed_dir, 'sessions_clean.csv'))
        df_orders = pd.read_csv(os.path.join(processed_dir, 'orders_clean.csv'))
        # Load raw items for product info
        df_items = pd.read_csv(os.path.join(raw_dir, 'order_items.csv'))
        
        return df_master, df_sessions, df_orders, df_items

    def engineer_features(self, df_master, df_sessions, df_orders, df_items):
        logger.info("⚙️ Engineering features...")
        
        # 1. Traffic Channel Grouping
        # Logic: 
        # - utm_campaign = 'nonbrand'/'brand' -> 'Paid' (AdWords)
        # - utm_source = 'bsearch' / 'gsearch' -> 'Paid' if campaign exists, else checks
        # - social -> 'Social'
        # - null utm_source -> 'Direct'
        # - organic -> 'Organic'
        
        # Merge session info back to master if missing (master should have session columns)
        # Master was created from clean sessions, so it has traffic_source
        # But we need utm_campaign which might be in sessions_clean but not master if create_master dropped it?
        # create_master_dataset used df_sessions.copy() so it should have all columns.
        
        def define_channel(row):
            source = str(row.get('traffic_source', '')).lower()
            campaign = str(row.get('utm_campaign', '')).lower()
            
            if source == 'direct':
                return 'Direct'
            if 'gsearch' in source or 'bsearch' in source:
                if 'nonbrand' in campaign or 'brand' in campaign:
                    return 'Paid Search'
                return 'Organic Search' # approximation
            if 'social' in source:
                return 'Social'
            return 'Other'

        # Ensure utm_campaign is present. If master was built from sessions, it should be there.
        # If not, we merge it.
        if 'utm_campaign' not in df_master.columns:
             temp_sessions = df_sessions[['session_id', 'utm_campaign']]
             df_master = df_master.merge(temp_sessions, on='session_id', how='left')
             
        df_master['traffic_channel'] = df_master.apply(define_channel, axis=1)
        
        # 2. Customer Segments
        # is_repeat_session 0/1 -> New vs Returning
        if 'is_repeat_session' in df_master.columns:
            df_master['customer_segment'] = df_master['is_repeat_session'].map({0: 'New', 1: 'Returning'})
        
        # 3. Product Features (Risk Score)
        # We need refund rate per product.
        # Join Orders -> Items -> Product
        # And Refunds -> Items
        # Or easier: We have df_master with 'was_refunded' (session level).
        # We want granular product risk.
        # Let's calculate Product Risk Score and map it to session based on product viewed/bought?
        # If session converted, we know what they bought.
        
        # Calculate Product Refund Rates
        # Items table: order_item_id, order_id, product_id
        # Orders table: order_id, was_refunded (calculated in cleaner)
        
        # We need was_refunded at item level? NO, we have it at order level in cleaner.
        # Generally if order is refunded, we assume items are bad? Or partial?
        # Detailed refund logic: order_item_refunds links to order_item_id.
        # We didn't pass items to cleaner.clean_refunds.
        # Let's re-calculate refund rate per PRODUCT here.
        
        # Load refunds raw or rely on order level?
        # Better to do rough product refund rate:
        # Merge Items + Refund Info (we need to load refunds again or trust order level)
        # Simpler: Merge df_items with df_orders[['order_id', 'was_refunded']]
        # Group by product_id -> mean(was_refunded)
        
        df_items_merged = df_items.merge(df_orders[['order_id', 'was_refunded']], on='order_id', how='left')
        product_risk = df_items_merged.groupby('product_id')['was_refunded'].mean().to_dict()
        
        # Map back to master?
        # A session might have purchased multiple products. 
        # We can take "Max Risk" of purchased products.
        # First, join Items to Session via Order.
        df_session_items = df_items.merge(df_orders[['order_id', 'session_id']], on='order_id')
        df_session_items['product_risk'] = df_session_items['product_id'].map(product_risk)
        
        # Agg by session
        df_session_risk = df_session_items.groupby('session_id')['product_risk'].max().reset_index()
        df_session_risk.columns = ['session_id', 'max_product_risk']
        
        df_master = df_master.merge(df_session_risk, on='session_id', how='left')
        df_master['max_product_risk'] = df_master['max_product_risk'].fillna(0.0)
        
        # 4. Time Features
        df_master['session_date'] = pd.to_datetime(df_master['session_date'])
        df_master['hour_of_day'] = df_master['session_date'].dt.hour
        df_master['day_of_week'] = df_master['session_date'].dt.day_name()
        df_master['is_weekend'] = df_master['session_date'].dt.dayofweek >= 5
        
        self.feature_report['features_added'] = ['traffic_channel', 'customer_segment', 'max_product_risk', 'time_features']
        return df_master

