import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pyathena import connect

# ─── CONFIG ───
REGION = 'eu-north-1'
S3_STAGING = 's3://dp-transformed-stock-data/athena-results/'
DATABASE = 'stock_db'

# ─── CONNECT TO ATHENA ───
@st.cache_resource
def get_connection():
    return connect(
        region_name=REGION,
        s3_staging_dir=S3_STAGING,
        schema_name=DATABASE
    )

# ─── QUERY FUNCTION ───
@st.cache_data(ttl=300)  # cache for 5 minutes
def run_query(query):
    conn = get_connection()
    return pd.read_sql(query, conn)

# ─── PAGE CONFIG ───
st.set_page_config(
    page_title="Stock Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Real-Time Stock Dashboard")
st.caption("Data from AWS Kinesis → S3 → Athena pipeline")

# ─── SIDEBAR FILTERS ───
st.sidebar.header("Filters")
symbol = st.sidebar.selectbox("Select Stock", ["TSLA", "NVDA", "Both"])
dates_query = run_query("SELECT DISTINCT date FROM stock_prices ORDER BY date DESC LIMIT 30")
available_dates = dates_query['date'].tolist()

if available_dates:
    selected_date = st.sidebar.selectbox("Select Date", available_dates)
else:
    selected_date = None

# ─── BUILD QUERY BASED ON FILTER ───
if symbol == "Both":
    where_clause = f"WHERE date = '{selected_date}'"
else:
    where_clause = f"WHERE symbol = '{symbol}' AND date = '{selected_date}'"

# ─── FETCH DATA ───
df = run_query(f"""
    SELECT symbol, event_time, open, high, low, close, volume, hour
    FROM stock_prices
    {where_clause}
    ORDER BY event_time ASC
""")

if df.empty:
    st.warning("No data found for selected filters.")
    st.stop()

# ─── METRICS ROW ───
st.subheader(f"Summary — {symbol} on {selected_date}")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Highest Price", f"${df['high'].max():.2f}")
col2.metric("Lowest Price", f"${df['low'].min():.2f}")
col3.metric("Avg Close", f"${df['close'].mean():.2f}")
col4.metric("Total Volume", f"{df['volume'].sum():,}")

st.divider()

# ─── PRICE CHART ───
st.subheader("Close Price Over Time")
fig_price = px.line(
    df,
    x='event_time',
    y='close',
    color='symbol',
    title=f"Close Price — {symbol}",
    labels={'event_time': 'Time', 'close': 'Close Price (USD)'}
)
fig_price.update_layout(hovermode='x unified')
st.plotly_chart(fig_price, use_container_width=True)

# ─── CANDLESTICK CHART ───
if symbol != "Both":
    st.subheader("Candlestick Chart")
    fig_candle = go.Figure(data=[go.Candlestick(
        x=df['event_time'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name=symbol
    )])
    fig_candle.update_layout(
        title=f"{symbol} Candlestick",
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False
    )
    st.plotly_chart(fig_candle, use_container_width=True)

# ─── VOLUME CHART ───
st.subheader("Trading Volume by Hour")
volume_by_hour = df.groupby(['hour', 'symbol'])['volume'].sum().reset_index()
fig_vol = px.bar(
    volume_by_hour,
    x='hour',
    y='volume',
    color='symbol',
    barmode='group',
    title="Total Volume by Hour",
    labels={'hour': 'Hour of Day', 'volume': 'Total Volume'}
)
st.plotly_chart(fig_vol, use_container_width=True)

# ─── RAW DATA TABLE ───
st.subheader("Raw Data")
st.dataframe(df, use_container_width=True)
