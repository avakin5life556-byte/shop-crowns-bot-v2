from bot.aiogram import Router, F
from bot.aiogram.types import Message, CallbackQuery
from bot.aiogram.fsm.context import FSMContext
from bot.database import db
from bot.keyboards.inline import get_yes_no_keyboard, get_contact_button, get_order_admin_keyboard
from bot.keyboards.reply import get_main_keyboard
from bot.states.order_states import ChangeNameStates, ChangePhotoStates
from bot.config import ADMIN_ID, TIMEZONE
from bot.datetime import datetime
import json

router = Router()
temp_data = {}


@router.message(F.text.in_({'  ', ' Free Requests'}))
async def show_free_orders(message: Message):
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    from keyboards.inline import get_back_button
    markup = get_back_button(lang)
    
    await message.answer("  " if lang == 'ar' else " Free Requests", reply_markup=markup)


@router.callback_query(F.data == "change_name")
async def change_name_start(callback: CallbackQuery, state: FSMContext):
    lang = db.get_user_language(callback.from_user.id)
    await callback.message.edit_text(
        "   5000 " if lang == 'ar' else " Do you have 5000 coins?",
        reply_markup=get_yes_no_keyboard()
    )
    await state.set_state(ChangeNameStates.CHECK_BALANCE)
    await callback.answer()


def register_orders_handlers(dp):
    dp.include_router(router)
