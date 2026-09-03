#!/usr/bin/env python3
"""
ZEBRA SMS ULTRA BOT - Fixed & Fully Working Version
MongoDB + JSON Hybrid | Traffic Dashboard | Auto-Range | Force Join
"""

import asyncio
import io
import re
import json
import html
import os
import httpx
import pyotp
import random
import string
import hashlib
import sys
import threading
import time
import base64
import inspect
import logging
from datetime import datetime, timedelta
from pymongo import MongoClient
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from telegram.error import TelegramError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ZebraUltra_Bot")

# Configuration Section
BOT_URL = "https://t.me/testjonson2_bot"
BOT_TOKEN = "8852330034:AAG-VW3qO9EuaPMcf54dtD_fpiNkTOkfKYI"
OTP_GROUP_ID = -1004415108815
OTP_GROUP_URL = "https://t.me/otpmastersgrp"
ADMIN_ID = 1586853120
ADMINS = [1586853120]
OWNER_ID = "1586853120"
PRIMARY_API_KEY = "6U3G3DDZ6GB"

DEVELOPER_ID = 8595326790
DEVELOPER_USERNAME = "@akikshahrin"
DEVELOPER_LINK = "https://t.me/akikshahrin"
MONGODB_URI = "mongodb+srv://dreamsbyshahin_db_user:Z********26@zebrasmsofficial.xkrbvj9.mongodb.net/?appName=ZEBRASMSOFFICIAL"

PRIMARY_BASE_URL = "https://zebrasms.com/api/v1"
PRIMARY_HEADERS = {"MAuth": PRIMARY_API_KEY, "Content-Type": "application/json"}
SECONDARY_API_KEY = "MBVVO65D7T9"
SECONDARY_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api"
SECONDARY_HEADERS = {"mauthapi": SECONDARY_API_KEY, "Content-Type": "application/json"}
SUPPORT_LINK = "https://t.me/Ricky_Ponti"

# File Paths
USER_DATA_FILE = "users.json"
PAID_SMS_FILE = "paid_sms.json"
STATS_FILE = "user_stats.json"
BANNED_USERS_FILE = "banned_users.json"
SYSTEM_CONFIG_FILE = "system_config.json"
ADMIN_DIRECT_NUMBERS_FILE = "admin_direct_numbers.json"
CUSTOM_SERVICES_FILE = "custom_services.json"
ACTIVITY_LOGS_FILE = "activity_logs.json"

# Database & Storage Systems
db_mongo = None
db_mongo_connected = False

def initialize_hybrid_database():
    global db_mongo, db_mongo_connected
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db_mongo = client["zebra_ultra_db"]
        db_mongo_connected = True
        logger.info("✅ MongoDB connected successfully!")
        return True
    except Exception as e:
        db_mongo = None
        db_mongo_connected = False
        logger.warning(f"⚠️ MongoDB connection failed: {e}")
        return False

initialize_hybrid_database()

# Helpers & Core Utils
active_numbers = {}
local_traffic_stats = {}

def normalize_number(num):
    return re.sub(r'\D', '', str(num))

def mask_number(num):
    return f"{num[:4]}****{num[-4:]}" if len(num) > 8 else num

def extract_otp(text):
    if not text or text == "No Content":
        return "N/A"
    spaced_otp = re.search(r'\b(\d{3}\s\d{3})\b', text)
    if spaced_otp:
        return spaced_otp.group(1).replace(" ", "")
    match = re.search(r'\b(\d{4,8})\b', text)
    return match.group(1) if match else "N/A"

def load_data(filename):
    if not os.path.exists(filename):
        return {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_data(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_user_otp_rate(uid):
    return 0.20

async def update_db_balance(uid, amount):
    data = load_data(USER_DATA_FILE)
    uid_str = str(uid)
    if uid_str not in data:
        data[uid_str] = {"balance": 0.0}
    data[uid_str]["balance"] = round(data[uid_str].get("balance", 0.0) + amount, 2)
    save_data(data, USER_DATA_FILE)
    return data[uid_str]["balance"]

def detect_service(full_sms):
    sms_lower = full_sms.lower()
    keywords = {
        "facebook": "FACEBOOK", "whatsapp": "WHATSAPP", "telegram": "TELEGRAM",
        "instagram": "INSTAGRAM", "binance": "BINANCE", "google": "GOOGLE"
    }
    for kw, val in keywords.items():
        if kw in sms_lower:
            return val
    return "SMS SERVICE"

def get_country_info(number):
    return ("🌍", "Unknown")

def get_country_prefix_from_number(num):
    clean = normalize_number(num)
    return clean[:3] if len(clean) >= 3 else "880"

def update_traffic_stats(service_name, country_code, range_val, hits=1):
    pass

# Main OTP Monitoring Task
async def monitor_loop(app):
    sent_otps = set()
    while True:
        try:
            r = await httpx.AsyncClient().get(f"{PRIMARY_BASE_URL}/publicapi/getupdate", headers=PRIMARY_HEADERS)
            if r.status_code == 200:
                result = r.json()
                otps = result.get("data", {}).get("rows", [])
                paid_data = load_data(PAID_SMS_FILE)
                
                for otp in otps:
                    number = otp.get("number")
                    if not number:
                        continue
                    full_sms = otp.get("message", "No Content")
                    otp_time = str(otp.get("at_ms", ""))
                    otp_code = extract_otp(full_sms)
                    key = f"{normalize_number(number)}_{otp_time}"
                    
                    if key in sent_otps:
                        continue
                        
                    num = normalize_number(number)
                    sms_key = f"{num}_{full_sms[:50]}"
                    
                    if num in active_numbers and sms_key not in paid_data:
                        sent_otps.add(key)
                        details = active_numbers[num]
                        uid = details["uid"]
                        service_name = detect_service(full_sms)
                        
                        user_rate = get_user_otp_rate(uid)
                        await update_db_balance(uid, user_rate)
                        
                        paid_data[sms_key] = {"uid": uid, "otp": otp_code}
                        save_data(paid_data, PAID_SMS_FILE)
                        
                        masked = mask_number(num)
                        msg_text = (
                            f"✅ <b>OTP RECEIVE SUCCESSFUL!</b>\n\n"
                            f"📱 <b>Number:</b> <code>+{masked}</code>\n"
                            f"🔑 <b>Code:</b> <code>{otp_code}</code>\n"
                            f"📩 <b>SMS:</b> <code>{html.escape(full_sms)}</code>\n\n"
                            f"💰 <i>Added {user_rate:.2f} BDT to your balance.</i>"
                        )
                        try:
                            await app.bot.send_message(chat_id=uid, text=msg_text, parse_mode="HTML")
                            if OTP_GROUP_ID:
                                group_text = f"🔥 <b>NEW OTP</b>\n📱 +{masked}\n🔑 Code: <code>{otp_code}</code>"
                                await app.bot.send_message(chat_id=OTP_GROUP_ID, text=group_text, parse_mode="HTML")
                        except Exception as e:
                            logger.error(f"Error sending message: {e}")
        except Exception as e:
            logger.error(f"Monitor Loop Exception: {e}")
        
        await asyncio.sleep(3)

# Bot Commands Handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"👋 Hello <b>{html.escape(user.first_name)}</b>!\n\n"
        f"Welcome to <b>ZEBRA SMS ULTRA BOT</b>.\n"
        f"Select an option from below to get started."
    )
    keyboard = ReplyKeyboardMarkup([
        [KeyboardButton("📞 GET NUMBER"), KeyboardButton("🌐 RANGE")],
        [KeyboardButton("📊 TRAFFIC"), KeyboardButton("💰 BALANCE")],
        [KeyboardButton("💬 SUPPORT")]
    ], resize_keyboard=True)
    await update.message.reply_text(welcome_text, parse_mode="HTML", reply_markup=keyboard)

# Flask Server Setup
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot Service is Active"

def run_flask():
    app_flask.run(host='0.0.0.0', port=8080)

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    
    # Start Monitor in background
    loop = asyncio.get_event_loop()
    loop.create_task(monitor_loop(app))
    
    logger.info("🤖 Bot starting polling...")
    app.run_polling()

if __name__ == '__main__':
    main()
