import asyncio
import os
import random
from contextlib import suppress
from io import BytesIO
from pathlib import Path
from PIL import Image

import aiohttp_jinja2
import jinja2
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InputFile, MediaGroup, InlineKeyboardMarkup, InlineKeyboardButton, \
    ParseMode
from aiogram.utils.exceptions import MessageNotModified, MessageToEditNotFound, MessageCantBeEdited
from aiohttp import web
from aiohttp.web_request import Request

from net.eval import eval_func
from net.utils import chunks, draw_number

suppress_exceptions = (AttributeError, MessageNotModified, MessageToEditNotFound, MessageCantBeEdited)

API_TOKEN = os.getenv('API_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

IMAGES_DIR = Path('static/images')
CONTENTS_DIR = IMAGES_DIR / 'contents_presets'
STYLES_DIR = IMAGES_DIR / 'styles_presets'

CONTENTS_PATHS = [path.as_posix() for path in CONTENTS_DIR.glob('*.jpg')]
STYLES_PATHS = [path.as_posix() for path in STYLES_DIR.glob('*.jpg')]

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
routes = web.RouteTableDef()

cancel_kb = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Cancel', callback_data='cancel'))

content_choice_kb = InlineKeyboardMarkup(row_width=3)
buttons = [InlineKeyboardButton(text=str(i), callback_data=f'content_{i}') for i in range(1, len(CONTENTS_PATHS) + 1)]
content_choice_kb.add(*buttons)

content_type_choice_kb = InlineKeyboardMarkup(row_width=2)
content_type_choice_kb.add(InlineKeyboardButton(text='Show Content Presets', callback_data='content_presets'))
content_type_choice_kb.add(InlineKeyboardButton(text='Cancel', callback_data='cancel'))

style_choice_kb = InlineKeyboardMarkup(row_width=5)
buttons = [InlineKeyboardButton(text=str(i), callback_data=f'style_{i}') for i in range(1, len(STYLES_PATHS) + 1)]
buttons.append(InlineKeyboardButton(text='Random', callback_data='style_random'))
buttons.append(InlineKeyboardButton(text='All', callback_data='all'))
style_choice_kb.add(*buttons)

style_type_choice_kb = InlineKeyboardMarkup(row_width=2)
style_type_choice_kb.add(InlineKeyboardButton(text='Show Style Presets', callback_data='style_presets'))
style_type_choice_kb.add(InlineKeyboardButton(text='Cancel', callback_data='cancel'))


class States(StatesGroup):
    waiting_for_user_content = State()
    waiting_for_user_style = State()


async def stylization_entry_point_handler(user_id):
    await States.waiting_for_user_content.set()
    await bot.send_message(user_id,
                           text='<b>❗ Send me an image for stylization or press for selection from the presets.</b>',
                           reply_markup=content_type_choice_kb)


# BOT HANDLERS
@dp.message_handler(commands=["start"])
async def cmd_start(msg: Message):
    await msg.answer("<b>❗ Hi!"
                     "\nI'm a style transfer bot."
                     "\nI can stylize your images.</b>")
    await msg.answer_photo(InputFile(IMAGES_DIR / 'welcome.jpg'))
    await stylization_entry_point_handler(msg.from_user.id)


@dp.message_handler(commands=["stylize"])
async def preparation_handler(msg: Message):
    await stylization_entry_point_handler(msg.from_user.id)


@dp.callback_query_handler(Text(equals='cancel'), state=States.waiting_for_user_content)
async def cmd_cancel(call: CallbackQuery, state: FSMContext):
    if await state.get_state() is None:
        return

    await call.answer(text="❗ Canceled.")
    with suppress(*suppress_exceptions):
        await bot.delete_message(call.from_user.id, call.message.message_id)
    await state.finish()
    await call.message.answer("<b>❗ Ok. If you want to try again then enter /stylize.</b>")


@dp.message_handler(state=States.waiting_for_user_content, content_types=['photo'])
async def waiting_for_content(msg: Message, state: FSMContext):
    with suppress(*suppress_exceptions):
        await bot.delete_message(msg.from_user.id, msg.message_id - 1)

    content_io = BytesIO()
    await msg.photo[-1].download(content_io)
    await state.update_data(user_content=content_io)

    await msg.answer(text="<b>❗ Ok, I got it. Now send me a style image or press for selection from the presets.</b>",
                     reply_markup=style_type_choice_kb)
    await States.waiting_for_user_style.set()


@dp.callback_query_handler(Text(equals='content_presets'), state=States.waiting_for_user_content)
async def send_content_presets(call: CallbackQuery):
    with suppress(*suppress_exceptions):
        await bot.delete_message(call.from_user.id, call.message.message_id)

    await call.message.answer("<b>❗ CONTENT PRESETS:</b>")
    media = MediaGroup()
    index = 0
    for chunk in chunks(CONTENTS_PATHS, 10):
        for path in chunk:
            index += 1
            img = await draw_number(path, index)
            media.attach_photo(InputFile(img))
        await call.message.answer_media_group(media)
        media = MediaGroup()
    media.clean()

    await call.message.answer(text="<b>❗ Press the content image number.</b>",
                              reply_markup=content_choice_kb)


@dp.callback_query_handler(Text(startswith='content_'), state=States.waiting_for_user_content)
async def waiting_for_selection_content(call: CallbackQuery, state: FSMContext):
    with suppress(*suppress_exceptions):
        await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id)

    user_content_choice = CONTENTS_PATHS[int(call.data[8:]) - 1]

    with Image.open(user_content_choice) as img:
        content_io = BytesIO()
        img.save(content_io, format='JPEG')
        content_io.seek(0)
        await state.update_data(user_content=content_io)

    await call.message.answer(text="<b>❗ Ok, I got it. Now send me a style image "
                                   "or press for selection from the presets.</b>",
                              reply_markup=style_type_choice_kb)

    await States.waiting_for_user_style.set()


# @dp.message_handler(state=States.waiting_for_user_content, content_types=['document'])
# async def waiting_for_user_content(msg: Message):
#     await msg.answer("<b>I can't handle uncompressed images or a document...</b>")
#     await stylization_entry_point_handler(msg.from_user.id)
#
#
# @dp.message_handler(state=States.waiting_for_user_style, content_types=['document'])
# async def waiting_for_user_style(msg: Message):
#     await msg.answer("<b>I can't handle uncompressed images or a document...</b>")
#     await stylization_entry_point_handler(msg.from_user.id)


@dp.message_handler(state=States.waiting_for_user_style, content_types=['photo'])
async def waiting_for_style(msg: Message, state: FSMContext):
    with suppress(*suppress_exceptions):
        await bot.delete_message(msg.from_user.id, msg.message_id - 1)

    content_io = (await state.get_data()).get('user_content')
    await state.reset_data()
    style_io = BytesIO()
    await msg.photo[-1].download(style_io)
    await msg.answer("<b>❗ I got it. Now wait...</b>")

    stylized_img_obj = await eval_func(content_io, style_io)
    stylized_img_obj.seek(0)

    await msg.answer("<b>❗ Your result:</b>")
    await msg.answer_photo(stylized_img_obj)

    await state.finish()


@dp.callback_query_handler(Text(equals='style_presets'), state=States.waiting_for_user_style)
async def waiting_for_selection_style(call: CallbackQuery):
    with suppress(*suppress_exceptions):
        await bot.delete_message(call.from_user.id, call.message.message_id)

    await call.message.answer("<b>❗ STYLE PRESETS:</b>")
    media = MediaGroup()
    index = 0
    for chunk in chunks(STYLES_PATHS, 10):
        for path in chunk:
            index += 1
            img = await draw_number(path, index)
            media.attach_photo(InputFile(img))
        await call.message.answer_media_group(media)
        media = MediaGroup()
    media.clean()

    await call.message.answer(text="<b>❗ Press the style image number.</b>",
                              reply_markup=style_choice_kb)


@dp.callback_query_handler(Text(startswith='style_'), state=States.waiting_for_user_style)
async def waiting_for_selection_style(call: CallbackQuery, state: FSMContext):
    with suppress(*suppress_exceptions):
        await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id)

    user_choice = call.data[6:]

    user_style_number = random.choice(range(1, len(STYLES_PATHS)+1)) if user_choice == 'random' else int(user_choice)

    await call.message.answer("<b>❗ I got it. Now wait...</b>")

    content_io = (await state.get_data()).get('user_content')
    await state.reset_data()

    style_url = STYLES_PATHS[user_style_number-1]

    stylized_io = await eval_func(content_io, style_url)
    stylized_io.seek(0)

    media = MediaGroup()
    media.attach_photo(InputFile(style_url))
    media.attach_photo(InputFile(stylized_io))
    await call.message.answer_media_group(media)
    media.clean()

    await state.finish()

    await stylization_entry_point_handler(call.from_user.id)


@dp.callback_query_handler(Text(equals='all'), state=States.waiting_for_user_style)
async def waiting_for_selection_style(call: CallbackQuery, state: FSMContext):
    with suppress(*suppress_exceptions):
        await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id)

    content_io = (await state.get_data()).get('user_content')
    await state.reset_data()

    index = 1
    amount = len(STYLES_PATHS)
    for style_url in STYLES_PATHS:
        stylized_io = await eval_func(content_io, style_url)
        stylized_io.seek(0)
        style_title = ' '.join(style_url.split('/')[-1].split('.')[:-1])
        await call.message.answer(text=f"<b>❗ + {style_title} ({index}/{amount})</b>")
        media = MediaGroup()
        media.attach_photo(InputFile(style_url))
        media.attach_photo(InputFile(stylized_io))
        await call.message.answer_media_group(media)
        media.clean()
        index += 1

    await state.finish()


# WEB HANDLERS
@aiohttp_jinja2.template('main.html')
async def get_handler(request: Request):
    return {}


async def get_images_handler(request: Request):
    images_urls = {'contents_urls': CONTENTS_PATHS,
                   'styles_urls': STYLES_PATHS}
    return web.json_response(images_urls)


async def post_handler(request):
    data = await request.post()

    content_img_obj = BytesIO(data['content'].file.read())
    style_img_obj = BytesIO(data['style'].file.read())

    stylized_img_obj = await eval_func(content_img_obj, style_img_obj)

    try:
        await asyncio.sleep(0.5)
        return web.Response(body=stylized_img_obj.getvalue(), content_type='image/jpeg')
    finally:
        stylized_img_obj.close()


async def main():
    app = web.Application(client_max_size=1024 ** 2 * 30)
    aiohttp_jinja2.setup(
        app=app,
        loader=jinja2.FileSystemLoader('templates')
    )

    app.add_routes([web.get(path='/', handler=get_handler),
                    web.get(path='/getimages', handler=get_images_handler),
                    web.post(path='/', handler=post_handler),
                    web.static(prefix='/static', path='static', show_index=True)])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "192.168.1.2")
    await bot.send_message(ADMIN_ID, 'Bot started. /start')

    tasks = [
        site.start(),
        dp.start_polling()
    ]
    print('App started.')
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
