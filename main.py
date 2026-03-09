import asyncio
import logging
import os
import random
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, LabeledPrice, 
    PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton
)

# --- КОНФИГУРАЦИЯ ЧЕРЕЗ ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ---
# Эти данные теперь бот будет брать из настроек хостинга (Render)
BOT_TOKEN = os.environ.get("BOT_TOKEN") 
PRODUCT_URL = os.environ.get("PRODUCT_URL")
STARS_PRICE = int(os.environ.get("STARS_PRICE", 25)) # По умолчанию 25, если не задано

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- КЛАВИАТУРА ---
def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🚀 Купить VIP ({STARS_PRICE} ⭐)", callback_data="buy")],
        [InlineKeyboardButton(text="🎰 Рандомайзер (Шанс 1%)", callback_data="random")]
    ])

# --- ПРИВЕТСТВИЕ ---
@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "<b>ANONYM SYSTEMS v4.0 VIP</b> 🐈👔\n\n"
        "Система защиты активирована. Выбери действие:\n"
        "• Мгновенный доступ через VIP-покупку\n"
        "• Попытка бесплатного взлома через рандомайзер",
        parse_mode="HTML",
        reply_markup=main_kb()
    )

# --- ЛОГИКА РАНДОМАЙЗЕРА ---
@dp.callback_query(F.data == "random")
async def run_random(call: CallbackQuery):
    msg = await call.message.answer("📡 Инициализация зашифрованного канала...")
    
    hacker_steps = [
        "🌐 Обход брандмауэра Windows Defender...",
        "💉 Инъекция скрипта в процесс svchost.exe...",
        "🔓 Попытка дешифровки токена...",
        "🛰️ Перехват сигнала со спутника Бирлик-1..."
    ]
    
    for step in hacker_steps:
        await asyncio.sleep(1.8)
        await msg.edit_text(step)

    if random.randint(1, 100) == 1:
        await msg.edit_text(
            f"🎉 <b>СИСТЕМА ВЗЛОМАНА!</b>\n\nТвоя секретная ссылка: {PRODUCT_URL}",
            parse_mode="HTML"
        )
    else:
        await msg.edit_text(
            "❌ <b>ОТКАЗ В ДОСТУПЕ.</b>\n\nПротоколы безопасности обновлены. Попробуй завтра!",
            parse_mode="HTML",
            reply_markup=main_kb()
        )

# --- ОПЛАТА ---
@dp.callback_query(F.data == "buy")
async def send_pay(call: CallbackQuery):
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title="ANONYM SYSTEMS VIP",
        description="Доступ к ультимативному архиву оптимизации",
        payload="vip_pay",
        provider_token="", 
        currency="XTR",
        prices=[LabeledPrice(label="XTR", amount=STARS_PRICE)]
    )

@dp.pre_checkout_query()
async def process_pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@dp.message(F.successful_payment)
async def success_pay(message: Message):
    await message.answer(f"✅ Оплата принята! Твоя ссылка: {PRODUCT_URL}")

# --- СЕРВЕР ДЛЯ ПОДДЕРЖАНИЯ ЖИЗНИ ---
async def handle_web(request):
    return web.Response(text="Security protocols active.")

async def main():
    app = web.Application()
    app.router.add_get("/", handle_web)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
