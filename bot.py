import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()



@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message):
    await message.answer("Привет! Я бот, который может выполнять различные команды.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())