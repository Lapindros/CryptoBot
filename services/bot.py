# import time
#
# import schedule
# import telebot
#
# from configs.configAPI import CONFIG_API
# from services.binance_controller import run_schedule_job
#
# bot = telebot.TeleBot(CONFIG_API['BOT_TOKEN'])
#
#
# @bot.message_handler(commands=['start'])
# def start(message):
#     bot.send_message(message.chat.id, "bot started")
#     bot.send_message(message.chat.id, "fetching started...")
#     schedule.every(5).seconds.do(run_schedule_job(message))
#     while True:
#         schedule.run_pending()
#         time.sleep(1)
