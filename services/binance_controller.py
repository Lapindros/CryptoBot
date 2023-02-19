import time
from datetime import datetime

import ccxt
import pandas as pd
import schedule
import telebot

from configs.configAPI import CONFIG_API

exchange = ccxt.binance({
    'apiKey': CONFIG_API['BINANCE_API_KEY'],
    'secret': CONFIG_API['BINANCE_API_SECRET']
})

bot = telebot.TeleBot(CONFIG_API['BOT_TOKEN'])


# Crypt1Arrzz1Faast_bot

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Hello, {message.from_user.first_name} {message.from_user.last_name}')
    bot.send_message(message.chat.id, "Bot started...")
    users = [message.chat.id]
    for chat in users:
        schedule.every(10).seconds.do(run_schedule_job, chat)
    while True:
        schedule.run_pending()
        time.sleep(1)


@bot.message_handler(commands=['stop'])
def stop(message):
    schedule.clear()
    print(schedule.get_jobs())
    bot.send_message(message.chat.id, "Bot stopped")


def getUSDTPairs():
    tickers = exchange.fetch_tickers()
    # tickers = {'BTC/USDT': {}, 'ETH/USDT': {}, 'LUNA/USDT': {}, 'RSR/USDT': {}, 'MCO/USD': {}, 'BSV/USDT': {}}
    usdtTickers = []
    for i in tickers.keys():
        if i.find("USDT") != -1:
            usdtTickers.append(i)
    return usdtTickers


def fetchSymbolOHLCV(symbol):
    bars = exchange.fetch_ohlcv(symbol, limit=11)

    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    return df


def detectBigVolume(df):
    volumeSums = 0
    priceCloseSums = 0

    df_copy = df
    df_copy['isBigValue'] = False

    for current in range(0, len(df_copy.index) - 1):
        volumeSums += df_copy['volume'][current]
        priceCloseSums += df_copy['close'][current]

    lastValue = df_copy.index[-1]
    average10Volume = volumeSums / (len(df_copy.index) - 1)
    average10ClosePrice = priceCloseSums / (len(df_copy.index) - 1)
    print('--------------------------------------------------------------------------')
    print(f'average10Volume - {average10Volume}')
    print(f'lastValue - {df_copy["volume"][lastValue]}')
    print(f'average10ClosePrice - {average10ClosePrice}')
    print(f'Last candle close - {df_copy["close"][lastValue]}')

    # and df_copy['close'][lastValue] > (average10ClosePrice * 10)

    if df_copy['volume'][lastValue] > (average10Volume * 10) and df_copy['close'][lastValue] > (
            average10ClosePrice * 10):
        df_copy.loc[lastValue, 'isBigValue'] = True
    else:
        df_copy.loc[lastValue, 'isBigValue'] = False

    return df_copy


def check_buy_sell_signals(df, symbol, chat):
    now = datetime.now()

    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print(df)
    last_row_index = len(df.index) - 1

    if df['isBigValue'][last_row_index]:
        bot.send_message(chat, f'{dt_string} {symbol} - PUMP!!! Buy!!!')


def run_schedule_job(chat):
    now = datetime.now()

    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    symbols = getUSDTPairs()
    for symbol in symbols:
        df = detectBigVolume(fetchSymbolOHLCV(symbol))
        print(f'{symbol} Fetching new bars for {dt_string}')
        check_buy_sell_signals(df, symbol, chat)


bot.polling()
