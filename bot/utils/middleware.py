from typing import Callable, Dict, Any, Awaitable, Optional
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import time
import asyncio
from bot.database.db import db
from bot.utils.helpers import is_rate_limited

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """
    Middleware للتحكم في معدل الطلبات ومنع السبام
    
    يقوم بتحديد عدد الرسائل المسموحة لكل مستخدم في نافذة زمنية محددة
    """
    
    def __init__(self, limit: int = 30, window: int = 60, block_duration: int = 30):
        """
        Args:
            limit: الحد الأقصى لعدد الرسائل المسموحة
            window: النافذة الزمنية بالثواني
            block_duration: مدة الحظر المؤقت بعد تجاوز الحد (بالثواني)
        """
        self.limit = limit
        self.window = window
        self.block_duration = block_duration
        self.blocked_users: Dict[int, float] = {}  # user_id -> وقت انتهاء الحظر
        self._cleanup_lock = asyncio.Lock()
        
    async def _cleanup_blocked_users(self) -> None:
        """تنظيف المستخدمين المحظورين الذين انتهت مدتهم"""
        async with self._cleanup_lock:
            now = time.time()
            expired_users = [
                user_id for user_id, block_until in self.blocked_users.items()
                if block_until <= now
            ]
            for user_id in expired_users:
                del self.blocked_users[user_id]
                logger.debug(f"Rate limit block expired for user {user_id}")
    
    async def _is_user_blocked(self, user_id: int) -> bool:
        """التحقق من أن المستخدم محظور مؤقتاً"""
        await self._cleanup_blocked_users()
        
        if user_id in self.blocked_users:
            block_until = self.blocked_users[user_id]
            if time.time() < block_until:
                remaining = int(block_until - time.time())
                return True, remaining
            else:
                del self.blocked_users[user_id]
        return False, 0
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # معالجة الرسائل فقط
        if not isinstance(event, Message):
            return await handler(event, data)
        
        user_id = event.from_user.id
        
        # التحقق من الحظر المؤقت
        is_blocked, remaining = await self._is_user_blocked(user_id)
        if is_blocked:
            logger.warning(f"Rate limit: User {user_id} is temporarily blocked for {remaining}s")
            
            # إرسال رسالة للمستخدم
            try:
                lang = db.get_user_language(user_id)
                message_text = (
                    f"⚠️ **تم تجاوز حد الرسائل المسموحة**\n\n"
                    f"يرجى الانتظار {remaining} ثانية قبل إرسال رسائل جديدة."
                    if lang == 'ar' else
                    f"⚠️ **Rate limit exceeded**\n\n"
                    f"Please wait {remaining} seconds before sending new messages."
                )
                await event.answer(message_text, parse_mode='Markdown')
            except Exception as e:
                logger.error(f"Failed to send rate limit message to user {user_id}: {e}")
            
            # منع معالجة الرسالة
            return
        
        # التحقق من معدل الطلبات
        try:
            key = f"global_rate_{user_id}"
            is_limited = is_rate_limited(user_id, key, limit=self.limit, window=self.window)
            
            if is_limited:
                # حظر المستخدم مؤقتاً
                self.blocked_users[user_id] = time.time() + self.block_duration
                logger.warning(f"Rate limit exceeded for user {user_id}, blocked for {self.block_duration}s")
                
                # إرسال رسالة للمستخدم
                try:
                    lang = db.get_user_language(user_id)
                    message_text = (
                        f"⚠️ **لقد تجاوزت حد الرسائل المسموحة**\n\n"
                        f"الحد الأقصى: {self.limit} رسالة لكل {self.window} ثانية.\n"
                        f"يرجى الانتظار {self.block_duration} ثانية قبل المحاولة مرة أخرى."
                        if lang == 'ar' else
                        f"⚠️ **You have exceeded the message limit**\n\n"
                        f"Maximum: {self.limit} messages per {self.window} seconds.\n"
                        f"Please wait {self.block_duration} seconds before trying again."
                    )
                    await event.answer(message_text, parse_mode='Markdown')
                except Exception as e:
                    logger.error(f"Failed to send rate limit message to user {user_id}: {e}")
                
                # منع معالجة الرسالة
                return
            
            # تحديث آخر نشاط للمستخدم بشكل غير متزامن
            try:
                db.update_last_active(user_id)
            except Exception as e:
                logger.error(f"Failed to update last_active for user {user_id}: {e}")
                
        except Exception as e:
            logger.error(f"Error in RateLimitMiddleware for user {user_id}: {e}")
            # في حالة الخطأ، نسمح بمرور الرسالة (fail open)
        
        # معالجة الرسالة بشكل طبيعي
        return await handler(event, data)


class AntiFloodMiddleware(BaseMiddleware):
    """
    Middleware لمنع الفيض (flooding) من نفس المستخدم
    يحد من سرعة إرسال الرسائل المتتالية
    """
    
    def __init__(self, limit: float = 0.5, max_history: int = 1000):
        """
        Args:
            limit: الحد الأدنى للفاصل الزمني بين الرسائل (بالثواني)
            max_history: الحد الأقصى لعدد المستخدمين المخزنين في الذاكرة
        """
        self.limit = limit
        self.max_history = max_history
        self.last_time: Dict[int, float] = {}
        self._cleanup_counter = 0
        self._cleanup_threshold = 100  # تنظيف كل 100 مستخدم جديد
        
    def _cleanup_old_entries(self) -> None:
        """تنظيف الإدخالات القديمة لتجنب استهلاك ذاكرة كبير"""
        self._cleanup_counter += 1
        
        # تنظيف دوري
        if self._cleanup_counter >= self._cleanup_threshold:
            self._cleanup_counter = 0
            
            # تحديد المستخدمين غير النشطين (أكثر من ساعة)
            now = time.time()
            inactive_threshold = now - 3600  # ساعة
            
            inactive_users = [
                user_id for user_id, last_time in self.last_time.items()
                if last_time < inactive_threshold
            ]
            
            # حذف المستخدمين غير النشطين
            for user_id in inactive_users:
                del self.last_time[user_id]
            
            # إذا كان العدد لا يزال كبيراً، نحذف أقدم الإدخالات
            if len(self.last_time) > self.max_history:
                sorted_users = sorted(self.last_time.items(), key=lambda x: x[1])
                users_to_remove = len(self.last_time) - self.max_history
                for i in range(users_to_remove):
                    if i < len(sorted_users):
                        del self.last_time[sorted_users[i][0]]
            
            logger.debug(f"AntiFlood cleanup: removed {len(inactive_users)} inactive users, "
                        f"current size: {len(self.last_time)}")
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # معالجة الرسائل فقط
        if not isinstance(event, Message):
            return await handler(event, data)
        
        user_id = event.from_user.id
        now = time.time()
        
        try:
            # التحقق من الفاصل الزمني
            if user_id in self.last_time:
                elapsed = now - self.last_time[user_id]
                
                if elapsed < self.limit:
                    wait_time = self.limit - elapsed
                    logger.debug(f"Anti-flood: User {user_id} is sending too fast, wait {wait_time:.2f}s")
                    
                    # لا نمنع الرسالة، فقط نمررها مع تسجيل التحذير
                    # هذا يمنع التأثير السلبي على تجربة المستخدم
                    pass
            
            # تحديث آخر وقت
            self.last_time[user_id] = now
            
            # تنظيف الإدخالات القديمة
            self._cleanup_old_entries()
            
        except Exception as e:
            logger.error(f"Error in AntiFloodMiddleware for user {user_id}: {e}")
        
        return await handler(event, data)
    
    def get_user_wait_time(self, user_id: int) -> float:
        """الحصول على وقت الانتظار المتبقي للمستخدم"""
        if user_id in self.last_time:
            elapsed = time.time() - self.last_time[user_id]
            if elapsed < self.limit:
                return self.limit - elapsed
        return 0.0


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware لتسجيل جميع الأحداث في البوت
    مفيد للمراقبة والتصحيح (Debugging)
    """
    
    def __init__(self, log_requests: bool = True, log_callbacks: bool = True):
        self.log_requests = log_requests
        self.log_callbacks = log_callbacks
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # تسجيل الأحداث حسب النوع
        if isinstance(event, Message) and self.log_requests:
            user_id = event.from_user.id
            user_name = event.from_user.full_name or "Unknown"
            text = event.text or "[non-text message]"
            
            # اختصار النص الطويل
            if len(text) > 100:
                text = text[:100] + "..."
            
            logger.info(f"📨 Message from {user_name} (ID: {user_id}): {text}")
            
        elif isinstance(event, CallbackQuery) and self.log_callbacks:
            user_id = event.from_user.id
            callback_data = event.data or "[no data]"
            logger.info(f"🔘 Callback from {user_id}: {callback_data}")
        
        try:
            result = await handler(event, data)
            return result
        except Exception as e:
            # تسجيل الأخطاء في الكود
            if isinstance(event, Message):
                user_id = event.from_user.id
                logger.error(f"Error in handler for user {user_id}: {e}", exc_info=True)
            else:
                logger.error(f"Error in handler: {e}", exc_info=True)
            raise  # إعادة رفع الخطأ للمعالجة الطبيعية
