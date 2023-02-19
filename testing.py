# from datetime import datetime
#
# import ccxt
# import pandas as pd
#
# from configs.configAPI import CONFIG_API
#
# exchange = ccxt.binance({
#     'apiKey': CONFIG_API['BINANCE_API_KEY'],
#     'secret': CONFIG_API['BINANCE_API_SECRET']
# })
#
#
# def getUSDTPairs():
#     tickers = exchange.fetch_tickers()
#     usdtTickers = []
#     for i in tickers:
#         if i.find("USDT") != -1:
#             usdtTickers.append(i)
#     return usdtTickers
#
#
# def fetchSymbolOHLCV(symbol):
#     bars = exchange.fetch_ohlcv(symbol, limit=3)
#
#     df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
#     df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
#
#     return df
#
#
# def detectBigVolume(df):
#     volumeSums = 0
#
#     df_copy = df
#     df_copy['isBigValue'] = False
#
#     for current in range(0, len(df_copy.index) - 1):
#         volumeSums += df_copy['volume'][current]
#
#     lastValueVolume = df_copy.index[-1]
#     average10Volume = volumeSums / (len(df_copy.index) - 1)
#     print('-------------------------------------')
#     print(f'average10Volume {average10Volume}')
#     print(df_copy['volume'][lastValueVolume])
#     if df_copy['volume'][lastValueVolume] > (average10Volume * 2):
#         df_copy.loc[lastValueVolume, 'isBigValue'] = True
#     else:
#         df_copy.loc[lastValueVolume, 'isBigValue'] = False
#
#     return df_copy
#
#
# def check_buy_sell_signals(df, symbol):
#     print('Checking for signals...')
#     print(df)
#     last_row_index = len(df.index) - 1
#
#     if df['isBigValue'][last_row_index]:
#         print(f'{symbol} - big volume!!!')
#
#
# def run_schedule_job():
#     symbols = getUSDTPairs()
#     for symbol in symbols:
#         df = detectBigVolume(fetchSymbolOHLCV(symbol))
#         print(f'{symbol} Fetching new bars for {datetime.now().isoformat()}')
#         check_buy_sell_signals(df, symbol)
#
#
# run_schedule_job()
