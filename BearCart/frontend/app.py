"""
BearCart: E-Commerce Growth & Conversion Intelligence Dashboard
Streamlit-based interactive analytics dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend import kpis, analysis, utils

# Page configuration
st.set_page_config(
    page_title="BearCart Analytics",
    page_icon="🐻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .kpi-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_all_data():
    """Load all data files with caching."""
    try:
        sessions = utils.load_data('sessions.csv')
        orders = utils.load_data('orders.csv')
        products = utils.load_data('products.csv')
        refunds = utils.load_data('refunds.csv')
        return sessions, orders, products, refunds
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please ensure data files exist in data/cleaned/ directory. Run data_cleaning.py first.")
        return None, None, None, None


def render_kpi_card(label: str, value: str, delta: str = None):
    """Render a KPI card with consistent styling."""
    delta_html = f'<div style="font-size: 0.8rem; color: #28a745;">{delta}</div>' if delta else ''
    st.markdown(f"""
        <div class="kpi-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)


def executive_overview_page(sessions, orders, refunds):
    """Executive Overview page with key KPIs."""
    st.markdown('<div class="main-header">📊 Executive Overview</div>', unsafe_allow_html=True)
    
    # Date filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=pd.to_datetime(sessions['timestamp']).min().date())
    with col2:
        end_date = st.date_input("End Date", value=pd.to_datetime(sessions['timestamp']).max().date())
    
    date_filter = (pd.Timestamp(start_date), pd.Timestamp(end_date) + timedelta(days=1))
    
    # Calculate KPIs
    total_sessions = kpis.calculate_total_sessions(sessions, date_filter)
    total_orders = kpis.calculate_total_orders(orders, date_filter)
    conversion_rate = kpis.calculate_conversion_rate(sessions, orders, date_filter)
    revenue = kpis.calculate_revenue(orders, date_filter)
    aov = kpis.calculate_average_order_value(orders, date_filter)
    revenue_per_session = kpis.calculate_revenue_per_session(sessions, orders, date_filter)
    refund_rate = kpis.calculate_refund_rate(orders, refunds, date_filter)
    refund_value = kpis.calculate_refund_value(refunds, date_filter)
    
    # Display KPI cards
    st.markdown("### Key Performance Indicators")
    kpi_cols = st.columns(4)
    
    with kpi_cols[0]:
        render_kpi_card("Total Sessions", utils.format_number(total_sessions))
    with kpi_cols[1]:
        render_kpi_card("Total Orders", utils.format_number(total_orders))
    with kpi_cols[2]:
        render_kpi_card("Conversion Rate", utils.format_percentage(conversion_rate))
    with kpi_cols[3]:
        render_kpi_card("Revenue", utils.format_currency(revenue))
    
    kpi_cols2 = st.columns(4)
    with kpi_cols2[0]:
        render_kpi_card("Average Order Value", utils.format_currency(aov))
    with kpi_cols2[1]:
        render_kpi_card("Revenue per Session", utils.format_currency(revenue_per_session))
    with kpi_cols2[2]:
        render_kpi_card("Refund Rate", utils.format_percentage(refund_rate))
    with kpi_cols2[3]:
        render_kpi_card("Total Refund Value", utils.format_currency(refund_value))
    
    # Business insights
    st.markdown("---")
    st.markdown("### 💡 Key Insights")
    
    insights = []
    if conversion_rate > 15:
        insights.append("✅ **Strong Conversion Performance**: Conversion rate exceeds industry average (15%)")
    elif conversion_rate < 10:
        insights.append("⚠️ **Conversion Opportunity**: Conversion rate below industry average - consider optimizing checkout flow")
    
    if aov > 100:
        insights.append("✅ **Healthy AOV**: Average order value indicates strong customer value")
    
    if refund_rate > 10:
        insights.append("⚠️ **Refund Alert**: Refund rate is elevated - investigate product quality or fulfillment issues")
    
    if revenue_per_session > 5:
        insights.append("✅ **Efficient Revenue Generation**: Strong revenue per session indicates effective monetization")
    
    for insight in insights:
        st.markdown(insight)
    
    if not insights:
        st.info("Review individual metrics for detailed insights.")


def traffic_marketing_page(sessions, orders):
    """Traffic & Marketing Analysis page."""
    st.markdown('<div class="main-header">🚦 Traffic & Marketing Analysis</div>', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        start_date = st.date_input("Start Date", value=pd.to_datetime(sessions['timestamp']).min().date(), key='traffic_start')
    with col2:
        end_date = st.date_input("End Date", value=pd.to_datetime(sessions['timestamp']).max().date(), key='traffic_end')
    with col3:
        selected_channel = st.selectbox("Filter by Channel", ['All'] + list(sessions['channel'].unique()), key='traffic_channel')
    
    date_filter = (pd.Timestamp(start_date), pd.Timestamp(end_date) + timedelta(days=1))
    channel_filter = None if selected_channel == 'All' else selected_channel
    
    # Sessions by Channel
    st.markdown("### Sessions by Marketing Channel")
    sessions_by_channel = analysis.get_sessions_by_channel(sessions, date_filter)
    
    if channel_filter:
        sessions_by_channel = sessions_by_channel[sessions_by_channel['channel'] == channel_filter]
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            sessions_by_channel,
            x='channel',
            y='session_count',
            title='Sessions by Channel',
            labels={'channel': 'Marketing Channel', 'session_count': 'Number of Sessions'},
            color='session_count',
            color_continuous_scale='Blues'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(
            sessions_by_channel,
            values='session_count',
            names='channel',
            title='Channel Distribution',
            hole=0.4
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Sessions by Device
    st.markdown("### Sessions by Device Type")
    sessions_by_device = analysis.get_sessions_by_device(sessions, date_filter)
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            sessions_by_device,
            x='device',
            y='session_count',
            title='Sessions by Device',
            labels={'device': 'Device Type', 'session_count': 'Number of Sessions'},
            color='session_count',
            color_continuous_scale='Greens'
        )
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(
            sessions_by_device,
            values='session_count',
            names='device',
            title='Device Distribution',
            hole=0.4
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # Time Trends
    st.markdown("### Traffic Trends Over Time")
    freq = st.selectbox("Time Granularity", ['Daily', 'Weekly', 'Monthly'], key='traffic_freq')
    freq_map = {'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M'}
    
    time_trend = analysis.get_sessions_time_trend(sessions, date_filter, freq_map[freq])
    
    fig = px.line(
        time_trend,
        x='date',
        y='session_count',
        title=f'Sessions Over Time ({freq})',
        labels={'date': 'Date', 'session_count': 'Number of Sessions'},
        markers=True
    )
    fig.update_traces(line_color='#1f77b4', line_width=3)
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def conversion_funnel_page(sessions, orders):
    """Conversion Funnel Analysis page."""
    st.markdown('<div class="main-header">🔄 Conversion Funnel</div>', unsafe_allow_html=True)
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=pd.to_datetime(sessions['timestamp']).min().date(), key='funnel_start')
    with col2:
        end_date = st.date_input("End Date", value=pd.to_datetime(sessions['timestamp']).max().date(), key='funnel_end')
    
    date_filter = (pd.Timestamp(start_date), pd.Timestamp(end_date) + timedelta(days=1))
    
    # Overall Funnel
    st.markdown("### Overall Conversion Funnel")
    funnel_data = analysis.get_conversion_funnel(sessions, orders, date_filter)
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.funnel(
            funnel_data,
            x='count',
            y='stage',
            title='Session to Order Conversion',
            labels={'count': 'Count', 'stage': 'Funnel Stage'}
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Calculate conversion rate
        sessions_count = funnel_data[funnel_data['stage'] == 'Sessions']['count'].values[0]
        orders_count = funnel_data[funnel_data['stage'] == 'Orders']['count'].values[0]
        conv_rate = (orders_count / sessions_count * 100) if sessions_count > 0 else 0
        
        st.metric("Conversion Rate", f"{conv_rate:.2f}%")
        st.metric("Sessions", f"{sessions_count:,}")
        st.metric("Orders", f"{orders_count:,}")
        st.metric("Drop-off", f"{sessions_count - orders_count:,}")
    
    # Conversion by Channel
    st.markdown("### Conversion Rate by Marketing Channel")
    conv_by_channel = analysis.get_conversion_by_channel(sessions, orders, date_filter)
    
    fig = px.bar(
        conv_by_channel,
        x='channel',
        y='conversion_rate',
        title='Conversion Rate by Channel',
        labels={'channel': 'Marketing Channel', 'conversion_rate': 'Conversion Rate (%)'},
        text='conversion_rate',
        color='conversion_rate',
        color_continuous_scale='Viridis'
    )
    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed table
    with st.expander("View Detailed Channel Performance"):
        st.dataframe(conv_by_channel, use_container_width=True)
    
    # Conversion by Device
    st.markdown("### Conversion Rate by Device Type")
    conv_by_device = analysis.get_conversion_by_device(sessions, orders, date_filter)
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            conv_by_device,
            x='device',
            y='conversion_rate',
            title='Conversion Rate by Device',
            labels={'device': 'Device Type', 'conversion_rate': 'Conversion Rate (%)'},
            text='conversion_rate',
            color='conversion_rate',
            color_continuous_scale='Plasma'
        )
        fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.dataframe(conv_by_device, use_container_width=True)


def revenue_aov_page(orders, products):
    """Revenue & AOV Analysis page."""
    st.markdown('<div class="main-header">💰 Revenue & Average Order Value</div>', unsafe_allow_html=True)
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=pd.to_datetime(orders['order_date']).min().date(), key='revenue_start')
    with col2:
        end_date = st.date_input("End Date", value=pd.to_datetime(orders['order_date']).max().date(), key='revenue_end')
    
    date_filter = (pd.Timestamp(start_date), pd.Timestamp(end_date) + timedelta(days=1))
    
    # Revenue Metrics
    revenue = kpis.calculate_revenue(orders, date_filter)
    aov = kpis.calculate_average_order_value(orders, date_filter)
    total_orders = kpis.calculate_total_orders(orders, date_filter)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Revenue", utils.format_currency(revenue))
    with col2:
        st.metric("Average Order Value", utils.format_currency(aov))
    with col3:
        st.metric("Total Orders", utils.format_number(total_orders))
    
    # Revenue Trends
    st.markdown("### Revenue Trends Over Time")
    freq = st.selectbox("Time Granularity", ['Daily', 'Weekly', 'Monthly'], key='revenue_freq')
    freq_map = {'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M'}
    
    revenue_trend = analysis.get_revenue_trends(orders, date_filter, freq_map[freq])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=revenue_trend['date'],
        y=revenue_trend['revenue'],
        mode='lines+markers',
        name='Revenue',
        line=dict(color='#1f77b4', width=3),
        fill='tonexty',
        fillcolor='rgba(31, 119, 180, 0.2)'
    ))
    fig.update_layout(
        title=f'Revenue Over Time ({freq})',
        xaxis_title='Date',
        yaxis_title='Revenue ($)',
        height=400,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # AOV Analysis
    st.markdown("### Average Order Value Analysis")
    aov_by_category = analysis.get_aov_by_category(orders, products, date_filter)
    
    fig = px.bar(
        aov_by_category,
        x='category',
        y='aov',
        title='Average Order Value by Category',
        labels={'category': 'Category', 'aov': 'Average Order Value ($)'},
        text='aov',
        color='aov',
        color_continuous_scale='Blues'
    )
    fig.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
    fig.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Revenue vs Orders
    st.markdown("### Revenue vs Order Volume")
    revenue_trend = analysis.get_revenue_trends(orders, date_filter, freq_map[freq])
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=revenue_trend['date'],
        y=revenue_trend['orders'],
        name='Orders',
        yaxis='y',
        offsetgroup=1,
        marker_color='#ff7f0e'
    ))
    fig.add_trace(go.Scatter(
        x=revenue_trend['date'],
        y=revenue_trend['revenue'],
        mode='lines+markers',
        name='Revenue',
        yaxis='y2',
        line=dict(color='#1f77b4', width=3)
    ))
    fig.update_layout(
        title=f'Revenue and Order Volume Over Time ({freq})',
        xaxis_title='Date',
        yaxis=dict(title='Number of Orders', side='left'),
        yaxis2=dict(title='Revenue ($)', overlaying='y', side='right'),
        height=400,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)


def refund_analysis_page(refunds, orders):
    """Refund Analysis page."""
    st.markdown('<div class="main-header">↩️ Refund Analysis</div>', unsafe_allow_html=True)
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=pd.to_datetime(refunds['refund_date']).min().date(), key='refund_start')
    with col2:
        end_date = st.date_input("End Date", value=pd.to_datetime(refunds['refund_date']).max().date(), key='refund_end')
    
    date_filter = (pd.Timestamp(start_date), pd.Timestamp(end_date) + timedelta(days=1))
    
    # Refund Metrics
    refund_rate = kpis.calculate_refund_rate(orders, refunds, date_filter)
    refund_value = kpis.calculate_refund_value(refunds, date_filter)
    total_refunds = len(refunds[(pd.to_datetime(refunds['refund_date']) >= date_filter[0]) & 
                                (pd.to_datetime(refunds['refund_date']) <= date_filter[1])])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Refund Rate", utils.format_percentage(refund_rate))
    with col2:
        st.metric("Total Refund Value", utils.format_currency(refund_value))
    with col3:
        st.metric("Number of Refunds", utils.format_number(total_refunds))
    
    # Refund Analysis
    refund_analysis = analysis.get_refund_analysis(refunds, orders, None, date_filter)
    
    # Refunds by Reason
    st.markdown("### Refunds by Reason")
    refunds_by_reason = refund_analysis['by_reason']
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            refunds_by_reason,
            x='reason',
            y='refund_count',
            title='Number of Refunds by Reason',
            labels={'reason': 'Refund Reason', 'refund_count': 'Number of Refunds'},
            color='refund_count',
            color_continuous_scale='Reds'
        )
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            refunds_by_reason,
            x='reason',
            y='refund_value',
            title='Refund Value by Reason',
            labels={'reason': 'Refund Reason', 'refund_value': 'Refund Value ($)'},
            text='refund_value',
            color='refund_value',
            color_continuous_scale='Oranges'
        )
        fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # Refund Trends
    st.markdown("### Refund Trends Over Time")
    refund_trend = refund_analysis['trend']
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=refund_trend['date'],
        y=refund_trend['refund_value'],
        mode='lines+markers',
        name='Refund Value',
        line=dict(color='#d62728', width=3),
        fill='tonexty',
        fillcolor='rgba(214, 39, 40, 0.2)'
    ))
    fig.update_layout(
        title='Refund Value Over Time',
        xaxis_title='Date',
        yaxis_title='Refund Value ($)',
        height=400,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Business Impact
    st.markdown("### 💡 Business Impact")
    revenue_in_period = kpis.calculate_revenue(orders, date_filter)
    net_revenue = revenue_in_period - refund_value
    refund_percentage = (refund_value / revenue_in_period * 100) if revenue_in_period > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Gross Revenue", utils.format_currency(revenue_in_period))
    with col2:
        st.metric("Refund Value", utils.format_currency(refund_value), delta=f"-{utils.format_percentage(refund_percentage)}")
    with col3:
        st.metric("Net Revenue", utils.format_currency(net_revenue))


def main():
    """Main application entry point."""
    # Sidebar
    st.sidebar.title("🐻 BearCart Analytics")
    st.sidebar.markdown("---")
    
    # Load data
    sessions, orders, products, refunds = load_all_data()
    
    if sessions is None:
        st.error("Unable to load data. Please ensure data files are available.")
        st.info("""
        **Setup Instructions:**
        1. Place raw data files in `data/raw/` directory:
           - sessions.csv
           - orders.csv
           - products.csv
           - refunds.csv
        2. Run `python backend/data_cleaning.py` to clean the data
        3. Refresh this page
        """)
        return
    
    # Navigation
    page = st.sidebar.selectbox(
        "Select Page",
        ["Executive Overview", "Traffic & Marketing", "Conversion Funnel", "Revenue & AOV", "Refund Analysis"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info("""
    **BearCart Analytics Dashboard**
    
    A comprehensive e-commerce analytics platform for data-driven decision making.
    
    Built with Streamlit and Plotly.
    """)
    
    # Route to appropriate page
    if page == "Executive Overview":
        executive_overview_page(sessions, orders, refunds)
    elif page == "Traffic & Marketing":
        traffic_marketing_page(sessions, orders)
    elif page == "Conversion Funnel":
        conversion_funnel_page(sessions, orders)
    elif page == "Revenue & AOV":
        revenue_aov_page(orders, products)
    elif page == "Refund Analysis":
        refund_analysis_page(refunds, orders)


if __name__ == "__main__":
    main()

