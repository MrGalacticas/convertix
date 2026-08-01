from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from math import ceil
from constants import CURRENCIES


def main_currency_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text=f"{CURRENCIES['UAH']['flag']} UAH",
        callback_data="UAH"
    )

    builder.button(
        text=f"{CURRENCIES['USD']['flag']} USD",
        callback_data="USD"
    )

    builder.button(
        text=f"{CURRENCIES['EUR']['flag']} EUR",
        callback_data="EUR"
    )

    builder.button(
        text="🌍 Все валюты",
        callback_data="ALL"
    )

    builder.adjust(2)

    return builder.as_markup()


CURRENCIES_PER_PAGE = 10


def all_currencies_keyboard(page: int = 0):
    currencies = list(CURRENCIES.items())

    start = page * CURRENCIES_PER_PAGE
    end = start + CURRENCIES_PER_PAGE

    current_page = currencies[start:end]

    keyboard = []

    for i in range(0, len(current_page), 2):
        row = []

        code, currency = current_page[i]
        row.append(
            InlineKeyboardButton(
                text=f"{currency['flag']} {code}",
                callback_data=code
            )
        )

        if i + 1 < len(current_page):
            code, currency = current_page[i + 1]
            row.append(
                InlineKeyboardButton(
                    text=f"{currency['flag']} {code}",
                    callback_data=code
                )
            )

        keyboard.append(row)

    total_pages = ceil(len(currencies) / CURRENCIES_PER_PAGE)

    navigation = []

    if page > 0:
        navigation.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"page:{page-1}"
            )
        )

    navigation.append(
        InlineKeyboardButton(
            text=f"{page+1}/{total_pages}",
            callback_data="ignore"
        )
    )

    if page < total_pages - 1:
        navigation.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"page:{page+1}"
            )
        )

    keyboard.append(navigation)

    keyboard.append([
        InlineKeyboardButton(
            text="🔍 Поиск",
            callback_data="SEARCH"
        ),
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="BACK"
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )



def search_results_keyboard(results: list[tuple[str, dict]]):
    builder = InlineKeyboardBuilder()

    for code, currency in results:
        builder.button(
            text=f"{currency['flag']} {code}",
            callback_data=code
        )

    builder.adjust(2)

    builder.button(
        text="🔙 Назад",
        callback_data="ALL"
    )

    return builder.as_markup()