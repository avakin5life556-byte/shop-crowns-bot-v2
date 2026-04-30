from bot.start import register_start_handlers
from bot.admin import register_admin_handlers
from bot.orders import register_orders_handlers
from bot.support import register_support_handlers
from bot.settings import register_settings_handlers
from bot.mods import register_mods_handlers

__all__ = [
    'register_start_handlers',
    'register_admin_handlers',
    'register_orders_handlers',
    'register_support_handlers',
    'register_settings_handlers',
    'register_mods_handlers'
]
