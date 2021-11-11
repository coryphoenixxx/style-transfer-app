from pathlib import Path


# API_TOKEN = " <YOUR TOKEN> "
# ADMIN_ID = <YOUR TELEGRAM ID>

MAX_IMAGE_SIZE = 1280  # Stylized image size
EVAL_ITER = 500000  # State iteration for eval

BASE_DIR = Path(__file__).parent.parent

STATE_DICTS_DIR = BASE_DIR / 'app/net/state_dicts'

IMAGES_DIR = Path('static/images')
CONTENT_PRESETS_DIR = IMAGES_DIR / 'content_presets'
STYLE_PRESETS_DIR = IMAGES_DIR / 'style_presets'

CONTENTS_PRESETS_PATHS = [path.as_posix() for path in CONTENT_PRESETS_DIR.glob('*.jpg')]
STYLES_PRESETS_PATHS = [path.as_posix() for path in STYLE_PRESETS_DIR.glob('*.jpg')]


# Train-specific parameters
START_ITER = 500000  # At this iteration neural network will start learn
MAX_ITER = 1000000  # To what iteration the neural network will learn
SAVE_ITER = 5000  # At which iteration the states will saved
BATCH_SIZE = 5
NUM_WORKERS = 4
TRAIN_RESIZE = 512  # Train images resizing value (for dataloader). Change only if you train from scratch!
TRAIN_CONTENT_DIR = Path('app/net/train_images/content')
TRAIN_STYLE_DIR = Path('app/net/train_images/style')
