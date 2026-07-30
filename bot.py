import asyncio
from email import message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from exchange import Exchange
from constants import CURRENCIES

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
exchange = Exchange()
class CurrencyStates(StatesGroup):
    from_currency = State()
    to_currency = State()
    amount = State()


def currency_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="🇺🇦 UAH", callback_data="UAH")
    builder.button(text="🇺🇸 USD", callback_data="USD")
    builder.button(text="🇪🇺 EUR", callback_data="EUR")

    builder.adjust(1)

    return builder.as_markup()

@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer(
    """Привет! Это калькулятор валют в Telegram.

Выберите валюту, из которой хотите конвертировать:""",
    reply_markup=currency_keyboard()
)


@dp.callback_query()
async def process_currency(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    current_state = await state.get_state()

    if current_state is None:
        await state.update_data(from_currency=callback.data)
        await state.set_state(CurrencyStates.to_currency)

        await callback.message.answer(
            "Теперь выберите валюту, в которую хотите конвертировать:",
            reply_markup=currency_keyboard()
        )

    elif current_state == CurrencyStates.to_currency:
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
            f"{amount} {from_currency} = {result} {to_currency}"
        )
        await state.clear()
        await message.answer(
    "Хотите выполнить ещё одну конвертацию?\n\nВыберите валюту:",
    reply_markup=currency_keyboard()
)
    except ValueError:
        await message.answer(
            "Пожалуйста, введите корректное число."
        )


async def main():
    await exchange.update_rates()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

    