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
ZEBRASMS_API_KEY = "6U3G3DDZ6GB"  # zebrasms.com থেকে পাওয়া আপনার API Key দিন
ZEBRASMS_BASE_URL = "https://zebrasms.com/api/v1"
# =======================================================

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ==================== DATABASE SETUP ====================
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance REAL DEFAULT 0.0
        )
    """)
    conn.commit()
    conn.close()

def get_user(user_id, username=None):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user and username is not None:
        cursor.execute("INSERT INTO users (user_id, username, balance) VALUES (?, ?, ?)", (user_id, username, 0.0))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
    conn.close()
    return user

def update_balance(user_id, amount):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if user:
        new_balance = user[0] + amount
        if new_balance < 0:
            conn.close()
            return False, "পর্যাপ্ত ব্যালেন্স নেই!"
        cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
        conn.commit()
        conn.close()
        return True, new_balance
    conn.close()
    return False, "ইউজার পাওয়া যায়নি!"

def get_total_users():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

# ==================== ZEBRASMS API FUNCTIONS ====================

def zebrasms_get_number(service="tg", country="0"):
    """ZebraSMS API থেকে নম্বর অর্ডারের ফাংশন"""
    params = {
        "api_key": ZEBRASMS_API_KEY,
        "action": "getNumber",
        "service": service,
        "country": country
    }
    try:
        response = requests.get(ZEBRASMS_BASE_URL, params=params, timeout=10)
        res_text = response.text
        # Response Sample: ACCESS_NUMBER:$id:$number
        if "ACCESS_NUMBER" in res_text:
            parts = res_text.split(":")
            tx_id = parts[1]
            number = parts[2]
            return True, {"id": tx_id, "number": number}
        else:
            return False, res_text
    except Exception as e:
        return False, str(e)

def zebrasms_get_status(tx_id):
    """ZebraSMS API থেকে OTP/SMS স্ট্যাটাস চেক"""
    params = {
        "api_key": ZEBRASMS_API_KEY,
        "action": "getStatus",
        "id": tx_id
    }
    try:
        response = requests.get(ZEBRASMS_BASE_URL, params=params, timeout=10)
        res_text = response.text
        # Response Sample: STATUS_OK:$code
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
    db_user = get_user(user.id, user.username or "No Username")
    
    keyboard = [
        [InlineKeyboardButton("📱 নম্বর কিনুন (Buy Number)", callback_data="select_service")],
        [InlineKeyboardButton("💰 ব্যালেন্স দেখুন", callback_data="check_balance")],
        [InlineKeyboardButton("👨‍💻 সাপোর্ট", url="https://t.me/your_support_username")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_msg = (
        f"👋 **হ্যালো {user.first_name}!**\n\n"
        f"**ZebraSMS** স্বয়ংক্রিয় বট-এ আপনাকে স্বাগতম! 📱\n\n"
        f"🆔 **আপনার ID:** `{user.id}`\n"
        f"💵 **ব্যালেন্স:** ৳{db_user[2]:.2f}\n\n"
        f"নিচের অপশন থেকে আপনার কাঙ্ক্ষিত সেবাটি বেছে নিন 👇"
    )
    
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    db_user = get_user(user_id)

    if query.data == "check_balance":
        await query.message.reply_text(f"💰 আপনার বর্তমান ব্যালেন্স: ৳{db_user[2]:.2f}")

    elif query.data == "select_service":
        keyboard = [
            [InlineKeyboardButton("Telegram (৳২০)", callback_data="buy_tg"), InlineKeyboardButton("WhatsApp (৳২৫)", callback_data="buy_wa")],
            [InlineKeyboardButton("Facebook (৳১৫)", callback_data="buy_fb"), InlineKeyboardButton("Gmail (৳১০)", callback_data="buy_gm")],
            [InlineKeyboardButton("🔙 প্রধান মেনু", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text("🎯 **একটি সার্ভিস নির্বাচন করুন:**", reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data.startswith("buy_"):
        service_code = query.data.split("_")[1]
        
        # সার্ভিস অনুযায়ী রেট নির্ধারণ (উদাহরণস্বরূপ)
        price_map = {"tg": 20.0, "wa": 25.0, "fb": 15.0, "gm": 10.0}
        price = price_map.get(service_code, 20.0)

        # ব্যালেন্স চেক
        if db_user[2] < price:
            await query.message.reply_text(f"❌ আপনার পর্যাপ্ত ব্যালেন্স নেই! প্রয়োজন: ৳{price:.2f}, আপনার আছে: ৳{db_user[2]:.2f}")
            return

        # API থেকে নম্বর রিকোয়েস্ট
        success, result = zebrasms_get_number(service=service_code)
        
        if success:
            # ব্যালেন্স কাটা
            update_balance(user_id, -price)
            tx_id = result["id"]
            num = result["number"]
            
            keyboard = [
                [InlineKeyboardButton("📩 OTP কোড চেক করুন", callback_data=f"check_otp_{tx_id}")],
                [InlineKeyboardButton("🔙 প্রধান মেনু", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            msg = (
                f"🎉 **নম্বর সফলভাবে কেনা হয়েছে!**\n\n"
                f"📞 **নম্বর:** `{num}`\n"
                f"🆔 **Transaction ID:** `{tx_id}`\n\n"
                f"💡 নম্বরটি অ্যাপে বসানোর পর নিচের 'OTP কোড চেক করুন' বাটনে ক্লিক করুন।"
            )
            await query.message.edit_text(msg, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await query.message.reply_text(f"❌ নম্বর পাওয়া যায়নি। ZebraSMS বার্তা: `{result}`", parse_mode="Markdown")

    elif query.data.startswith("check_otp_"):
        tx_id = query.data.split("_")[2]
        success, code = zebrasms_get_status(tx_id)
        
        if success:
            await query.message.reply_text(f"🎉 **আপনার OTP কোড:** `{code}`", parse_mode="Markdown")
        elif code == "WAITING":
            await query.message.reply_text("⏳ এখনও OTP আসেনি, অনুগ্রহ করে কিছুক্ষণ পর আবার চেষ্টা করুন।")
        else:
            await query.message.reply_text(f"⚠️ অবস্থা: `{code}`", parse_mode="Markdown")

    elif query.data == "main_menu":
        db_user = get_user(user_id)
        keyboard = [
            [InlineKeyboardButton("📱 নম্বর কিনুন (Buy Number)", callback_data="select_service")],
            [InlineKeyboardButton("💰 ব্যালেন্স দেখুন", callback_data="check_balance")],
            [InlineKeyboardButton("👨‍💻 সাপোর্ট", url="https://t.me/your_support_username")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        welcome_msg = (
            f"👋 **হ্যালো {query.from_user.first_name}!**\n\n"
            f"🆔 **আপনার ID:** `{user_id}`\n"
            f"💵 **ব্যালেন্স:** ৳{db_user[2]:.2f}"
        )
        await query.message.edit_text(welcome_msg, reply_markup=reply_markup, parse_mode="Markdown")

# ==================== ADMIN COMMANDS ====================

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ আপনি এই কমান্ডটি ব্যবহার করার অনুমতি পাননি।")
        return

    admin_msg = (
        "🛠️ **অ্যাডমিন প্যানেল**\n\n"
        "➕ **ব্যালেন্স যোগ করতে:**\n"
        "`/addbalance <user_id> <amount>`\n\n"
        "📊 **মোট ইউজার দেখতে:**\n"
        "`/users`"
    )
    await update.message.reply_text(admin_msg, parse_mode="Markdown")

async def add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        target_user_id = int(context.args[0])
        amount = float(context.args[1])
        
        success, result = update_balance(target_user_id, amount)
        if success:
            await update.message.reply_text(f"✅ সফলভাবে ইউজার `{target_user_id}` কে ৳{amount:.2f} যোগ করা হয়েছে।\nনতুন ব্যালেন্স: ৳{result:.2f}", parse_mode="Markdown")
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=f"🎉 আপনার অ্যাকাউন্টে ৳{amount:.2f} যোগ করা হয়েছে!\nবর্তমান ব্যালেন্স: ৳{result:.2f}"
                )
            except Exception:
                pass
        else:
            await update.message.reply_text(f"❌ এরর: {result}")

    except (IndexError, ValueError):
        await update.message.reply_text("❌ সঠিক ফরম্যাট: `/addbalance <user_id> <amount>`", parse_mode="Markdown")

async def total_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    count = get_total_users()
    await update.message.reply_text(f"👥 বটের মোট ইউজার সংখ্যা: {count}")

# ==================== MAIN APPLICATION ====================

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Admin Handlers
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("addbalance", add_balance))
    app.add_handler(CommandHandler("users", total_users))

    print("ZebraSMS বট সফলভাবে চালু হয়েছে...")
    app.run_polling()

if __name__ == "__main__":
    main()
