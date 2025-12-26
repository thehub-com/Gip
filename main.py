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
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# ====== BOT ======
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ====== DB ======
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ====== LOGGING ======
logging.basicConfig(level=logging.INFO)


# ====== USER REGISTER ======
async def register_user(tg_id: int, username: str):
    user = supabase.table("users") \
        .select("tg_id") \
        .eq("tg_id", tg_id) \
        .execute()

    if not user.data:
        supabase.table("users").insert({
            "tg_id": tg_id,
            "username": username,
            "gip": 0
        }).execute()


# ====== /start ======
@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    tg_id = message.from_user.id
    username = message.from_user.username

    await register_user(tg_id, username)

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
        "• 🎁 Кейсы\n"
        "• 🛒 Маркетплейс\n"
        "• 👤 Профиль\n"
        "• 💎 Валюта GIP\n\n"
        "👇 Выбери действие:",
        reply_markup=kb,
        parse_mode="Markdown"
    )


# ====== КЕЙСЫ ======
@dp.callback_query_handler(text="cases")
async def cases_menu(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer(
        "🎁 **Кейсы**\n\n"
        "Скоро будут доступны:\n"
        "• Бомж\n"
        "• Среднячок\n"
        "• Богатый\n"
        "• Мега\n"
        "• GFT\n\n"
        "⏳ В разработке",
        parse_mode="Markdown"
    )


# ====== BUY GIP ======
@dp.callback_query_handler(text="buy_gip")
async def buy_gip(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer(
        "💎 **Покупка GIP**\n\n"
        "Покупка за ⭐ Telegram Stars\n"
        "Скоро будет доступно",
        parse_mode="Markdown"
    )


# ====== /admin ======
@dp.message_handler(commands=["admin"])
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("➕ Выдать GIP", callback_data="admin_add_gip"),
        types.InlineKeyboardButton("➖ Забрать GIP", callback_data="admin_remove_gip")
    )
    kb.add(
        types.InlineKeyboardButton("🚫 Бан", callback_data="admin_ban"),
        types.InlineKeyboardButton("✅ Разбан", callback_data="admin_unban")
    )

    await message.answer(
        "👮 **Админ-панель**",
        reply_markup=kb,
        parse_mode="Markdown"
    )


# ====== START ======
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
