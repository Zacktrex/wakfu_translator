# wakfu_translator/constants.py
"""
Application-wide constants and configuration values.
"""

# UI Constants
MAX_CHAT_LINES = 500  # Maximum lines to keep in chat tabs
WINDOW_OPACITY_DEFAULT = 0.85
WINDOW_RESIZE_MARGIN = 8
WINDOW_DEFAULT_WIDTH = 600
WINDOW_DEFAULT_HEIGHT = 280

# File Reading Constants
DEFAULT_CHECK_INTERVAL = 2  # seconds between file checks
DEFAULT_CHECK_LAST_LINES = 40  # number of lines to check from end of file
MAX_DISPLAYED_LINES = 5000  # Maximum cached displayed lines (deque size)

# Translation Constants
MAX_TRANSLATION_CACHE_SIZE = 1000  # Maximum cached translations
MAX_TRANSLATED_LINES = 1000  # Maximum deque size for translated lines tracking

# Language Support
# Updated to only include the provided set.
SUPPORTED_LANGUAGES = [
    "ar",  # Arabic
    "zh",  # Chinese
    "en",  # English
    "fr",  # French
    "de",  # German
    "hi",  # Hindi
    "it",  # Italian
    "ja",  # Japanese
    "pl",  # Polish
    "pt",  # Portuguese
    "tr",  # Turkish
    "ru",  # Russian
    "es",  # Spanish
]
DEFAULT_TARGET_LANGUAGE = "en"
DEFAULT_SOURCE_LANGUAGE = "en"

# Chat Channels (based on Wakfu chat system)
CHAT_CHANNELS = [
    "Vicinity", "Private", "Game Log", "Fight Log", "Group", "Guild",
    "Trade", "Politics", "PvP Area", "ANKAMA Discussion",
    "Community (FR)", "Community (EN)", "Community (ES)", "Community (PT)",
    "Politics (EN)", "Recruitment (EN)", "Recruitment (ES)", "Recruitment (FR)"
]

# Channels to exclude from General tab and translation
EXCLUDED_CHANNELS = ["Fight Log", "Game Log"]

# Player Tracking
TRACKED_PLAYERS_FILE = "tracked_players.json"
DEFAULT_PLAYER_LANGUAGE = "en"

# Thread Constants
THREAD_SHUTDOWN_TIMEOUT = 2  # seconds to wait for thread shutdown
MESSAGE_QUEUE_TIMEOUT = 1  # seconds to wait for queue.get()

# Model Installation
MODEL_INSTALL_TIMEOUT = 30  # seconds to wait for model download/install
