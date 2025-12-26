import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from supabase import create_client
from dotenv import load_dotenv

# ================== LOAD ENV ==================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# ================== BOT ==================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ================== DB ==================
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================== LOGGING ==================
logging.basicConfig(level=logging.INFO)


# ================== /start ==================
@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    tg_id = message.from_user.id
    username = message.from_user.username

    # регистрация пользователя (если уже есть — обновит)
    supabase.table("users").upsert({
        "tg_id": tg_id,
        "username": username,
        "gip": 0
    }).execute()

    kb = types.InlineKeyboardMarkup(row_width=2)

    kb.add(
        types.InlineKeyboardButton("🎁 Кейсы", callback_data="cases"),
        types.InlineKeyboardButton("💎 Купить GIP", callback_data="buy_gip"),
    )

    kb.add(
        types.InlineKeyboardButton(
            "🛒 Маркетплейс",
            web_app=types.WebAppInfo(url="https://example.com/market")
        ),
        types.InlineKeyboardButton(
            "👤 Профиль",
            web_app=types.WebAppInfo(url="https://example.com/profile")
        ),
    )

    kb.add(
        types.InlineKeyboardButton("🆘 Поддержка", url="https://t.me/gock_admin_bot")
    )

    await message.answer(
        "🌌 **GIP — GOCK Interaction Points**\n\n"
        "• 🎁 Кейсы\n"
        "• 🛒 Маркет\n"
        "• 💎 Валюта GIP\n\n"
        "👇 Выбери действие:",
        reply_markup=kb,
        parse_mode="Markdown"
    )


# ================== КЕЙСЫ ==================
@dp.callback_query_handler(text="cases")
async def cases_handler(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer(
        "🎁 **Кейсы скоро будут доступны**\n\n"
        "Анимации как в Telegram 🎰\n"
        "Редкости, дубликаты, рынок",
        parse_mode="Markdown"
    )


# ================== ПОКУПКА GIP ==================
@dp.callback_query_handler(text="buy_gip")
async def buy_gip_handler(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer(
        "💎 **Покупка GIP**\n\n"
        "Покупка за ⭐ Telegram Stars\n"
        "Скоро будет доступно",
        parse_mode="Markdown"
    )


# ================== /admin ==================
@dp.message_handler(commands=["admin"])
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Нет доступа")
        return

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("➕ Добавить GIP", "📦 Кейсы")
    kb.add("👥 Пользователи", "❌ Закрыть")

    await message.answer(
        "⚙️ **Админ-панель GIP**",
        reply_markup=kb,
        parse_mode="Markdown"
    )


# ================== ADMIN ACTIONS ==================
@dp.message_handler(text="❌ Закрыть")
async def close_admin(message: types.Message):
    await message.answer("Админка закрыта", reply_markup=types.ReplyKeyboardRemove())


# ================== START ==================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
