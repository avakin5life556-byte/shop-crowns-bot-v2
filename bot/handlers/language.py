from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging
from bot.database.db import db  # تصحيح المسار
from bot.keyboards.inline import get_language_keyboard
from bot.keyboards.reply import get_main_keyboard
from bot.utils.translations import get_text, get_language_name
from bot.config import SUPPORTED_LANGUAGES

# إعداد logging
logger = logging.getLogger(__name__)

router = Router()


def safe_get_text(user_id: int, key: str, default_text: str = "") -> str:
    """دالة آمنة للحصول على النصوص مع fallback"""
    try:
        text = get_text(user_id, key)
        if text and isinstance(text, str) and len(text) > 0:
            return text
    except Exception as e:
        logger.error(f"Error getting text for key {key} for user {user_id}: {e}")
    
    # Fallback إذا كان default_text موجود
    if default_text:
        return default_text
    
    # Fallback نهائي
    lang = db.get_user_language(user_id)
    if key == 'banned':
        return "🚫 تم حظرك من البوت" if lang == 'ar' else "🚫 You are banned"
    elif key == 'lang_title':
        return "🌍 **اختر لغتك المفضلة:**" if lang == 'ar' else "🌍 **Choose your preferred language:**"
    elif key == 'lang_changed':
        return "✅ **تم تغيير اللغة بنجاح**" if lang == 'ar' else "✅ **Language changed successfully**"
    elif key == 'welcome':
        return "اهلاً بك في متجر Shop Crowns 🎉🎁\nاختر من القائمة 👇" if lang == 'ar' else "Welcome to Shop Crowns 🎉🎁\nChoose from the menu 👇"
    
    return default_text if default_text else ""


@router.message(F.text.in_({'🌍 تغيير اللغة', '🌍 Change Language'}))
async def change_language_menu(message: Message):
    """عرض قائمة تغيير اللغة"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        banned_text = safe_get_text(user_id, 'banned', "🚫 تم حظرك من البوت")
        await message.answer(banned_text, parse_mode='Markdown')
        return
    
    # التحقق من وجود نص في الرسالة
    if not message.text:
        return
    
    lang_title = safe_get_text(user_id, 'lang_title', "🌍 **اختر لغتك المفضلة:**")
    
    try:
        await message.answer(
            lang_title,
            reply_markup=get_language_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error showing language menu for user {user_id}: {e}")
        await message.answer("❌ حدث خطأ، حاول مرة أخرى", parse_mode='Markdown')


@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    """تغيير اللغة المختارة"""
    user_id = callback.from_user.id
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await callback.answer("🚫 تم حظرك", show_alert=True)
        return
    
    # التحقق من وجود callback.data
    if not callback.data:
        await callback.answer("❌ حدث خطأ", show_alert=True)
        return
    
    # استخراج اللغة الجديدة مع التحقق من الصحة
    try:
        parts = callback.data.split('_')
        if len(parts) < 2:
            logger.error(f"Invalid callback data format: {callback.data}")
            await callback.answer("❌ بيانات غير صالحة", show_alert=True)
            return
        
        new_lang = parts[1]
    except Exception as e:
        logger.error(f"Error parsing callback data {callback.data}: {e}")
        await callback.answer("❌ حدث خطأ", show_alert=True)
        return
    
    # التحقق من أن اللغة مدعومة
    if new_lang not in SUPPORTED_LANGUAGES:
        logger.warning(f"Unsupported language {new_lang} requested by user {user_id}, falling back to 'ar'")
        new_lang = 'ar'
    
    # تحديث اللغة في قاعدة البيانات
    try:
        success = db.set_user_language(user_id, new_lang)
        if not success:
            logger.error(f"Failed to set language {new_lang} for user {user_id}")
            await callback.answer("❌ فشل تغيير اللغة", show_alert=True)
            return
    except Exception as e:
        logger.error(f"Error setting language for user {user_id}: {e}")
        await callback.answer("❌ حدث خطأ أثناء تغيير اللغة", show_alert=True)
        return
    
    # الحصول على النصوص باللغة الجديدة
    lang_changed_text = safe_get_text(user_id, 'lang_changed', "✅ **تم تغيير اللغة بنجاح**")
    welcome_text = safe_get_text(user_id, 'welcome', "اهلاً بك في متجر Shop Crowns 🎉🎁\nاختر من القائمة 👇")
    
    # تحديث نص الرسالة (إزالة الكيبورد)
    try:
        await callback.message.edit_text(
            lang_changed_text,
            reply_markup=None,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error editing message for user {user_id}: {e}")
        # إذا فشل التعديل، نرسل رسالة جديدة
        await callback.message.answer(lang_changed_text, parse_mode='Markdown')
    
    # إرسال القائمة الرئيسية باللغة الجديدة
    try:
        # استخدام اللغة الجديدة للكيبورد
        await callback.message.answer(
            welcome_text,
            reply_markup=get_main_keyboard(new_lang),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error sending main keyboard for user {user_id}: {e}")
        # محاولة إرسال كيبورد باللغة العربية كـ fallback
        try:
            await callback.message.answer(
                "اهلاً بك في متجر Shop Crowns 🎉🎁\nاختر من القائمة 👇",
                reply_markup=get_main_keyboard('ar'),
                parse_mode='Markdown'
            )
        except Exception as e2:
            logger.error(f"Error sending fallback keyboard for user {user_id}: {e2}")
            await callback.message.answer("❌ حدث خطأ في عرض القائمة", parse_mode='Markdown')
    
    # تأكيد العملية
    await callback.answer()
    
    # تسجيل تغيير اللغة
    logger.info(f"User {user_id} changed language to {new_lang}")


def register_language_handlers(dp):
    """تسجيل معالجات اللغة"""
    dp.include_router(router)
    logger.info("تم تسجيل معالجات اللغة بنجاح")
