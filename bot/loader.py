import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BOT_TOKEN

logger = logging.getLogger(__name__)

# تهيئة البوت
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.MARKDOWN
    )
)

# FSM Storage
storage = MemoryStorage()

# Dispatcher
dp = Dispatcher(storage=storage)

logger.info("✅ Bot and Dispatcher initialized successfully")
