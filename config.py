from pathlib import Path


API_TOKEN = '<YOUR_API_TOKEN>'
ADMIN_ID = '<YOUR_TELEGRAM_ID>'

MAX_IMAGE_SIZE = 1280
EVAL_ITER = 500000

START_ITER = 500000
MAX_ITER = 1000000
SAVE_ITER = 5000
BATCH_SIZE = 5
NUM_WORKERS = 4
TRAIN_RESIZE = 512
TRAIN_CONTENT_DIR = Path('net/train_images/content')
TRAIN_STYLE_DIR = Path('net/train_images/style')

STATE_DICTS_DIR = Path('net/state_dicts')

IMAGES_DIR = Path('static/images')
CONTENT_PRESETS_DIR = IMAGES_DIR / 'content_presets'
STYLE_PRESETS_DIR = IMAGES_DIR / 'style_presets'

CONTENTS_PRESETS_PATHS = [path.as_posix() for path in CONTENT_PRESETS_DIR.glob('*.jpg')]
STYLES_PRESETS_PATHS = [path.as_posix() for path in STYLE_PRESETS_DIR.glob('*.jpg')]
