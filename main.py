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
        "🔒 *برای استفاده از ربات، لطفاً عضو کانال شوید*\n\n"
        f"📌 کانال: {REQUIRED_CHANNEL}\n\n"
        "✅ پس از عضویت، روی دکمه FINISH کلیک کنید."
    )
    
    await update.message.reply_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def send_join_message_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ارسال پیام عضویت اجباری از طریق Callback (برای زمانی که کاربر روی دکمه‌ای کلیک می‌کند)
    """
    query = update.callback_query
    channel_link = await get_channel_link()
    
    keyboard = [
        [InlineKeyboardButton("📢 JOIN CHANNEL", url=channel_link)],
        [InlineKeyboardButton("✅ FINISH", callback_data="check_membership")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        "🔒 *برای استفاده از ربات، لطفاً عضو کانال شوید*\n\n"
        f"📌 کانال: {REQUIRED_CHANNEL}\n\n"
        "✅ پس از عضویت، روی دکمه FINISH کلیک کنید."
    )
    
    await query.message.reply_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    await query.answer()

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
        "🔒 *برای استفاده از ربات، لطفاً عضو کانال شوید*\n\n"
        f"📌 کانال: {REQUIRED_CHANNEL}\n\n"
        "✅ پس از عضویت، روی دکمه FINISH کلیک کنید."
    )
    
    await query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    await query.answer()

# ====================== دکوراتور بررسی عضویت ======================
async def membership_required(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    تابع کمکی برای بررسی عضویت قبل از اجرای هر قابلیت
    """
    user_id = update.effective_user.id
    
    # بررسی عضویت لحظه‌ای از طریق API
    if await is_user_member(user_id, context):
        return True
    
    # کاربر عضو نیست - نمایش پیام عضویت
    logger.info(f"User {user_id} is not a member. Showing join message.")
    
    if update.message:
        await send_join_message(update, context)
    elif update.callback_query:
        await send_join_message_callback(update, context)
    
    return False

# ====================== هندلرهای اصلی ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    هندلر دستور /start
    """
    user_id = update.effective_user.id
    logger.info(f"User {user_id} started the bot")
    
    # بررسی عضویت لحظه‌ای
    if await is_user_member(user_id, context):
        # کاربر عضو است - نمایش پنل اصلی
        await show_main_panel(update, context)
    else:
        # کاربر عضو نیست - نمایش پیام عضویت
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
        # کاربر عضو است - حذف پیام عضویت و نمایش پنل
        await query.message.delete()
        await show_main_panel_callback(update, context)
        logger.info(f"✅ User {user_id} verified successfully")
    else:
        # کاربر عضو نیست - نمایش خطا
        await query.answer(
            text="❌ Please join the channel first.",
            show_alert=True
        )
        logger.info(f"❌ User {user_id} membership check failed")

async def show_main_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    نمایش پنل اصلی ربات بعد از تأیید عضویت
    """
    await update.message.reply_text(
        "🎯 *پنل اصلی ربات*\n\n"
        "✅ عضویت شما با موفقیت تأیید شد!\n"
        "از امکانات زیر استفاده کنید:\n\n"
        "/help - راهنما\n"
        "/info - اطلاعات ربات",
        parse_mode='Markdown'
    )

async def show_main_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    نمایش پنل اصلی از طریق Callback (بعد از کلیک FINISH)
    """
    query = update.callback_query
    await query.message.reply_text(
        "🎯 *پنل اصلی ربات*\n\n"
        "✅ عضویت شما با موفقیت تأیید شد!\n"
        "از امکانات زیر استفاده کنید:\n\n"
        "/help - راهنما\n"
        "/info - اطلاعات ربات",
        parse_mode='Markdown'
    )

# ====================== کامندهای نمونه (با بررسی عضویت) ======================
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    کامند /info - فقط برای کاربران عضو
    """
    # بررسی عضویت قبل از اجرا
    if not await membership_required(update, context):
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
    # بررسی عضویت قبل از اجرا
    if not await membership_required(update, context):
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
    # بررسی عضویت قبل از اجرا
    if not await membership_required(update, context):
        return
    
    await update.message.reply_text(
        "❌ کامند ناشناخته!\n"
        "از /help برای مشاهده کامندهای موجود استفاده کنید."
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    هندلر عمومی برای تمام Callbackهای ربات (به جز FINISH)
    """
    query = update.callback_query
    user_id = update.effective_user.id
    
    # بررسی عضویت قبل از اجرا
    if not await is_user_member(user_id, context):
        # کاربر عضو نیست - نمایش پیام عضویت
        await send_join_message_callback(update, context)
        return
    
    # اینجا کد مربوط به سایر دکمه‌های ربات قرار می‌گیرد
    await query.answer("✅ شما عضو کانال هستید!")

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
    
    # هندلر دکمه FINISH
    application.add_handler(CallbackQueryHandler(check_membership_callback, pattern="check_membership"))
    
    # هندلر برای سایر Callbackها (اگر در ربات شما وجود دارند)
    application.add_handler(CallbackQueryHandler(handle_callback, pattern="^(?!check_membership$).*$"))
    
    # هندلر برای کامندهای ناشناخته
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    # ========== راه‌اندازی ==========
    logger.info("🚀 Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
