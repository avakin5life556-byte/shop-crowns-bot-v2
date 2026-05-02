import re
import json
import time
from collections import defaultdict
from typing import Optional, Dict, Any, List, Tuple

# تخزين مؤقت لمحاولات الـ Rate Limit مع تنظيف تلقائي
_rate_limit_storage: Dict[str, List[float]] = defaultdict(list)
_RATE_LIMIT_CLEANUP_INTERVAL: int = 3600  # تنظيف كل ساعة
_last_cleanup_time: float = time.time()


def _cleanup_old_rate_limits() -> None:
    """تنظيف البيانات القديمة من rate limit storage لتجنب memory leak"""
    global _last_cleanup_time
    now = time.time()
    
    # تنظيف كل ساعة فقط
    if now - _last_cleanup_time < _RATE_LIMIT_CLEANUP_INTERVAL:
        return
    
    expired_threshold = now - 3600  # حذف البيانات الأقدم من ساعة
    keys_to_delete = []
    
    for key, timestamps in _rate_limit_storage.items():
        # تصفية الطوابع الزمنية القديمة
        valid_timestamps = [t for t in timestamps if t > expired_threshold]
        if valid_timestamps:
            _rate_limit_storage[key] = valid_timestamps
        else:
            keys_to_delete.append(key)
    
    # حذف المفاتيح الفارغة
    for key in keys_to_delete:
        del _rate_limit_storage[key]
    
    _last_cleanup_time = now


def is_rate_limited(user_id: int, action: str, limit: int = 5, window: int = 60) -> bool:
    """
    التحقق من معدل الطلبات لمنع السبام
    
    Args:
        user_id: معرف المستخدم
        action: نوع الإجراء
        limit: الحد الأقصى لعدد المحاولات
        window: النافذة الزمنية بالثواني
    
    Returns:
        True إذا كان المستخدم تجاوز الحد، False إذا كان مسموح
    """
    try:
        # تنظيف دوري
        _cleanup_old_rate_limits()
        
        # validation للمعلمات
        if limit <= 0:
            limit = 5
        if window <= 0:
            window = 60
        
        key: str = f"{user_id}:{action}"
        now: float = time.time()
        
        # تنظيف الطوابع الزمنية القديمة
        _rate_limit_storage[key] = [
            t for t in _rate_limit_storage.get(key, []) 
            if now - t < window
        ]
        
        # التحقق من الحد
        if len(_rate_limit_storage[key]) >= limit:
            return True
        
        # إضافة الطابع الجديد
        _rate_limit_storage[key].append(now)
        return False
        
    except Exception:
        # في حالة حدوث أي خطأ، نسمح بالطلب (fail open)
        return False


def sanitize_input(text: Optional[str], max_length: int = 500, allow_newlines: bool = False) -> str:
    """
    تنظيم وتأمين المدخلات النصية
    
    Args:
        text: النص المراد تنظيفه
        max_length: الحد الأقصى لطول النص
        allow_newlines: السماح بأسطر جديدة
    
    Returns:
        النص المنظف
    """
    if not text or not isinstance(text, str):
        return ""
    
    # validation للـ max_length
    if max_length <= 0:
        max_length = 500
    
    # إزالة HTML/XML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # إزالة الأحرف الخطرة
    text = re.sub(r'[<>{}()\[\]\\;`]', '', text)
    
    # معالجة الأسطر الجديدة
    if not allow_newlines:
        text = text.replace('\n', ' ').replace('\r', ' ')
    
    # إزالة المسافات الزائدة وتحديد الطول
    text = ' '.join(text.split())
    
    if len(text) > max_length:
        text = text[:max_length]
        # محاولة القص عند أخر مسافة
        last_space = text.rfind(' ')
        if last_space > max_length // 2:
            text = text[:last_space]
    
    return text.strip()


def validate_email(email: Optional[str]) -> bool:
    """
    التحقق من صحة البريد الإلكتروني
    
    Args:
        email: البريد الإلكتروني للمستخدم
    
    Returns:
        True إذا كان البريد صالحاً، False إذا لم يكن كذلك
    """
    if not email or not isinstance(email, str):
        return False
    
    email = email.strip().lower()
    
    # التحقق من الطول
    if len(email) < 5 or len(email) > 254:
        return False
    
    # نمط البريد الإلكتروني (RFC 5322 مبسط)
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False
    
    # التحقق من وجود نقاط متتالية
    if '..' in email.split('@')[0]:
        return False
    
    # التحقق من الأجزاء
    local_part, domain_part = email.split('@')
    
    if len(local_part) > 64:
        return False
    
    if len(domain_part) > 255:
        return False
    
    return True


def safe_json_dumps(data: Dict[str, Any], default_value: str = "{}") -> str:
    """
    تحويل قاموس إلى JSON بشكل آمن
    
    Args:
        data: القاموس المراد تحويله
        default_value: القيمة الافتراضية في حالة الخطأ
    
    Returns:
        نص JSON أو القيمة الافتراضية
    """
    if not isinstance(data, dict):
        return default_value
    
    try:
        return json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    except (TypeError, ValueError, OverflowError) as e:
        # تسجيل الخطأ يمكن إضافته هنا لو مطلوب
        return default_value
    except Exception:
        return default_value


def safe_json_loads(data: Optional[str], default_value: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    تحويل JSON إلى قاموس بشكل آمن
    
    Args:
        data: نص JSON المراد تحويله
        default_value: القيمة الافتراضية في حالة الخطأ
    
    Returns:
        قاموس أو القيمة الافتراضية
    """
    if default_value is None:
        default_value = {}
    
    if not data or not isinstance(data, str):
        return default_value
    
    try:
        parsed = json.loads(data)
        if isinstance(parsed, dict):
            return parsed
        return default_value
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        # تسجيل الخطأ يمكن إضافته هنا لو مطلوب
        return default_value
    except Exception:
        return default_value


def clear_rate_limit_for_user(user_id: int, action: Optional[str] = None) -> int:
    """
    مسح بيانات rate limit لمستخدم معين
    
    Args:
        user_id: معرف المستخدم
        action: نوع الإجراء (إذا كان None، يتم مسح كل الإجراءات)
    
    Returns:
        عدد المفاتيح التي تم مسحها
    """
    try:
        cleared_count = 0
        keys_to_delete = []
        
        for key in _rate_limit_storage.keys():
            if key.startswith(f"{user_id}:"):
                if action is None or key == f"{user_id}:{action}":
                    keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del _rate_limit_storage[key]
            cleared_count += 1
        
        return cleared_count
    except Exception:
        return 0


def get_rate_limit_info(user_id: int, action: str, window: int = 60) -> Tuple[int, int]:
    """
    الحصول على معلومات حول حالة rate limit للمستخدم
    
    Args:
        user_id: معرف المستخدم
        action: نوع الإجراء
        window: النافذة الزمنية بالثواني
    
    Returns:
        tuple (عدد المحاولات المتبقية, الوقت المتبقي بالثواني)
    """
    try:
        key: str = f"{user_id}:{action}"
        now: float = time.time()
        
        # تنظيف الطوابع الزمنية القديمة
        recent_attempts = [
            t for t in _rate_limit_storage.get(key, [])
            if now - t < window
        ]
        
        remaining_attempts = max(0, 5 - len(recent_attempts))
        wait_time = 0
        
        if recent_attempts:
            oldest = min(recent_attempts)
            wait_time = max(0, int(window - (now - oldest)))
        
        return remaining_attempts, wait_time
    except Exception:
        return 5, 0
