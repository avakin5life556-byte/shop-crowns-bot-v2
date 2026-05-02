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


class BroadcastStates(StatesGroup):
    """حالات الإذاعة العامة"""
    WAITING_TEXT = State()
    WAITING_PHOTO = State()
    WAITING_VIDEO = State()
    CONFIRMING = State()


class ChatStates(StatesGroup):
    """حالات الدردشة المباشرة"""
    ACTIVE = State()
    ADMIN_REPLYING = State()
    WAITING_MESSAGE = State()


class ComplaintStates(StatesGroup):
    """حالات الشكاوى والتذاكر"""
    WAITING_MESSAGE = State()
    ADMIN_REPLYING = State()
    LIVE_CHAT = State()


class OrderStates(StatesGroup):
    """حالات الطلبات العامة"""
    WAITING_ORDER_DETAILS = State()
    CONFIRMING_ORDER = State()


class ChangeNameStates(StatesGroup):
    """حالات تغيير الاسم"""
    CHECK_BALANCE = State()
    WAITING_NAME = State()
    WAITING_EMAIL = State()
    WAITING_PASSWORD = State()


class ChangePhotoStates(StatesGroup):
    """حالات تغيير الصورة"""
    CHECK_BALANCE = State()
    WAITING_PHOTO = State()
    WAITING_EMAIL = State()
    WAITING_PASSWORD = State()


class PaidOrderStates(StatesGroup):
    """حالات الطلبات المدفوعة"""
    SELECTING_PRODUCT = State()
    WAITING_PAYMENT = State()
    CONFIRMING = State()
