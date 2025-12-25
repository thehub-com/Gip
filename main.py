import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from supabase import create_client

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    tg_id = message.from_user.id
    username = message.from_user.username

    supabase.table("users").upsert({
        "tg_id": tg_id,
        "username": username
    }).execute()

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(
            "🛒 Открыть маркетплейс",
            web_app=types.WebAppInfo(
                url="https://example.com"
            )
        )
    )

    await message.answer(
        "🌑 **GIP — GOCK Interaction Points**\n\n"
        "💠 Твой цифровой рынок:\n"
        "• кейсы\n"
        "• подарки\n"
        "• NFT\n"
        "• торговля\n\n"
        "👇 Открывай маркет:",
        reply_markup=kb,
        parse_mode="Markdown"
    )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
