import asyncio
import logging
import sys
import signal

# Import from local modules (relative to project root)
from loader import bot, dp
from bot.database import db
from handlers import (
    register_start_handlers,
    register_admin_handlers,
    register_free_orders_handlers,
    register_paid_orders_handlers,
    register_mods_handlers,
    register_support_handlers,
    register_complaints_handlers,
    register_chat_handlers,
    register_rating_handlers,
    register_language_handlers,
    register_broadcast_handlers,
    register_ban_handlers,
    register_settings_handlers
)
from utils.middleware import RateLimitMiddleware, AntiFloodMiddleware
from utils.session_manager import session_manager
from handlers.chat import check_timeouts_periodically
from config import ADMIN_ID, LOG_LEVEL, LOG_FORMAT

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

# Register middleware
dp.message.middleware(RateLimitMiddleware())
dp.callback_query.middleware(RateLimitMiddleware())
dp.message.middleware(AntiFloodMiddleware())

# Register all handlers
register_start_handlers(dp)
register_admin_handlers(dp)
register_ban_handlers(dp)
register_free_orders_handlers(dp)
register_paid_orders_handlers(dp)
register_mods_handlers(dp)
register_support_handlers(dp)
register_complaints_handlers(dp)
register_chat_handlers(dp)
register_rating_handlers(dp)
register_language_handlers(dp)
register_broadcast_handlers(dp)
register_settings_handlers(dp)

logger.info("All handlers registered successfully")


# ========== Startup Event ==========
async def on_startup():
    """Called when bot starts"""
    logger.info("🚀 Shop Crowns Bot started")
    await bot.send_message(ADMIN_ID, "✅ البوت شغال بكفاءة عالية")
    
    # Start timeout checker background task
    asyncio.create_task(check_timeouts_periodically())
    logger.info("🕐 Timeout checker started")
    
    # Start session cleanup task
    asyncio.create_task(session_manager.start_cleanup_task())
    logger.info("🧹 Session cleanup task started")
    
    # Verify database connection
    try:
        db.update_last_active(ADMIN_ID)
        logger.info("✅ Database connected")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")


# ========== Shutdown Event ==========
async def on_shutdown():
    """Called when bot shuts down"""
    logger.info("🛑 Bot shutting down")
    
    # Close database connection
    db.close()
    logger.info("✅ Database closed")
    
    # Close bot session
    await bot.session.close()
    logger.info("✅ Bot session closed")


# ========== Signal Handlers for Graceful Shutdown ==========
def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    asyncio.create_task(on_shutdown())
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


# ========== Main Entry Point ==========
async def main():
    """Main function to run the bot"""
    try:
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        await dp.start_polling(bot, skip_updates=True)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        await on_shutdown()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
