
import os
import telebot
from flask import Flask, request

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def home():
    return "🤖 BotProfessor9 is live!"

@bot.message_handler(commands=['start'])
def send_welcome(msg):
    bot.send_message(msg.chat.id, "👋 Hello! BotProfessor9_bot is now running 24/7 on Render! 🚀")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://botprofessor9.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
