print("🔥 BOT IS RUNNING NOW")
import asyncio
import logging
import sys
import signal
from typing import Optional

from bot.loader import bot, dp
from bot.database.db import db
from bot.handlers import (
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
from bot.utils.middleware import RateLimitMiddleware, AntiFloodMiddleware, LoggingMiddleware
from bot.utils.session_manager import session_manager
from bot.handlers.chat import check_timeouts_periodically
from bot.config import ADMIN_ID, LOG_LEVEL, LOG_FORMAT

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        
    ]
)
logger = logging.getLogger(__name__)

# متغير لتتبع حالة الإغلاق
_shutting_down: bool = False
_shutdown_tasks: list = []


# ✅ Register middleware (لن تمنع وصول الأمر /start)
dp.message.middleware(RateLimitMiddleware())
dp.callback_query.middleware(RateLimitMiddleware())
dp.message.middleware(AntiFloodMiddleware())
# dp.message.middleware(LoggingMiddleware())  # اختياري - يمكن تفعيله للتصحيح

# ✅ Register all handlers
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

logger.info("✅ All handlers registered successfully")


# ========== Background Tasks Management ==========

_background_tasks: list = []


def create_background_task(coro) -> asyncio.Task:
    """إنشاء مهمة خلفية وتتبعها للإغلاق الآمن"""
    task = asyncio.create_task(coro)
    _background_tasks.append(task)
    task.add_done_callback(_background_tasks.remove)
    return task


async def cancel_all_background_tasks():
    """إلغاء جميع المهام الخلفية بشكل آمن"""
    logger.info(f"Cancelling {len(_background_tasks)} background tasks...")
    for task in _background_tasks:
        if not task.done():
            task.cancel()
    
    if _background_tasks:
        await asyncio.gather(*_background_tasks, return_exceptions=True)
        logger.info("All background tasks cancelled")


# ========== Startup Event ==========
async def on_startup():
    """Called when bot starts"""
    global _shutting_down
    _shutting_down = False
    
    logger.info("🚀 Shop Crowns Bot starting up...")
    
    try:
        # حذف الويب هوك والتحديثات المعلقة
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Webhook deleted, pending updates dropped")
        
        # إرسال إشعار للأدمن
        await bot.send_message(
            ADMIN_ID, 
            "✅ **البوت شغال بكفاءة عالية**\n\n"
            "📊 **المراقبة نشطة**\n"
            "🔒 **الأمان مفعل**\n"
            "⏰ **المهلات تعمل**\n"
            "🚀 جاهز للاستخدام",
            parse_mode='Markdown'
        )
        logger.info("✅ Admin notification sent")
        
    except Exception as e:
        logger.error(f"Failed to send startup notification: {e}")
    
    # بدء المهام الخلفية
    create_background_task(check_timeouts_periodically())
    logger.info("🕐 Timeout checker started")
    
    create_background_task(session_manager.start_cleanup_task())
    logger.info("🧹 Session cleanup task started")
    
    # التحقق من اتصال قاعدة البيانات
    try:
        db.update_last_active(ADMIN_ID)
        db_stats = db.get_stats()
        logger.info(f"✅ Database connected - Active users: {db_stats.get('active', 0)}")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
    
    logger.info("🎉 Bot startup completed successfully")


# ========== Shutdown Event ==========
async def on_shutdown():
    """Called when bot shuts down"""
    global _shutting_down
    
    if _shutting_down:
        logger.info("Shutdown already in progress, skipping...")
        return
    
    _shutting_down = True
    logger.info("🛑 Bot shutting down...")
    
    # إيقاف المهام الخلفية
    await cancel_all_background_tasks()
    
    # إيقاف مدير الجلسات
    try:
        await session_manager.stop_cleanup_task()
        logger.info("✅ Session manager stopped")
    except Exception as e:
        logger.error(f"Error stopping session manager: {e}")
    
    # إغلاق قاعدة البيانات
    try:
        db.close()
        logger.info("✅ Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")
    
    # إغلاق جلسة البوت
    try:
        await bot.session.close()
        logger.info("✅ Bot session closed")
    except Exception as e:
        logger.error(f"Error closing bot session: {e}")
    
    logger.info("✅ Bot shutdown completed successfully")


# ========== Signal Handlers ==========
def signal_handler(signum: int, frame) -> None:
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    
    # إنشاء مهمة للإغلاق المتزامن مع منع تكرار الإشارات
    loop = None
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if loop and loop.is_running():
        # إذا كان الحدث يعمل، نضيف المهمة إلى الحلقة
        asyncio.create_task(graceful_shutdown())
    else:
        # نقوم بالتشغيل المتزامن
        loop.run_until_complete(graceful_shutdown())
        sys.exit(0)


async def graceful_shutdown():
    """إيقاف البوت بشكل متدرج وآمن"""
    try:
        # إيقاف الـ polling أولاً
        await dp.stop_polling()
        logger.info("Polling stopped")
        
        # ثم shutdown
        await on_shutdown()
    except Exception as e:
        logger.error(f"Error during graceful shutdown: {e}")


def setup_signal_handlers():
    """تهيئة معالجات الإشارات للإيقاف الآمن"""
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    # تجاهل SIGPIPE (يحدث أحياناً في Railway)
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)


# ========== Main Entry Point ==========
async def main():
    """Main function to run the bot"""
    # تهيئة معالجات الإشارات
    setup_signal_handlers()
    
    # تسجيل أحداث البداية والنهاية
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    try:
        logger.info("🚀 Starting bot polling...")
        await dp.start_polling(bot, skip_updates=True)
    except KeyboardInterrupt:
        logger.info("⚠️ Bot stopped by user (KeyboardInterrupt)")
    except asyncio.CancelledError:
        logger.info("⚠️ Bot task cancelled")
    except Exception as e:
        logger.error(f"❌ Fatal error in main: {e}", exc_info=True)
        await on_shutdown()
        sys.exit(1)
    finally:
        logger.info("🏁 Bot main loop finished")


def run_main():
    """تشغيل الدالة الرئيسية مع التعامل مع الحلقات المتعددة"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot terminated by user")
        sys.exit(0)
    except RuntimeError as e:
        if "already running" in str(e):
            logger.warning("Event loop already running, creating new loop...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(main())
            finally:
                loop.close()
        else:
            raise
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    run_main()
