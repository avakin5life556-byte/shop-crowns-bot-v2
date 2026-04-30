import os
from dotenv import load_dotenv
import pytz

load_dotenv()

# ========== Bot Configuration ==========

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is required")

ADMIN_ID = int(os.getenv("ADMIN_ID", "1452361376"))

# ========== Timezone ==========

TIMEZONE = pytz.timezone('Africa/Cairo')
TIMEZONE_STR = os.getenv("TIMEZONE", "Africa/Cairo")

# ========== Mod Links ==========

MOD_LINKS = {
    'sky': 'https://www.mediafire.com/file/h69gc4ai6zvtc2r/Sky_Ava.apk/file',
    'bull': 'https://swiftlnx.com/BqN5PFs',
    'bull_alt': 'https://swiftlnx.com/N3ea3s',
    'gold': 'https://www.mediafire.com/file/1vz806m0yrfafh5/Gold+Vip.apk/file'
}

# ========== Timeout Settings ==========

ORDER_TIMEOUT_MINUTES = int(os.getenv("ORDER_TIMEOUT_MINUTES", "20"))
CHAT_TIMEOUT_MINUTES = int(os.getenv("CHAT_TIMEOUT_MINUTES", "20"))
QUEUE_CHECK_INTERVAL = int(os.getenv("QUEUE_CHECK_INTERVAL", "60"))

# ========== Database ==========

DATABASE_PATH = os.getenv("DATABASE_PATH", "shop_crowns.db")

# ========== Logging ==========

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# ========== Language Settings ==========

DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "ar")
SUPPORTED_LANGUAGES = ['ar', 'en']
