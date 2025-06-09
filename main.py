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
session = {"history": [], "chat_id": None, "timer": None}

# Patterns Definition
BS_PATTERNS = {
    "Single":    ["B","S"]*6,
    "Double":    ["S","S","B","B"]*3,
    "Triple":    ["B","B","B","S","S","S"]*2,
    "Quadra":    ["S"]*4 + ["B"]*4 + ["S"]*4,
    "ThreeInOne":["B","B","B","S","B","S","B","B","B"],
    "TwoInOne":  ["S","S","S","S","B","S","S","S","S"],
    "ThreeInTwo":["B","B","B","S","S","B","B","B","S","S"],
    "FourInOne": ["S","S","S","S","B","B","B","B","S"],
    "FourInTwo": ["B","B","B","B","S","S","B","B","B","B","S","S"],
    "Long":      ["B"]*4 + ["S"]*4 + ["B"]*4 + ["S"]*2,
    "Zigzag":    ["B","S","S","B","B","S","S","B","B","S","S"]
}
RG_PATTERNS = {
    "Single":    ["R","G"]*6,
    "Double":    ["G","G","R","R"]*3,
    "Triple":    ["R","R","R","G","G","G"]*2,
    "Quadra":    ["G"]*4 + ["R"]*4 + ["G"]*4,
    "ThreeInOne":["R","R","R","G","R","G","R","R","R"],
    "TwoInOne":  ["G","G","G","G","R","G","G","G","G"],
    "ThreeInTwo":["R","R","R","G","G","R","R","R","G","G"],
    "FourInOne": ["G","G","G","G","R","R","R","R","G"],
    "FourInTwo": ["R","R","R","R","G","G","R","R","R","R","G","G"],
    "Long":      ["R"]*4 + ["G"]*4 + ["R"]*4 + ["G"]*2,
    "Zigzag":    ["R","G","G","R","R","G","G","R","R","G","G"]
}

def classify_bs(nums):
    return ["B" if n>=5 else "S" for n in nums]

def classify_rg(nums):
    return ["R" if n%2==0 else "G" for n in nums]

def detect_pattern(seq, patterns):
    for name, pat in patterns.items():
        # check if seq ends with pattern slice
        L = len(pat)
        if seq[-L:] == pat:
            return name
    return "No match"

def end_session():
    session.clear()

def reset_timer():
    if session.get("timer"):
        session["timer"].cancel()
    session["timer"] = Timer(1800, end_session)
    session["timer"].start()

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    upd = telegram.Update.de_json(request.get_json(force=True), bot)
    msg = upd.message.text.strip()
    cid = upd.message.chat.id
    session["chat_id"] = cid
    reset_timer()

    if msg.lower()=="/start_session":
        session["history"] = []
        bot.send_message(cid, "📊 Send me 100–300 PRNG numbers now.")
    elif all(c.isdigit() or c.isspace() for c in msg):
        nums = list(map(int, msg.split()))
        if 100 <= len(nums) <= 300:
            session["history"] = nums
            bot.send_message(cid, f"✅ Got {len(nums)} numbers. Now type /analyze to see patterns.")
        else:
            bot.send_message(cid, "⚠️ Send between 100–300 numbers, please.")
    elif msg.lower()=="/analyze":
        nums = session.get("history", [])
        if not nums:
            return 'ok'
        bs_seq = classify_bs(nums)
        rg_seq = classify_rg(nums)
        bs_pat = detect_pattern(bs_seq, BS_PATTERNS)
        rg_pat = detect_pattern(rg_seq, RG_PATTERNS)
        bot.send_message(cid,
            f"🔍 Big/Small Seq: {''.join(bs_seq[-20:])}…\nPattern: {bs_pat}\n\n"
            f"🔍 Red/Green Seq: {''.join(rg_seq[-20:])}…\nPattern: {rg_pat}"
        )
    elif msg in ["✅","👍","❌","👎"]:
        bot.send_message(cid, f"📩 Feedback noted: {msg}")
    else:
        bot.send_message(cid, "ℹ️ Unknown. Use /start_session or /analyze.")

    return 'ok'

@app.route('/')
def home():
    return 'BotProfessor9 Phase2 ✅'

if __name__=="__main__":
    from waitress import serve
    serve(app, host='0.0.0.0', port=10000)
