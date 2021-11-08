import asyncio
import random
from contextlib import suppress
from io import BytesIO

from PIL import Image
from aiogram import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import MediaGroup, InputFile, Message, CallbackQuery
from aiogram.utils.exceptions import MessageNotModified, MessageToEditNotFound, MessageCantBeEdited

from bot.keyboards import make_style_choice_kb, make_content_choice_kb, make_style_presets_kb, \
    make_content_presets_kb
from config import IMAGES_DIR, STYLES_PATHS, CONTENTS_PATHS, API_TOKEN
from net.eval import eval
from utils import cut_into_chunks, draw_number

from aiogram import Bot
from aiogram.types import ParseMode


bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


suppress_exceptions = (AttributeError, MessageNotModified, MessageToEditNotFound, MessageCantBeEdited)


class States(StatesGroup):
    waiting_for_user_content = State()
    waiting_for_user_style = State()
    calculation = State()


async def entry_point_handler(user_id: int):
    await States.waiting_for_user_content.set()
    await bot.send_message(user_id,
                           text="<b>❗ Send me an image for stylization or press for selection from the presets.</b>",
                           reply_markup=await make_content_presets_kb())


async def form_and_send_media(call: CallbackQuery, paths: list):
    """Send numbered images to the user in chunks of 10"""
    media = MediaGroup()
    index = 0
    for chunk in cut_into_chunks(paths, 10):
        for path in chunk:
            index += 1
            img = await draw_number(path, index)
            media.attach_photo(InputFile(img))
        await call.message.answer_media_group(media)
        media = MediaGroup()

        if len(paths) > 20:
            await asyncio.sleep(3)  # Prevent flood exception

    media.clean()


@dp.message_handler(commands=["start"])
async def cmd_start(msg: Message):
    await msg.answer("<b>❗ Hi!"
                     "\nI'm a style transfer bot."
                     "\nI can stylize your images.</b>")
    await msg.answer_photo(InputFile(IMAGES_DIR / 'welcome.jpg'))
    await entry_point_handler(msg.from_user.id)


@dp.message_handler(commands=["stylize"])
async def cmd_stylize(msg: Message):
    await entry_point_handler(msg.from_user.id)


@dp.callback_query_handler(Text(equals='cancel'), state=[States.waiting_for_user_content,
                                                         States.waiting_for_user_style])
async def cmd_cancel(call: CallbackQuery, state: FSMContext):
    await call.answer(text="❗ Canceled.")
    with suppress(*suppress_exceptions):
        await bot.delete_message(call.from_user.id, call.message.message_id)
    await state.finish()
    await call.message.answer("<b>❗ Ok. If you want to try again then enter /stylize.</b>")


@dp.message_handler(state=States.waiting_for_user_content, content_types=['photo'])
async def get_user_content(msg: Message, state: FSMContext):
    with suppress(*suppress_exceptions):
        await bot.delete_message(msg.from_user.id, msg.message_id - 1)

    content_io = BytesIO()
    await msg.photo[-1].download(destination_file=content_io)
    await state.update_data(user_content=content_io)

    await msg.answer(text="<b>❗ Ok, I got it. Now send me a style image or press for selection from the presets.</b>",
                     reply_markup=await make_style_presets_kb())
    await States.waiting_for_user_style.set()


@dp.callback_query_handler(Text(equals='content_presets'), state=States.waiting_for_user_content)
async def send_content_presets(call: CallbackQuery):
    with suppress(*suppress_exceptions):
        await bot.delete_message(call.from_user.id, call.message.message_id)

    await call.message.answer("<b>❗ CONTENT PRESETS:</b>")
    await form_and_send_media(call, CONTENTS_PATHS)
    await call.message.answer(text="<b>❗ Press the content image number.</b>",
                              reply_markup=await make_content_choice_kb())


@dp.callback_query_handler(Text(startswith='content_'), state=States.waiting_for_user_content)
async def get_selected_user_content(call: CallbackQuery, state: FSMContext):
    with suppress(*suppress_exceptions):
        await bot.delete_message(call.from_user.id, call.message.message_id)

    user_content_choice = CONTENTS_PATHS[int(call.data[8:]) - 1]

    with Image.open(user_content_choice) as img:
        content_io = BytesIO()
        img.save(content_io, format='JPEG')
        content_io.seek(0)
        await state.update_data(user_content=content_io)

    await call.message.answer(text="<b>❗ Ok, I got it. Now send me a style image"
                                   "or press for selection from the presets.</b>",
                              reply_markup=await make_style_presets_kb())

    await States.waiting_for_user_style.set()


@dp.message_handler(state=States.waiting_for_user_content, content_types=['document'])
async def get_content_document(msg: Message):
    with suppress(*suppress_exceptions):
        await bot.delete_message(msg.from_user.id, msg.message_id-1)

    await msg.answer("<b>❗ I can't handle uncompressed images or a document...</b>")
    await asyncio.sleep(1)
    await msg.answer(text="<b>❗ Send me an image for stylization or press for selection from the presets.</b>",
                     reply_markup=await make_content_presets_kb())


@dp.message_handler(state=States.waiting_for_user_style, content_types=['document'])
async def get_style_document(msg: Message):
    with suppress(*suppress_exceptions):
        await bot.delete_message(msg.from_user.id, msg.message_id-1)

    await msg.answer("<b>❗ I can't handle uncompressed images or a document...</b>")
    await asyncio.sleep(1)
    await msg.answer(text="<b>❗ Send me a style image or press for selection from the presets.</b>",
                     reply_markup=await make_style_presets_kb())


@dp.message_handler(state=States.waiting_for_user_style, content_types=['photo'])
async def get_user_style(msg: Message, state: FSMContext):
    with suppress(*suppress_exceptions):
        await bot.delete_message(msg.from_user.id, msg.message_id - 1)

    content_io = (await state.get_data()).get('user_content')
    await state.reset_data()
    style_io = BytesIO()
    await msg.photo[-1].download(destination_file=style_io)
    await msg.answer("<b>❗ I got it. Now wait...</b>")

    await States.calculation.set()

    stylized_io = await eval(content_io, style_io)

    await msg.answer("<b>❗ Your result:</b>")
    stylized_io.seek(0)
    await msg.answer_photo(stylized_io)

    await state.finish()
    await asyncio.sleep(1)
    await msg.answer("<b>❗ If you want to try again press /stylize.</b>")


@dp.callback_query_handler(Text(equals='style_presets'), state=States.waiting_for_user_style)
async def send_style_presets(call: CallbackQuery):
    with suppress(*suppress_exceptions):
        await bot.delete_message(call.from_user.id, call.message.message_id)

    await call.message.answer("<b>❗ STYLE PRESETS:</b>")
    await form_and_send_media(call, STYLES_PATHS)
    await call.message.answer(text="<b>❗ Press the style image number.</b>",
                              reply_markup=await make_style_choice_kb())


@dp.callback_query_handler(Text(startswith='style_'), state=States.waiting_for_user_style)
async def stylize_by_style_number(call: CallbackQuery, state: FSMContext):
    with suppress(*suppress_exceptions):
        await bot.delete_message(call.from_user.id, call.message.message_id)

    await States.calculation.set()

    user_choice = call.data[6:]

    user_style_number = random.choice(range(1, len(STYLES_PATHS)+1)) if user_choice == 'random' else int(user_choice)

    await call.message.answer("<b>❗ I got it. Now wait...</b>")

    content_io = (await state.get_data()).get('user_content')
    await state.reset_data()

    style_url = STYLES_PATHS[user_style_number-1]
    style_title = ' '.join(style_url.split('/')[-1].split('.')[:-1])
    await call.message.answer(text=f"<b>❗ + {style_title}</b>")

    stylized_io = await eval(content_io, style_url)
    stylized_io.seek(0)

    media = MediaGroup()
    media.attach_photo(InputFile(style_url))
    media.attach_photo(InputFile(stylized_io))
    await call.message.answer_media_group(media)
    media.clean()

    await state.finish()
    await asyncio.sleep(1)
    await call.message.answer("<b>❗ If you want to try again press /stylize.</b>")


@dp.callback_query_handler(Text(equals='all'), state=States.waiting_for_user_style)
async def stylize_and_send_for_all_styles(call: CallbackQuery, state: FSMContext):
    with suppress(*suppress_exceptions):
        await bot.edit_message_reply_markup(call.from_user.id, call.message.message_id)

    await States.calculation.set()

    content_io = (await state.get_data()).get('user_content')
    await state.reset_data()

    index = 1
    amount = len(STYLES_PATHS)
    for style_url in STYLES_PATHS:
        stylized_io = await eval(content_io, style_url)
        stylized_io.seek(0)
        style_title = ' '.join(style_url.split('/')[-1].split('.')[:-1])
        media = MediaGroup()
        media.attach_photo(InputFile(style_url))
        media.attach_photo(InputFile(stylized_io))

        await call.message.answer(text=f"<b>❗ + {style_title} ({index}/{amount})</b>")
        await call.message.answer_media_group(media)
        media.clean()
        index += 1

    await state.finish()
    await asyncio.sleep(1)
    await call.message.answer("<b>❗ If you want to try again press /stylize.</b>")
