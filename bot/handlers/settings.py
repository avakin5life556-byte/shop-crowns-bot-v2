from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database import db
from bot.keyboards.reply import get_main_keyboard

router = Router()


@router.message(F.text.in_({'🌍 تغيير اللغة', '🌍 Change Language'}))
async def change_lang_start(message: Message):
    lang = db.get_user_language(message.from_user.id)
    from bot.keyboards.inline import get_back_button
    await message.answer("اختر لغتك:" if lang == 'ar' else "Choose your language:", reply_markup=get_back_button(lang))


def register_settings_handlers(dp):
    dp.include_router(router)
