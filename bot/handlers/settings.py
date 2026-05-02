from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging
from bot.database.db import db  # تصحيح المسار
from bot.keyboards.reply import get_main_keyboard
from bot.keyboards.inline import get_language_keyboard, get_back_keyboard
from bot.config import ADMIN_ID

# إعداد logging
logger = logging.getLogger(__name__)

router = Router()


def safe_get_text(lang: str, key: str) -> str:
    """دالة آمنة للحصول على النصوص مع fallback"""
    if key == 'settings_title':
        return "⚙️ **الإعدادات**\n\nاختر الإعداد الذي تريد تعديله:" if lang == 'ar' else "⚙️ **Settings**\n\nChoose the setting you want to change:"
    elif key == 'language_title':
        return "🌍 **اختر لغتك المفضلة:**" if lang == 'ar' else "🌍 **Choose your preferred language:**"
    elif key == 'language_changed':
        return "✅ **تم تغيير اللغة بنجاح**" if lang == 'ar' else "✅ **Language changed successfully**"
    elif key == 'welcome':
        return "اهلاً بك في متجر Shop Crowns 🎉🎁\nاختر من القائمة 👇" if lang == 'ar' else "Welcome to Shop Crowns 🎉🎁\nChoose from the menu 👇"
    elif key == 'back':
        return "🔙 رجوع" if lang == 'ar' else "🔙 Back"
    
    return "⚙️ الإعدادات" if lang == 'ar' else "Settings"


# ========== عرض قائمة الإعدادات ==========
@router.message(F.text.in_({'⚙️ الإعدادات', '⚙️ Settings'}))
async def show_settings(message: Message):
    """عرض قائمة الإعدادات الرئيسية"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await message.answer("🚫 تم حظرك من البوت" if lang == 'ar' else "🚫 You are banned", parse_mode='Markdown')
        return
    
    # إنشاء قائمة إعدادات مدمجة (سيتم توسيعها لاحقاً)
    from bot.keyboards.inline import get_settings_keyboard
    
    title = safe_get_text(lang, 'settings_title')
    
    try:
        await message.answer(
            title,
            reply_markup=get_settings_keyboard(lang) if 'get_settings_keyboard' in dir() else get_language_keyboard(lang),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error showing settings menu for user {user_id}: {e}")
        # Fallback: عرض خيار اللغة فقط
        await message.answer(
            title,
            reply_markup=get_language_keyboard(),
            parse_mode='Markdown'
        )


# ========== تغيير اللغة (توجيه إلى نظام اللغة الرئيسي) ==========
@router.message(F.text.in_({'🌍 تغيير اللغة', '🌍 Change Language'}))
async def change_language_redirect(message: Message):
    """توجيه المستخدم إلى نظام تغيير اللغة (تجنب تكرار الكود)"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await message.answer("🚫 تم حظرك من البوت" if lang == 'ar' else "🚫 You are banned", parse_mode='Markdown')
        return
    
    # عرض واجهة تغيير اللغة باستخدام الـ keyboard المخصص للغات
    try:
        await message.answer(
            safe_get_text(lang, 'language_title'),
            reply_markup=get_language_keyboard(),
            parse_mode='Markdown'
        )
        logger.info(f"User {user_id} accessed language settings")
    except Exception as e:
        logger.error(f"Error showing language menu for user {user_id}: {e}")
        await message.answer("❌ حدث خطأ، حاول مرة أخرى", parse_mode='Markdown')


# ========== معالج اختيار اللغة من قائمة الإعدادات ==========
@router.callback_query(F.data == "change_lang")
async def change_lang_from_settings(callback: CallbackQuery):
    """فتح قائمة تغيير اللغة من الإعدادات"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await callback.answer("🚫 تم حظرك من البوت" if lang == 'ar' else "🚫 You are banned", show_alert=True)
        return
    
    try:
        await callback.message.edit_text(
            safe_get_text(lang, 'language_title'),
            reply_markup=get_language_keyboard(),
            parse_mode='Markdown'
        )
        await callback.answer()
        logger.info(f"User {user_id} opened language selection from settings")
    except Exception as e:
        logger.error(f"Error opening language selection for user {user_id}: {e}")
        await callback.answer("❌ حدث خطأ", show_alert=True)


# ========== معالج تغيير اللغة (تم نقله هنا للتكامل) ==========
@router.callback_query(F.data.startswith("lang_"))
async def set_language_from_settings(callback: CallbackQuery):
    """تغيير اللغة المختارة - يتم توجيه المستخدم وإعادة العرض باللغة الجديدة"""
    user_id = callback.from_user.id
    
    # التحقق من وجود callback.data
    if not callback.data:
        await callback.answer("❌ حدث خطأ", show_alert=True)
        return
    
    # استخراج اللغة الجديدة
    try:
        parts = callback.data.split('_')
        if len(parts) < 2:
            await callback.answer("❌ بيانات غير صالحة", show_alert=True)
            return
        new_lang = parts[1]
    except Exception as e:
        logger.error(f"Error parsing language callback: {e}")
        await callback.answer("❌ حدث خطأ", show_alert=True)
        return
    
    # التحقق من أن اللغة مدعومة
    from bot.config import SUPPORTED_LANGUAGES
    if new_lang not in SUPPORTED_LANGUAGES:
        logger.warning(f"Unsupported language {new_lang} requested by user {user_id}")
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
    lang_changed_text = safe_get_text(new_lang, 'language_changed')
    welcome_text = safe_get_text(new_lang, 'welcome')
    
    # تحديث الرسالة الحالية (إظهار نجاح التغيير)
    try:
        await callback.message.edit_text(
            lang_changed_text,
            reply_markup=None,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error editing message for user {user_id}: {e}")
        await callback.message.answer(lang_changed_text, parse_mode='Markdown')
    
    # إرسال القائمة الرئيسية باللغة الجديدة
    try:
        await callback.message.answer(
            welcome_text,
            reply_markup=get_main_keyboard(new_lang),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error sending main keyboard for user {user_id}: {e}")
        await callback.message.answer(
            "اهلاً بك في متجر Shop Crowns 🎉🎁\nاختر من القائمة 👇",
            reply_markup=get_main_keyboard('ar'),
            parse_mode='Markdown'
        )
    
    await callback.answer()
    logger.info(f"User {user_id} changed language to {new_lang} from settings")


# ========== زر الرجوع إلى الإعدادات ==========
@router.callback_query(F.data == "back_to_settings")
async def back_to_settings(callback: CallbackQuery):
    """العودة إلى قائمة الإعدادات الرئيسية"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    title = safe_get_text(lang, 'settings_title')
    
    try:
        from bot.keyboards.inline import get_settings_keyboard
        await callback.message.edit_text(
            title,
            reply_markup=get_settings_keyboard(lang),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error returning to settings for user {user_id}: {e}")
        await callback.message.edit_text(
            title,
            reply_markup=get_language_keyboard(),
            parse_mode='Markdown'
        )
    
    await callback.answer()


# ========== زر الرجوع العام ==========
@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    """العودة إلى القائمة الرئيسية"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    welcome_text = safe_get_text(lang, 'welcome')
    
    try:
        await callback.message.edit_text(
            welcome_text,
            reply_markup=get_main_keyboard(lang),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error returning to main menu for user {user_id}: {e}")
        await callback.message.answer(
            welcome_text,
            reply_markup=get_main_keyboard(lang),
            parse_mode='Markdown'
        )
    
    await callback.answer()


def register_settings_handlers(dp):
    """تسجيل معالجات الإعدادات"""
    dp.include_router(router)
    logger.info("تم تسجيل معالجات الإعدادات بنجاح")
