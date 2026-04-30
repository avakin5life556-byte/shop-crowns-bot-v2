from aiogram.fsm.state import State, StatesGroup

class ComplaintStates(StatesGroup):
    WAITING_MESSAGE = State()


class SupportStates(StatesGroup):
    LIVE_CHAT = State()
    WAITING_REPLY = State()
