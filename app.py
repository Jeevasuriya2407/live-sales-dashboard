import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import random
import time
from datetime import datetime

# ── Page Config ─────────────────────────
st.set_page_config(page_title="Advanced Sales Dashboard", layout="wide")

# ── Theme Colors ────────────────────────
COLORS = ["#6366f1","#22d3ee","#f59e0b","#10b981","#ec4899","#8b5cf6"]

PLOT_THEME = dict(
    paper_bgcolor="#0f1117",
    plot_bgcolor="#0f1117",
    font=dict(color="#e5e7eb")
)

# ── CSS ────────────────────────────────
st.markdown("""
<style>
.stApp { background-color: #0f1117; }
h1,h2,h3,h4,h5,p { color:#e5e7eb; }
</style>
""", unsafe_allow_html=True)

# ── Data ───────────────────────────────
PRODUCTS = {"Shoes":2500,"T-Shirt":1200,"Watch":3500,"Bag":1800,"Headphones":2200}
CITIES = ["Chennai","Bangalore","Hyderabad","Mumbai","Delhi"]

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Product","Price","City","Time"])
    st.session_state.count = 0

def generate():
    product = random.choice(list(PRODUCTS.keys()))
    price = PRODUCTS[product] + random.randint(-200,300)
    city = random.choice(CITIES)

    new = {
        "Product": product,
        "Price": price,
        "City": city,
        "Time": datetime.now()
    }

    st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new])], ignore_index=True)

generate()
df = st.session_state.data

# ── KPIs ───────────────────────────────
total_revenue = int(df["Price"].sum())
total_orders = len(df)
avg_order = int(df["Price"].mean()) if total_orders else 0

st.title("📊 Advanced Sales Dashboard")
st.success("● LIVE")

k1,k2,k3 = st.columns(3)
k1.metric("Revenue", f"₹{total_revenue:,}")
k2.metric("Orders", total_orders)
k3.metric("Avg Order", f"₹{avg_order:,}")

st.markdown("---")

# ── Line Chart (Trend) ─────────────────
trend = df.groupby(df["Time"].dt.second)["Price"].sum().reset_index()

fig1 = px.line(trend, x="Time", y="Price", markers=True)
fig1.update_layout(**PLOT_THEME, title="Revenue Trend")
st.plotly_chart(fig1, use_container_width=True)

# ── Row 2 ─────────────────────────────
c1,c2 = st.columns(2)

with c1:
    fig2 = px.bar(df, x="City", y="Price", color="City", color_discrete_sequence=COLORS)
    fig2.update_layout(**PLOT_THEME, title="Revenue by City")
    st.plotly_chart(fig2, use_container_width=True)

with c2:
    fig3 = px.pie(df, names="Product", hole=0.5, color_discrete_sequence=COLORS)
    fig3.update_layout(**PLOT_THEME, title="Product Share")
    st.plotly_chart(fig3, use_container_width=True)

# ── Row 3 ─────────────────────────────
c3,c4 = st.columns(2)

with c3:
    fig4 = px.histogram(df, x="Price", nbins=10, color_discrete_sequence=["#22d3ee"])
    fig4.update_layout(**PLOT_THEME, title="Order Distribution")
    st.plotly_chart(fig4, use_container_width=True)

with c4:
    fig5 = px.scatter(df, x="Price", y="City", size="Price", color="Product",
                      color_discrete_sequence=COLORS)
    fig5.update_layout(**PLOT_THEME, title="Revenue vs City (Bubble)")
    st.plotly_chart(fig5, use_container_width=True)

# ── Heatmap ───────────────────────────
pivot = df.pivot_table(index="City", columns="Product", values="Price", aggfunc="sum", fill_value=0)

fig6 = go.Figure(data=go.Heatmap(
    z=pivot.values,
    x=pivot.columns,
    y=pivot.index,
    colorscale="Viridis"
))
fig6.update_layout(**PLOT_THEME, title="City vs Product Heatmap")

st.plotly_chart(fig6, use_container_width=True)

# ── Table ─────────────────────────────
st.subheader("Recent Transactions")
st.dataframe(df.tail(10), use_container_width=True)

# ── Refresh ───────────────────────────
time.sleep(3)
st.rerun()
