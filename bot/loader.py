import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

from bot.config import BOT_TOKEN

logger = logging.getLogger(__name__)

# تهيئة البوت
bot = Bot(
    token=BOT_TOKEN,
    parse_mode=ParseMode.MARKDOWN,
    protect_content=False
)

# FSM Storage
storage = MemoryStorage()

# Dispatcher
dp = Dispatcher(storage=storage)

logger.info("✅ Bot and Dispatcher initialized successfully")
