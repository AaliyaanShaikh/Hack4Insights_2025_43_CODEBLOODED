# BearCart Hackathon: Implementation Playbook
## Quick-Start Code Templates & Tactical Execution Guide

---

## 🔧 PART 1: DATA CLEANING PIPELINE (Python)

### Template: Production-Ready Cleaning Function

```python
import pandas as pd
import numpy as np
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BearCartDataCleaner:
    """Production-grade data cleaning for BearCart hackathon"""
    
    def __init__(self):
        self.cleaning_report = {}
        
    def load_and_profile(self, filepath):
        """Load data and create initial profile"""
        df = pd.read_csv(filepath)
        profile = {
            'rows_initial': len(df),
            'columns': len(df.columns),
            'missing_pct': (df.isnull().sum() / len(df) * 100).to_dict(),
            'duplicates': df.duplicated().sum()
        }
        logger.info(f"Loaded {filepath}: {profile['rows_initial']} rows, {profile['missing_pct']}")
        return df, profile
    
    def clean_sessions(self, df_sessions):
        """Clean sessions table"""
        logger.info("🔍 Cleaning sessions table...")
        
        # Remove duplicates
        duplicates = df_sessions.duplicated(subset=['session_id']).sum()
        df_sessions = df_sessions.drop_duplicates(subset=['session_id'])
        logger.info(f"  ✓ Removed {duplicates} duplicate sessions")
        
        # Fix date columns
        df_sessions['session_date'] = pd.to_datetime(df_sessions['session_date'], errors='coerce')
        
        # Handle traffic source nulls
        df_sessions['traffic_source'] = df_sessions['traffic_source'].fillna('Direct')
        
        # Remove bot traffic (< 1 second or > 8 hours)
        df_sessions['session_duration'] = pd.to_numeric(
            df_sessions['session_duration'], errors='coerce'
        )
        bot_mask = (df_sessions['session_duration'] < 1) | (df_sessions['session_duration'] > 28800)
        bots_removed = bot_mask.sum()
        df_sessions = df_sessions[~bot_mask]
        logger.info(f"  ✓ Removed {bots_removed} suspected bot sessions")
        
        # Outlier handling for session_duration
        q95 = df_sessions['session_duration'].quantile(0.95)
        df_sessions['session_duration_clean'] = df_sessions['session_duration'].clip(upper=q95)
        
        self.cleaning_report['sessions_removed'] = duplicates + bots_removed
        return df_sessions
    
    def clean_orders(self, df_orders, df_sessions):
        """Clean orders table and validate against sessions"""
        logger.info("🔍 Cleaning orders table...")
        
        # Remove orders with null IDs
        df_orders = df_orders[df_orders['order_id'].notna()]
        
        # Fix dates
        df_orders['order_date'] = pd.to_datetime(df_orders['order_date'], errors='coerce')
        df_sessions['session_date'] = pd.to_datetime(df_sessions['session_date'])
        
        # Validate order_date >= session_date (merge required)
        df_merged = df_orders.merge(
            df_sessions[['session_id', 'session_date']], 
            on='session_id', 
            how='left'
        )
        invalid_dates = (df_merged['order_date'] < df_merged['session_date']).sum()
        df_orders = df_orders[~(df_merged['order_date'] < df_merged['session_date'])]
        logger.info(f"  ✓ Removed {invalid_dates} orders with invalid timestamps")
        
        # Clean order_value
        df_orders['order_value'] = pd.to_numeric(df_orders['order_value'], errors='coerce')
        negative_orders = (df_orders['order_value'] < 0).sum()
        df_orders = df_orders[df_orders['order_value'] > 0]
        logger.info(f"  ✓ Removed {negative_orders} orders with negative values")
        
        # Create order value features
        df_orders['order_value_log'] = np.log1p(df_orders['order_value'])
        df_orders['high_value_order'] = (df_orders['order_value'] > 
                                         df_orders['order_value'].quantile(0.75)).astype(int)
        
        self.cleaning_report['orders_removed'] = invalid_dates + negative_orders
        return df_orders
    
    def clean_refunds(self, df_refunds, df_orders):
        """Clean refunds and validate logic"""
        logger.info("🔍 Cleaning refunds table...")
        
        # Validate refund_date >= order_date
        df_refunds['refund_date'] = pd.to_datetime(df_refunds['refund_date'])
        df_refunds = df_refunds.merge(
            df_orders[['order_id', 'order_date']], 
            on='order_id', 
            how='left'
        )
        invalid_refunds = (df_refunds['refund_date'] < df_refunds['order_date']).sum()
        df_refunds = df_refunds[df_refunds['refund_date'] >= df_refunds['order_date']]
        logger.info(f"  ✓ Removed {invalid_refunds} invalid refunds")
        
        # Calculate days to refund
        df_refunds['days_to_refund'] = (df_refunds['refund_date'] - 
                                        df_refunds['order_date']).dt.days
        
        self.cleaning_report['refunds_removed'] = invalid_refunds
        return df_refunds
    
    def create_master_dataset(self, df_sessions, df_orders, df_refunds):
        """Create unified master table for analysis"""
        logger.info("🔨 Creating master dataset...")
        
        # Sessions → Orders join
        df_master = df_sessions.copy()
        df_order_agg = df_orders.groupby('session_id').agg({
            'order_id': 'count',
            'order_value': ['sum', 'mean'],
            'order_date': 'first'
        }).reset_index()
        df_order_agg.columns = ['session_id', 'orders_in_session', 'total_order_value', 
                               'avg_order_value', 'first_order_date']
        
        df_master = df_master.merge(df_order_agg, on='session_id', how='left')
        df_master['converted'] = df_master['orders_in_session'].fillna(0) > 0
        df_master['conversion_flag'] = df_master['converted'].astype(int)
        
        # Refunds join
        df_refund_flag = df_refunds.groupby('order_id').size().reset_index(name='was_refunded')
        df_refund_flag['was_refunded'] = 1
        
        df_orders_refund = df_orders.merge(df_refund_flag, on='order_id', how='left')
        df_orders_refund['was_refunded'] = df_orders_refund['was_refunded'].fillna(0)
        
        df_refund_agg = df_orders_refund.groupby('session_id')['was_refunded'].max().reset_index()
        df_master = df_master.merge(df_refund_agg, on='session_id', how='left')
        df_master['was_refunded'] = df_master['was_refunded'].fillna(0)
        
        logger.info(f"  ✓ Master dataset: {len(df_master)} sessions with conversion & refund flags")
        return df_master

# USAGE:
# cleaner = BearCartDataCleaner()
# df_sessions, sessions_profile = cleaner.load_and_profile('sessions.csv')
# df_orders, orders_profile = cleaner.load_and_profile('orders.csv')
# df_refunds, refunds_profile = cleaner.load_and_profile('refunds.csv')
# df_sessions = cleaner.clean_sessions(df_sessions)
# df_orders = cleaner.clean_orders(df_orders, df_sessions)
# df_refunds = cleaner.clean_refunds(df_refunds, df_orders)
# df_master = cleaner.create_master_dataset(df_sessions, df_orders, df_refunds)
```

---

## 📊 PART 2: KEY METRICS CALCULATION ENGINE

```python
class BearCartMetrics:
    """Calculate all KPIs for dashboard"""
    
    @staticmethod
    def traffic_metrics(df_sessions):
        """Traffic and engagement KPIs"""
        return {
            'total_sessions': len(df_sessions),
            'unique_users': df_sessions['user_id'].nunique(),
            'avg_session_duration': df_sessions['session_duration_clean'].mean(),
            'bounce_rate': (df_sessions['session_duration_clean'] < 5).sum() / len(df_sessions),
            'sessions_by_channel': df_sessions['traffic_source'].value_counts().to_dict(),
            'sessions_by_device': df_sessions['device_type'].value_counts().to_dict(),
        }
    
    @staticmethod
    def conversion_metrics(df_master):
        """Conversion funnel KPIs"""
        total_sessions = len(df_master)
        converted = df_master['conversion_flag'].sum()
        
        return {
            'overall_conversion_rate': converted / total_sessions,
            'total_conversions': int(converted),
            'conversion_by_channel': df_master.groupby('traffic_source')['conversion_flag'].agg(['sum', 'count']),
            'conversion_by_device': df_master.groupby('device_type')['conversion_flag'].agg(['sum', 'count']),
            'avg_time_to_conversion': df_master[df_master['converted']]['session_duration_clean'].mean(),
        }
    
    @staticmethod
    def revenue_metrics(df_master):
        """Revenue and AOV KPIs"""
        total_revenue = df_master['total_order_value'].sum()
        orders = df_master[df_master['converted']]
        
        return {
            'total_revenue': total_revenue,
            'average_order_value': df_master['avg_order_value'].mean(),
            'revenue_per_session': total_revenue / len(df_master),
            'revenue_by_channel': df_master.groupby('traffic_source')['total_order_value'].sum().to_dict(),
            'revenue_by_device': df_master.groupby('device_type')['total_order_value'].sum().to_dict(),
            'top_products_by_revenue': df_master.groupby('product_category')['total_order_value'].sum().nlargest(10).to_dict(),
        }
    
    @staticmethod
    def quality_metrics(df_master):
        """Refund and customer health KPIs"""
        total_orders = df_master['orders_in_session'].sum()
        refunded_orders = df_master['was_refunded'].sum()
        
        return {
            'overall_refund_rate': refunded_orders / total_orders if total_orders > 0 else 0,
            'repeat_customer_rate': (df_master['is_returning_customer'] == 1).sum() / len(df_master),
            'refund_rate_by_category': df_master.groupby('product_category')['was_refunded'].mean().to_dict(),
            'at_risk_segments': df_master[df_master['was_refunded'] == 1][['traffic_source', 'device_type']].value_counts().to_dict(),
        }

# USAGE:
# metrics = BearCartMetrics()
# traffic = metrics.traffic_metrics(df_sessions)
# conversion = metrics.conversion_metrics(df_master)
# revenue = metrics.revenue_metrics(df_master)
# quality = metrics.quality_metrics(df_master)
```

---

## 📈 PART 3: DASHBOARD DATA EXPORT (For Frontend)

```python
def prepare_dashboard_data(df_master, df_orders, df_refunds):
    """Export cleaned data in JSON format for dashboard"""
    
    dashboard_data = {
        # KPI Cards
        'kpis': {
            'total_revenue': f"${df_master['total_order_value'].sum():,.2f}",
            'conversion_rate': f"{(df_master['conversion_flag'].mean() * 100):.1f}%",
            'avg_order_value': f"${df_master['avg_order_value'].mean():,.2f}",
            'refund_rate': f"{(df_master['was_refunded'].mean() * 100):.1f}%",
            'repeat_rate': f"{((df_master['is_returning_customer'].sum() / len(df_master)) * 100):.1f}%",
        },
        
        # Conversion Funnel
        'funnel': {
            'stages': ['Sessions', 'Browsed', 'Added to Cart', 'Purchased'],
            'values': [
                len(df_master),
                len(df_master[df_master['session_duration_clean'] > 5]),
                len(df_master[df_master['total_order_value'].notna()]),
                int(df_master['conversion_flag'].sum())
            ]
        },
        
        # Revenue by Channel
        'revenue_by_channel': df_master.groupby('traffic_source')['total_order_value'].sum().to_dict(),
        
        # Conversion by Channel
        'conversion_by_channel': (
            df_master.groupby('traffic_source')['conversion_flag'].mean() * 100
        ).round(1).to_dict(),
        
        # Top Products
        'top_products': (
            df_master.groupby('product_category')['total_order_value'].sum()
            .nlargest(10)
            .to_dict()
        ),
        
        # Refund Risk
        'high_refund_categories': (
            df_master.groupby('product_category')['was_refunded'].mean()
            .sort_values(ascending=False)
            .head(5)
            .to_dict()
        ),
        
        # Time Series (Revenue by Day)
        'revenue_trend': (
            df_master.groupby(df_master['session_date'].dt.date)['total_order_value'].sum()
            .to_dict()
        ),
    }
    
    return dashboard_data
```

---

## 🎯 PART 4: INSIGHT GENERATION FRAMEWORK

```python
class InsightEngine:
    """Generate business-focused insights with quantification"""
    
    @staticmethod
    def mobile_vs_desktop_insight(df_master):
        """Identify mobile performance gap"""
        desktop = df_master[df_master['device_type'] == 'Desktop']
        mobile = df_master[df_master['device_type'] == 'Mobile']
        
        desktop_conv = desktop['conversion_flag'].mean()
        mobile_conv = mobile['conversion_flag'].mean()
        gap_pct = ((desktop_conv - mobile_conv) / mobile_conv) * 100
        
        sessions_impact = len(mobile) * desktop_conv
        potential_orders = sessions_impact - mobile['conversion_flag'].sum()
        potential_revenue = potential_orders * df_master['avg_order_value'].mean()
        
        return {
            'title': 'Mobile UX Performance Gap',
            'finding': f'Desktop converts at {desktop_conv*100:.1f}% vs Mobile {mobile_conv*100:.1f}% (Gap: {gap_pct:.0f}%)',
            'impact': f'Potential ${potential_revenue:,.0f} if mobile matches desktop',
            'priority': 'HIGH',
            'recommendation': 'Audit mobile checkout flow, implement 1-click checkout'
        }
    
    @staticmethod
    def channel_quality_insight(df_master):
        """Identify best-performing channels"""
        channel_metrics = df_master.groupby('traffic_source').agg({
            'conversion_flag': ['mean', 'sum'],
            'total_order_value': ['mean', 'sum'],
            'session_id': 'count'
        }).round(2)
        
        best_channel = channel_metrics['conversion_flag']['mean'].idxmax()
        best_aov_channel = channel_metrics['total_order_value']['mean'].idxmax()
        
        return {
            'title': 'Channel Performance Hierarchy',
            'finding': f'{best_channel} drives highest conversion; {best_aov_channel} highest AOV',
            'channels': channel_metrics.to_dict(),
            'recommendation': 'Allocate budget to high-conversion channels first'
        }
    
    @staticmethod
    def refund_risk_insight(df_master):
        """Identify products/categories at refund risk"""
        refund_by_category = df_master.groupby('product_category').agg({
            'was_refunded': 'mean',
            'total_order_value': 'sum',
            'orders_in_session': 'sum'
        }).sort_values('was_refunded', ascending=False)
        
        highest_risk = refund_by_category.index[0]
        risk_rate = refund_by_category['was_refunded'].iloc[0]
        
        return {
            'title': 'Product Quality Risk',
            'finding': f'{highest_risk} has {risk_rate*100:.1f}% refund rate (industry avg ~5%)',
            'impact': 'Investigate product descriptions, quality issues, shipping damage',
            'recommendation': 'Quality audit for high-refund categories'
        }

# USAGE:
# insights = []
# insights.append(InsightEngine.mobile_vs_desktop_insight(df_master))
# insights.append(InsightEngine.channel_quality_insight(df_master))
# insights.append(InsightEngine.refund_risk_insight(df_master))
```

---

## 🎨 PART 5: QUICK-START DASHBOARD TEMPLATE (HTML/CSS/JS)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BearCart Analytics Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        
        .dashboard {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 30px;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
        }
        
        .header h1 {
            color: #333;
            font-size: 2em;
        }
        
        .kpi-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .kpi-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .kpi-card h3 {
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
        }
        
        .kpi-card .value {
            font-size: 2em;
            font-weight: bold;
        }
        
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
        }
        
        .chart-container {
            position: relative;
            height: 400px;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
        }
        
        .chart-title {
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🛒 BearCart Analytics Dashboard</h1>
            <div style="color: #999; font-size: 0.9em;">Last Updated: <span id="timestamp"></span></div>
        </div>
        
        <div class="kpi-cards">
            <div class="kpi-card">
                <h3>Total Revenue</h3>
                <div class="value">$2.3M</div>
            </div>
            <div class="kpi-card">
                <h3>Conversion Rate</h3>
                <div class="value">3.2%</div>
            </div>
            <div class="kpi-card">
                <h3>Average Order Value</h3>
                <div class="value">$85.50</div>
            </div>
            <div class="kpi-card">
                <h3>Refund Rate</h3>
                <div class="value">5.2%</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-container">
                <div class="chart-title">Revenue by Channel</div>
                <canvas id="revenueChart"></canvas>
            </div>
            <div class="chart-container">
                <div class="chart-title">Conversion Funnel</div>
                <canvas id="funnelChart"></canvas>
            </div>
        </div>
    </div>
    
    <script>
        // Revenue by Channel
        const revenueCtx = document.getElementById('revenueChart').getContext('2d');
        new Chart(revenueCtx, {
            type: 'bar',
            data: {
                labels: ['Organic', 'Paid Ads', 'Social', 'Direct', 'Referral'],
                datasets: [{
                    label: 'Revenue ($)',
                    data: [850000, 620000, 480000, 320000, 150000],
                    backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            }
        });
        
        // Conversion Funnel
        const funnelCtx = document.getElementById('funnelChart').getContext('2d');
        new Chart(funnelCtx, {
            type: 'bar',
            data: {
                labels: ['Sessions', 'Browse', 'Add to Cart', 'Purchase'],
                datasets: [{
                    label: 'Count',
                    data: [145000, 98000, 12000, 4650],
                    backgroundColor: '#667eea'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            }
        });
        
        // Update timestamp
        document.getElementById('timestamp').textContent = new Date().toLocaleString();
    </script>
</body>
</html>
```

---

## ✅ EXECUTION TIMELINE

| Time | Task | Deliverable |
|------|------|-------------|
| **Hour 1-2** | Data loading + profiling | Understand structure, identify issues |
| **Hour 3-4** | Data cleaning | Remove duplicates, fix dates, handle nulls |
| **Hour 5-6** | Feature engineering | Create conversion_flag, channel groups, risk scores |
| **Hour 7-8** | Calculate all KPIs | Metrics JSON export ready |
| **Hour 9-12** | Build dashboard | 4-5 pages, interactive filters |
| **Hour 13-14** | Generate insights | Run insight engine, prioritize by impact |
| **Hour 15-16** | Polish + presentation | Practice pitch, final tweaks |

---

## 🚀 DEPLOYMENT CHECKLIST

- [ ] All CSV exports created (cleaned_sessions.csv, cleaned_orders.csv, master_dataset.csv)
- [ ] Dashboard runs locally without external dependencies (or API documented)
- [ ] Metrics JSON file ready for dashboard consumption
- [ ] Insight summary PDF generated with visualizations
- [ ] Data cleaning documentation complete with assumptions
- [ ] Python notebook with full reproducible code
- [ ] Presentation slides with story arc (Problem → Analysis → Insights → Action)
- [ ] README with setup instructions

---

**You've got this! Ship fast, iterate, win. 🏆**
