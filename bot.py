import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

# ====== CONFIG ======
BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN"
CHAT_ID = "PASTE_YOUR_CHAT_ID"
CAPITAL = 100000

stocks = [
    "HAL.NS",
    "BEL.NS",
    "TCS.NS",
    "PFC.NS",
    "REC.NS",
    "TVSMOTOR.NS",
    "RELIANCE.NS",
    "HDFCBANK.NS",
    "INFY.NS",
    "ITC.NS"
]

# =====================

def get_stock_data(symbol):
    data = yf.download(symbol, period="3mo", interval="1d", progress=False)
    data["50DMA"] = data["Close"].rolling(50).mean()
    data["RSI"] = compute_rsi(data["Close"])
    return data

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def generate_report():
    message = f"📊 Daily Portfolio Report – {datetime.today().strftime('%d %b %Y')}\n\n"
    
    allocation = CAPITAL / len(stocks)
    total_value = 0
    
    for stock in stocks:
        data = get_stock_data(stock)
        last = data.iloc[-1]
        price = round(last["Close"], 2)
        rsi = round(last["RSI"], 1)
        dma50 = round(last["50DMA"], 2)
        
        action = "HOLD"
        if rsi < 40:
            action = "ADD"
        elif rsi > 75:
            action = "EXIT"
        
        message += f"{stock.replace('.NS','')}\n"
        message += f"CMP: ₹{price}\n"
        message += f"50DMA: ₹{dma50}\n"
        message += f"RSI: {rsi}\n"
        message += f"Action: {action}\n"
        message += "----------------------\n"
        
        total_value += allocation
    
    message += f"\nCapital: ₹{CAPITAL}"
    message += f"\nInvested: ₹{total_value}"
    
    return message

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

if __name__ == "__main__":
    report = generate_report()
    send_telegram(report)
