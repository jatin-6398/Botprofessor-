import os
import time                   # ⬅️ time import
import telebot
from dotenv import load_dotenv

load_dotenv()                 # .env से token ले
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# 🔥 पूरी तरह से webhook या पुराने polling हटाने के लिए:
bot.remove_webhook()          # old webhook हटाओ
time.sleep(2)                 # 2 सेकंड का छोटा इंतज़ार

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Hello! Prediction bot is live 🔮")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, f"You said: {message.text} 😎")

print("✅ Bot is running with infinite polling...")

# 👇 इसे use करो:
bot.infinity_polling(skip_pending=True)
