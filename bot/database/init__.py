from .db import Database, db

# محاولة استيراد النماذج إذا كانت موجودة
try:
    from bot.models import User, Order, Ticket
    __all__ = ['Database', 'db', 'User', 'Order', 'Ticket']
except ImportError:
    # إذا لم تكن النماذج موجودة، نستورد فقط قاعدة البيانات
    __all__ = ['Database', 'db']
