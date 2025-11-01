"""
ATS (Automatic Train Supervision) Real-Time Dashboard
Streamlit-in-Snowflake Native Application
Visualizing train telemetry data using Snowpark
"""
import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Get Snowflake session (automatically provided in Streamlit-in-Snowflake)
session = get_active_session()

# Configuration constants
MAX_DATA_POINTS = 500
DEFAULT_DATA_LIMIT = 100

# Page configuration
st.set_page_config(
    page_title="ATS Real-Time Dashboard (Snowflake Native)",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .alert-box {
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .alert-critical {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
    }
    .alert-warning {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
    }
    .sis-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_latest_data(limit=DEFAULT_DATA_LIMIT):
    """
    Fetch latest telemetry data with limit using Snowpark.
    
    Args:
        limit: Maximum number of records to fetch (default: 100)
        
    Returns:
        pd.DataFrame: Latest telemetry data
    """
    # Enforce maximum limit to prevent memory issues
    limit = min(limit, MAX_DATA_POINTS)
    
    query = f"""
    SELECT 
        timestamp,
        train_id,
        passenger_count,
        total_weight_tons,
        power_draw_kw,
        speed_kmh,
        latitude,
        longitude,
        is_overcrowded,
        is_high_power_draw
    FROM ATS_DB.ATS_SCHEMA.ATS_TRANSFORMED
    WHERE timestamp >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
    ORDER BY timestamp DESC
    LIMIT {limit}
    """
    return session.sql(query).to_pandas()

@st.cache_data(ttl=60)
def get_alerts():
    """
    Fetch recent active alerts (last 24 hours only).
    
    Returns:
        pd.DataFrame: Recent alerts data
    """
    query = """
    SELECT 
        timestamp,
        train_id,
        alert_type,
        passenger_count,
        power_draw_kw,
        total_weight_tons
    FROM ATS_DB.ATS_SCHEMA.ATS_ALERTS
    WHERE timestamp >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
    ORDER BY timestamp DESC
    LIMIT 50
    """
    return session.sql(query).to_pandas()

@st.cache_data(ttl=60)
def get_hourly_stats():
    """
    Fetch hourly statistics for the last 24 hours.
    
    Returns:
        pd.DataFrame: Hourly aggregated statistics
    """
    query = """
    SELECT 
        hour,
        total_readings,
        unique_trains,
        avg_passenger_count,
        max_passenger_count,
        avg_power_draw_kw,
        max_power_draw_kw,
        overcrowding_incidents,
        high_power_incidents
    FROM ATS_DB.ATS_SCHEMA.ATS_HOURLY_STATS
    WHERE hour >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
    ORDER BY hour DESC
    LIMIT 24
    """
    return session.sql(query).to_pandas()

@st.cache_data(ttl=60)
def get_train_status():
    """
    Fetch latest status for each train (active in last hour).
    
    Returns:
        pd.DataFrame: Current status of all active trains
    """
    query = """
    SELECT 
        train_id,
        timestamp,
        passenger_count,
        total_weight_tons,
        power_draw_kw,
        speed_kmh,
        is_overcrowded,
        is_high_power_draw
    FROM ATS_DB.ATS_SCHEMA.ATS_LATEST_STATUS
    WHERE timestamp >= DATEADD(hour, -1, CURRENT_TIMESTAMP())
    ORDER BY train_id
    """
    return session.sql(query).to_pandas()

# Main Dashboard
def main():
    # Header with Snowflake Native badge
    st.markdown('<div class="sis-badge">🌨️ Snowflake Native App</div>', unsafe_allow_html=True)
    st.title("🚆 ATS Real-Time Monitoring Dashboard")
    st.markdown("*Automatic Train Supervision System - Live Telemetry (Streamlit-in-Snowflake)*")
    
    # Sidebar
    st.sidebar.header("⚙️ Dashboard Controls")
    auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
    refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 10, 60, 30)
    data_limit = st.sidebar.slider("Data points to display", 50, 500, 100)
    
    if st.sidebar.button("🔄 Refresh Now"):
        st.cache_data.clear()
        st.rerun()
    
    # Status indicator
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📡 Connection Status")
    try:
        # Test session
        session.sql("SELECT CURRENT_VERSION()").collect()
        st.sidebar.success("✅ Connected to Snowflake")
        st.sidebar.info(f"**Session ID:** {session.get_current_account()}")
    except Exception as e:
        st.sidebar.error(f"❌ Connection Failed: {e}")
        return
    
    # Fetch data
    with st.spinner("Loading data from Snowflake..."):
        try:
            df_latest = get_latest_data(data_limit)
            df_alerts = get_alerts()
            df_stats = get_hourly_stats()
            df_trains = get_train_status()
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            st.info("💡 Make sure the ATS pipeline is running and views are created.")
            return
    
    if df_latest is None or df_latest.empty:
        st.warning("⚠️ No data available. Ensure the ATS simulator is running and Kafka connector is configured.")
        return
    
    # KPI Metrics
    st.header("📊 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_trains = df_trains['TRAIN_ID'].nunique() if df_trains is not None and not df_trains.empty else 0
        st.metric("Active Trains", total_trains, "Online")
    
    with col2:
        avg_passengers = int(df_latest['PASSENGER_COUNT'].mean()) if not df_latest.empty else 0
        st.metric("Avg Passengers", avg_passengers, "per train")
    
    with col3:
        alert_count = len(df_alerts) if df_alerts is not None and not df_alerts.empty else 0
        st.metric("Active Alerts", alert_count, "⚠️" if alert_count > 0 else "✅")
    
    with col4:
        avg_power = round(df_latest['POWER_DRAW_KW'].mean(), 2) if not df_latest.empty else 0
        st.metric("Avg Power Draw", f"{avg_power} kW", "Current")
    
    # Alerts Section
    st.header("🚨 Active Alerts")
    if df_alerts is not None and not df_alerts.empty:
        for _, alert in df_alerts.head(5).iterrows():
            alert_type = "critical" if alert['ALERT_TYPE'] == 'OVERCROWDING' else "warning"
            icon = "🔴" if alert_type == "critical" else "🟡"
            st.markdown(f"""
                <div class="alert-box alert-{alert_type}">
                    {icon} <strong>{alert['ALERT_TYPE']}</strong> - Train {alert['TRAIN_ID']} 
                    at {alert['TIMESTAMP']}<br>
                    Passengers: {alert['PASSENGER_COUNT']} | Power: {alert['POWER_DRAW_KW']} kW
                </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No active alerts - All systems normal")
    
    # Charts
    st.header("📈 Real-Time Metrics")
    
    # Passenger Count Over Time
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Passenger Count Timeline")
        if not df_latest.empty:
            fig_passengers = px.line(
                df_latest.sort_values('TIMESTAMP'),
                x='TIMESTAMP',
                y='PASSENGER_COUNT',
                color='TRAIN_ID',
                title='Passenger Count by Train',
                labels={'PASSENGER_COUNT': 'Passengers', 'TIMESTAMP': 'Time'}
            )
            fig_passengers.update_layout(height=400)
            st.plotly_chart(fig_passengers, use_container_width=True)
    
    with col2:
        st.subheader("Power Draw Timeline")
        if not df_latest.empty:
            fig_power = px.line(
                df_latest.sort_values('TIMESTAMP'),
                x='TIMESTAMP',
                y='POWER_DRAW_KW',
                color='TRAIN_ID',
                title='Power Consumption by Train',
                labels={'POWER_DRAW_KW': 'Power (kW)', 'TIMESTAMP': 'Time'}
            )
            fig_power.add_hline(y=150, line_dash="dash", line_color="red", 
                               annotation_text="Max Threshold")
            fig_power.update_layout(height=400)
            st.plotly_chart(fig_power, use_container_width=True)
    
    # Distribution Charts
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Passenger Distribution")
        if not df_latest.empty:
            fig_hist = px.histogram(
                df_latest,
                x='PASSENGER_COUNT',
                nbins=30,
                title='Passenger Count Distribution',
                labels={'PASSENGER_COUNT': 'Passengers'}
            )
            fig_hist.update_layout(height=350)
            st.plotly_chart(fig_hist, use_container_width=True)
    
    with col4:
        st.subheader("Train Speed Distribution")
        if not df_latest.empty:
            fig_speed = px.box(
                df_latest,
                x='TRAIN_ID',
                y='SPEED_KMH',
                title='Speed Distribution by Train',
                labels={'SPEED_KMH': 'Speed (km/h)', 'TRAIN_ID': 'Train ID'}
            )
            fig_speed.update_layout(height=350)
            st.plotly_chart(fig_speed, use_container_width=True)
    
    # Hourly Statistics
    if df_stats is not None and not df_stats.empty:
        st.header("📅 Hourly Statistics")
        col5, col6 = st.columns(2)
        
        with col5:
            fig_hourly = go.Figure()
            fig_hourly.add_trace(go.Bar(
                x=df_stats['HOUR'],
                y=df_stats['TOTAL_READINGS'],
                name='Total Readings',
                marker_color='lightblue'
            ))
            fig_hourly.update_layout(
                title='Readings per Hour',
                xaxis_title='Hour',
                yaxis_title='Count',
                height=350
            )
            st.plotly_chart(fig_hourly, use_container_width=True)
        
        with col6:
            fig_incidents = go.Figure()
            fig_incidents.add_trace(go.Scatter(
                x=df_stats['HOUR'],
                y=df_stats['OVERCROWDING_INCIDENTS'],
                name='Overcrowding',
                mode='lines+markers',
                line=dict(color='red')
            ))
            fig_incidents.add_trace(go.Scatter(
                x=df_stats['HOUR'],
                y=df_stats['HIGH_POWER_INCIDENTS'],
                name='High Power',
                mode='lines+markers',
                line=dict(color='orange')
            ))
            fig_incidents.update_layout(
                title='Incidents per Hour',
                xaxis_title='Hour',
                yaxis_title='Incident Count',
                height=350
            )
            st.plotly_chart(fig_incidents, use_container_width=True)
    
    # Train Status Table
    st.header("🚂 Train Status Overview")
    if df_trains is not None and not df_trains.empty:
        # Format the dataframe
        df_display = df_trains.copy()
        df_display['STATUS'] = df_display.apply(
            lambda row: '🔴 ALERT' if row['IS_OVERCROWDED'] or row['IS_HIGH_POWER_DRAW'] else '✅ OK',
            axis=1
        )
        df_display = df_display[['TRAIN_ID', 'TIMESTAMP', 'PASSENGER_COUNT', 
                                 'POWER_DRAW_KW', 'SPEED_KMH', 'STATUS']]
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # Raw Data Explorer
    with st.expander("🔍 Raw Data Explorer"):
        st.dataframe(df_latest.head(50), use_container_width=True, hide_index=True)
    
    # Footer
    st.markdown("---")
    col_footer1, col_footer2 = st.columns([3, 1])
    with col_footer1:
        st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    with col_footer2:
        st.markdown("*Powered by Snowflake ❄️*")
    
    # Auto-refresh
    if auto_refresh:
        import time
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()
