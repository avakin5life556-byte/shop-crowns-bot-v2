import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ParseMode

from bot.config import BOT_TOKEN

# إعداد التسجيل
logger = logging.getLogger(__name__)

# تهيئة البوت مع إعدادات متقدمة
bot = Bot(
    token=BOT_TOKEN,
    parse_mode=ParseMode.MARKDOWN,
    protect_content=False
)

# تهيئة المخزن المؤقت للحالات (FSM)
storage = MemoryStorage()

# تهيئة المدير
dp = Dispatcher(storage=storage)

# تسجيل نجاح التهيئة
logger.info("✅ Bot and Dispatcher initialized successfully")
