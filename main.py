import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from supabase import create_client
from dotenv import load_dotenv

# ===== ENV =====
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

ADMIN_ID = 5516708022  # ТВОЙ ID

# ===== BOT =====
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ===== DB =====
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ===== LOG =====
logging.basicConfig(level=logging.INFO)

# ===== STARTUP =====
async def on_startup(dp):
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Webhook удалён, бот запущен")

# ===== /start =====
@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    tg_id = message.from_user.id
    username = message.from_user.username

    # безопасная регистрация
    supabase.table("users").upsert(
        {
            "tg_id": tg_id,
            "username": username,
            "gip": 0
        },
        on_conflict="tg_id"
    ).execute()

    kb = types.InlineKeyboardMarkup(row_width=2)

    kb.add(
        types.InlineKeyboardButton(
            "🛒 Маркетплейс",
            web_app=types.WebAppInfo(url="https://example.com/market")
        ),
        types.InlineKeyboardButton("🎁 Кейсы", callback_data="cases")
    )

    kb.add(
        types.InlineKeyboardButton(
            "👤 Профиль",
            web_app=types.WebAppInfo(url="https://example.com/profile")
        ),
        types.InlineKeyboardButton("💎 Купить GIP", callback_data="buy_gip")
    )

    kb.add(
        types.InlineKeyboardButton("🆘 Поддержка", url="https://t.me/gock_admin_bot")
    )

    await message.answer(
        "🌌 **GIP — GOCK Interaction Points**\n\n"
        "• 🎁 Кейсы\n"
        "• 🛒 Маркетплейс\n"
        "• 👤 Профиль\n"
        "• 💎 Валюта GIP\n\n"
        "👇 Выбери действие:",
        reply_markup=kb,
        parse_mode="Markdown"
    )

# ===== /admin =====
@dp.message_handler(commands=["admin"])
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply("⛔ Доступ запрещён")

    await message.reply(
        "👑 **Админ-панель GIP**\n\n"
        "• выдача / снятие GIP\n"
        "• баны\n"
        "• добавление кейсов\n"
        "• управление маркетом",
        parse_mode="Markdown"
    )

# ===== CALLBACKS =====
@dp.callback_query_handler(text="cases")
async def cases(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("🎁 Кейсы скоро будут доступны")

@dp.callback_query_handler(text="buy_gip")
async def buy_gip(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("💎 Покупка GIP за ⭐ скоро")

# ===== ERRORS =====
@dp.errors_handler()
async def errors_handler(update, exception):
    logging.exception(f"Ошибка: {exception}")
    return True

# ===== RUN =====
if __name__ == "__main__":
    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup
    )
