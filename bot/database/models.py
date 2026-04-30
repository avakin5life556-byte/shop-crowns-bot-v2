from bot.dataclasses import dataclass
from bot.datetime import datetime
from bot.typing import Optional

@dataclass
class User:
    user_id: int
    full_name: str
    username: Optional[str]
    language: str = 'ar'
    country: str = 'مصر'
    is_banned: bool = False
    registered_at: str = None
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'full_name': self.full_name,
            'username': self.username,
            'language': self.language,
            'country': self.country,
            'is_banned': self.is_banned,
            'registered_at': self.registered_at
        }


@dataclass
class Order:
    order_number: str
    user_id: int
    order_type: str
    order_data: str
    status: str = 'pending'
    created_at: str = None
    updated_at: str = None


@dataclass
class Ticket:
    ticket_number: str
    user_id: int
    ticket_type: str
    status: str = 'open'
    created_at: str = None
    closed_at: str = None
    assigned_admin: Optional[int] = None
