from aiogram.fsm.state import State, StatesGroup


class AdminControlStates(StatesGroup):
    """حالات تحكم الأدمن في البوت"""
    WAITING_PHOTO = State()
    WAITING_VIDEO = State()
    WAITING_DOCUMENT = State()
    WAITING_BROADCAST = State()


class AdminReplyStates(StatesGroup):
    """حالات رد الأدمن"""
    WAITING_REPLY = State()
    WAITING_BAN_USER = State()
    WAITING_UNBAN_USER = State()