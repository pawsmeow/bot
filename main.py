import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import registration, admin_commands

async def main():
    bot = Bot(token="т7919539622:AAGZWyYCb5fGuduSrbo02uBqobiDRnJMwbg")
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(registration.router, admin_commands.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
