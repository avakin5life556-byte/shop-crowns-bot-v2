from bot.aiogram.fsm.state import State, StatesGroup


class ComplaintStates(StatesGroup):
    """حالات قسم الشكاوى"""
    WAITING_MESSAGE = State()      # انتظار رسالة الشكوى
    LIVE_CHAT = State()            # شات مباشر نشط
    ADMIN_REPLYING = State()       # الأدمن يرد
