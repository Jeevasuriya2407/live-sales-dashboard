import streamlit as st
import pandas as pd
import plotly.express as px
import random
import time
import requests
from datetime import datetime

st.set_page_config(layout="wide")

# ── DATA ─────────────────────────────
PRODUCTS = {"Shoes":2500, "T-Shirt":1200, "Watch":3500, "Bag":1800}
CITIES = ["Chennai", "Bangalore", "Mumbai", "Delhi"]

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["Time","Product","Price","City","Weather"])


# ── WEATHER (cached) ────────────────
@st.cache_data(ttl=3600)
def get_weather(city):
    geo = {
        "Chennai": (13.08, 80.27),
        "Bangalore": (12.97, 77.59),
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


# ── UI PLACEHOLDERS (KEY FIX) ───────
kpi = st.empty()
chart1 = st.empty()
chart2 = st.empty()
table = st.empty()


# ── STREAMING LOOP ───────────────────
while True:

    # Generate ONE new record only
    product = random.choice(list(PRODUCTS.keys()))
    price = PRODUCTS[product] + random.randint(-200,300)
    city = random.choice(CITIES)
    weather = get_weather(city)

    new_row = {
        "Time": datetime.now(),
        "Product": product,
        "Price": price,
        "City": city,
        "Weather": weather
    }

    st.session_state.df = pd.concat(
        [st.session_state.df, pd.DataFrame([new_row])],
        ignore_index=True
    )

    df = st.session_state.df.copy()

    # ── KPIs ──
    with kpi.container():
        c1,c2,c3 = st.columns(3)
        c1.metric("Revenue", f"₹{df['Price'].sum():,}")
        c2.metric("Orders", len(df))
        c3.metric("Avg", f"₹{df['Price'].mean():.0f}")

    # ── CHARTS ──
    with chart1.container():
        fig = px.line(df, x="Time", y="Price", title="Live Sales Trend")
        st.plotly_chart(fig, use_container_width=True)

    with chart2.container():
        city_df = df.groupby("City")["Price"].sum().reset_index()
        fig2 = px.bar(city_df, x="City", y="Price", color="City")
        st.plotly_chart(fig2, use_container_width=True)

    # ── TABLE ──
    with table.container():
        st.dataframe(df.tail(10))

    time.sleep(3)   # control speed
