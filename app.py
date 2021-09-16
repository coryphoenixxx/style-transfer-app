import asyncio

from aiogram import Bot, Dispatcher, types
from aiohttp import web

import os


API_TOKEN = os.getenv('API_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
routes = web.RouteTableDef()


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):

    await message.reply("start!")


@routes.get('/')
async def api_handler(request):
    return web.Response(text='Hello')


async def main():

    app = web.Application()
    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 9000)

    tasks = [
        site.start(),
        dp.start_polling()
    ]

    await asyncio.gather(*tasks)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
