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

# --- Конфигурация ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
STARS_PRICE = 50
PRODUCT_URL = "https://drive.google.com/file/d/1hSkkNyLwpXZw-T4fS9XSQ0YIA9a_yxbH/view?usp=sharing"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

if not BOT_TOKEN:
    exit("ОШИБКА: Забыли BOT_TOKEN!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Клавиатура ---
def buy_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=f"🚀 Buy GameBooster ({STARS_PRICE} ⭐)", callback_data="buy")
    ]])

# --- Хендлеры ---
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "<b>GAMEBooster</b> — Maximum FPS Optimizer\n\nPrice: 50 Stars",
        parse_mode="HTML",
        reply_markup=buy_keyboard()
    )

@dp.callback_query(F.data == "buy")
async def callback_buy(call: CallbackQuery):
    await call.answer()
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title="GAMEBooster",
        description="Instant File Delivery",
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
    await message.answer(f"✅ Payment OK!\nYour link: {PRODUCT_URL}")

# --- Веб-сервер для UptimeRobot ---
async def handle_web(request):
    return web.Response(text="Bot is running")

async def main():
    # 1. Запуск веб-сервера (чтобы Render и UptimeRobot видели, что мы живы)
    app = web.Application()
    app.router.add_get("/", handle_web)
    # Удаляем логи доступа aiohttp, чтобы в консоли было чисто
    runner = web.AppRunner(app, access_log=None) 
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    await web.TCPSite(runner, "0.0.0.0", port).start()

    # 2. Очистка старых сессий Telegram
    log.info("Сброс старых соединений...")
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.sleep(2) # Даем Telegram время «отпустить» старый процесс
    
    log.info("Система чиста. Бот выходит в эфир!")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
