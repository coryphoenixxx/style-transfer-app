from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CONTENTS_PRESETS_PATHS, STYLES_PRESETS_PATHS


async def make_content_choice_kb():
    content_choice_kb = InlineKeyboardMarkup(row_width=3)
    buttons = [InlineKeyboardButton(text=str(i), callback_data=f'content_{i}') for i in range(1, len(CONTENTS_PRESETS_PATHS) + 1)]
    content_choice_kb.add(*buttons)
    return content_choice_kb


async def make_content_presets_kb():
    content_presets_kb = InlineKeyboardMarkup(row_width=2)
    content_presets_kb.add(InlineKeyboardButton(text='Show Content Presets', callback_data='content_presets'))
    content_presets_kb.add(InlineKeyboardButton(text='Cancel', callback_data='cancel'))
    return content_presets_kb


async def make_style_choice_kb():
    style_choice_kb = InlineKeyboardMarkup(row_width=5)
    buttons = [InlineKeyboardButton(text=str(i), callback_data=f'style_{i}') for i in range(1, len(STYLES_PRESETS_PATHS) + 1)]
    buttons.append(InlineKeyboardButton(text='Random', callback_data='style_random'))
    buttons.append(InlineKeyboardButton(text='All', callback_data='all'))
    style_choice_kb.add(*buttons)
    return style_choice_kb


async def make_style_presets_kb():
    style_presets_kb = InlineKeyboardMarkup(row_width=2)
    style_presets_kb.add(InlineKeyboardButton(text='Show Style Presets', callback_data='style_presets'))
    style_presets_kb.add(InlineKeyboardButton(text='Cancel', callback_data='cancel'))
    return style_presets_kb
