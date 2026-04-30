import re
import json
from collections import defaultdict
import time

_rate_limit_storage = defaultdict(list)


def is_rate_limited(user_id: int, action: str, limit: int = 5, window: int = 60) -> bool:
    key = f"{user_id}:{action}"
    now = time.time()
    _rate_limit_storage[key] = [t for t in _rate_limit_storage[key] if now - t < window]
    
    if len(_rate_limit_storage[key]) >= limit:
        return True
    
    _rate_limit_storage[key].append(now)
    return False


def sanitize_input(text: str, max_length: int = 500) -> str:
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[<>{}()\[\]\\;`]', '', text)
    if len(text) > max_length:
        text = text[:max_length]
    return text.strip()


def validate_email(email: str) -> bool:
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def safe_json_dumps(data: dict) -> str:
    try:
        return json.dumps(data, ensure_ascii=False)
    except:
        return "{}"


def safe_json_loads(data: str) -> dict:
    try:
        return json.loads(data)
    except:
        return {}