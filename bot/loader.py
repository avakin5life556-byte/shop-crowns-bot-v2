from bot.aiogram import Bot, Dispatcher
from bot.aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
