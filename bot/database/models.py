from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class User:
    user_id: int
    full_name: str
    username: Optional[str]
    language: str = 'ar'
    country: str = 'مصر'
    is_banned: bool = False
    registered_at: Optional[str] = None
    last_active: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert User to dictionary with proper types for database"""
        return {
            'user_id': self.user_id,
            'full_name': self.full_name,
            'username': self.username,
            'language': self.language,
            'country': self.country,
            'is_banned': int(self.is_banned),  # تحويل bool إلى int لتوافق SQLite
            'registered_at': self.registered_at,
            'last_active': self.last_active
        }


@dataclass
class Order:
    order_number: str
    user_id: int
    order_type: str
    order_data: str
    status: str = 'pending'
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert Order to dictionary"""
        return {
            'order_number': self.order_number,
            'user_id': self.user_id,
            'order_type': self.order_type,
            'order_data': self.order_data,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


@dataclass
class Ticket:
    ticket_number: str
    user_id: int
    ticket_type: str
    status: str = 'open'
    created_at: Optional[str] = None
    updated_at: Optional[str] = None  # تمت الإضافة لتتوافق مع قاعدة البيانات
    closed_at: Optional[str] = None
    assigned_admin: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert Ticket to dictionary"""
        return {
            'ticket_number': self.ticket_number,
            'user_id': self.user_id,
            'ticket_type': self.ticket_type,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'closed_at': self.closed_at,
            'assigned_admin': self.assigned_admin
}
