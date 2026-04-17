import streamlit as st
import pandas as pd
import plotly.express as px
import random
import requests
from datetime import datetime

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

# ── AUTO REFRESH (30 sec) ─────────────
st.autorefresh(interval=30000, key="refresh")


# ── WEATHER (OPEN-METEO, NO KEY) ─────
@st.cache_data(ttl=3600)
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
    st.session_state.data = pd.DataFrame(columns=[
        "Time", "Product", "Price", "City", "Weather"
    ])


# ── GENERATE ONLY ONCE PER REFRESH ────
if "last_generated" not in st.session_state:
    st.session_state.last_generated = None

now = datetime.now()

if (st.session_state.last_generated is None or
    (now - st.session_state.last_generated).seconds >= 30):

    product = random.choice(list(PRODUCTS.keys()))
    price = PRODUCTS[product] + random.randint(-200, 300)
    city = random.choice(CITIES)
    weather = get_weather(city)

    new = pd.DataFrame([{
        "Time": now,
        "Product": product,
        "Price": price,
        "City": city,
        "Weather": weather
    }])

    st.session_state.data = pd.concat([st.session_state.data, new], ignore_index=True)

    # LIMIT DATA SIZE (performance fix)
    if len(st.session_state.data) > 200:
        st.session_state.data = st.session_state.data.tail(200)

    st.session_state.last_generated = now


df = st.session_state.data.copy()


# ── HEADER ─────────────────────────────
st.title("📊 AI-Powered Real-Time Sales Dashboard")
st.caption("Live system with Weather Intelligence + AI Insights")


# ── KPIs ───────────────────────────────
total_revenue = df["Price"].sum()
total_orders = len(df)
avg_order = df["Price"].mean() if total_orders else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Revenue", f"₹{int(total_revenue):,}")
col2.metric("📦 Orders", total_orders)
col3.metric("📊 Avg Order", f"₹{int(avg_order):,}")
col4.metric("🌦 Top Weather", df["Weather"].mode()[0] if total_orders else "N/A")


st.markdown("---")


# ── CHARTS ────────────────────────────
c1, c2 = st.columns(2)

with c1:
    fig1 = px.line(df, x="Time", y="Price", markers=True,
                   title="📈 Sales Trend")
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    city_df = df.groupby("City")["Price"].sum().reset_index()
    fig2 = px.bar(city_df, x="City", y="Price", color="City",
                  title="🏙 Revenue by City")
    st.plotly_chart(fig2, use_container_width=True)


c3, c4 = st.columns(2)

with c3:
    weather_df = df.groupby("Weather")["Price"].sum().reset_index()
    fig3 = px.bar(weather_df, x="Weather", y="Price", color="Weather",
                  title="🌦 Weather Impact")
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    fig4 = px.pie(df, names="Product", title="🛍 Product Mix")
    st.plotly_chart(fig4, use_container_width=True)


# ── AI INSIGHTS ───────────────────────
st.markdown("## 🚨 AI Insights Panel")

if len(df) < 5:
    st.info("Collecting data... insights will appear soon.")
else:
    df["rolling_mean"] = df["Price"].rolling(5).mean()
    df["rolling_std"] = df["Price"].rolling(5).std()

    df = df.dropna()

    df["z_score"] = (df["Price"] - df["rolling_mean"]) / df["rolling_std"]

    anomalies = df[df["z_score"].abs() > 2]

    if not anomalies.empty:
        st.warning(f"⚠ {len(anomalies)} anomalies detected!")
        st.dataframe(anomalies[["Time", "City", "Product", "Price"]].tail(5))
    else:
        st.success("No unusual sales behavior detected.")

    # Weather insight
    rain = df[df["Weather"] == "Rain"]["Price"].mean()
    normal = df[df["Weather"] == "Normal"]["Price"].mean()

    if pd.notna(rain) and pd.notna(normal):
        if rain < normal:
            st.info("📉 Rain is reducing sales in affected cities.")
        else:
            st.info("📊 Weather impact is currently neutral or positive.")


# ── TABLE ─────────────────────────────
st.markdown("## 📋 Latest Transactions")

show = df.tail(10).copy()
show["Price"] = show["Price"].apply(lambda x: f"₹{int(x):,}")

st.dataframe(show, use_container_width=True)
