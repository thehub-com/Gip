import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import CommandStart
from supabase import create_client
from dotenv import load_dotenv

# ---------- ENV ----------
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

# ---------- LOGGING ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# ---------- BOT ----------
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# ---------- SUPABASE ----------
supabase = None
if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# ---------- HANDLERS ----------
@router.message(CommandStart())
async def start_handler(message: types.Message):
    tg_id = message.from_user.id
    username = message.from_user.username

    # создаём пользователя, если есть supabase
    if supabase:
        supabase.table("users").upsert(
            {
                "tg_id": tg_id,
                "username": username,
                "gip": 0
            }
        ).execute()

    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="🎁 Кейсы",
                    callback_data="open_cases"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="🛒 Маркет",
                    web_app=types.WebAppInfo(
                        url="https://example.com"  # потом заменим
                    )
                )
            ]
        ]
    )

    await message.answer(
        "👋 Добро пожаловать в **GIP**\n\n"
        "🎁 Кейсы\n"
        "🛒 Маркетплейс\n"
        "💠 Подарки и NFT",
        reply_markup=kb,
        parse_mode="Markdown"
    )

# ---------- MAIN ----------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
