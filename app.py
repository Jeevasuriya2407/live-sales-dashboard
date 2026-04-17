import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time
import random
from datetime import datetime

# ─────────────────────────────
# CONFIG
# ─────────────────────────────
st.set_page_config(page_title="Live Revenue Pulse", layout="wide")

PRODUCTS = {
    "Shoes": 2500,
    "T-Shirt": 1200,
    "Watch": 3500,
    "Bag": 1800,
    "Headphones": 2200
}

CITIES = ["Chennai", "Bangalore", "Hyderabad", "Mumbai", "Delhi"]

# ─────────────────────────────
# DAY 1 — Fake Sale Generator
# (runs inside Streamlit Cloud)
# ─────────────────────────────
def generate_sale(order_id):
    product = random.choice(list(PRODUCTS.keys()))
    price   = PRODUCTS[product] + random.randint(-200, 300)
    city    = random.choice(CITIES)
    return {
        "OrderID":   order_id,
        "Product":   product,
        "Price":     price,
        "City":      city,
        "Timestamp": datetime.now()
    }

# ─────────────────────────────
# DAY 3 — Real Weather API
# ─────────────────────────────
def get_weather(city):
    coords = {
        "Chennai":   (13.08, 80.27),
        "Bangalore": (12.97, 77.59),
        "Hyderabad": (17.38, 78.48),
        "Mumbai":    (19.07, 72.87),
        "Delhi":     (28.61, 77.21)
    }
    try:
        lat, lon = coords[city]
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}&current_weather=true"
        )
        res  = requests.get(url, timeout=5).json()
        temp = res["current_weather"]["temperature"]
        code = res["current_weather"]["weathercode"]

        if temp >= 30:
            impact = "🔥 Heat Impact"
        elif code in [51,53,55,61,63,65,71,73,75,80,81,82,95,96,99]:
            impact = "🌧️ Rain Impact"
        else:
            impact = "☁️ Normal"

        return temp, impact
    except:
        return "N/A", "⚠️ Unavailable"

# ─────────────────────────────
# STATE INIT
# ─────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(
        columns=["OrderID","Product","Price","City","Timestamp"]
    )
    st.session_state.order_id      = 1001
    st.session_state.last_sale     = time.time() - 31
    st.session_state.last_weather  = time.time() - 301
    st.session_state.weather_cache = {}

# ─────────────────────────────
# DAY 2 — Generate sale every 30s
# ─────────────────────────────
now = time.time()

if now - st.session_state.last_sale > 30:
    new_row = generate_sale(st.session_state.order_id)
    st.session_state.df = pd.concat(
        [st.session_state.df, pd.DataFrame([new_row])],
        ignore_index=True
    )
    st.session_state.order_id  += 1
    st.session_state.last_sale  = now

    if len(st.session_state.df) > 200:
        st.session_state.df = st.session_state.df.tail(200)

# ─────────────────────────────
# DAY 3 — Refresh weather every 5 min
# ─────────────────────────────
if now - st.session_state.last_weather > 300:
    st.session_state.weather_cache = {}
    st.session_state.last_weather  = now

for city in CITIES:
    if city not in st.session_state.weather_cache:
        temp, impact = get_weather(city)
        st.session_state.weather_cache[city] = (temp, impact)

# ─────────────────────────────
# LOAD DATA
# ─────────────────────────────
df = st.session_state.df

# ─────────────────────────────
# HEADER
# ─────────────────────────────
st.title("📊 Live Revenue Pulse")
st.caption(
    f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
    f"| New sale every 30s | Weather refreshes every 5 min"
)

st.markdown("---")

# ─────────────────────────────
# DAY 2 — KPI Counters
# ─────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Total Revenue",   f"₹{int(df['Price'].sum()):,}"       if len(df) else "₹0")
c2.metric("🛒 Total Orders",    len(df))
c3.metric("📦 Avg Order Value", f"₹{int(df['Price'].mean()):,}"      if len(df) else "₹0")
c4.metric("📍 Active Cities",   df["City"].nunique()                  if len(df) else 0)

st.markdown("---")

# ─────────────────────────────
# DAY 3 — Weather Impact Table
# ─────────────────────────────
st.subheader("🌦️ Live Weather Impact by City")

weather_rows = []
for city in CITIES:
    temp, impact     = st.session_state.weather_cache.get(city, ("N/A", "⚠️ Unavailable"))
    city_revenue     = int(df[df["City"] == city]["Price"].sum()) if len(df) else 0
    city_orders      = len(df[df["City"] == city])
    weather_rows.append({
        "City":           city,
        "Temperature":    f"{temp}°C",
        "Weather Impact": impact,
        "Total Revenue":  f"₹{city_revenue:,}",
        "Orders":         city_orders
    })

st.table(pd.DataFrame(weather_rows))

st.markdown("---")

# ─────────────────────────────
# CHARTS
# ─────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Sales Trend")
    if len(df) > 1:
        fig = px.line(df, x="Timestamp", y="Price", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Waiting for sales data...")

with col2:
    st.subheader("🏙️ Revenue by City")
    if len(df):
        city_rev = df.groupby("City")["Price"].sum().reset_index()
        fig = px.bar(city_rev, x="City", y="Price", color="City")
        st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("🛍️ Product Distribution")
    if len(df):
        prod_df = df["Product"].value_counts().reset_index()
        prod_df.columns = ["Product", "Count"]
        fig = px.pie(prod_df, names="Product", values="Count")
        st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("🏆 Revenue by Product")
    if len(df):
        prod_rev = df.groupby("Product")["Price"].sum().reset_index()
        fig = px.bar(prod_rev, x="Product", y="Price", color="Product")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ─────────────────────────────
# RECENT SALES
# ─────────────────────────────
st.subheader("📋 Recent Sales")
if len(df):
    st.dataframe(
        df.tail(10).sort_values("Timestamp", ascending=False),
        use_container_width=True
    )

# ─────────────────────────────
# AUTO RERUN every 30s
# ─────────────────────────────
time.sleep(30)
st.rerun()
