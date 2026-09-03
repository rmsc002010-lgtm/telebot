import os
import sys
import time
import json
import re
import asyncio
import threading
import logging
import httpx
import pyotp
from flask import Flask
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Logging Setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ==================== System Configuration ====================
BOT_URL = "https://t.me/testjonson2_bot"
BOT_TOKEN = "8852330034:AAG-VW3qO9EuaPMcf54dtD_fpiNkTOkfKYI"
OTP_GROUP_ID = -1004415108815
OTP_GROUP_URL = "https://t.me/otpmastersgrp"

ADMIN_ID = 1586853120
ADMINS = [1586853120]
OWNER_ID = "1586853120"

DEVELOPER_ID = 8595326790
DEVELOPER_USERNAME = "@akikshahrin"
DEVELOPER_LINK = "https://t.me/akikshahrin"
SUPPORT_LINK = "https://t.me/akikshahrin"

MONGODB_URI = "mongodb+srv://dreamsbyshahin_db_user:Z********26@zebrasmsofficial.xkrbvj9.mongodb.net/?appName=ZEBRASMSOFFICIAL"

PRIMARY_API_KEY = "6U3G3DDZ6GB"
PRIMARY_BASE_URL = "https://zebrasms.com/api/v1"
PRIMARY_HEADERS = {"MAuth": PRIMARY_API_KEY, "Content-Type": "application/json"}

SECONDARY_API_KEY = "MBVVO65D7T9"
SECONDARY_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api"
SECONDARY_HEADERS = {"mauthapi": SECONDARY_API_KEY, "Content-Type": "application/json"}

DATA_FILE = "local_database.json"

# ==================== 1. Flask Keep-Alive Server ====================
app = Flask(__name__)

@app.route('/')
def home():
    return "Zebra SMS Ultra Bot Engine Active!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# ==================== 2. Hybrid Database System ====================
class HybridDatabase:
    def __init__(self):
        self.mongo_client = None
        self.db = None
        self.local_data = {"users": {}, "numbers": {}, "active_orders": {}}
        self.init_mongo()
        self.load_local()

    def init_mongo(self):
        try:
            self.mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
            self.db = self.mongo_client["dreamsbyshahin_db_user"]
            self.mongo_client.admin.command('ping')
        except Exception as e:
            logger.warning(f"MongoDB Offline, Local JSON Mode Active: {e}")
            self.mongo_client = None

    def load_local(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    self.local_data = json.load(f)
            except Exception as e:
                logger.error(f"Error loading JSON: {e}")

    def save_local(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.local_data, f, indent=4)

db_system = HybridDatabase()

# ==================== 3. API Call Helper Logic ====================
async def request_number_from_api(service_code="tg", country_code="1"):
    """ Primary API থেকে নম্বর নেওয়ার জন্য কল দেওয়া হয়, ব্যর্থ হলে Secondary এপিআই ট্রাই করে """
    async with httpx.AsyncClient() as client:
        # 1. Try Primary API
        try:
            url = f"{PRIMARY_BASE_URL}/get_number?service={service_code}&country={country_code}"
            res = await client.get(url, headers=PRIMARY_HEADERS, timeout=10)
            data = res.json()
            if res.status_code == 200 and data.get("status") == "success":
                return {
                    "status": True,
                    "number": data.get("number"),
                    "order_id": data.get("id"),
                    "api": "primary"
                }
        except Exception as e:
            logger.error(f"Primary API Error: {e}")

        # 2. Try Secondary API Fallback
        try:
            url = f"{SECONDARY_BASE_URL}/get_number?service={service_code}"
            res = await client.get(url, headers=SECONDARY_HEADERS, timeout=10)
            data = res.json()
            if res.status_code == 200 and "number" in data:
                return {
                    "status": True,
                    "number": data.get("number"),
                    "order_id": data.get("id"),
                    "api": "secondary"
                }
        except Exception as e:
            logger.error(f"Secondary API Error: {e}")

    return {"status": False, "message": "কোনো API থেকে এই মুহূর্তে নম্বর পাওয়া যায়নি।"}

# ==================== 4. Telegram UI & Buy Number Handler ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)
    
    if uid not in db_system.local_data["users"]:
        db_system.local_data["users"][uid] = {
            "name": user.full_name,
            "balance": 50.0,  # Default Trial Balance
        }
        db_system.save_local()

    text = f"👋 **স্বাগতম, {user.first_name}!**\n\n💰 ব্যালেন্স: **{db_system.local_data['users'][uid]['balance']} BDT**"
    keyboard = [
        [InlineKeyboardButton("📱 Get Telegram Number", callback_data="get_num_tg")],
        [InlineKeyboardButton("💬 Get WhatsApp Number", callback_data="get_num_wa")],
        [InlineKeyboardButton("👨‍💻 Support", url=SUPPORT_LINK)]
    ]
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = str(query.from_user.id)

    if query.data.startswith("get_num_"):
        service = query.data.replace("get_num_", "")
        await query.edit_message_text("⏳ API থেকে নম্বর খোঁজা হচ্ছে, অনুগ্রহ করে অপেক্ষা করুন...")
        
        # API কল করে নম্বর রিকোয়েস্ট
        result = await request_number_from_api(service_code=service)
        
        if result["status"]:
            num = result["number"]
            order_id = result["order_id"]
            
            # সেভ একটিভ অর্ডার
            db_system.local_data["active_orders"][uid] = {
                "number": num,
                "order_id": order_id,
                "api": result["api"],
                "time": time.time()
            }
            db_system.save_local()

            text = (
                f"✅ **নম্বর সফলভাবে কেনা হয়েছে!**\n\n"
                f"📱 **নম্বর:** `{num}`\n"
                f"🆔 **Order ID:** `{order_id}`\n\n"
                f"📩 অ্যাপে নম্বর বসিয়ে OTP সেন্ড করুন। ওটিপি আসলে অটোমেটিক শো করবে।"
            )
            btn = [[InlineKeyboardButton("❌ Cancel Order", callback_data=f"cancel_{order_id}")]]
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(btn))
        else:
            await query.edit_message_text(f"❌ **ত্রুটি:** {result['message']}\nপরে আবার চেষ্টা করুন।")

# ==================== 5. Bot Engine Runner ====================
def main():
    threading.Thread(target=run_flask, daemon=True).start()

    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(handle_callback))

    logger.info("Bot Server Online.")
    app_bot.run_polling()

if __name__ == "__main__":
    main()
