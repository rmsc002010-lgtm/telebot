#!/usr/bin/env python3
"""
🦓 ZEBRA SMS ULTRA BOT - Ultimate Version (ALL BUGS FIXED)
MongoDB + JSON Hybrid | Premium UI | Traffic Dashboard | Auto-Range | Force Join
"""
# ══════════════════════════════════════════════════════════════════════════════
# 🔥 IMPORTS SECTION 🔥
# ══════════════════════════════════════════════════════════════════════════════
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

# ══════════════════════════════════════════════════════════════════════════════
# 🔒 CONFIGURATION SECTION 🔒
# ══════════════════════════════════════════════════════════════════════════════
BOT_URL = "https://t.me/testjonson2_bot"
BOT_TOKEN = "8852330034:AAG-VW3qO9EuaPMcf54dtD_fpiNkTOkfKYI"
OTP_GROUP_ID = -1004415108815
OTP_GROUP_URL = "https://t.me/otpmastersgrp"
ADMIN_ID = 1586853120
ADMINS = [1586853120]
OWNER_ID = "1586853120"
PRIMARY_API_KEY = "6U3G3DDZ6GB"

# ══════════════════════════════════════════════════════════════════════════════
# 🔒 CONFIGURATION SECTION — DO NOT CHANGE ANYTHING BELOW 🔒
# ⚠️ কোনো কিছু পরিবর্তন করলে Bot কাজ নাও করতে পারে!
# ══════════════════════════════════════════════════════════════════════════════
DEVELOPER_ID = 8595326790
DEVELOPER_USERNAME = "@akikshahrin"
DEVELOPER_LINK = "https://t.me/akikshahrin"
MONGODB_URI = "mongodb+srv://dreamsbyshahin_db_user:Z********26@zebrasmsofficial.xkrbvj9.mongodb.net/?appName=ZEBRASMSOFFICIAL"

CRITICAL_PATTERNS = [
    b"DEVELOPER_USERNAME", b"Zebra_Sms_Support_Admin", b"security_check",
    b"verify_integrity", b"DEVELOPER BY", b"CONFIGURATION SECTION",
    b"DO NOT EDIT BELOW THIS LINE", b"MONGODB_URI",
    b"dreamsbyshahin_db_user", b"zebrasmsofficial.xkrbvj9"
]

def verify_integrity():
    try:
        main_file = __file__
        if not os.path.exists(main_file):
            return False, "Main.py not found"
        with open(main_file, "rb") as f:
            file_content = f.read()
        for pattern in CRITICAL_PATTERNS:
            if pattern not in file_content:
                return False, f"Missing pattern: {pattern.decode()}"
        if DEVELOPER_USERNAME.encode() not in file_content:
            return False, "Developer signature missing"
        if b"DO NOT EDIT BELOW THIS LINE" not in file_content:
            return False, "Security boundary missing"
        return True, "OK"
    except Exception as e:
        return False, f"Error: {str(e)}"

def security_check():
    print("🔐 Running security check...")
    ok, msg = verify_integrity()
    if not ok:
        print(f"🚨 SECURITY VIOLATION: {msg}")
        print(f"📞 Contact Developer: {DEVELOPER_USERNAME}")
        sys.exit(1)
    print("✅ Security check passed!")

def periodic_security_check():
    while True:
        time.sleep(1800)
        ok, msg = verify_integrity()
        if not ok:
            print(f"🚨 TAMPERING DETECTED: {msg}")
            sys.exit(1)

def start_periodic_check():
    security_check()
    thread = threading.Thread(target=periodic_security_check, daemon=True)
    thread.start()
    print("✅ Periodic security check started (every 30 minutes)")
    

PRIMARY_BASE_URL = "https://zebrasms.com/api/v1"
PRIMARY_HEADERS = {"MAuth": PRIMARY_API_KEY, "Content-Type": "application/json"}
SECONDARY_API_KEY = "MBVVO65D7T9"
SECONDARY_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api"
SECONDARY_HEADERS = {"mauthapi": SECONDARY_API_KEY, "Content-Type": "application/json"}
SUPPORT_LINK = "https://t.me/akikshahrin"
RANGE_GROUP_LINK = "https://t.me/zebra_sms02"
DEFAULT_CHANNEL_LINK = "https://t.me/ApexNum_file_Group"
DEFAULT_CHANNEL_LABEL = "@Id_Bazaar_Support"

# ══════════════════════════════════════════════════════════════════════════════
# 🗄️ HYBRID DATABASE SETUP
# ══════════════════════════════════════════════════════════════════════════════
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

app_flask = Flask(__name__)

@app_flask.route('/')
def keep_alive():
    return f"Zebra SMS Ultra Bot is running 24/7! | Hybrid DB: {'MongoDB Active' if db_mongo_connected else 'JSON Fallback Active'}"

@app_flask.route('/health')
def health_check():
    return {
        "status": "running",
        "mongodb": "connected" if db_mongo_connected else "disconnected",
        "timestamp": datetime.now().isoformat()
    }

def run_flask():
    app_flask.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_flask, daemon=True).start()
logger.info("🌐 Flask Keep-Alive Server started on port 8080")

# ══════════════════════════════════════════════════════════════════════════════
# 📁 FILE PATHS
# ══════════════════════════════════════════════════════════════════════════════
USER_DATA_FILE = "users.json"
PAID_SMS_FILE = "paid_sms.json"
STATS_FILE = "user_stats.json"
REFERRAL_DATA_FILE = "referral_data.json"
BANNED_USERS_FILE = "banned_users.json"
WITHDRAW_DATA_FILE = "withdraw_requests.json"
ACTIVITY_LOGS_FILE = "activity_logs.json"
DATA_RANGE_FILE = "datarange.json"
SYSTEM_CONFIG_FILE = "system_config.json"
USER_OTP_RATE_FILE = "user_otp_rates.json"
REQUIRED_CHANNELS_FILE = "required_channels.json"
ADMIN_DIRECT_NUMBERS_FILE = "admin_direct_numbers.json"
CUSTOM_SERVICES_FILE = "custom_services.json"
REFERRAL_HISTORY_FILE = "referral_history.json"
PAYMENT_HISTORY_FILE = "payment_history.json"
VIP_USERS_FILE = "vip_users.json"
BACKUP_FOLDER = "backups"

# ══════════════════════════════════════════════════════════════════════════════
# 🎯 HYBRID DATABASE FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def hybrid_save(collection_name, data_id, data_dict):
    try:
        filename = f"hybrid_{collection_name}.json"
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                existing = json.load(f)
        else:
            existing = {}
        existing[str(data_id)] = data_dict
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Hybrid JSON save error: {e}")
    if db_mongo_connected and db_mongo is not None:
        try:
            collection = db_mongo[collection_name]
            data_dict["_id"] = str(data_id)
            data_dict["last_updated"] = datetime.now().isoformat()
            collection.update_one({"_id": str(data_id)}, {"$set": data_dict}, upsert=True)
        except Exception as e:
            logger.error(f"Hybrid MongoDB save error: {e}")

def hybrid_load(collection_name, data_id=None):
    if db_mongo_connected and db_mongo is not None:
        try:
            collection = db_mongo[collection_name]
            if data_id:
                doc = collection.find_one({"_id": str(data_id)})
                if doc:
                    doc.pop("_id", None)
                    doc.pop("last_updated", None)
                    return doc
            else:
                docs = collection.find({})
                result = {}
                for doc in docs:
                    doc_id = doc.pop("_id", None)
                    doc.pop("last_updated", None)
                    if doc_id:
                        result[doc_id] = doc
                if result:
                    return result
        except Exception as e:
            logger.error(f"Hybrid MongoDB load error: {e}")
    try:
        filename = f"hybrid_{collection_name}.json"
        if not os.path.exists(filename):
            return {} if not data_id else None
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data_id:
            return data.get(str(data_id))
        return data
    except Exception as e:
        logger.error(f"Hybrid JSON load error: {e}")
        return {} if not data_id else None

def hybrid_delete(collection_name, data_id):
    try:
        filename = f"hybrid_{collection_name}.json"
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            if str(data_id) in data:
                del data[str(data_id)]
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Hybrid JSON delete error: {e}")
    if db_mongo_connected and db_mongo is not None:
        try:
            collection = db_mongo[collection_name]
            collection.delete_one({"_id": str(data_id)})
        except Exception as e:
            logger.error(f"Hybrid MongoDB delete error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# 🔄 PERIODIC MONGODB SYNC
# ══════════════════════════════════════════════════════════════════════════════
def sync_all_data_to_mongodb():
    if not db_mongo_connected or db_mongo is None:
        return False, "MongoDB not connected"
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, "r") as f:
                users_data = json.load(f)
            db_mongo.users_data.update_one(
                {"_id": "all_users"},
                {"$set": {"data": users_data, "updated": datetime.now().isoformat()}},
                upsert=True
            )
        if os.path.exists(SYSTEM_CONFIG_FILE):
            with open(SYSTEM_CONFIG_FILE, "r") as f:
                config = json.load(f)
            db_mongo.system_config.update_one(
                {"_id": "main_config"},
                {"$set": {"config": config, "updated": datetime.now().isoformat()}},
                upsert=True
            )
        if os.path.exists(BANNED_USERS_FILE):
            with open(BANNED_USERS_FILE, "r") as f:
                banned = json.load(f)
            db_mongo.banned_users.update_one(
                {"_id": "banned_list"},
                {"$set": {"list": banned, "updated": datetime.now().isoformat()}},
                upsert=True
            )
        if os.path.exists(REQUIRED_CHANNELS_FILE):
            with open(REQUIRED_CHANNELS_FILE, "r") as f:
                channels = json.load(f)
            db_mongo.required_channels.update_one(
                {"_id": "channels_list"},
                {"$set": {"channels": channels, "updated": datetime.now().isoformat()}},
                upsert=True
            )
        logger.info("✅ All data synced to MongoDB successfully!")
        return True, "Sync successful"
    except Exception as e:
        logger.error(f"❌ MongoDB sync error: {e}")
        return False, str(e)

def periodic_mongodb_sync():
    while True:
        time.sleep(300)
        try:
            sync_all_data_to_mongodb()
        except Exception as e:
            logger.error(f"Periodic sync error: {e}")

threading.Thread(target=periodic_mongodb_sync, daemon=True).start()
logger.info("🔄 Periodic MongoDB sync thread started (every 5 minutes)")

# ══════════════════════════════════════════════════════════════════════════════
# 📥 RESTORE FROM MONGODB ON STARTUP
# ══════════════════════════════════════════════════════════════════════════════
def restore_from_mongodb():
    if not db_mongo_connected or db_mongo is None:
        logger.info("ℹ️ MongoDB not connected, skipping restore")
        return
    try:
        doc = db_mongo.users_data.find_one({"_id": "all_users"})
        if doc and doc.get("data"):
            if not os.path.exists(USER_DATA_FILE) or os.path.getsize(USER_DATA_FILE) < 10:
                with open(USER_DATA_FILE, "w") as f:
                    json.dump(doc["data"], f, indent=4)
                logger.info("✅ Users data restored from MongoDB")
        doc = db_mongo.system_config.find_one({"_id": "main_config"})
        if doc and doc.get("config"):
            if not os.path.exists(SYSTEM_CONFIG_FILE):
                with open(SYSTEM_CONFIG_FILE, "w") as f:
                    json.dump(doc["config"], f, indent=4)
                logger.info("✅ System config restored from MongoDB")
        doc = db_mongo.banned_users.find_one({"_id": "banned_list"})
        if doc and doc.get("list"):
            if not os.path.exists(BANNED_USERS_FILE):
                with open(BANNED_USERS_FILE, "w") as f:
                    json.dump(doc["list"], f, indent=4)
                logger.info("✅ Banned users restored from MongoDB")
        logger.info("✅ MongoDB restore completed successfully!")
    except Exception as e:
        logger.error(f"❌ MongoDB restore error: {e}")

restore_from_mongodb()

# ══════════════════════════════════════════════════════════════════════════════
# 🎨 PREMIUM CUSTOM EMOJIS
# ══════════════════════════════════════════════════════════════════════════════
PREMIUM_CUSTOM_EMOJIS = {
    "zenex": "<tg-emoji emoji-id='5334763399299506604'>😒</tg-emoji>",
    "time": "<tg-emoji emoji-id='5336983442125001376'>🕓</tg-emoji>",
    "otp": "<tg-emoji emoji-id='5337255927735163754'>🔐</tg-emoji>",
    "fire": "<tg-emoji emoji-id='5337267511261960341'>🔥</tg-emoji>",
    "king": "<tg-emoji emoji-id='5353032893096567467'>👑</tg-emoji>",
    "dashboard": "<tg-emoji emoji-id='5352877703043258544'>📊</tg-emoji>",
    "user": "<tg-emoji emoji-id='5352861489541714456'>👤</tg-emoji>",
    "rocket": "<tg-emoji emoji-id='5352597830089347330'>🚀</tg-emoji>",
    "gem": "<tg-emoji emoji-id='5352838545826420397'>💎</tg-emoji>",
    "done": "<tg-emoji emoji-id='5352694861990501856'>✅</tg-emoji>",
    "error": "<tg-emoji emoji-id='5420130255174145507'>❌</tg-emoji>",
    "search": "<tg-emoji emoji-id='5463352748751753567'>🔍</tg-emoji>",
    "number": "<tg-emoji emoji-id='5337132498965010628'>🍏</tg-emoji>",
    "phone": "<tg-emoji emoji-id='5355208818017999139'>📱</tg-emoji>",
    "warn": "<tg-emoji emoji-id='5336944168944047463'>⚠️</tg-emoji>",
    "wait": "<tg-emoji emoji-id='5337172996211648018'>⏳</tg-emoji>",
    "note": "<tg-emoji emoji-id='5395444784611480792'>📝</tg-emoji>",
    "world": "<tg-emoji emoji-id='5336972142066047577'>🌐</tg-emoji>",
    "gear": "<tg-emoji emoji-id='5420155432272438703'>⚙️</tg-emoji>",
    "back": "<tg-emoji emoji-id='5267490665117275176'>⬅️</tg-emoji>",
    "shield": "<tg-emoji emoji-id='5190447043545438788'>🛡</tg-emoji>",
    "money": "<tg-emoji emoji-id='5348469219761626211'>💰</tg-emoji>",
    "lock": "<tg-emoji emoji-id='5337255927735163754'>🔒</tg-emoji>",
    "star": "<tg-emoji emoji-id='5352838545826420397'>⭐</tg-emoji>",
    "bell": "<tg-emoji emoji-id='5395444784611480792'>🔔</tg-emoji>",
    "pin": "<tg-emoji emoji-id='5334763399299506604'>📌</tg-emoji>",
    "country": "<tg-emoji emoji-id='5336972142066047577'>🌍</tg-emoji>",
    "service": "<tg-emoji emoji-id='5352838545826420397'>📱</tg-emoji>"
}

PREMIUM_APP_EMOJIS = {
    "facebook": "5334807341109908955", "whatsapp": "5334759662677957452",
    "telegram": "5337010556253543833", "imo": "5337155807752524558",
    "instagram": "5334868205091459431", "apple": "5334637951894722661",
    "google": "5335010201005231986", "microsoft": "5334880948259427772",
    "tiktok": "5339213256001102461", "amazon": "4995019580536524226",
    "twitter": "5215726959056662534", "snapchat": "5359441366554255082",
    "netflix": "6255738712664050133", "linkedin": "6224222994265279792",
    "discord": "5116246243646898866", "viber": "5463060437572528782",
    "wechat": "5782757599560602950", "line": "5399818044866327279",
    "paypal": "5776103539872896061", "uber": "5298715455316303708",
    "bkash": "5348469219761626211", "rocket": "5352597830089347330",
    "binance": "5348212415077064131", "gmail": "5348494358205207761",
    "messenger": "5348486915026884464", "pubg": "5337132498965010628",
    "freefire": "5337132498965010628"
}

PREMIUM_FLAG_EMOJIS = {
    "BD": {"phone_code": "880", "flag": "🇧🇩", "name": "Bangladesh", "id": "5336972142066047577"},
    "IN": {"phone_code": "91", "flag": "🇮🇳", "name": "India", "id": "5911154710571651231"},
    "US": {"phone_code": "1", "flag": "🇺🇸", "name": "United States", "id": "5913274246867456342"},
    "GB": {"phone_code": "44", "flag": "🇬🇧", "name": "United Kingdom", "id": "5913460373570195273"},
    "CM": {"phone_code": "237", "flag": "🇨🇲", "name": "Cameroon", "id": "5911172109484167745"},
    "CI": {"phone_code": "225", "flag": "🇨🇮", "name": "Ivory Coast", "id": "5222233374948602940"},
    "MG": {"phone_code": "261", "flag": "🇲🇬", "name": "Madagascar", "id": "5913766918271012920"},
    "RO": {"phone_code": "40", "flag": "🇷🇴", "name": "Romania", "id": "5913460373570195273"},
    "KE": {"phone_code": "254", "flag": "🇰🇪", "name": "Kenya", "id": "5911154710571651231"},
    "NG": {"phone_code": "234", "flag": "🇳🇬", "name": "Nigeria", "id": "5911143844304393105"},
    "EG": {"phone_code": "20", "flag": "🇪🇬", "name": "Egypt", "id": "5911143844304393105"},
    "ZA": {"phone_code": "27", "flag": "🇿🇦", "name": "South Africa", "id": "5911143844304393105"},
    "GH": {"phone_code": "233", "flag": "🇬🇭", "name": "Ghana", "id": "5911143844304393105"},
    "TZ": {"phone_code": "255", "flag": "🇹🇿", "name": "Tanzania", "id": "5911418949844603556"},
    "UG": {"phone_code": "256", "flag": "🇺🇬", "name": "Uganda", "id": "5911143844304393105"},
    "FR": {"phone_code": "33", "flag": "🇫🇷", "name": "France", "id": "5913460373570195273"},
    "DE": {"phone_code": "49", "flag": "🇩🇪", "name": "Germany", "id": "5913460373570195273"},
    "PK": {"phone_code": "92", "flag": "🇵🇰", "name": "Pakistan", "id": "5911287639809463107"},
    "RU": {"phone_code": "7", "flag": "🇷🇺", "name": "Russia", "id": "5913274246867456342"},
    "CN": {"phone_code": "86", "flag": "🇨🇳", "name": "China", "id": "5913274246867456342"},
    "JP": {"phone_code": "81", "flag": "🇯🇵", "name": "Japan", "id": "5913274246867456342"},
    "KR": {"phone_code": "82", "flag": "🇰🇷", "name": "South Korea", "id": "5913274246867456342"},
    "BR": {"phone_code": "55", "flag": "🇧🇷", "name": "Brazil", "id": "5911418949844603556"},
    "MX": {"phone_code": "52", "flag": "🇲🇽", "name": "Mexico", "id": "5911418949844603556"},
    "AU": {"phone_code": "61", "flag": "🇦🇺", "name": "Australia", "id": "5911418949844603556"}
}

def get_premium_custom_emoji(key, default="✨"):
    return PREMIUM_CUSTOM_EMOJIS.get(key, default)

def get_app_premium_emoji(app_name):
    if not app_name:
        return "<tg-emoji emoji-id='5336879280578138635'>🖥</tg-emoji>"
    name_lower = app_name.lower()
    for key, emoji_id in PREMIUM_APP_EMOJIS.items():
        if key in name_lower:
            return f"<tg-emoji emoji-id='{emoji_id}'>📱</tg-emoji>"
    return "<tg-emoji emoji-id='5336879280578138635'>🖥</tg-emoji>"

def get_premium_flag_emoji(phone_code_or_country):
    clean_code = str(phone_code_or_country).replace("+", "").strip()
    for short_code, info in PREMIUM_FLAG_EMOJIS.items():
        if info.get("phone_code") == clean_code:
            return f"<tg-emoji emoji-id='{info.get('id', '5336972142066047577')}'>{info['flag']}</tg-emoji>"
    if clean_code.upper() in PREMIUM_FLAG_EMOJIS:
        info = PREMIUM_FLAG_EMOJIS[clean_code.upper()]
        return f"<tg-emoji emoji-id='{info.get('id', '5336972142066047577')}'>{info['flag']}</tg-emoji>"
    return "<tg-emoji emoji-id='5336972142066047577'>🌍</tg-emoji>"

# ══════════════════════════════════════════════════════════════════════════════
# 📊 LIVE TRAFFIC TRACKING SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
local_traffic_stats = {}
traffic_last_updated = None
AUTO_RANGE_MODE = False

def update_traffic_stats(service_name, country_code, range_val, hits=1):
    global local_traffic_stats, traffic_last_updated
    if not service_name or not country_code:
        return
    service_name = service_name.strip().title()
    country_code = country_code.strip().upper()
    if service_name not in local_traffic_stats:
        local_traffic_stats[service_name] = {}
    if country_code not in local_traffic_stats[service_name]:
        local_traffic_stats[service_name][country_code] = {"success": 0, "ranges": {}}
    local_traffic_stats[service_name][country_code]["success"] += hits
    if range_val:
        range_val = range_val.strip().upper()
        if range_val not in local_traffic_stats[service_name][country_code]["ranges"]:
            local_traffic_stats[service_name][country_code]["ranges"][range_val] = 0
        local_traffic_stats[service_name][country_code]["ranges"][range_val] += hits
    traffic_last_updated = datetime.now()

def get_traffic_stats():
    return local_traffic_stats, traffic_last_updated

def get_top_ranges_for_service_country(service_name, country_code, limit=5):
    if service_name not in local_traffic_stats:
        return []
    if country_code not in local_traffic_stats[service_name]:
        return []
    ranges_dict = local_traffic_stats[service_name][country_code].get("ranges", {})
    if not ranges_dict:
        return []
    sorted_ranges = sorted(ranges_dict.items(), key=lambda x: x[1], reverse=True)
    return sorted_ranges[:limit]

def toggle_auto_range_mode():
    global AUTO_RANGE_MODE
    AUTO_RANGE_MODE = not AUTO_RANGE_MODE
    return AUTO_RANGE_MODE

def get_auto_range_mode():
    return AUTO_RANGE_MODE

async def auto_select_best_range(service_name, country_code):
    if not get_auto_range_mode():
        return None
    top_ranges = get_top_ranges_for_service_country(service_name, country_code, limit=1)
    if top_ranges:
        return top_ranges[0][0]
    return None

async def search_number_in_traffic(query):
    query = str(query).strip().upper()
    results = []
    for service, countries in local_traffic_stats.items():
        for country, data in countries.items():
            for range_val, hits in data.get("ranges", {}).items():
                if query in range_val or query in country or query.lower() in service.lower():
                    results.append({
                        "service": service,
                        "country": country,
                        "range": range_val,
                        "hits": hits
                    })
    results.sort(key=lambda x: x["hits"], reverse=True)
    return results[:20]

# ══════════════════════════════════════════════════════════════════════════════
# 🛡️ FORCE JOIN SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
async def check_force_join(user_id, message=None, context=None):
    if is_admin(user_id):
        return True
    channels = get_all_required_channels()
    if not channels:
        return True
    not_joined = []
    for channel in channels:
        chat_id = channel.get("chat_id")
        username = channel.get("username")
        check_id = chat_id or username
        if not check_id:
            continue
        try:
            if context and context.bot:
                member = await context.bot.get_chat_member(check_id, user_id)
                if member.status in ["left", "kicked", "restricted"]:
                    not_joined.append(channel)
            else:
                not_joined.append(channel)
        except Exception as e:
            logger.warning(f"Force join check failed for {check_id}: {e}")
            not_joined.append(channel)
    if not_joined and message:
        text = (
            f"{get_premium_custom_emoji('shield')} <b>ACCESS RESTRICTED</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{get_premium_custom_emoji('warn')} <b>Hello!</b> To use our bot services, you must join our official channels listed below.\n"
            f"<i>After joining, click the '✅ Check Again' button to verify.</i>"
        )
        buttons = []
        for ch in not_joined:
            label = ch.get("label", "Join Channel")
            url = ch.get("link")
            if url:
                buttons.append([InlineKeyboardButton(f"📢 {label}", url=url)])
        buttons.append([InlineKeyboardButton("✅ Check Again", callback_data="check_force_join")])
        await message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))
        return False
    return len(not_joined) == 0

# ══════════════════════════════════════════════════════════════════════════════
# 🎨 ADVANCED UI/UX FORMATTING
# ══════════════════════════════════════════════════════════════════════════════
def format_premium_box(title, content, style="primary"):
    styles = {
        "primary": ("╔", "═", "╗", "║", "╚", "╝"),
        "success": ("┏", "━", "┓", "┃", "┗", "┛"),
        "danger": ("┌", "─", "┐", "│", "└", "┘")
    }
    chars = styles.get(style, styles["primary"])
    box = f"{chars[0]}{chars[1]*20}{chars[2]}\n"
    box += f"{chars[3]} {title} {chars[3]}\n"
    box += f"{chars[4]}{chars[1]*20}{chars[5]}"
    return f"{box}\n{content}"

def format_premium_divider(style="primary"):
    dividers = {
        "primary": "━━━━━━━━━━━━━━━━━━━━━━",
        "success": "══════════════════════",
        "danger": "──────────────────────"
    }
    return dividers.get(style, dividers["primary"])

# ══════════════════════════════════════════════════════════════════════════════
# 📊 TRAFFIC DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def render_traffic_dashboard():
    stats, last_updated = get_traffic_stats()
    if not stats:
        return (
            f"{get_premium_custom_emoji('dashboard')} <b>LIVE TRAFFIC DASHBOARD</b>\n"
            f"{format_premium_divider('primary')}\n"
            f"<i>কোনো ট্রাফিক ডাটা নেই। কিছুক্ষণ পর আবার চেষ্টা করুন।</i>"
        )
    total_services = len(stats)
    total_hits = sum(data["success"] for countries in stats.values() for data in countries.values())
    text = (
        f"{get_premium_custom_emoji('dashboard')} <b>LIVE TRAFFIC DASHBOARD</b>\n"
        f"{format_premium_divider('primary')}\n"
        f"{get_premium_custom_emoji('world')} <b>Total Services:</b> <code>{total_services}</code>\n"
        f"{get_premium_custom_emoji('rocket')} <b>Total Hits:</b> <code>{total_hits:,}</code>\n"
    )
    if last_updated:
        text += f"{get_premium_custom_emoji('time')} <b>Last Updated:</b> <code>{last_updated.strftime('%I:%M %p')}</code>\n"
    text += f"\n{format_premium_divider('success')}\n"
    services_with_totals = []
    for service, countries in stats.items():
        service_total = sum(data["success"] for data in countries.values())
        services_with_totals.append((service, service_total, countries))
    services_with_totals.sort(key=lambda x: x[1], reverse=True)
    for idx, (service, total, countries) in enumerate(services_with_totals[:10], 1):
        app_emoji = get_app_premium_emoji(service)
        text += f"{idx}. {app_emoji} <b>{service}</b> - <code>{total:,}</code> hits\n"
        sorted_countries = sorted(countries.items(), key=lambda x: x[1]["success"], reverse=True)
        for country, data in sorted_countries[:3]:
            flag_emoji = get_premium_flag_emoji(country)
            text += f"   {flag_emoji} {country}: <code>{data['success']:,}</code>\n"
        text += "\n"
    if len(services_with_totals) > 10:
        text += f"<i>... এবং আরও {len(services_with_totals) - 10}টি সার্ভিস</i>\n"
    return text

def build_traffic_keyboard():
    stats, _ = get_traffic_stats()
    if not stats:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh", callback_data="traffic_refresh")],
            [InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]
        ])
    buttons = []
    services_with_totals = []
    for service, countries in stats.items():
        service_total = sum(data["success"] for data in countries.values())
        services_with_totals.append((service, service_total))
    services_with_totals.sort(key=lambda x: x[1], reverse=True)
    for service, total in services_with_totals[:8]:
        app_emoji = get_app_premium_emoji(service)
        buttons.append([InlineKeyboardButton(f"{app_emoji} {service} ({total:,})", callback_data=f"traffic_svc_{service}")])
    buttons.append([
        InlineKeyboardButton("🔄 Refresh", callback_data="traffic_refresh"),
        InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")
    ])
    return InlineKeyboardMarkup(buttons)

def build_service_traffic_keyboard(service_name):
    if service_name not in local_traffic_stats:
        return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="traffic_home")]])
    countries = local_traffic_stats[service_name]
    buttons = []
    sorted_countries = sorted(countries.items(), key=lambda x: x[1]["success"], reverse=True)
    for country, data in sorted_countries[:10]:
        flag_emoji = get_premium_flag_emoji(country)
        buttons.append([InlineKeyboardButton(f"{flag_emoji} {country} ({data['success']:,})", callback_data=f"traffic_ctr_{service_name}_{country}")])
    buttons.append([InlineKeyboardButton("🔙 BACK", callback_data="traffic_home")])
    return InlineKeyboardMarkup(buttons)

def build_country_traffic_keyboard(service_name, country_code):
    if service_name not in local_traffic_stats or country_code not in local_traffic_stats[service_name]:
        return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data=f"traffic_svc_{service_name}")]])
    data = local_traffic_stats[service_name][country_code]
    ranges = data.get("ranges", {})
    sorted_ranges = sorted(ranges.items(), key=lambda x: x[1], reverse=True)
    buttons = []
    for range_val, hits in sorted_ranges[:10]:
        buttons.append([InlineKeyboardButton(f"📋 {range_val} ({hits})", callback_data=f"copy_range_{range_val}")])
    buttons.append([InlineKeyboardButton("🔙 BACK", callback_data=f"traffic_svc_{service_name}")])
    return InlineKeyboardMarkup(buttons)

# ══════════════════════════════════════════════════════════════════════════════
# 🎯 TRAFFIC COMMANDS
# ══════════════════════════════════════════════════════════════════════════════
async def traffic_command(update, context):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return
    if not await check_force_join(uid, message=update.message, context=context):
        return
    text = render_traffic_dashboard()
    keyboard = build_traffic_keyboard()
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)

async def search_command(update, context):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return
    if not context.args:
        await update.message.reply_text(
            f"{get_premium_custom_emoji('search')} <b>SEARCH TRAFFIC</b>\n"
            f"<blockquote>🔍 সার্চ করতে নিচের ফরম্যাট ব্যবহার করুন:\n"
            f"<code>/search 237</code> (Country Code)\n"
            f"<code>/search 237620</code> (Range)\n"
            f"<code>/search Facebook</code> (Service Name)</blockquote>\n"
            f"<i>আপনি নাম্বার, রেঞ্জ, বা সার্ভিস নাম দিয়ে সার্চ করতে পারবেন।</i>",
            parse_mode="HTML"
        )
        return
    query = " ".join(context.args)
    results = await search_number_in_traffic(query)
    if not results:
        await update.message.reply_text(
            f"{get_premium_custom_emoji('error')} <b>কোনো রেজাল্ট পাওয়া যায়নি!</b>\n"
            f"<blockquote>🔍 Query: <code>{html.escape(query)}</code></blockquote>\n"
            f"<i>অন্য কিছু দিয়ে সার্চ করে দেখুন।</i>",
            parse_mode="HTML",
            reply_markup=main_keyboard(uid)
        )
        return
    text = (
        f"{get_premium_custom_emoji('search')} <b>SEARCH RESULTS</b>\n"
        f"{format_premium_divider('primary')}\n"
        f"<blockquote>🔍 Query: <code>{html.escape(query)}</code>\n"
        f"📊 মোট রেজাল্ট: <b>{len(results)}</b></blockquote>\n"
    )
    for idx, result in enumerate(results[:10], 1):
        app_emoji = get_app_premium_emoji(result["service"])
        flag_emoji = get_premium_flag_emoji(result["country"])
        text += (
            f"{idx}. {app_emoji} <b>{result['service']}</b>\n"
            f"   {flag_emoji} {result['country']} - <code>{result['range']}</code>\n"
            f"   {get_premium_custom_emoji('rocket')} Hits: <code>{result['hits']}</code>\n"
        )
    if len(results) > 10:
        text += f"<i>... এবং আরও {len(results) - 10}টি রেজাল্ট</i>\n"
    buttons = []
    for result in results[:5]:
        buttons.append([InlineKeyboardButton(f"📋 {result['range']}", callback_data=f"copy_range_{result['range']}")])
    buttons.append([InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

async def admin_traffic_control(update, context):
    uid = update.effective_user.id
    if not is_admin(uid):
        await update.message.reply_text("🚫 UNAUTHORIZED!", reply_markup=main_keyboard(uid))
        return
    stats, last_updated = get_traffic_stats()
    auto_mode = get_auto_range_mode()
    text = (
        f"{get_premium_custom_emoji('dashboard')} <b>ADMIN TRAFFIC CONTROL</b>\n"
        f"{format_premium_divider('primary')}\n"
        f"{get_premium_custom_emoji('rocket')} <b>Auto-Range Mode:</b> <code>{'ENABLED ✅' if auto_mode else 'DISABLED ❌'}</code>\n"
        f"{get_premium_custom_emoji('world')} <b>Total Services:</b> <code>{len(stats)}</code>\n"
        f"{get_premium_custom_emoji('time')} <b>Last Updated:</b> <code>{last_updated.strftime('%I:%M %p') if last_updated else 'N/A'}</code>\n"
        f"{format_premium_divider('success')}\n"
        f"<i>নিচের বাটন থেকে ট্রাফিক কন্ট্রোল করুন:</i>"
    )
    buttons = [
        [InlineKeyboardButton(f"{'🔴 DISABLE' if auto_mode else '🟢 ENABLE'} Auto-Range", callback_data="admin_toggle_auto_range")],
        [InlineKeyboardButton("📊 View Full Dashboard", callback_data="traffic_home"), InlineKeyboardButton("🔄 Refresh Stats", callback_data="admin_refresh_traffic")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_to_admin_panel")]
    ]
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

# ══════════════════════════════════════════════════════════════════════════════
# 🎯 WELCOME MESSAGE & DEFAULTS
# ══════════════════════════════════════════════════════════════════════════════
WELCOME_MESSAGE = """⚡️💎 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 💎⚡️
🌍 Premium Virtual Number Platform
📩 Instant OTP Delivery
🚀 Fast Verification Service
🔐 Secure & Anonymous Access
📲 Facebook • WhatsApp • Telegram • Instagram
✨ And More...
💎 Enjoy Premium Quality Service With
⚡️  ⚡️"""

DEFAULT_OTP_RATE = 0.20
DEFAULT_REFERRAL_PRICE = 0
DEFAULT_MIN_WITHDRAW = 50
DEFAULT_MAX_WITHDRAW = 10000
DEFAULT_PAYMENT_METHODS = {"BKASH": True, "NAGAD": True, "ROCKET": True, "BINANCE": True}
WITHDRAWAL_FEE_PERCENTAGE = 0
AUTO_REMOVE_MINUTES = 20

request_queue = asyncio.Queue()
MAX_WORKERS = 20
CHECK_INTERVAL = 2
CACHE_TTL = 30

primary_client = httpx.AsyncClient(
    timeout=httpx.Timeout(connect=10.0, read=15.0, write=10.0, pool=5.0),
    headers=PRIMARY_HEADERS,
    limits=httpx.Limits(max_connections=1000, max_keepalive_connections=200)
)
secondary_client = httpx.AsyncClient(
    timeout=httpx.Timeout(connect=10.0, read=15.0, write=10.0, pool=5.0),
    headers=SECONDARY_HEADERS,
    limits=httpx.Limits(max_connections=1000, max_keepalive_connections=200)
)

active_numbers = {}
admin_direct_numbers = {}
custom_services_cache = {}
last_range = {}
_services_cache = {"services": {}, "timestamp": 0}
_country_otp_timestamps = {}
HOT_THRESHOLD = 5
HOT_WINDOW = timedelta(minutes=30)

PREMIUM_EMOJIS = {
    "country": ["🌍", "🌎", "🌏", "🗺️", "📍"],
    "number": ["📞", "📱", "☎️", "📲", "🔢"],
    "otp": ["🔑", "🔐", "🔓", "🗝️", "✨"],
    "range": ["📶", "🚀", "⚡", "💫", "🌟"],
    "service": ["📱", "💎", "⭐", "🎯", "🏆"],
    "sms": ["📩", "💌", "✉️", "📨", "📧"],
    "balance": ["💰", "💵", "💎", "💸", "🪙"],
    "time": ["⏰", "⏳", "🔄", "📊", "📈"],
    "status": ["✅", "⏳", "🔄", "📊", "📈"]
}

def get_premium_emoji(category):
    emojis = PREMIUM_EMOJIS.get(category, ["✨"])
    return random.choice(emojis)

# ══════════════════════════════════════════════════════════════════════════════
# 🗺️ COUNTRY PREFIX MAP
# ══════════════════════════════════════════════════════════════════════════════
COUNTRY_PREFIX_MAP = {
    "2376": ("🇨🇲", "Cameroon"), "2250": ("🇨🇮", "Ivory Coast"),
    "2613": ("🇲🇬", "Madagascar"), "4077": ("🇷🇴", "Romania"),
    "237": ("🇨🇲", "Cameroon"), "225": ("🇨🇮", "Ivory Coast"),
    "261": ("🇲🇬", "Madagascar"), "20": ("🇪🇬", "Egypt"),
    "27": ("🇿🇦", "South Africa"), "234": ("🇳🇬", "Nigeria"),
    "254": ("🇰🇪", "Kenya"), "233": ("🇬🇭", "Ghana"),
    "212": ("🇲🇦", "Morocco"), "213": ("🇩🇿", "Algeria"),
    "216": ("🇹🇳", "Tunisia"), "218": ("🇱🇾", "Libya"),
    "249": ("🇸🇩", "Sudan"), "251": ("🇪🇹", "Ethiopia"),
    "252": ("🇸🇴", "Somalia"), "253": ("🇩🇯", "Djibouti"),
    "255": ("🇹🇿", "Tanzania"), "256": ("🇺🇬", "Uganda"),
    "257": ("🇧🇮", "Burundi"), "258": ("🇲🇿", "Mozambique"),
    "260": ("🇿🇲", "Zambia"), "263": ("🇿🇼", "Zimbabwe"),
    "264": ("🇳🇦", "Namibia"), "265": ("🇲🇼", "Malawi"),
    "44": ("🇬🇧", "United Kingdom"), "33": ("🇫🇷", "France"),
    "49": ("🇩🇪", "Germany"), "39": ("🇮🇹", "Italy"),
    "34": ("🇪🇸", "Spain"), "31": ("🇳🇱", "Netherlands"),
    "1": ("🇺🇸", "United States"), "7": ("🇷🇺", "Russia"),
    "91": ("🇮🇳", "India"), "92": ("🇵🇰", "Pakistan"),
    "880": ("🇧🇩", "Bangladesh"), "86": ("🇨🇳", "China"),
    "81": ("🇯🇵", "Japan"), "82": ("🇰🇷", "South Korea"),
    "84": ("🇻🇳", "Vietnam"), "66": ("🇹🇭", "Thailand"),
    "62": ("🇮🇩", "Indonesia"), "60": ("🇲🇾", "Malaysia"),
    "65": ("🇸🇬", "Singapore"), "63": ("🇵🇭", "Philippines"),
    "55": ("🇧🇷", "Brazil"), "52": ("🇲🇽", "Mexico"),
    "54": ("🇦🇷", "Argentina"), "57": ("🇨🇴", "Colombia"),
    "61": ("🇦🇺", "Australia"), "64": ("🇳🇿", "New Zealand"),
}

def get_country_prefix_from_number(number: str) -> str:
    clean = re.sub(r'\D', '', str(number))
    prefixes = sorted(COUNTRY_PREFIX_MAP.keys(), key=len, reverse=True)
    for p in prefixes:
        if clean.startswith(p):
            return p
    return ""

def get_country_by_prefix(prefix: str):
    if prefix in COUNTRY_PREFIX_MAP:
        return COUNTRY_PREFIX_MAP[prefix]
    sorted_prefixes = sorted(COUNTRY_PREFIX_MAP.keys(), key=len, reverse=True)
    for p in sorted_prefixes:
        if prefix.startswith(p):
            return COUNTRY_PREFIX_MAP[p]
    return ("🌍", "Unknown")

def get_country_info(number):
    number = str(number).strip()
    clean_num = re.sub(r'\D', '', number)
    sorted_prefixes = sorted(COUNTRY_PREFIX_MAP.keys(), key=len, reverse=True)
    for prefix in sorted_prefixes:
        if clean_num.startswith(prefix):
            return COUNTRY_PREFIX_MAP[prefix]
    return ("🌍", "Unknown")

# ══════════════════════════════════════════════════════════════════════════════
# 🛠️ HELPER FOR COUNTRY PREFIX (NEW - FIXES UNKNOWN COUNTRY)
# ══════════════════════════════════════════════════════════════════════════════
def get_number_country_prefix(num):
    """Fallback country prefix extraction for unknown numbers"""
    prefix = get_country_prefix_from_number(num)
    if not prefix:
        clean = re.sub(r'\D', '', num)
        # Fallback to first 3 digits or 1 digit to avoid "Unknown"
        prefix = clean[:3] if len(clean) >= 3 else (clean[:1] if clean else "OTHER")
    return prefix

def get_admin_numbers_by_country():
    admin_nums = load_admin_direct_numbers()
    country_map = {}
    for num, info in admin_nums.items():
        if info.get("used", False):
            continue
        country_prefix = get_number_country_prefix(num)
        
        if country_prefix not in country_map:
            flag, name = get_country_by_prefix(country_prefix)
            if name == "Unknown":
                name = f"Country +{country_prefix}"  # Show actual code instead of Unknown
            country_map[country_prefix] = {"flag": flag, "name": name, "numbers": []}
        country_map[country_prefix]["numbers"].append({"number": num, "info": info})
    return country_map

def update_country_otp_count(number: str):
    prefix = get_country_prefix_from_number(number)
    if not prefix:
        return
    now = datetime.now()
    if prefix not in _country_otp_timestamps:
        _country_otp_timestamps[prefix] = []
    ts_list = _country_otp_timestamps[prefix]
    ts_list.append(now)
    cutoff = now - HOT_WINDOW
    _country_otp_timestamps[prefix] = [t for t in ts_list if t > cutoff]

def is_country_hot(prefix: str) -> bool:
    if prefix not in _country_otp_timestamps:
        return False
    now = datetime.now()
    cutoff = now - HOT_WINDOW
    recent = [t for t in _country_otp_timestamps[prefix] if t > cutoff]
    _country_otp_timestamps[prefix] = recent
    return len(recent) >= HOT_THRESHOLD

# ══════════════════════════════════════════════════════════════════════════════
# 📞 ADMIN DIRECT NUMBERS (UPDATED - 20 MIN AUTO REMOVE)
# ══════════════════════════════════════════════════════════════════════════════
def load_admin_direct_numbers():
    if not os.path.exists(ADMIN_DIRECT_NUMBERS_FILE):
        with open(ADMIN_DIRECT_NUMBERS_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(ADMIN_DIRECT_NUMBERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_admin_direct_numbers(data):
    with open(ADMIN_DIRECT_NUMBERS_FILE, "w") as f:
        json.dump(data, f, indent=4)
    if db_mongo_connected and db_mongo is not None:
        try:
            db_mongo.admin_direct_numbers.update_one(
                {"_id": "all_numbers"},
                {"$set": {"data": data, "updated": datetime.now().isoformat()}},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Admin numbers sync error: {e}")

def add_admin_direct_number(number, added_by_admin_id, service="CUSTOM", range_info=""):
    global admin_direct_numbers
    admin_direct_numbers = load_admin_direct_numbers()
    clean_num = normalize_number(number)
    admin_direct_numbers[clean_num] = {
        "number": clean_num,
        "added_by": added_by_admin_id,
        "added_at": datetime.now().isoformat(),
        "used": False,
        "assigned_to": None,
        "service": service,
        "range": range_info,
        "otp_count": 0
    }
    save_admin_direct_numbers(admin_direct_numbers)
    return True

def add_bulk_admin_numbers(numbers_list, added_by_admin_id, service="CUSTOM"):
    global admin_direct_numbers
    admin_direct_numbers = load_admin_direct_numbers()
    added_count = 0
    for num in numbers_list:
        clean_num = normalize_number(num)
        if not clean_num:
            continue
        if clean_num not in admin_direct_numbers:
            admin_direct_numbers[clean_num] = {
                "number": clean_num,
                "added_by": added_by_admin_id,
                "added_at": datetime.now().isoformat(),
                "used": False,
                "assigned_to": None,
                "service": service,
                "range": "",
                "otp_count": 0
            }
            added_count += 1
    save_admin_direct_numbers(admin_direct_numbers)
    return added_count

def remove_admin_direct_number(number):
    global admin_direct_numbers
    admin_direct_numbers = load_admin_direct_numbers()
    clean_num = normalize_number(number)
    if clean_num in admin_direct_numbers:
        del admin_direct_numbers[clean_num]
        save_admin_direct_numbers(admin_direct_numbers)
        return True
    return False

def remove_all_admin_numbers():
    global admin_direct_numbers
    admin_direct_numbers = {}
    save_admin_direct_numbers(admin_direct_numbers)
    return True

def mark_admin_number_used(number, uid):
    global admin_direct_numbers
    admin_direct_numbers = load_admin_direct_numbers()
    clean_num = normalize_number(number)
    if clean_num in admin_direct_numbers:
        admin_direct_numbers[clean_num]["used"] = True
        admin_direct_numbers[clean_num]["assigned_to"] = uid
        save_admin_direct_numbers(admin_direct_numbers)
        return True
    return False

def increment_admin_number_otp(number):
    global admin_direct_numbers
    admin_direct_numbers = load_admin_direct_numbers()
    clean_num = normalize_number(number)
    if clean_num in admin_direct_numbers:
        admin_direct_numbers[clean_num]["otp_count"] = admin_direct_numbers[clean_num].get("otp_count", 0) + 1
        save_admin_direct_numbers(admin_direct_numbers)

def get_admin_number_info(number):
    admin_direct_numbers_local = load_admin_direct_numbers()
    clean_num = normalize_number(number)
    return admin_direct_numbers_local.get(clean_num)

def get_available_admin_numbers_count():
    admin_nums = load_admin_direct_numbers()
    return sum(1 for info in admin_nums.values() if not info.get("used", False))

def auto_remove_expired_numbers():
    global admin_direct_numbers
    admin_direct_numbers = load_admin_direct_numbers()
    now = datetime.now()
    to_remove = []
    for num, info in admin_direct_numbers.items():
        added_at = datetime.fromisoformat(info["added_at"])
        time_diff = (now - added_at).total_seconds() / 60
        if time_diff >= AUTO_REMOVE_MINUTES or info.get("used", False):
            to_remove.append(num)
    for num in to_remove:
        del admin_direct_numbers[num]
    if to_remove:
        save_admin_direct_numbers(admin_direct_numbers)
        print(f"🗑️ Auto-removed {len(to_remove)} expired/used numbers")
    return len(to_remove)

# ══════════════════════════════════════════════════════════════════════════════
# 🎯 CUSTOM SERVICES (UPDATED - WITH RANGES)
# ══════════════════════════════════════════════════════════════════════════════
def load_custom_services():
    if not os.path.exists(CUSTOM_SERVICES_FILE):
        with open(CUSTOM_SERVICES_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(CUSTOM_SERVICES_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_custom_services(data):
    with open(CUSTOM_SERVICES_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_custom_service(service_id, name, ranges):
    services = load_custom_services()
    services[service_id] = {
        "id": service_id,
        "name": name,
        "ranges": ranges,
        "created_at": datetime.now().isoformat(),
        "created_by": "admin"
    }
    save_custom_services(services)
    return True

def remove_custom_service(service_id):
    services = load_custom_services()
    if service_id in services:
        del services[service_id]
        save_custom_services(services)
        return True
    return False

def get_all_custom_services():
    return load_custom_services()

# ══════════════════════════════════════════════════════════════════════════════
# ⚙️ SYSTEM CONFIG
# ══════════════════════════════════════════════════════════════════════════════
def load_system_config():
    if not os.path.exists(SYSTEM_CONFIG_FILE):
        default_config = {
            "min_withdraw": DEFAULT_MIN_WITHDRAW,
            "max_withdraw": DEFAULT_MAX_WITHDRAW,
            "payment_methods": DEFAULT_PAYMENT_METHODS.copy(),
            "otp_rate": DEFAULT_OTP_RATE,
            "referral_price": DEFAULT_REFERRAL_PRICE
        }
        save_system_config(default_config)
        return default_config
    try:
        with open(SYSTEM_CONFIG_FILE, "r") as f:
            config = json.load(f)
        if "otp_rate" not in config:
            config["otp_rate"] = DEFAULT_OTP_RATE
        if "referral_price" not in config:
            config["referral_price"] = DEFAULT_REFERRAL_PRICE
        save_system_config(config)
        return config
    except:
        return {
            "min_withdraw": DEFAULT_MIN_WITHDRAW,
            "max_withdraw": DEFAULT_MAX_WITHDRAW,
            "payment_methods": DEFAULT_PAYMENT_METHODS.copy(),
            "otp_rate": DEFAULT_OTP_RATE,
            "referral_price": DEFAULT_REFERRAL_PRICE
        }

def save_system_config(config):
    with open(SYSTEM_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
    if db_mongo_connected and db_mongo is not None:
        try:
            db_mongo.system_config.update_one(
                {"_id": "main_config"},
                {"$set": {"config": config, "updated": datetime.now().isoformat()}},
                upsert=True
            )
        except Exception as e:
            logger.error(f"System config sync error: {e}")

def get_otp_rate():
    config = load_system_config()
    return config.get("otp_rate", DEFAULT_OTP_RATE)

def get_referral_price():
    config = load_system_config()
    return config.get("referral_price", DEFAULT_REFERRAL_PRICE)

def set_referral_price(price):
    config = load_system_config()
    config["referral_price"] = price
    save_system_config(config)
    return True

def get_enabled_payment_methods():
    config = load_system_config()
    return [name for name, enabled in config["payment_methods"].items() if enabled]

def toggle_payment_method(method_name):
    config = load_system_config()
    if method_name in config["payment_methods"]:
        config["payment_methods"][method_name] = not config["payment_methods"][method_name]
        save_system_config(config)
        return config["payment_methods"][method_name]
    return None

# ══════════════════════════════════════════════════════════════════════════════
# 💰 PER-USER OTP RATE
# ══════════════════════════════════════════════════════════════════════════════
def load_user_otp_rates():
    if not os.path.exists(USER_OTP_RATE_FILE):
        with open(USER_OTP_RATE_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(USER_OTP_RATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_user_otp_rates(data):
    with open(USER_OTP_RATE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user_otp_rate(user_id):
    rates = load_user_otp_rates()
    uid_str = str(user_id)
    if uid_str in rates:
        try:
            rate = float(rates[uid_str])
            if rate > 0:
                return rate
        except:
            pass
    return get_otp_rate()

def set_user_otp_rate(user_id, rate):
    rates = load_user_otp_rates()
    uid_str = str(user_id)
    if rate > 0:
        rates[uid_str] = rate
    else:
        if uid_str in rates:
            del rates[uid_str]
    save_user_otp_rates(rates)

# ══════════════════════════════════════════════════════════════════════════════
# 🗄️ DATABASE & STATS
# ══════════════════════════════════════════════════════════════════════════════
def load_referral_history():
    if not os.path.exists(REFERRAL_HISTORY_FILE):
        with open(REFERRAL_HISTORY_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(REFERRAL_HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_referral_history(data):
    with open(REFERRAL_HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_referral(referrer_id, referred_id):
    history = load_referral_history()
    ref_str = str(referrer_id)
    if ref_str not in history:
        history[ref_str] = {"referred_users": [], "total_earned": 0.0}
    if str(referred_id) not in [str(u) for u in history[ref_str]["referred_users"]]:
        referral_price = get_referral_price()
        history[ref_str]["referred_users"].append({
            "user_id": str(referred_id),
            "joined_at": datetime.now().isoformat(),
            "bonus_given": referral_price
        })
        save_referral_history(history)
        return True
    return False

def get_referral_stats(referrer_id):
    history = load_referral_history()
    ref_str = str(referrer_id)
    if ref_str not in history:
        return {"count": 0, "earned": 0.0, "users": []}
    return {
        "count": len(history[ref_str]["referred_users"]),
        "earned": history[ref_str].get("total_earned", 0.0),
        "users": history[ref_str]["referred_users"]
    }

def get_referrer_of(user_id):
    history = load_referral_history()
    for ref_id, data in history.items():
        for u in data.get("referred_users", []):
            if str(u.get("user_id")) == str(user_id):
                return int(ref_id)
    return None

# ══════════════════════════════════════════════════════════════════════════════
# 💳 PAYMENT HISTORY
# ══════════════════════════════════════════════════════════════════════════════
def load_payment_history():
    if not os.path.exists(PAYMENT_HISTORY_FILE):
        with open(PAYMENT_HISTORY_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(PAYMENT_HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_payment_history(data):
    with open(PAYMENT_HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def add_payment_record(uid, method, amount, number, payment_id, status="pending"):
    history = load_payment_history()
    uid_str = str(uid)
    if uid_str not in history:
        history[uid_str] = []
    history[uid_str].append({
        "payment_id": payment_id,
        "method": method,
        "amount": amount,
        "number": number,
        "status": status,
        "timestamp": datetime.now().isoformat()
    })
    save_payment_history(history)

def update_payment_status(payment_id, status):
    history = load_payment_history()
    for uid_str, records in history.items():
        for rec in records:
            if rec.get("payment_id") == payment_id:
                rec["status"] = status
    save_payment_history(history)
    return True

def get_user_payment_history(uid, limit=10):
    history = load_payment_history()
    records = history.get(str(uid), [])
    return sorted(records, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]

# ══════════════════════════════════════════════════════════════════════════════
# 🔑 USER OTP HISTORY
# ══════════════════════════════════════════════════════════════════════════════
def get_user_otp_history(uid, limit=15):
    logs = load_data(ACTIVITY_LOGS_FILE)
    if not isinstance(logs, list):
        return []
    user_logs = [
        log for log in logs
        if str(log.get('uid')) == str(uid) and log.get('action') == "OTP_RECEIVED"
    ]
    return sorted(user_logs, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]

# ══════════════════════════════════════════════════════════════════════════════
# 🔍 ADMIN USER SEARCH
# ══════════════════════════════════════════════════════════════════════════════
def search_users(query):
    user_db = load_data(USER_DATA_FILE)
    results = []
    query_lower = str(query).lower().strip()
    for uid, data in user_db.items():
        if query_lower in uid:
            results.append({"id": uid, "data": data, "match": "ID"})
            continue
        try:
            if float(query_lower) == data.get("balance", 0):
                results.append({"id": uid, "data": data, "match": "Balance"})
        except:
            pass
    return results[:20]

# ══════════════════════════════════════════════════════════════════════════════
# 💾 CORE DATABASE FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def load_data(filename=USER_DATA_FILE):
    if not os.path.exists(filename):
        default = [] if filename == ACTIVITY_LOGS_FILE else {}
        with open(filename, "w") as f:
            json.dump(default, f)
        return default
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return [] if filename == ACTIVITY_LOGS_FILE else {}

def save_data(data, filename=USER_DATA_FILE):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    if db_mongo_connected and db_mongo is not None:
        try:
            if filename == USER_DATA_FILE:
                db_mongo.users_data.update_one(
                    {"_id": "all_users"},
                    {"$set": {"data": data, "updated": datetime.now().isoformat()}},
                    upsert=True
                )
            elif filename == BANNED_USERS_FILE:
                db_mongo.banned_users.update_one(
                    {"_id": "banned_list"},
                    {"$set": {"list": data, "updated": datetime.now().isoformat()}},
                    upsert=True
                )
            elif filename == REQUIRED_CHANNELS_FILE:
                db_mongo.required_channels.update_one(
                    {"_id": "channels_list"},
                    {"$set": {"channels": data, "updated": datetime.now().isoformat()}},
                    upsert=True
                )
        except Exception as e:
            logger.error(f"Data sync error: {e}")

def get_user(uid):
    uid = str(uid)
    data = load_data()
    if uid not in data:
        data[uid] = {"user_id": uid, "balance": 0.0, "total_numbers": 0, "referral_count": 0, "verified": False}
        save_data(data)
    return data[uid]

async def update_db_balance(uid, amount):
    uid = str(uid)
    data = load_data()
    if uid in data:
        data[uid]["balance"] = round(data[uid].get("balance", 0.0) + amount, 2)
        save_data(data)
        return data[uid]["balance"]
    return 0.0

def user_exists(uid):
    return str(uid) in load_data(USER_DATA_FILE)

def get_all_users():
    return list(load_data(USER_DATA_FILE).keys())

# ══════════════════════════════════════════════════════════════════════════════
# 📊 USER STATS
# ══════════════════════════════════════════════════════════════════════════════
def load_stats():
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)

def add_number_taken(uid, count=1):
    uid = str(uid)
    stats = load_stats()
    if uid not in stats:
        stats[uid] = {"numbers_taken": [], "otps_received": []}
    now = datetime.now().isoformat()
    for _ in range(count):
        stats[uid]["numbers_taken"].append(now)
    save_stats(stats)

def add_otp_received(uid):
    uid = str(uid)
    stats = load_stats()
    if uid not in stats:
        stats[uid] = {"numbers_taken": [], "otps_received": []}
    stats[uid]["otps_received"].append(datetime.now().isoformat())
    save_stats(stats)

def get_user_stats(uid):
    uid = str(uid)
    stats = load_stats()
    user_stats = stats.get(uid, {"numbers_taken": [], "otps_received": []})
    now = datetime.now()
    today_midnight = datetime(now.year, now.month, now.day)
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    numbers_taken = user_stats.get("numbers_taken", [])
    otps_received = user_stats.get("otps_received", [])
    today_numbers = sum(1 for t in numbers_taken if datetime.fromisoformat(t) >= today_midnight)
    today_otps = sum(1 for t in otps_received if datetime.fromisoformat(t) >= today_midnight)
    last24h_numbers = sum(1 for t in numbers_taken if datetime.fromisoformat(t) > last_24h)
    last24h_otps = sum(1 for t in otps_received if datetime.fromisoformat(t) > last_24h)
    last7d_numbers = sum(1 for t in numbers_taken if datetime.fromisoformat(t) > last_7d)
    last7d_otps = sum(1 for t in otps_received if datetime.fromisoformat(t) > last_7d)
    return {
        "total_numbers": len(numbers_taken), "total_otps": len(otps_received),
        "today_numbers": today_numbers, "today_otps": today_otps,
        "last24h_numbers": last24h_numbers, "last24h_otps": last24h_otps,
        "last7d_numbers": last7d_numbers, "last7d_otps": last7d_otps
    }

def get_global_system_stats():
    stats = load_stats()
    now = datetime.now()
    today_midnight = datetime(now.year, now.month, now.day)
    last_7d = now - timedelta(days=7)
    total_n = total_o = today_n = today_o = seven_n = seven_o = 0
    for uid in stats:
        u = stats[uid]
        n_list = u.get("numbers_taken", [])
        o_list = u.get("otps_received", [])
        total_n += len(n_list)
        total_o += len(o_list)
        for t in n_list:
            dt = datetime.fromisoformat(t)
            if dt >= today_midnight: today_n += 1
            if dt >= last_7d: seven_n += 1
        for t in o_list:
            dt = datetime.fromisoformat(t)
            if dt >= today_midnight: today_o += 1
            if dt >= last_7d: seven_o += 1
    return today_n, today_o, seven_n, seven_o, total_n, total_o

def log_global_activity(uid, action, details):
    if not os.path.exists(ACTIVITY_LOGS_FILE):
        with open(ACTIVITY_LOGS_FILE, "w") as f:
            json.dump([], f)
    try:
        with open(ACTIVITY_LOGS_FILE, "r") as f:
            logs = json.load(f)
    except:
        logs = []
    if not isinstance(logs, list):
        logs = []
    now = datetime.now()
    logs.append({
        "uid": str(uid), "action": action, "details": details,
        "timestamp": now.isoformat(), "date": now.strftime("%d/%m/%Y"), "time": now.strftime("%H:%M:%S")
    })
    with open(ACTIVITY_LOGS_FILE, "w") as f:
        json.dump(logs, f, indent=4)

# ══════════════════════════════════════════════════════════════════════════════
# 🚫 BANNED USERS
# ══════════════════════════════════════════════════════════════════════════════
def load_banned_users():
    if not os.path.exists(BANNED_USERS_FILE):
        with open(BANNED_USERS_FILE, "w") as f:
            json.dump([], f)
        return []
    try:
        with open(BANNED_USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_banned_users(banned_list):
    with open(BANNED_USERS_FILE, "w") as f:
        json.dump(banned_list, f, indent=4)
    if db_mongo_connected and db_mongo is not None:
        try:
            db_mongo.banned_users.update_one(
                {"_id": "banned_list"},
                {"$set": {"list": banned_list, "updated": datetime.now().isoformat()}},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Banned users sync error: {e}")

def is_user_banned(uid):
    return str(uid) in load_banned_users()

def ban_user(uid):
    banned_list = load_banned_users()
    uid_str = str(uid)
    if uid_str not in banned_list:
        banned_list.append(uid_str)
        save_banned_users(banned_list)
        return True
    return False

def unban_user(uid):
    banned_list = load_banned_users()
    uid_str = str(uid)
    if uid_str in banned_list:
        banned_list.remove(uid_str)
        save_banned_users(banned_list)
        return True
    return False

# ══════════════════════════════════════════════════════════════════════════════
# 🔗 REQUIRED CHANNELS
# ══════════════════════════════════════════════════════════════════════════════
STYLES = ["primary", "success", "danger"]

def load_required_channels():
    if not os.path.exists(REQUIRED_CHANNELS_FILE):
        with open(REQUIRED_CHANNELS_FILE, "w") as f:
            json.dump([], f)
        return []
    try:
        with open(REQUIRED_CHANNELS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_required_channels(data):
    with open(REQUIRED_CHANNELS_FILE, "w") as f:
        json.dump(data, f, indent=4)
    if db_mongo_connected and db_mongo is not None:
        try:
            db_mongo.required_channels.update_one(
                {"_id": "channels_list"},
                {"$set": {"channels": data, "updated": datetime.now().isoformat()}},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Required channels sync error: {e}")

def get_all_required_channels():
    return load_required_channels()

def add_required_channel(link, label=None, chat_id=None):
    channels = load_required_channels()
    for ch in channels:
        if ch.get("link") == link:
            return False, "এই লিংক ইতিমধ্যে আছে।"
    if not label:
        label = link.replace("https://t.me/", "@").replace("@", "@")
    if label.startswith("+"):
        label = "Channel " + label
    else:
        label = "@" + label
    style_index = len(channels) % len(STYLES)
    entry = {"link": link, "label": label, "style": STYLES[style_index]}
    if chat_id:
        entry["chat_id"] = chat_id
    else:
        username_match = re.search(r'(?:https?://)?(?:www\.)?t\.me/([a-zA-Z0-9_]+)', link)
        if username_match:
            entry["username"] = username_match.group(1)
        else:
            return False, "লিংক থেকে চ্যাট আইডি বের করা যায়নি।"
    channels.append(entry)
    save_required_channels(channels)
    return True, "সফলভাবে যোগ করা হয়েছে।"

def remove_required_channel(link_or_label):
    channels = load_required_channels()
    new_channels = [ch for ch in channels if ch.get("link") != link_or_label and ch.get("label") != link_or_label]
    if len(new_channels) < len(channels):
        save_required_channels(new_channels)
        return True, "সরানো হয়েছে।"
    return False, "কোনো ম্যাচ পাওয়া যায়নি।"

# ══════════════════════════════════════════════════════════════════════════════
# 🛠️ HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def is_admin(user_id):
    return user_id in ADMINS

def format_balance(balance):
    return f"{balance:.2f}"

def extract_otp(text):
    if not text or text == "No Content":
        return "N/A"
    spaced_otp = re.search(r'\b(\d{3}\s\d{3})\b', text)
    if spaced_otp:
        return spaced_otp.group(1).replace(" ", "")
    match = re.search(r'\b(\d{4,8})\b', text)
    return match.group(1) if match else "N/A"

def normalize_number(num):
    return re.sub(r'\D', '', str(num))

def mask_number(num):
    if len(num) > 6:
        return f"{num[:4]}****{num[-6:]}"
    return num

def is_valid_bangladesh_number(number):
    number = re.sub(r'\D', '', str(number))
    return len(number) == 11 and number.startswith('01')

def is_range_request(param):
    return 'X' in param.upper() or param.replace('X', '').replace('x', '').isdigit()

def is_referral_request(param):
    return param.isdigit()

def detect_service(full_sms):
    if not full_sms:
        return "SMS SERVICE"
    sms_lower = full_sms.lower()
    service_keywords = {
        "facebook": "FACEBOOK", "fb": "FACEBOOK", "instagram": "INSTAGRAM", "insta": "INSTAGRAM",
        "tiktok": "TIKTOK", "twitter": "TWITTER", "x.com": "TWITTER", "snapchat": "SNAPCHAT",
        "snap": "SNAPCHAT", "whatsapp": "WHATSAPP", "telegram": "TELEGRAM", "discord": "DISCORD",
        "messenger": "MESSENGER", "linkedin": "LINKEDIN", "google": "GOOGLE", "gmail": "GOOGLE",
        "amazon": "AMAZON", "microsoft": "MICROSOFT", "outlook": "MICROSOFT", "yahoo": "YAHOO",
        "paypal": "PAYPAL", "binance": "BINANCE", "coinbase": "COINBASE", "spotify": "SPOTIFY",
        "netflix": "NETFLIX", "uber": "UBER", "apple": "APPLE", "icloud": "APPLE",
        "bkash": "BKASH", "nagad": "NAGAD", "stripe": "STRIPE", "line": "LINE",
        "wechat": "WECHAT", "viber": "VIBER", "signal": "SIGNAL", "pubg": "PUBG",
        "free fire": "FREE FIRE", "imo": "IMO"
    }
    for keyword, service_name in sorted(service_keywords.items(), key=lambda x: len(x[0]), reverse=True):
        if keyword in sms_lower:
            return service_name
    return "SMS SERVICE"

# ══════════════════════════════════════════════════════════════════════════════
# 🎹 KEYBOARDS
# ══════════════════════════════════════════════════════════════════════════════
def main_keyboard(user_id):
    keyboard = [
        [KeyboardButton(text="📞 GET NUMBER"), KeyboardButton(text="🌐 RANGE")],
        [KeyboardButton(text="📊 TRAFFIC"), KeyboardButton(text="💰 BALANCE")],
        [KeyboardButton(text="⚡ 2FA"), KeyboardButton(text="📜 HISTORY")],
        [KeyboardButton(text="👤 PROFILE"), KeyboardButton(text="🎁 REFER")],
        [KeyboardButton(text="💬 SUPPORT")]
    ]
    if is_admin(user_id):
        keyboard.append([KeyboardButton(text="⚙️ ADMIN PANEL ⚙️")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def cancel_keyboard():
    return ReplyKeyboardMarkup([[KeyboardButton("❌ CANCEL")]], resize_keyboard=True)

def admin_main_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("👥 USERS"), KeyboardButton("⚙️ CONFIG")],
        [KeyboardButton("🔗 CHANNELS"), KeyboardButton("📞 NUMBERS")],
        [KeyboardButton("🎯 SERVICES"), KeyboardButton("💸 WITHDRAW")],
        [KeyboardButton("📊 TRAFFIC CONTROL"), KeyboardButton("📊 ANALYTICS")],
        [KeyboardButton("🔍 SEARCH USER"), KeyboardButton("🔙 BACK TO MAIN")]
    ], resize_keyboard=True)

def user_management_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📢 BROADCAST"), KeyboardButton("🆔 ALL IDs")],
        [KeyboardButton("📜 BAN LIST"), KeyboardButton("💰 BALANCES")],
        [KeyboardButton("👥 USER LIST"), KeyboardButton("🔍 SEARCH")],
        [KeyboardButton("🔙 BACK")]
    ], resize_keyboard=True)

def system_config_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📈 STATUS"), KeyboardButton("👤 USER CHECK")],
        [KeyboardButton("⛔ BAN"), KeyboardButton("🔓 UNBAN")],
        [KeyboardButton("➖ REMOVE"), KeyboardButton("➕ ADD")],
        [KeyboardButton("⚙️ MIN WITHDRAW"), KeyboardButton("💲 OTP PRICE")],
        [KeyboardButton("💳 PAYMENTS"), KeyboardButton("🎁 REFER PRICE")],
        [KeyboardButton("🔙 BACK")]
    ], resize_keyboard=True)

def required_channels_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("➕ ADD"), KeyboardButton("❌ REMOVE")],
        [KeyboardButton("📋 LIST"), KeyboardButton("🔙 BACK")]
    ], resize_keyboard=True)

def add_numbers_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("➕ ADD BULK"), KeyboardButton("📋 VIEW")],
        [KeyboardButton("🗑️ REMOVE ALL"), KeyboardButton("🔙 BACK")]
    ], resize_keyboard=True)

def custom_services_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("➕ ADD"), KeyboardButton("📋 VIEW")],
        [KeyboardButton("❌ REMOVE"), KeyboardButton("🔙 BACK")]
    ], resize_keyboard=True)

def withdraw_method_keyboard():
    enabled_methods = get_enabled_payment_methods()
    if not enabled_methods:
        enabled_methods = ["BKASH", "NAGAD", "ROCKET", "BINANCE"]
    buttons = []
    for method in enabled_methods:
        if method == "BKASH": buttons.append([KeyboardButton("📱 BKASH")])
        elif method == "NAGAD": buttons.append([KeyboardButton("💵 NAGAD")])
        elif method == "ROCKET": buttons.append([KeyboardButton("🚀 ROCKET")])
        elif method == "BINANCE": buttons.append([KeyboardButton("🏦 BINANCE")])
    buttons.append([KeyboardButton("❌ CANCEL")])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def history_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑 OTP History", callback_data="history_otp"),
         InlineKeyboardButton("💸 Payment History", callback_data="history_payment")],
        [InlineKeyboardButton("🎁 Referral Stats", callback_data="history_referral")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]
    ])

# ══════════════════════════════════════════════════════════════════════════════
# 🌐 API CALLS
# ══════════════════════════════════════════════════════════════════════════════
async def fetch_services_from_secondary():
    try:
        r = await secondary_client.get(f"{SECONDARY_BASE_URL}/liveaccess")
        data = r.json()
        if data.get("meta", {}).get("code") == 200:
            services_data = data.get("data", {}).get("services", [])
            services = {}
            for svc in services_data:
                sid = svc.get("sid", "").lower()
                ranges = svc.get("ranges", [])
                if sid and ranges:
                    services[sid] = ranges
            if "instagram" not in services and "facebook" in services: services["instagram"] = services["facebook"]
            if "whatsapp" not in services and "facebook" in services: services["whatsapp"] = services["facebook"]
            if "telegram" not in services and "facebook" in services: services["telegram"] = services["facebook"]
            return services
        return {}
    except Exception as e:
        print(f"[secondary] fetch error: {e}")
        return {}

async def fetch_services_cached():
    global _services_cache
    now = datetime.now().timestamp()
    if _services_cache["services"] and (now - _services_cache["timestamp"]) < CACHE_TTL:
        return _services_cache["services"]
    merged_services = await fetch_services_from_secondary()
    custom_svcs = get_all_custom_services()
    for svc_id, svc_info in custom_svcs.items():
        safe_key = f"custom_{svc_id}"
        merged_services[safe_key] = {
            "ranges": svc_info.get("ranges", []),
            "display_name": f"{svc_info['name']}",
            "platform": "custom",
            "is_custom": True
        }
    if merged_services:
        _services_cache["services"] = merged_services
        _services_cache["timestamp"] = now
    return merged_services

async def get_number_from_api(rid: str):
    try:
        if not rid.endswith('XXX'):
            rid = rid + 'XXX'
        payload = {"range": str(rid)}
        r = await primary_client.post(f"{PRIMARY_BASE_URL}/publicapi/getnum", json=payload)
        result = r.json()
        if result.get("meta", {}).get("code") == 0:
            rows = result.get("data", {}).get("rows", [])
            if rows:
                return rows[0].get("number"), rows[0].get("country")
        return None, None
    except Exception as e:
        print(f"get_number error: {e}")
        return None, None

async def fetch_otp_from_api():
    try:
        r = await primary_client.get(f"{PRIMARY_BASE_URL}/publicapi/getupdate")
        result = r.json()
        if result.get("meta", {}).get("code") == 0:
            rows = result.get("data", {}).get("rows", [])
            return {"otps": [{"number": row.get("number", ""), "message": row.get("message", "No SMS Content"), "time": str(row.get("at_ms", ""))} for row in rows]}
        return {"otps": []}
    except Exception as e:
        print(f"fetch_otp error: {e}")
        return {"otps": []}

# ══════════════════════════════════════════════════════════════════════════════
# 🔐 2FA SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
def generate_2fa_code(secret_key):
    try:
        clean_secret = secret_key.replace(" ", "").strip()
        totp = pyotp.TOTP(clean_secret)
        return totp.now(), clean_secret
    except:
        return None, None

async def get_2fa_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return
    if not await check_force_join(uid, message=update.message, context=context):
        return
    context.user_data["mode"] = "get_2fa"
    await update.message.reply_text(
        f"{get_premium_custom_emoji('otp')} <b>GET 2FA CODE</b> {get_premium_custom_emoji('otp')}\n"
        f"<blockquote>🔑 ENTER YOUR 2FA SECRET KEY:</blockquote>",
        parse_mode="HTML"
    )

async def process_2fa_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    secret_key = update.message.text.strip()
    context.user_data["mode"] = None
    otp_code, clean_key = generate_2fa_code(secret_key)
    if otp_code is None:
        await update.message.reply_text(
            f"{get_premium_custom_emoji('error')} <b>INVALID 2FA SECRET KEY</b>\n"
            f"⚠️ Please send a valid base32 key.",
            parse_mode="HTML", reply_markup=main_keyboard(uid)
        )
        return
    now = datetime.now()
    final_msg = (f"{get_premium_custom_emoji('done')} <b>2FA CODE GENERATED!</b>\n"
                 f"<blockquote>🔑 KEY: <code>{clean_key}</code></blockquote>\n"
                 f"<blockquote>🔢 CODE: <code>{otp_code}</code></blockquote>\n"
                 f"<blockquote>⏳ EXPIRES IN: 30 SECONDS</blockquote>\n"
                 f"📅 {now.strftime('%d %B, %Y')} | {now.strftime('%I:%M %p')}")
    await update.message.reply_text(final_msg, parse_mode="HTML")

# ══════════════════════════════════════════════════════════════════════════════
# 📱 SERVICE SELECTION (UPDATED - WITH 📌 PIN FOR CUSTOM SERVICES)
# ══════════════════════════════════════════════════════════════════════════════
def _build_services_keyboard(services):
    buttons = []
    emoji_map = {"whatsapp": "💚", "facebook": "📘", "discord": "🎮", "telegram": "✈️", "instagram": "📸", "twitter": "🐦", "tiktok": "🎵", "snapchat": "👻", "google": "🔍", "gmail": "📧", "binance": "💰", "paypal": "💳", "amazon": "🛒", "netflix": "🎬", "spotify": "🎧", "uber": "🚗", "apple": "🍎", "microsoft": "🪟"}
    
    # 🎁 SPECIAL NUMBERS BUTTON (TOP)
    available_count = get_available_admin_numbers_count()
    if available_count > 0:
        buttons.append([InlineKeyboardButton(f"🎁 SPECIAL NUMBERS ({available_count} available)", callback_data="special_numbers")])
    
    # 📌 CUSTOM SERVICES (SEPARATE SECTION)
    custom_services_buttons = []
    regular_services_buttons = []
    for i, (svc_key, svc_data) in enumerate(services.items()):
        is_custom = svc_key.startswith("custom_")
        if is_custom:
            display_name = svc_data.get("display_name", "Custom")
            emoji = "📌"
            custom_services_buttons.append((display_name, emoji, svc_key))
        else:
            display_name = svc_key
            emoji = emoji_map.get(svc_key.lower(), "📡")
            regular_services_buttons.append((display_name, emoji, svc_key))
    
    # Add custom services first with 📌 pin (with section header)
    if custom_services_buttons:
        buttons.append([InlineKeyboardButton("📌 CUSTOM SERVICES (Admin Added)", callback_data="noop")])
        for display_name, emoji, svc_key in custom_services_buttons:
            callback_data = f"svc_{svc_key}"[:64]
            buttons.append([InlineKeyboardButton(f"{emoji} {display_name.capitalize()}", callback_data=callback_data)])
        buttons.append([InlineKeyboardButton("━━━━━━━━━━━━━━━━━━━━━━", callback_data="noop")])
    
    # Add regular services in rows of 2
    row = []
    for display_name, emoji, svc_key in regular_services_buttons:
        callback_data = f"svc_{svc_key}"[:64]
        row.append(InlineKeyboardButton(f"{emoji} {display_name.capitalize()}", callback_data=callback_data))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton("⚙️ CUSTOM RANGE", callback_data="custom_range")])
    buttons.append([InlineKeyboardButton("🔙 BACK TO MAIN", callback_data="back_to_main")])
    return InlineKeyboardMarkup(buttons)

def _build_countries_keyboard(ranges, service):
    country_map = {}
    for r in ranges:
        prefix = re.sub(r'[^0-9]', '', r)
        if not prefix: continue
        country_prefix = get_country_prefix_from_number(prefix)
        if not country_prefix: continue
        if country_prefix not in country_map:
            flag, name = get_country_by_prefix(country_prefix)
            country_map[country_prefix] = {"flag": flag, "name": name, "rid": prefix, "hot": is_country_hot(country_prefix)}
    if not country_map:
        return InlineKeyboardMarkup([[InlineKeyboardButton("❌ কোন দেশ উপলব্ধ নেই", callback_data="back_services")]])
    hot_countries = [c for c in country_map.values() if c["hot"]]
    non_hot_countries = [c for c in country_map.values() if not c["hot"]]
    countries = hot_countries + non_hot_countries
    btns = []
    for info in countries:
        label = f"{info['flag']} {info['name']}" + (" 🔥" if info["hot"] else "")
        btns.append(InlineKeyboardButton(label, callback_data=f"country_{info['rid']}_{service}"))
    rows = [btns[j:j+2] for j in range(0, len(btns), 2)]
    rows.append([InlineKeyboardButton("◀️ BACK", callback_data="back_services")])
    return InlineKeyboardMarkup(rows)

def _build_ranges_keyboard(ranges, country_prefix, service):
    filtered_ranges = [r for r in ranges if r.startswith(country_prefix)]
    if not filtered_ranges:
        return InlineKeyboardMarkup([[InlineKeyboardButton("❌ কোন রেঞ্জ নেই", callback_data="back_services")]])
    btns = []
    for r in filtered_ranges:
        clean_r = re.sub(r'[^0-9Xx]', '', r)
        emoji = get_premium_emoji("range")
        label = f"{emoji} {clean_r}"
        btns.append(InlineKeyboardButton(label, callback_data=f"range_{clean_r}_{service}"))
    rows = [btns[j:j+2] for j in range(0, len(btns), 2)]
    rows.append([InlineKeyboardButton("◀️ BACK", callback_data=f"svc_{service}")])
    return InlineKeyboardMarkup(rows)

def _build_special_numbers_country_keyboard():
    country_map = get_admin_numbers_by_country()
    if not country_map:
        return InlineKeyboardMarkup([[InlineKeyboardButton("❌ কোনো স্পেশাল নাম্বার নেই", callback_data="back_services")]])
    btns = []
    for prefix, data in sorted(country_map.items(), key=lambda x: len(x[1]["numbers"]), reverse=True):
        flag = data["flag"]
        name = data["name"]
        count = len(data["numbers"])
        label = f"{flag} {name} ({count})"
        btns.append(InlineKeyboardButton(label, callback_data=f"special_country_{prefix}"))
    rows = [btns[j:j+2] for j in range(0, len(btns), 2)]
    rows.append([InlineKeyboardButton("◀️ BACK", callback_data="back_services")])
    return InlineKeyboardMarkup(rows)

async def show_app_selection(update, context):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return
    if not await check_force_join(uid, message=update.message, context=context):
        return
    services = await fetch_services_cached()
    if not services:
        await update.message.reply_text("❌ সার্ভিস লোড করা যাচ্ছে না!", reply_markup=main_keyboard(uid))
        return
    context.user_data["la_services"] = services
    await update.message.reply_text(
        f"{get_premium_custom_emoji('phone')} <b>SELECT YOUR SERVICE</b> {get_premium_custom_emoji('phone')}\n"
        f"<blockquote>📱 নিচ থেকে একটি <b>Service</b> সিলেক্ট করুন:\n"
        f"📌 = Custom Services (Admin Added)</blockquote>",
        parse_mode="HTML",
        reply_markup=_build_services_keyboard(services)
    )

# ══════════════════════════════════════════════════════════════════════════════
# 🎁 SPECIAL NUMBERS (UPDATED - COUNTRY → DIRECT ALLOCATE → NEW NUMBER)
# ══════════════════════════════════════════════════════════════════════════════
async def assign_special_number(query, context, uid):
    available_count = get_available_admin_numbers_count()
    if available_count == 0:
        text = (
            f"{get_premium_custom_emoji('error')} <b>স্টক খালি!</b>\n"
            f"<blockquote>বর্তমানে কোনো স্পেশাল নাম্বার available নেই।\n"
            f"অ্যাডমিনের সাথে যোগাযোগ করুন।</blockquote>"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh Stock", callback_data="special_refresh_stock")],
            [InlineKeyboardButton("🔙 BACK", callback_data="back_services")]
        ])
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
        return
    keyboard = _build_special_numbers_country_keyboard()
    text = (
        f"{get_premium_custom_emoji('gem')} <b>SPECIAL NUMBERS</b>\n"
        f"{format_premium_divider('primary')}\n"
        f"<blockquote>🎁 মোট Available: <b>{available_count}</b> টি নাম্বার\n"
        f"⏰ প্রতিটি নাম্বারের সময়সীমা: <b>{AUTO_REMOVE_MINUTES} মিনিট</b></blockquote>\n"
        f"✨ নিচের দেশ থেকে নাম্বার সিলেক্ট করুন:"
    )
    await query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)

# ══════════════════════════════════════════════════════════════════════════════
# 🎯 SPECIAL NUMBER ALLOCATION BY COUNTRY (NEW SYSTEM - FIXES ALL ISSUES)
# ══════════════════════════════════════════════════════════════════════════════
async def allocate_one_special_number_by_country(query, context, uid, country_prefix):
    admin_nums = load_admin_direct_numbers()
    available_nums = []
    
    # Find available numbers for this specific country
    for num, info in admin_nums.items():
        if info.get("used", False):
            continue
        num_prefix = get_number_country_prefix(num)
        if num_prefix == country_prefix:
            available_nums.append(num)
    
    if not available_nums:
        await query.message.edit_text(
            f"{get_premium_custom_emoji('error')} <b>স্টক খালি!</b>\n"
            f"<blockquote>⚠️ এই দেশের কোনো নাম্বার বর্তমানে available নেই।\n"
            f"অ্যাডমিনের সাথে যোগাযোগ করুন বা অন্য দেশ সিলেক্ট করুন।</blockquote>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK TO COUNTRIES", callback_data="special_numbers")],
                [InlineKeyboardButton("🔙 MAIN MENU", callback_data="back_services")]
            ])
        )
        return
    
    # Pick the first available number
    selected_num = available_nums[0]
    info = admin_nums[selected_num]
    
    # Mark as used and assign
    info["used"] = True
    info["assigned_to"] = uid
    info["assigned_at"] = datetime.now().isoformat()
    save_admin_direct_numbers(admin_nums)
    
    add_number_taken(uid, 1)
    country_flag, country_name = get_country_info(selected_num)
    if country_name == "Unknown":
        country_name = f"Country +{country_prefix}"
    
    service_name = info.get("service", "CUSTOM")
    
    text = (
        f"{get_premium_custom_emoji('gem')} <b>SPECIAL NUMBER ASSIGNED</b>\n"
        f"{format_premium_divider('success')}\n"
        f"<blockquote>{get_premium_custom_emoji('country')} COUNTRY: <code>{country_flag} {country_name}</code></blockquote>\n"
        f"<blockquote>{get_premium_custom_emoji('service')} SERVICE: <code>{service_name.upper()}</code></blockquote>\n"
        f"<blockquote>{get_premium_custom_emoji('number')} NUMBER: <code>{selected_num}</code></blockquote>\n"
        f"<b>{get_premium_custom_emoji('time')} SMS STATUS: ⏳ WAITING...</b>\n"
        f"<blockquote>⏰ Auto-remove: {AUTO_REMOVE_MINUTES} মিনিট পর</blockquote>"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🍏 Copy Number", callback_data=f"copy_number_{selected_num}"),
         InlineKeyboardButton(f"🔄 NEW NUMBER", callback_data=f"special_new_num_{country_prefix}")],
        [InlineKeyboardButton("📢 OTP GROUP", url=OTP_GROUP_URL)],
        [InlineKeyboardButton("🔙 BACK TO COUNTRIES", callback_data="special_numbers")]
    ])
    
    await query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)

async def assign_specific_special_number(query, context, uid, number):
    admin_nums = load_admin_direct_numbers()
    clean_num = normalize_number(number)
    if clean_num not in admin_nums or admin_nums[clean_num].get("used", False):
        await query.answer("❌ এই নাম্বার আর available নেই!", show_alert=True)
        return
    info = admin_nums[clean_num]
    added_at = datetime.fromisoformat(info["added_at"])
    time_diff = (datetime.now() - added_at).total_seconds() / 60
    if time_diff >= AUTO_REMOVE_MINUTES:
        await query.answer("⏰ এই নাম্বারের সময় শেষ হয়ে গেছে!", show_alert=True)
        return
    info["used"] = True
    info["assigned_to"] = uid
    info["assigned_at"] = datetime.now().isoformat()
    save_admin_direct_numbers(admin_nums)
    add_number_taken(uid, 1)
    country_flag, country_name = get_country_info(clean_num)
    service_name = info.get("service", "CUSTOM")
    text = (
        f"{get_premium_custom_emoji('gem')} <b>SPECIAL NUMBER ASSIGNED</b>\n"
        f"{format_premium_divider('success')}\n"
        f"<blockquote>{get_premium_emoji('country')} COUNTRY: <code>{country_flag} {country_name}</code></blockquote>\n"
        f"<blockquote>{get_premium_emoji('service')} SERVICE: <code>{service_name.upper()}</code></blockquote>\n"
        f"<blockquote>{get_premium_emoji('number')} NUMBER: <code>{clean_num}</code></blockquote>\n"
        f"<b>{get_premium_custom_emoji('time')} SMS STATUS: ⏳ WAITING...</b>\n"
        f"<blockquote>⏰ Auto-remove: {AUTO_REMOVE_MINUTES} মিনিট পর</blockquote>"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🍏 Copy Number", callback_data=f"copy_number_{clean_num}")],
        [InlineKeyboardButton("📢 OTP GROUP", url=OTP_GROUP_URL)],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_services")]
    ])
    await query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)

# ══════════════════════════════════════════════════════════════════════════════
# 🔄 AUTO OTP MONITOR
# ══════════════════════════════════════════════════════════════════════════════
async def monitor_loop(app):
    sent_otps = set()
    last_auto_remove_check = datetime.now()
    while True:
        try:
            now = datetime.now()
            if (now - last_auto_remove_check).total_seconds() >= 60:
                removed_count = auto_remove_expired_numbers()
                last_auto_remove_check = now
            otp_data = await fetch_otp_from_api()
            otps = otp_data.get("otps", [])
            paid_data = load_data(PAID_SMS_FILE)
            paid_keys_set = set(paid_data.keys())
            for otp in otps:
                number = otp.get("number")
                if not number: continue
                full_sms = otp.get("message", "No SMS Content")
                otp_time = otp.get("time", "")
                otp_code = extract_otp(full_sms)
                key = f"{normalize_number(number)}_{otp_time}"
                if key in sent_otps: continue
                num = normalize_number(number)
                sms_key = f"{num}_{full_sms[:50]}"
                is_in_active = num in active_numbers
                admin_info = get_admin_number_info(num)
                is_in_admin = admin_info is not None
                if (is_in_active or is_in_admin) and sms_key not in paid_keys_set:
                    sent_otps.add(key)
                    if is_in_active:
                        details = active_numbers[num]
                        uid = details["uid"]
                        service_name = detect_service(full_sms)
                        range_info = details.get("range", "")
                    else:
                        uid = admin_info.get("assigned_to")
                        service_name = admin_info.get("service", detect_service(full_sms))
                        range_info = admin_info.get("range", "")
                    mark_admin_number_used(num, uid)
                    increment_admin_number_otp(num)
                    is_free_service = service_name in ("TELEGRAM", "WHATSAPP")
                    if uid:
                        if not is_free_service:
                            user_rate = get_user_otp_rate(uid)
                            await update_db_balance(uid, user_rate)
                            add_otp_received(uid)
                            log_global_activity(uid, "OTP_RECEIVED", {"number": num, "otp": otp_code, "sms": full_sms})
                            update_country_otp_count(num)
                        else:
                            log_global_activity(uid, "OTP_RECEIVED_FREE", {"number": num, "otp": otp_code, "service": service_name})
                    if not range_info:
                        range_info = (num[:-3] + 'XXX') if len(num) > 3 else (num + 'XXX')
                    country_prefix = get_country_prefix_from_number(num)
                    if country_prefix:
                        update_traffic_stats(service_name, country_prefix, range_info, hits=1)
                    paid_keys_set.add(sms_key)
                    paid_data[sms_key] = {"uid": uid, "otp": otp_code}
                    country_flag, country_name = get_country_info(num)
                    clean_num = num.replace('+', '').strip()
                    full_number = f"+{clean_num}"
                    masked_number = f"+{mask_number(clean_num)}"
                    safe_full_sms = html.escape(str(full_sms))
                    safe_otp_code = html.escape(str(otp_code))
                    balance_msg = "⚠️ এই OTP‑তে কোনো টাকা যোগ করা হবে না (Telegram/WhatsApp)" if is_free_service else f"💵 ADD BALANCE FOR {get_user_otp_rate(uid):.2f} BDT" if uid else "💵 Admin Number"
                    user_msg = (f"{get_premium_emoji('status')} <b>OTP RECEIVE SUCCESSFUL</b> {get_premium_emoji('status')}\n"
                                f"<blockquote>{get_premium_emoji('range')} RANGE: <code>{range_info}</code></blockquote>\n"
                                f"<blockquote>{get_premium_emoji('country')} COUNTRY: <code>{country_flag} {country_name}</code></blockquote>\n"
                                f"<blockquote>{get_premium_emoji('service')} SERVICE: <code>{service_name}</code></blockquote>\n"
                                f"<blockquote>{get_premium_emoji('number')} NUMBER: <code>{full_number}</code></blockquote>\n"
                                f"<blockquote>{get_premium_emoji('otp')} OTP: <code>{safe_otp_code}</code></blockquote>\n"
                                f"<blockquote>{get_premium_emoji('sms')} FULL SMS:\n<code>{safe_full_sms}</code></blockquote>\n"
                                f"<b>{balance_msg}</b>")
                    user_buttons = InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"{get_premium_emoji('number')} Copy Number", callback_data=f"copy_number_{full_number}"),
                         InlineKeyboardButton(f"{get_premium_emoji('otp')} Copy OTP", callback_data=f"copy_otp_{safe_otp_code}")]
                    ])
                    group_msg = (f"{get_premium_emoji('status')} <b>OTP RECEIVE SUCCESSFUL</b> {get_premium_emoji('status')}\n"
                                 f"<blockquote>{get_premium_emoji('range')} RANGE: <code>{range_info}</code></blockquote>\n"
                                 f"<blockquote>{get_premium_emoji('country')} COUNTRY: <code>{country_flag} {country_name}</code></blockquote>\n"
                                 f"<blockquote>{get_premium_emoji('service')} SERVICE: <code>{service_name}</code></blockquote>\n"
                                 f"<blockquote>{get_premium_emoji('number')} NUMBER: <code>{masked_number}</code></blockquote>\n"
                                 f"<blockquote>{get_premium_emoji('otp')} OTP: <code>{safe_otp_code}</code></blockquote>\n"
                                 f"<blockquote>{get_premium_emoji('sms')} FULL SMS:\n<code>{safe_full_sms}</code></blockquote>")
                    group_buttons = InlineKeyboardMarkup([[
                        InlineKeyboardButton("‼️ PANEL", url=RANGE_GROUP_LINK),
                        InlineKeyboardButton("📢 OTP GROUP", url=OTP_GROUP_URL)
                    ]])
                    if uid:
                        try:
                            await app.bot.send_message(uid, user_msg, parse_mode="HTML", reply_markup=user_buttons)
                        except Exception as e:
                            print(f"❌ User Message Send Fail: {e}")
                    try:
                        await app.bot.send_message(OTP_GROUP_ID, group_msg, parse_mode="HTML", reply_markup=group_buttons)
                    except Exception as e:
                        print(f"❌ Group Send Fail: {e}")
            save_data(paid_data, PAID_SMS_FILE)
            current_time = datetime.now()
            for num_key in list(active_numbers.keys()):
                entry = active_numbers[num_key]
                if 'timestamp' not in entry:
                    entry['timestamp'] = current_time
                elif (current_time - entry['timestamp']).total_seconds() > 3600:
                    del active_numbers[num_key]
        except Exception as e:
            print(f"Monitor Error: {e}")
        await asyncio.sleep(CHECK_INTERVAL)

# ══════════════════════════════════════════════════════════════════════════════
# 📞 NUMBER ALLOCATION
# ══════════════════════════════════════════════════════════════════════════════
async def fast_allocate_number(query, context, rid, service, range_display):
    uid = query.from_user.id
    if is_user_banned(uid):
        await query.message.edit_text("🚫 YOU ARE BANNED 🚫")
        return
    try:
        num, country = await get_number_from_api(rid)
    except Exception as e:
        await query.message.edit_text(f"❌ Server error: {str(e)[:100]}")
        return
    if not num:
        await query.message.edit_text(
            f"{get_premium_custom_emoji('error')} <b>Number পাওয়া যায়নি।</b>\n"
            f"<blockquote>⚠️ এই range-এ এখন number নেই বা server busy।\n"
            f"আরেকটি range চেষ্টা করুন।</blockquote>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back_services")]])
        )
        return
    clean_num = normalize_number(num)
    add_number_taken(uid, 1)
    last_range[uid] = rid
    active_numbers[clean_num] = {"uid": uid, "range": range_display, "timestamp": datetime.now(), "service": service}
    country_flag, country_name = get_country_info(clean_num)
    text = (f"{get_premium_emoji('status')} <b>YOUR NUMBER</b> {get_premium_emoji('status')}\n"
            f"<blockquote>{get_premium_emoji('country')} COUNTRY: <code>{country_flag} {html.escape(country_name)}</code></blockquote>\n"
            f"<blockquote>{get_premium_emoji('range')} RANGE: <code>{range_display}</code></blockquote>\n"
            f"<blockquote>{get_premium_emoji('service')} SERVICE: <code>{service.upper()}</code></blockquote>\n"
            f"<blockquote>{get_premium_emoji('number')} NUMBER: <code>{num}</code></blockquote>\n"
            f"<b>{get_premium_custom_emoji('time')} SMS STATUS: ⏳ WAITING...</b>")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{get_premium_emoji('number')} Copy Number", callback_data=f"copy_number_{num}"),
         InlineKeyboardButton("🔄 SAME RANGE", callback_data=f"same_range_{rid}_{service}")],
        [InlineKeyboardButton("📢 OTP GROUP", url=OTP_GROUP_URL)],
        [InlineKeyboardButton("◀️ BACK", callback_data="back_to_services")]
    ])
    try:
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    except Exception as e:
        print(f"fast_allocate edit error: {e}")

async def process_numbers(update_or_query, context, range_text, count, service=""):
    if isinstance(update_or_query, Update) and update_or_query.callback_query:
        uid = update_or_query.callback_query.from_user.id
        chat_id = update_or_query.callback_query.message.chat_id
    else:
        uid = update_or_query.effective_user.id
        chat_id = update_or_query.effective_chat.id
    if is_user_banned(uid):
        await context.bot.send_message(chat_id=chat_id, text="🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return
    status_msg = await context.bot.send_message(chat_id=chat_id, text="🔍 SEARCHING . . .")
    rid = re.sub(r'[^0-9]', '', range_text)
    if not rid:
        await status_msg.edit_text("❌ INVALID RANGE!")
        return
    try:
        add_number_taken(uid, count)
        last_range[uid] = rid
        num, country = await get_number_from_api(rid)
        if not num:
            await status_msg.edit_text("❌ NO NUMBERS FOUND. TRY A VALID RANGE.")
            return
        clean_num = normalize_number(num)
        active_numbers[clean_num] = {"uid": uid, "range": range_text, "timestamp": datetime.now(), "service": service}
        country_flag, country_name = get_country_info(clean_num)
        service_block = f'<blockquote>{get_premium_emoji("service")} SERVICE: <code>{service.upper()}</code></blockquote>' if service else ''
        final_text = (f"{get_premium_emoji('status')} <b>YOUR NUMBER DETAILS</b> {get_premium_emoji('status')}\n"
                      f"<blockquote>{get_premium_emoji('country')} COUNTRY: <code>{country_flag} {country_name}</code></blockquote>\n"
                      f"<blockquote>{get_premium_emoji('range')} RANGE: <code>{range_text}</code></blockquote>\n"
                      f"{service_block}\n"
                      f"<blockquote>{get_premium_emoji('number')} NUMBER: <code>{num}</code></blockquote>\n"
                      f"<b>{get_premium_emoji('time')} SMS STATUS: ⏳ WAITING...</b>")
        svc = service if service else "CUSTOM"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{get_premium_emoji('number')} Copy Number", callback_data=f"copy_number_{num}"),
             InlineKeyboardButton("🔄 SAME RANGE", callback_data=f"same_range_{rid}_{svc}")],
            [InlineKeyboardButton("📢 OTP GROUP", url=OTP_GROUP_URL)],
            [InlineKeyboardButton("◀️ BACK", callback_data="back_to_services")]
        ])
        await status_msg.edit_text(final_text, parse_mode="HTML", reply_markup=keyboard)
    except Exception as e:
        print(f"Process Number Error: {e}")
        await status_msg.edit_text(f"❌ System Error: {str(e)}")

async def process_auto_number(update, context, range_text):
    uid = update.effective_user.id
    chat_id = update.effective_chat.id
    if is_user_banned(uid):
        await context.bot.send_message(chat_id=chat_id, text="🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return
    status_msg = await context.bot.send_message(chat_id=chat_id, text="🔍 SEARCHING...")
    rid = re.sub(r'[^0-9]', '', range_text)
    if not rid:
        await status_msg.edit_text("❌ INVALID RANGE! Send numbers only.")
        return
    try:
        num, country = await get_number_from_api(rid)
        if not num:
            await status_msg.edit_text("❌ NO NUMBERS FOUND. TRY A VALID RANGE.")
            return
        clean_num = normalize_number(num)
        add_number_taken(uid, 1)
        last_range[uid] = rid
        active_numbers[clean_num] = {"uid": uid, "range": range_text, "timestamp": datetime.now(), "service": "CUSTOM"}
        country_flag, country_name = get_country_info(clean_num)
        final_text = (f"{get_premium_emoji('status')} <b>YOUR NUMBER DETAILS</b> {get_premium_emoji('status')}\n"
                      f"<blockquote>{get_premium_emoji('country')} COUNTRY: <code>{country_flag} {country_name}</code></blockquote>\n"
                      f"<blockquote>{get_premium_emoji('range')} RANGE: <code>{range_text}</code></blockquote>\n"
                      f"<blockquote>{get_premium_emoji('number')} NUMBER: <code>{num}</code></blockquote>\n"
                      f"<b>{get_premium_custom_emoji('time')} SMS STATUS: ⏳ WAITING...</b>")
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{get_premium_emoji('number')} Copy Number", callback_data=f"copy_number_{num}"),
             InlineKeyboardButton("🔄 SAME RANGE", callback_data=f"same_range_{rid}_CUSTOM")],
            [InlineKeyboardButton("📢 OTP GROUP", url=OTP_GROUP_URL)],
            [InlineKeyboardButton("◀️ BACK", callback_data="back_to_services")]
        ])
        await status_msg.edit_text(final_text, parse_mode="HTML", reply_markup=keyboard)
    except Exception as e:
        print(f"Auto Number Error: {e}")
        await status_msg.edit_text(f"❌ Error: {str(e)}")

async def worker():
    while True:
        task = await request_queue.get()
        try:
            if task['type'] == 'process_numbers':
                await process_numbers(task['update'], task['context'], task['range_text'], task['count'], task.get('service', ''))
            elif task['type'] == 'auto_number':
                await process_auto_number(task['update'], task['context'], task['range_text'])
        except Exception as e:
            print(f"Worker Error: {e}")
        finally:
            request_queue.task_done()

# ══════════════════════════════════════════════════════════════════════════════
# 💸 WITHDRAW FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def load_withdraw_requests():
    if not os.path.exists(WITHDRAW_DATA_FILE):
        with open(WITHDRAW_DATA_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(WITHDRAW_DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_withdraw_requests(data):
    with open(WITHDRAW_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_payment_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

async def withdraw_method_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    uid = update.effective_user.id
    if text == "❌ CANCEL":
        context.user_data["withdraw_mode"] = None
        await update.message.reply_text("❌ WITHDRAW CANCELLED", reply_markup=main_keyboard(uid))
        return
    method_map = {"📱 BKASH": "BKASH", "💵 NAGAD": "NAGAD", "🚀 ROCKET": "ROCKET", "🏦 BINANCE": "BINANCE"}
    if text in method_map:
        method = method_map[text]
        config = load_system_config()
        if not config["payment_methods"].get(method, False):
            await update.message.reply_text("⚠️ এই মেথড বর্তমানে বন্ধ আছে। অন্য মেথড নির্বাচন করুন।", reply_markup=withdraw_method_keyboard())
            return
        balance = get_user(uid)['balance']
        context.user_data["withdraw_method"] = method
        context.user_data["withdraw_mode"] = "amount"
        min_with = config["min_withdraw"]
        max_with = config["max_withdraw"]
        msg = (f"<blockquote>💸 SEND YOUR AMOUNT!\n"
               f"💵 TOTAL BALANCE: {format_balance(balance)} BDT</blockquote>\n"
               f"<blockquote>📉 MINIMUM WITHDRAW {min_with} BDT</blockquote>\n"
               f"<blockquote>📈 MAXIMUM WITHDRAW {max_with} BDT</blockquote>\n"
               f"✅ <b>কোনো উইথড্র চার্জ নেই! সম্পূর্ণ ফ্রি</b>")
        await update.message.reply_text(msg, parse_mode="HTML", reply_markup=cancel_keyboard())
    else:
        await update.message.reply_text("⚠️ PLEASE SELECT A VALID PAYMENT METHOD!", reply_markup=withdraw_method_keyboard())

async def withdraw_amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    uid = update.effective_user.id
    if text == "❌ CANCEL":
        context.user_data["withdraw_mode"] = None
        await update.message.reply_text("❌ WITHDRAW CANCELLED", reply_markup=main_keyboard(uid))
        return
    try:
        amount = float(text)
    except:
        await update.message.reply_text("⚠️ PLEASE SEND A VALID AMOUNT!", reply_markup=cancel_keyboard())
        return
    balance = get_user(uid)['balance']
    config = load_system_config()
    min_with, max_with = config["min_withdraw"], config["max_withdraw"]
    if amount < min_with or amount > max_with:
        await update.message.reply_text(f"📉 MIN: {min_with} BDT | MAX: {max_with} BDT", reply_markup=cancel_keyboard())
        return
    if amount > balance:
        await update.message.reply_text("🚫 INSUFFICIENT BALANCE!", reply_markup=cancel_keyboard())
        return
    context.user_data["withdraw_amount"] = amount
    context.user_data["withdraw_mode"] = "number"
    await update.message.reply_text("📞 PLEASE SEND YOUR PAYMENT NUMBER!\n<blockquote>🔢 EXAMPLE: 017XXXXXXXX</blockquote>", parse_mode="HTML", reply_markup=cancel_keyboard())

async def withdraw_number_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    uid = update.effective_user.id
    if text == "❌ CANCEL":
        context.user_data["withdraw_mode"] = None
        await update.message.reply_text("❌ WITHDRAW CANCELLED", reply_markup=main_keyboard(uid))
        return
    if not is_valid_bangladesh_number(text):
        await update.message.reply_text("⚠️ PLEASE SEND VALID NUMBER! 017XXXXXXXX", reply_markup=cancel_keyboard())
        return
    method = context.user_data.get("withdraw_method")
    amount = context.user_data.get("withdraw_amount")
    payment_number = text
    payment_id = generate_payment_id()
    context.user_data["temp_withdraw"] = {"method": method, "amount": amount, "number": payment_number, "payment_id": payment_id}
    msg = (f"✨ <b>YOUR PAYMENT DETAILS!</b> ✨\n"
           f"<blockquote>📝 METHOD: {method}\n"
           f"📞 NUMBER: {payment_number}\n"
           f"💰 AMOUNT: {format_balance(amount)} BDT\n"
           f"✅ কোন চার্জ নেই! সম্পূর্ণ ফ্রি\n"
           f"✅ CORRECT → CONFIRM\n"
           f"❌ WRONG → CANCEL</blockquote>")
    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ CANCEL", callback_data="withdraw_cancel"), InlineKeyboardButton("✅ CONFIRM", callback_data="withdraw_confirm")]
    ]))

async def process_withdraw_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()
    temp_data = context.user_data.get("temp_withdraw")
    if not temp_data:
        await query.message.reply_text("⚠️ SESSION EXPIRED.", reply_markup=main_keyboard(uid))
        return
    method, amount, payment_number, payment_id = temp_data["method"], temp_data["amount"], temp_data["number"], temp_data["payment_id"]
    await update_db_balance(uid, -amount)
    wr = load_withdraw_requests()
    wr[str(payment_id)] = {"user_id": uid, "method": method, "amount": amount, "number": payment_number, "payment_id": payment_id, "status": "pending", "timestamp": datetime.now().isoformat()}
    save_withdraw_requests(wr)
    add_payment_record(uid, method, amount, payment_number, payment_id, "pending")
    await query.message.edit_text(f"✅ <b>WITHDRAWAL REQUEST SUBMITTED</b> ✅\n"
                                  f"<blockquote>📝 METHOD: <code>{method}</code>\n"
                                  f"📞 NUMBER: <code>{payment_number}</code>\n"
                                  f"💰 AMOUNT: <code>{format_balance(amount)} BDT</code>\n"
                                  f"🆔 ID: <code>{payment_id}</code></blockquote>", parse_mode="HTML")
    await context.bot.send_message(uid, "🎉 <b>WITHDRAW REQUEST SUBMITTED!</b>", parse_mode="HTML", reply_markup=main_keyboard(uid))
    admin_msg = (f"✅ <b>NEW WITHDRAWAL REQUEST</b>\n"
                 f"<blockquote>🆔 USER: <code>{uid}</code>\n"
                 f"📝 METHOD: <code>{method}</code>\n"
                 f"📞 NUMBER: <code>{payment_number}</code>\n"
                 f"💰 AMOUNT: <code>{format_balance(amount)} BDT</code>\n"
                 f"🆔 ID: <code>{payment_id}</code></blockquote>")
    admin_kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ REJECT", callback_data=f"admin_reject_{payment_id}"), InlineKeyboardButton("✅ APPROVE", callback_data=f"admin_approve_{payment_id}")]])
    for admin_id in ADMINS:
        try:
            await context.bot.send_message(admin_id, admin_msg, parse_mode="HTML", reply_markup=admin_kb)
        except Exception as e:
            print(f"Admin notify fail {admin_id}: {e}")
    context.user_data["temp_withdraw"] = None
    context.user_data["withdraw_mode"] = None

async def process_withdraw_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()
    context.user_data["temp_withdraw"] = None
    context.user_data["withdraw_mode"] = None
    await query.message.edit_text("❌ WITHDRAW CANCELLED")
    await context.bot.send_message(uid, "🔹 PLEASE USE THE BUTTONS BELOW:", reply_markup=main_keyboard(uid))

async def admin_approve_withdraw(update, context, payment_id):
    query = update.callback_query
    await query.answer()
    wr = load_withdraw_requests()
    if payment_id not in wr:
        await query.message.reply_text("⚠️ REQUEST NOT FOUND!")
        return
    rd = wr[payment_id]
    wr[payment_id]["status"] = "approved"
    save_withdraw_requests(wr)
    update_payment_status(payment_id, "approved")
    try:
        await context.bot.send_message(
            rd["user_id"],
            f"🎉 <b>WITHDRAWAL APPROVED!</b>\n"
            f"<blockquote>📝 METHOD: <code>{rd['method']}</code>\n"
            f"📞 NUMBER: <code>{rd['number']}</code>\n"
            f"💰 AMOUNT: <code>{format_balance(rd['amount'])} BDT</code></blockquote>",
            parse_mode="HTML"
        )
    except:
        pass
    await query.message.edit_text(f"✅ APPROVED | User: {rd['user_id']} | Amount: {format_balance(rd['amount'])} BDT")

async def admin_reject_withdraw(update, context, payment_id):
    query = update.callback_query
    await query.answer()
    wr = load_withdraw_requests()
    if payment_id not in wr:
        await query.message.reply_text("⚠️ REQUEST NOT FOUND!")
        return
    rd = wr[payment_id]
    await update_db_balance(rd["user_id"], rd["amount"])
    wr[payment_id]["status"] = "rejected"
    save_withdraw_requests(wr)
    update_payment_status(payment_id, "rejected")
    try:
        await context.bot.send_message(rd["user_id"], f"❌ WITHDRAWAL REQUEST REJECTED\n"
                                                      f"<blockquote>💰 AMOUNT: {format_balance(rd['amount'])} BDT\n"
                                                      f"✅ আপনার টাকা ফেরত দেওয়া হয়েছে।</blockquote>", parse_mode="HTML")
    except: pass
    await query.message.edit_text(f"❌ REJECTED | User: {rd['user_id']} | Amount: {format_balance(rd['amount'])} BDT | ✅ Balance Refunded")

# ══════════════════════════════════════════════════════════════════════════════
# 📜 USER HISTORY & REFERRAL
# ══════════════════════════════════════════════════════════════════════════════
async def show_history_menu(update, context):
    if update.callback_query:
        uid = update.callback_query.from_user.id
        msg = update.callback_query.message
    else:
        uid = update.effective_user.id
        msg = update.message
    if is_user_banned(uid):
        await msg.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return
    user_data = get_user(uid)
    stats = get_user_stats(uid)
    text = (
        f"📜 <b>YOUR HISTORY</b>\n"
        f"<blockquote>🔑 মোট OTP: <b>{stats['total_otps']}</b>\n"
        f"💸 মোট উইথড্র: আপনার পেমেন্ট হিস্টোরি দেখুন\n"
        f"🎁 রেফারেল: নিচের বাটনে ক্লিক করুন</blockquote>\n"
        f"✨ নিচ থেকে নির্বাচন করুন:"
    )
    await msg.reply_text(text, parse_mode="HTML", reply_markup=history_keyboard())

async def show_otp_history(update, context):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()
    logs = get_user_otp_history(uid, limit=15)
    if not logs:
        await query.message.edit_text(
            "📜 <b>OTP HISTORY</b>\n"
            "<blockquote>❌ কোনো OTP হিস্টোরি নেই।</blockquote>",
            parse_mode="HTML",
            reply_markup=history_keyboard()
        )
        return
    text = f"🔑 <b>RECENT OTP HISTORY</b> (Last 15)\n"
    text += f"━━━━━━━━━━━━━━━━━━━━\n"
    for i, log in enumerate(logs, 1):
        try:
            dt = datetime.fromisoformat(log['timestamp'])
            d = log.get('details', {})
            num = d.get('number', 'N/A')
            otp = d.get('otp', 'N/A')
            text += f"\n{i}. <b>{dt.strftime('%d/%m %I:%M %p')}</b>\n"
            text += f"   📞 <code>{num}</code>\n"
            text += f"   🔑 <code>{otp}</code>\n"
        except:
            continue
    text += "\n━━━━━━━━━━━━━━━━━━━━\n"
    text += "✨ মোট দেখানো হয়েছে: 15টি"
    await query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back_to_history")]])
    )

async def show_payment_history(update, context):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()
    records = get_user_payment_history(uid, limit=10)
    if not records:
        await query.message.edit_text(
            "💸 <b>PAYMENT HISTORY</b>\n"
            "<blockquote>❌ কোনো পেমেন্ট হিস্টোরি নেই।</blockquote>",
            parse_mode="HTML",
            reply_markup=history_keyboard()
        )
        return
    text = f"💸 <b>PAYMENT HISTORY</b> (Last 10)\n"
    text += f"━━━━━━━━━━━━━━━━━━━━\n"
    for i, rec in enumerate(records, 1):
        try:
            dt = datetime.fromisoformat(rec['timestamp'])
            status_emoji = {"approved": "✅", "rejected": "❌", "pending": "⏳"}.get(rec['status'], "❓")
            text += f"\n{i}. {status_emoji} <b>{rec['method']}</b>\n"
            text += f"   💰 {rec['amount']:.2f} BDT\n"
            text += f"   📞 <code>{rec['number']}</code>\n"
            text += f"   📅 {dt.strftime('%d/%m/%Y %I:%M %p')}\n"
        except:
            continue
    await query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back_to_history")]])
    )

async def show_referral_stats(update, context):
    query = update.callback_query
    uid = query.from_user.id
    await query.answer()
    stats = get_referral_stats(uid)
    bot_username = context.bot.username
    current_referral_price = get_referral_price()
    text = (
        f"🎁 <b>REFERRAL PROGRAM</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<blockquote>🔗 আপনার রেফারেল লিংক:\n"
        f"<code>https://t.me/{bot_username}?start={uid}</code></blockquote>\n"
        f"📊 <b>আপনার স্ট্যাটস:</b>\n"
        f"<blockquote>👥 মোট রেফার: <b>{stats['count']}</b>\n"
        f"💰 মোট আয়: <b>{stats['earned']:.2f} BDT</b>\n"
        f"💵 প্রতি রেফার: <b>{current_referral_price:.2f} BDT</b></blockquote>\n"
    )
    if stats['users']:
        text += "\n📋 <b>সাম্প্রতিক রেফার:</b>\n"
        for u in stats['users'][-5:]:
            try:
                dt = datetime.fromisoformat(u['joined_at'])
                text += f"• <code>{u['user_id']}</code> - {dt.strftime('%d/%m')}\n"
            except:
                pass
        text += "\n✨ বন্ধুদের আমন্ত্রণ করুন এবং বোনাস উপার্জন করুন!"
    await query.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Copy Link", callback_data=f"copy_referral_{uid}")],
            [InlineKeyboardButton("🔙 BACK", callback_data="back_to_history")]
        ])
    )

# ══════════════════════════════════════════════════════════════════════════════
# 🔍 ADMIN SEARCH USER
# ══════════════════════════════════════════════════════════════════════════════
async def admin_search_user_start(update, context):
    context.user_data["admin_search_mode"] = True
    await update.message.reply_text(
        "🔍 <b>SEARCH USER</b>\n"
        "<blockquote>✨ ইউজার ID, Balance বা আংশিক ID দিয়ে সার্চ করুন।\n"
        "উদাহরণ:\n"
        "• <code>7647858886</code> (পুরো ID)\n"
        "• <code>7647</code> (আংশিক ID)\n"
        "• <code>100</code> (Balance)</blockquote>\n"
        "❌ বাতিল করতে CANCEL চাপুন।",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )

async def admin_process_search_user(update, context):
    if not context.user_data.get("admin_search_mode"):
        return
    query = update.message.text.strip()
    if query == "❌ CANCEL":
        context.user_data["admin_search_mode"] = False
        await update.message.reply_text("❌ বাতিল করা হয়েছে।", reply_markup=user_management_keyboard())
        return
    results = search_users(query)
    context.user_data["admin_search_mode"] = False
    if not results:
        await update.message.reply_text(
            f"❌ <b>কোনো ইউজার পাওয়া যায়নি!</b>\n"
            f"<blockquote>🔍 Query: <code>{query}</code></blockquote>",
            parse_mode="HTML",
            reply_markup=user_management_keyboard()
        )
        return
    text = f"🔍 <b>SEARCH RESULTS</b> ({len(results)} found)\n"
    text += f"<blockquote>🔎 Query: <code>{query}</code></blockquote>\n"
    text += f"━━━━━━━━━━━━━━━━━━━━\n"
    for i, res in enumerate(results, 1):
        uid = res['id']
        data = res['data']
        balance = data.get('balance', 0)
        text += f"\n{i}. 🆔 <code>{uid}</code>\n"
        text += f"   💰 {balance:.2f} BDT\n"
        text += f"   🎯 Match: {res['match']}\n"
    buttons = []
    for res in results[:10]:
        buttons.append([InlineKeyboardButton(f"👤 {res['id']}", callback_data=f"admin_view_user_{res['id']}")])
    buttons.append([InlineKeyboardButton("🔙 BACK", callback_data="back_to_admin_panel")])
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

async def admin_view_user_details(update, context):
    query = update.callback_query
    await query.answer()
    target_uid = query.data.replace("admin_view_user_", "")
    user_data = get_user(int(target_uid))
    stats = get_user_stats(target_uid)
    payments = get_user_payment_history(int(target_uid), limit=5)
    text = (
        f"👤 <b>USER DETAILS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<blockquote>🆔 ID: <code>{target_uid}</code>\n"
        f"💰 Balance: <b>{user_data.get('balance', 0):.2f} BDT</b>\n"
        f"📊 Total Numbers: {stats['total_numbers']}\n"
        f"🔑 Total OTPs: {stats['total_otps']}\n"
        f"📅 Today: 📱{stats['today_numbers']} | 🔑{stats['today_otps']}</blockquote>\n"
    )
    if payments:
        text += "\n💸 <b>Recent Payments:</b>\n"
        for p in payments[:3]:
            status_emoji = {"approved": "✅", "rejected": "❌", "pending": "⏳"}.get(p['status'], "❓")
            text += f"• {status_emoji} {p['amount']:.2f} BDT ({p['method']})\n"
    buttons = [
        [InlineKeyboardButton("➕ Add Balance", callback_data=f"admin_add_bal_{target_uid}"),
         InlineKeyboardButton("➖ Remove", callback_data=f"admin_rem_bal_{target_uid}")],
        [InlineKeyboardButton("⛔ Ban", callback_data=f"admin_ban_{target_uid}"),
         InlineKeyboardButton("🔓 Unban", callback_data=f"admin_unban_{target_uid}")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_to_admin_panel")]
    ]
    await query.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

# ══════════════════════════════════════════════════════════════════════════════
# ⚙️ ADMIN FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
async def admin_add_balance_start(update, context):
    context.user_data["add_balance_mode"] = True
    await update.message.reply_text("💰 SEND USER ID TO ADD BALANCE:")

async def admin_remove_balance_start(update, context):
    context.user_data["remove_balance_mode"] = True
    await update.message.reply_text("💸 SEND USER ID TO REMOVE BALANCE:")

async def process_add_balance_user(update, context):
    uid_to_add = update.message.text.strip()
    if not uid_to_add.isdigit() or not user_exists(int(uid_to_add)):
        await update.message.reply_text("❌ INVALID USER ID OR NOT FOUND!")
        context.user_data["add_balance_mode"] = False
        return
    context.user_data["pending_add_user"] = int(uid_to_add)
    await update.message.reply_text("💵 SEND AMOUNT TO ADD:")

async def process_remove_balance_user(update, context):
    uid_to_remove = update.message.text.strip()
    if not uid_to_remove.isdigit() or not user_exists(int(uid_to_remove)):
        await update.message.reply_text("❌ INVALID USER ID OR NOT FOUND!")
        context.user_data["remove_balance_mode"] = False
        return
    context.user_data["pending_remove_user"] = int(uid_to_remove)
    await update.message.reply_text("💸 SEND AMOUNT TO REMOVE:")

async def process_add_balance_amount(update, context):
    try:
        amount = float(update.message.text.strip())
        if amount <= 0: raise ValueError
    except:
        await update.message.reply_text("❌ INVALID AMOUNT!")
        return
    uid = context.user_data.get("pending_add_user")
    if not uid:
        context.user_data["add_balance_mode"] = False
        await update.message.reply_text("⚠️ SESSION EXPIRED.")
        return
    new_balance = await update_db_balance(uid, amount)
    await update.message.reply_text(f"✅ ADD BALANCE SUCCESSFUL\n"
                                    f"🆔 USER: `{uid}`\n"
                                    f"💰 ADDED: `{format_balance(amount)} BDT`\n"
                                    f"📈 NEW BALANCE: `{format_balance(new_balance)} BDT`", parse_mode="Markdown")
    try: await context.bot.send_message(uid, f"🎉 ADMIN ADDED `{format_balance(amount)} BDT` TO YOUR ACCOUNT!\n"
                                             f"💵 NEW BALANCE: `{format_balance(new_balance)} BDT`", parse_mode="Markdown")
    except: pass
    context.user_data["add_balance_mode"] = False
    context.user_data["pending_add_user"] = None

async def process_remove_balance_amount(update, context):
    try:
        amount = float(update.message.text.strip())
        if amount <= 0: raise ValueError
    except:
        await update.message.reply_text("❌ INVALID AMOUNT!")
        return
    uid = context.user_data.get("pending_remove_user")
    if not uid:
        context.user_data["remove_balance_mode"] = False
        await update.message.reply_text("⚠️ SESSION EXPIRED.")
        return
    old_balance = get_user(uid).get("balance", 0)
    if amount > old_balance:
        await update.message.reply_text(f"❌ INSUFFICIENT BALANCE! Current: {format_balance(old_balance)} BDT")
        context.user_data["remove_balance_mode"] = False
        context.user_data["pending_remove_user"] = None
        return
    new_balance = await update_db_balance(uid, -amount)
    await update.message.reply_text(f"✅ REMOVE BALANCE SUCCESSFUL\n"
                                    f"🆔 USER: `{uid}`\n"
                                    f"💸 REMOVED: `{format_balance(amount)} BDT`\n"
                                    f"📉 NEW BALANCE: `{format_balance(new_balance)} BDT`", parse_mode="Markdown")
    try: await context.bot.send_message(uid, f"⚠️ ADMIN REMOVED `{format_balance(amount)} BDT` FROM YOUR ACCOUNT!\n"
                                             f"💵 NEW BALANCE: `{format_balance(new_balance)} BDT`", parse_mode="Markdown")
    except: pass
    context.user_data["remove_balance_mode"] = False
    context.user_data["pending_remove_user"] = None

async def admin_ban_user_start(update, context):
    context.user_data["admin_ban_mode"] = True
    await update.message.reply_text("🚫 SEND TELEGRAM ID TO BAN USER:")

async def admin_unban_user_start(update, context):
    context.user_data["admin_unban_mode"] = True
    await update.message.reply_text("🔓 SEND TELEGRAM ID TO UNBAN USER:")

async def process_ban_user(update, context):
    uid_to_ban = update.message.text.strip()
    if not uid_to_ban.isdigit() or not user_exists(int(uid_to_ban)):
        await update.message.reply_text("❌ INVALID USER ID OR NOT FOUND!")
        context.user_data["admin_ban_mode"] = False
        return
    if is_user_banned(int(uid_to_ban)):
        await update.message.reply_text("⚠️ USER IS ALREADY BANNED!")
        context.user_data["admin_ban_mode"] = False
        return
    ban_user(int(uid_to_ban))
    try: await context.bot.send_message(int(uid_to_ban), "🚫 YOU HAVE BEEN BANNED\n"
                                                         f"📞 Contact support.", parse_mode="Markdown")
    except: pass
    await update.message.reply_text(f"✅ USER `{uid_to_ban}` BANNED!", parse_mode="Markdown", reply_markup=system_config_keyboard())
    context.user_data["admin_ban_mode"] = False

async def process_unban_user(update, context):
    uid_to_unban = update.message.text.strip()
    if not uid_to_unban.isdigit() or not is_user_banned(int(uid_to_unban)):
        await update.message.reply_text("❌ INVALID USER ID OR NOT BANNED!")
        context.user_data["admin_unban_mode"] = False
        return
    unban_user(int(uid_to_unban))
    try: await context.bot.send_message(int(uid_to_unban), "✅ YOU HAVE BEEN UNBANNED! Use /start", parse_mode="Markdown")
    except: pass
    await update.message.reply_text(f"✅ USER `{uid_to_unban}` UNBANNED!", parse_mode="Markdown", reply_markup=system_config_keyboard())
    context.user_data["admin_unban_mode"] = False

async def show_banned_users_list(update, context):
    banned_list = load_banned_users()
    if not banned_list:
        await update.message.reply_text("📜 NO BANNED USERS.", reply_markup=system_config_keyboard())
        return
    text = "📜 BANNED USER LIST\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n"
    text += "\n".join(f"{i}. `{uid}`" for i, uid in enumerate(banned_list, 1))
    text += f"\n📊 Total: {len(banned_list)}"
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=system_config_keyboard())

async def admin_change_min_withdraw_start(update, context):
    context.user_data["admin_min_withdraw_mode"] = True
    await update.message.reply_text(f"💵 সেন্ড দ্য নিউ মিনিমাম উইথড্র অ্যামাউন্ট (শুধু সংখ্যা):\n"
                                    f"বর্তমান মান: {load_system_config()['min_withdraw']}", reply_markup=cancel_keyboard())

async def admin_change_min_withdraw_amount(update, context):
    if not context.user_data.get("admin_min_withdraw_mode"): return
    try:
        new_min = float(update.message.text.strip())
        if new_min < 0: raise ValueError
        config = load_system_config()
        config["min_withdraw"] = new_min
        save_system_config(config)
        await update.message.reply_text(f"✅ মিনিমাম উইথড্র অ্যামাউন্ট পরিবর্তন করে {new_min} BDT করা হয়েছে।", reply_markup=system_config_keyboard())
    except:
        await update.message.reply_text("❌ ভ্যালিড অ্যামাউন্ট দিন।", reply_markup=system_config_keyboard())
    finally:
        context.user_data["admin_min_withdraw_mode"] = False

async def admin_change_otp_rate_start(update, context):
    context.user_data["admin_otp_rate_mode"] = True
    await update.message.reply_text(f"💲 বর্তমান OTP রেট: `{get_otp_rate():.2f} BDT`\n"
                                    f"সেন্ড দ্য নিউ রেট (শুধু সংখ্যা, যেমন: `0.25`):\n"
                                    f"<blockquote>সাবধান: এটি সব নতুন OTP-তে প্রযোজ্য হবে।</blockquote>", parse_mode="HTML", reply_markup=cancel_keyboard())

async def admin_change_otp_rate_amount(update, context):
    if not context.user_data.get("admin_otp_rate_mode"): return
    try:
        new_rate = float(update.message.text.strip())
        if new_rate <= 0: raise ValueError
        config = load_system_config()
        config["otp_rate"] = new_rate
        save_system_config(config)
        await update.message.reply_text(f"✅ OTP রেট পরিবর্তন করে `{new_rate:.2f} BDT` করা হয়েছে।", parse_mode="HTML", reply_markup=system_config_keyboard())
    except:
        await update.message.reply_text("❌ ভ্যালিড রেট দিন (যেমন: 0.25)।", reply_markup=system_config_keyboard())
    finally:
        context.user_data["admin_otp_rate_mode"] = False

async def admin_change_referral_price_start(update, context):
    context.user_data["admin_referral_price_mode"] = True
    current_price = get_referral_price()
    await update.message.reply_text(
        f"🎁 <b>REFER PRICE SET</b>\n"
        f"<blockquote>💵 বর্তমান রেফার প্রাইস: <b>{current_price:.2f} BDT</b></blockquote>\n"
        f"✨ নতুন রেফার প্রাইস পাঠান (শুধু সংখ্যা, যেমন: <code>5</code> বা <code>0</code>):\n"
        f"<blockquote>⚠️ 0 দিলে রেফারেল বোনাস বন্ধ হয়ে যাবে।</blockquote>",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )

async def admin_change_referral_price_amount(update, context):
    if not context.user_data.get("admin_referral_price_mode"):
        return
    try:
        new_price = float(update.message.text.strip())
        if new_price < 0:
            raise ValueError
        set_referral_price(new_price)
        await update.message.reply_text(
            f"✅ <b>REFER PRICE UPDATED!</b>\n"
            f"<blockquote>💵 নতুন রেফার প্রাইস: <b>{new_price:.2f} BDT</b></blockquote>\n"
            f"✨ এখন থেকে নতুন রেফারেলের জন্য এই পরিমাণ বোনাস যোগ হবে।",
            parse_mode="HTML",
            reply_markup=system_config_keyboard()
        )
    except:
        await update.message.reply_text("❌ ভ্যালিড প্রাইস দিন (যেমন: 5 বা 0)।", reply_markup=system_config_keyboard())
    finally:
        context.user_data["admin_referral_price_mode"] = False

async def admin_toggle_payment_methods(update, context):
    config = load_system_config()
    buttons = [[InlineKeyboardButton(f"{'✅' if enabled else '❌'} {method}", callback_data=f"toggle_method_{method}")] for method, enabled in config["payment_methods"].items()]
    buttons.append([InlineKeyboardButton("🔙 BACK", callback_data="back_to_admin_panel")])
    await update.message.reply_text("💳 পেমেন্ট মেথড টগল করুন:\n"
                                    "সবুজ চিহ্ন মানে সচল, লাল মানে বন্ধ।\n"
                                    "ক্লিক করে চেঞ্জ করুন।", reply_markup=InlineKeyboardMarkup(buttons))

async def handle_toggle_method_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("toggle_method_"):
        method = data.replace("toggle_method_", "")
        new_state = toggle_payment_method(method)
        status = "সচল ✅" if new_state else "বন্ধ ❌"
        config = load_system_config()
        buttons = [[InlineKeyboardButton(f"{'✅' if enabled else '❌'} {m}", callback_data=f"toggle_method_{m}")] for m, enabled in config["payment_methods"].items()]
        buttons.append([InlineKeyboardButton("🔙 BACK", callback_data="back_to_admin_panel")])
        await query.message.edit_text(f"✅ {method} মেথড এখন {status}।\n"
                                      f"💳 পেমেন্ট মেথড টগল করুন:", reply_markup=InlineKeyboardMarkup(buttons))
    elif data == "back_to_admin_panel":
        await query.message.delete()
        await query.message.chat.send_message("⚙️ System Configuration:", reply_markup=system_config_keyboard())

async def admin_add_channel_start(update, context):
    context.user_data["add_channel_mode"] = True
    await update.message.reply_text("➕ ADD CHANNEL/GROUP\n"
                                    "ফরম্যাট: `লিংক|লেবেল` (লেবেল ঐচ্ছিক)\n"
                                    "উদাহরণ: `https://t.me/zebra_sms|📢 আমাদের চ্যানেল`\n"
                                    "প্রাইভেট লিংকের জন্য: `লিংক|চ্যাট_আইডি|লেবেল`", parse_mode="Markdown", reply_markup=cancel_keyboard())

async def admin_process_add_channel(update, context):
    if not context.user_data.get("add_channel_mode"): return
    text = update.message.text.strip()
    if text == "❌ CANCEL":
        context.user_data["add_channel_mode"] = None
        await update.message.reply_text("❌ বাতিল করা হয়েছে।", reply_markup=required_channels_keyboard())
        return
    parts = text.split("|")
    link = parts[0].strip()
    label, chat_id = None, None
    if len(parts) > 1:
        if parts[1].strip().isdigit():
            chat_id = int(parts[1].strip())
            label = parts[2].strip() if len(parts) > 2 else None
        else:
            label = parts[1].strip()
            if len(parts) > 2 and parts[2].strip().isdigit():
                chat_id = int(parts[2].strip())
    success, msg = add_required_channel(link, label, chat_id)
    await update.message.reply_text(f"{'✅' if success else '❌'} {msg}", reply_markup=required_channels_keyboard() if success else cancel_keyboard())
    context.user_data["add_channel_mode"] = None

async def admin_remove_channel_start(update, context):
    context.user_data["remove_channel_mode"] = True
    await update.message.reply_text("❌ REMOVE CHANNEL/GROUP\n"
                                    "দয়া করে যে লিংক বা লেবেল রিমুভ করতে চান তা দিন:", parse_mode="Markdown", reply_markup=cancel_keyboard())

async def admin_process_remove_channel(update, context):
    if not context.user_data.get("remove_channel_mode"): return
    text = update.message.text.strip()
    if text == "❌ CANCEL":
        context.user_data["remove_channel_mode"] = None
        await update.message.reply_text("❌ বাতিল করা হয়েছে।", reply_markup=required_channels_keyboard())
        return
    success, msg = remove_required_channel(text)
    await update.message.reply_text(f"{'✅' if success else '❌'} {msg}", reply_markup=required_channels_keyboard() if success else cancel_keyboard())
    context.user_data["remove_channel_mode"] = None

async def admin_list_channels(update, context):
    channels = get_all_required_channels()
    if not channels:
        await update.message.reply_text("📋 কোনো চ্যানেল/গ্রুপ যোগ করা হয়নি।", reply_markup=required_channels_keyboard())
        return
    text = "📋 বর্তমান চ্যানেল/গ্রুপ লিস্ট:\n"
    text += "\n".join(f"{i}. লেবেল: `{ch.get('label', 'N/A')}`\n"
                      f"   লিংক: `{ch.get('link', 'N/A')}`\n"
                      f"   chat_id: `{ch.get('chat_id', 'N/A')}`\n" for i, ch in enumerate(channels, 1))
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=required_channels_keyboard())

async def admin_show_all_users(update, context):
    uid = update.effective_user.id
    if not is_admin(uid): return
    user_db = load_data(USER_DATA_FILE)
    all_uids = list(user_db.keys())
    total_users = len(all_uids)
    if total_users == 0:
        await update.message.reply_text("📊 মোট ইউজার: 0\n"
                                        "কোনো ইউজার রেজিস্টার্ড নেই।", reply_markup=user_management_keyboard())
        return
    user_list_sorted = sorted(all_uids, key=int)
    if total_users <= 50:
        msg = f"📊 মোট ইউজার: `{total_users}`\n"
        msg += "ইউজার লিস্ট:\n"
        msg += "\n".join(f"{i+1}. `{u}`" for i, u in enumerate(user_list_sorted))
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=user_management_keyboard())
    else:
        content = f"Total Users: {total_users}\n"
        content += "\n".join(user_list_sorted)
        f = io.BytesIO(content.encode())
        f.name = f"all_users_{total_users}.txt"
        await update.message.reply_document(document=f, caption=f"📊 মোট ইউজার: {total_users}\n"
                                                                f"ইউজার আইডি লিস্ট সংযুক্ত।", reply_markup=user_management_keyboard())

async def admin_show_all_balances(update, context):
    user_db = load_data(USER_DATA_FILE)
    if not user_db:
        await update.message.reply_text("📊 কোনো ইউজার নেই।", reply_markup=user_management_keyboard())
        return
    content = "User ID | Balance (BDT)\n"
    content += "="*40 + "\n"
    total_balance = 0
    for uid, data in sorted(user_db.items(), key=lambda x: x[1].get('balance', 0), reverse=True):
        bal = data.get('balance', 0)
        total_balance += bal
        content += f"{uid} | {bal:.2f}\n"
    content += "="*40 + f"\nTOTAL: {total_balance:.2f} BDT"
    f = io.BytesIO(content.encode())
    f.name = f"all_balances_{len(user_db)}.txt"
    await update.message.reply_document(document=f, caption=f"💰 মোট ইউজার: {len(user_db)}\n"
                                                            f"💵 মোট ব্যালেন্স: {total_balance:.2f} BDT", reply_markup=user_management_keyboard())

async def admin_status_view(update, context):
    config = load_system_config()
    user_db = load_data(USER_DATA_FILE)
    banned = load_banned_users()
    channels = get_all_required_channels()
    auto_mode = get_auto_range_mode()
    text = (
        f"📈 <b>SYSTEM STATUS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<blockquote>👥 Total Users: <b>{len(user_db)}</b>\n"
        f"⛔ Banned Users: <b>{len(banned)}</b>\n"
        f"🔗 Channels: <b>{len(channels)}</b>\n"
        f"💲 OTP Rate: <b>{config.get('otp_rate', 0):.2f} BDT</b>\n"
        f"🎁 Referral Price: <b>{config.get('referral_price', 0):.2f} BDT</b>\n"
        f"💵 Min Withdraw: <b>{config.get('min_withdraw', 0)} BDT</b>\n"
        f"🚀 Auto-Range: <b>{'ENABLED' if auto_mode else 'DISABLED'}</b>\n"
        f"🗄️ MongoDB: <b>{'Connected' if db_mongo_connected else 'Disconnected'}</b></blockquote>"
    )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=system_config_keyboard())

async def admin_user_check_start(update, context):
    context.user_data["admin_user_check_mode"] = True
    await update.message.reply_text(
        "👤 <b>USER CHECK</b>\n"
        "<blockquote>✨ ইউজার ID দিন বিস্তারিত দেখতে:</blockquote>\n"
        "❌ বাতিল করতে CANCEL চাপুন।",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )

async def admin_process_user_check(update, context):
    if not context.user_data.get("admin_user_check_mode"):
        return
    query = update.message.text.strip()
    if query == "❌ CANCEL":
        context.user_data["admin_user_check_mode"] = False
        await update.message.reply_text("❌ বাতিল করা হয়েছে।", reply_markup=system_config_keyboard())
        return
    context.user_data["admin_user_check_mode"] = False
    if not query.isdigit():
        await update.message.reply_text("❌ ভ্যালিড ইউজার ID দিন!", reply_markup=system_config_keyboard())
        return
    if not user_exists(int(query)):
        await update.message.reply_text("❌ ইউজার পাওয়া যায়নি!", reply_markup=system_config_keyboard())
        return
    user_data = get_user(int(query))
    stats = get_user_stats(int(query))
    text = (
        f"👤 <b>USER DETAILS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<blockquote>🆔 ID: <code>{query}</code>\n"
        f"💰 Balance: <b>{user_data.get('balance', 0):.2f} BDT</b>\n"
        f"📊 Total Numbers: {stats['total_numbers']}\n"
        f"🔑 Total OTPs: {stats['total_otps']}\n"
        f"📅 Today: 📱{stats['today_numbers']} | 🔑{stats['today_otps']}\n"
        f"⛔ Banned: {'Yes' if is_user_banned(int(query)) else 'No'}</blockquote>"
    )
    buttons = [
        [InlineKeyboardButton("➕ Add Balance", callback_data=f"admin_add_bal_{query}"),
         InlineKeyboardButton("➖ Remove", callback_data=f"admin_rem_bal_{query}")],
        [InlineKeyboardButton("⛔ Ban", callback_data=f"admin_ban_{query}"),
         InlineKeyboardButton("🔓 Unban", callback_data=f"admin_unban_{query}")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_to_admin_panel")]
    ]
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

# ══════════════════════════════════════════════════════════════════════════════
# 🎯 ADMIN CUSTOM SERVICES (UPDATED - STEP BY STEP)
# ══════════════════════════════════════════════════════════════════════════════
async def admin_add_custom_service_start(update, context):
    context.user_data["add_custom_service_mode"] = "name"
    await update.message.reply_text(
        "🎯 <b>ADD CUSTOM SERVICE</b>\n"
        f"{format_premium_divider('primary')}\n"
        "<blockquote>✨ প্রথমে সার্ভিসের নাম দিন:\n"
        "উদাহরণ: <code>facebook</code>, <code>whatsapp</code>, <code>instagram</code></blockquote>\n"
        "❌ বাতিল করতে CANCEL চাপুন।",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )

async def admin_process_add_custom_service_name(update, context):
    text = update.message.text.strip()
    if text == "❌ CANCEL":
        context.user_data["add_custom_service_mode"] = None
        await update.message.reply_text("❌ বাতিল করা হয়েছে।", reply_markup=custom_services_keyboard())
        return
    service_name = text.lower().replace(" ", "_")
    context.user_data["new_service_name"] = service_name
    context.user_data["add_custom_service_mode"] = "ranges"
    await update.message.reply_text(
        f"🎯 <b>SERVICE NAME: {service_name.upper()}</b>\n"
        f"{format_premium_divider('success')}\n"
        "<blockquote>✨ এখন রেঞ্জ লিস্ট দিন (বাল্ক আকারে):\n"
        "প্রতিটি রেঞ্জ নতুন লাইনে দিন।\n"
        "উদাহরণ:\n"
        "<code>234XXX</code>\n"
        "<code>237XXX</code>\n"
        "<code>225XXX</code></blockquote>\n"
        "✅ সব রেঞ্জ দেওয়া হলে Enter চাপুন।\n"
        "❌ বাতিল করতে CANCEL চাপুন।",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )

async def admin_process_add_custom_service_ranges(update, context):
    text = update.message.text.strip()
    if text == "❌ CANCEL":
        context.user_data["add_custom_service_mode"] = None
        context.user_data.pop("new_service_name", None)
        await update.message.reply_text("❌ বাতিল করা হয়েছে।", reply_markup=custom_services_keyboard())
        return
    service_name = context.user_data.get("new_service_name")
    if not service_name:
        await update.message.reply_text("⚠️ Session expired. আবার চেষ্টা করুন।", reply_markup=custom_services_keyboard())
        context.user_data["add_custom_service_mode"] = None
        return
    ranges = [r.strip().upper() for r in text.split("\n") if r.strip()]
    if not ranges:
        await update.message.reply_text("❌ কোনো রেঞ্জ পাওয়া যায়নি! আবার দিন।", reply_markup=cancel_keyboard())
        return
    service_id = service_name
    if add_custom_service(service_id, service_name, ranges):
        await update.message.reply_text(
            f"✅ <b>CUSTOM SERVICE ADDED!</b>\n"
            f"{format_premium_divider('success')}\n"
            f"<blockquote>🎯 Service: <b>{service_name.upper()}</b>\n"
            f"📶 Ranges: <b>{len(ranges)}</b> টি</blockquote>\n"
            f"✨ GET NUMBER এ 📌 আইকন সহ দেখা যাবে।",
            parse_mode="HTML",
            reply_markup=custom_services_keyboard()
        )
    else:
        await update.message.reply_text("❌ সার্ভিস add করা যায়নি!", reply_markup=custom_services_keyboard())
    context.user_data["add_custom_service_mode"] = None
    context.user_data.pop("new_service_name", None)

async def admin_view_custom_services(update, context):
    services = get_all_custom_services()
    if not services:
        await update.message.reply_text("📋 কোনো কাস্টম সার্ভিস নেই।", reply_markup=custom_services_keyboard())
        return
    text = "📋 <b>CUSTOM SERVICES LIST</b>\n"
    text += f"{format_premium_divider('primary')}\n"
    for svc_id, svc_info in services.items():
        name = svc_info.get("name", svc_id)
        ranges = svc_info.get("ranges", [])
        text += f"\n📌 <b>{name.upper()}</b>\n"
        text += f"   🆔 ID: <code>{svc_id}</code>\n"
        text += f"   📶 Ranges: {len(ranges)} টি\n"
        if ranges[:3]:
            text += f"   📝 Sample: {', '.join(ranges[:3])}\n"
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=custom_services_keyboard())

async def admin_remove_custom_service_start(update, context):
    context.user_data["remove_custom_service_mode"] = True
    services = get_all_custom_services()
    if not services:
        await update.message.reply_text("📋 কোনো কাস্টম সার্ভিস নেই।", reply_markup=custom_services_keyboard())
        context.user_data["remove_custom_service_mode"] = None
        return
    text = "❌ <b>REMOVE CUSTOM SERVICE</b>\n"
    text += f"{format_premium_divider('danger')}\n"
    text += "<blockquote>✨ সার্ভিস ID দিন:\n"
    for svc_id in services.keys():
        text += f"• <code>{svc_id}</code>\n"
    text += "</blockquote>\n"
    text += "❌ বাতিল করতে CANCEL চাপুন।"
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=cancel_keyboard())

async def admin_process_remove_custom_service(update, context):
    text = update.message.text.strip()
    if text == "❌ CANCEL":
        context.user_data["remove_custom_service_mode"] = None
        await update.message.reply_text("❌ বাতিল করা হয়েছে।", reply_markup=custom_services_keyboard())
        return
    service_id = text.lower()
    if remove_custom_service(service_id):
        await update.message.reply_text(
            f"✅ <b>SERVICE REMOVED!</b>\n"
            f"<blockquote>🗑️ <code>{service_id}</code> সফলভাবে মুছে ফেলা হয়েছে।</blockquote>",
            parse_mode="HTML",
            reply_markup=custom_services_keyboard()
        )
    else:
        await update.message.reply_text("❌ এই ID এর সার্ভিস পাওয়া যায়নি!", reply_markup=cancel_keyboard())
    context.user_data["remove_custom_service_mode"] = None

# ══════════════════════════════════════════════════════════════════════════════
# 📞 ADMIN SPECIAL NUMBERS (UPDATED - BULK ADD + CONFIRMATION)
# ══════════════════════════════════════════════════════════════════════════════
async def admin_add_special_numbers_start(update, context):
    context.user_data["add_special_number_mode"] = "service"
    await update.message.reply_text(
        "📞 <b>ADD SPECIAL NUMBERS</b>\n"
        f"{format_premium_divider('primary')}\n"
        "<blockquote>✨ প্রথমে সার্ভিসের নাম দিন:\n"
        "উদাহরণ: <code>facebook</code>, <code>whatsapp</code>, <code>custom</code></blockquote>\n"
        "❌ বাতিল করতে CANCEL চাপুন।",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )

async def admin_process_add_special_service(update, context):
    text = update.message.text.strip()
    if text == "❌ CANCEL":
        context.user_data["add_special_number_mode"] = None
        await update.message.reply_text("❌ বাতিল করা হয়েছে।", reply_markup=add_numbers_keyboard())
        return
    service_name = text.upper()
    context.user_data["special_service_name"] = service_name
    context.user_data["add_special_number_mode"] = "numbers"
    await update.message.reply_text(
        f"📞 <b>SERVICE: {service_name}</b>\n"
        f"{format_premium_divider('success')}\n"
        "<blockquote>✨ এখন নাম্বার লিস্ট দিন (বাল্ক আকারে):\n"
        "প্রতিটি নাম্বার নতুন লাইনে দিন।\n"
        "উদাহরণ:\n"
        "<code>2348012345678</code>\n"
        "<code>237620123456</code>\n"
        "<code>22501234567</code></blockquote>\n"
        f"⏰ প্রতিটি নাম্বার <b>{AUTO_REMOVE_MINUTES} মিনিট</b> পর auto-remove হবে।\n"
        "✅ সব নাম্বার দেওয়া হলে Enter চাপুন।\n"
        "❌ বাতিল করতে CANCEL চাপুন।",
        parse_mode="HTML",
        reply_markup=cancel_keyboard()
    )

async def admin_process_add_special_numbers(update, context):
    text = update.message.text.strip()
    if text == "❌ CANCEL":
        context.user_data["add_special_number_mode"] = None
        context.user_data.pop("special_service_name", None)
        await update.message.reply_text("❌ বাতিল করা হয়েছে।", reply_markup=add_numbers_keyboard())
        return
    service_name = context.user_data.get("special_service_name")
    if not service_name:
        await update.message.reply_text("⚠️ Session expired. আবার চেষ্টা করুন।", reply_markup=add_numbers_keyboard())
        context.user_data["add_special_number_mode"] = None
        return
    # Split by newline or comma to be more robust
    numbers = [n.strip() for n in text.replace(",", "\n").split("\n") if n.strip()]
    if not numbers:
        await update.message.reply_text("❌ কোনো নাম্বার পাওয়া যায়নি! আবার দিন।", reply_markup=cancel_keyboard())
        return
    try:
        added_count = add_bulk_admin_numbers(numbers, ADMIN_ID, service_name)
        
        # Explicit confirmation message
        confirm_text = (
            f"✅ <b>SPECIAL NUMBERS ADDED SUCCESSFULLY!</b>\n"
            f"{format_premium_divider('success')}\n"
            f"<blockquote>📞 Service: <b>{service_name}</b>\n"
            f"✅ Added: <b>{added_count}</b> টি নাম্বার স্টকে যোগ হয়েছে।\n"
            f"⏰ Auto-remove: <b>{AUTO_REMOVE_MINUTES} মিনিট</b> পর</blockquote>\n"
            f"✨ GET NUMBER এ 🎁 SPECIAL NUMBERS সেকশনে দেখা যাবে।"
        )
        await update.message.reply_text(confirm_text, parse_mode="HTML", reply_markup=add_numbers_keyboard())
    except Exception as e:
        await update.message.reply_text(f"❌ Error adding numbers: {str(e)}", reply_markup=add_numbers_keyboard())
    
    context.user_data["add_special_number_mode"] = None
    context.user_data.pop("special_service_name", None)

async def admin_view_special_numbers(update, context):
    admin_nums = load_admin_direct_numbers()
    if not admin_nums:
        await update.message.reply_text("📋 কোনো স্পেশাল নাম্বার নেই।", reply_markup=add_numbers_keyboard())
        return
    available = sum(1 for info in admin_nums.values() if not info.get("used", False))
    used = sum(1 for info in admin_nums.values() if info.get("used", False))
    text = "📋 <b>SPECIAL NUMBERS LIST</b>\n"
    text += f"{format_premium_divider('primary')}\n"
    text += f"<blockquote>✅ Available: <b>{available}</b>\n"
    text += f"🎯 Used: <b>{used}</b>\n"
    text += f"📊 Total: <b>{len(admin_nums)}</b></blockquote>\n"
    for num, info in list(admin_nums.items())[:20]:
        status = "✅" if not info.get("used", False) else "🎯"
        service = info.get("service", "CUSTOM")
        added_at = datetime.fromisoformat(info["added_at"])
        time_diff = (datetime.now() - added_at).total_seconds() / 60
        time_left = max(0, AUTO_REMOVE_MINUTES - time_diff)
        text += f"\n{status} <code>{num}</code>\n"
        text += f"   📱 {service} | ⏰ {int(time_left)}m left\n"
    if len(admin_nums) > 20:
        text += f"\n<i>... এবং আরও {len(admin_nums) - 20}টি নাম্বার</i>"
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=add_numbers_keyboard())

async def admin_remove_all_special_numbers(update, context):
    admin_nums = load_admin_direct_numbers()
    if not admin_nums:
        await update.message.reply_text("📋 কোনো স্পেশাল নাম্বার নেই।", reply_markup=add_numbers_keyboard())
        return
    count = len(admin_nums)
    remove_all_admin_numbers()
    await update.message.reply_text(
        f"✅ <b>ALL NUMBERS REMOVED!</b>\n"
        f"<blockquote>🗑️ <b>{count}</b> টি নাম্বার সফলভাবে মুছে ফেলা হয়েছে।</blockquote>",
        parse_mode="HTML",
        reply_markup=add_numbers_keyboard()
    )

# ══════════════════════════════════════════════════════════════════════════════
# 📨 MESSAGE HANDLERS
# ══════════════════════════════════════════════════════════════════════════════
async def show_main_menu(update, context, uid):
    await context.bot.send_message(chat_id=uid, text="🔹 PLEASE USE THE BUTTONS BELOW:", reply_markup=main_keyboard(uid))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    uid = update.effective_user.id
    text = update.message.text.strip()
    
    # ==================== WITHDRAW FLOW ====================
    if context.user_data.get("withdraw_mode") == "select_method":
        await withdraw_method_selected(update, context)
        return
    if context.user_data.get("withdraw_mode") == "amount":
        await withdraw_amount_received(update, context)
        return
    if context.user_data.get("withdraw_mode") == "number":
        await withdraw_number_received(update, context)
        return
    
    # ==================== ADMIN BALANCE FLOW ====================
    if context.user_data.get("add_balance_mode") and is_admin(uid):
        if context.user_data.get("pending_add_user"):
            await process_add_balance_amount(update, context)
        else:
            await process_add_balance_user(update, context)
        return
    if context.user_data.get("remove_balance_mode") and is_admin(uid):
        if context.user_data.get("pending_remove_user"):
            await process_remove_balance_amount(update, context)
        else:
            await process_remove_balance_user(update, context)
        return
    
    # ==================== ADMIN BAN/UNBAN ====================
    if context.user_data.get("admin_ban_mode") and is_admin(uid):
        await process_ban_user(update, context)
        return
    if context.user_data.get("admin_unban_mode") and is_admin(uid):
        await process_unban_user(update, context)
        return
    
    # ==================== ADMIN CONFIG ====================
    if context.user_data.get("admin_min_withdraw_mode") and is_admin(uid):
        await admin_change_min_withdraw_amount(update, context)
        return
    if context.user_data.get("admin_otp_rate_mode") and is_admin(uid):
        await admin_change_otp_rate_amount(update, context)
        return
    if context.user_data.get("admin_referral_price_mode") and is_admin(uid):
        await admin_change_referral_price_amount(update, context)
        return
    
    # ==================== ADMIN CHANNELS ====================
    if context.user_data.get("add_channel_mode") and is_admin(uid):
        await admin_process_add_channel(update, context)
        return
    if context.user_data.get("remove_channel_mode") and is_admin(uid):
        await admin_process_remove_channel(update, context)
        return
    
    # ==================== ADMIN SEARCH USER FLOW ====================
    if context.user_data.get("admin_search_mode") and is_admin(uid):
        await admin_process_search_user(update, context)
        return
    
    # ==================== ADMIN USER CHECK FLOW ====================
    if context.user_data.get("admin_user_check_mode") and is_admin(uid):
        await admin_process_user_check(update, context)
        return
    
    # ==================== ✅ ADMIN CUSTOM SERVICES FLOW (NEW) ====================
    if context.user_data.get("add_custom_service_mode") == "name" and is_admin(uid):
        await admin_process_add_custom_service_name(update, context)
        return
    if context.user_data.get("add_custom_service_mode") == "ranges" and is_admin(uid):
        await admin_process_add_custom_service_ranges(update, context)
        return
    if context.user_data.get("remove_custom_service_mode") and is_admin(uid):
        await admin_process_remove_custom_service(update, context)
        return
    
    # ==================== ✅ ADMIN SPECIAL NUMBERS FLOW (NEW) ====================
    if context.user_data.get("add_special_number_mode") == "service" and is_admin(uid):
        await admin_process_add_special_service(update, context)
        return
    if context.user_data.get("add_special_number_mode") == "numbers" and is_admin(uid):
        await admin_process_add_special_numbers(update, context)
        return
    
    # ==================== ✅ BROADCAST FLOW (FIXED) ====================
    if context.user_data.get("broadcast_mode") and is_admin(uid):
        if text == "❌ CANCEL":
            context.user_data["broadcast_mode"] = False
            await update.message.reply_text("❌ Broadcast বাতিল।", reply_markup=user_management_keyboard())
            return
        broadcast_text = update.message.text
        user_db = load_data(USER_DATA_FILE)
        sent = 0
        failed = 0
        status_msg = await update.message.reply_text(f"📢 Broadcasting to {len(user_db)} users...")
        for user_id in user_db.keys():
            try:
                await context.bot.send_message(int(user_id), broadcast_text, parse_mode="HTML")
                sent += 1
            except:
                failed += 1
            await asyncio.sleep(0.05)
        context.user_data["broadcast_mode"] = False
        await status_msg.edit_text(
            f"✅ <b>BROADCAST COMPLETE</b>\n"
            f"<blockquote>📤 Sent: {sent}\n"
            f"❌ Failed: {failed}\n"
            f"👥 Total: {len(user_db)}</blockquote>",
            parse_mode="HTML",
            reply_markup=user_management_keyboard()
        )
        return
    
    # ==================== CUSTOM RANGE ====================
    if context.user_data.get("mode") == "custom_range":
        context.user_data["mode"] = None
        range_text = text.strip().upper()
        if not re.search(r'\d', range_text):
            await update.message.reply_text(
                "❌ <b>INVALID RANGE!</b>\n"
                "<blockquote>সঠিক উদাহরণ: <code>234XXX</code> বা <code>26134</code></blockquote>",
                parse_mode="HTML",
                reply_markup=main_keyboard(uid)
            )
            return
        await request_queue.put({
            'type': 'process_numbers',
            'update': update,
            'context': context,
            'range_text': range_text,
            'count': 1,
            'service': 'CUSTOM'
        })
        return
    
    # ==================== BAN CHECK ====================
    if not is_admin(uid) and is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return
    
    # ==================== ✅ SELECTIVE CANCEL (FIXED) ====================
    if text == "❌ CANCEL":
        keys_to_remove = [
            "add_balance_mode", "remove_balance_mode", "pending_add_user",
            "pending_remove_user", "admin_ban_mode", "admin_unban_mode",
            "admin_min_withdraw_mode", "admin_otp_rate_mode",
            "admin_referral_price_mode", "add_channel_mode",
            "remove_channel_mode", "admin_search_mode",
            "admin_user_check_mode", "broadcast_mode",
            "withdraw_mode", "withdraw_method", "withdraw_amount",
            "temp_withdraw", "mode", "add_custom_service_mode",
            "remove_custom_service_mode", "new_service_name",
            "add_special_number_mode", "special_service_name"
        ]
        for key in keys_to_remove:
            context.user_data.pop(key, None)
        await update.message.reply_text("❌ CANCELLED", reply_markup=main_keyboard(uid))
        return
    
    # ==================== USER MENU BUTTONS ====================
    if text == "🌐 RANGE":
        await update.message.reply_text(
            "🌐 **RANGE GROUP**\n"
            "📌 গ্রুপে জয়েন করে রেঞ্জ কপি করুন।",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 JOIN", url=RANGE_GROUP_LINK)],
                [InlineKeyboardButton("⚙️ CUSTOM RANGE", callback_data="custom_range")]
            ])
        )
        return
    if text == "⚡ 2FA":
        await get_2fa_code(update, context)
        return
    if text == "📜 HISTORY":
        await show_history_menu(update, context)
        return
    if text == "🎁 REFER":
        stats = get_referral_stats(uid)
        bot_username = context.bot.username
        ref_link = f"https://t.me/{bot_username}?start={uid}"
        current_referral_price = get_referral_price()
        text_msg = (
            f"🎁 <b>REFER & EARN</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<blockquote>🔗 আপনার লিংক:\n"
            f"<code>{ref_link}</code></blockquote>\n"
            f"<blockquote>💵 প্রতি রেফারে: <b>{current_referral_price:.2f} BDT</b>\n"
            f"👥 মোট রেফার: <b>{stats['count']}</b>\n"
            f"💰 মোট আয়: <b>{stats['earned']:.2f} BDT</b></blockquote>\n"
            f"✨ বন্ধুদের এই লিংক পাঠান!"
        )
        await update.message.reply_text(
            text_msg,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 Copy Link", callback_data=f"copy_referral_{uid}")],
                [InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]
            ])
        )
        return
    if text == "👤 PROFILE":
        user_data = get_user(uid)
        stats = get_user_stats(uid)
        user = update.effective_user
        profile_text = (
            f"👤 <b>YOUR PROFILE</b>\n"
            f"<blockquote>🏷️ NAME: <b>{html.escape(user.full_name)}</b></blockquote>\n"
            f"<blockquote>🆔 USERNAME: @{html.escape(user.username or 'No username')}</blockquote>\n"
            f"<blockquote>🗝️ TELEGRAM ID: <code>{uid}</code></blockquote>\n"
            f"<blockquote>💵 BALANCE: <b>{format_balance(user_data.get('balance', 0))} BDT</b></blockquote>\n"
            f"✨ <b>TODAY</b>\n"
            f"<blockquote>📱 NUMBERS: {stats['today_numbers']}\n"
            f"🔑 OTPS: {stats['today_otps']}</blockquote>\n"
            f"🔥 <b>LAST 7 DAYS</b>\n"
            f"<blockquote>📱 NUMBERS: {stats['last7d_numbers']}\n"
            f"🔑 OTPS: {stats['last7d_otps']}</blockquote>\n"
            f"🌐 <b>ALL TIME</b>\n"
            f"<blockquote>📱 NUMBERS: {stats['total_numbers']}\n"
            f"🔑 OTPS: {stats['total_otps']}</blockquote>\n"
            f"✅ <b>উইথড্র সম্পূর্ণ ফ্রি! কোন চার্জ নেই</b>"
        )
        await update.message.reply_text(profile_text, parse_mode="HTML")
        return
    if text == "💰 BALANCE":
        balance = get_user(uid)['balance']
        await update.message.reply_text(
            f"💰 <b>YOUR CURRENT BALANCE</b>\n"
            f"<blockquote>💵 TOTAL: <b>{format_balance(balance)} BDT</b></blockquote>\n"
            f"✅ <b>উইথড্র সম্পূর্ণ ফ্রি! কোন চার্জ নেই</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💸 WITHDRAW", callback_data="withdraw_start")]])
        )
        return
    if text == "📞 GET NUMBER":
        await show_app_selection(update, context)
        return
    if text == "📊 TRAFFIC":
        await traffic_command(update, context)
        return
    if context.user_data.get("mode") == "get_2fa":
        await process_2fa_key(update, context)
        return
    if text == "💬 SUPPORT":
        await update.message.reply_text(
            "💬 SUPPORT 🎧\n"
            "CLICK THE BUTTON BELOW TO CONTACT SUPPORT 📩",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 SUPPORT", url=SUPPORT_LINK)],
                [InlineKeyboardButton("👨‍💻 DEVELOPER BY", url=DEVELOPER_LINK)]
            ]),
            parse_mode="Markdown"
        )
        return
    
    # ==================== ADMIN PANEL NAVIGATION ====================
    if text == "⚙️ ADMIN PANEL ⚙️" and is_admin(uid):
        context.user_data["admin_mode"] = "main"
        await update.message.reply_text(
            "⌬━━━━━━━━━━━━━━━━━━━━⌬\n"
            "WELCOME ADMIN PANEL\n"
            "⌬━━━━━━━━━━━━━━━━━━━━⌬",
            reply_markup=admin_main_keyboard()
        )
        return
    if text == "🔙 BACK TO MAIN" and context.user_data.get("admin_mode"):
        context.user_data.clear()
        await update.message.reply_text("🔙 Back to main menu.", reply_markup=main_keyboard(uid))
        return
    
    # ==================== ADMIN MAIN BUTTONS ====================
    if text == "👥 USERS" and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        context.user_data["user_management_mode"] = "main"
        await update.message.reply_text("👥 <b>USER MANAGEMENT</b>", parse_mode="HTML", reply_markup=user_management_keyboard())
        return
    if text == "⚙️ CONFIG" and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        context.user_data["system_config_mode"] = "main"
        await update.message.reply_text("⚙️ <b>SYSTEM CONFIGURATION</b>", parse_mode="HTML", reply_markup=system_config_keyboard())
        return
    if text == "🔗 CHANNELS" and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        context.user_data["required_channels_mode"] = "main"
        await update.message.reply_text("🔗 <b>CHANNELS MANAGEMENT</b>", parse_mode="HTML", reply_markup=required_channels_keyboard())
        return
    
    # ==================== ✅ FIX: NUMBERS & SERVICES - SET MODE PROPERLY ====================
    if text == "📞 NUMBERS" and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        context.user_data["numbers_management_mode"] = True
        context.user_data.pop("services_management_mode", None)  # Clear other mode
        await update.message.reply_text("📞 <b>SPECIAL NUMBERS MANAGEMENT</b>", parse_mode="HTML", reply_markup=add_numbers_keyboard())
        return
    if text == "🎯 SERVICES" and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        context.user_data["services_management_mode"] = True
        context.user_data.pop("numbers_management_mode", None)  # Clear other mode
        await update.message.reply_text("🎯 <b>CUSTOM SERVICES MANAGEMENT</b>", parse_mode="HTML", reply_markup=custom_services_keyboard())
        return
    
    if text == "💸 WITHDRAW" and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        wr = load_withdraw_requests()
        pending = {k: v for k, v in wr.items() if v.get("status") == "pending"}
        if not pending:
            await update.message.reply_text("💸 <b>কোনো পেন্ডিং উইথড্র নেই!</b>\n"
                                            "✨ সব উইথড্র প্রসেস করা হয়েছে।", parse_mode="HTML", reply_markup=admin_main_keyboard())
            return
        text_msg = f"💸 <b>PENDING WITHDRAWALS</b> ({len(pending)})\n"
        text_msg += f"━━━━━━━━━━━━━━━━━━━━\n"
        buttons = []
        for pid, data in list(pending.items())[:10]:
            text_msg += f"\n🆔 <code>{pid[:10]}...</code>\n"
            text_msg += f"👤 <code>{data['user_id']}</code> | 💰 {data['amount']:.2f} BDT | 📱 {data['method']}\n"
            text_msg += f"📞 <code>{data['number']}</code>\n"
            buttons.append([InlineKeyboardButton("❌ REJECT", callback_data=f"admin_reject_{pid}"), InlineKeyboardButton("✅ APPROVE", callback_data=f"admin_approve_{pid}")])
        buttons.append([InlineKeyboardButton("🔙 BACK", callback_data="back_to_admin_panel")])
        await update.message.reply_text(text_msg, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))
        return
    if text == "🔍 SEARCH USER" and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        await admin_search_user_start(update, context)
        return
    if text == "📊 TRAFFIC CONTROL" and is_admin(uid):
        await admin_traffic_control(update, context)
        return
    if text == "📊 ANALYTICS" and context.user_data.get("admin_mode") == "main" and is_admin(uid):
        t_n, t_o, s_n, s_o, tot_n, tot_o = get_global_system_stats()
        user_db = load_data(USER_DATA_FILE)
        total_users = len(user_db)
        total_balance = sum(v.get("balance", 0) for v in user_db.values())
        banned = load_banned_users()
        text_msg = (
            f"📊 <b>SYSTEM ANALYTICS</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👥 <b>USERS:</b>\n"
            f"<blockquote>📈 Total: {total_users}\n"
            f"⛔ Banned: {len(banned)}\n"
            f"💰 Total Balance: {total_balance:.2f} BDT</blockquote>\n"
            f"✨ <b>TODAY:</b>\n"
            f"<blockquote>📱 Numbers: {t_n}\n"
            f"🔑 OTPs: {t_o}</blockquote>\n"
            f"🔥 <b>LAST 7 DAYS:</b>\n"
            f"<blockquote>📱 Numbers: {s_n}\n"
            f"🔑 OTPs: {s_o}</blockquote>\n"
            f"🌐 <b>ALL TIME:</b>\n"
            f"<blockquote>📱 Numbers: {tot_n}\n"
            f"🔑 OTPs: {tot_o}</blockquote>"
        )
        await update.message.reply_text(text_msg, parse_mode="HTML", reply_markup=admin_main_keyboard())
        return
    
    # ==================== USER MANAGEMENT SUB-MENU BUTTONS ====================
    if context.user_data.get("user_management_mode") and is_admin(uid):
        if text == "📢 BROADCAST":
            await update.message.reply_text(
                "📢 <b>BROADCAST</b>\n"
                "<blockquote>✨ সব ইউজারদের মেসেজ পাঠান।\n"
                "📝 মেসেজ লিখে পাঠান:</blockquote>\n"
                "❌ বাতিল করতে CANCEL চাপুন।",
                parse_mode="HTML",
                reply_markup=cancel_keyboard()
            )
            context.user_data["broadcast_mode"] = True
            return
        if text == "🆔 ALL IDs":
            await admin_show_all_users(update, context)
            return
        if text == "📜 BAN LIST":
            await show_banned_users_list(update, context)
            return
        if text == "💰 BALANCES":
            await admin_show_all_balances(update, context)
            return
        if text == "👥 USER LIST":
            await admin_show_all_users(update, context)
            return
        if text == "🔍 SEARCH":
            await admin_search_user_start(update, context)
            return
        if text == "🔙 BACK":
            context.user_data["user_management_mode"] = None
            await update.message.reply_text("⚙️ ADMIN PANEL", reply_markup=admin_main_keyboard())
            return
    
    # ==================== SYSTEM CONFIG SUB-MENU BUTTONS ====================
    if context.user_data.get("system_config_mode") and is_admin(uid):
        if text == "📈 STATUS":
            await admin_status_view(update, context)
            return
        if text == "👤 USER CHECK":
            await admin_user_check_start(update, context)
            return
        if text == "⛔ BAN":
            await admin_ban_user_start(update, context)
            return
        if text == "🔓 UNBAN":
            await admin_unban_user_start(update, context)
            return
        if text == "➖ REMOVE":
            await admin_remove_balance_start(update, context)
            return
        if text == "➕ ADD":
            await admin_add_balance_start(update, context)
            return
        if text == "⚙️ MIN WITHDRAW":
            await admin_change_min_withdraw_start(update, context)
            return
        if text == "💲 OTP PRICE":
            await admin_change_otp_rate_start(update, context)
            return
        if text == "💳 PAYMENTS":
            await admin_toggle_payment_methods(update, context)
            return
        if text == "🎁 REFER PRICE":
            await admin_change_referral_price_start(update, context)
            return
        if text == "🔙 BACK":
            context.user_data["system_config_mode"] = None
            await update.message.reply_text("⚙️ ADMIN PANEL", reply_markup=admin_main_keyboard())
            return
    
    # ==================== REQUIRED CHANNELS SUB-MENU BUTTONS ====================
    if context.user_data.get("required_channels_mode") and is_admin(uid):
        if text == "➕ ADD":
            await admin_add_channel_start(update, context)
            return
        if text == "❌ REMOVE":
            await admin_remove_channel_start(update, context)
            return
        if text == "📋 LIST":
            await admin_list_channels(update, context)
            return
        if text == "🔙 BACK":
            context.user_data["required_channels_mode"] = None
            await update.message.reply_text("⚙️ ADMIN PANEL", reply_markup=admin_main_keyboard())
            return
    
    # ==================== ✅ CUSTOM SERVICES SUB-MENU BUTTONS (FIXED - MODE CHECK) ====================
    if text == "➕ ADD" and context.user_data.get("services_management_mode") and is_admin(uid):
        await admin_add_custom_service_start(update, context)
        return
    if text == "📋 VIEW" and context.user_data.get("services_management_mode") and is_admin(uid):
        await admin_view_custom_services(update, context)
        return
    if text == "❌ REMOVE" and context.user_data.get("services_management_mode") and is_admin(uid):
        await admin_remove_custom_service_start(update, context)
        return
    if text == "🔙 BACK" and context.user_data.get("services_management_mode"):
        context.user_data["services_management_mode"] = None
        await update.message.reply_text("⚙️ ADMIN PANEL", reply_markup=admin_main_keyboard())
        return
    
    # ==================== ✅ SPECIAL NUMBERS SUB-MENU BUTTONS (FIXED - MODE CHECK) ====================
    if text == "➕ ADD BULK" and context.user_data.get("numbers_management_mode") and is_admin(uid):
        await admin_add_special_numbers_start(update, context)
        return
    if text == "📋 VIEW" and context.user_data.get("numbers_management_mode") and is_admin(uid):
        admin_nums = load_admin_direct_numbers()
        if admin_nums:
            await admin_view_special_numbers(update, context)
        else:
            await update.message.reply_text("📋 কোনো স্পেশাল নাম্বার নেই।", reply_markup=add_numbers_keyboard())
        return
    if text == "🗑️ REMOVE ALL" and context.user_data.get("numbers_management_mode") and is_admin(uid):
        admin_nums = load_admin_direct_numbers()
        if admin_nums:
            await admin_remove_all_special_numbers(update, context)
        else:
            await update.message.reply_text("📋 কোনো স্পেশাল নাম্বার নেই।", reply_markup=add_numbers_keyboard())
        return
    if text == "🔙 BACK" and context.user_data.get("numbers_management_mode"):
        context.user_data["numbers_management_mode"] = None
        await update.message.reply_text("⚙️ ADMIN PANEL", reply_markup=admin_main_keyboard())
        return
    
    # ==================== DEFAULT FALLBACK ====================
    await update.message.reply_text(
        "🔹 PLEASE USE THE BUTTONS BELOW:",
        reply_markup=main_keyboard(uid)
    )

# ══════════════════════════════════════════════════════════════════════════════
# 🚀 START & CALLBACK HANDLERS
# ══════════════════════════════════════════════════════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    uid_str = str(uid)
    existing_data = load_data(USER_DATA_FILE)
    is_new_user = uid_str not in existing_data
    if is_new_user:
        get_user(uid)
    args = context.args
    if args:
        param = args[0]
        if is_range_request(param):
            await request_queue.put({
                'type': 'auto_number',
                'update': update,
                'context': context,
                'range_text': param
            })
            return
        elif is_referral_request(param):
            try:
                referrer_id = int(param)
                if referrer_id != uid and str(referrer_id) in existing_data:
                    if add_referral(referrer_id, uid):
                        referral_bonus = get_referral_price()
                        if referral_bonus > 0:
                            await update_db_balance(referrer_id, referral_bonus)
                            try:
                                await context.bot.send_message(
                                    referrer_id,
                                    f"🎉 <b>REFER BONUS!</b>\n"
                                    f"<blockquote>✅ নতুন ইউজার জয়েন করেছে।\n"
                                    f"💰 বোনাস: <b>{referral_bonus:.2f} BDT</b></blockquote>",
                                    parse_mode="HTML"
                                )
                            except Exception:
                                pass
                        user_data = get_user(uid)
                        user_data["referred_by"] = referrer_id
                        save_data(existing_data)
            except Exception as e:
                print(f"Referral error: {e}")
    context.user_data.clear()
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode="HTML")
    await update.message.reply_text("🔹 PLEASE USE THE BUTTONS BELOW:", reply_markup=main_keyboard(uid))

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    data = query.data
    await query.answer()
    
    # ==================== NOOP CALLBACK ====================
    if data == "noop":
        return
    if not is_admin(uid) and is_user_banned(uid):
        await query.edit_message_text("🚫 YOU ARE BANNED 🚫")
        return
    
    # ==================== ✅ ADMIN USER ACTION CALLBACKS (FIXED - CRITICAL) ====================
    if data.startswith("admin_add_bal_"):
        target_uid = data.replace("admin_add_bal_", "")
        if not is_admin(uid):
            await query.answer("🚫 UNAUTHORIZED!", show_alert=True)
            return
        context.user_data["add_balance_mode"] = True
        context.user_data["pending_add_user"] = int(target_uid)
        await query.message.reply_text(
            f"💵 <b>ADD BALANCE</b>\n"
            f"<blockquote>🆔 User: <code>{target_uid}</code>\n"
            f"💰 Amount পাঠান (শুধু সংখ্যা):</blockquote>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return
    if data.startswith("admin_rem_bal_"):
        target_uid = data.replace("admin_rem_bal_", "")
        if not is_admin(uid):
            await query.answer("🚫 UNAUTHORIZED!", show_alert=True)
            return
        context.user_data["remove_balance_mode"] = True
        context.user_data["pending_remove_user"] = int(target_uid)
        await query.message.reply_text(
            f"💸 <b>REMOVE BALANCE</b>\n"
            f"<blockquote>🆔 User: <code>{target_uid}</code>\n"
            f"💰 Amount পাঠান (শুধু সংখ্যা):</blockquote>",
            parse_mode="HTML",
            reply_markup=cancel_keyboard()
        )
        return
    if data.startswith("admin_ban_"):
        target_uid = data.replace("admin_ban_", "")
        if not is_admin(uid):
            await query.answer("🚫 UNAUTHORIZED!", show_alert=True)
            return
        if is_user_banned(int(target_uid)):
            await query.answer("⚠️ User already banned!", show_alert=True)
            return
        ban_user(int(target_uid))
        try:
            await context.bot.send_message(int(target_uid), "🚫 YOU HAVE BEEN BANNED!")
        except:
            pass
        await query.answer(f"✅ User {target_uid} BANNED!", show_alert=True)
        return
    if data.startswith("admin_unban_"):
        target_uid = data.replace("admin_unban_", "")
        if not is_admin(uid):
            await query.answer("🚫 UNAUTHORIZED!", show_alert=True)
            return
        if not is_user_banned(int(target_uid)):
            await query.answer("⚠️ User is not banned!", show_alert=True)
            return
        unban_user(int(target_uid))
        try:
            await context.bot.send_message(int(target_uid), "✅ YOU HAVE BEEN UNBANNED!")
        except:
            pass
        await query.answer(f"✅ User {target_uid} UNBANNED!", show_alert=True)
        return
    
    # ==================== TRAFFIC CALLBACKS ====================
    if data == "traffic_home":
        text = render_traffic_dashboard()
        keyboard = build_traffic_keyboard()
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
        return
    if data == "traffic_refresh":
        await query.answer("🔄 Refreshing traffic dashboard...")
        text = render_traffic_dashboard()
        keyboard = build_traffic_keyboard()
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
        return
    if data.startswith("traffic_svc_"):
        service_name = data.replace("traffic_svc_", "")
        if service_name not in local_traffic_stats:
            await query.answer("❌ No traffic data for this service", show_alert=True)
            return
        countries = local_traffic_stats[service_name]
        buttons = []
        sorted_countries = sorted(countries.items(), key=lambda x: x[1]["success"], reverse=True)
        for country, data_item in sorted_countries[:10]:
            flag_emoji = get_premium_flag_emoji(country)
            buttons.append([InlineKeyboardButton(f"{flag_emoji} {country} ({data_item['success']:,})", callback_data=f"traffic_ctr_{service_name}_{country}")])
        buttons.append([InlineKeyboardButton("🔙 BACK", callback_data="traffic_home")])
        text = f"{get_app_premium_emoji(service_name)} <b>{service_name.upper()}</b>\n"
        text += f"Select a country to view ranges:"
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))
        return
    if data.startswith("traffic_ctr_"):
        parts = data.replace("traffic_ctr_", "").split("_")
        if len(parts) >= 2:
            service_name = parts[0]
            country_code = parts[1]
            if service_name in local_traffic_stats and country_code in local_traffic_stats[service_name]:
                data_item = local_traffic_stats[service_name][country_code]
                ranges = data_item.get("ranges", {})
                sorted_ranges = sorted(ranges.items(), key=lambda x: x[1], reverse=True)
                buttons = []
                for range_val, hits in sorted_ranges[:10]:
                    buttons.append([InlineKeyboardButton(f"📋 {range_val} ({hits})", callback_data=f"copy_range_{range_val}")])
                buttons.append([InlineKeyboardButton("🔙 BACK", callback_data=f"traffic_svc_{service_name}")])
                flag_emoji = get_premium_flag_emoji(country_code)
                text = f"{get_app_premium_emoji(service_name)} {flag_emoji} <b>{service_name.upper()} - {country_code}</b>\n"
                text += f"Total Hits: <code>{data_item['success']:,}</code>\n"
                text += f"Top Ranges:"
                await query.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))
                return
    if data.startswith("copy_range_"):
        range_val = data.replace("copy_range_", "")
        await query.message.reply_text(
            f"📶 <b>RANGE TO COPY</b>\n"
            f"<blockquote><code>{range_val}</code></blockquote>\n"
            f"✨ <b>উপরের রেঞ্জে ট্যাপ করে কপি করুন!</b>",
            parse_mode="HTML"
        )
        return
    
    # ==================== ADMIN TRAFFIC CALLBACKS ====================
    if data == "admin_toggle_auto_range":
        if not is_admin(uid):
            await query.answer("🚫 UNAUTHORIZED!", show_alert=True)
            return
        new_state = toggle_auto_range_mode()
        await query.answer(f"✅ Auto-Range Mode {'ENABLED' if new_state else 'DISABLED'}!")
        stats, last_updated = get_traffic_stats()
        auto_mode = get_auto_range_mode()
        text = (
            f"{get_premium_custom_emoji('dashboard')} <b>ADMIN TRAFFIC CONTROL</b>\n"
            f"{format_premium_divider('primary')}\n"
            f"{get_premium_custom_emoji('rocket')} <b>Auto-Range Mode:</b> <code>{'ENABLED ✅' if auto_mode else 'DISABLED ❌'}</code>\n"
            f"{get_premium_custom_emoji('world')} <b>Total Services:</b> <code>{len(stats)}</code>\n"
            f"{get_premium_custom_emoji('time')} <b>Last Updated:</b> <code>{last_updated.strftime('%I:%M %p') if last_updated else 'N/A'}</code>\n"
            f"{format_premium_divider('success')}\n"
            f"<i>নিচের বাটন থেকে ট্রাফিক কন্ট্রোল করুন:</i>"
        )
        buttons = [
            [InlineKeyboardButton(f"{'🔴 DISABLE' if auto_mode else '🟢 ENABLE'} Auto-Range", callback_data="admin_toggle_auto_range")],
            [InlineKeyboardButton("📊 View Full Dashboard", callback_data="traffic_home"), InlineKeyboardButton("🔄 Refresh Stats", callback_data="admin_refresh_traffic")],
            [InlineKeyboardButton("🔙 BACK", callback_data="back_to_admin_panel")]
        ]
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))
        return
    if data == "admin_refresh_traffic":
        await query.answer("🔄 Traffic stats refreshed!")
        await query.message.edit_text(
            f"{get_premium_custom_emoji('done')} <b>Traffic Stats Refreshed!</b>\n"
            f"✨ সর্বশেষ ডাটা এখন আপডেটেড।",
            parse_mode="HTML",
            reply_markup=query.message.reply_markup
        )
        return
    
    # ==================== FORCE JOIN CALLBACK ====================
    if data == "check_force_join":
        await query.answer("🔍 Checking channel membership...")
        is_joined = await check_force_join(uid, message=None, context=context)
        if is_joined:
            await query.message.delete()
            await context.bot.send_message(
                uid,
                f"{get_premium_custom_emoji('done')} <b>VERIFICATION SUCCESSFUL!</b>\n"
                f"✨ আপনি এখন বটের সকল সার্ভিস ব্যবহার করতে পারবেন।",
                parse_mode="HTML",
                reply_markup=main_keyboard(uid)
            )
        else:
            await query.message.edit_text(
                f"{get_premium_custom_emoji('error')} <b>VERIFICATION FAILED!</b>\n"
                f"⚠️ আপনি এখনও সকল চ্যানেলে জয়েন করেননি।\n"
                f"অনুগ্রহ করে সকল চ্যানেলে জয়েন করে আবার চেষ্টা করুন।",
                parse_mode="HTML"
            )
        return
    
    # ==================== ✅ SPECIAL NUMBERS HANDLERS (UPDATED - NEW FLOW) ====================
    if data == "special_numbers":
        await assign_special_number(query, context, uid)
        return
    if data == "special_refresh_stock":
        available = get_available_admin_numbers_count()
        await query.message.edit_text(
            f"📊 <b>SPECIAL NUMBERS STOCK</b>\n"
            f"<blockquote>✅ Available: <b>{available}</b> টি নাম্বার</blockquote>\n"
            f"✨ নিচের বাটনে ক্লিক করে নাম্বার নিন:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎁 GET NUMBER", callback_data="special_numbers")],
                [InlineKeyboardButton("🔙 BACK", callback_data="back_services")]
            ])
        )
        return
    if data.startswith("special_country_"):
        country_prefix = data.replace("special_country_", "")
        # Directly allocate one number instead of showing list
        await allocate_one_special_number_by_country(query, context, uid, country_prefix)
        return
    if data.startswith("special_new_num_"):
        country_prefix = data.replace("special_new_num_", "")
        # Allocate another new number from the same country
        await allocate_one_special_number_by_country(query, context, uid, country_prefix)
        return
    if data.startswith("special_num_"):
        # This is kept for backward compatibility if needed
        number = data.replace("special_num_", "")
        await assign_specific_special_number(query, context, uid, number)
        return
    
    # ==================== COPY BUTTON HANDLERS ====================
    if data.startswith("copy_number_"):
        number = data.replace("copy_number_", "")
        await query.message.reply_text(
            f"📞 <b>NUMBER TO COPY</b>\n"
            f"<blockquote><code>{number}</code></blockquote>\n"
            f"✨ <b>উপরের নাম্বারে ট্যাপ করে কপি করুন!</b>",
            parse_mode="HTML"
        )
        return
    if data.startswith("copy_otp_"):
        otp = data.replace("copy_otp_", "")
        await query.message.reply_text(
            f"🔑 <b>OTP TO COPY</b>\n"
            f"<blockquote><code>{otp}</code></blockquote>\n"
            f"✨ <b>উপরের OTP ট্যাপ করে কপি করুন!</b>",
            parse_mode="HTML"
        )
        return
    
    # ==================== SERVICE SELECTION ====================
    if data.startswith("svc_"):
        svc_key = data[4:]
        services = await fetch_services_cached()
        if svc_key not in services or not services[svc_key]:
            await query.answer("এই সার্ভিস বর্তমানে উপলব্ধ নেই।", show_alert=True)
            return
        svc_data = services[svc_key]
        is_custom = svc_key.startswith("custom_")
        if is_custom:
            display_name = svc_data.get("display_name", "Custom").replace("🎯 ", "")
            ranges = svc_data.get("ranges", [])
            platform = svc_data.get("platform", "custom")
            context.user_data["la_service"] = display_name
            context.user_data["la_ranges"] = ranges
            await query.message.edit_text(
                f"📌✨ {display_name.upper()} ✨📌\n"
                f"<blockquote>📱 Platform: <b>{platform}</b></blockquote>\n"
                f"<blockquote>🌍 হট দেশগুলো (🔥) আগে দেখানো হয়েছে:</blockquote>",
                parse_mode="HTML",
                reply_markup=_build_countries_keyboard(ranges, svc_key)
            )
        else:
            ranges = svc_data
            context.user_data["la_service"] = svc_key
            context.user_data["la_ranges"] = ranges
            await query.message.edit_text(
                f"📡✨ {svc_key.upper()} - AVAILABLE COUNTRIES ✨📡\n"
                f"<blockquote>📱 Service: <b>{html.escape(svc_key)}</b></blockquote>\n"
                f"<blockquote>🌍 হট দেশগুলো (🔥) আগে দেখানো হয়েছে:</blockquote>",
                parse_mode="HTML",
                reply_markup=_build_countries_keyboard(ranges, svc_key)
            )
        return
    
    # ==================== COUNTRY SELECTION ====================
    if data.startswith("country_"):
        parts = data.split("_")
        if len(parts) < 3:
            await query.answer("Invalid country data.", show_alert=True)
            return
        country_prefix = parts[1]
        service = parts[2]
        ranges = context.user_data.get("la_ranges", [])
        await query.message.edit_text(
            f"🌍✨ AVAILABLE RANGES ✨🌍\n"
            f"<blockquote>📶 এই দেশের সক্রিয় রেঞ্জগুলো নিচে দেখুন:</blockquote>",
            parse_mode="HTML",
            reply_markup=_build_ranges_keyboard(ranges, country_prefix, service)
        )
        return
    
    # ==================== RANGE SELECTION ====================
    if data.startswith("range_"):
        parts = data.split("_")
        if len(parts) < 3:
            await query.answer("Invalid range data.", show_alert=True)
            return
        rid = parts[1]
        service = parts[2]
        await fast_allocate_number(query, context, rid, service, rid + "XXX")
        return
    if data == "custom_range":
        context.user_data["mode"] = "custom_range"
        await query.message.edit_text("⚙️ <b>CUSTOM RANGE</b>\n"
                                      "<blockquote>📶 আপনার কাস্টম range টাইপ করুন।\n"
                                      "উদাহরণ: <code>234XXX</code> বা <code>26134</code></blockquote>\n"
                                      "<blockquote>⌨️ নিচে range লিখে Send করুন:</blockquote>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ BACK", callback_data="back_services")]]))
        return
    if data in ["back_services", "back_to_services"]:
        services = await fetch_services_cached()
        if not services:
            await query.edit_message_text("❌ সার্ভিস লোড করা যায়নি।")
            return
        await query.edit_message_text("📡✨ 𝗦𝗘𝗟𝗘𝗖𝗧 𝗬𝗢𝗨𝗥 𝗦𝗘𝗥𝗩𝗜𝗖𝗘 ✨📡\n"
                                      "<blockquote>📱 নিচ থেকে একটি <b>Service</b> সিলেক্ট করুন:</blockquote>", parse_mode="HTML", reply_markup=_build_services_keyboard(services))
        return
    if data.startswith("same_range_"):
        parts = data.split("_")
        if len(parts) < 3:
            await query.answer("Invalid same range data.", show_alert=True)
            return
        rid, service = parts[2], parts[3] if len(parts) > 3 else "CUSTOM"
        try:
            await query.message.edit_reply_markup(reply_markup=None)
            num, country = await get_number_from_api(rid)
            if not num:
                await query.message.reply_text("❌ <b>এই রেঞ্জে বর্তমানে কোনো নম্বর নেই!</b>\n"
                                               "<blockquote>⚠️ দয়া করে অন্য রেঞ্জ নির্বাচন করুন বা পরে আবার চেষ্টা করুন।</blockquote>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ BACK TO SERVICES", callback_data="back_services")]]))
                return
            clean_num = normalize_number(num)
            active_numbers[clean_num] = {"uid": uid, "range": rid, "timestamp": datetime.now(), "service": service}
            add_number_taken(uid, 1)
            flag, cname = get_country_info(clean_num)
            text = (f"{get_premium_emoji('status')} <b>YOUR NEW NUMBER FROM SAME RANGE</b> {get_premium_emoji('status')}\n"
                    f"<blockquote>{get_premium_emoji('country')} COUNTRY: <code>{flag} {cname}</code></blockquote>\n"
                    f"<blockquote>{get_premium_emoji('range')} RANGE: <code>{rid}</code></blockquote>\n"
                    f"<blockquote>{get_premium_emoji('service')} SERVICE: <code>{service.upper()}</code></blockquote>\n"
                    f"<blockquote>{get_premium_emoji('number')} NUMBER: <code>{num}</code></blockquote>\n"
                    f"<b>{get_premium_emoji('time')} SMS STATUS: ⏳ WAITING...</b>")
            await query.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{get_premium_emoji('number')} Copy Number", callback_data=f"copy_number_{num}"),
                 InlineKeyboardButton("🔄 SAME RANGE", callback_data=f"same_range_{rid}_{service}")],
                [InlineKeyboardButton("📢 OTP GROUP", url=OTP_GROUP_URL)],
                [InlineKeyboardButton("◀️ BACK", callback_data="back_to_services")]
            ]))
        except Exception as e:
            await query.message.reply_text(f"❌ Server error: {str(e)[:100]}", reply_markup=main_keyboard(uid))
        return
    
    # ==================== WITHDRAW CALLBACKS ====================
    if data == "withdraw_start":
        balance = get_user(uid)['balance']
        min_with = load_system_config()["min_withdraw"]
        if balance < min_with:
            await query.message.reply_text(f"<blockquote>💵 BALANCE: {format_balance(balance)} BDT\n"
                                           f"📉 MIN WITHDRAW: {min_with} BDT</blockquote>", parse_mode="HTML")
            return
        context.user_data["withdraw_mode"] = "select_method"
        await query.message.reply_text("💳 SELECT YOUR PAYMENT METHOD!", reply_markup=withdraw_method_keyboard())
        return
    if data == "withdraw_confirm":
        await process_withdraw_confirm(update, context)
        return
    if data == "withdraw_cancel":
        await process_withdraw_cancel(update, context)
        return
    if data.startswith("admin_approve_"):
        await admin_approve_withdraw(update, context, data.replace("admin_approve_", ""))
        return
    if data.startswith("admin_reject_"):
        await admin_reject_withdraw(update, context, data.replace("admin_reject_", ""))
        return
    
    # ==================== HISTORY CALLBACKS ====================
    if data == "back_to_history":
        await show_history_menu(update, context)
        return
    if data == "history_otp":
        await show_otp_history(update, context)
        return
    if data == "history_payment":
        await show_payment_history(update, context)
        return
    if data == "history_referral":
        await show_referral_stats(update, context)
        return
    if data.startswith("copy_referral_"):
        user_id = data.replace("copy_referral_", "")
        bot_username = context.bot.username
        link = f"https://t.me/{bot_username}?start={user_id}"
        await query.message.reply_text(
            f"🔗 <b>YOUR REFERRAL LINK</b>\n"
            f"<blockquote><code>{link}</code></blockquote>\n"
            f"✨ <b>উপরের লিংকে ট্যাপ করে কপি করুন!</b>",
            parse_mode="HTML"
        )
        return
    
    # ==================== ADMIN VIEW USER CALLBACKS ====================
    if data.startswith("admin_view_user_"):
        await admin_view_user_details(update, context)
        return
    
    # ==================== ✅ SELECTIVE CLEAR ON BACK TO MAIN (FIXED) ====================
    if data == "back_to_main":
        await query.edit_message_text("🔙 Returning to main menu...")
        await query.message.chat.send_message("🔹 PLEASE USE THE BUTTONS BELOW:", reply_markup=main_keyboard(uid))
        keys_to_remove = [
            "add_balance_mode", "remove_balance_mode", "pending_add_user",
            "pending_remove_user", "admin_ban_mode", "admin_unban_mode",
            "admin_min_withdraw_mode", "admin_otp_rate_mode",
            "admin_referral_price_mode", "add_channel_mode",
            "remove_channel_mode", "admin_search_mode",
            "admin_user_check_mode", "broadcast_mode",
            "withdraw_mode", "withdraw_method", "withdraw_amount",
            "temp_withdraw", "mode", "user_management_mode",
            "system_config_mode", "required_channels_mode",
            "add_custom_service_mode", "remove_custom_service_mode",
            "new_service_name", "add_special_number_mode",
            "special_service_name", "services_management_mode",
            "numbers_management_mode"
        ]
        for key in keys_to_remove:
            context.user_data.pop(key, None)
        return
    if data.startswith("toggle_method_"):
        await handle_toggle_method_callback(update, context)
        return
    if data == "back_to_admin_panel":
        try:
            await query.message.delete()
        except:
            pass
        await query.message.chat.send_message("⚙️ ADMIN PANEL", reply_markup=admin_main_keyboard())
        return

# ══════════════════════════════════════════════════════════════════════════════
# 🎯 MAIN FUNCTION
# ══════════════════════════════════════════════════════════════════════════════
async def post_init(application):
    for _ in range(MAX_WORKERS):
        asyncio.create_task(worker())
    asyncio.create_task(monitor_loop(application))

def main():
    start_periodic_check()
    app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("traffic", traffic_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("🚀 ZEBRA SMS ULTRA BOT STARTED...")
    print(f"👑 Admin ID: {ADMINS[0]}")
    print(f"📢 OTP Group: {OTP_GROUP_ID}")
    print(f"🔗 OTP Group Link: {OTP_GROUP_URL}")
    print(f"🔗 Bot URL: {BOT_URL}")
    print(f"⏰ Auto Remove: {AUTO_REMOVE_MINUTES} minutes")
    print(f"🗄️ MongoDB: {'Connected' if db_mongo_connected else 'Disconnected'}")
    print(f"🌐 Flask Keep-Alive: Running on port 8080")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
