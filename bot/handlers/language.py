from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database import db
from bot.keyboards.inline import get_language_keyboard
from bot.keyboards.reply import get_main_keyboard
from bot.utils.translations import get_text, get_language_name
from bot.config import SUPPORTED_LANGUAGES

router = Router()


@router.message(F.text.in_({'🌍 تغيير اللغة', '🌍 Change Language'}))
async def change_language_menu(message: Message):
    """عرض قائمة تغيير اللغة"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    if db.is_user_banned(user_id):
        await message.answer(get_text(user_id, 'banned'), parse_mode='Markdown')
        return
    
    await message.answer(
        get_text(user_id, 'lang_title'),
        reply_markup=get_language_keyboard(),
        parse_mode='Markdown'
    )


@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    """تغيير اللغة المختارة"""
    user_id = callback.from_user.id
    new_lang = callback.data.split('_')[1]
    
    if new_lang not in SUPPORTED_LANGUAGES:
        new_lang = 'ar'
    
    # تحديث اللغة في قاعدة البيانات
    db.set_user_language(user_id, new_lang)
    
    # تحديث نص الرسالة
    await callback.message.edit_text(
        get_text(user_id, 'lang_changed'),
        reply_markup=None,
        parse_mode='Markdown'
    )
    
    # إرسال القائمة الرئيسية باللغة الجديدة
    await callback.message.answer(
        get_text(user_id, 'welcome'),
        reply_markup=get_main_keyboard(new_lang),
        parse_mode='Markdown'
    )
    
    await callback.answer()


def register_language_handlers(dp):
    """تسجيل معالجات اللغة"""
    dp.include_router(router)
