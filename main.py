import asyncio
import logging
import os
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, LabeledPrice, 
    PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import CommandStart

# --- Конфиг без шума ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
STARS_PRICE = 50
PRODUCT_URL = "https://drive.google.com/file/d/1hSkkNyLwpXZw-T4fS9XSQ0YIA9a_yxbH/view?usp=sharing"
RENDER_URL = "https://gamebooster-bot.onrender.com"

# Настраиваем логи, чтобы не спамили лишним
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

if not BOT_TOKEN:
    exit("ОШИБКА: Забыли BOT_TOKEN в переменных окружения!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Логика Anti-Sleep (тихий режим) ---
async def keep_alive_ping():
    await asyncio.sleep(60) # Даем системе загрузиться
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(RENDER_URL, timeout=10) as resp:
                    # Логируем только если что-то не так, чтобы не создавать шум
                    if resp.status != 200:
                        log.warning(f"Self-ping status: {resp.status}")
            except Exception as e:
                log.error(f"Ping error: {e}")
            await asyncio.sleep(600) # 10 минут тишины

# --- Кнопки ---
def buy_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=f"🚀 Buy GameBooster ({STARS_PRICE} ⭐)", callback_data="buy")
    ]])

# --- Обработчики ---
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
        provider_token="", # Для Stars пусто
        currency="XTR",
        prices=[LabeledPrice(label="XTR", amount=STARS_PRICE)]
    )

@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@dp.message(F.successful_payment)
async def got_payment(message: Message):
    await message.answer(f"✅ Payment OK!\nYour link: {PRODUCT_URL}")

# --- Чистый запуск без конфликтов ---
async def handle_web(request):
    return web.Response(text="Bot is running")

async def main():
    # 1. Запуск веб-сервера (для Render)
    app = web.Application()
    app.router.add_get("/", handle_web)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    await web.TCPSite(runner, "0.0.0.0", port).start()

    # 2. Запуск фонового пинга (отдельной задачей)
    asyncio.create_task(keep_alive_ping())

    # 3. Чистим очередь обновлений и запускаем бота
    await bot.delete_webhook(drop_pending_updates=True)
    log.info("Система чиста. Бот в эфире!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
