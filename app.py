import streamlit as st
import pandas as pd
import plotly.express as px
import random
import requests
from datetime import datetime
import time

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

# ── STATE ─────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["Time","Product","Price","City","Weather"])

if "last_update" not in st.session_state:
    st.session_state.last_update = 0


# ── WEATHER (CACHED) ──────────────────
@st.cache_data(ttl=3600)
def get_weather(city):
    geo = {
        "Chennai": (13.08, 80.27),
        "Bangalore": (12.97, 77.59),
        "Hyderabad": (17.38, 78.48),
        "Mumbai": (19.07, 72.87),
        "Delhi": (28.70, 77.10)
    }

    lat, lon = geo[city]
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    data = requests.get(url).json()

    temp = data["current_weather"]["temperature"]
    code = data["current_weather"]["weathercode"]

    if code in [51,53,55,61,63,65]:
        return "Rain"
    elif temp > 35:
        return "Heat"
    return "Normal"


# ── STREAM CONTROL ───────────────────
now = time.time()

if now - st.session_state.last_update > 30:

    product = random.choice(list(PRODUCTS.keys()))
    price = PRODUCTS[product] + random.randint(-200, 300)
    city = random.choice(CITIES)
    weather = get_weather(city)

    new_row = pd.DataFrame([{
        "Time": datetime.now(),
        "Product": product,
        "Price": price,
        "City": city,
        "Weather": weather
    }])

    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)

    if len(st.session_state.df) > 200:
        st.session_state.df = st.session_state.df.tail(200)

    st.session_state.last_update = now
    st.rerun()


df = st.session_state.df


# ── HEADER ─────────────────────────────
st.title("📊 AI-Powered Real-Time Sales Intelligence Dashboard")
st.caption("Streaming BI System (No Flicker | Event Driven)")


# ── KPI SECTION ───────────────────────
c1,c2,c3,c4 = st.columns(4)

c1.metric("💰 Revenue", f"₹{df['Price'].sum():,}" if len(df) else "₹0")
c2.metric("📦 Orders", len(df))
c3.metric("📊 Avg Order", f"₹{df['Price'].mean():.0f}" if len(df) else "₹0")
c4.metric("🌦 Mode Weather", df["Weather"].mode()[0] if len(df) else "N/A")

st.markdown("---")


# ── ROW 1: TREND + CITY ──────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Sales Trend")
    if len(df):
        fig1 = px.line(df, x="Time", y="Price", markers=True)
        st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🏙 Revenue by City")
    if len(df):
        city_df = df.groupby("City")["Price"].sum().reset_index()
        fig2 = px.bar(city_df, x="City", y="Price", color="City")
        st.plotly_chart(fig2, use_container_width=True)


# ── ROW 2: PRODUCT + WEATHER ─────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("🛍 Product Distribution")
    if len(df):
        product_df = df["Product"].value_counts().reset_index()
        product_df.columns = ["Product","Count"]
        fig3 = px.pie(product_df, names="Product", values="Count")
        st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("🌦 Weather Impact on Sales")
    if len(df):
        weather_df = df.groupby("Weather")["Price"].sum().reset_index()
        fig4 = px.bar(weather_df, x="Weather", y="Price", color="Weather")
        st.plotly_chart(fig4, use_container_width=True)


# ── AI INSIGHTS ───────────────────────
st.markdown("## 🚨 AI Insights Panel")

if len(df) < 5:
    st.info("Collecting data for AI insights...")
else:
    df["rolling_mean"] = df["Price"].rolling(5).mean()
    df["rolling_std"] = df["Price"].rolling(5).std()
    df = df.dropna()

    df["z_score"] = (df["Price"] - df["rolling_mean"]) / df["rolling_std"]

    anomalies = df[df["z_score"].abs() > 2]

    if len(anomalies):
        st.warning(f"⚠ {len(anomalies)} anomalies detected in sales!")
        st.dataframe(anomalies[["Time","City","Product","Price"]].tail(5))
    else:
        st.success("No anomalies detected.")

    # Weather insight
    rain = df[df["Weather"] == "Rain"]["Price"].mean()
    normal = df[df["Weather"] == "Normal"]["Price"].mean()

    if pd.notna(rain) and pd.notna(normal):
        if rain < normal:
            st.info("📉 Rain is negatively impacting sales performance.")
        else:
            st.info("📊 Weather impact is stable or positive.")


# ── TABLE ─────────────────────────────
st.markdown("## 📋 Latest Transactions")

st.dataframe(df.tail(10), use_container_width=True)
