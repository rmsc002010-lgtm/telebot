import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# অ্যাডমিন আইডি (আপনার টেলিগ্রাম ইউজার আইডি দিয়ে পরিবর্তন করুন)
ADMIN_ID = 1586853120 

# আপনার টেলিগ্রাম বট টোকেন দিন
BOT_TOKEN = "8782800246:AAHJ-i7-umPomE7FBJsEK8G8d5ySfqg_0FM"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# /start কমান্ড হ্যান্ডলার
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    keyboard = [
        [
            InlineKeyboardButton("📱 নম্বর কিনুন (Buy Number)", callback_data='buy_number'),
            InlineKeyboardButton("👤 আমার অ্যাকাউন্ট (Account)", callback_data='account')
        ],
        [
            InlineKeyboardButton("💳 ব্যালেন্স রিচার্জ (Recharge)", callback_data='recharge'),
            InlineKeyboardButton("📩 ইতিহাস (History)", callback_data='history')
        ],
        [
            InlineKeyboardButton("🌐 ZebraSMS ওয়েবসাইট", url='https://zebrasms.com/')
        ]
    ]

    # ইউজার যদি অ্যাডমিন হন, তবে অ্যাডমিন প্যানেল বাটন যুক্ত হবে
    if user.id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("⚙️ অ্যাডমিন প্যানেল", callback_data='admin_panel')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"স্বাগতম {user.first_name}! 👋\n\n"
        "ZebraSMS বটের মাধ্যমে সরাসরি ভার্চুয়াল নম্বর পেতে নিচের বাটনগুলো ব্যবহার করুন।"
    )

    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup)

# বাটন ক্লিক হ্যান্ডলার
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == 'buy_number':
        keyboard = [
            [InlineKeyboardButton("WhatsApp", callback_data='buy_wa'), InlineKeyboardButton("Telegram", callback_data='buy_tg')],
            [InlineKeyboardButton("Facebook", callback_data='buy_fb'), InlineKeyboardButton("Gmail", callback_data='buy_gmail')],
            [InlineKeyboardButton("🔙 প্রধান মেনু", callback_data='main_menu')]
        ]
        await query.edit_message_text("কোন সার্ভিসের নম্বর নিতে চান নির্বাচন করুন:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'account':
        acc_text = (
            "👤 **আপনার তথ্য:**\n\n"
            f"আইডি: `{query.from_user.id}`\n"
            "ব্যালেন্স: ৳0.00\n"
            "মোট কেনা নম্বর: 0"
        )
        keyboard = [[InlineKeyboardButton("🔙 প্রধান মেনু", callback_data='main_menu')]]
        await query.edit_message_text(acc_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'recharge':
        recharge_text = (
            "💳 **ব্যালেন্স রিচার্জ পদ্ধতি:**\n\n"
            "বিকাশ/নগদ রকেট নম্বর নিতে অ্যাডমিনের সাথে যোগাযোগ করুন অথবা পেমেন্ট ট্রানজেকশন আইডি পাঠান।"
        )
        keyboard = [
            [InlineKeyboardButton("👨‍💻 অ্যাডমিন যোগাযোগ", url='https://t.me/your_admin_username')],
            [InlineKeyboardButton("🔙 প্রধান মেনু", callback_data='main_menu')]
        ]
        await query.edit_message_text(recharge_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == 'admin_panel':
        if query.from_user.id != ADMIN_ID:
            await query.edit_message_text("আপনার এই সেকশনে প্রবেশের অনুমতি নেই।")
            return
        
        admin_keyboard = [
            [InlineKeyboardButton("➕ ব্যালেন্স যোগ করুন", callback_data='admin_add_balance')],
            [InlineKeyboardButton("📢 ব্রডকাস্ট মেসেজ", callback_data='admin_broadcast')],
            [InlineKeyboardButton("🔙 প্রধান মেনু", callback_data='main_menu')]
        ]
        await query.edit_message_text("⚙️ **অ্যাডমিন কন্ট্রোল প্যানেল**", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(admin_keyboard))

    elif data == 'main_menu':
        await start(update, context)

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))

    print("বট সফলভাবে চালু হয়েছে...")
    app.run_polling()