import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
import time
from datetime import datetime

st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; }
    section[data-testid="stSidebar"] { background-color: #0f1117; }

    /* Hide default Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }

    /* KPI cards */
    [data-testid="metric-container"] {
        background-color: #1a1d27;
        border: 1px solid #2a2d3a;
        border-radius: 12px;
        padding: 18px 20px;
    }
    [data-testid="metric-container"] label {
        color: #6b7280 !important;
        font-size: 12px !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #f1f5f9 !important;
        font-size: 26px !important;
        font-weight: 600 !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-size: 12px !important;
    }

    /* Section headers */
    .section-header {
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #e2e8f0;
        margin-bottom: 10px;
        margin-top: 4px;
        border-left: 3px solid #6366f1;
        padding-left: 10px;
    }

    /* Chart containers */
    .chart-card {
        background-color: #1a1d27;
        border: 1px solid #2a2d3a;
        border-radius: 12px;
        padding: 20px;
    }

    /* Table styling */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Live badge */
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #14291a;
        border: 1px solid #1e4228;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 12px;
        color: #4ade80;
        font-weight: 500;
    }
    .live-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #4ade80;
        animation: blink 1.4s infinite;
        display: inline-block;
    }
    @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

    /* Divider */
    hr { border-color: #2a2d3a !important; margin: 8px 0 20px 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Data & Constants ─────────────────────────────────────────────────────────
PRODUCTS = {
    "Shoes": 2500,
    "T-Shirt": 1200,
    "Watch": 3500,
    "Bag": 1800,
    "Headphones": 2200,
}
CITIES = ["Chennai", "Bangalore", "Hyderabad", "Mumbai", "Delhi"]
PRODUCT_COLORS = {
    "Shoes": "#6366f1",
    "T-Shirt": "#22d3ee",
    "Watch": "#f59e0b",
    "Bag": "#ec4899",
    "Headphones": "#10b981",
}
CITY_COLORS = ["#6366f1", "#22d3ee", "#f59e0b", "#ec4899", "#10b981"]

PLOT_CONFIG = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#d1d5db", size=12),
    margin=dict(l=8, r=8, t=10, b=8),
)

# ── Session State ─────────────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(
        columns=["#", "Product", "Base", "Price", "City", "Time"]
    )
    st.session_state.order_counter = 0

# ── Generate Sale ─────────────────────────────────────────────────────────────
def generate_sale():
    product = random.choice(list(PRODUCTS.keys()))
    price = PRODUCTS[product] + random.randint(-200,300)

    city = random.choice(CITIES)  # ✅ FIXED

    new = {
        "Product": product,
        "Price": price,
        "City": city,
        "Time": datetime.now()
    }

    st.session_state.data = pd.concat(
        [st.session_state.data, pd.DataFrame([new])],
        ignore_index=True
    )

generate_sale()
df = st.session_state.data

# ── Computed Metrics ──────────────────────────────────────────────────────────
total_revenue = int(df["Price"].sum())
total_orders = len(df)
avg_order = int(df["Price"].mean()) if total_orders else 0
top_city = df.groupby("City")["Price"].sum().idxmax() if total_orders else "—"
top_city_rev = int(df.groupby("City")["Price"].sum().max()) if total_orders else 0

# Trend: compare last 5 vs previous 5
last5 = df.tail(5)["Price"].sum()
prev5 = df.iloc[-10:-5]["Price"].sum() if len(df) >= 10 else 0
trend_pct = round((last5 - prev5) / prev5 * 100, 1) if prev5 else 0.0

# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_badge = st.columns([6, 1])
with col_title:
    st.markdown("## 📊 Real-Time Sales Dashboard")
with col_badge:
    st.markdown(
        f'<div style="text-align:right; padding-top:14px;">'
        f'<span class="live-badge"><span class="live-dot"></span>LIVE</span></div>',
        unsafe_allow_html=True,
    )

st.markdown(
    f'<p style="color:#6b7280; font-size:13px; margin-top:-8px; margin-bottom:16px;">'
    f'Updated at {datetime.now().strftime("%H:%M:%S")} &nbsp;·&nbsp; '
    f'{total_orders} orders tracked</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# ── KPI Row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Revenue", f"₹{total_revenue:,}", f"{'+' if trend_pct >= 0 else ''}{trend_pct}% vs prev 5")
k2.metric("Total Orders", f"{total_orders}", f"Across {len(CITIES)} cities")
k3.metric("Avg Order Value", f"₹{avg_order:,}")
k4.metric("Top City", top_city, f"₹{top_city_rev:,}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts Row ────────────────────────────────────────────────────────────────
chart_left, chart_right = st.columns(2)

with chart_left:
    st.markdown('<p class="section-header">Revenue by city</p>', unsafe_allow_html=True)
    city_rev = df.groupby("City")["Price"].sum().reset_index().sort_values("Price", ascending=True)
    fig_bar = go.Figure(go.Bar(
        x=city_rev["Price"],
        y=city_rev["City"],
        orientation="h",
        marker=dict(color=CITY_COLORS[:len(city_rev)], line=dict(width=0)),
        text=[f"₹{v:,}" for v in city_rev["Price"]],
        textposition="outside",
        textfont=dict(size=11, color="#e2e8f0"),
    ))
    fig_bar.update_layout(
        **PLOT_CONFIG,
        height=260,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=12, color="#e2e8f0")),
        bargap=0.35,
    )
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

with chart_right:
    st.markdown('<p class="section-header">Orders by product</p>', unsafe_allow_html=True)
    prod_counts = df["Product"].value_counts().reset_index()
    prod_counts.columns = ["Product", "Orders"]
    fig_donut = go.Figure(go.Pie(
        labels=prod_counts["Product"],
        values=prod_counts["Orders"],
        hole=0.62,
        marker=dict(
            colors=[PRODUCT_COLORS.get(p, "#6b7280") for p in prod_counts["Product"]],
            line=dict(width=0),
        ),
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>Orders: %{value}<br>Share: %{percent}<extra></extra>",
    ))
    fig_donut.update_layout(
        **PLOT_CONFIG,
        height=260,
        showlegend=True,
        legend=dict(
            orientation="v",
            x=1.0, y=0.5,
            font=dict(size=11, color="#e2e8f0"),
            itemclick=False,
        ),
    )
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

# ── Transactions Table ────────────────────────────────────────────────────────
st.markdown('<p class="section-header">Recent transactions</p>', unsafe_allow_html=True)

display_df = df.tail(10).copy().iloc[::-1].reset_index(drop=True)
display_df["vs Base"] = display_df["Price"] - display_df["Base"]
display_df["vs Base"] = display_df["vs Base"].apply(
    lambda x: f"+₹{int(x):,}" if x >= 0 else f"-₹{abs(int(x)):,}"
)
display_df["Price"] = display_df["Price"].apply(lambda x: f"₹{int(x):,}")

table_cols = ["#", "Product", "City", "Price", "vs Base", "Time"]
st.dataframe(
    display_df[table_cols],
    use_container_width=True,
    hide_index=True,
    column_config={
        "#": st.column_config.NumberColumn(width="small"),
        "Product": st.column_config.TextColumn(width="medium"),
        "City": st.column_config.TextColumn(width="medium"),
        "Price": st.column_config.TextColumn(width="medium"),
        "vs Base": st.column_config.TextColumn(width="medium"),
        "Time": st.column_config.TextColumn(width="medium"),
    },
)

# ── Auto-refresh ──────────────────────────────────────────────────────────────
time.sleep(4)
st.rerun()

