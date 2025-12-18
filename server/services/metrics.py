import pandas as pd
import numpy as np
import logging
import os

logger = logging.getLogger(__name__)

class BearCartMetrics:
    """Calculate all KPIs for dashboard"""
    
    def __init__(self, data_dir=None):
        if data_dir:
            self.load_data(data_dir)
            
    def load_data(self, data_dir):
        """Load processed data into memory"""
        self.df_master = pd.read_csv(os.path.join(data_dir, 'master_dataset.csv'))
        self.df_orders = pd.read_csv(os.path.join(data_dir, 'orders_clean.csv'))
        
        # Load items
        items_path = os.path.join(data_dir, 'items_clean.csv')
        if os.path.exists(items_path):
             self.df_items = pd.read_csv(items_path)
        else:
             # Fallback to raw if not processed yet (backwards compat)
             raw_items_path = os.path.join(data_dir, '../../raw/order_items.csv')
             if os.path.exists(raw_items_path):
                 self.df_items = pd.read_csv(raw_items_path)
             else:
                 logger.warning("Items data not found, product metrics will be limited.")
                 self.df_items = pd.DataFrame()
             
    def traffic_metrics(self):
        """Traffic and engagement KPIs"""
        df = self.df_master
        return {
            'total_sessions': int(len(df)),
            'unique_users': int(df['user_id'].nunique()) if 'user_id' in df.columns else 0,
            'sessions_by_channel': df['traffic_channel'].value_counts().to_dict(),
            'total_pageviews': int(df['total_pageviews'].sum()) if 'total_pageviews' in df.columns else 0,
        }
    
    def conversion_metrics(self):
        """Conversion funnel KPIs"""
        df = self.df_master
        total_sessions = len(df)
        converted = df['conversion_flag'].sum()
        
        # Funnel Analysis
        funnel = {}
        if 'step_home' in df.columns:
            funnel = {
                'sessions': int(df['step_home'].sum()), # Approx total sessions landing or hitting home
                'products': int(df['step_product'].sum()),
                'cart': int(df['step_cart'].sum()),
                'shipping': int(df['step_shipping'].sum()),
                'billing': int(df['step_billing'].sum()),
                'purchase': int(df['step_thankyou'].sum()), # Matches 'conversion_flag' ideally
            }
        
        return {
            'overall_conversion_rate': float(converted / total_sessions) if total_sessions > 0 else 0,
            'total_conversions': int(converted),
            'conversion_by_channel': df.groupby('traffic_channel')['conversion_flag'].mean().to_dict(),
            'conversion_by_device': df.groupby('device_type')['conversion_flag'].mean().to_dict() if 'device_type' in df.columns else {},
            'funnel_steps': funnel
        }
    
    def revenue_metrics(self):
        """Revenue and AOV KPIs"""
        df = self.df_master
        total_revenue = df['total_order_value'].sum()
        
        metrics = {
            'total_revenue': float(total_revenue),
            'average_order_value': float(df[df['converted'] == 1]['total_order_value'].mean() if len(df[df['converted'] == 1]) > 0 else 0),
            'revenue_per_session': float(total_revenue / len(df)) if len(df) > 0 else 0,
            'revenue_by_channel': df.groupby('traffic_channel')['total_order_value'].sum().to_dict(),
        }
        
        return metrics

    def product_metrics(self):
        """Product performance KPIs from items"""
        if self.df_items.empty:
            return {}
            
        # Group by product
        df_prod = self.df_items.groupby('product_name').agg({
            'product_id': 'count',
            'price_usd': 'sum',
            'margin_usd': 'sum'
        }).reset_index()
        
        df_prod = df_prod.rename(columns={'product_id': 'sales_count', 'price_usd': 'total_revenue', 'margin_usd': 'total_margin'})
        
        # Sort by revenue
        df_prod = df_prod.sort_values('total_revenue', ascending=False)
        
        # Calculates Refund Rate per Product (requires linkage to refunds)
        # Assuming we don't have item-level refund linkage here easily without another join.
        # Simple top products list
        
        return df_prod.to_dict('records') # List of dicts

    def quality_metrics(self):
        """Refund and customer health KPIs"""
        df = self.df_master
        
        refunded_sessions = df[df['was_refunded'] == 1].shape[0]
        converted_sessions = df[df['converted'] == 1].shape[0]
        total_refunds = df['was_refunded'].sum() # Simple count of refunded SESSIONS (approx orders)
        
        return {
            'overall_refund_rate': float(refunded_sessions / converted_sessions) if converted_sessions > 0 else 0,
            'total_refunds': int(total_refunds),
            'repeat_customer_rate': float((df['customer_segment'] == 'Returning').sum() / len(df)) if 'customer_segment' in df.columns else 0,
            'at_risk_segments': df[df['was_refunded'] == 1]['traffic_channel'].value_counts().head(5).to_dict(),
        }

    def get_dashboard_data(self):
        """Aggregate all metrics for frontend"""
        return {
            'traffic': self.traffic_metrics(),
            'conversion': self.conversion_metrics(),
            'revenue': self.revenue_metrics(),
            'quality': self.quality_metrics(),
            'products': self.product_metrics()
        }
