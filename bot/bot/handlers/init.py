from .start import register_start_handlers
from .admin import register_admin_handlers
from .orders import register_orders_handlers
from .support import register_support_handlers
from .settings import register_settings_handlers
from .mods import register_mods_handlers

__all__ = [
    'register_start_handlers',
    'register_admin_handlers',
    'register_orders_handlers',
    'register_support_handlers',
    'register_settings_handlers',
    'register_mods_handlers'
]
