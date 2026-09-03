import logging
import sqlite3
import random
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

# ZebraSMS Console API Config
ZEBRASMS_API_KEY = "6U3G3DDZ6GB"  # আপনার ZebraSMS API Key
ZEBRASMS_BASE_URL = "https://zebrasms.com/api/v1"
# =======================================================

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Console / Range Mappings (নম্বর রেঞ্জ এবং তার সাথে সংশ্লিষ্ট দেশ ও কোড)
RANGE_MAPPING = {
    "range_1": {"label": "📞 Range: +1 (201) [USA]", "country": "USA", "country_code": "187"},
    "range_2": {"label": "📞 Range: +1 (415) [USA]", "country": "USA", "country_code": "187"},
    "range_3": {"label": "📞 Range: +44 (7700) [UK]", "country": "United Kingdom", "country_code": "12"},
    "range_4": {"label": "📞 Range: +7 (900) [Russia]", "country": "Russia", "country_code": "0"},
    "range_5": {"label": "📞 Range: +91 (9876) [India]", "country": "India", "country_code": "22"},
    "range_6": {"label": "📞 Range: +62 (812) [Indonesia]", "country": "Indonesia", "country_code": "6"}
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

# ==================== ZEBRASMS DIALER / API FUNCTIONS ====================

def get_number_by_range(country_code, service="tg"):
    """ZebraSMS API / Console থেকে নির্দিষ্ট দেশ ও রেঞ্জের নম্বর ফেচ করা"""
    params = {
        "api_key": ZEBRASMS_API_KEY,
        "action": "getNumber",
        "service": service,
        "country": country_code
    }
    try:
        response = requests.get(ZEBRASMS_BASE_URL, params=params, timeout=10)
        res_text = response.text
        if "ACCESS_NUMBER" in res_text:
            parts = res_text.split(":")
            tx_id = parts[1]
            number = parts[2]
            return True, {"id": tx_id, "number": number}
        else:
            return False, res_text
    except Exception as e:
        return False, str(e)

def check_range_otp(tx_id):
    """ZebraSMS Console থেকে OTP চেক করা"""
    params = {
        "api_key": ZEBRASMS_API_KEY,
        "action": "getStatus",
        "id": tx_id
    }
    try:
        response = requests.get(ZEBRASMS_BASE_URL, params=params, timeout=10)
        res_text = response.text
        if "STATUS_OK" in res_text:
            code = res_text.split(":")[1]
            return True, code
        elif "STATUS_WAIT_CODE" in res_text:
            return False, "WAITING"
        else:
            return False, res_text
    except Exception as e:
        return False, str(e)

# ==================== USER HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user.id, user.username or "No Username")
    
    keyboard = [
        [InlineKeyboardButton("🔢 নম্বর রেঞ্জ নির্বাচন করুন (Select Range)", callback_data="select_range")],
        [InlineKeyboardButton("👨‍💻 সাপোর্ট (Support)", url="https://t.me/your_support_username")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_msg = (
        f"👋 **হ্যালো {user.first_name}!**\n\n"
        f"আমাদের **ZebraSMS Console Dialer Bot**-এ স্বাগতম! 📱\n"
        f"আপনি রেঞ্জ সিলেক্ট করলে স্বয়ংক্রিয়ভাবে দেশ এবং কনসোলের সম্পূর্ণ ফ্রি নম্বর চলে আসবে।\n\n"
        f"🆔 **আপনার ID:** `{user.id}`\n\n"
        f"নিচের বাটনে চাপ দিয়ে রেঞ্জ সিলেক্ট করুন 👇"
    )
    
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id

    if query.data == "select_range":
        # ডায়ালারের নম্বর রেঞ্জ বাটনসমূহ
        keyboard = []
        for key, val in RANGE_MAPPING.items():
            keyboard.append([InlineKeyboardButton(val["label"], callback_data=f"getrange_{key}")])
            
        keyboard.append([InlineKeyboardButton("🔙 প্রধান মেনু", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.edit_text("🎯 **কনসোল থেকে আপনার কাঙ্ক্ষিত নম্বর রেঞ্জটি সিলেক্ট করুন:**", reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data.startswith("getrange_"):
        range_key = query.data.split("_")[1]
        range_info = RANGE_MAPPING.get(f"range_{range_key}")

        if not range_info:
            await query.message.edit_text("❌ অকার্যকর রেঞ্জ!")
            return

        await query.message.edit_text(f"⏳ **{range_info['country']}** - কনসোল থেকে নম্বর জেনারেট হচ্ছে...")

        # ZebraSMS API দিয়ে রেঞ্জ অনুযায়ী নম্বর ফেচ করা
        success, result = get_number_by_range(country_code=range_info["country_code"])

        if success:
            tx_id = result["id"]
            number = result["number"]

            keyboard = [
                [InlineKeyboardButton("📩 OTP কোড চেক করুন", callback_data=f"check_otp_{tx_id}")],
                [InlineKeyboardButton("🔄 নতুন নম্বর নিন", callback_data="select_range")],
                [InlineKeyboardButton("🔙 প্রধান মেনু", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            msg = (
                f"🎉 **রেঞ্জ অনুযায়ী নম্বর প্রস্তুত!**\n\n"
                f"🌍 **দেশ:** {range_info['country']}\n"
                f"📞 **নম্বর:** `{number}`\n"
                f"🆔 **Transaction ID:** `{tx_id}`\n\n"
                f"💡 নম্বরটি অ্যাপে বসিয়ে কোড পাঠানোর পর 'OTP কোড চেক করুন' বাটনে চাপ দিন।"
            )
            await query.message.edit_text(msg, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            keyboard = [[InlineKeyboardButton("🔄 অন্য রেঞ্জ চেষ্টা করুন", callback_data="select_range")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.edit_text(f"❌ কনসোলে এই রেঞ্জের নম্বর খালি রয়েছে।\nবার্তার বিবরণ: `{result}`", reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data.startswith("check_otp_"):
        tx_id = query.data.split("_")[2]
        success, code = check_range_otp(tx_id)

        if success:
            await query.message.reply_text(f"🎉 **আপনার OTP কোড:** `{code}`", parse_mode="Markdown")
        elif code == "WAITING":
            await query.message.reply_text("⏳ কোড আসার অপেক্ষায় আছে... অ্যাপে SMS পাঠালে ২-৩ সেকেন্ড পর আবার চাপ দিন।")
        else:
            await query.message.reply_text(f"⚠️ স্ট্যাটাস: `{code}`", parse_mode="Markdown")

    elif query.data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("🔢 নম্বর রেঞ্জ নির্বাচন করুন (Select Range)", callback_data="select_range")],
            [InlineKeyboardButton("👨‍💻 সাপোর্ট (Support)", url="https://t.me/your_support_username")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        welcome_msg = (
            f"👋 **হ্যালো {query.from_user.first_name}!**\n\n"
            f"🆔 **আপনার ID:** `{user_id}`\n\n"
            f"ফ্রি নম্বর নিতে নিচের বাটনটি চাপুন 👇"
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
        await update.message.reply_text("❌ মেসেজ লিখুন। উদাহরণ: `/broadcast নতুন ডায়ালার রেঞ্জ যুক্ত হয়েছে!`", parse_mode="Markdown")
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

    # User Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Admin Handlers
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("broadcast", broadcast))

    print("ZebraSMS Console Bot চালু হয়েছে...")
    app.run_polling()

if __name__ == "__main__":
    main()
