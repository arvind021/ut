import telebot
import requests
import numpy as np
from datetime import datetime

# Telegram Bot Token
API_TOKEN = '7838948696:AAHvNO20x0NYDxL0hKUQqj5rUlAS72cad_c'
bot = telebot.TeleBot(API_TOKEN)

# Binance API URL for 1-minute candles (BTCUSDT pair)
BINANCE_API_URL = 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=100'

def get_binance_candles():
    try:
        response = requests.get(BINANCE_API_URL)
        if response.status_code == 200:
            data = response.json()
            candles = [float(candle[4]) for candle in data]  # close prices only
            return candles
        else:
            print(f"Error fetching data: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def predict_next_candle(candles):
    # Simple moving average strategy
    ma_short = np.mean(candles[-5:])
    ma_long = np.mean(candles[-20:])
    if ma_short > ma_long:
        return 'UP'
    else:
        return 'DOWN'

@bot.message_handler(commands=['predict'])
def handle_predict(message):
    candles = get_binance_candles()
    if candles:
        prediction = predict_next_candle(candles)
        bot.reply_to(message, f"📈 Next 1-minute candle prediction: {prediction}")
    else:
        bot.reply_to(message, "❌ Failed to fetch candle data from Binance.")

bot.polling()
