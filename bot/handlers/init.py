from bot.handlers.start import register_start_handlers
from bot.handlers.admin import register_admin_handlers
from bot.handlers.free_orders import register_free_orders_handlers
from bot.handlers.paid_orders import register_paid_orders_handlers
from bot.handlers.complaints import register_complaints_handlers
from bot.handlers.chat import register_chat_handlers
from bot.handlers.rating import register_rating_handlers
from bot.handlers.language import register_language_handlers
from bot.handlers.broadcast import register_broadcast_handlers
from bot.handlers.admin_ban import register_ban_handlers
from bot.handlers.settings import register_settings_handlers
from bot.handlers.mods import register_mods_handlers

__all__ = [
    'register_start_handlers',
    'register_admin_handlers',
    'register_free_orders_handlers',
    'register_paid_orders_handlers',
    'register_complaints_handlers',
    'register_chat_handlers',
    'register_rating_handlers',
    'register_language_handlers',
    'register_broadcast_handlers',
    'register_ban_handlers',
    'register_settings_handlers',
    'register_mods_handlers'
]
