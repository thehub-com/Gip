import os
import logging
import random
import requests
from aiogram import Bot, Dispatcher, executor, types

# ---------- CONFIG ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ---------- SUPABASE REST HELPERS ----------

def sb_select(table, query=""):
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/{table}{query}",
        headers=HEADERS,
        timeout=10
    )
    r.raise_for_status()
    return r.json()

def sb_insert(table, data):
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=data,
        timeout=10
    )
    r.raise_for_status()
    return r.json()

def sb_update(table, data, match):
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?{match}",
        headers=HEADERS,
        json=data,
        timeout=10
    )
    r.raise_for_status()
    return r.json()

# ---------- COMMANDS ----------

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    tg_id = message.from_user.id
    username = message.from_user.username

    users = sb_select("users", f"?tg_id=eq.{tg_id}")

    if not users:
        sb_insert("users", {
            "tg_id": tg_id,
            "username": username,
            "gip": 0
        })

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(
            "🛒 Открыть маркетплейс",
            web_app=types.WebAppInfo(url="https://example.com")
        )
    )

    await message.answer(
        "🌑 **GIP — GOCK Interaction Points**\n\n"
        "• Кейсы\n"
        "• Подарки\n"
        "• Маркет\n"
        "• NFT\n\n"
        "👇 Открывай маркет:",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@dp.message_handler(commands=["cases"])
async def cases(message: types.Message):
    cases = sb_select("cases")
    text = "🎁 **Кейсы:**\n\n"
    for c in cases:
        text += f"• {c['name']} — {c['price']} GIP\n/open_{c['id']}\n\n"
    await message.answer(text, parse_mode="Markdown")

@dp.message_handler(lambda m: m.text.startswith("/open_"))
async def open_case(message: types.Message):
    tg_id = message.from_user.id
    case_id = int(message.text.split("_")[1])

    user = sb_select("users", f"?tg_id=eq.{tg_id}")[0]
    case = sb_select("cases", f"?id=eq.{case_id}")[0]

    if user["gip"] < case["price"]:
        await message.answer("❌ Недостаточно GIP")
        return

    # списываем GIP
    sb_update(
        "users",
        {"gip": user["gip"] - case["price"]},
        f"tg_id=eq.{tg_id}"
    )

    dist = case["rarity_distribution"]
    rarity = random.choices(
        list(dist.keys()),
        weights=list(dist.values())
    )[0]

    gifts = sb_select("gifts", f"?rarity=eq.{rarity}")
    gift = random.choice(gifts)

    sb_insert("user_gifts", {
        "user_id": user["id"],
        "gift_id": gift["id"],
        "obtained_from": case["name"]
    })

    await message.answer(
        f"🎉 **{case['name']}** открыт!\n\n"
        f"🎁 Выпало: **{gift['name']}**\n"
        f"⭐ Редкость: `{gift['rarity']}`",
        parse_mode="Markdown"
    )

# ---------- START ----------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
