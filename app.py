import streamlit as st
import pandas as pd
import plotly.express as px
import random
from datetime import datetime
import requests
import numpy as np

# ── CONFIG ─────────────────────────────
st.set_page_config(page_title="AI Sales Dashboard", layout="wide")

PRODUCTS = {
    "Shoes": 2500,
    "T-Shirt": 1200,
    "Watch": 3500,
    "Bag": 1800,
    "Headphones": 2200
}

CITIES = ["Chennai", "Bangalore", "Hyderabad", "Mumbai", "Delhi"]

# ── WEATHER (OPEN-METEO, NO API KEY) ──
@st.cache_data(ttl=600)
def get_weather(city):
    geo = {
        "Chennai": (13.0827, 80.2707),
        "Bangalore": (12.9716, 77.5946),
        "Hyderabad": (17.3850, 78.4867),
        "Mumbai": (19.0760, 72.8777),
        "Delhi": (28.7041, 77.1025)
    }

    lat, lon = geo[city]

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    data = requests.get(url).json()

    temp = data["current_weather"]["temperature"]
    code = data["current_weather"]["weathercode"]

    if code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return "Rain"
    elif temp > 35:
        return "Heat"
    else:
        return "Normal"


# ── SESSION STATE ─────────────────────
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Time", "Product", "Price", "City", "Weather"])


# ── FAKE SALE GENERATOR ───────────────
def generate_sale():
    product = random.choice(list(PRODUCTS.keys()))
    price = PRODUCTS[product] + random.randint(-200, 300)
    city = random.choice(CITIES)
    weather = get_weather(city)

    new = {
        "Time": datetime.now(),
        "Product": product,
        "Price": price,
        "City": city,
        "Weather": weather
    }

    st.session_state.data = pd.concat(
        [st.session_state.data, pd.DataFrame([new])],
        ignore_index=True
    )


generate_sale()
df = st.session_state.data.copy()

# ── AUTO REFRESH (30 sec) ─────────────
st.markdown("""
<meta http-equiv="refresh" content="30">
""", unsafe_allow_html=True)


# ── HEADER ─────────────────────────────
st.title("📊 AI-Powered Real-Time Sales Intelligence")
st.success("LIVE SYSTEM | Refresh every 30 seconds")


# ── KPIs ───────────────────────────────
total_revenue = df["Price"].sum()
total_orders = len(df)
avg_order = df["Price"].mean() if total_orders else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Revenue", f"₹{int(total_revenue):,}")
c2.metric("📦 Orders", total_orders)
c3.metric("📊 Avg Order", f"₹{int(avg_order):,}")
c4.metric("🌦 Weather Mode", df["Weather"].mode()[0] if total_orders else "N/A")


st.markdown("---")

# ── CHARTS ────────────────────────────
col1, col2 = st.columns(2)

with col1:
    fig1 = px.line(df, x="Time", y="Price", title="📈 Sales Trend", markers=True)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    city_df = df.groupby("City")["Price"].sum().reset_index()
    fig2 = px.bar(city_df, x="City", y="Price", color="City", title="🏙 Revenue by City")
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    weather_df = df.groupby("Weather")["Price"].sum().reset_index()
    fig3 = px.bar(weather_df, x="Weather", y="Price", color="Weather",
                  title="🌦 Weather Impact on Sales")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    fig4 = px.pie(df, names="Product", title="🛍 Product Distribution")
    st.plotly_chart(fig4, use_container_width=True)


# ── ANOMALY DETECTION ──────────────────
st.markdown("## 🚨 AI Insights Panel")

if len(df) > 5:
    df["rolling_mean"] = df["Price"].rolling(5).mean()
    df["rolling_std"] = df["Price"].rolling(5).std()
    df["z_score"] = (df["Price"] - df["rolling_mean"]) / df["rolling_std"]

    anomalies = df[df["z_score"].abs() > 2]

    if not anomalies.empty:
        st.warning("⚠ Anomalies detected in sales spikes/drops!")
        st.dataframe(anomalies[["Time", "City", "Product", "Price"]].tail(5))
    else:
        st.success("No unusual sales behavior detected.")

# ── AI INSIGHT LOGIC ───────────────────
if len(df) > 10:
    rain_sales = df[df["Weather"] == "Rain"]["Price"].mean()
    normal_sales = df[df["Weather"] == "Normal"]["Price"].mean()

    if rain_sales < normal_sales:
        st.info("📉 Insight: Rain is reducing sales performance in affected cities.")
    else:
        st.info("📈 Insight: Weather has positive or neutral impact on sales.")

# ── TABLE ─────────────────────────────
st.markdown("## 📋 Latest Transactions")

show = df.tail(10).copy()
show["Price"] = show["Price"].apply(lambda x: f"₹{int(x):,}")

st.dataframe(show, use_container_width=True)
