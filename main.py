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

# ─── Конфиг ───────────────────────────────────────────────────────────────────
# Токен берем из переменных окружения хостинга (Render/Koyeb)
BOT_TOKEN   = os.environ.get("8718220580:AAFZXCUF87zIpDa2GFz7jYu0B68ECvjauMc") 
STARS_PRICE = 50          # цена в Stars
PRODUCT_URL = "https://drive.google.com/file/d/1hSkkNyLwpXZw-T4fS9XSQ0YIA9a_yxbH/view?usp=sharing"
KEEP_ALIVE_INTERVAL = 15 * 60  # 15 минут в секундах

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher()

# ─── Кнопка «Купить» ──────────────────────────────────────────────────────────
def buy_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=f"🛒 Купить за {STARS_PRICE} ⭐",
            callback_data="buy"
        )
    ]])

# ─── /start ───────────────────────────────────────────────────────────────────
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👾 <b>GAMEBooster — Оптимизатор ПК для игр</b>\n\n"
        "🚀 Разгони свой компьютер и получи максимальный FPS!\n"
        "Цена: <b>50 ⭐ Telegram Stars</b>\n\n"
        "Нажми кнопку ниже, чтобы купить и сразу получить файл 👇",
        parse_mode="HTML",
        reply_markup=buy_keyboard()
    )

# ─── Нажатие «Купить» → создаём Invoice (БЕЗ ФОТО) ─────────────────────────────
@dp.callback_query(F.data == "buy")
async def callback_buy(call: CallbackQuery):
    await call.answer()
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title="GAMEBooster — Оптимизатор ПК",
        description="Мгновенная доставка. Разгони свой ПК и увеличь FPS в играх!",
        payload="gamebooster_purchase",
        provider_token="",                       # Пусто для Stars
        currency="XTR",                         # Код валюты для Stars
        prices=[LabeledPrice(label="GAMEBooster", amount=STARS_PRICE)]
        # Параметры фото удалены для чистоты кода
    )

# ─── Pre-checkout: подтверждаем готовность сервера ────────────────────────────
@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    log.info("Pre-checkout от пользователя %s", query.from_user.id)
    await query.answer(ok=True) # Подтверждаем транзакцию

# ─── Успешная оплата → выдаём товар ──────────────────────────────────────────
@dp.message(F.successful_payment)
async def successful_payment(message: Message):
    user = message.from_user
    stars = message.successful_payment.total_amount
    log.info("✅ Оплата %d ⭐ от %s (id=%s)", stars, user.full_name, user.id)

    await message.answer(
        "✅ <b>Оплата прошла! Спасибо за покупку.</b>\n"
        "✅ <b>Payment successful! Thank you for your purchase.</b>\n\n"
        f"🎮 Вот твой <b>GAMEBooster</b>:\n{PRODUCT_URL}\n\n"
        "📌 Сохрани ссылку — она не истекает.\n"
        "Если возникнут вопросы — напиши нам!",
        parse_mode="HTML"
    )

# ─── «Белый шум» для Render ─────────────────────────────────────
async def keep_alive_loop():
    while True:
        await asyncio.sleep(KEEP_ALIVE_INTERVAL)
        log.info("🟢 [keep-alive] Система активна. Бот работает.")

# ─── Лёгкий веб-сервер для предотвращения Port Timeout на Render ──────────────
async def health(request):
    return web.Response(text="OK")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    # Берем порт из переменной PORT или ставим 8080 по умолчанию
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    log.info(f"🌐 Веб-сервер запущен на порту {port}")

# ─── Точка входа ─────────────────────────────────────────────────────────────
async def main():
    log.info("🤖 GAMEBooster bot запускается...")
    # Запускаем всё параллельно через gather
    await asyncio.gather(
        start_webserver(),
        keep_alive_loop(),
        dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types()),
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Бот остановлен")