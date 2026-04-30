from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from bot.database import db
from bot.utils.helpers import is_rate_limited
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message):
            user_id = event.from_user.id
            if is_rate_limited(user_id, 'global', limit=30, window=60):
                await event.answer("⚠️ أرسلت رسائل كثيرة، انتظر قليلاً")
                return
            db.update_last_active(user_id)
        
        return await handler(event, data)
