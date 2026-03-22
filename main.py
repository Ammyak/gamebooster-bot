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

# --- КОНФИГУРАЦИЯ ---
BOT_TOKEN = os.environ.get("BOT_TOKEN") 
PRODUCT_URL = os.environ.get("PRODUCT_URL")
APP_URL = os.environ.get("APP_URL")
STARS_PRICE = int(os.environ.get("STARS_PRICE", 25))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- КЛАВИАТУРА ---
def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🚀 Купить Product ({STARS_PRICE} ⭐)", callback_data="buy_product")],
        [InlineKeyboardButton(text=f"📱 Купить App ({STARS_PRICE} ⭐)", callback_data="buy_app")],
        [InlineKeyboardButton(text="🎰 Рандомайзер (Шанс 1%)", callback_data="random")]
    ])

# --- ПРИВЕТСТВИЕ ---
@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "<b>ANONYM SYSTEMS v4.0 VIP</b> 🐈👔\n\n"
        "Система защиты активирована. Выбери действие:\n"
        "• Мгновенная покупка нужного компонента\n"
        "• Попытка взлома через рандомайзер (выпадет случайный софт)",
        parse_mode="HTML",
        reply_markup=main_kb()
    )

# --- ЛОГИКА РАНДОМАЙЗЕРА ---
@dp.callback_query(F.data == "random")
async def run_random(call: CallbackQuery):
    msg = await call.message.answer("📡 Попытка несанкционированного доступа...")
    
    hacker_steps = [
        "🌐 Подключение к прокси...",
        "💉 Инъекция кода...",
        "🔓 Дешифровка базы...",
        "🛰️ Перехват пакетов..."
    ]
    
    for step in hacker_steps:
        await asyncio.sleep(1.2)
        await msg.edit_text(f"<code>{step}</code>", parse_mode="HTML")

    # ШАНС 1% (random.randint(1, 100) == 1)
    if random.randint(1, 100) == 1:
        # Выбираем случайную ссылку из двух доступных
        win_url = random.choice([PRODUCT_URL, APP_URL])
        await msg.edit_text(
            f"🎉 <b>СИСТЕМА ВЗЛОМАНА!</b>\n\nТвой случайный трофей: {win_url}",
            parse_mode="HTML"
        )
    else:
        await msg.edit_text(
            "❌ <b>ОТКАЗ В ДОСТУПЕ.</b>\n\nПротоколы безопасности слишком сильны. Попробуй еще раз!",
            parse_mode="HTML",
            reply_markup=main_kb()
        )

# --- ОПЛАТА ---
@dp.callback_query(F.data.startswith("buy_"))
async def send_pay(call: CallbackQuery):
    product_type = call.data.split("_")[1]
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title=f"Доступ к {product_type.upper()}",
        description=f"Прямой доступ к компоненту {product_type}",
        payload=f"pay_{product_type}",
        provider_token="", 
        currency="XTR",
        prices=[LabeledPrice(label="XTR", amount=STARS_PRICE)]
    )

@dp.pre_checkout_query()
async def process_pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@dp.message(F.successful_payment)
async def success_pay(message: Message):
    payload = message.successful_payment.invoice_payload
    target_url = PRODUCT_URL if payload == "pay_product" else APP_URL
    await message.answer(f"✅ Оплата принята! Твоя ссылка: {target_url}")

# --- ВЕБ-СЕРВЕР ---
async def handle_web(request):
    return web.Response(text="Security protocols active.")

async def main():
    port = int(os.environ.get("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", handle_web)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", port).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
