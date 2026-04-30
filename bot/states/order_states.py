from aiogram.fsm.state import State, StatesGroup


class ChangeNameStates(StatesGroup):
    """حالات تغيير الاسم - Change name states"""
    CHECK_BALANCE = State()
    WAITING_NAME = State()
    WAITING_EMAIL = State()
    WAITING_PASSWORD = State()


class ChangePhotoStates(StatesGroup):
    """حالات تغيير الصورة - Change photo states"""
    CHECK_BALANCE = State()
    WAITING_PHOTO = State()
    WAITING_EMAIL = State()
    WAITING_PASSWORD = State()


class PaidOrderStates(StatesGroup):
    """حالات الطلبات المدفوعة - Paid order states"""
    SELECTING = State()
    WAITING_CONTACT = State()
