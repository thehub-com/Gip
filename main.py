import os
import logging

from aiogram import Bot, Dispatcher, executor, types
from supabase import create_client
from dotenv import load_dotenv

# ================= ENV =================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in env")

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)

# ================= BOT =================
bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot)

# ================= DB =================
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= HELPERS =================
def main_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=2)

    kb.add(
        types.InlineKeyboardButton(
            text="🎁 Кейсы",
            callback_data="cases"
        ),
        types.InlineKeyboardButton(
            text="👤 Профиль",
            callback_data="profile"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            text="🛒 Маркетплейс",
            web_app=types.WebAppInfo(url="https://example.com/market")
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

    return kb


# ================= /START =================
@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    tg_id = message.from_user.id
    username = message.from_user.username or "unknown"

    # регистрация / обновление пользователя
    supabase.table("users").upsert({
        "tg_id": tg_id,
        "username": username,
        "gip": 0
    }).execute()

    await message.answer(
        "🌌 **GIP — GOCK Interaction Points**\n\n"
        "Добро пожаловать в экосистему GIP:\n\n"
        "🎁 Кейсы с подарками\n"
        "🛒 Маркетплейс пользователей\n"
        "👤 Профиль и статистика\n"
        "💎 Внутренняя валюта GIP\n\n"
        "👇 Выбери действие:",
        reply_markup=main_keyboard()
    )


# ================= ПРОФИЛЬ =================
@dp.callback_query_handler(text="profile")
async def profile_handler(call: types.CallbackQuery):
    await call.answer()

    tg_id = call.from_user.id

    user = supabase.table("users") \
        .select("*") \
        .eq("tg_id", tg_id) \
        .single() \
        .execute()

    data = user.data or {}
    gip = data.get("gip", 0)

    await call.message.answer(
        f"👤 **Твой профиль**\n\n"
        f"🆔 ID: `{tg_id}`\n"
        f"💎 GIP: **{gip}**\n\n"
        f"📦 Кейсы и подарки скоро появятся"
    )


# ================= КЕЙСЫ =================
@dp.callback_query_handler(text="cases")
async def cases_handler(call: types.CallbackQuery):
    await call.answer()

    await call.message.answer(
        "🎁 **Кейсы GIP**\n\n"
        "Доступные кейсы:\n\n"
        "1️⃣ Бомж — 100 GIP\n"
        "2️⃣ Средничок — 2500 GIP\n"
        "3️⃣ Богатый — 15000 GIP\n"
        "4️⃣ Мега — 50000 GIP\n"
        "5️⃣ GFT — 100000 GIP\n\n"
        "🎰 Анимация как в Telegram\n"
        "📊 Шансы честные\n\n"
        "⏳ Открытие — скоро"
    )


# ================= ПОКУПКА GIP =================
@dp.callback_query_handler(text="buy_gip")
async def buy_gip_handler(call: types.CallbackQuery):
    await call.answer()

    await call.message.answer(
        "💎 **Покупка GIP**\n\n"
        "Ты сможешь купить GIP за ⭐ Telegram Stars\n\n"
        "🔒 Платежи скоро будут подключены"
    )


# ================= FALLBACK =================
@dp.message_handler()
async def fallback(message: types.Message):
    await message.answer(
        "🤖 Я тебя не понял.\n\n"
        "Используй /start"
    )


# ================= START =================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
