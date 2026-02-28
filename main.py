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
# Мы берем переменную "BOT_TOKEN", которую ты пропишешь в настройках Render
BOT_TOKEN = os.environ.get("BOT_TOKEN")
STARS_PRICE = 50          # цена в Stars
PRODUCT_URL = "https://drive.google.com/file/d/1hSkkNyLwpXZw-T4fS9XSQ0YIA9a_yxbH/view?usp=sharing"
KEEP_ALIVE_INTERVAL = 15 * 60  # 15 минут

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger(__name__)

# Проверка, что токен вообще есть
if not BOT_TOKEN:
    log.error("ОШИБКА: BOT_TOKEN не найден в настройках хостинга!")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

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

# ─── Нажатие «Купить» → создаём Invoice ─────────────────────────────
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
    )

# ─── Pre-checkout: подтверждаем транзакцию ────────────────────────────
@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

# ─── Успешная оплата → выдаём товар ──────────────────────────────────────────
@dp.message(F.successful_payment)
async def successful_payment(message: Message):
    await message.answer(
        "✅ <b>Оплата прошла! Спасибо за покупку.</b>\n\n"
        f"🎮 Вот твой <b>GAMEBooster</b>:\n{PRODUCT_URL}\n\n"
        "📌 Сохрани ссылку — она не истекает.",
        parse_mode="HTML"
    )

# ─── Веб-сервер для Render (чтобы не засыпал) ──────────────────────────────
async def health(request):
    return web.Response(text="OK")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# ─── Точка входа ─────────────────────────────────────────────────────────────
async def main():
    log.info("🤖 GAMEBooster bot запускается...")
    # Запускаем бота и веб-сервер вместе
    await asyncio.gather(
        start_webserver(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log.info("Бот остановлен")
