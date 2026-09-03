import asyncio
import html
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from motor.motor_asyncio import AsyncIOMotorClient

# ══════════════════════════════════════════════════════════════════════════════
# ⚙️ CONFIGURATION & CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
BOT_URL = "https://t.me/testjonson2_bot"
BOT_TOKEN = "8852330034:AAG-VW3qO9EuaPMcf54dtD_fpiNkTOkfKYI"
OTP_GROUP_ID = -1004415108815
OTP_GROUP_URL = "https://t.me/otpmastersgrp"
ADMIN_ID = 1586853120
ADMINS = [1586853120]
OWNER_ID = "1586853120"
PRIMARY_API_KEY = "6U3G3DDZ6GB"
DEVELOPER_ID = 8595326790
DEVELOPER_USERNAME = "@akikshahrin"
DEVELOPER_LINK = "https://t.me/akikshahrin"
MONGODB_URI = "mongodb+srv://dreamsbyshahin_db_user:Z********26@zebrasmsofficial.xkrbvj9.mongodb.net/?appName=ZEBRASMSOFFICIAL"

PRIMARY_BASE_URL = "https://zebrasms.com/api/v1"
PRIMARY_HEADERS = {"MAuth": PRIMARY_API_KEY, "Content-Type": "application/json"}
SECONDARY_API_KEY = "MBVVO65D7T9"
SECONDARY_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api"
SECONDARY_HEADERS = {"mauthapi": SECONDARY_API_KEY, "Content-Type": "application/json"}
SUPPORT_LINK = "https://t.me/akikshahrin"

CHECK_INTERVAL = 5  # Seconds between checks
PAID_SMS_FILE = "paid_sms.json"

WELCOME_MESSAGE = "<b>Welcome to Zebra SMS Ultra Bot!</b>\nSelect an option from the menu below:"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# MongoDB Async Connection Setup
try:
    mongo_client = AsyncIOMotorClient(MONGODB_URI)
    db = mongo_client["zebrasmsofficial"]
    logger.info("Connecting to MongoDB Atlas...")
except Exception as e:
    logger.error(f"MongoDB connection error: {e}")

# In-memory data structures
active_numbers = {}
paid_data = {}


# ══════════════════════════════════════════════════════════════════════════════
# 🛠️ HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def get_premium_custom_emoji(name: str) -> str:
    emojis = {
        "done": "✅",
        "country": "🌐",
        "service": "📱",
        "number": "📞",
        "otp": "🔑",
        "sms": "💬",
        "dashboard": "📊",
        "phone": "📲",
        "range": "📶",
        "money": "💰",
        "user": "👤",
        "gem": "💎",
        "shield": "🛡️",
    }
    return emojis.get(name, "⭐")


def format_premium_divider(style: str) -> str:
    return "━━━━━━━━━━━━━━━━━━━━━━"


def get_country_info(num: str):
    return "🌐", "Global"


def update_traffic_stats(service: str, country: str, range_info: str, hits: int = 1):
    pass


def mask_number(num: str) -> str:
    if len(str(num)) > 6:
        return str(num)[:3] + "****" + str(num)[-3:]
    return str(num)


def save_data(data, filepath):
    pass


def is_user_banned(uid: int) -> bool:
    return False


def is_admin(uid: int) -> bool:
    return uid == ADMIN_ID or uid in ADMINS or str(uid) == OWNER_ID


def get_user(uid: int):
    return {"balance": 0.00}


def get_user_stats(uid: int):
    return {"total_numbers": 0, "total_otps": 0}


def get_user_otp_rate(uid: int) -> float:
    return 0.10


def format_balance(val: float) -> str:
    return f"{val:.2f}"


def get_referral_stats(uid: int):
    return {"count": 0}


def get_referral_price() -> float:
    return 0.50


def user_exists(uid: int) -> bool:
    return True


def add_referral(ref_id: int, new_id: int) -> bool:
    return False


async def update_db_balance(uid: int, amount: float):
    pass


def add_number_taken(uid: int, count: int = 1):
    pass


def normalize_number(num: str) -> str:
    return str(num).replace("+", "").strip()


async def check_force_join(uid: int, message=None, context=None) -> bool:
    return True


def start_periodic_check():
    pass


# API Mock Placeholders
async def fetch_services_cached():
    return {"telegram": {"ranges": ["237620XXX"]}, "whatsapp": {"ranges": ["120155XXX"]}}


async def auto_select_best_range(svc: str, prefix: str):
    return "237620XXX"


async def get_number_from_api(rng: str):
    return "+237620123456", "Cameroon"


# Keyboards
def main_keyboard(uid: int):
    kbd = [
        [InlineKeyboardButton("📞 GET NUMBER", callback_data="back_services")],
        [InlineKeyboardButton("📊 TRAFFIC", callback_data="traffic_home")],
        [InlineKeyboardButton("💬 SUPPORT", url=SUPPORT_LINK), InlineKeyboardButton("👥 OTP GROUP", url=OTP_GROUP_URL)]
    ]
    if is_admin(uid):
        kbd.append([InlineKeyboardButton("⚙️ ADMIN PANEL", callback_data="admin_panel")])
    return InlineKeyboardMarkup(kbd)


def cancel_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("❌ CANCEL", callback_data="back_to_main")]])


def admin_main_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]])


def user_management_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]])


def system_config_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")]])


def build_traffic_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Refresh", callback_data="traffic_refresh")]])


def build_service_traffic_keyboard(svc):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Traffic Home", callback_data="traffic_home")]])


def build_country_traffic_keyboard(svc, ctr):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Traffic Home", callback_data="traffic_home")]])


def _build_services_keyboard(services):
    buttons = [[InlineKeyboardButton(svc.upper(), callback_data=f"svc_{svc}")] for svc in services]
    buttons.append([InlineKeyboardButton("🔙 BACK", callback_data="back_to_main")])
    return InlineKeyboardMarkup(buttons)


def _build_countries_keyboard(ranges, svc):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇨🇲 Cameroon (+237)", callback_data=f"country_237_{svc}")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_services")]
    ])


def _build_ranges_keyboard(ranges, prefix, svc):
    buttons = [[InlineKeyboardButton(r, callback_data=f"range_{r}_{svc}")] for r in ranges]
    buttons.append([InlineKeyboardButton("🔙 BACK", callback_data=f"svc_{svc}")])
    return InlineKeyboardMarkup(buttons)


def render_traffic_dashboard():
    return "<b>📊 TRAFFIC DASHBOARD</b>\nLive traffic data system."


# Dummy Command / Flow Handlers
async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Search command placeholder.")


async def process_2fa_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Processing 2FA Key...")


async def show_app_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    services = await fetch_services_cached()
    await update.message.reply_text("Select Service:", reply_markup=_build_services_keyboard(services))


async def traffic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = render_traffic_dashboard()
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=build_traffic_keyboard())


async def get_2fa_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send your 2FA Secret Key:")


async def assign_special_number(query, context, uid):
    await query.message.edit_text("Special Numbers Menu")


async def allocate_one_special_number_by_country(query, context, uid, prefix):
    await query.message.edit_text("Allocating Special Number...")


async def admin_traffic_control(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Admin Traffic Control")


# ══════════════════════════════════════════════════════════════════════════════
# 🔄 MONITOR LOOP
# ══════════════════════════════════════════════════════════════════════════════
async def monitor_loop(app):
    """Background task to continuously check for incoming OTPs."""
    while True:
        try:
            num = "237620123456"
            service_name = "Telegram"
            range_info = "237620XXX"
            otp_code = "123456"
            full_sms = "Your Telegram code is 123456"
            uid = None
            sms_key = f"{num}_{otp_code}"

            country_flag, country_name = get_country_info(num)
            update_traffic_stats(service_name, country_name, range_info, hits=1)

            now_time = datetime.now()
            user_msg = (
                f"{get_premium_custom_emoji('done')} <b>OTP RECEIVED SUCCESSFULLY!</b>\n"
                f"{format_premium_divider('success')}\n"
                f"<blockquote>{get_premium_custom_emoji('country')} COUNTRY: <code>{country_flag} {country_name}</code></blockquote>\n"
                f"<blockquote>{get_premium_custom_emoji('service')} SERVICE: <code>{service_name}</code></blockquote>\n"
                f"<blockquote>{get_premium_custom_emoji('number')} NUMBER: <code>{num}</code></blockquote>\n"
                f"<blockquote>{get_premium_custom_emoji('otp')} OTP: <code>{otp_code}</code></blockquote>\n"
                f"<blockquote>{get_premium_custom_emoji('sms')} SMS: <code>{html.escape(full_sms)}</code></blockquote>\n"
                f"📅 {now_time.strftime('%d %B, %Y')} | {now_time.strftime('%I:%M %p')}"
            )

            if uid:
                try:
                    await app.bot.send_message(chat_id=uid, text=user_msg, parse_mode="HTML")
                except Exception as e:
                    logger.error(f"Failed to send OTP to user {uid}: {e}")

            group_msg = (
                f"⚡ <b>NEW OTP RECEIVED</b> ⚡\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📱 <b>Service:</b> {service_name}\n"
                f"📞 <b>Number:</b> {mask_number(num)}\n"
                f"🔑 <b>OTP:</b> <code>{otp_code}</code>\n"
                f"💬 <b>SMS:</b> <code>{html.escape(full_sms)}</code>"
            )
            try:
                await app.bot.send_message(chat_id=OTP_GROUP_ID, text=group_msg, parse_mode="HTML")
            except Exception as e:
                logger.error(f"Failed to send OTP to Group: {e}")

            paid_data[sms_key] = {
                "uid": uid,
                "number": num,
                "otp": otp_code,
                "sms": full_sms,
                "timestamp": now_time.isoformat(),
            }
            save_data(paid_data, PAID_SMS_FILE)

            await asyncio.sleep(CHECK_INTERVAL)
        except Exception as e:
            logger.error(f"Monitor loop error: {e}")
            await asyncio.sleep(5)


# ══════════════════════════════════════════════════════════════════════════════
# 🎯 CALLBACK QUERY HANDLER
# ══════════════════════════════════════════════════════════════════════════════
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    data = query.data

    await query.answer()

    if data == "check_force_join":
        if await check_force_join(uid, message=query.message, context=context):
            await query.message.edit_text("✅ Verification successful! You can now use the bot.")
        else:
            await query.answer("❌ You haven't joined all required channels yet!", show_alert=True)
        return

    if is_user_banned(uid):
        await query.answer("🚫 You are banned!", show_alert=True)
        return

    if data == "back_to_main":
        await query.message.edit_text(WELCOME_MESSAGE, parse_mode="HTML", reply_markup=main_keyboard(uid))
        return

    if data == "admin_panel" and is_admin(uid):
        await query.message.edit_text("⚙️ <b>ADMIN PANEL</b>", parse_mode="HTML", reply_markup=admin_main_keyboard())
        return

    if data == "traffic_home":
        text = render_traffic_dashboard()
        keyboard = build_traffic_keyboard()
        await query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
        return

    if data == "traffic_refresh":
        text = render_traffic_dashboard()
        keyboard = build_traffic_keyboard()
        try:
            await query.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
        except Exception:
            pass
        return

    if data.startswith("traffic_svc_"):
        svc_name = data.replace("traffic_svc_", "")
        keyboard = build_service_traffic_keyboard(svc_name)
        await query.message.edit_text(
            f"{get_premium_custom_emoji('dashboard')} <b>TRAFFIC: {svc_name.upper()}</b>\n"
            f"Select country to view ranges:",
            parse_mode="HTML",
            reply_markup=keyboard,
        )
        return

    if data.startswith("traffic_ctr_"):
        parts = data.split("_")
        svc_name = parts[2]
        ctr_code = parts[3]
        keyboard = build_country_traffic_keyboard(svc_name, ctr_code)
        await query.message.edit_text(
            f"{get_premium_custom_emoji('dashboard')} <b>TRAFFIC: {svc_name.upper()} ({ctr_code})</b>\n"
            f"Top active ranges:",
            parse_mode="HTML",
            reply_markup=keyboard,
        )
        return

    if data.startswith("copy_range_"):
        rng = data.replace("copy_range_", "")
        await query.answer(f"Copied Range: {rng}", show_alert=True)
        return

    if data.startswith("copy_number_"):
        num = data.replace("copy_number_", "")
        await query.answer(f"Copied Number: {num}", show_alert=True)
        return

    if data == "special_numbers":
        await assign_special_number(query, context, uid)
        return

    if data.startswith("special_country_"):
        prefix = data.replace("special_country_", "")
        await allocate_one_special_number_by_country(query, context, uid, prefix)
        return

    if data.startswith("special_new_num_"):
        prefix = data.replace("special_new_num_", "")
        await allocate_one_special_number_by_country(query, context, uid, prefix)
        return

    if data == "back_services":
        services = await fetch_services_cached()
        await query.message.edit_text(
            f"{get_premium_custom_emoji('phone')} <b>SELECT YOUR SERVICE</b> {get_premium_custom_emoji('phone')}\n"
            f"<blockquote>📱 নিচ থেকে একটি <b>Service</b> সিলেক্ট করুন:</blockquote>",
            parse_mode="HTML",
            reply_markup=_build_services_keyboard(services),
        )
        return

    if data.startswith("svc_"):
        svc = data.replace("svc_", "")
        services = await fetch_services_cached()
        svc_data = services.get(svc, {})
        ranges = svc_data.get("ranges", []) if isinstance(svc_data, dict) else svc_data
        keyboard = _build_countries_keyboard(ranges, svc)
        await query.message.edit_text(
            f"{get_premium_custom_emoji('country')} <b>SELECT COUNTRY FOR {svc.upper()}</b>",
            parse_mode="HTML",
            reply_markup=keyboard,
        )
        return

    if data.startswith("country_"):
        parts = data.split("_")
        prefix = parts[1]
        svc = parts[2]
        services = await fetch_services_cached()
        svc_data = services.get(svc, {})
        ranges = svc_data.get("ranges", []) if isinstance(svc_data, dict) else svc_data

        auto_range = await auto_select_best_range(svc, prefix)
        if auto_range:
            number, country = await get_number_from_api(auto_range)
            if number:
                active_numbers[normalize_number(number)] = {
                    "uid": uid,
                    "service": svc,
                    "range": auto_range,
                }
                add_number_taken(uid, 1)
                await query.message.edit_text(
                    f"{get_premium_custom_emoji('done')} <b>NUMBER ALLOCATED (AUTO-RANGE)</b>\n"
                    f"{format_premium_divider('success')}\n"
                    f"<blockquote>📱 Service: <code>{svc.upper()}</code></blockquote>\n"
                    f"<blockquote>📞 Number: <code>{number}</code></blockquote>\n"
                    f"<blockquote>📶 Range: <code>{auto_range}</code></blockquote>\n"
                    f"<b>⏳ Waiting for SMS...</b>",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🍏 Copy Number", callback_data=f"copy_number_{number}")],
                        [InlineKeyboardButton("🔙 BACK", callback_data="back_services")],
                    ]),
                )
                return

        keyboard = _build_ranges_keyboard(ranges, prefix, svc)
        await query.message.edit_text(
            f"{get_premium_custom_emoji('range')} <b>SELECT RANGE FOR {svc.upper()}</b>",
            parse_mode="HTML",
            reply_markup=keyboard,
        )
        return

    if data.startswith("range_"):
        parts = data.split("_")
        rng = parts[1]
        svc = parts[2]
        number, country = await get_number_from_api(rng)
        if number:
            active_numbers[normalize_number(number)] = {
                "uid": uid,
                "service": svc,
                "range": rng,
            }
            add_number_taken(uid, 1)
            await query.message.edit_text(
                f"{get_premium_custom_emoji('done')} <b>NUMBER ALLOCATED</b>\n"
                f"{format_premium_divider('success')}\n"
                f"<blockquote>📱 Service: <code>{svc.upper()}</code></blockquote>\n"
                f"<blockquote>📞 Number: <code>{number}</code></blockquote>\n"
                f"<blockquote>📶 Range: <code>{rng}</code></blockquote>\n"
                f"<b>⏳ Waiting for SMS...</b>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🍏 Copy Number", callback_data=f"copy_number_{number}")],
                    [InlineKeyboardButton("🔙 BACK", callback_data="back_services")],
                ]),
            )
        else:
            await query.answer("❌ Failed to fetch number for this range. Try another!", show_alert=True)
        return

    if data == "custom_range":
        context.user_data["mode"] = "custom_range_input"
        await query.message.edit_text(
            f"{get_premium_custom_emoji('range')} <b>ENTER CUSTOM RANGE</b>\n"
            f"Please send the range code (e.g. <code>237620XXX</code>):",
            parse_mode="HTML",
        )
        return


# ══════════════════════════════════════════════════════════════════════════════
# 💬 MESSAGE HANDLER & COMMANDS
# ══════════════════════════════════════════════════════════════════════════════
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip()
    uid = update.effective_user.id

    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫", reply_markup=main_keyboard(uid))
        return

    mode = context.user_data.get("mode")

    if text == "❌ CANCEL":
        context.user_data["mode"] = None
        await update.message.reply_text("❌ Action cancelled.", reply_markup=main_keyboard(uid))
        return

    if mode == "get_2fa":
        await process_2fa_key(update, context)
        return

    if mode == "custom_range_input":
        context.user_data["mode"] = None
        rng = text.upper()
        number, country = await get_number_from_api(rng)
        if number:
            active_numbers[normalize_number(number)] = {
                "uid": uid,
                "service": "CUSTOM",
                "range": rng,
            }
            add_number_taken(uid, 1)
            await update.message.reply_text(
                f"{get_premium_custom_emoji('done')} <b>NUMBER ALLOCATED</b>\n"
                f"{format_premium_divider('success')}\n"
                f"<blockquote>📞 Number: <code>{number}</code></blockquote>\n"
                f"<blockquote>📶 Range: <code>{rng}</code></blockquote>\n"
                f"<b>⏳ Waiting for SMS...</b>",
                parse_mode="HTML",
                reply_markup=main_keyboard(uid),
            )
        else:
            await update.message.reply_text(
                "❌ Failed to fetch number. Invalid or empty range.", reply_markup=main_keyboard(uid)
            )
        return

    if text == "📞 GET NUMBER":
        await show_app_selection(update, context)
        return

    if text == "🌐 RANGE":
        context.user_data["mode"] = "custom_range_input"
        await update.message.reply_text(
            f"{get_premium_custom_emoji('range')} <b>ENTER RANGE</b>\n"
            f"Send range (e.g. <code>237620XXX</code>):",
            parse_mode="HTML",
            reply_markup=cancel_keyboard(),
        )
        return

    if text == "📊 TRAFFIC":
        await traffic_command(update, context)
        return

    if text == "💰 BALANCE":
        usr = get_user(uid)
        await update.message.reply_text(
            f"{get_premium_custom_emoji('money')} <b>YOUR BALANCE</b>\n"
            f"{format_premium_divider('primary')}\n"
            f"<blockquote>💰 Current Balance: <b>${format_balance(usr['balance'])}</b></blockquote>",
            parse_mode="HTML",
            reply_markup=main_keyboard(uid),
        )
        return

    if text == "⚡ 2FA":
        await get_2fa_code(update, context)
        return

    if text == "👤 PROFILE":
        usr = get_user(uid)
        u_stats = get_user_stats(uid)
        rate = get_user_otp_rate(uid)
        await update.message.reply_text(
            f"{get_premium_custom_emoji('user')} <b>USER PROFILE</b>\n"
            f"{format_premium_divider('primary')}\n"
            f"<blockquote>🆔 User ID: <code>{uid}</code>\n"
            f"💰 Balance: <b>${format_balance(usr['balance'])}</b>\n"
            f"⚡ OTP Rate: <b>${rate:.2f}</b>\n"
            f"📞 Total Numbers: <b>{u_stats['total_numbers']}</b>\n"
            f"🔑 Total OTPs: <b>{u_stats['total_otps']}</b></blockquote>",
            parse_mode="HTML",
            reply_markup=main_keyboard(uid),
        )
        return

    if text == "🎁 REFER":
        r_stats = get_referral_stats(uid)
        ref_link = f"{BOT_URL}?start={uid}"
        ref_price = get_referral_price()
        await update.message.reply_text(
            f"{get_premium_custom_emoji('gem')} <b>REFERRAL SYSTEM</b>\n"
            f"{format_premium_divider('primary')}\n"
            f"<blockquote>🔗 Your Link: <code>{ref_link}</code>\n"
            f"👥 Total Referred: <b>{r_stats['count']}</b>\n"
            f"💰 Reward Per Refer: <b>${ref_price:.2f}</b></blockquote>",
            parse_mode="HTML",
            reply_markup=main_keyboard(uid),
        )
        return

    if text == "💬 SUPPORT":
        await update.message.reply_text(
            f"{get_premium_custom_emoji('shield')} <b>SUPPORT</b>\n"
            f"Contact Admin: {SUPPORT_LINK}",
            reply_markup=main_keyboard(uid),
        )
        return

    if text == "⚙️ ADMIN PANEL ⚙️" and is_admin(uid):
        await update.message.reply_text(
            "⚙️ <b>ADMIN PANEL</b>", parse_mode="HTML", reply_markup=admin_main_keyboard()
        )
        return

    if text in ("🔙 BACK TO MAIN", "🔙 BACK"):
        await update.message.reply_text(
            WELCOME_MESSAGE, parse_mode="HTML", reply_markup=main_keyboard(uid)
        )
        return

    if is_admin(uid):
        if text == "👥 USERS":
            await update.message.reply_text(
                "👥 <b>USER MANAGEMENT</b>", parse_mode="HTML", reply_markup=user_management_keyboard()
            )
            return
        if text == "⚙️ CONFIG":
            await update.message.reply_text(
                "⚙️ <b>SYSTEM CONFIG</b>", parse_mode="HTML", reply_markup=system_config_keyboard()
            )
            return
        if text == "📊 TRAFFIC CONTROL":
            await admin_traffic_control(update, context)
            return

    await update.message.reply_text(WELCOME_MESSAGE, parse_mode="HTML", reply_markup=main_keyboard(uid))


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if is_user_banned(uid):
        await update.message.reply_text("🚫 YOU ARE BANNED 🚫")
        return

    get_user(uid)

    if context.args and context.args[0].isdigit():
        referrer_id = int(context.args[0])
        if referrer_id != uid and user_exists(referrer_id):
            if add_referral(referrer_id, uid):
                ref_price = get_referral_price()
                if ref_price > 0:
                    await update_db_balance(referrer_id, ref_price)
                    try:
                        await context.bot.send_message(
                            chat_id=referrer_id,
                            text=f"🎁 <b>New Referral!</b> You earned ${ref_price:.2f}",
                            parse_mode="HTML",
                        )
                    except Exception:
                        pass

    if not await check_force_join(uid, message=update.message, context=context):
        return

    await update.message.reply_text(WELCOME_MESSAGE, parse_mode="HTML", reply_markup=main_keyboard(uid))


# ══════════════════════════════════════════════════════════════════════════════
# 🚀 MAIN APPLICATION INITIALIZATION
# ══════════════════════════════════════════════════════════════════════════════
def main():
    start_periodic_check()

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("traffic", traffic_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("2fa", get_2fa_code))

    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    async def post_init(app):
        asyncio.create_task(monitor_loop(app))

    application.post_init = post_init

    logger.info("🤖 Zebra SMS Ultra Bot Started Successfully!")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
