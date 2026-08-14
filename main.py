import sys
sys.path.append('/opt/render/project/src')

import logging
from telegram import Update
...
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from telegram.ext import ContextTypes

from config import Config
from utils import SessionManager
from handlers import Handlers, PHONE, CODE, PASSWORD

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ خطایی رخ داده است. لطفاً دوباره تلاش کنید."
        )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ عملیات لغو شد.\n"
        "برای شروع مجدد /start را ارسال کنید."
    )
    return ConversationHandler.END

async def post_init(application: Application):
    logger.info("Bot started successfully!")

def main():
    config = Config()
    session_manager = SessionManager(config)
    handlers = Handlers(session_manager)
    
    application = Application.builder().token(config.BOT_TOKEN).post_init(post_init).build()
    
    create_session_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.create_session_start, pattern='^create_session$')],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_phone)],
            CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_code)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_code)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    send_saved_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.send_saved_start, pattern='^send_saved$')],
        states={
            'SEND_MESSAGE': [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.send_saved_message)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(CommandHandler('start', handlers.start))
    application.add_handler(create_session_conv)
    application.add_handler(send_saved_conv)
    application.add_handler(CallbackQueryHandler(handlers.list_sessions, pattern='^list_sessions$'))
    application.add_handler(CallbackQueryHandler(handlers.about, pattern='^about$'))
    application.add_handler(CallbackQueryHandler(handlers.help, pattern='^help$'))
    application.add_handler(CallbackQueryHandler(handlers.support, pattern='^support$'))
    application.add_handler(CallbackQueryHandler(handlers.back_to_menu, pattern='^back$'))
    application.add_handler(CallbackQueryHandler(handlers.send_saved_choose, pattern='^send_'))
    application.add_error_handler(error_handler)
    
    print("🤖 Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
