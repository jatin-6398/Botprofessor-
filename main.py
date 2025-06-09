import os
import time
from flask import Flask, request
import telegram
from threading import Timer
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

# Session Data
session_data = {
    "history": [],
    "chat_id": None,
    "last_active": None,
    "timer": None
}

def end_session():
    session_data["history"] = []
    session_data["chat_id"] = None
    session_data["last_active"] = None
    session_data["timer"] = None
    print("⏳ Session auto-ended due to inactivity.")

def reset_timer():
    if session_data["timer"]:
        session_data["timer"].cancel()
    session_data["timer"] = Timer(1800, end_session)  # 30 minutes = 1800 seconds
    session_data["timer"].start()

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    message = update.message.text
    chat_id = update.message.chat.id
    session_data["chat_id"] = chat_id
    session_data["last_active"] = time.time()
    reset_timer()

    if message.lower() == "/start_session":
        session_data["history"] = []
        bot.send_message(chat_id=chat_id, text="📊 Send 100–300 PRNG numbers (like: 3 5 2 8 1...)")
    elif all(c.isdigit() or c.isspace() for c in message):
        numbers = list(map(int, message.strip().split()))
        if 10 <= len(numbers) <= 300:
            session_data["history"] = numbers
            bot.send_message(chat_id=chat_id, text=f"✅ Received {len(numbers)} numbers.\nNow send feedback like ✅ or ❌ after prediction.")
        else:
            bot.send_message(chat_id=chat_id, text="⚠️ Please send between 100–300 numbers.")
    elif message in ["✅", "👍", "❌", "👎"]:
        bot.send_message(chat_id=chat_id, text=f"📩 Feedback received: {message}")
    else:
        bot.send_message(chat_id=chat_id, text="ℹ️ Unknown message. Type /start_session to begin.")

    return 'ok'

@app.route('/')
def home():
    return 'BotProfessor9 is active ✅'

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=10000)
