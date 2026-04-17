import streamlit as st
import pandas as pd
import plotly.express as px
import random
import requests
from datetime import datetime
import time

# ─────────────────────────────
# CONFIG
# ─────────────────────────────
st.set_page_config(page_title="AI Sales Dashboard", layout="wide")

PRODUCTS = {
    "Shoes": 2500,
    "T-Shirt": 1200,
    "Watch": 3500,
    "Bag": 1800,
    "Headphones": 2200
}

CITIES = ["Chennai", "Bangalore", "Hyderabad", "Mumbai", "Delhi"]

# ─────────────────────────────
# STATE INIT
# ─────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["Time","Product","Price","City","Weather"])

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# ─────────────────────────────
# AUTO REFRESH CONTROL (ROOT FIX)
# ─────────────────────────────
now = time.time()

if now - st.session_state.last_refresh > 30:
    st.session_state.last_refresh = now

    # ── generate new sale ──
    product = random.choice(list(PRODUCTS.keys()))
    price = PRODUCTS[product] + random.randint(-200, 300)
    city = random.choice(CITIES)

    # simple weather simulation (safe, no API crash risk)
    weather = random.choice(["Rain", "Heat", "Normal"])

    new_row = pd.DataFrame([{
        "Time": datetime.now(),
        "Product": product,
        "Price": price,
        "City": city,
        "Weather": weather
    }])

    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)

    # limit memory
    if len(st.session_state.df) > 200:
        st.session_state.df = st.session_state.df.tail(200)

    st.rerun()

df = st.session_state.df

# ─────────────────────────────
# HEADER
# ─────────────────────────────
st.title("📊 Real-Time AI Sales Dashboard (Stable Version)")
st.caption("Streamlit Cloud Safe | No Flicker | Event Driven")

# ─────────────────────────────
# KPIs
# ─────────────────────────────
c1, c2, c3, c4 = st.columns(4)

c1.metric("Revenue", f"₹{df['Price'].sum():,}" if len(df) else "₹0")
c2.metric("Orders", len(df))
c3.metric("Avg Order", f"₹{df['Price'].mean():.0f}" if len(df) else "₹0")
c4.metric("Top City", df["City"].mode()[0] if len(df) else "N/A")

st.markdown("---")

# ─────────────────────────────
# CHART 1 - TREND
# ─────────────────────────────
st.subheader("📈 Sales Trend")
if len(df) > 1:
    fig = px.line(df, x="Time", y="Price", markers=True)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────
# CHART 2 - CITY REVENUE
# ─────────────────────────────
st.subheader("🏙 Revenue by City")
if len(df):
    city_df = df.groupby("City")["Price"].sum().reset_index()
    fig = px.bar(city_df, x="City", y="Price", color="City")
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────
# CHART 3 - PRODUCT MIX
# ─────────────────────────────
st.subheader("🛍 Product Distribution")
if len(df):
    prod_df = df["Product"].value_counts().reset_index()
    prod_df.columns = ["Product", "Count"]
    fig = px.pie(prod_df, names="Product", values="Count")
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────
# CHART 4 - WEATHER IMPACT
# ─────────────────────────────
st.subheader("🌦 Weather Impact on Sales")
if len(df):
    weather_df = df.groupby("Weather")["Price"].sum().reset_index()
    fig = px.bar(weather_df, x="Weather", y="Price", color="Weather")
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────
# AI INSIGHTS
# ─────────────────────────────
st.markdown("## 🚨 AI Insights")

if len(df) < 5:
    st.info("Collecting data for insights...")
else:
    temp = df.copy()

    temp["mean"] = temp["Price"].rolling(5).mean()
    temp["std"] = temp["Price"].rolling(5).std()
    temp = temp.dropna()

    if len(temp):
        temp["z"] = (temp["Price"] - temp["mean"]) / temp["std"]
        anomalies = temp[temp["z"].abs() > 2]

        if len(anomalies):
            st.warning(f"{len(anomalies)} anomalies detected")
            st.dataframe(anomalies[["Time","City","Product","Price"]].tail(5))
        else:
            st.success("No anomalies detected")

    rain = df[df["Weather"] == "Rain"]["Price"].mean()
    normal = df[df["Weather"] == "Normal"]["Price"].mean()

    if pd.notna(rain) and pd.notna(normal):
        if rain < normal:
            st.info("Rain is reducing sales")
        else:
            st.info("Weather impact is stable")

# ─────────────────────────────
# TABLE
# ─────────────────────────────
st.markdown("## 📋 Latest Transactions")
st.dataframe(df.tail(10), use_container_width=True)
