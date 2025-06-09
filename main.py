
import os
import telebot
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Hello! This is your 24/7 working prediction bot 🔮")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, f"You said: {message.text} 😎")

print("Bot is running...")

bot.polling()
