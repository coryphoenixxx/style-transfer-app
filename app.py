import asyncio
import os
import aiohttp_jinja2
import jinja2
import random

from time import time

from contextlib import suppress
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InputFile, MediaGroup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageNotModified, MessageToEditNotFound, MessageCantBeEdited
from aiohttp import web
from aiohttp.web_request import Request
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from net.eval import eval_func
# from net.loader import *

suppress_exceptions = (AttributeError, MessageNotModified, MessageToEditNotFound, MessageCantBeEdited)

API_TOKEN = os.getenv('API_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
routes = web.RouteTableDef()

style_choice_kb = InlineKeyboardMarkup(row_width=5)

buttons = [InlineKeyboardButton(text=str(i), callback_data=f'style_{i}') for i in range(1, 21)]
buttons.append(InlineKeyboardButton(text='Random', callback_data=f'style_random'))

style_choice_kb.add(*buttons)


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
    await msg.photo[-1].download(f'images/user{msg.from_user.id}_image.jpg')

    media = MediaGroup()
    for i in range(1, 21):
        media.attach_photo(InputFile(f'images/numbered_style/numbered_style_{i}.jpg'))
        if i % 10 == 0:
            await msg.answer_media_group(media)
            media = MediaGroup()
    media.clean()

    await msg.answer("Send me the style image number or press random button!", reply_markup=style_choice_kb)

    await States.next()


@dp.callback_query_handler(Text(startswith='style_'), state=States.waiting_for_selection_style)
async def waiting_for_selection_style(call: CallbackQuery, state: FSMContext):
    with suppress(*suppress_exceptions):
        await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id)

    user_id = call.from_user.id
    user_choice = call.data[6:]

    if user_choice == 'random':
        style_number = random.choice(range(1, 21))
    else:
        style_number = user_choice

    await call.message.reply('Ok, now wait...', )

    content_url = f'images/user{user_id}_image.jpg'
    style_url = f'images/default_style/default_style_{style_number}.jpg'

    start = time()
    print(start)
    eval_func(content_url, style_url, user_id)
    print(time() - start)

    await call.message.answer_photo(InputFile(f'images/user{user_id}_stylized.jpg'))

    os.remove(f'images/user{user_id}_image.jpg')
    os.remove(f'images/user{user_id}_stylized.jpg')

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
