import os
import sys
import logging
from typing import Dict, Optional
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# ============================================
# تنظیمات اولیه
# ============================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logger.error("❌ BOT_TOKEN در Environment Variables یافت نشد!")
    sys.exit("لطفاً BOT_TOKEN را در متغیرهای محیطی تنظیم کنید.")

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# ============================================
# جدول Mapping مورس - فارسی و انگلیسی
# ============================================

# جدول تبدیل حروف فارسی به مورس
PERSIAN_TO_MORSE = {
    'ا': '.-',    'ب': '-...',  'پ': '.--.',  'ت': '-',     'ث': '...-',
    'ج': '.---',  'چ': '---.',  'ح': '....',  'خ': '---',   'د': '-..',
    'ذ': '..-',   'ر': '.-.',   'ز': '--..',  'ژ': '--.-',  'س': '...',
    'ش': '----',  'ص': '-.--',  'ض': '..--',  'ط': '..-',   'ظ': '-..-',
    'ع': '.-.-',  'غ': '--.',   'ف': '..-.',  'ق': '--.-',  'ک': '-.-',
    'گ': '--.',   'ل': '.-..',  'م': '--',    'ن': '-.',    'و': '.--',
    'ه': '....',  'ی': '..'
}

# جدول تبدیل حروف انگلیسی به مورس (International Morse Code)
ENGLISH_TO_MORSE = {
    'a': '.-',    'b': '-...',  'c': '-.-.',  'd': '-..',   'e': '.',
    'f': '..-.',  'g': '--.',   'h': '....',  'i': '..',    'j': '.---',
    'k': '-.-',   'l': '.-..',  'm': '--',    'n': '-.',    'o': '---',
    'p': '.--.',  'q': '--.-',  'r': '.-.',   's': '...',   't': '-',
    'u': '..-',   'v': '...-',  'w': '.--',   'x': '-..-',  'y': '-.--',
    'z': '--..'
}

# جدول تبدیل اعداد به مورس
NUMBERS_TO_MORSE = {
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.'
}

# جدول تبدیل علائم رایج به مورس
SYMBOLS_TO_MORSE = {
    '.': '.-.-.-', ',': '--..--', '?': '..--..', '!': '-.-.--',
    ':': '---...', ';': '-.-.-.', '-': '-....-', '/': '-..-.',
    ' ': '/'  # فاصله بین کلمات
}

# ترکیب تمام جداول برای تبدیل متن به مورس
ALL_TO_MORSE = {**PERSIAN_TO_MORSE, **ENGLISH_TO_MORSE, **NUMBERS_TO_MORSE, **SYMBOLS_TO_MORSE}

# ساخت جدول معکوس برای تبدیل مورس به متن
REVERSE_MORSE_MAP = {v: k for k, v in ALL_TO_MORSE.items()}

# ============================================
# مدیریت حالت‌های FSM
# ============================================

class MorseStates(StatesGroup):
    waiting_for_text_to_morse = State()
    waiting_for_morse_to_text = State()

# ============================================
# دکمه‌های Inline Keyboard
# ============================================

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔤 متن ➜ مورس", callback_data="to_morse")],
            [InlineKeyboardButton(text="📡 مورس ➜ متن", callback_data="to_text")],
            [InlineKeyboardButton(text="❓ راهنما", callback_data="help")]
        ]
    )

def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 برگشت به منوی اصلی", callback_data="back_to_main")]
        ]
    )

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ لغو")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

# ============================================
# توابع تبدیل
# ============================================

def text_to_morse(text: str) -> str:
    """تبدیل متن به کد مورس"""
    result = []
    for char in text:
        if char in ALL_TO_MORSE:
            result.append(ALL_TO_MORSE[char])
        else:
            result.append('?')  # کاراکتر پشتیبانی نمی‌شود
    return ' '.join(result)

def morse_to_text(morse: str) -> str:
    """تبدیل کد مورس به متن"""
    morse_parts = morse.split(' ')
    result = []
    
    for code in morse_parts:
        code = code.strip()
        if not code:
            continue
        if code in REVERSE_MORSE_MAP:
            result.append(REVERSE_MORSE_MAP[code])
        else:
            result.append('?')  # کد نامعتبر
    
    return ''.join(result)

def validate_morse_code(morse: str) -> bool:
    """اعتبارسنجی کد مورس"""
    parts = morse.split(' ')
    for part in parts:
        part = part.strip()
        if part and part not in REVERSE_MORSE_MAP:
            return False
    return True

# ============================================
# هندلرهای دستورات
# ============================================

@dp.message_handler(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """هندلر دستور /start"""
    await state.finish()
    welcome_text = (
        "👋 سلام! به ربات تبدیل متن به کد مورس خوش آمدید.\n\n"
        "من می‌توانم متن شما را به کد مورس تبدیل کنم یا برعکس.\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
    )
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu_keyboard()
    )

@dp.message_handler(Command("help"))
async def cmd_help(message: types.Message, state: FSMContext):
    """هندلر دستور /help"""
    await state.finish()
    help_text = (
        "🤖 *راهنمای ربات مورس*\n\n"
        "🔹 *متن ➜ مورس*: متن خود را ارسال کنید تا به کد مورس تبدیل شود.\n"
        "🔹 *مورس ➜ متن*: کد مورس را ارسال کنید تا به متن تبدیل شود.\n\n"
        "📌 *پشتیبانی از حروف:*\n"
        "• فارسی: ا ب پ ت ث ج چ ح خ د ذ ر ز ژ س ش ص ض ط ظ ع غ ف ق ک گ ل م ن و ه ی\n"
        "• انگلیسی: a-z\n"
        "• اعداد: 0-9\n"
        "• علائم: . , ? ! : ; - /\n\n"
        "📌 *نکات:*\n"
        "• برای فاصله بین کلمات از '/' استفاده کنید.\n"
        "• کد مورس را با فاصله جدا کنید.\n\n"
        "برای شروع مجدد، دستور /start را ارسال کنید."
    )
    await message.answer(help_text, parse_mode="Markdown", reply_markup=get_main_menu_keyboard())

@dp.callback_query_handler(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    """برگشت به منوی اصلی"""
    await state.finish()
    await callback.message.delete()
    await callback.message.answer(
        "🔙 به منوی اصلی بازگشتید.\nلطفاً یکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "help")
async def help_callback(callback: types.CallbackQuery, state: FSMContext):
    """راهنما از طریق دکمه"""
    await cmd_help(callback.message, state)
    await callback.answer()

# ============================================
# هندلرهای انتخاب حالت
# ============================================

@dp.callback_query_handler(lambda c: c.data == "to_morse")
async def start_text_to_morse(callback: types.CallbackQuery, state: FSMContext):
    """شروع فرآیند تبدیل متن به مورس"""
    await state.set_state(MorseStates.waiting_for_text_to_morse)
    await callback.message.delete()
    await callback.message.answer(
        "📝 لطفاً متن خود را ارسال کنید.\n\n"
        "پشتیبانی از حروف فارسی، انگلیسی، اعداد و علائم . , ? ! : ; - /",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "to_text")
async def start_morse_to_text(callback: types.CallbackQuery, state: FSMContext):
    """شروع فرآیند تبدیل مورس به متن"""
    await state.set_state(MorseStates.waiting_for_morse_to_text)
    await callback.message.delete()
    await callback.message.answer(
        "📡 لطفاً کد مورس خود را ارسال کنید.\n\n"
        "مثال: .... . .-.. .-.. --- / .-- --- .-. .-.. -..\n"
        "برای فاصله بین کلمات از '/' استفاده کنید.",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

# ============================================
# هندلرهای دریافت پیام
# ============================================

@dp.message_handler(state=MorseStates.waiting_for_text_to_morse)
async def handle_text_to_morse(message: types.Message, state: FSMContext):
    """پردازش متن دریافتی و تبدیل به مورس"""
    if message.text == "❌ لغو":
        await state.finish()
        await message.answer(
            "❌ عملیات لغو شد.",
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer(
            "به منوی اصلی بازگشتید.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    try:
        text = message.text.strip()
        if not text:
            await message.answer(
                "⚠️ متن خالی ارسال شده است. لطفاً متن معتبر ارسال کنید.",
                reply_markup=get_cancel_keyboard()
            )
            return
        
        morse_result = text_to_morse(text)
        result_text = f"✅ *نتیجه تبدیل:*\n\n```\n{morse_result}\n```"
        
        if len(result_text) > 4000:
            parts = [result_text[i:i+4000] for i in range(0, len(result_text), 4000)]
            for part in parts:
                await message.answer(part, parse_mode="Markdown")
        else:
            await message.answer(result_text, parse_mode="Markdown")
        
        await message.answer(
            "🔁 دوباره متن خود را ارسال کنید یا از دکمه زیر استفاده کنید:",
            reply_markup=get_back_keyboard()
        )
        
    except Exception as e:
        logger.error(f"خطا در تبدیل متن به مورس: {e}")
        await message.answer(
            "⚠️ خطایی در پردازش رخ داد. لطفاً دوباره تلاش کنید.",
            reply_markup=get_cancel_keyboard()
        )

@dp.message_handler(state=MorseStates.waiting_for_morse_to_text)
async def handle_morse_to_text(message: types.Message, state: FSMContext):
    """پردازش کد مورس دریافتی و تبدیل به متن"""
    if message.text == "❌ لغو":
        await state.finish()
        await message.answer(
            "❌ عملیات لغو شد.",
            reply_markup=ReplyKeyboardRemove()
        )
        await message.answer(
            "به منوی اصلی بازگشتید.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    try:
        morse_text = message.text.strip()
        if not morse_text:
            await message.answer(
                "⚠️ کد مورس خالی ارسال شده است. لطفاً کد معتبر ارسال کنید.",
                reply_markup=get_cancel_keyboard()
            )
            return
        
        if not validate_morse_code(morse_text):
            await message.answer(
                "❌ کد مورس نامعتبر است. لطفاً کد را بررسی کنید.\n\n"
                "مثال: .... . .-.. .-.. --- / .-- --- .-. .-.. -..",
                reply_markup=get_cancel_keyboard()
            )
            return
        
        text_result = morse_to_text(morse_text)
        result_text = f"✅ *نتیجه تبدیل:*\n\n```\n{text_result}\n```"
        
        if len(result_text) > 4000:
            parts = [result_text[i:i+4000] for i in range(0, len(result_text), 4000)]
            for part in parts:
                await message.answer(part, parse_mode="Markdown")
        else:
            await message.answer(result_text, parse_mode="Markdown")
        
        await message.answer(
            "🔁 دوباره کد مورس را ارسال کنید یا از دکمه زیر استفاده کنید:",
            reply_markup=get_back_keyboard()
        )
        
    except Exception as e:
        logger.error(f"خطا در تبدیل مورس به متن: {e}")
        await message.answer(
            "⚠️ خطایی در پردازش رخ داد. لطفاً دوباره تلاش کنید.",
            reply_markup=get_cancel_keyboard()
        )

@dp.message_handler()
async def handle_other_messages(message: types.Message, state: FSMContext):
    """مدیریت پیام‌های غیرمنتظره"""
    await message.answer(
        "❓ لطفاً از دکمه‌های موجود استفاده کنید یا دستور /start را ارسال کنید.",
        reply_markup=get_main_menu_keyboard()
    )

# ============================================
# اجرای ربات
# ============================================

if __name__ == "__main__":
    from aiogram import executor
    try:
        logger.info("🚀 ربات در حال اجرا...")
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        logger.error(f"❌ خطا در اجرای ربات: {e}")
        sys.exit(1)
