import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="💰 Crypto Market Dashboard", layout="wide")
st.title("💹 Cryptocurrency Market Dashboard")
st.markdown(
    "Visualize live cryptocurrency prices and trends using data from CoinGecko API.")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Settings")
coins_list = ['bitcoin', 'ethereum', 'ripple', 'litecoin', 'dogecoin']
coin = st.sidebar.selectbox("Select Cryptocurrency", coins_list)
currency = st.sidebar.selectbox("Select Currency", ['eur', 'usd'])
days = st.sidebar.slider("Select Historical Data (days)", 1, 90, 30)

# --- FETCH DATA FUNCTIONS ---


@st.cache_data
def get_current_price(coin, currency):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies={currency}"
    response = requests.get(url).json()
    return response[coin][currency]


@st.cache_data
def get_historical_data(coin, currency, days):
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency={currency}&days={days}"
    response = requests.get(url).json()
    df = pd.DataFrame(response['prices'], columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df


# --- CURRENT PRICE ---
price = get_current_price(coin, currency)
st.subheader(
    f"Current Price of {coin.capitalize()} : {price} {currency.upper()}")

# --- HISTORICAL DATA ---
st.subheader(f"📈 {coin.capitalize()} Price in Last {days} Days")
data = get_historical_data(coin, currency, days)
st.dataframe(data.tail(10))

# --- PRICE CHART ---
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(data['timestamp'], data['price'], label=f"{coin.capitalize()} Price")
ax.set_xlabel("Date")
ax.set_ylabel(f"Price ({currency.upper()})")
ax.legend()
st.pyplot(fig)

# --- MOVING AVERAGE ---
st.subheader("📊 Moving Average")
ma_window = st.slider("Select Moving Average Window (days)", 3, 20, 7)
data['MA'] = data['price'].rolling(ma_window).mean()

fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.plot(data['timestamp'], data['price'], label="Price", alpha=0.7)
ax2.plot(data['timestamp'], data['MA'],
         label=f"{ma_window}-Day MA", color='orange')
ax2.set_xlabel("Date")
ax2.set_ylabel(f"Price ({currency.upper()})")
ax2.legend()
st.pyplot(fig2)

# --- DOWNLOAD DATA ---
csv = data.to_csv(index=False).encode('utf-8')
st.download_button(
    label="⬇️ Download Historical Data as CSV",
    data=csv,
    file_name=f"{coin}_data.csv",
    mime="text/csv"
)
