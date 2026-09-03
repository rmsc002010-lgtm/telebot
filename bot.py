import logging
import sqlite3
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8852330034:AAG-VW3qO9EuaPMcf54dtD_fpiNkTOkfKYI"
ADMIN_ID = 1586853120

# ZebraSMS API Configuration
ZEBRASMS_API_KEY = "6U3G3DDZ6GB"
# Standard API URL (ZebraSMS এর আসল কাজ করার জন্য এন্ডপয়েন্ট)
ZEBRASMS_BASE_URL = "https://zebrasms.com/stubs/handler_api.php"
# =======================================================

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Console Dialer Range Mapping (ZebraSMS এর দেশ ও সার্ভিস কোড অনুযায়ী)
RANGE_MAPPING = {
    "1": {"label": "📞 Range: +1 (USA)", "country": "USA", "country_code": "187", "service": "tg"},
    "2": {"label": "📞 Range: +44 (UK)", "country": "United Kingdom", "country_code": "12", "service": "tg"},
    "3": {"label": "📞 Range: +7 (Russia)", "country": "Russia", "country_code": "0", "service": "tg"},
    "4": {"label": "📞 Range: +91 (India)", "country": "India", "country_code": "22", "service": "tg"},
    "5": {"label": "📞 Range: +62 (Indonesia)", "country": "Indonesia", "country_code": "6", "service": "tg"}
}

# ==================== DATABASE SETUP ====================
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT
        )
    """)
    conn.commit()
    conn.close()

def register_user(user_id, username):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

def get_total_users():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

# ==================== ZEBRASMS API FUNCTIONS ====================

def api_get_number(country_code, service_code):
    """ZebraSMS API থেকে নম্বর ফেচ করার কার্যকরী ফাংশন"""
    params = {
        "api_key": ZEBRASMS_API_KEY,
        "action": "getNumber",
        "service": service_code,
        "country": country_code
    }
    try:
        response = requests.get(ZEBRASMS_BASE_URL, params=params, timeout=12)
        res_text = response.text.strip()
        
        # ZebraSMS Standard Format Check
        if "ACCESS_NUMBER" in res_text:
            parts = res_text.split(":")
            return True, {"id": parts[1], "number": parts[2]}
        elif "NO_NUMBERS" in res_text:
            return False, "এই দেশে/রেঞ্জে এখন কোনো নম্বর খালি নেই (NO_NUMBERS)।"
        elif "NO_BALANCE" in res_text:
            return False, "API একাউন্টে ব্যালেন্স শেষ হয়ে গেছে।"
        else:
            # Fallback for JSON Format if API returns JSON
            try:
                data = response.json()
                if "number" in data and "id" in data:
                    return True, {"id": data["id"], "number": data["number"]}
            except Exception:
                pass
            return False, f"Server Response: {res_text}"
            
    except Exception as e:
        return False, str(e)

def api_check_otp(tx_id):
    """ZebraSMS API থেকে OTP চেক করার ফাংশন"""
    params = {
        "api_key": ZEBRASMS_API_KEY,
        "action": "getStatus",
        "id": tx_id
    }
    try:
        response = requests.get(ZEBRASMS_BASE_URL, params=params, timeout=12)
        res_text = response.text.strip()
        
        if "STATUS_OK" in res_text:
            code = res_text.split(":")[1]
            return True, code
        elif "STATUS_WAIT_CODE" in res_text:
            return False, "WAITING"
        elif "STATUS_CANCEL" in res_text:
            return False, "CANCELLED"
        else:
            return False, res_text
    except Exception as e:
        return False, str(e)

# ==================== USER HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user.id, user.username or "No Username")
    
    keyboard = [
        [InlineKeyboardButton("🔢 নম্বর রেঞ্জ নির্বাচন করুন", callback_data="select_range")],
        [InlineKeyboardButton("👨‍💻 সাপোর্ট", url="https://t.me/your_support_username")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_msg = (
        f"👋 **হ্যালো {user.first_name}!**\n\n"
        f"আমাদের **ZebraSMS Console Dialer Bot**-এ স্বাগতম! 📱\n"
        f"নিচের বাটনটি চেপে সরাসরি ওয়েবসাইট থেকে ফ্রিতে নম্বর সংগ্রহ করুন।\n\n"
        f"🆔 **আপনার ID:** `{user.id}`"
    )
    
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id

    if query.data == "select_range":
        keyboard = []
        for key, val in RANGE_MAPPING.items():
            keyboard.append([InlineKeyboardButton(val["label"], callback_data=f"getrange_{key}")])
            
        keyboard.append([InlineKeyboardButton("🔙 প্রধান মেনু", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text("🎯 **কনসোল ডায়ালার থেকে রেঞ্জ সিলেক্ট করুন:**", reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data.startswith("getrange_"):
        range_key = query.data.split("_")[1]
        range_info = RANGE_MAPPING.get(range_key)

        if not range_info:
            await query.message.edit_text("❌ ভুল রেঞ্জ পছন্দ করা হয়েছে।")
            return

        await query.message.edit_text(f"⏳ **{range_info['country']}** - কনসোল থেকে নম্বর খোঁজা হচ্ছে...")

        success, result = api_get_number(country_code=range_info["country_code"], service_code=range_info["service"])

        if success:
            tx_id = result["id"]
            number = result["number"]

            keyboard = [
                [InlineKeyboardButton("📩 OTP কোড রিফ্রেশ করুন", callback_data=f"check_otp_{tx_id}")],
                [InlineKeyboardButton("🔄 অন্য নম্বর নিন", callback_data="select_range")],
                [InlineKeyboardButton("🔙 প্রধান মেনু", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            msg = (
                f"🎉 **নম্বর পাওয়া গেছে!**\n\n"
                f"🌍 **দেশ:** {range_info['country']}\n"
                f"📞 **নম্বর:** `{number}`\n"
                f"🆔 **Transaction ID:** `{tx_id}`\n\n"
                f"💡 অ্যাপে SMS পাঠানোর পর নিচের **'OTP কোড রিফ্রেশ করুন'** বাটনে চাপ দিন।"
            )
            await query.message.edit_text(msg, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            keyboard = [[InlineKeyboardButton("🔄 অন্য দেশ/রেঞ্জ চেষ্টা করুন", callback_data="select_range")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.edit_text(f"❌ **নম্বর পাওয়া যায়নি!**\n\n**কারণ:** `{result}`", reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data.startswith("check_otp_"):
        tx_id = query.data.split("_")[2]
        success, code = api_check_otp(tx_id)

        if success:
            await query.message.reply_text(f"🎉 **আপনার OTP কোড:** `{code}`", parse_mode="Markdown")
        elif code == "WAITING":
            await query.message.reply_text("⏳ কোড আসার অপেক্ষায় আছে... অ্যাপে SMS পাঠানোর ২-৫ সেকেন্ড পর আবার চেষ্টা করুন।")
        else:
            await query.message.reply_text(f"⚠️ স্ট্যাটাস: `{code}`", parse_mode="Markdown")

    elif query.data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("🔢 নম্বর রেঞ্জ নির্বাচন করুন", callback_data="select_range")],
            [InlineKeyboardButton("👨‍💻 সাপোর্ট", url="https://t.me/your_support_username")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        welcome_msg = (
            f"👋 **হ্যালো {query.from_user.first_name}!**\n\n"
            f"🆔 **আপনার ID:** `{user_id}`"
        )
        await query.message.edit_text(welcome_msg, reply_markup=reply_markup, parse_mode="Markdown")

# ==================== ADMIN COMMANDS ====================

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    total = get_total_users()
    admin_msg = (
        f"🛠️ **অ্যাডমিন প্যানেল**\n\n"
        f"📊 **মোট ইউজার:** {total}\n\n"
        f"📢 **ব্রডকাস্ট পাঠাতে:**\n"
        f"`/broadcast আপনার মেসেজ`"
    )
    await update.message.reply_text(admin_msg, parse_mode="Markdown")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("❌ মেসেজ লিখুন। উদাহরণ: `/broadcast সিস্টেম আপডেট হয়েছে`", parse_mode="Markdown")
        return

    msg = " ".join(context.args)
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()

    count = 0
    for u in users:
        try:
            await context.bot.send_message(chat_id=u[0], text=msg)
            count += 1
        except Exception:
            pass

    await update.message.reply_text(f"✅ মোট {count} জন ইউজারকে মেসেজ পাঠানো হয়েছে।")

# ==================== MAIN APPLICATION ====================

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Admin Handlers
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("broadcast", broadcast))

    print("ZebraSMS Bot চালুর জন্য প্রস্তুত...")
    app.run_polling()

if __name__ == "__main__":
    main()
