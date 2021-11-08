import os
from pathlib import Path


API_TOKEN = os.getenv('API_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

MAX_IMAGE_SIZE = 1280

START_ITER = 500000
EVAL_ITER = 500000
MAX_ITER = 1000000

IMAGES_DIR = Path('static/images')
CONTENTS_DIR = IMAGES_DIR / 'contents_presets'
STYLES_DIR = IMAGES_DIR / 'styles_presets'
STATES_DICTS_DIR = Path('net/state_dicts')

CONTENTS_PATHS = [path.as_posix() for path in CONTENTS_DIR.glob('*.jpg')]
STYLES_PATHS = [path.as_posix() for path in STYLES_DIR.glob('*.jpg')]
