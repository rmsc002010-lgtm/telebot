import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# ================== কনফিগারেশন ==================
# ১. আপনার বট টোকেন বসান (BotFather থেকে পাওয়া)
BOT_TOKEN = "8782800246:AAHJ-i7-umPomE7FBJsEK8G8d5ySfqg_0FM" 

# ২. আপনার টেলিগ্রাম নিউমেরিক ইউজার আইডি বসান
ADMIN_ID = 1586853120 

# ৩. আপনার টেলিগ্রাম ইউজারনেম বসান (@ ছাড়া)
ADMIN_USERNAME = "akikshahrin" 
# =================================================

# লগিং সেটআপ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# মূল বাটন মেনু তৈরি করার ফাংশন
def get_main_keyboard(user_id: int):
    keyboard = [
        [
            InlineKeyboardButton("📱 নম্বর কিনুন (Buy Number)", callback_data='btn_buy_number'),
            InlineKeyboardButton("👤 আমার অ্যাকাউন্ট (Account)", callback_data='btn_account')
        ],
        [
            InlineKeyboardButton("💳 ব্যালেন্স রিচার্জ (Recharge)", callback_data='btn_recharge'),
            InlineKeyboardButton("📩 ইতিহাস (History)", callback_data='btn_history')
        ],
        [
            InlineKeyboardButton("🌐 ZebraSMS ওয়েবসাইট", url='https://zebrasms.com/')
        ]
    ]

    # অ্যাডমিন হলে অ্যাডমিন প্যানেল যুক্ত হবে
    if user_id == ADMIN_ID:
        keyboard.append([InlineKeyboardButton("⚙️ অ্যাডমিন প্যানেল", callback_data='btn_admin_panel')])

    return InlineKeyboardMarkup(keyboard)

# /start কমান্ড
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"স্বাগতম {user.first_name}! 👋\n\n"
        "ZebraSMS বটের মাধ্যমে সরাসরি ভার্চুয়াল নম্বর পেতে নিচের বাটনগুলো ব্যবহার করুন।"
    )
    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard(user.id))

# সকল বাটন ক্লিক হ্যান্ডলার
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # টেলিগ্রাম ক্লায়েন্টকে নিশ্চিত করা যে বাটনে ক্লিক লেগেছে
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    # ১. প্রধান মেনুতে ফেরা
    if data == 'btn_main_menu':
        welcome_text = (
            f"স্বাগতম {query.from_user.first_name}! 👋\n\n"
            "ZebraSMS বটের মাধ্যমে সরাসরি ভার্চুয়াল নম্বর পেতে নিচের বাটনগুলো ব্যবহার করুন।"
        )
        await query.edit_message_text(welcome_text, reply_markup=get_main_keyboard(user_id))

    # ২. নম্বর কেনার মেনু
    elif data == 'btn_buy_number':
        services_keyboard = [
            [
                InlineKeyboardButton("WhatsApp", callback_data='srv_whatsapp'),
                InlineKeyboardButton("Telegram", callback_data='srv_telegram')
            ],
            [
                InlineKeyboardButton("Facebook", callback_data='srv_facebook'),
                InlineKeyboardButton("Gmail", callback_data='srv_gmail')
            ],
            [InlineKeyboardButton("🔙 প্রধান মেনু", callback_data='btn_main_menu')]
        ]
        await query.edit_message_text(
            "কোন সার্ভিসের নম্বর নিতে চান নির্বাচন করুন:",
            reply_markup=InlineKeyboardMarkup(services_keyboard)
        )

    # ৩. নির্দিষ্ট সার্ভিস নির্বাচন (WhatsApp, Telegram, Facebook, Gmail)
    elif data.startswith('srv_'):
        service_key = data.split('_')[1]
        service_names = {
            'whatsapp': 'WhatsApp',
            'telegram': 'Telegram',
            'facebook': 'Facebook',
            'gmail': 'Gmail'
        }
        selected_name = service_names.get(service_key, 'Service')

        action_keyboard = [
            [InlineKeyboardButton("🔄 নম্বর পান (Get Number)", callback_data=f'getnum_{service_key}')],
            [InlineKeyboardButton("🔙 পেছনে যান", callback_data='btn_buy_number')]
        ]

        await query.edit_message_text(
            f"📌 **সার্ভিস:** {selected_name}\n"
            f"💰 **মূল্য:** ৳৫০ (স্যাম্পল)\n"
            f"📊 **স্টক:** পর্যাপ্ত নম্বর খালি আছে\n\n"
            f"নম্বর সংগ্রহ করতে নিচের 'নম্বর পান' বাটনে চাপুন।",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(action_keyboard)
        )

    # ৪. নম্বর পাওয়ার কনফার্মেশন ক্লিক
    elif data.startswith('getnum_'):
        service_key = data.split('_')[1].upper()
        
        back_keyboard = [[InlineKeyboardButton("🔙 নম্বর তালিকায় ফেরত যান", callback_data='btn_buy_number')]]
        
        # এখানে পরবর্তীতে ZebraSMS এর API যুক্ত করা হবে
        await query.edit_message_text(
            f"⚠️ **পর্যাপ্ত ব্যালেন্স নেই!**\n\n"
            f"আপনার অ্যাকাউন্টে {service_key} এর নম্বর কেনার জন্য পর্যাপ্ত ব্যালেন্স নেই। অনুগ্রহ করে অ্যাকাউন্ট রিচার্জ করুন।",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(back_keyboard)
        )

    # ৫. অ্যাকাউন্ট তথ্য
    elif data == 'btn_account':
        acc_text = (
            "👤 **আপনার অ্যাকাউন্ট বিবরণী:**\n\n"
            f"🆔 **ইউজার আইডি:** `{user_id}`\n"
            f"💵 **ব্যালেন্স:** ৳0.00\n"
            f"📦 **মোট ক্রয়কৃত নম্বর:** 0"
        )
        keyboard = [[InlineKeyboardButton("🔙 প্রধান মেনু", callback_data='btn_main_menu')]]
        await query.edit_message_text(acc_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    # ৬. ব্যালেন্স রিচার্জ
    elif data == 'btn_recharge':
        recharge_text = (
            "💳 **ব্যালেন্স রিচার্জ পদ্ধতি:**\n\n"
            "বিকাশ/নগদ/রকেটের মাধ্যমে ম্যানুয়ালি ব্যালেন্স যোগ করতে অ্যাডমিনের সাথে যোগাযোগ করুন।"
        )
        keyboard = [
            [InlineKeyboardButton("👨‍💻 অ্যাডমিন এর সাথে কথা বলুন", url=f'https://t.me/{ADMIN_USERNAME}')],
            [InlineKeyboardButton("🔙 প্রধান মেনু", callback_data='btn_main_menu')]
        ]
        await query.edit_message_text(recharge_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    # ৭. ইতিহাস (History)
    elif data == 'btn_history':
        history_text = "📩 **ক্রয়কৃত নম্বরের ইতিহাস:**\n\nআপনার কেনা কোনো সক্রিয় বা পুরোনো নম্বরের ডাটা পাওয়া যায়নি।"
        keyboard = [[InlineKeyboardButton("🔙 প্রধান মেনু", callback_data='btn_main_menu')]]
        await query.edit_message_text(history_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    # ৮. অ্যাডমিন প্যানেল
    elif data == 'btn_admin_panel':
        if user_id != ADMIN_ID:
            await query.edit_message_text("❌ আপনার এই সেকশনে প্রবেশের অনুমতি নেই।")
            return
        
        admin_keyboard = [
            [InlineKeyboardButton("➕ ইউজার ব্যালেন্স যুক্ত করুন", callback_data='admin_add_bal')],
            [InlineKeyboardButton("📢 ব্রডকাস্ট নোটিশ", callback_data='admin_broadcast')],
            [InlineKeyboardButton("🔙 প্রধান মেনু", callback_data='btn_main_menu')]
        ]
        await query.edit_message_text("⚙️ **অ্যাডমিন কন্ট্রোল প্যানেল:**", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(admin_keyboard))

    # অ্যাডমিন একশন হ্যান্ডলার স্যাম্পল
    elif data in ['admin_add_bal', 'admin_broadcast']:
        keyboard = [[InlineKeyboardButton("🔙 অ্যাডমিন প্যানেল", callback_data='btn_admin_panel')]]
        await query.edit_message_text("🛠 এই ফিচারটি পরবর্তীতে কমান্ড ইনপুটের মাধ্যমে যুক্ত করা হবে।", reply_markup=InlineKeyboardMarkup(keyboard))

# মেইন রানার
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # কমান্ড হ্যান্ডলার
    app.add_handler(CommandHandler("start", start_command))
    
    # বাটন ব্যাকএন্ড হ্যান্ডলার
    app.add_handler(CallbackQueryHandler(handle_callback_query))

    print("বট সফলভাবে চালুর জন্য প্রস্তুত...")
    app.run_polling()
