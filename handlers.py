from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
import re

PHONE, CODE, PASSWORD = range(3)

class Handlers:
    def __init__(self, session_manager):
        self.session_manager = session_manager
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("📱 ساخت سشن", callback_data='create_session')],
            [InlineKeyboardButton("📋 لیست سشن‌ها", callback_data='list_sessions')],
            [InlineKeyboardButton("💬 ارسال به ذخیره شده", callback_data='send_saved')],
            [InlineKeyboardButton("ℹ️ درباره ربات", callback_data='about')],
            [InlineKeyboardButton("❓ راهنما", callback_data='help')],
            [InlineKeyboardButton("🆘 پشتیبانی", callback_data='support')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🤖 **ربات ساخت سشن تلگرام**\n\n"
            "به ربات ساخت سشن خوش آمدید!\n"
            "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def about(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        text = (
            "📱 **درباره ربات**\n\n"
            "این ربات برای مدیریت و ساخت سشن‌های تلگرام طراحی شده است.\n\n"
            "✨ **ویژگی‌ها:**\n"
            "• ساخت سشن با شماره تلفن\n"
            "• ذخیره سشن‌ها به فرمت .session\n"
            "• ارسال پیام به پیام‌های ذخیره شده\n"
            "• مشاهده لیست سشن‌ها\n\n"
            "🔒 **امنیت:**\n"
            "• اطلاعات شما محلی ذخیره می‌شود\n"
            "• از پروکسی آلمان استفاده می‌کند\n"
            "• با مشخصات Windows 11 اجرا می‌شود\n\n"
            "👨‍💻 **ساخته شده با:**\n"
            "• Python + Telethon\n"
            "• python-telegram-bot"
        )
        
        await query.edit_message_text(text, parse_mode='Markdown')
        await self.show_main_menu(update, context)
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        text = (
            "❓ **راهنمای استفاده**\n\n"
            "1️⃣ **ساخت سشن:**\n"
            "• شماره تلفن خود را وارد کنید\n"
            "• کد تایید ارسال شده را وارد کنید\n"
            "• در صورت فعال بودن دو مرحله‌ای، رمز عبور را وارد کنید\n\n"
            "2️⃣ **لیست سشن‌ها:**\n"
            "• مشاهده تمام سشن‌های ساخته شده\n"
            "• اطلاعات کامل هر سشن\n\n"
            "3️⃣ **ارسال به ذخیره شده:**\n"
            "• انتخاب سشن مورد نظر\n"
            "• ارسال پیام به پیام‌های ذخیره شده\n\n"
            "⚠️ **نکات مهم:**\n"
            "• حتماً کد تایید را به درستی وارد کنید\n"
            "• سشن‌ها به صورت خودکار ذخیره می‌شوند\n"
            "• برای هر شماره فقط یک سشن ساخته می‌شود"
        )
        
        await query.edit_message_text(text, parse_mode='Markdown')
        await self.show_main_menu(update, context)
    
    async def support(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        text = (
            "🆘 **پشتیبانی**\n\n"
            "برای ارتباط با پشتیبانی و دریافت راهنمایی بیشتر، با آیدی زیر در ارتباط باشید:\n\n"
            f"👤 **پشتیبانی:** {self.session_manager.config.SUPPORT_ID}\n\n"
            "⏰ **ساعت پاسخگویی:**\n"
            "شنبه تا چهارشنبه: ۹ صبح تا ۶ عصر"
        )
        
        await query.edit_message_text(text, parse_mode='Markdown')
        await self.show_main_menu(update, context)
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("📱 ساخت سشن", callback_data='create_session')],
            [InlineKeyboardButton("📋 لیست سشن‌ها", callback_data='list_sessions')],
            [InlineKeyboardButton("💬 ارسال به ذخیره شده", callback_data='send_saved')],
            [InlineKeyboardButton("ℹ️ درباره ربات", callback_data='about')],
            [InlineKeyboardButton("❓ راهنما", callback_data='help')],
            [InlineKeyboardButton("🆘 پشتیبانی", callback_data='support')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.effective_message.reply_text(
            "📋 **منوی اصلی**\n\n"
            "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def create_session_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "📱 **ساخت سشن جدید**\n\n"
            "لطفاً شماره تلفن خود را با فرمت بین‌المللی وارد کنید:\n"
            "مثال: +989123456789\n\n"
            "⚠️ برای لغو عملیات /cancel را ارسال کنید."
        )
        return PHONE
    
    async def get_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        phone = update.message.text.strip()
        
        if not re.match(r'^\+?[0-9]{10,15}$', phone):
            await update.message.reply_text(
                "❌ شماره تلفن نامعتبر!\n"
                "لطفاً یک شماره معتبر با فرمت بین‌المللی وارد کنید.\n"
                "مثال: +989123456789"
            )
            return PHONE
        
        context.user_data['phone'] = phone
        
        await update.message.reply_text(
            f"📱 شماره {phone} ثبت شد.\n\n"
            "📨 کد تایید به تلگرام شما ارسال شد.\n"
            "لطفاً کد ۵ رقمی را وارد کنید:\n\n"
            "⚠️ برای لغو عملیات /cancel را ارسال کنید."
        )
        return CODE
    
    async def get_code(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        code = update.message.text.strip()
        
        if not code.isdigit() or len(code) != 5:
            await update.message.reply_text(
                "❌ کد تایید نامعتبر!\n"
                "لطفاً کد ۵ رقمی را به درستی وارد کنید."
            )
            return CODE
        
        context.user_data['code'] = code
        phone = context.user_data['phone']
        
        try:
            client, me = await self.session_manager.create_session(phone, code)
            
            await update.message.reply_text(
                f"✅ **سشن با موفقیت ساخته شد!**\n\n"
                f"👤 **نام:** {me.first_name}\n"
                f"🆔 **آیدی:** {me.id}\n"
                f"📱 **شماره:** {phone}\n"
                f"👤 **یوزرنیم:** @{me.username if me.username else 'ندارد'}\n\n"
                f"📁 فایل سشن در مسیر sessions/{phone}.session ذخیره شد.",
                parse_mode='Markdown'
            )
            
            return ConversationHandler.END
            
        except ValueError as e:
            await update.message.reply_text(f"❌ {str(e)}\n\nلطفاً دوباره تلاش کنید.")
            return CODE
        except Exception as e:
            await update.message.reply_text(
                f"❌ خطا در ساخت سشن: {str(e)}\n\n"
                "لطفاً دوباره تلاش کنید یا با پشتیبانی تماس بگیرید."
            )
            return CODE
    
    async def list_sessions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        sessions = self.session_manager.list_sessions()
        
        if not sessions:
            await query.edit_message_text(
                "📋 **لیست سشن‌ها**\n\n"
                "هیچ سشنی ساخته نشده است.\n"
                "برای ساخت سشن جدید از دکمه 'ساخت سشن' استفاده کنید.",
                parse_mode='Markdown'
            )
            await self.show_main_menu(update, context)
            return
        
        text = "📋 **لیست سشن‌های موجود**\n\n"
        for i, session in enumerate(sessions, 1):
            text += (
                f"{i}. 📱 **{session.get('phone', 'نامشخص')}**\n"
                f"   👤 {session.get('first_name', 'نامشخص')}\n"
                f"   🆔 {session.get('user_id', 'نامشخص')}\n"
                f"   📅 {session.get('created_at', 'نامشخص')[:10]}\n\n"
            )
        
        await query.edit_message_text(text, parse_mode='Markdown')
        await self.show_main_menu(update, context)
    
    async def send_saved_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        sessions = self.session_manager.list_sessions()
        
        if not sessions:
            await query.edit_message_text(
                "❌ هیچ سشنی موجود نیست!\n"
                "لطفاً ابتدا یک سشن بسازید."
            )
            await self.show_main_menu(update, context)
            return
        
        keyboard = []
        for session in sessions:
            phone = session.get('phone', 'نامشخص')
            name = session.get('first_name', 'نامشخص')
            keyboard.append([
                InlineKeyboardButton(
                    f"{name} ({phone})",
                    callback_data=f'send_{phone}'
                )
            ])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data='back')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "💬 **ارسال به پیام‌های ذخیره شده**\n\n"
            "لطفاً سشن مورد نظر را انتخاب کنید:",
            reply_markup=reply_markup
        )
    
    async def send_saved_choose(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        phone = query.data.replace('send_', '')
        context.user_data['send_phone'] = phone
        
        await query.edit_message_text(
            f"📱 سشن {phone} انتخاب شد.\n\n"
            "📝 لطفاً پیام مورد نظر برای ارسال به پیام‌های ذخیره شده را وارد کنید:\n\n"
            "⚠️ برای لغو عملیات /cancel را ارسال کنید."
        )
        return 'SEND_MESSAGE'
    
    async def send_saved_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message.text
        phone = context.user_data.get('send_phone')
        
        if not phone:
            await update.message.reply_text("❌ خطا: سشن انتخاب نشده است.")
            return ConversationHandler.END
        
        try:
            await self.session_manager.send_message_to_saved(phone, message)
            
            await update.message.reply_text(
                "✅ **پیام با موفقیت ارسال شد!**\n\n"
                f"📱 **سشن:** {phone}\n"
                f"💬 **پیام:** {message[:50]}{'...' if len(message) > 50 else ''}"
            )
            
            await self.show_main_menu(update, context)
            return ConversationHandler.END
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ خطا در ارسال پیام: {str(e)}\n\n"
                "لطفاً دوباره تلاش کنید."
            )
            return 'SEND_MESSAGE'
    
    async def back_to_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await self.show_main_menu(update, context)
