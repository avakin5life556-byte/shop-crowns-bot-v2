from bot.aiogram.fsm.state import State, StatesGroup


class BroadcastStates(StatesGroup):
    """حالات الإذاعة"""
    WAITING_TEXT = State()       # انتظار نص الإذاعة
    WAITING_PHOTO = State()      # انتظار صورة للإذاعة
    WAITING_VIDEO = State()      # انتظار فيديو للإذاعة
    CONFIRMING = State()         # تأكيد الإذاعة
