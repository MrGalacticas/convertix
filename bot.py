import asyncio
import os

from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiohttp import web

from config import BOT_TOKEN
from exchange import Exchange
from constants import CURRENCIES
from keyboards import ( 
    main_currency_keyboard,
    all_currencies_keyboard,
    search_results_keyboard,
)  



bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
exchange = Exchange()

class CurrencyStates(StatesGroup):
    from_currency = State()
    to_currency = State()
    amount = State()
    search = State()


@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer(
    """Привет! Это калькулятор валют в Telegram.

Выберите валюту, из которой хотите конвертировать:""",
    reply_markup=main_currency_keyboard()
)


@dp.callback_query()
async def process_currency(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if callback.data == "ALL":
        await callback.message.edit_text(
            "🌍 Выберите валюту:",
            reply_markup=all_currencies_keyboard()
        )
        return

    if callback.data.startswith("page:"):
        page = int(callback.data.split(":")[1])

        await callback.message.edit_reply_markup(
            reply_markup=all_currencies_keyboard(page)
        )

        return

    if callback.data == "BACK":
        await callback.message.edit_text(
            "Выберите валюту:",
            reply_markup=main_currency_keyboard()
        )
        return

    if callback.data == "ignore":
        return

    if callback.data == "SEARCH":
        await state.set_state(CurrencyStates.search)
        await callback.message.answer("🔍 Введите код или название валюты:"
        )
        return
    
    current_state = await state.get_state()

    if current_state is None:

        if callback.data not in CURRENCIES:
            return

        await state.update_data(from_currency=callback.data)
        await state.set_state(CurrencyStates.to_currency)

        await callback.message.answer(
            "Теперь выберите валюту, в которую хотите конвертировать:",
            reply_markup=all_currencies_keyboard()
        )

    elif current_state == CurrencyStates.to_currency:

        if callback.data not in CURRENCIES:
            return

        await state.update_data(to_currency=callback.data)
        await state.set_state(CurrencyStates.amount)

        await callback.message.answer(
            "Введите сумму:"
        )


@dp.message(CurrencyStates.amount)
async def process_amount(message: Message, state: FSMContext):

    try:
        amount = float(message.text)
        data = await state.get_data()
        from_currency = data["from_currency"]
        to_currency = data["to_currency"]

        result = exchange.convert(amount, from_currency, to_currency)

        await message.answer(
        f"""💱 Конвертация..

{CURRENCIES[from_currency]["flag"]} {amount:g} {from_currency}
⬇️
{CURRENCIES[to_currency]["flag"]} {result:g} {to_currency}"""
    
        )
        await state.clear()
        await message.answer(
    "Хотите выполнить ещё одну конвертацию?\n\nВыберите валюту, из которой хотите конвертировать:",
    reply_markup=main_currency_keyboard()
)
    except ValueError:
        await message.answer(
            "Пожалуйста, введите корректное число."
        )


@dp.message(CurrencyStates.search)
async def process_search(message: Message, state: FSMContext):
    query = message.text.lower()

    matches = []

    for code, currency in CURRENCIES.items():

        if (
            query in code.lower()
            or query in currency["name"].lower()
        ):
            matches.append((code, currency))

    if not matches:
        await message.answer("❌ Ничего не найдено.")
        return

    await message.answer(
    "🔍 Найденные валюты:",
    reply_markup=search_results_keyboard(matches[:10])
    )

    await state.clear()


async def health(request):
    return web.Response(text="OK")


async def start_web():
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/healthz", health)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


async def main():
    await exchange.update_rates()
    await start_web()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

    