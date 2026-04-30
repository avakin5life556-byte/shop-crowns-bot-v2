from aiogram.fsm.state import State, StatesGroup


class ChatStates(StatesGroup):
    """حالات الدردشة المباشرة"""
    ACTIVE = State()           # محادثة نشطة
    ADMIN_REPLYING = State()   # الأدمن يرد
    WAITING_USER = State()     # انتظار رد المستخدم
