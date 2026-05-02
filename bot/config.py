import os
from dotenv import load_dotenv
import pytz
from typing import List, Dict, Optional

# تحميل متغيرات البيئة
load_dotenv()


def get_env_int(key: str, default: int, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
    """الحصول على قيمة عددية من متغيرات البيئة بشكل آمن"""
    try:
        value = int(os.getenv(key, str(default)))
        if min_val is not None and value < min_val:
            value = default
        if max_val is not None and value > max_val:
            value = default
        return value
    except (ValueError, TypeError):
        return default


def get_env_str(key: str, default: str = "") -> str:
    """الحصول على قيمة نصية من متغيرات البيئة بشكل آمن"""
    value = os.getenv(key, default)
    return value if value is not None else default


def get_env_bool(key: str, default: bool = False) -> bool:
    """الحصول على قيمة منطقية من متغيرات البيئة بشكل آمن"""
    value = os.getenv(key)
    if value is None:
        return default
    return value.lower() in ('true', '1', 'yes', 'on')


# ========== Bot Configuration ==========

BOT_TOKEN = get_env_str("BOT_TOKEN")

# تشخيص وتحسين رسالة الخطأ
if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN is missing! Please set it in .env file or Railway environment variables.")
    raise ValueError("BOT_TOKEN is required but not provided. Cannot start the bot.")

# تشخيص إضافي لطوله
if len(BOT_TOKEN) < 40:
    print(f"⚠️ WARNING: BOT_TOKEN seems invalid (length: {len(BOT_TOKEN)}). Expected at least 40 characters.")

print(f"✅ BOT_TOKEN loaded successfully (length: {len(BOT_TOKEN)})")

ADMIN_ID = get_env_int("ADMIN_ID", 1452361376, min_val=1)

# ========== Timezone ==========

TIMEZONE_STR = get_env_str("TIMEZONE", "Africa/Cairo")

try:
    TIMEZONE = pytz.timezone(TIMEZONE_STR)
except pytz.exceptions.UnknownTimeZoneError:
    print(f"⚠️ WARNING: Unknown timezone '{TIMEZONE_STR}', falling back to 'Africa/Cairo'")
    TIMEZONE = pytz.timezone("Africa/Cairo")
    TIMEZONE_STR = "Africa/Cairo"

# ========== Mod Links ==========

MOD_LINKS: Dict[str, str] = {
    'sky': get_env_str("MOD_LINK_SKY", "https://www.mediafire.com/file/h69gc4ai6zvtc2r/Sky_Ava.apk/file"),
    'bull': get_env_str("MOD_LINK_BULL", "https://swiftlnx.com/BqN5PFs"),
    'bull_alt': get_env_str("MOD_LINK_BULL_ALT", "https://swiftlnx.com/N3ea3s"),
    'gold': get_env_str("MOD_LINK_GOLD", "https://www.mediafire.com/file/1vz806m0yrfafh5/Gold+Vip.apk/file")
}

# ========== Timeout Settings ==========

ORDER_TIMEOUT_MINUTES = get_env_int("ORDER_TIMEOUT_MINUTES", 20, min_val=1, max_val=120)
CHAT_TIMEOUT_MINUTES = get_env_int("CHAT_TIMEOUT_MINUTES", 20, min_val=1, max_val=60)
QUEUE_CHECK_INTERVAL = get_env_int("QUEUE_CHECK_INTERVAL", 60, min_val=10, max_val=300)

# ========== Database ==========

DATABASE_PATH = get_env_str("DATABASE_PATH", "shop_crowns.db")

# ========== Logging ==========

LOG_LEVEL = get_env_str("LOG_LEVEL", "INFO")
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# ========== Language Settings ==========

DEFAULT_LANGUAGE = get_env_str("DEFAULT_LANGUAGE", "ar")
SUPPORTED_LANGUAGES: List[str] = ['ar', 'en']

# ========== Rate Limit Settings ==========

RATE_LIMIT_GLOBAL = get_env_int("RATE_LIMIT_GLOBAL", 30, min_val=5, max_val=100)
RATE_LIMIT_WINDOW = get_env_int("RATE_LIMIT_WINDOW", 60, min_val=10, max_val=300)
RATE_LIMIT_ORDERS = get_env_int("RATE_LIMIT_ORDERS", 5, min_val=1, max_val=20)

# ========== Broadcast Settings ==========

BROADCAST_SLEEP_INTERVAL = get_env_int("BROADCAST_SLEEP_INTERVAL", 1, min_val=1, max_val=5)

# ========== Payment Settings (اختياري) ==========

PAYMENT_PROVIDER_TOKEN = get_env_str("PAYMENT_PROVIDER_TOKEN", "")

# ========== Webhook Settings (للاستخدام مع Railway) ==========

USE_WEBHOOK = get_env_bool("USE_WEBHOOK", False)
WEBHOOK_URL = get_env_str("WEBHOOK_URL", "")
WEBHOOK_PATH = get_env_str("WEBHOOK_PATH", "/webhook")

# ========== Security Settings ==========

MAX_MESSAGE_LENGTH = get_env_int("MAX_MESSAGE_LENGTH", 4096, min_val=100, max_val=4096)
MAX_CAPTCHA_ATTEMPTS = get_env_int("MAX_CAPTCHA_ATTEMPTS", 3, min_val=1, max_val=5)

# ========== Admin Notifications ==========

NOTIFY_ADMIN_ON_STARTUP = get_env_bool("NOTIFY_ADMIN_ON_STARTUP", True)
NOTIFY_ADMIN_ON_NEW_USER = get_env_bool("NOTIFY_ADMIN_ON_NEW_USER", True)

# ========== Cleanup Settings ==========

SESSION_CLEANUP_INTERVAL = get_env_int("SESSION_CLEANUP_INTERVAL", 3600, min_val=300, max_val=86400)
SESSION_TTL = get_env_int("SESSION_TTL", 1800, min_val=300, max_val=7200)


def validate_config() -> bool:
    """التحقق من صحة الإعدادات"""
    errors = []
    
    if not BOT_TOKEN:
        errors.append("BOT_TOKEN is missing")
    
    if len(BOT_TOKEN) < 40:
        errors.append("BOT_TOKEN seems invalid (too short)")
    
    if ADMIN_ID <= 0:
        errors.append("ADMIN_ID must be a positive integer")
    
    if DEFAULT_LANGUAGE not in SUPPORTED_LANGUAGES:
        errors.append(f"DEFAULT_LANGUAGE '{DEFAULT_LANGUAGE}' not in {SUPPORTED_LANGUAGES}")
    
    if errors:
        for error in errors:
            print(f"❌ Config Error: {error}")
        return False
    
    return True


def print_config_summary() -> None:
    """طباعة ملخص الإعدادات (للتأكيد)"""
    print("=" * 50)
    print("📋 Bot Configuration Summary")
    print("=" * 50)
    print(f"🤖 Bot Token: {'✅ Set' if BOT_TOKEN else '❌ Missing'}")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print(f"🌍 Timezone: {TIMEZONE_STR}")
    print(f"🗣️ Default Language: {DEFAULT_LANGUAGE}")
    print(f"⏱️ Order Timeout: {ORDER_TIMEOUT_MINUTES} minutes")
    print(f"⏱️ Chat Timeout: {CHAT_TIMEOUT_MINUTES} minutes")
    print(f"📁 Database: {DATABASE_PATH}")
    print(f"📊 Log Level: {LOG_LEVEL}")
    print(f"🔄 Webhook: {'Enabled' if USE_WEBHOOK else 'Disabled (Polling)'}")
    print("=" * 50)


# تنفيذ التحقق من الإعدادات عند التحميل
if not validate_config():
    print("⚠️ WARNING: Configuration has issues. Bot may not work correctly.")

# عند التشغيل كـ main (اختياري للتحقق)
if __name__ == "__main__":
    print_config_summary()
