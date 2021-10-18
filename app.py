import asyncio
import os
import random
from contextlib import suppress
from io import BytesIO

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

suppress_exceptions = (AttributeError, MessageNotModified, MessageToEditNotFound, MessageCantBeEdited)

API_TOKEN = os.getenv('API_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
routes = web.RouteTableDef()

style_choice_kb = InlineKeyboardMarkup(row_width=5)
buttons = [InlineKeyboardButton(text=str(i), callback_data=f'style_{i}') for i in range(1, 21)]
buttons.append(InlineKeyboardButton(text='Random', callback_data=f'style_random'))
buttons.append(InlineKeyboardButton(text='All', callback_data=f'all'))
style_choice_kb.add(*buttons)

cancel_kb = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Cancel', callback_data='cancel'))

style_type_choice_kb = InlineKeyboardMarkup(row_width=2)
style_type_choice_kb.add(InlineKeyboardButton(text='Send My Style Image', callback_data='user_style'))
style_type_choice_kb.add(InlineKeyboardButton(text='Choose Prepared Style Images', callback_data='prep_style'))


class States(StatesGroup):
    waiting_for_content = State()
    waiting_for_user_style = State()
    waiting_for_selection_style = State()


async def stylization_entry_point_handler(user_id):
    await States.waiting_for_content.set()
    await bot.send_message(user_id, text='<b>❗ Send me an image for stylization!</b>', reply_markup=cancel_kb)


@dp.message_handler(commands=["start"])
async def cmd_start(msg: Message):
    await msg.answer("<b>Hi! I'm a style transfer bot."
                     "\n(SANet implementation: https://arxiv.org/pdf/1812.02342.pdf)"
                     "\n\nI can stylize your images.</b>")
    await msg.answer_photo(InputFile('images/welcome.jpg'))
    await stylization_entry_point_handler(msg.from_user.id)


@dp.message_handler(commands=["stylize"])
async def preparation_handler(msg: Message):
    await stylization_entry_point_handler(msg.from_user.id)


@dp.callback_query_handler(Text(equals='cancel'), state=States.waiting_for_content)
async def cmd_cancel(call: CallbackQuery, state: FSMContext):
    if await state.get_state() is None:
        return

    await call.answer(text="❗ Canceled.")
    with suppress(*suppress_exceptions):
        await bot.delete_message(call.from_user.id, call.message.message_id)
    await state.finish()
    await call.message.answer("<b>❗ Ok. If you want to try again then enter /stylize.</b>")


@dp.message_handler(state=States.waiting_for_content, content_types=['photo'])
async def waiting_for_content(msg: Message, state: FSMContext):
    with suppress(*suppress_exceptions):
        await bot.delete_message(msg.from_user.id, msg.message_id - 1)

    content_io = BytesIO()
    await msg.photo[-1].download(content_io)
    await state.update_data(user_content=content_io)

    await msg.answer("<b>❗ What's next?</b>", reply_markup=style_type_choice_kb)


# @dp.message_handler(state=States.waiting_for_content, content_types=['document'])
# async def waiting_for_user_content(msg: Message):
#     await msg.answer("<b>I can't handle uncompressed images or a document...</b>")
#     await stylization_entry_point_handler(msg.from_user.id)
#
#
# @dp.message_handler(state=States.waiting_for_user_style, content_types=['document'])
# async def waiting_for_user_style(msg: Message):
#     await msg.answer("<b>I can't handle uncompressed images or a document...</b>")
#     await stylization_entry_point_handler(msg.from_user.id)


@dp.callback_query_handler(Text(equals='user_style'), state=States.waiting_for_content)
async def waiting_for_selection_style(call: CallbackQuery):
    with suppress(*suppress_exceptions):
        await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.message.answer("<b>Ok, send me your style image.</b>", reply_markup=cancel_kb)
    await States.waiting_for_user_style.set()


@dp.message_handler(state=States.waiting_for_user_style, content_types=['photo'])
async def waiting_for_content(msg: Message, state: FSMContext):
    user_id = msg.from_user.id

    with suppress(*suppress_exceptions):
        await bot.delete_message(user_id, msg.message_id - 1)

    content_io = (await state.get_data()).get('user_content')
    await state.reset_data()
    style_io = BytesIO()
    await msg.photo[-1].download(style_io)
    await msg.answer('I got it. Now wait...')

    stylized_img_obj = await eval_func(content_io, style_io)
    stylized_img_obj.seek(0)

    await msg.answer("<b>Your result:</b>")
    await msg.answer_photo(stylized_img_obj)

    await state.finish()


@dp.callback_query_handler(Text(equals='prep_style'), state=States.waiting_for_content)
async def waiting_for_selection_style(call: CallbackQuery):
    with suppress(*suppress_exceptions):
        await bot.delete_message(call.from_user.id, call.message.message_id)

    media = MediaGroup()
    for i in range(1, 21):
        media.attach_photo(InputFile(f'images/numbered_style/numbered_style_{i}.jpg'))
        if i % 10 == 0:
            await call.message.answer_media_group(media)
            media = MediaGroup()
    media.clean()

    await call.message.answer("Send me the style image number or press random button!", reply_markup=style_choice_kb)
    await States.waiting_for_selection_style.set()


@dp.callback_query_handler(Text(startswith='style_'), state=States.waiting_for_selection_style)
async def waiting_for_selection_style(call: CallbackQuery, state: FSMContext):
    with suppress(*suppress_exceptions):
        await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id)

    user_choice = call.data[6:]

    style_number = random.choice(range(1, 21)) if user_choice == 'random' else user_choice

    await call.message.answer("<b>I got it. Now wait...</b>")

    content_io = (await state.get_data()).get('user_content')
    await state.reset_data()

    style_url = f'images/default_style/default_style_{style_number}.jpg'

    stylized_io = await eval_func(content_io, style_url)
    stylized_io.seek(0)

    media = MediaGroup()
    media.attach_photo(InputFile(style_url))
    media.attach_photo(InputFile(stylized_io))
    await call.message.answer_media_group(media)
    media.clean()

    await state.finish()

    await stylization_entry_point_handler(call.from_user.id)


@dp.callback_query_handler(Text(startswith='all'), state=States.waiting_for_selection_style)
async def waiting_for_selection_style(call: CallbackQuery, state: FSMContext):
    with suppress(*suppress_exceptions):
        await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id)

    content_io = (await state.get_data()).get('user_content')
    await state.reset_data()

    for style_number in range(1, 21):
        style_url = f'images/default_style/default_style_{style_number}.jpg'

        stylized_io = await eval_func(content_io, style_url)
        stylized_io.seek(0)

        media = MediaGroup()

        media.attach_photo(InputFile(f'images/default_style/default_style_{style_number}.jpg'))
        media.attach_photo(InputFile(stylized_io))
        await call.message.answer_media_group(media)
        media.clean()
        await asyncio.sleep(2)
    await state.finish()


@aiohttp_jinja2.template('main.html')
async def get_handler(request: Request):
    return


async def post_handler(request):
    data = await request.post()

    content_img_obj = BytesIO(data['content'].file.read())
    style_img_obj = BytesIO(data['style'].file.read())

    stylized_img_obj = await eval_func(content_img_obj, style_img_obj)

    await asyncio.sleep(2)

    try:
        return web.Response(body=stylized_img_obj.getvalue(), content_type='image/jpeg')
    finally:
        stylized_img_obj.close()


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
