import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

# ================= CONFIG =================
BOT_TOKEN = "8269225957:AAHzGpYQvT5jXEka9Be0nN08jLEmBVEI4zo"
CHAT_ID = "1579119023"
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
# ===========================================


def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def get_stock_data(symbol):
    try:
        data = yf.download(symbol, period="3mo", interval="1d", progress=False)

        if data.empty:
            return None

        data["50DMA"] = data["Close"].rolling(50).mean()
        data["RSI"] = compute_rsi(data["Close"])

        return data

    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None


def generate_report():
    today = datetime.today().strftime('%d %b %Y')
    message = f"📊 Daily Portfolio Report – {today}\n\n"

    allocation = CAPITAL / len(stocks)
    total_invested = 0

    for stock in stocks:
        data = get_stock_data(stock)

        if data is None or data.empty:
            continue

        last = data.iloc[-1]

        price = round(float(last["Close"]), 2)
        rsi = round(float(last["RSI"]), 1)
        dma50 = round(float(last["50DMA"]), 2)

        # ===== Signal Logic =====
        action = "HOLD"

        if rsi < 35 and price > dma50:
            action = "STRONG BUY"
        elif rsi < 40:
            action = "ADD"
        elif rsi > 75:
            action = "EXIT"
        elif price < dma50:
            action = "WEAK"

        # ========================

        message += f"🔹 {stock.replace('.NS','')}\n"
        message += f"CMP: ₹{price}\n"
        message += f"50DMA: ₹{dma50}\n"
        message += f"RSI: {rsi}\n"
        message += f"Signal: {action}\n"
        message += "----------------------\n"

        total_invested += allocation

    message += f"\n💰 Capital: ₹{CAPITAL}"
    message += f"\n📈 Allocated: ₹{int(total_invested)}"

    return message


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=payload)


if __name__ == "__main__":
    report = generate_report()
    send_telegram(report)
