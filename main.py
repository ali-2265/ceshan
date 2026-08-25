import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatMemberStatus

# ====================== بارگذاری متغیرهای محیطی ======================
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
REQUIRED_CHANNEL = os.getenv('REQUIRED_CHANNEL', '@your_channel_username')

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN not found in environment variables!")

# ====================== تنظیمات لاگ ======================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ====================== دیکشنری کش برای کاربران تأییدشده ======================
user_verified = {}

# ====================== توابع کمکی ======================
async def is_user_member(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    بررسی عضویت واقعی کاربر در کانال از طریق Telegram API
    """
    try:
        chat_member = await context.bot.get_chat_member(
            chat_id=REQUIRED_CHANNEL,
            user_id=user_id
        )
        status = chat_member.status
        logger.info(f"User {user_id} status in channel: {status}")
        
        # وضعیت‌های معتبر برای عضویت
        valid_statuses = [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        ]
        
        return status in valid_statuses
    except Exception as e:
        logger.error(f"Error checking membership for user {user_id}: {e}")
        return False

async def get_channel_link() -> str:
    """دریافت لینک کانال"""
    channel = REQUIRED_CHANNEL.replace('@', '').strip()
    if channel.startswith('-100'):  # اگر Channel ID عددی باشد
        return f"https://t.me/{channel}"
    return f"https://t.me/{channel}"

async def send_join_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ارسال پیام عضویت اجباری با دکمه‌های شیشه‌ای
    """
    channel_link = await get_channel_link()
    
    keyboard = [
        [InlineKeyboardButton("📢 JOIN CHANNEL", url=channel_link)],
        [InlineKeyboardButton("✅ FINISH", callback_data="check_membership")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "🔒 *به ربات خوش آمدید!*\n\n"
        "برای استفاده از امکانات ربات، لطفاً ابتدا در کانال زیر عضو شوید:\n"
        f"📌 {REQUIRED_CHANNEL}\n\n"
        "✅ پس از عضویت، روی دکمه FINISH کلیک کنید."
    )
    
    await update.message.reply_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def edit_join_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ویرایش پیام عضویت اجباری (برای زمانی که کاربر از دکمه استفاده می‌کند)
    """
    query = update.callback_query
    channel_link = await get_channel_link()
    
    keyboard = [
        [InlineKeyboardButton("📢 JOIN CHANNEL", url=channel_link)],
        [InlineKeyboardButton("✅ FINISH", callback_data="check_membership")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "🔒 *به ربات خوش آمدید!*\n\n"
        "برای استفاده از امکانات ربات، لطفاً ابتدا در کانال زیر عضو شوید:\n"
        f"📌 {REQUIRED_CHANNEL}\n\n"
        "✅ پس از عضویت، روی دکمه FINISH کلیک کنید."
    )
    
    await query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ====================== پنل اصلی ربات ======================
async def show_main_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    نمایش پنل اصلی ربات بعد از تأیید عضویت
    """
    await update.message.reply_text(
        "🎯 *پنل اصلی ربات*\n\n"
        "✅ عضویت شما با موفقیت تأیید شد!\n"
        "از امکانات زیر استفاده کنید:\n\n"
        "/help - راهنما\n"
        "/info - اطلاعات ربات\n"
        "/start - نمایش این پیام",
        parse_mode='Markdown'
    )

async def show_main_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    نمایش پنل اصلی از طریق Callback (بعد از کلیک FINISH)
    """
    query = update.callback_query
    await query.message.delete()
    await query.message.reply_text(
        "🎯 *پنل اصلی ربات*\n\n"
        "✅ عضویت شما با موفقیت تأیید شد!\n"
        "از امکانات زیر استفاده کنید:\n\n"
        "/help - راهنما\n"
        "/info - اطلاعات ربات\n"
        "/start - نمایش این پیام",
        parse_mode='Markdown'
    )

# ====================== هندلرهای اصلی ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    هندلر دستور /start
    """
    user_id = update.effective_user.id
    
    # بررسی عضویت کاربر
    if await is_user_member(user_id, context):
        user_verified[user_id] = True
        await show_main_panel(update, context)
    else:
        await send_join_message(update, context)

async def check_membership_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    هندلر دکمه FINISH - بررسی لحظه‌ای عضویت
    """
    query = update.callback_query
    user_id = update.effective_user.id
    
    await query.answer()
    
    # بررسی عضویت از طریق API
    if await is_user_member(user_id, context):
        user_verified[user_id] = True
        await show_main_panel_callback(update, context)
        logger.info(f"✅ User {user_id} verified successfully")
    else:
        await query.answer(
            text="❌ You haven't joined the channel yet! Please join first.",
            show_alert=True
        )
        logger.info(f"❌ User {user_id} membership check failed")

# ====================== کامندهای نمونه ======================
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    کامند /info - فقط برای کاربران عضو
    """
    user_id = update.effective_user.id
    
    # بررسی عضویت
    if not await is_user_member(user_id, context):
        await send_join_message(update, context)
        return
    
    await update.message.reply_text(
        "ℹ️ *اطلاعات ربات*\n\n"
        "🤖 نام: عضویت اجباری نمونه\n"
        "📌 نسخه: 1.0.0\n"
        "👨‍💻 توسعه‌دهنده: شما",
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    کامند /help - فقط برای کاربران عضو
    """
    user_id = update.effective_user.id
    
    # بررسی عضویت
    if not await is_user_member(user_id, context):
        await send_join_message(update, context)
        return
    
    await update.message.reply_text(
        "🆘 *راهنمای ربات*\n\n"
        "/start - شروع و تأیید عضویت\n"
        "/info - اطلاعات ربات\n"
        "/help - نمایش این راهنما",
        parse_mode='Markdown'
    )

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    هندلر برای کامندهای ناشناخته
    """
    user_id = update.effective_user.id
    
    # بررسی عضویت
    if not await is_user_member(user_id, context):
        await send_join_message(update, context)
        return
    
    await update.message.reply_text(
        "❌ کامند ناشناخته!\n"
        "از /help برای مشاهده کامندهای موجود استفاده کنید."
    )

# ====================== تابع اصلی ======================
def main():
    """
    راه‌اندازی ربات
    """
    # ایجاد اپلیکیشن
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ========== ثبت هندلرها ==========
    # کامندها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Callback دکمه FINISH
    application.add_handler(CallbackQueryHandler(check_membership_callback, pattern="check_membership"))
    
    # هندلر برای کامندهای ناشناخته
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    # ========== راه‌اندازی ==========
    logger.info("🚀 Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
