import os
import time                    # ⬅️ time import karo
import telebot
from dotenv import load_dotenv

load_dotenv()                  # .env se token load

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# 🔥 Add these lines to clear any existing webhook/getUpdates conflict
bot.delete_webhook()          
time.sleep(1)                  # thoda wait karo taaki webhook delete ho jaye

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Hello! This is your 24/7 working prediction bot 🔮")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, f"You said: {message.text} 😎")

print("✅ Bot is running...")

bot.polling()                  # ab conflict error nahi aayega
