"""Configuration settings for the poem short generator."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4"

# Piper TTS Configuration
PIPER_VOICE_MODEL = os.getenv("PIPER_VOICE_MODEL", "en_US-lessac-medium")
PIPER_VOICE_PATH = os.getenv("PIPER_VOICE_PATH", None)  # Optional: path to voice model file

# Video Configuration
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
VIDEO_CODEC = "libx264"

# Paths
BASE_DIR = Path(__file__).parent
ASSETS_BACKGROUNDS_DIR = BASE_DIR / "assets" / "backgrounds"
OUTPUT_BASE_DIR = BASE_DIR / "output"

# Caption Styling
CAPTION_FONT = "Arial"  # Default font, can be overridden with path to TTF file
CAPTION_FONT_SIZE = 48
CAPTION_COLOR = (255, 255, 255)  # White in RGB
CAPTION_POSITION = "center"  # Options: "center", "bottom", "top"
CAPTION_STROKE_COLOR = (0, 0, 0)  # Black outline for better readability
CAPTION_STROKE_WIDTH = 2
CAPTION_MAX_WIDTH = 900  # Maximum width for text wrapping (pixels)

# Output Configuration
OUTPUT_VIDEO_FORMAT = "mp4"
OUTPUT_AUDIO_FORMAT = "wav"

