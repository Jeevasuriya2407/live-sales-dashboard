import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import random
import time
from datetime import datetime

# ── Page Config ─────────────────────────────────────────
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# ── Dark Theme CSS ──────────────────────────────────────
st.markdown("""
<style>
.stApp { background-color: #0f1117; }

h1, h2, h3, h4, h5, h6, p, span, div {
    color: #e5e7eb !important;
}

[data-testid="metric-container"] {
    background: linear-gradient(145deg, #1a1d27, #11131a);
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.4);
}

.section-header {
    font-size: 13px;
    font-weight: 600;
    color: #9ca3af;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# ── Plot Theme ──────────────────────────────────────────
PLOT_THEME = dict(
    paper_bgcolor="#0f1117",
    plot_bgcolor="#0f1117",
    font=dict(color="#e5e7eb"),
    xaxis=dict(showgrid=False, color="#9ca3af"),
    yaxis=dict(showgrid=False, color="#9ca3af"),
)

# ── Data ───────────────────────────────────────────────
PRODUCTS = {
    "Shoes": 2500,
    "T-Shirt": 1200,
    "Watch": 3500,
    "Bag": 1800,
    "Headphones": 2200,
}

CITIES = ["Chennai", "Bangalore", "Hyderabad", "Mumbai", "Delhi"]

# ── Session State ──────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(
        columns=["#", "Product", "Base", "Price", "City", "Time"]
    )
    st.session_state.order_counter = 0

# ── Generate Data ──────────────────────────────────────
def generate_sale():
    product = random.choice(list(PRODUCTS.keys()))
    base = PRODUCTS[product]
    price = base + random.randint(-200, 300)
    city = random.choice(CITIES)

    st.session_state.order_counter += 1

    new_row = {
        "#": st.session_state.order_counter,
        "Product": product,
        "Base": base,
        "Price": price,
        "City": city,
        "Time": datetime.now().strftime("%H:%M:%S"),
    }

    st.session_state.data = pd.concat(
        [st.session_state.data, pd.DataFrame([new_row])],
        ignore_index=True,
    )

generate_sale()
df = st.session_state.data

# ── Metrics ────────────────────────────────────────────
total_revenue = int(df["Price"].sum())
total_orders = len(df)
avg_order = int(df["Price"].mean()) if total_orders else 0

top_city = df.groupby("City")["Price"].sum().idxmax() if total_orders else "-"
top_city_rev = int(df.groupby("City")["Price"].sum().max()) if total_orders else 0

# ── Header ─────────────────────────────────────────────
st.title("📊 Real-Time Sales Dashboard")
st.success("● LIVE DATA STREAMING")

# ── KPI Row ────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Revenue", f"₹{total_revenue:,}")
k2.metric("Total Orders", total_orders)
k3.metric("Avg Order Value", f"₹{avg_order:,}")
k4.metric("Top City", f"{top_city} (₹{top_city_rev:,})")

st.markdown("---")

# ── Revenue Trend (Full Width) ─────────────────────────
df["Time_dt"] = pd.to_datetime(df["Time"])
trend = df.groupby("Time_dt")["Price"].sum().reset_index()

fig_line = go.Figure()
fig_line.add_trace(go.Scatter(
    x=trend["Time_dt"],
    y=trend["Price"],
    mode="lines+markers",
    line=dict(width=3)
))
fig_line.update_layout(**PLOT_THEME, title="Revenue Trend")

st.plotly_chart(fig_line, use_container_width=True)

# ── Row 2 ─────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<p class="section-header">Revenue by City</p>', unsafe_allow_html=True)
    city_rev = df.groupby("City")["Price"].sum().reset_index()

    fig_bar = go.Figure(go.Bar(
        x=city_rev["Price"],
        y=city_rev["City"],
        orientation="h"
    ))
    fig_bar.update_layout(**PLOT_THEME)
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.markdown('<p class="section-header">Orders by Product</p>', unsafe_allow_html=True)
    prod_counts = df["Product"].value_counts().reset_index()
    prod_counts.columns = ["Product", "Orders"]

    fig_pie = go.Figure(go.Pie(
        labels=prod_counts["Product"],
        values=prod_counts["Orders"],
        hole=0.5
    ))
    fig_pie.update_layout(**PLOT_THEME)
    st.plotly_chart(fig_pie, use_container_width=True)

# ── Row 3 ─────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.markdown('<p class="section-header">Revenue by Product</p>', unsafe_allow_html=True)
    prod_rev = df.groupby("Product")["Price"].sum().reset_index()

    fig_prod = go.Figure(go.Bar(
        x=prod_rev["Product"],
        y=prod_rev["Price"]
    ))
    fig_prod.update_layout(**PLOT_THEME)
    st.plotly_chart(fig_prod, use_container_width=True)

with col4:
    st.markdown('<p class="section-header">Order Value Distribution</p>', unsafe_allow_html=True)

    fig_hist = go.Figure(go.Histogram(x=df["Price"], nbinsx=10))
    fig_hist.update_layout(**PLOT_THEME)
    st.plotly_chart(fig_hist, use_container_width=True)

# ── Heatmap ────────────────────────────────────────────
st.markdown('<p class="section-header">City vs Product Sales</p>', unsafe_allow_html=True)

pivot = df.pivot_table(
    index="City",
    columns="Product",
    values="Price",
    aggfunc="sum",
    fill_value=0
)

fig_heatmap = go.Figure(data=go.Heatmap(
    z=pivot.values,
    x=pivot.columns,
    y=pivot.index
))
fig_heatmap.update_layout(**PLOT_THEME)

st.plotly_chart(fig_heatmap, use_container_width=True)

# ── Table ──────────────────────────────────────────────
st.markdown('<p class="section-header">Recent Transactions</p>', unsafe_allow_html=True)
st.dataframe(df.tail(10), use_container_width=True)

# ── Auto Refresh ───────────────────────────────────────
time.sleep(3)
st.rerun()
