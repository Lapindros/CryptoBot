import time
from datetime import datetime

import ccxt
import pandas as pd
import schedule
import telebot

from configs.configAPI import CONFIG_API
from configs.configBot import CONFIG_BOT
from services.logger import log_info

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
    log_info("Bot started...")
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
    bot.send_message(message.chat.id, "Bot stopped!")
    log_info("Bot stopped!")


def get_usdt_pairs():
    tickers = exchange.fetch_tickers()
    # tickers = {'BTC/USDT': {}, 'ETH/USDT': {}, 'LUNA/USDT': {}, 'RSR/USDT': {}, 'MCO/USD': {}, 'BSV/USDT': {}}
    usdt_tickers = []
    for i in tickers.keys():
        if i.find("USDT") != -1:
            usdt_tickers.append(i)
    return usdt_tickers


def fetch_symbol_ohlcv(symbol):
    bars = exchange.fetch_ohlcv(symbol, limit=11)

    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

    return df


def detect_big_volume(df):
    volume_sums = 0
    price_close_sums = 0

    df_copy = df
    df_copy['need_to_buy'] = False

    for current in range(0, len(df_copy.index) - 1):
        volume_sums += df_copy['volume'][current]
        price_close_sums += df_copy['close'][current]

    last_value = df_copy.index[-1]
    average10_volume = volume_sums / (len(df_copy.index) - 1)
    average10_close_price = price_close_sums / (len(df_copy.index) - 1)
    print('--------------------------------------------------------------------------')
    print(f'average10_volume - {average10_volume}')
    print(f'last_value - {df_copy["volume"][last_value]}')
    print(f'average10_close_price - {average10_close_price}')
    print(f'Last candle close - {df_copy["close"][last_value]}')

    # and df_copy['close'][last_value] > (average10_close_price * 10)

    if df_copy['volume'][last_value] > (average10_volume * CONFIG_BOT['MULTI_FACTOR']) and df_copy['close'][last_value] > (average10_close_price * CONFIG_BOT['MULTI_FACTOR']):
        df_copy.loc[last_value, 'need_to_buy'] = True
    else:
        df_copy.loc[last_value, 'need_to_buy'] = False

    return df_copy


def check_buy_sell_signals(df, symbol, chat):
    now = datetime.now()

    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print(df)
    last_row_index = len(df.index) - 1
    if df['need_to_buy'][last_row_index]:
        bot.send_message(chat, f'{dt_string} PUMP!!! - {symbol}')
        log_info(f'{dt_string} PUMP!!! - {symbol}')


def run_schedule_job(chat):
    # now = datetime.now()
    # dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    # dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

    symbols = get_usdt_pairs()
    for symbol in symbols:
        df = detect_big_volume(fetch_symbol_ohlcv(symbol))
        print(f'Fetching new bars for {symbol}')
        check_buy_sell_signals(df, symbol, chat)


bot.polling()
