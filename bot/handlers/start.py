from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
import pytz
from bot.database.db import db
from bot.keyboards.reply import get_main_keyboard, get_admin_keyboard
from bot.keyboards.inline import get_language_keyboard
from bot.utils.translations import get_text, get_user_language, get_supported_languages
from config import ADMIN_ID, TIMEZONE

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """
    Handle /start command - register user and send welcome message
    """
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username or ""
    language_code = message.from_user.language_code or "ar"
    
    # Check if user is banned
    if db.is_user_banned(user_id):
        await message.answer(get_text(user_id, "messages.banned"), parse_mode='Markdown')
        return
    
    # Register user in database
    db.register_user(user_id, full_name, username, language_code)
    db.update_last_active(user_id)
    
    # Clear any active state
    await state.clear()
    
    # Get user's preferred language
    lang = db.get_user_language(user_id)
    
    # Send welcome message
    welcome_text = get_text(user_id, "messages.welcome_new")
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard(user_id),
        parse_mode='Markdown'
    )
    
    # Notify admin about new user
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
    
    # Log user registration
    db.log_admin_action(ADMIN_ID, 'user_registered', user_id, None, f'New user: {full_name}')


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """
    Admin panel command
    """
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
async def cmd_language(message: Message):
    """
    Change language command
    """
    user_id = message.from_user.id
    
    if db.is_user_banned(user_id):
        await message.answer(get_text(user_id, "messages.banned"), parse_mode='Markdown')
        return
    
    await message.answer(
        get_text(user_id, "messages.choose_language"),
        reply_markup=get_language_keyboard(),
        parse_mode='Markdown'
    )


@router.message(F.text == "🌍 تغيير اللغة")
@router.message(F.text == "🌍 Change Language")
async def change_language_button(message: Message):
    """
    Change language from button
    """
    user_id = message.from_user.id
    
    if db.is_user_banned(user_id):
        await message.answer(get_text(user_id, "messages.banned"), parse_mode='Markdown')
        return
    
    await message.answer(
        get_text(user_id, "messages.choose_language"),
        reply_markup=get_language_keyboard(),
        parse_mode='Markdown'
    )


@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery, state: FSMContext):
    """
    Set user language preference
    """
    user_id = callback.from_user.id
    new_lang = callback.data.split('_')[1]
    
    if new_lang not in get_supported_languages():
        new_lang = 'ar'
    
    # Update language in database
    db.set_user_language(user_id, new_lang)
    db.update_last_active(user_id)
    
    # Clear state
    await state.clear()
    
    # Send confirmation
    await callback.message.edit_text(
        get_text(user_id, "messages.language_changed"),
        reply_markup=None,
        parse_mode='Markdown'
    )
    
    # Send welcome message in new language
    await callback.message.answer(
        get_text(user_id, "messages.welcome_new"),
        reply_markup=get_main_keyboard(user_id),
        parse_mode='Markdown'
    )
    
    await callback.answer()


@router.message(Command("help"))
async def cmd_help(message: Message):
    """
    Help command
    """
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    help_text = (
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
        if lang == 'ar' else
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
    
    await message.answer(help_text, parse_mode='Markdown', reply_markup=get_main_keyboard(user_id))


def register_start_handlers(dp):
    """
    Register all start handlers
    """
    dp.include_router(router)
