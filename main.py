import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, LabeledPrice, 
    PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import CommandStart
from groq import Groq

# --- Конфигурация ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PRODUCT_URL = os.environ.get("PRODUCT_URL", "https://your-link.com")
STARS_PRICE = 50

# Триггеры для ИИ (если ручные проверки не сработали)
AI_TRIGGERS = ["fps", "boost", "lag", "лаг", "оптимизация", "help", "помощь"]

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
groq_client = Groq(api_key=GROQ_API_KEY)

def ask_llama(user_text):
    try:
        completion = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are TurboCat, AI for ANONYM SYSTEMS. Be cool and professional."},
                {"role": "user", "content": user_text}
            ],
            temperature=0.6
        )
        return completion.choices[0].message.content
    except:
        return "🐈: My AI brain is sleeping. Ask me later!"

# --- Клавиатура ---
def buy_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=f"🚀 Buy ANONYM SYSTEMS ({STARS_PRICE} ⭐)", callback_data="buy")
    ]])

# --- Хендлеры с кучей IF ---
@dp.message(F.text)
async def message_handler(message: Message):
    text = message.text.lower()

    # 1. Ручные проверки (те самые IF)
    if text == "/start":
        await message.answer("Welcome to ANONYM SYSTEMS! Need a boost? 🚀", reply_markup=buy_keyboard())
    
    elif "привет" in text or "hello" in text:
        await message.answer("Привет! Я TurboCat. Чем помочь? 🐈👔")

    elif "безопасно" in text or "safe" in text or "virus" in text:
        await message.answer("🛡️ <b>Security Info:</b>\nOur code is open-source and we have a strict Privacy Policy on our website. No data collection!", parse_mode="HTML")

    elif "купить" in text or "buy" in text or "цена" in text:
        await message.answer(f"Full pack costs {STARS_PRICE} Stars. Use the button below!", reply_markup=buy_keyboard())

    elif "паровоз" in text or "train" in text:
        await message.answer("🚂 Choo-choo! Check the 'cool' folder in the archive!")

    # 2. Если ручные IF не сработали, проверяем триггеры для ИИ
    elif any(trigger in text for trigger in AI_TRIGGERS):
        response = ask_llama(message.text)
        await message.answer(f"🤖 <b>AI Assistant:</b>\n{response}", parse_mode="HTML")

    # 3. На всё остальное бот просто вежливо молчит или шлет эмодзи
    else:
        await message.answer("🐾")

# --- Оплата (остается без изменений) ---
@dp.callback_query(F.data == "buy")
async def callback_buy(call: CallbackQuery):
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title="ANONYM SYSTEMS v3.0",
        description="Access to optimization files",
        payload="gb_pay",
        provider_token="", 
        currency="XTR",
        prices=[LabeledPrice(label="XTR", amount=STARS_PRICE)]
    )

@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@dp.message(F.successful_payment)
async def got_payment(message: Message):
    await message.answer(f"✅ Success! Download: {PRODUCT_URL}")

# --- Web Server ---
async def handle_web(request):
    return web.Response(text="Bot is alive")

async def main():
    app = web.Application()
    app.router.add_get("/", handle_web)
    runner = web.AppRunner(app, access_log=None) 
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080))).start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
