import asyncio
import os
import aiohttp_jinja2
import jinja2
import random

from aiogram import Bot, Dispatcher
from aiogram.types import Message, InputFile, InputMediaPhoto, MediaGroup
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


class States(StatesGroup):
    waiting_for_content = State()
    waiting_for_selection_style = State()


@dp.message_handler(state=States.waiting_for_content, commands='cancel')
async def cmd_cancel(msg: Message, state: FSMContext):
    if await state.get_state() is None:
        return

    await msg.answer(text="❗ <b>Canceled.</b>")
    await state.finish()


@dp.message_handler(commands=["start"])
async def cmd_start(msg: Message):
    await States.waiting_for_content.set()
    await bot.send_message(msg.from_user.id, text='Send me an image! or /cancel')


@dp.message_handler(state=States.waiting_for_content, content_types=['photo'])
async def waiting_for_content(msg: Message):
    await msg.photo[-1].download('images/test.jpg')

    await msg.answer("Ok, now choose the style image!")

    media = MediaGroup()
    for i in range(1, 11):
        media.attach_photo(InputFile(f'images/style_images/default_style{i}.jpg'))
    await msg.answer_media_group(media)

    media = MediaGroup()
    for i in range(11, 21):
        media.attach_photo(InputFile(f'images/style_images/default_style{i}.jpg'))
    await msg.answer_media_group(media)

    await States.next()


@dp.message_handler(state=States.waiting_for_selection_style)
async def waiting_for_selection_style(msg: Message, state: FSMContext):
    user_choice = msg.text
    await msg.reply('Ok, now wait...')

    user_choice = random.choice(range(1, 21))
    content_url = 'images/test.jpg'
    style_url = f'images/style_images/default_style{user_choice}.jpg'

    eval_func(content_url, style_url)

    await msg.answer_photo(InputFile(f'images/stylized.jpg'))

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
