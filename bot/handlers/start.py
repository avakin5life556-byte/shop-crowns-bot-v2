from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
import pytz
import logging
from bot.database.db import db
from bot.keyboards.reply import get_main_keyboard, get_admin_keyboard
from bot.keyboards.inline import get_language_keyboard
from bot.utils.translations import get_text, get_user_language, get_supported_languages
from bot.config import ADMIN_ID, TIMEZONE

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Handle /start command"""
    logger.info(f"✅ /start received from user {message.from_user.id}")
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username or ""
    language_code = message.from_user.language_code or "ar"

    # Check if user is banned
    if db.is_user_banned(user_id):
        await message.answer(get_text(user_id, "messages.banned"), parse_mode='Markdown')
        return

    # Register user
    db.register_user(user_id, full_name, username, language_code)
    db.update_last_active(user_id)
    await state.clear()

    # Send welcome message
    welcome_text = get_text(user_id, "messages.welcome_new")
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard(user_id),
        parse_mode='Markdown'
    )

    # Notify admin
    stats = db.get_stats()
    total_users = stats['active'] + stats['banned']
    now = datetime.now(TIMEZONE)

    admin_msg = get_text(
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
    
    logger.info(f"✅ /start processed successfully for user {user_id}")


@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    """Handler for /admin command"""
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        await message.answer(get_text(user_id, "messages.error"), parse_mode='Markdown')
        return
    await message.answer(
        get_text(user_id, "admin_menu.title"),
        reply_markup=get_admin_keyboard(user_id),
        parse_mode='Markdown'
    )


@router.message(Command("language"))
@router.message(Command("lang"))
async def cmd_language(message: types.Message):
    """Handler for /language command"""
    user_id = message.from_user.id
    if db.is_user_banned(user_id):
        await message.answer(get_text(user_id, "messages.banned"), parse_mode='Markdown')
        return
    await message.answer(
        get_text(user_id, "messages.choose_language"),
        reply_markup=get_language_keyboard(),
        parse_mode='Markdown'
    )


@router.message(lambda m: m.text in ["🌍 تغيير اللغة", "🌍 Change Language"])
async def change_language_button(message: types.Message):
    """Handler for language change button"""
    user_id = message.from_user.id
    if db.is_user_banned(user_id):
        await message.answer(get_text(user_id, "messages.banned"), parse_mode='Markdown')
        return
    await message.answer(
        get_text(user_id, "messages.choose_language"),
        reply_markup=get_language_keyboard(),
        parse_mode='Markdown'
    )


@router.callback_query(lambda c: c.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery, state: FSMContext):
    """Handler for setting user language"""
    user_id = callback.from_user.id
    new_lang = callback.data.split('_')[1]
    if new_lang not in get_supported_languages():
        new_lang = 'ar'

    db.set_user_language(user_id, new_lang)
    db.update_last_active(user_id)
    await state.clear()

    await callback.message.edit_text(
        get_text(user_id, "messages.language_changed"),
        reply_markup=None,
        parse_mode='Markdown'
    )
    await callback.message.answer(
        get_text(user_id, "messages.welcome_new"),
        reply_markup=get_main_keyboard(user_id),
        parse_mode='Markdown'
    )
    await callback.answer()


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Handler for /help command"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
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
    await message.answer(help_text, parse_mode='Markdown', reply_markup=get_main_keyboard(user_id))


def register_start_handlers(dp):
    """Register all start handlers"""
    dp.include_router(router)
