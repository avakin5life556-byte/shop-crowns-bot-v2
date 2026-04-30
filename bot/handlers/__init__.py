from bot.start import register_start_handlers
from bot.admin import register_admin_handlers
from bot.free_orders import register_free_orders_handlers
from bot.paid_orders import register_paid_orders_handlers
from bot.mods import register_mods_handlers
from bot.support import register_support_handlers
from bot.complaints import register_complaints_handlers
from bot.chat import register_chat_handlers
from bot.rating import register_rating_handlers
from bot.language import register_language_handlers
from bot.broadcast import register_broadcast_handlers
from bot.admin_ban import register_ban_handlers
from bot.settings import register_settings_handlers

__all__ = [
    'register_start_handlers',
    'register_admin_handlers',
    'register_free_orders_handlers',
    'register_paid_orders_handlers',
    'register_mods_handlers',
    'register_support_handlers',
    'register_complaints_handlers',
    'register_chat_handlers',
    'register_rating_handlers',
    'register_language_handlers',
    'register_broadcast_handlers',
    'register_ban_handlers',
    'register_settings_handlers'
]
