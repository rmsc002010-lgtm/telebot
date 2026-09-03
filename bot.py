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

# ==================== System Configuration & Credentials ====================
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
USER_RATES_FILE = "user_otp_rates.json"

# ==================== 1. Flask Keep-Alive Server ====================
app = Flask(__name__)

@app.route('/')
def home():
    return "Zebra SMS Ultra Bot is active and running!"

@app.route('/health')
def health():
    return {"status": "healthy", "timestamp": time.time()}

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# ==================== 2. Hybrid Database Engine ====================
class HybridDatabase:
    def __init__(self):
        self.mongo_client = None
        self.db = None
        self.local_data = {"users": {}, "numbers": {}, "traffic": {}, "settings": {}}
        self.init_mongo()
        self.load_local()

    def init_mongo(self):
        try:
            self.mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
            self.db = self.mongo_client["dreamsbyshahin_db_user"]
            self.mongo_client.admin.command('ping')
            logger.info("MongoDB Connected Successfully.")
        except Exception as e:
            logger.warning(f"MongoDB connection failed, operating in JSON mode: {e}")
            self.mongo_client = None

    def load_local(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    self.local_data = json.load(f)
            except Exception as e:
                logger.error(f"Error loading local JSON database: {e}")

    def save_local(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.local_data, f, indent=4)

    def sync_db(self):
        while True:
            try:
                time.sleep(300)  # Syncs every 5 minutes
                if self.mongo_client:
                    for uid, udata in self.local_data.get("users", {}).items():
                        self.db.users.update_one({"_id": uid}, {"$set": udata}, upsert=True)
                    logger.info("Database auto-sync completed.")
                self.save_local()
            except Exception as e:
                logger.error(f"Auto-Sync Error: {e}")

db_system = HybridDatabase()

# ==================== 3. Security Integrity & Monitoring ====================
def verify_integrity():
    if not BOT_TOKEN or not MONGODB_URI:
        logger.critical("Critical security error: Key tokens missing!")
        sys.exit(1)

def security_monitor():
    while True:
        verify_integrity()
        time.sleep(1800)

# ==================== 4. Number Auto-Cleanup Task ====================
def number_cleanup_loop():
    """ Automatically removes numbers older than 20 minutes (1200 sec) or used numbers """
    while True:
        try:
            time.sleep(60)
            current_time = time.time()
            numbers = db_system.local_data.get("numbers", {})
            to_remove = []

            for num, details in numbers.items():
                added_time = details.get("added_at", 0)
                is_used = details.get("used", False)
                if is_used or (current_time - added_time > 1200):
                    to_remove.append(num)

            for num in to_remove:
                del db_system.local_data["numbers"][num]
                logger.info(f"Auto-removed number: {num}")

            if to_remove:
                db_system.save_local()
        except Exception as e:
            logger.error(f"Error during number cleanup: {e}")

# ==================== 5. Utility Functions ====================
def extract_otp(text):
    match = re.search(r'\b\d{4,8}\b', text)
    return match.group(0) if match else None

def get_number_country_prefix(phone_number):
    clean_num = re.sub(r'\D', '', str(phone_number))
    if clean_num.startswith("880"): return "Bangladesh (+880)"
    if clean_num.startswith("91"): return "India (+91)"
    if clean_num.startswith("1"): return "USA/Canada (+1)"
    return "Global / Unknown"

# ==================== 6. Command & Interaction Handlers ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)
    
    if uid not in db_system.local_data["users"]:
        db_system.local_data["users"][uid] = {
            "name": user.full_name,
            "balance": 0.0,
            "joined_at": time.time(),
            "banned": False
        }
        db_system.save_local()

    text = (
        f"👋 **স্বাগতম, {user.first_name}!**\n\n"
        f"**Zebra SMS Ultra Bot**-এ আপনাকে স্বাগতম।\n"
        f"💰 আপনার বর্তমান ব্যালেন্স: **{db_system.local_data['users'][uid]['balance']} BDT**\n\n"
        f"📢 ওটিপি আপডেট পেতে আমাদের গ্রুপে জয়েন করুন: [OTP Masters Group]({OTP_GROUP_URL})"
    )
    
    keyboard = [
        [InlineKeyboardButton("📱 Buy Number", callback_data="buy_num"), InlineKeyboardButton("📊 Live Traffic", callback_data="traffic")],
        [InlineKeyboardButton("🔐 2FA Generator", callback_data="2fa_gen"), InlineKeyboardButton("👨‍💻 Support", url=SUPPORT_LINK)]
    ]
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard), disable_web_page_preview=True)

async def generate_2fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("কীভাবে ব্যবহার করবেন: `/2fa <YOUR_SECRET_KEY>`", parse_mode="Markdown")
        return
    
    secret = context.args[0].replace(" ", "")
    try:
        totp = pyotp.TOTP(secret)
        code = totp.now()
        await update.message.reply_text(f"🔑 **আপনার 2FA কোড:** `{code}`", parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("❌ অকার্যকর Secret Key! সঠিক Key প্রদান করুন।")

async def add_manual_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return

    if not context.args:
        await update.message.reply_text("ব্যবহার নিয়ম: `/addnum <Phone_Number> <Service_Name>`", parse_mode="Markdown")
        return

    num = context.args[0]
    service = context.args[1] if len(context.args) > 1 else "General"
    
    db_system.local_data["numbers"][num] = {
        "service": service,
        "added_at": time.time(),
        "used": False,
        "country": get_number_country_prefix(num)
    }
    db_system.save_local()
    await update.message.reply_text(f"✅ **নম্বর যোগ করা হয়েছে!**\n📱 নম্বর: `{num}`\n⏱️ ২০ মিনিট পর এটি স্বয়ংক্রিয়ভাবে ডিলিট হয়ে যাবে।", parse_mode="Markdown")

# ==================== 7. Asynchronous Primary API & OTP Polling Loop ====================
async def monitor_otp_loop():
    async with httpx.AsyncClient() as client:
        while True:
            try:
                # Primary API (zebrasms.com) & Secondary API (2oo9.cloud) Monitor Task
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Error in background OTP poller: {e}")
                await asyncio.sleep(5)

# ==================== 8. Application Startup ====================
def main():
    verify_integrity()

    # Background threads startup
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=db_system.sync_db, daemon=True).start()
    threading.Thread(target=security_monitor, daemon=True).start()
    threading.Thread(target=number_cleanup_loop, daemon=True).start()

    # Bot Builder Setup
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers Registration
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("2fa", generate_2fa))
    app_bot.add_handler(CommandHandler("addnum", add_manual_number))

    logger.info("Zebra SMS Ultra Bot successfully started.")
    app_bot.run_polling()

if __name__ == "__main__":
    main()
