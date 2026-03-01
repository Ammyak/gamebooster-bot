import asyncio
import logging
import os
import httpx
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, LabeledPrice, 
    PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import CommandStart

# --- Конфигурация ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PRODUCT_URL = os.environ.get("PRODUCT_URL", "https://your-link.com")
STARS_PRICE = 50

# --- РАСШИРЕННЫЕ ТРИГГЕРЫ ---
# Если эти слова есть в сообщении — включается ИИ
AI_TRIGGERS = [
    "fps", "фпс", "boost", "буст", "lag", "лаг", "фриз", "latency", 
    "delay", "задержка", "оптимизация", "optimization", "help", "помощь", 
    "настройка", "tweak", "твик", "windows", "виндовс", "system"
]

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Прямой запрос к Groq (Llama 3) ---
async def ask_llama(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system", 
                "content": (
                    "You are TurboCat, an AI for ANONYM SYSTEMS v3.0. "
                    "You help gamers optimize PC. Be cool, use gamer slang. "
                    "Answer in the language of the user (RU or EN)."
                )
            },
            {"role": "user", "content": user_text}
        ],
        "temperature": 0.6
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data, timeout=25.0)
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            log.error(f"AI Error: {e}")
            return "🐈: Мои кошачьи мозги перегрелись. Попробуй позже!"

# --- Клавиатура ---
def buy_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=f"🚀 Купить ANONYM SYSTEMS ({STARS_PRICE} ⭐)", callback_data="buy")
    ]])

# --- ХЕНДЛЕР С КУЧЕЙ ТРИГГЕРОВ ---
@dp.message(F.text)
async def message_handler(message: Message):
    text = message.text.lower()

    # 1. Точные команды и быстрые ответы (IF)
    if text == "/start":
        await message.answer(
            "<b>ANONYM SYSTEMS v3.0</b> 🐈👔\n\n"
            "Максимальный ФПС и плавная картинка. Спрашивай что угодно!\n\n"
            f"Цена: {STARS_PRICE} Stars",
            parse_mode="HTML",
            reply_markup=buy_keyboard()
        )
    
    elif any(word in text for word in ["привет", "hello", "хай", "ку"]):
        await message.answer("Мяу! Я TurboCat. Готов разнести твои лаги в пух и прах! 🐈🚀")

    elif any(word in text for word in ["безопасно", "safe", "вирус", "virus", "рат", "rat"]):
        await message.answer(
            "🛡️ <b>Безопасность превыше всего:</b>\n"
            "- Наш код открыт (Open Source)\n"
            "- Мы не собираем данные (см. Privacy Policy)\n"
            "- Никаких вирусов, только .bat и .reg скрипты.",
            parse_mode="HTML"
        )

    elif any(word in text for word in ["купить", "buy", "цена", "цена", "стоимость", "stars"]):
        await message.answer(
            f"Пакет ANONYM SYSTEMS стоит всего <b>{STARS_PRICE} Stars</b>.\n"
            "Нажми на кнопку ниже, чтобы начать!",
            parse_mode="HTML",
            reply_markup=buy_keyboard()
        )

    # 2. Если сработали темы-триггеры — зовем нейросеть
    elif any(trigger in text for trigger in AI_TRIGGERS):
        await message.answer("🤖 <i>TurboCat думает...</i>", parse_mode="HTML")
        response = await ask_llama(message.text)
        await message.answer(f"🤖 <b>AI Assistant:</b>\n{response}", parse_mode="HTML")

    # 3. Если ничего не подошло
    else:
        await message.answer("🐾 (Я тебя слушаю, используй триггеры вроде 'фпс', 'лаги' или 'помощь')")

# --- Оплата и сервер (без изменений) ---
@dp.callback_query(F.data == "buy")
async def callback_buy(call: CallbackQuery):
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title="ANONYM SYSTEMS v3.0",
        description="Доступ к архиву оптимизации",
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
    await message.answer(f"✅ Оплата прошла! Твоя ссылка: {PRODUCT_URL}")

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
