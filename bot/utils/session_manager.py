import asyncio
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime

# إعداد logging
logger = logging.getLogger(__name__)


class SessionManager:
    """
    مدير جلسات المستخدمين
    يدير الجلسات المؤقتة في الذاكرة مع نظام انتهاء صلاحية تلقائي
    """
    
    def __init__(self, session_ttl: int = 1800):
        """
        Args:
            session_ttl: مدة صلاحية الجلسة بالثواني (افتراضي 30 دقيقة)
        """
        self.sessions: Dict[int, Dict[str, Any]] = {}
        self.last_activity: Dict[int, float] = {}
        self.session_ttl = session_ttl
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        
    def create_session(self, user_id: int, data: dict = None) -> None:
        """
        إنشاء جلسة جديدة لمستخدم
        
        Args:
            user_id: معرف المستخدم
            data: البيانات الأولية للجلسة
        """
        try:
            now = time.time()
            
            with self._lock:
                self.sessions[user_id] = data.copy() if data else {}
                self.last_activity[user_id] = now
                
            logger.debug(f"Session created for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to create session for user {user_id}: {e}")
    
    def get_session(self, user_id: int) -> Dict[str, Any]:
        """
        الحصول على بيانات الجلسة لمستخدم
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            بيانات الجلسة (قاموس فارغ إذا لم تكن موجودة)
        """
        try:
            # التحقق من وجود الجلسة
            if user_id not in self.sessions:
                return {}
            
            # التحقق من صلاحية الجلسة
            if not self._is_session_valid(user_id):
                self.delete_session(user_id)
                return {}
            
            # تحديث وقت آخر نشاط
            self.last_activity[user_id] = time.time()
            
            # إرجاع نسخة من البيانات لمنع التعديل المباشر
            return self.sessions[user_id].copy()
            
        except Exception as e:
            logger.error(f"Failed to get session for user {user_id}: {e}")
            return {}
    
    def update_session(self, user_id: int, data: dict) -> None:
        """
        تحديث بيانات الجلسة لمستخدم
        
        Args:
            user_id: معرف المستخدم
            data: البيانات الجديدة للتحديث
        """
        try:
            if not data:
                return
            
            # التحقق من وجود الجلسة
            if user_id not in self.sessions:
                self.create_session(user_id, data)
                return
            
            # التحقق من صلاحية الجلسة
            if not self._is_session_valid(user_id):
                self.delete_session(user_id)
                self.create_session(user_id, data)
                return
            
            # تحديث البيانات مع قفل
            with self._lock:
                if user_id in self.sessions:
                    self.sessions[user_id].update(data.copy())
                    self.last_activity[user_id] = time.time()
                    
            logger.debug(f"Session updated for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to update session for user {user_id}: {e}")
    
    def delete_session(self, user_id: int) -> bool:
        """
        حذف جلسة مستخدم
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            True إذا تم الحذف، False إذا لم تكن موجودة
        """
        try:
            with self._lock:
                if user_id in self.sessions:
                    del self.sessions[user_id]
                    self.last_activity.pop(user_id, None)
                    logger.debug(f"Session deleted for user {user_id}")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete session for user {user_id}: {e}")
            return False
    
    def _is_session_valid(self, user_id: int) -> bool:
        """
        التحقق من صلاحية الجلسة
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            True إذا كانت الجلسة صالحة، False إذا انتهت صلاحيتها
        """
        try:
            if user_id not in self.last_activity:
                return False
                
            last_active = self.last_activity[user_id]
            now = time.time()
            
            return (now - last_active) <= self.session_ttl
            
        except Exception as e:
            logger.error(f"Failed to check session validity for user {user_id}: {e}")
            return False
    
    def _cleanup_expired_sessions(self) -> int:
        """
        تنظيف الجلسات المنتهية صلاحيتها
        
        Returns:
            عدد الجلسات التي تم حذفها
        """
        try:
            now = time.time()
            expired_users = []
            
            # تحديد الجلسات المنتهية
            for user_id, last_active in self.last_activity.items():
                if (now - last_active) > self.session_ttl:
                    expired_users.append(user_id)
            
            # حذف الجلسات المنتهية
            with self._lock:
                for user_id in expired_users:
                    self.sessions.pop(user_id, None)
                    self.last_activity.pop(user_id, None)
                    
            if expired_users:
                logger.info(f"Cleaned up {len(expired_users)} expired sessions")
                
            return len(expired_users)
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
            return 0
    
    def get_session_count(self) -> int:
        """
        الحصول على عدد الجلسات النشطة
        
        Returns:
            عدد الجلسات في الذاكرة
        """
        return len(self.sessions)
    
    def get_session_age(self, user_id: int) -> Optional[int]:
        """
        الحصول على عمر الجلسة بالثواني
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            عمر الجلسة بالثواني، أو None إذا لم تكن موجودة
        """
        if user_id in self.last_activity:
            return int(time.time() - self.last_activity[user_id])
        return None
    
    def extend_session(self, user_id: int, extra_time: int = 300) -> bool:
        """
        تمديد صلاحية الجلسة بمدة إضافية
        
        Args:
            user_id: معرف المستخدم
            extra_time: الوقت الإضافي بالثواني
            
        Returns:
            True إذا تم التمديد، False إذا لم تكن الجلسة موجودة
        """
        try:
            if user_id in self.last_activity:
                # لا نمدد أكثر من الحد الأقصى
                current_age = time.time() - self.last_activity[user_id]
                if current_age < self.session_ttl:
                    self.last_activity[user_id] = time.time()
                    logger.debug(f"Session extended for user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to extend session for user {user_id}: {e}")
            return False
    
    async def start_cleanup_task(self) -> None:
        """
        بدء مهمة التنظيف الدورية للجلسات المنتهية
        تعمل في الخلفية وتنظف كل 60 ثانية
        """
        try:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Session cleanup task started")
        except Exception as e:
            logger.error(f"Failed to start cleanup task: {e}")
    
    async def _cleanup_loop(self) -> None:
        """
        حلقة التنظيف الدورية
        """
        while True:
            try:
                await asyncio.sleep(60)  # تنظيف كل دقيقة
                self._cleanup_expired_sessions()
                
            except asyncio.CancelledError:
                logger.info("Session cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60)  # استمرار حتى في حالة الخطأ
    
    async def stop_cleanup_task(self) -> None:
        """
        إيقاف مهمة التنظيف الدورية
        """
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("Session cleanup task stopped")
    
    def clear_all_sessions(self) -> int:
        """
        مسح جميع الجلسات (للصيانة)
        
        Returns:
            عدد الجلسات التي تم مسحها
        """
        try:
            with self._lock:
                count = len(self.sessions)
                self.sessions.clear()
                self.last_activity.clear()
                logger.warning(f"Cleared all {count} sessions")
                return count
        except Exception as e:
            logger.error(f"Failed to clear all sessions: {e}")
            return 0


# instance جاهز للاستخدام
session_manager = SessionManager(session_ttl=1800)  # 30 دقيقة
