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

# ── FULL DARK THEME FIX ──────────────
st.markdown("""
<style>
.stApp { background-color: #0f1117; }

/* Titles */
h1, h2, h3, h4, h5, h6 {
    color: #f9fafb !important;
}

/* General text */
p, span, div, label {
    color: #e5e7eb !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0f1117;
}

section[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

/* Sidebar headers */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #facc15 !important;
}

/* Dropdown text */
div[data-baseweb="select"] * {
    color: #000000 !important;
}

/* Selected filter chips */
span[data-baseweb="tag"] {
    background-color: #6366f1 !important;
    color: white !important;
}

/* Widget labels
*/
label[data-testid="stWidgetLabel"] {
    color: #cbd5f5 !important;
    font-weight: 500;
}

/* Metrics */
[data-testid="metric-container"] label {
    color: #9ca3af !important;
}
[data-testid="metric-container"] div {
    color: #ffffff !important;
}

/* Table */
[data-testid="stDataFrame"] {
    color: #e5e7eb !important;
}
</style>
""", unsafe_allow_html=True)

# ── DATA ─────────────────────────────
PRODUCTS = {"Shoes":2500,"T-Shirt":1200,"Watch":3500,"Bag":1800,"Headphones":2200}
CITIES = ["Chennai","Bangalore","Hyderabad","Mumbai","Delhi"]

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Product","Base","Price","City","Time"])

def generate():
    product = random.choice(list(PRODUCTS.keys()))
    base = PRODUCTS[product]
    price = base + random.randint(-200,300)
    city = random.choice(CITIES)

    new = {
        "Product": product,
        "Base": base,
        "Price": price,
        "City": city,
        "Time": datetime.now()
    }

    st.session_state.data = pd.concat(
        [st.session_state.data, pd.DataFrame([new])],
        ignore_index=True
    )

generate()
df = st.session_state.data.copy()

# ── FILTERS ──────────────────────────
st.sidebar.header("Filters")

city_filter = st.sidebar.multiselect(
    "City",
    df["City"].unique(),
    default=df["City"].unique()
)

product_filter = st.sidebar.multiselect(
    "Product",
    df["Product"].unique(),
    default=df["Product"].unique()
)

filtered_df = df[
    (df["City"].isin(city_filter)) &
    (df["Product"].isin(product_filter))
].copy()

# ── CLEAN DATA ───────────────────────
filtered_df["Price"] = pd.to_numeric(filtered_df["Price"], errors="coerce")
filtered_df["Base"] = pd.to_numeric(filtered_df["Base"], errors="coerce")
filtered_df.dropna(inplace=True)
filtered_df["Size"] = filtered_df["Price"].abs()

# ── METRICS ──────────────────────────
total_revenue = int(filtered_df["Price"].sum())
total_orders = len(filtered_df)
avg_order = int(filtered_df["Price"].mean()) if total_orders else 0

top_product = filtered_df["Product"].value_counts().idxmax() if total_orders else "-"
top_city = filtered_df.groupby("City")["Price"].sum().idxmax() if total_orders else "-"

# ── HEADER ───────────────────────────
st.markdown("<h1 style='color:#6366f1;'>📊 AI Powered Sales Dashboard</h1>", unsafe_allow_html=True)
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
fig1.update_layout(paper_bgcolor="#0f1117", font=dict(color="#e5e7eb"))
st.plotly_chart(fig1, use_container_width=True)

# ── ROW 2 ────────────────────────────
c1,c2 = st.columns(2)

with c1:
    fig2 = px.bar(filtered_df, x="City", y="Price", color="City", color_discrete_sequence=COLORS)
    fig2.update_layout(paper_bgcolor="#0f1117", font=dict(color="#e5e7eb"))
    st.plotly_chart(fig2, use_container_width=True)

with c2:
    fig3 = px.pie(filtered_df, names="Product", hole=0.5, color_discrete_sequence=COLORS[:5])
    fig3.update_layout(paper_bgcolor="#0f1117", font=dict(color="#e5e7eb"))
    st.plotly_chart(fig3, use_container_width=True)

# ── ROW 3 ────────────────────────────
c3,c4 = st.columns(2)

with c3:
    fig4 = px.histogram(filtered_df, x="Price", nbins=10, color_discrete_sequence=[SECONDARY])
    fig4.update_layout(paper_bgcolor="#0f1117", font=dict(color="#e5e7eb"))
    st.plotly_chart(fig4, use_container_width=True)

with c4:
    fig5 = px.scatter(filtered_df, x="Price", y="City", size="Size", color="Product",
                      size_max=40, color_discrete_sequence=COLORS)
    fig5.update_layout(paper_bgcolor="#0f1117", font=dict(color="#e5e7eb"))
    st.plotly_chart(fig5, use_container_width=True)

# ── HEATMAP ──────────────────────────
pivot = filtered_df.pivot_table(index="City", columns="Product", values="Price",
                                aggfunc="sum", fill_value=0)

fig6 = go.Figure(data=go.Heatmap(
    z=pivot.values,
    x=pivot.columns,
    y=pivot.index,
    colorscale=[[0, "#1f2937"], [0.5, SECONDARY], [1, PRIMARY]]
))
fig6.update_layout(paper_bgcolor="#0f1117", font=dict(color="#e5e7eb"))
st.plotly_chart(fig6, use_container_width=True)

# ── AI INSIGHTS ──────────────────────
st.markdown("## 🤖 AI Insights")

if total_orders > 0:
    insight = f"""
    • Top city: {top_city}  
    • Best product: {top_product}  
    • Avg order value: ₹{avg_order}  
    """

    if avg_order > 2500:
        insight += "• Customers spending is HIGH 💰"
    else:
        insight += "• Opportunity to increase sales 📈"

    st.info(insight)

# ── TABLE ────────────────────────────
st.subheader("Recent Transactions")

display_df = filtered_df.tail(10).copy()
display_df["vs Base"] = display_df["Price"] - display_df["Base"]
display_df["vs Base"] = pd.to_numeric(display_df["vs Base"], errors="coerce")
display_df["vs Base"].fillna(0, inplace=True)

display_df["vs Base"] = display_df["vs Base"].apply(
    lambda x: f"+₹{int(x):,}" if x >= 0 else f"-₹{abs(int(x)):,}"
)

display_df["Price"] = display_df["Price"].apply(lambda x: f"₹{int(x):,}")

st.dataframe(display_df, use_container_width=True)

# ── AUTO REFRESH ─────────────────────
time.sleep(2)
st.rerun()
