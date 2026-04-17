import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
import time
from datetime import datetime

# ── PAGE CONFIG ───────────────────────
st.set_page_config(page_title="AI Sales Dashboard", layout="wide")

# ── COLORS ───────────────────────────
PRIMARY = "#6366f1"
SECONDARY = "#22d3ee"
SUCCESS = "#10b981"
WARNING = "#f59e0b"
DANGER = "#ef4444"

COLORS = [PRIMARY, SECONDARY, SUCCESS, WARNING, "#ec4899"]

# ── DARK THEME ───────────────────────
st.markdown("""
<style>
.stApp { background-color: #0f1117; }
h1,h2,h3,h4,h5,p { color:#e5e7eb; }

.card {
    background: linear-gradient(145deg,#1a1d27,#11131a);
    padding: 20px;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

# ── DATA ─────────────────────────────
PRODUCTS = {"Shoes":2500,"T-Shirt":1200,"Watch":3500,"Bag":1800,"Headphones":2200}
CITIES = ["Chennai","Bangalore","Hyderabad","Mumbai","Delhi"]

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Product","Price","City","Time"])

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

    st.session_state.data = pd.concat(
        [st.session_state.data, pd.DataFrame([new])],
        ignore_index=True
    )

generate()
df = st.session_state.data

# ── FILTERS ──────────────────────────
st.sidebar.header("Filters")

city_filter = st.sidebar.multiselect(
    "Select City",
    df["City"].unique(),
    default=df["City"].unique()
)

product_filter = st.sidebar.multiselect(
    "Select Product",
    df["Product"].unique(),
    default=df["Product"].unique()
)

filtered_df = df[
    (df["City"].isin(city_filter)) &
    (df["Product"].isin(product_filter))
]

# ── METRICS ──────────────────────────
total_revenue = int(filtered_df["Price"].sum())
total_orders = len(filtered_df)
avg_order = int(filtered_df["Price"].mean()) if total_orders else 0

top_city = filtered_df.groupby("City")["Price"].sum().idxmax() if total_orders else "-"
top_product = filtered_df["Product"].value_counts().idxmax() if total_orders else "-"

# ── HEADER ───────────────────────────
st.title("📊 AI Powered Sales Dashboard")
st.success("● LIVE")

# ── KPI ──────────────────────────────
k1,k2,k3,k4 = st.columns(4)

k1.metric("Revenue", f"₹{total_revenue:,}")
k2.metric("Orders", total_orders)
k3.metric("Avg Order", f"₹{avg_order:,}")
k4.metric("Top Product", top_product)

st.markdown("---")

# ── TREND ────────────────────────────
filtered_df["Time"] = pd.to_datetime(filtered_df["Time"])
trend = filtered_df.sort_values("Time")

fig1 = px.line(trend, x="Time", y="Price", markers=True)
fig1.update_traces(line=dict(color=PRIMARY, width=3))
fig1.update_layout(paper_bgcolor="#0f1117", font=dict(color="white"))

st.plotly_chart(fig1, use_container_width=True)

# ── ROW 2 ────────────────────────────
c1,c2 = st.columns(2)

with c1:
    fig2 = px.bar(filtered_df, x="City", y="Price", color="City",
                  color_discrete_sequence=COLORS)
    fig2.update_layout(paper_bgcolor="#0f1117", font=dict(color="white"))
    st.plotly_chart(fig2, use_container_width=True)

with c2:
    fig3 = px.pie(filtered_df, names="Product", hole=0.5,
                  color_discrete_sequence=COLORS[:5])
    fig3.update_layout(paper_bgcolor="#0f1117", font=dict(color="white"))
    st.plotly_chart(fig3, use_container_width=True)

# ── ROW 3 ────────────────────────────
c3,c4 = st.columns(2)

with c3:
    fig4 = px.histogram(filtered_df, x="Price", nbins=10,
                        color_discrete_sequence=[SECONDARY])
    fig4.update_layout(paper_bgcolor="#0f1117", font=dict(color="white"))
    st.plotly_chart(fig4, use_container_width=True)

with c4:
    fig5 = px.scatter(filtered_df, x="Price", y="City",
                      size="Price", color="Product",
                      color_discrete_sequence=COLORS)
    fig5.update_layout(paper_bgcolor="#0f1117", font=dict(color="white"))
    st.plotly_chart(fig5, use_container_width=True)

# ── HEATMAP ──────────────────────────
pivot = filtered_df.pivot_table(
    index="City",
    columns="Product",
    values="Price",
    aggfunc="sum",
    fill_value=0
)

fig6 = go.Figure(data=go.Heatmap(
    z=pivot.values,
    x=pivot.columns,
    y=pivot.index,
    colorscale=[[0, "#1f2937"], [0.5, SECONDARY], [1, PRIMARY]]
))
fig6.update_layout(paper_bgcolor="#0f1117", font=dict(color="white"))

st.plotly_chart(fig6, use_container_width=True)

# ── AI INSIGHTS ──────────────────────
st.markdown("## 🤖 AI Insights")

if total_orders > 0:
    city_rev = filtered_df.groupby("City")["Price"].sum()
    best_city = city_rev.idxmax()

    insight = f"""
    • Top performing city: {best_city}  
    • Best selling product: {top_product}  
    • Average order value is ₹{avg_order}  
    """

    if avg_order > 2500:
        insight += "• Customers are spending high 💰"
    else:
        insight += "• Opportunity to increase pricing or upsell 📈"

    st.info(insight)

# ── TABLE ────────────────────────────
st.subheader("Recent Transactions")
st.dataframe(filtered_df.tail(10), use_container_width=True)

# ── REFRESH ──────────────────────────
time.sleep(3)
st.rerun()
