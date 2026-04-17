import streamlit as st
import pandas as pd
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

# ── Custom CSS ─────────────────────────────────────────
st.markdown("""
<style>
.stApp { background-color: #0f1117; }
#MainMenu, footer, header { visibility: hidden; }

[data-testid="metric-container"] {
    background-color: #1a1d27;
    border-radius: 12px;
    padding: 15px;
}

.section-header {
    font-size: 12px;
    color: #6b7280;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ── Data ───────────────────────────────────────────────
PRODUCTS = {
    "Shoes": 2500,
    "T-Shirt": 1200,
    "Watch": 3500,
    "Bag": 1800,
    "Headphones": 2200,
}

CITIES = ["Chennai", "Bangalore", "Hyderabad", "Mumbai", "Delhi"]

CITY_COLORS = ["#6366f1", "#22d3ee", "#f59e0b", "#ec4899", "#10b981"]

# ── Session State ──────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(
        columns=["#", "Product", "Base", "Price", "City", "Time"]
    )
    st.session_state.order_counter = 0

# ── Generate Sale ──────────────────────────────────────
def generate_sale():
    product = random.choice(list(PRODUCTS.keys()))
    base = PRODUCTS[product]
    price = base + random.randint(-200, 300)

    city = random.choice(CITIES)  # ✅ FIXED

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
st.caption(f"Updated at {datetime.now().strftime('%H:%M:%S')}")

# ── KPI ────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Revenue", f"₹{total_revenue:,}")
k2.metric("Total Orders", total_orders)
k3.metric("Avg Order Value", f"₹{avg_order:,}")
k4.metric("Top City", f"{top_city} (₹{top_city_rev:,})")

# ── Charts ─────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<p class="section-header">Revenue by City</p>', unsafe_allow_html=True)

    city_rev = df.groupby("City")["Price"].sum().reset_index()

    fig_bar = go.Figure(go.Bar(
        x=city_rev["Price"],
        y=city_rev["City"],
        orientation="h"
    ))

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

    st.plotly_chart(fig_pie, use_container_width=True)

# ── Table ──────────────────────────────────────────────
st.markdown('<p class="section-header">Recent Transactions</p>', unsafe_allow_html=True)

st.dataframe(df.tail(10), use_container_width=True)

# ── Auto Refresh ───────────────────────────────────────
time.sleep(3)
st.rerun()
