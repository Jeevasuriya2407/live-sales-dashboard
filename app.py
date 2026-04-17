import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px
import random
import requests
from datetime import datetime

# ── AUTO REFRESH (REAL FIX) ──
st_autorefresh(interval=30000, key="refresh")  # 30 seconds

st.set_page_config(layout="wide")

PRODUCTS = {"Shoes":2500,"T-Shirt":1200,"Watch":3500,"Bag":1800,"Headphones":2200}
CITIES = ["Chennai","Bangalore","Hyderabad","Mumbai","Delhi"]

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["Time","Product","Price","City","Weather"])


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
    data = requests.get(url, timeout=5).json()

    temp = data["current_weather"]["temperature"]
    code = data["current_weather"]["weathercode"]

    if code in [51,53,55,61,63,65]:
        return "Rain"
    elif temp > 35:
        return "Heat"
    return "Normal"


# ── GENERATE DATA EVERY REFRESH ──
product = random.choice(list(PRODUCTS.keys()))
price = PRODUCTS[product] + random.randint(-200,300)
city = random.choice(CITIES)
weather = get_weather(city)

st.session_state.df = pd.concat([
    st.session_state.df,
    pd.DataFrame([{
        "Time": datetime.now(),
        "Product": product,
        "Price": price,
        "City": city,
        "Weather": weather
    }])
], ignore_index=True)

df = st.session_state.df.tail(200)


# ── UI ──
st.title("📊 Real-Time AI Sales Dashboard (FIXED STREAMING)")

c1,c2,c3 = st.columns(3)
c1.metric("Revenue", f"₹{df['Price'].sum():,}")
c2.metric("Orders", len(df))
c3.metric("Avg", f"₹{df['Price'].mean():.0f}")


st.markdown("---")

# ── CHARTS ──
st.subheader("📈 Sales Trend")
st.plotly_chart(px.line(df, x="Time", y="Price"), use_container_width=True)

st.subheader("🏙 Revenue by City")
st.plotly_chart(px.bar(df.groupby("City")["Price"].sum().reset_index(),
                       x="City", y="Price", color="City"),
                use_container_width=True)

st.subheader("🛍 Product Mix")
prod = df["Product"].value_counts().reset_index()
prod.columns = ["Product","Count"]
st.plotly_chart(px.pie(prod, names="Product", values="Count"),
                use_container_width=True)

st.subheader("🌦 Weather Impact")
st.plotly_chart(px.bar(df.groupby("Weather")["Price"].sum().reset_index(),
                       x="Weather", y="Price", color="Weather"),
                use_container_width=True)

st.markdown("## 📋 Latest Data")
st.dataframe(df.tail(10), use_container_width=True)
