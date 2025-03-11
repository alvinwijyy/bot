from fastapi import FastAPI
import requests
import pandas as pd
import talib

app = FastAPI()

API_KEY = "bf2dc7f3-5fc2-4af7-aa5a-1e8c616e8a0c"
BASE_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
HEADERS = {"X-CMC_PRO_API_KEY": API_KEY}
CRYPTO_LIST = ["BTC", "ETH", "BNB", "XRP", "ADA"]

def fetch_crypto_data(symbol):
    params = {"symbol": symbol, "convert": "USD"}
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    data = response.json()
    
    if "data" in data and symbol in data["data"]:
        quote = data["data"][symbol]["quote"]["USD"]
        return {
            "price": quote["price"],
            "volume": quote["volume_24h"],
            "market_cap": quote["market_cap"],
            "percent_change_24h": quote["percent_change_24h"]
        }
    return None

def compute_indicators(df):
    df["SMA_20"] = talib.SMA(df["price"], timeperiod=20)
    df["EMA_20"] = talib.EMA(df["price"], timeperiod=20)
    df["RSI"] = talib.RSI(df["price"], timeperiod=14)
    df["MACD"], df["MACD_signal"], _ = talib.MACD(df["price"], fastperiod=12, slowperiod=26, signalperiod=9)
    return df

def generate_signal(df):
    latest = df.iloc[-1]
    buy_signal = (latest["RSI"] < 30 and latest["price"] > latest["SMA_20"]) or (latest["MACD"] > latest["MACD_signal"])
    return "BUY" if buy_signal else "NO BUY"

@app.get("/analyze")
def analyze_cryptos():
    results = []
    for symbol in CRYPTO_LIST:
        data = fetch_crypto_data(symbol)
        if data:
            df = pd.DataFrame([data])
            df = compute_indicators(df)
            signal = generate_signal(df)
            results.append({"symbol": symbol, "price": data["price"], "signal": signal})
    
    return results
