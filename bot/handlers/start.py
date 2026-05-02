from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
import logging
from bot.database.db import db
from bot.keyboards.reply import get_main_keyboard, get_admin_keyboard
from bot.keyboards.inline import get_language_keyboard
from bot.utils.translations import get_text
from bot.config import ADMIN_ID, TIMEZONE, SUPPORTED_LANGUAGES

# إعداد logging
logger = logging.getLogger(__name__)
router = Router()


def safe_get_text(user_id: int, key: str, **kwargs) -> str:
    """دالة آمنة للحصول على النصوص مع fallback"""
    try:
        text = get_text(user_id, key, **kwargs) if kwargs else get_text(user_id, key)
        if text and isinstance(text, str) and len(text) > 0:
            return text
    except Exception as e:
        logger.error(f"Error getting text for key {key} for user {user_id}: {e}")
    
    # Fallback حسب المفتاح
    lang = db.get_user_language(user_id)
    if key == "messages.banned":
        return "🚫 **تم حظرك من البوت**" if lang == 'ar' else "🚫 **You are banned**"
    elif key == "messages.welcome_new":
        return "🎉 **اهلاً بك في متجر Shop Crowns** 🎉\n\nاختر من القائمة 👇" if lang == 'ar' else "🎉 **Welcome to Shop Crowns** 🎉\n\nChoose from the menu 👇"
    elif key == "messages.new_user_notification":
        name = kwargs.get('name', 'غير معروف')
        username = kwargs.get('username', 'لا يوجد')
        user_id_val = kwargs.get('user_id', 0)
        language = kwargs.get('language', 'ar')
        total_users = kwargs.get('total_users', 0)
        return (
            f"🆕 **مستخدم جديد**\n\n"
            f"👤 **الاسم:** {name}\n"
            f"📝 **اليوزر:** @{username}\n"
            f"🆔 **المعرف:** `{user_id_val}`\n"
            f"🗣️ **اللغة:** {language}\n"
            f"📊 **إجمالي المستخدمين:** {total_users}"
        ) if lang == 'ar' else (
            f"🆕 **New User**\n\n"
            f"👤 **Name:** {name}\n"
            f"📝 **Username:** @{username}\n"
            f"🆔 **User ID:** `{user_id_val}`\n"
            f"🗣️ **Language:** {language}\n"
            f"📊 **Total Users:** {total_users}"
        )
    elif key == "messages.error":
        return "❌ **حدث خطأ، حاول مرة أخرى**" if lang == 'ar' else "❌ **An error occurred, try again**"
    elif key == "admin_menu.title":
        return "👑 **لوحة التحكم - الأدمن**\n\nاختر الإجراء المناسب:" if lang == 'ar' else "👑 **Admin Control Panel**\n\nChoose the appropriate action:"
    elif key == "messages.choose_language":
        return "🌍 **اختر لغتك المفضلة:**" if lang == 'ar' else "🌍 **Choose your preferred language:**"
    elif key == "messages.language_changed":
        return "✅ **تم تغيير اللغة بنجاح**" if lang == 'ar' else "✅ **Language changed successfully**"
    
    return "مرحباً بك في البوت" if lang == 'ar' else "Welcome to the bot"


def safe_split_callback(callback_data: str) -> tuple:
    """تقسيم بيانات الكول باك بشكل آمن"""
    try:
        if not callback_data:
            return None, None
        parts = callback_data.split('_')
        if len(parts) < 2:
            return None, None
        return parts[0], parts[1]
    except Exception as e:
        logger.error(f"Error splitting callback data: {e}")
        return None, None


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Handle /start command"""
    try:
        user_id = message.from_user.id
        full_name = message.from_user.full_name or "مستخدم"
        username = message.from_user.username or ""
        language_code = message.from_user.language_code or "ar"
        
        logger.info(f"✅ /start received from user {user_id}")
        
        # التحقق من الحظر
        if db.is_user_banned(user_id):
            await message.answer(safe_get_text(user_id, "messages.banned"), parse_mode='Markdown')
            return
        
        # تسجيل المستخدم
        try:
            db.register_user(user_id, full_name, username, language_code)
            db.update_last_active(user_id)
        except Exception as e:
            logger.error(f"Error registering user {user_id}: {e}")
        
        # مسح الحالة
        await state.clear()
        
        # إرسال رسالة الترحيب
        welcome_text = safe_get_text(user_id, "messages.welcome_new")
        
        # الحصول على اللغة للمستخدم للكيبورد
        lang = db.get_user_language(user_id)
        
        await message.answer(
            welcome_text,
            reply_markup=get_main_keyboard(lang),
            parse_mode='Markdown'
        )
        
        # إشعار الأدمن
        try:
            stats = db.get_stats()
            total_users = stats.get('active', 0) + stats.get('banned', 0)
            now = datetime.now(TIMEZONE)
            
            admin_msg = safe_get_text(
                user_id,
                "messages.new_user_notification",
                name=full_name,
                username=username,
                user_id=user_id,
                language=language_code,
                total_users=total_users
            )
            await message.bot.send_message(ADMIN_ID, admin_msg, parse_mode='Markdown')
            db.log_admin_action(ADMIN_ID, 'user_registered', user_id, None, f'New user: {full_name}')
        except Exception as e:
            logger.error(f"Error sending admin notification for user {user_id}: {e}")
        
        logger.info(f"✅ /start processed successfully for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error in cmd_start: {e}")
        await message.answer("❌ حدث خطأ، حاول مرة أخرى", parse_mode='Markdown')


@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    """Handler for /admin command"""
    try:
        user_id = message.from_user.id
        if user_id != ADMIN_ID:
            await message.answer(safe_get_text(user_id, "messages.error"), parse_mode='Markdown')
            return
        
        lang = db.get_user_language(user_id)
        await message.answer(
            safe_get_text(user_id, "admin_menu.title"),
            reply_markup=get_admin_keyboard(lang),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in cmd_admin: {e}")
        await message.answer("❌ حدث خطأ", parse_mode='Markdown')


@router.message(Command("language"))
@router.message(Command("lang"))
async def cmd_language(message: types.Message):
    """Handler for /language command - توجيه إلى واجهة تغيير اللغة"""
    try:
        user_id = message.from_user.id
        if db.is_user_banned(user_id):
            await message.answer(safe_get_text(user_id, "messages.banned"), parse_mode='Markdown')
            return
        
        await message.answer(
            safe_get_text(user_id, "messages.choose_language"),
            reply_markup=get_language_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in cmd_language: {e}")
        await message.answer("❌ حدث خطأ", parse_mode='Markdown')


@router.message(lambda m: m.text in ["🌍 تغيير اللغة", "🌍 Change Language"])
async def change_language_button(message: types.Message):
    """Handler for language change button - توجيه إلى واجهة تغيير اللغة"""
    try:
        user_id = message.from_user.id
        if db.is_user_banned(user_id):
            await message.answer(safe_get_text(user_id, "messages.banned"), parse_mode='Markdown')
            return
        
        await message.answer(
            safe_get_text(user_id, "messages.choose_language"),
            reply_markup=get_language_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in change_language_button: {e}")
        await message.answer("❌ حدث خطأ", parse_mode='Markdown')


@router.callback_query(lambda c: c.data and c.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery, state: FSMContext):
    """Handler for setting user language"""
    try:
        user_id = callback.from_user.id
        
        # التحقق من الحظر
        if db.is_user_banned(user_id):
            await callback.answer(safe_get_text(user_id, "messages.banned"), show_alert=True)
            return
        
        # استخراج اللغة بشكل آمن
        prefix, new_lang = safe_split_callback(callback.data)
        if not new_lang:
            await callback.answer("❌ بيانات غير صالحة", show_alert=True)
            return
        
        # التحقق من أن اللغة مدعومة
        if new_lang not in SUPPORTED_LANGUAGES:
            logger.warning(f"Unsupported language {new_lang} requested by user {user_id}")
            new_lang = 'ar'
        
        # تحديث اللغة
        try:
            db.set_user_language(user_id, new_lang)
            db.update_last_active(user_id)
        except Exception as e:
            logger.error(f"Error setting language for user {user_id}: {e}")
            await callback.answer("❌ فشل تغيير اللغة", show_alert=True)
            return
        
        await state.clear()
        
        # تحديث النصوص باللغة الجديدة
        await callback.message.edit_text(
            safe_get_text(user_id, "messages.language_changed"),
            reply_markup=None,
            parse_mode='Markdown'
        )
        
        # إرسال القائمة الرئيسية باللغة الجديدة
        await callback.message.answer(
            safe_get_text(user_id, "messages.welcome_new"),
            reply_markup=get_main_keyboard(new_lang),
            parse_mode='Markdown'
        )
        
        await callback.answer()
        logger.info(f"User {user_id} changed language to {new_lang}")
        
    except Exception as e:
        logger.error(f"Error in set_language: {e}")
        await callback.answer("❌ حدث خطأ", show_alert=True)


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Handler for /help command"""
    try:
        user_id = message.from_user.id
        lang = db.get_user_language(user_id)
        
        # التحقق من الحظر
        if db.is_user_banned(user_id):
            await message.answer(safe_get_text(user_id, "messages.banned"), parse_mode='Markdown')
            return
        
        help_text_ar = (
            "📚 **قائمة الأوامر المتاحة**\n\n"
            "/start - بدء البوت\n"
            "/help - عرض هذه المساعدة\n"
            "/language - تغيير اللغة\n\n"
            "**الأقسام:**\n"
            "🎮 المودات - تحميل المودات\n"
            "💰 طلبات الشراء - شراء كراونز، كوينز، الخ\n"
            "🎁 الطلبات المجانية - تغيير الاسم، الصورة\n"
            "📝 الشكاوى - تقديم شكوى أو استفسار\n"
            "⭐ تقييم البوت - تقييم الخدمة\n"
            "🌍 تغيير اللغة - تغيير لغة البوت"
        )
        help_text_en = (
            "📚 **Available Commands**\n\n"
            "/start - Start the bot\n"
            "/help - Show this help\n"
            "/language - Change language\n\n"
            "**Sections:**\n"
            "🎮 Mods - Download mods\n"
            "💰 Purchase Requests - Buy crowns, coins, etc\n"
            "🎁 Free Requests - Change name, photo\n"
            "📝 Complaints - Submit complaint or inquiry\n"
            "⭐ Rate Bot - Rate the service\n"
            "🌍 Change Language - Change bot language"
        )
        
        help_text = help_text_ar if lang == 'ar' else help_text_en
        await message.answer(help_text, parse_mode='Markdown', reply_markup=get_main_keyboard(lang))
        
    except Exception as e:
        logger.error(f"Error in cmd_help: {e}")
        await message.answer("❌ حدث خطأ", parse_mode='Markdown')


def register_start_handlers(dp):
    """Register all start handlers"""
    dp.include_router(router)
    logger.info("تم تسجيل معالجات start بنجاح")
