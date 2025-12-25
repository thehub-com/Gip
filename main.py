import os
import asyncio
import random
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

logging.basicConfig(level=logging.INFO)

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# ---------- SUPABASE ----------
def sb_select(table, query=""):
    r = requests.get(f"{SUPABASE_URL}/rest/v1/{table}{query}", headers=HEADERS)
    r.raise_for_status()
    return r.json()

def sb_insert(table, data):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=data)
    r.raise_for_status()

def sb_update(table, data, match):
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}?{match}", headers=HEADERS, json=data)
    r.raise_for_status()

# ---------- HANDLERS ----------
@dp.message(Command("start"))
async def start(message: types.Message):
    tg_id = message.from_user.id
    username = message.from_user.username

    users = sb_select("users", f"?tg_id=eq.{tg_id}")
    if not users:
        sb_insert("users", {"tg_id": tg_id, "username": username, "gip": 0})

    await message.answer("🔥 GIP bot запущен\n\n/cases")

@dp.message(Command("cases"))
async def cases(message: types.Message):
    cases = sb_select("cases")
    text = "🎁 Кейсы:\n\n"
    for c in cases:
        text += f"{c['id']}. {c['name']} — {c['price']} GIP\n"
    await message.answer(text)

# ---------- START ----------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
