from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database import db
from bot.keyboards.inline import get_live_chat_keyboard, get_support_rating_keyboard
from bot.keyboards.reply import get_main_keyboard
from bot.states.support_states import ComplaintStates
from bot.config import ADMIN_ID
from datetime import datetime

router = Router()


@router.message(F.text.in_({'📝 الشكاوى', '📝 Complaints'}))
async def show_complaint(message: Message, state: FSMContext):
    lang = db.get_user_language(message.from_user.id)
    await message.answer("📝 اكتب شكواك:" if lang == 'ar' else "📝 Write your complaint:")
    await state.set_state(ComplaintStates.WAITING_MESSAGE)


def register_support_handlers(dp):
    dp.include_router(router)
