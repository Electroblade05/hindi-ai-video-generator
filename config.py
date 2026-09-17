import os


# ============================================================
# VIDEO
# ============================================================

FPS = 30

DEFAULT_SHORTS_WIDTH = 1080
DEFAULT_SHORTS_HEIGHT = 1920

DEFAULT_YOUTUBE_WIDTH = 1280
DEFAULT_YOUTUBE_HEIGHT = 720


# ============================================================
# DIRECTORIES
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "output",
)

IMAGES_DIR = os.path.join(
    OUTPUT_DIR,
    "images",
)

AUDIO_DIR = os.path.join(
    OUTPUT_DIR,
    "audio",
)

SCENES_DIR = os.path.join(
    OUTPUT_DIR,
    "scenes",
)

CAPTIONS_DIR = os.path.join(
    OUTPUT_DIR,
    "captions",
)

FINAL_DIR = os.path.join(
    OUTPUT_DIR,
    "final",
)


# ============================================================
# TTS VOICES
# ============================================================

FEMALE_HINDI_VOICE = (
    "hi-IN-SwaraNeural"
)

MALE_HINDI_VOICE = (
    "hi-IN-MadhurNeural"
)

DEFAULT_HINDI_VOICE = (
    FEMALE_HINDI_VOICE
)


# ============================================================
# IMAGE GENERATION
# ============================================================

POLLINATIONS_URL = (
    "https://image.pollinations.ai/prompt/"
)

DEFAULT_LOCAL_IMAGE_ENDPOINT = (
    "http://127.0.0.1:7860"
)


# ============================================================
# FONT
# ============================================================

FONT_DIR = os.path.join(
    BASE_DIR,
    "fonts",
)

FONT_PATH = os.path.join(
    FONT_DIR,
    "NotoSansDevanagari-Regular.ttf",
)
