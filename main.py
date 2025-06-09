#!/usr/bin/env python3
"""
BotProfessor9_bot – A Telegram bot with multi-dimensional prediction and analysis.
"""

import logging
import re
import time
from datetime import datetime, timedelta
from threading import Timer

from telegram import Update, ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from dotenv import load_dotenv
import os

# --------- Load config ---------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")  # from .env

# Session Timeout in seconds (30 minutes)
SESSION_TIMEOUT = 30 * 60

# Global sessions dict
sessions = {}

# Conversation states
WAITING_FOR_NUMBERS, WAITING_FOR_FEEDBACK = range(2)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# --------- ANALYSIS MODULES (DUMMY) ---------
def multi_dimensional_analysis(data):
    return {"multi_analysis": 1}

def probability_distribution(data):
    return {"prob_distribution": 1}

def trend_identification(data):
    return {"trend": "up" if sum(data) % 2 == 0 else "down"}

def recent_data_weighting(data):
    return {"recent_weight": 1}

def big_small_classification(numbers):
    return ["Big" if n >= 5 else "Small" for n in numbers]

def red_green_classification(numbers):
    return ["Red" if n % 2 == 0 else "Green" for n in numbers]

def dynamic_thresholds(data):
    return {"threshold": 75}

def confidence_score_calculation(data):
    return 80  # dummy

def dual_verification(data):
    return {"dual_verification": True}

def risk_adjustment(data):
    return {"risk_adjustment": 1}

def anomaly_detection_module(data):
    return {"anomaly": False}

def feedback_integration_module(data, feedback):
    return {"feedback_adjusted": True}


def analyze_numbers(numbers, feedback=None):
    analysis = {}
    analysis.update(multi_dimensional_analysis(numbers))
    analysis.update(probability_distribution(numbers))
    analysis.update(trend_identification(numbers))
    analysis.update(recent_data_weighting(numbers))
    analysis["big_small"] = big_small_classification(numbers)
    analysis["red_green"] = red_green_classification(numbers)
    analysis.update(dynamic_thresholds(numbers))
    analysis["confidence"] = confidence_score_calculation(numbers)
    analysis.update(dual_verification(numbers))
    analysis.update(risk_adjustment(numbers))
    analysis.update(anomaly_detection_module(numbers))
    if feedback is not None:
        analysis.update(feedback_integration_module(numbers, feedback))
    return analysis


# --------- SESSION MANAGEMENT ---------
def start_new_session(chat_id: int):
    sessions[chat_id] = {
        "last_activity": datetime.now(),
        "data": {}
    }
    # schedule clear
    Timer(SESSION_TIMEOUT, clear_session, args=(chat_id,)).start()

def update_session_activity(chat_id: int):
    if chat_id in sessions:
        sessions[chat_id]["last_activity"] = datetime.now()

def clear_session(chat_id: int):
    if chat_id in sessions:
        age = datetime.now() - sessions[chat_id]["last_activity"]
        if age.total_seconds() >= SESSION_TIMEOUT:
            del sessions[chat_id]
            logger.info(f"Session cleared for {chat_id}")


# --------- HANDLERS ---------
def start(update: Update, context: CallbackContext) -> int:
    chat_id = update.effective_chat.id
    start_new_session(chat_id)
    update.message.reply_text(
        "Namaste! Session started. Send 10–300 PRNG numbers in one message, space-separated (e.g. `6 3 2 8 2 9 ...`)."
    )
    return WAITING_FOR_NUMBERS

def receive_numbers(update: Update, context: CallbackContext) -> int:
    chat_id = update.effective_chat.id
    update_session_activity(chat_id)
    nums = list(map(int, re.findall(r'\d+', update.message.text)))
    if not (10 <= len(nums) <= 300):
        update.message.reply_text("⚠️ Please send between 10 and 300 numbers.")
        return WAITING_FOR_NUMBERS

    sessions[chat_id]["data"]["numbers"] = nums
    analysis = analyze_numbers(nums)
    conf = analysis.get("confidence", 0)

    # Determine tier
    if conf >= 90:
        tier = "Killer Terd 😎🔥"
    elif conf >= 85:
        tier = "High Probability Terd 🏹"
    elif conf >= 75:
        tier = "Sniper Terd 🎯"
    elif conf >= 70:
        tier = "Best Terd 👍"
    else:
        tier = "Ignore Terd 🚫"

    msg = (
        f"Prediction Confidence: *{conf}%* — *{tier}*\n\n"
        "Modules applied: 1. Multi-Dimensional\n"
        "2. Probability Distn\n3. Trend ID\n4. Recent Wt\n5. Big/Small\n"
        "6. Red/Green\n7. Dual Verif\n8. Risk Adj\n9. Dyn Thr\n10. Conf Score\n\n"
        "Send feedback (number/emoji/text) to update."
    )
    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
    return WAITING_FOR_FEEDBACK

def receive_feedback(update: Update, context: CallbackContext) -> int:
    chat_id = update.effective_chat.id
    update_session_activity(chat_id)
    text = update.message.text
    # extract numeric or emoji feedback
    fb_val = None
    if re.search(r'\d+', text):
        fb_val = int(re.search(r'\d+', text).group())
    else:
        fb_val = 1 if any(e in text for e in ("✅","👍")) else 0

    nums = sessions[chat_id]["data"].get("numbers", [])
    updated = analyze_numbers(nums, feedback=fb_val)
    new_conf = updated.get("confidence", 0)
    resp = (
        f"Feedback: *{text}*\nUpdated Confidence: *{new_conf}%*\n"
        "Session continues until confidence ≥90% or you /cancel."
    )
    update.message.reply_text(resp, parse_mode=ParseMode.MARKDOWN)

    if new_conf >= 90:
        update.message.reply_text("Session complete. Data cleared, bot sleeping for 30 min 😴")
        sessions.pop(chat_id, None)
        return ConversationHandler.END

    return WAITING_FOR_FEEDBACK

def cancel(update: Update, context: CallbackContext) -> int:
    chat_id = update.effective_chat.id
    sessions.pop(chat_id, None)
    update.message.reply_text("Session cancelled. Type /start to begin again.")
    return ConversationHandler.END

def error_handler(update, context):
    logger.error("Error:", exc_info=context.error)


# --------- MAIN ---------
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_FOR_NUMBERS: [MessageHandler(Filters.text & ~Filters.command, receive_numbers)],
            WAITING_FOR_FEEDBACK: [MessageHandler(Filters.text & ~Filters.command, receive_feedback)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=SESSION_TIMEOUT,
    )
    dp.add_handler(conv)
    dp.add_error_handler(error_handler)

    updater.start_polling()
    logger.info("BotProfessor9_bot is up and running!")
    updater.idle()

if __name__ == "__main__":
    main()
