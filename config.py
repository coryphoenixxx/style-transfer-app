import os
from pathlib import Path


API_TOKEN = os.getenv('API_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

MAX_IMAGE_SIZE = 128

START_ITER = 500000
EVAL_ITER = 500000
MAX_ITER = 1000000
BATCH_SIZE = 18
NUM_WORKERS = 2

IMAGES_DIR = Path('static/images')
CONTENTS_DIR = IMAGES_DIR / 'contents_presets'
STYLES_DIR = IMAGES_DIR / 'styles_presets'

CONTENTS_PATHS = [path.as_posix() for path in CONTENTS_DIR.glob('*.jpg')]
STYLES_PATHS = [path.as_posix() for path in STYLES_DIR.glob('*.jpg')]
