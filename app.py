import asyncio
import os
import aiohttp_jinja2
import jinja2

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiohttp import web
from aiohttp.web_request import Request
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

from net.eval import eval_func

API_TOKEN = os.getenv('API_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
routes = web.RouteTableDef()


@dp.message_handler(commands=["start"])
async def cmd_start(msg: Message):
    await States.waiting_for_content.set()
    await bot.send_message(msg.from_user.id, text='Send me an image! or /cancel')


class States(StatesGroup):
    waiting_for_content = State()
    waiting_for_selection_style = State()


@dp.message_handler(state=States.waiting_for_content, commands='cancel')
async def cmd_cancel(msg: Message, state: FSMContext):
    if await state.get_state() is None:
        return

    await msg.answer(text='❗ <b>Canceled.</b>')
    await state.finish()


@dp.message_handler(state=States.waiting_for_content)
async def waiting_for_content(msg: Message, state: FSMContext):
    await msg.reply('Content')
    await States.next()


@dp.message_handler(state=States.waiting_for_selection_style)
async def waiting_for_selection_style(msg: Message, state: FSMContext):
    await msg.reply('Style')
    await state.finish()


@aiohttp_jinja2.template('main.html')
async def get_handler(request: Request):
    return {'content_url': "images/default_content.jpg",
            'style_url': "images/default_style.jpg"}


@aiohttp_jinja2.template('main.html')
async def post_handler(request: Request):
    content_url = 'images/default_content.jpg'
    style_url = 'images/default_style.jpg'

    eval_func(content_url, style_url)

    return {'content_url': "images/default_content.jpg",
            'style_url': "images/default_style.jpg",
            'stylized_url': "images/stylized.jpg"
            }


async def main():
    app = web.Application()
    aiohttp_jinja2.setup(
        app=app,
        loader=jinja2.FileSystemLoader('templates')
    )

    app.add_routes([web.get(path='/', handler=get_handler),
                    web.post(path='/', handler=post_handler),
                    web.static(prefix='/images', path='images', show_index=True)])

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
