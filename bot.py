from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import load_dotenv
import os
import asyncio
from routers import router


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать работу с ботом")
    ]
    await bot.set_my_commands(commands)



async def main():
    load_dotenv()
    tg_token = os.getenv("TG_TOCKEN")
    telegram_bot = Bot(token=tg_token)

    dispatcher = Dispatcher(bot=telegram_bot)
    dispatcher.include_router(router)
    await set_commands(telegram_bot)
    print("Бот запущен. Ожидаем сообщений...")

    await dispatcher.start_polling(telegram_bot)

if __name__ == "__main__":
    asyncio.run(main())