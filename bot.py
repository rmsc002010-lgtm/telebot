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

# ZebraSMS API Config
ZEBRASMS_API_KEY = "6U3G3DDZ6GB"
ZEBRASMS_BASE_URL = "https://zebrasms.com/stubs/handler_api.php"
# =======================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Live Console Mapping
CONSOLE_RANGE_MAPPING = {
    "1": {
        "label": "🇲🇬 Madagascar (+261)",
        "country": "Madagascar",
        "country_code": "261"
    },
    "2": {
        "label": "🇨🇲 Cameroon (+237)",
        "country": "Cameroon",
        "country_code": "237"
    },
    "3": {
        "label": "🇲🇪 Montenegro (+382)",
        "country": "Montenegro",
        "country_code": "382"
    }
}

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

# ==================== ZEBRASMS API ====================

def api_get_number(country_code):
    """সব সম্ভাব্য সার্ভিস কোড ট্রাই করে নম্বর বের করার চেষ্টা"""
    # ZebraSMS-এর সম্ভাব্য সার্ভিস কোডসমূহ: fb (Facebook), ot (Any Other), tg (Telegram), wa (WhatsApp)
    services_to_try = ["fb", "ot", "f", "full", "any"]
    
    for service_code in services_to_try:
        params = {
            "api_key": ZEBRASMS_API_KEY,
            "action": "getNumber",
            "service": service_code,
            "country": country_code
        }
        try:
            response = requests.get(ZEBRASMS_BASE_URL, params=params, timeout=10)
            res_text = response.text.strip()
            
            if "ACCESS_NUMBER" in res_text:
                parts = res_text.split(":")
                return True, {"id": parts[1], "number": parts[2], "service": service_code}
            elif "NO_BALANCE" in res_text:
                return False, "⚠️ API একাউন্টে ব্যালেন্স শেষ।"
            elif "BAD_KEY" in res_text:
                return False, "⚠️ API Key ভুল বা ইনভ্যালিড।"
        except Exception as e:
            return False, str(e)
            
    return False, "❌ প্যানেলে এই দেশের কোনো স্টকে নম্বর খালি নেই। অন্য দেশ ট্রাই করুন।"

def api_check_otp(tx_id):
    params = {
        "api_key": ZEBRASMS_API_KEY,
        "action": "getStatus",
        "id": tx_id
    }
    try:
        response = requests.get(ZEBRASMS_BASE_URL, params=params, timeout=10)
        res_text = response.text.strip()
        
        if "STATUS_OK" in res_text:
            code = res_text.split(":")[1]
            return True, code
        elif "STATUS_WAIT_CODE" in res_text:
            return False, "WAITING"
        else:
            return False, res_text
    except Exception as e:
        return False, str(e)

# ==================== HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user.id, user.username or "No Username")
    
    keyboard = [
        [InlineKeyboardButton("🌐 কনসোল রেঞ্জ সিলেক্ট করুন", callback_data="select_range")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_msg = (
        f"👋 **হ্যালো {user.first_name}!**\n\n"
        f"ZebraSMS Live Console Bot-এ স্বাগতম!\n"
        f"🆔 **আপনার ID:** `{user.id}`"
    )
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "select_range":
        keyboard = []
        for key, val in CONSOLE_RANGE_MAPPING.items():
            keyboard.append([InlineKeyboardButton(val["label"], callback_data=f"getrange_{key}")])
            
        keyboard.append([InlineKeyboardButton("🔙 প্রধান মেনু", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text("🎯 **দেশ নির্বাচন করুন:**", reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data.startswith("getrange_"):
        range_key = query.data.split("_")[1]
        range_info = CONSOLE_RANGE_MAPPING.get(range_key)

        await query.message.edit_text(f"⏳ **{range_info['country']}** - নম্বর খোঁজা হচ্ছে...")

        success, result = api_get_number(country_code=range_info["country_code"])

        if success:
            tx_id = result["id"]
            number = result["number"]

            keyboard = [
                [InlineKeyboardButton("📩 OTP কোড চেক করুন", callback_data=f"check_otp_{tx_id}")],
                [InlineKeyboardButton("🔄 নতুন নম্বর নিন", callback_data="select_range")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            msg = (
                f"🎉 **নম্বর পাওয়া গেছে!**\n\n"
                f"🌍 **দেশ:** {range_info['country']}\n"
                f"📞 **নম্বর:** `{number}`\n"
                f"🆔 **ID:** `{tx_id}`\n\n"
                f"💡 SMS পাঠানোর পর **'OTP কোড চেক করুন'** বাটনে চাপ দিন।"
            )
            await query.message.edit_text(msg, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            keyboard = [[InlineKeyboardButton("🔄 অন্য দেশ চেষ্টা করুন", callback_data="select_range")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.edit_text(f"❌ **নম্বর পাওয়া যায়নি!**\n\n**কারণ:** {result}", reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data.startswith("check_otp_"):
        tx_id = query.data.split("_")[2]
        success, code = api_check_otp(tx_id)

        if success:
            await query.message.reply_text(f"🎉 **আপনার OTP কোড:** `{code}`", parse_mode="Markdown")
        elif code == "WAITING":
            await query.message.reply_text("⏳ OTP এখনও পৌঁছায়নি। কিছুক্ষন অপেক্ষা করে আবার চেষ্টা করুন।")
        else:
            await query.message.reply_text(f"⚠️ স্ট্যাটাস: `{code}`", parse_mode="Markdown")

    elif query.data == "main_menu":
        keyboard = [[InlineKeyboardButton("🌐 কনসোল রেঞ্জ সিলেক্ট করুন", callback_data="select_range")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text("প্রধান মেনু", reply_markup=reply_markup)

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
