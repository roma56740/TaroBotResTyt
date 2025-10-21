import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import router
from database import init_db  # 👈 это важно

async def main():
    init_db()  # 👈 инициализация базы данных
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
