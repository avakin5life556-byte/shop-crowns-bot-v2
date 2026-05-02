from aiogram.fsm.state import State, StatesGroup


class ComplaintStates(StatesGroup):
    """حالات الشكاوى - Complaints states"""
    WAITING_MESSAGE = State()


class SupportStates(StatesGroup):
    """حالات الدعم الفني - Support states"""
    LIVE_CHAT = State()
    WAITING_REPLY = State()
