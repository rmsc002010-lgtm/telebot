import logging
import sqlite3
import random
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
# =======================================================

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Sample Free Virtual Numbers List (এখানে আপনি আপনার পছন্দমতো ফ্রি নম্বর যোগ করতে পারেন)
FREE_NUMBERS = [
    "+1 (202) 555-0143",
    "+1 (202) 555-0188",
    "+44 7700 900077",
    "+44 7700 900088",
    "+1 (315) 555-0199",
    "+1 (415) 555-0122"
]

# ==================== DATABASE SETUP ====================
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

# ==================== USER HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    register_user(user.id, user.username or "No Username")
    
    keyboard = [
        [InlineKeyboardButton("📱 ফ্রি নম্বর নিন (Get Free Number)", callback_data="get_free_number")],
        [InlineKeyboardButton("ℹ️ কিভাবে ব্যবহার করবেন?", callback_data="how_to_use")],
        [InlineKeyboardButton("👨‍💻 সাপোর্ট (Support)", url="https://t.me/your_support_username")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_msg = (
        f"👋 **হ্যালো {user.first_name}!**\n\n"
        f"আমাদের **ফ্রি নম্বর বক্সে** আপনাকে স্বাগতম! 🎁\n"
        f"এখানে আপনি কোনো টাকা ছাড়াই ওটিপি (OTP) বা ভেরিফিকেশনের জন্য ভার্চুয়াল নম্বর নিতে পারবেন।\n\n"
        f"🆔 **আপনার ID:** `{user.id}`\n\n"
        f"নিচের বাটনে ক্লিক করে এখনই নম্বর সংগ্রহ করুন 👇"
    )
    
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id

    if query.data == "get_free_number":
        # Random free number generated from list
        selected_number = random.choice(FREE_NUMBERS)
        
        keyboard = [
            [InlineKeyboardButton("🔄 অন্য নম্বর দেখুন", callback_data="get_free_number")],
            [InlineKeyboardButton("📩 OTP কোড রিফ্রেশ করুন", callback_data="get_otp_code")],
            [InlineKeyboardButton("🔙 প্রধান মেনু", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        msg = (
            f"🎉 **আপনার জন্য প্রস্তুতকৃত ফ্রি নম্বর:**\n\n"
            f"📞 **নম্বর:** `{selected_number}`\n\n"
            f"💡 **পরামর্শ:** ওপরের নম্বরে ক্লিক করে কপি করুন এবং আপনার কাঙ্ক্ষিত অ্যাপে ব্যবহার করুন।"
        )
        await query.message.edit_text(msg, reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == "get_otp_code":
        # Mock OTP behavior for free public numbers
        keyboard = [
            [InlineKeyboardButton("🔄 রিফ্রেশ (Refresh)", callback_data="get_otp_code")],
            [InlineKeyboardButton("🔙 প্রধান মেনু", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        otp_msg = (
            f"⏳ **কোড সার্চ করা হচ্ছে...**\n\n"
            f"পাবলিক নম্বরের ক্ষেত্রে SMS আসতে ১-২ মিনিট সময় লাগতে পারে।\n"
            f"যদি কোড না আসে তবে কিছুক্ষণ পর 'রিফ্রেশ' বাটনে ক্লিক করুন।"
        )
        await query.message.edit_text(otp_msg, reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == "how_to_use":
        keyboard = [[InlineKeyboardButton("🔙 প্রধান মেনু", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        guide_text = (
            "📖 **ব্যবহার বিধি:**\n\n"
            "১. 'ফ্রি নম্বর নিন' বাটনে ক্লিক করুন।\n"
            "২. নম্বরটি কপি করে আপনার প্রয়োজনীয় ওয়েবসাইট বা অ্যাপে বসান।\n"
            "৩. এসএমএস পাঠানো হলে 'OTP কোড রিফ্রেশ' বাটনে চাপ দিয়ে কোডটি সংগ্রহ করুন।"
        )
        await query.message.edit_text(guide_text, reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("📱 ফ্রি নম্বর নিন (Get Free Number)", callback_data="get_free_number")],
            [InlineKeyboardButton("ℹ️ কিভাবে ব্যবহার করবেন?", callback_data="how_to_use")],
            [InlineKeyboardButton("👨‍💻 সাপোর্ট (Support)", url="https://t.me/your_support_username")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text("🏠 **প্রধান মেনু:**", reply_markup=reply_markup, parse_mode="Markdown")

# ==================== ADMIN COMMANDS ====================

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ আপনি এই কমান্ডটি ব্যবহার করার অনুমতি পাননি।")
        return

    total_users = get_total_users()
    admin_msg = (
        f"🛠️ **অ্যাডমিন প্যানেল**\n\n"
        f"📊 **মোট ইউজারের সংখ্যা:** {total_users}\n\n"
        f"📢 **ব্রডকাস্ট মেসেজ পাঠাতে:**\n"
        f"`/broadcast <আপনার মেসেজ>`"
    )
    await update.message.reply_text(admin_msg, parse_mode="Markdown")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("❌ মেসেজ লিখুন। উদাহরণ:\n`/broadcast শুভকামনা সবাইকে!`", parse_mode="Markdown")
        return

    msg_to_send = " ".join(context.args)
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()

    count = 0
    for u in users:
        try:
            await context.bot.send_message(chat_id=u[0], text=msg_to_send)
            count += 1
        except Exception:
            pass

    await update.message.reply_text(f"✅ মোট {count} জন ইউজারকে সফলভাবে মেসেজ পাঠানো হয়েছে।")

# ==================== MAIN APPLICATION ====================

def main():
    # Database Initialization
    init_db()

    # Create Bot Application
    app = Application.builder().token(BOT_TOKEN).build()

    # User Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Admin Handlers
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("broadcast", broadcast))

    print("বট সফলভাবে চালু হয়েছে...")
    app.run_polling()

if __name__ == "__main__":
    main()
