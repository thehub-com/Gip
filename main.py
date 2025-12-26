import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from supabase import create_client
from dotenv import load_dotenv

# ====== ENV ======
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# ====== BOT ======
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ====== DB ======
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ====== LOGGING ======
logging.basicConfig(level=logging.INFO)


# ====== /start ======
@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    tg_id = message.from_user.id
    username = message.from_user.username

    # регистрация / обновление пользователя
    supabase.table("users").upsert({
        "tg_id": tg_id,
        "username": username,
        "gip": 0
    }).execute()

    kb = types.InlineKeyboardMarkup(row_width=2)

    kb.add(
        types.InlineKeyboardButton(
            text="🛒 Маркетплейс",
            web_app=types.WebAppInfo(url="https://example.com/market")
        ),
        types.InlineKeyboardButton(
            text="🎁 Кейсы",
            callback_data="cases"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            text="👤 Профиль",
            web_app=types.WebAppInfo(url="https://example.com/profile")
        ),
        types.InlineKeyboardButton(
            text="💎 Купить GIP",
            callback_data="buy_gip"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            text="🆘 Поддержка",
            url="https://t.me/gock_admin_bot"
        )
    )

    await message.answer(
        "🌌 **GIP — GOCK Interaction Points**\n\n"
        "Добро пожаловать в экосистему GIP:\n\n"
        "• 🎁 Кейсы с подарками и NFT\n"
        "• 🛒 Маркетплейс пользователей\n"
        "• 👤 Кастомный профиль\n"
        "• 💎 Внутренняя валюта GIP\n\n"
        "👇 Выбери действие:",
        reply_markup=kb,
        parse_mode="Markdown"
    )


# ====== КЕЙСЫ ======
@dp.callback_query_handler(text="cases")
async def cases_menu(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer(
        "🎁 **Кейсы GIP**\n\n"
        "Открывай кейсы и получай подарки разной редкости.\n"
        "🎰 Анимации как в Telegram\n"
        "📉 Шансы честные\n\n"
        "⏳ Скоро доступно",
        parse_mode="Markdown"
    )


# ====== ПОКУПКА GIP ======
@dp.callback_query_handler(text="buy_gip")
async def buy_gip(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer(
        "💎 **Покупка GIP**\n\n"
        "Ты сможешь купить GIP за ⭐ Telegram Stars\n"
        "или получить за активность.\n\n"
        "🔒 Платежи скоро будут подключены",
        parse_mode="Markdown"
    )


# ====== START BOT ======
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
