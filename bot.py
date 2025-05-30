import telebot
import requests
import numpy as np
from datetime import datetime

# Telegram Bot Token
API_TOKEN = '7838948696:AAHvNO20x0NYDxL0hKUQqj5rUlAS72cad_c'
bot = telebot.TeleBot(API_TOKEN)

# Get Binance candles dynamically based on symbol
def get_binance_candles(symbol):
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=100'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            closes = [float(candle[4]) for candle in data]  # Close prices
            volumes = [float(candle[5]) for candle in data]  # Volumes
            return closes, volumes
        else:
            print(f"Error fetching data: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"Exception: {e}")
        return None, None

def calculate_rsi(prices, period=14):
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

def predict_next_candle(candles):
    ma_short = np.mean(candles[-5:])
    ma_long = np.mean(candles[-20:])
    trend = 'UP' if ma_short > ma_long else 'DOWN'
    return trend, ma_short, ma_long

@bot.message_handler(commands=['predict'])
def handle_predict(message):
    try:
        parts = message.text.split()
        if len(parts) == 2:
            symbol = parts[1].upper()
        else:
            symbol = 'BTCUSDT'  # default symbol

        closes, volumes = get_binance_candles(symbol)
        if closes:
            trend, ma5, ma20 = predict_next_candle(closes)
            rsi = calculate_rsi(closes)
            vol_avg = round(np.mean(volumes[-10:]), 2)

            reply_text = (
                f"📊 {symbol} Prediction:\n\n"
                f"• MA(5): {ma5:.2f}\n"
                f"• MA(20): {ma20:.2f}\n"
                f"• RSI(14): {rsi}\n"
                f"• Avg Volume (10m): {vol_avg}\n"
                f"• Trend: {'📈 UP' if trend == 'UP' else '📉 DOWN'}\n\n"
                f"🔮 Expected next 1m candle: {trend}"
            )
            bot.reply_to(message, reply_text)
        else:
            bot.reply_to(message, f"❌ Failed to fetch candle data for {symbol}.")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {e}")

@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    help_text = (
        "🤖 *Binary Candle Prediction Bot*\n\n"
        "Use the following command to predict:\n"
        "/predict [SYMBOL]\n"
        "Example: /predict BTCUSDT or /predict ETHUSDT\n\n"
        "Default is BTCUSDT if no symbol is provided."
    )
    bot.reply_to(message, help_text, parse_mode='Markdown')

bot.polling()
