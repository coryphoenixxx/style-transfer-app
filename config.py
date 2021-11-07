import os
from pathlib import Path

from aiogram import Bot
from aiogram.types import ParseMode

API_TOKEN = os.getenv('API_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

BASE_DIR = Path(__file__).resolve().parent.parent

IMAGES_DIR = Path('static/images')
CONTENTS_DIR = IMAGES_DIR / 'contents_presets'
STYLES_DIR = IMAGES_DIR / 'styles_presets'

CONTENTS_PATHS = [path.as_posix() for path in CONTENTS_DIR.glob('*.jpg')]  # TODO: create function
STYLES_PATHS = [path.as_posix() for path in STYLES_DIR.glob('*.jpg')]

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
