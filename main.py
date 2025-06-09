import os
import time
import telebot
from dotenv import load_dotenv

# .env file se BOT_TOKEN uthao
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Bot instance banao
bot = telebot.TeleBot(BOT_TOKEN)

# IMPORTANT: Webhook hatao agar pehle se koi chalu hai
bot.delete_webhook()
time.sleep(1)  # Thoda ruk jao 1 second

# Start command ka response
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Hello! This is your 24/7 working prediction bot 🔮")

# Har message ka reply
@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, f"You said: {message.text} 😎")

# Bot chalu karo
print("🤖 Bot is running... Ready to respond!")
bot.polling()
