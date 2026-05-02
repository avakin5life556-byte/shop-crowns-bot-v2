import logging

logger = logging.getLogger(__name__)

# تسجيل جميع الـ handlers بشكل آمن مع try/except
try:
    from .start import register_start_handlers
except Exception as e:
    logger.error(f"Failed to import start handlers: {e}")
    register_start_handlers = None

try:
    from .admin import register_admin_handlers
except Exception as e:
    logger.error(f"Failed to import admin handlers: {e}")
    register_admin_handlers = None

try:
    from .free_orders import register_free_orders_handlers
except Exception as e:
    logger.error(f"Failed to import free_orders handlers: {e}")
    register_free_orders_handlers = None

try:
    from .paid_orders import register_paid_orders_handlers
except Exception as e:
    logger.error(f"Failed to import paid_orders handlers: {e}")
    register_paid_orders_handlers = None

try:
    from .mods import register_mods_handlers
except Exception as e:
    logger.error(f"Failed to import mods handlers: {e}")
    register_mods_handlers = None

try:
    from .support import register_support_handlers
except Exception as e:
    logger.error(f"Failed to import support handlers: {e}")
    register_support_handlers = None

try:
    from .complaints import register_complaints_handlers
except Exception as e:
    logger.error(f"Failed to import complaints handlers: {e}")
    register_complaints_handlers = None

try:
    from .chat import register_chat_handlers
except Exception as e:
    logger.error(f"Failed to import chat handlers: {e}")
    register_chat_handlers = None

try:
    from .rating import register_rating_handlers
except Exception as e:
    logger.error(f"Failed to import rating handlers: {e}")
    register_rating_handlers = None

try:
    from .language import register_language_handlers
except Exception as e:
    logger.error(f"Failed to import language handlers: {e}")
    register_language_handlers = None

try:
    from .broadcast import register_broadcast_handlers
except Exception as e:
    logger.error(f"Failed to import broadcast handlers: {e}")
    register_broadcast_handlers = None

try:
    from .admin_ban import register_ban_handlers
except Exception as e:
    logger.error(f"Failed to import admin_ban handlers: {e}")
    register_ban_handlers = None

try:
    from .settings import register_settings_handlers
except Exception as e:
    logger.error(f"Failed to import settings handlers: {e}")
    register_settings_handlers = None

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
