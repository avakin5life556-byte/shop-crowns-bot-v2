from aiogram import Router, F
from aiogram.types import Message
import logging
from bot.database.db import db
from bot.keyboards.reply import get_main_keyboard, get_back_keyboard, get_mods_keyboard
from bot.config import MOD_LINKS
from bot.utils.helpers import is_rate_limited

# إعداد logging
logger = logging.getLogger(__name__)

router = Router()

# بيانات الـ Mods مع نصوص صحيحة
MODS = {
    'sky': {
        'ar': '☁️ Sky Mod',
        'en': '☁️ Sky Mod',
        'link': MOD_LINKS.get('sky', 'https://example.com/sky')
    },
    'bull': {
        'ar': '🐂 Bull Mod',
        'en': '🐂 Bull Mod',
        'link': f"{MOD_LINKS.get('bull', 'https://example.com/bull')}\n{MOD_LINKS.get('bull_alt', 'https://example.com/bull_alt')}"
    },
    'gold': {
        'ar': '⭐ Gold Mod',
        'en': '⭐ Gold Mod',
        'link': MOD_LINKS.get('gold', 'https://example.com/gold')
    }
}


def safe_get_mod_name(mod_key: str, lang: str) -> str:
    """الحصول على اسم الـ Mod بشكل آمن"""
    try:
        mod_info = MODS.get(mod_key, {})
        return mod_info.get(lang, mod_info.get('ar', 'Mod'))
    except Exception as e:
        logger.error(f"Error getting mod name for {mod_key}: {e}")
        return "Mod"


def safe_get_mod_link(mod_key: str) -> str:
    """الحصول على رابط الـ Mod بشكل آمن"""
    try:
        mod_info = MODS.get(mod_key, {})
        return mod_info.get('link', 'https://example.com')
    except Exception as e:
        logger.error(f"Error getting mod link for {mod_key}: {e}")
        return "https://example.com"


# ========== عرض قائمة الـ Mods ==========
@router.message(F.text.in_({'🎮 المودات', '🎮 Mods'}))
async def show_mods(message: Message):
    """عرض قائمة المودات المتاحة"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await message.answer("🚫 تم حظرك من البوت" if lang == 'ar' else "🚫 You are banned", parse_mode='Markdown')
        return
    
    title = "🎮 **المودات المتاحة**\n\nاختر المود الذي تريد تحميله:" if lang == 'ar' else "🎮 **Available Mods**\n\nChoose the mod you want to download:"
    
    # استخدام reply keyboard للقائمة الرئيسية للمودات
    await message.answer(
        title,
        reply_markup=get_mods_keyboard(user_id, lang),
        parse_mode='Markdown'
    )


# ========== اختيار مود معين ==========
@router.message(F.text.in_({'☁️ سكاي مود', '☁️ Sky Mod'}))
async def handle_sky_mod(message: Message):
    """معالجة اختيار Sky Mod"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await message.answer("🚫 تم حظرك من البوت" if lang == 'ar' else "🚫 You are banned", parse_mode='Markdown')
        return
    
    # التحقق من معدل الطلبات
    try:
        if is_rate_limited(user_id, 'mod_download', limit=10, window=60):
            await message.answer("⚠️ عدد كبير من الطلبات، انتظر قليلاً" if lang == 'ar' else "⚠️ Too many requests, wait", parse_mode='Markdown')
            return
    except Exception as e:
        logger.error(f"Rate limit error for user {user_id}: {e}")
    
    mod_key = 'sky'
    mod_name = safe_get_mod_name(mod_key, lang)
    mod_link = safe_get_mod_link(mod_key)
    
    # إنشاء رسالة التحميل
    if lang == 'ar':
        message_text = (
            f"✅ **{mod_name}**\n\n"
            f"🔗 **رابط التحميل:**\n"
            f"`{mod_link}`\n\n"
            f"📌 اضغط مع الاستمرار على الرابط ثم اختر فتح في المتصفح\n\n"
            f"🔙 اضغط على 'رجوع' للعودة إلى القائمة"
        )
    else:
        message_text = (
            f"✅ **{mod_name}**\n\n"
            f"🔗 **Download Link:**\n"
            f"`{mod_link}`\n\n"
            f"📌 Long press on the link then select open in browser\n\n"
            f"🔙 Press 'Back' to return to the menu"
        )
    
    await message.answer(
        message_text,
        reply_markup=get_back_keyboard(user_id, lang),
        parse_mode='Markdown',
        disable_web_page_preview=True
    )
    
    # تسجيل العملية
    try:
        db.log_admin_action(user_id, f'download_mod_{mod_key}', user_id, None, f'تحميل مود {mod_name}' if lang == 'ar' else f'Download mod {mod_name}')
        logger.info(f"User {user_id} downloaded mod {mod_key}")
    except Exception as e:
        logger.error(f"Failed to log mod download for user {user_id}: {e}")


@router.message(F.text.in_({'🐂 بول مود', '🐂 Bull Mod'}))
async def handle_bull_mod(message: Message):
    """معالجة اختيار Bull Mod"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await message.answer("🚫 تم حظرك من البوت" if lang == 'ar' else "🚫 You are banned", parse_mode='Markdown')
        return
    
    # التحقق من معدل الطلبات
    try:
        if is_rate_limited(user_id, 'mod_download', limit=10, window=60):
            await message.answer("⚠️ عدد كبير من الطلبات، انتظر قليلاً" if lang == 'ar' else "⚠️ Too many requests, wait", parse_mode='Markdown')
            return
    except Exception as e:
        logger.error(f"Rate limit error for user {user_id}: {e}")
    
    mod_key = 'bull'
    mod_name = safe_get_mod_name(mod_key, lang)
    mod_link = safe_get_mod_link(mod_key)
    
    # إنشاء رسالة التحميل
    if lang == 'ar':
        message_text = (
            f"✅ **{mod_name}**\n\n"
            f"🔗 **روابط التحميل:**\n"
            f"`{mod_link}`\n\n"
            f"📌 اضغط مع الاستمرار على الرابط ثم اختر فتح في المتصفح\n\n"
            f"🔙 اضغط على 'رجوع' للعودة إلى القائمة"
        )
    else:
        message_text = (
            f"✅ **{mod_name}**\n\n"
            f"🔗 **Download Links:**\n"
            f"`{mod_link}`\n\n"
            f"📌 Long press on the link then select open in browser\n\n"
            f"🔙 Press 'Back' to return to the menu"
        )
    
    await message.answer(
        message_text,
        reply_markup=get_back_keyboard(user_id, lang),
        parse_mode='Markdown',
        disable_web_page_preview=True
    )
    
    # تسجيل العملية
    try:
        db.log_admin_action(user_id, f'download_mod_{mod_key}', user_id, None, f'تحميل مود {mod_name}' if lang == 'ar' else f'Download mod {mod_name}')
        logger.info(f"User {user_id} downloaded mod {mod_key}")
    except Exception as e:
        logger.error(f"Failed to log mod download for user {user_id}: {e}")


@router.message(F.text.in_({'⭐ جولد مود', '⭐ Gold Mod'}))
async def handle_gold_mod(message: Message):
    """معالجة اختيار Gold Mod"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await message.answer("🚫 تم حظرك من البوت" if lang == 'ar' else "🚫 You are banned", parse_mode='Markdown')
        return
    
    # التحقق من معدل الطلبات
    try:
        if is_rate_limited(user_id, 'mod_download', limit=10, window=60):
            await message.answer("⚠️ عدد كبير من الطلبات، انتظر قليلاً" if lang == 'ar' else "⚠️ Too many requests, wait", parse_mode='Markdown')
            return
    except Exception as e:
        logger.error(f"Rate limit error for user {user_id}: {e}")
    
    mod_key = 'gold'
    mod_name = safe_get_mod_name(mod_key, lang)
    mod_link = safe_get_mod_link(mod_key)
    
    # إنشاء رسالة التحميل
    if lang == 'ar':
        message_text = (
            f"✅ **{mod_name}**\n\n"
            f"🔗 **رابط التحميل:**\n"
            f"`{mod_link}`\n\n"
            f"📌 اضغط مع الاستمرار على الرابط ثم اختر فتح في المتصفح\n\n"
            f"🔙 اضغط على 'رجوع' للعودة إلى القائمة"
        )
    else:
        message_text = (
            f"✅ **{mod_name}**\n\n"
            f"🔗 **Download Link:**\n"
            f"`{mod_link}`\n\n"
            f"📌 Long press on the link then select open in browser\n\n"
            f"🔙 Press 'Back' to return to the menu"
        )
    
    await message.answer(
        message_text,
        reply_markup=get_back_keyboard(user_id, lang),
        parse_mode='Markdown',
        disable_web_page_preview=True
    )
    
    # تسجيل العملية
    try:
        db.log_admin_action(user_id, f'download_mod_{mod_key}', user_id, None, f'تحميل مود {mod_name}' if lang == 'ar' else f'Download mod {mod_name}')
        logger.info(f"User {user_id} downloaded mod {mod_key}")
    except Exception as e:
        logger.error(f"Failed to log mod download for user {user_id}: {e}")


# ========== أوامر مباشرة للمودات (كاحتياطي) ==========
@router.message(F.text == '/sky')
async def handle_sky_command(message: Message):
    """معالجة الأمر المباشر /sky"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    if db.is_user_banned(user_id):
        await message.answer("🚫 تم حظرك من البوت" if lang == 'ar' else "🚫 You are banned", parse_mode='Markdown')
        return
    
    mod_key = 'sky'
    mod_name = "☁️ Sky Mod"
    mod_link = MOD_LINKS.get('sky', 'https://example.com/sky')
    
    text = (
        f"✅ **{mod_name}**\n\n"
        f"🔗 **رابط التحميل:**\n"
        f"`{mod_link}`"
    )
    
    await message.answer(text, parse_mode='Markdown', disable_web_page_preview=True)
    
    try:
        db.log_admin_action(user_id, f'download_mod_{mod_key}', user_id, None, f'تحميل مود {mod_name}' if lang == 'ar' else f'Download mod {mod_name}')
    except Exception as e:
        logger.error(f"Failed to log mod download for user {user_id}: {e}")


@router.message(F.text == '/bull')
async def handle_bull_command(message: Message):
    """معالجة الأمر المباشر /bull"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    if db.is_user_banned(user_id):
        await message.answer("🚫 تم حظرك من البوت" if lang == 'ar' else "🚫 You are banned", parse_mode='Markdown')
        return
    
    mod_key = 'bull'
    mod_name = "🐂 Bull Mod"
    mod_link = f"{MOD_LINKS.get('bull', 'https://example.com/bull')}\n{MOD_LINKS.get('bull_alt', 'https://example.com/bull_alt')}"
    
    text = (
        f"✅ **{mod_name}**\n\n"
        f"🔗 **روابط التحميل:**\n"
        f"`{mod_link}`"
    )
    
    await message.answer(text, parse_mode='Markdown', disable_web_page_preview=True)
    
    try:
        db.log_admin_action(user_id, f'download_mod_{mod_key}', user_id, None, f'تحميل مود {mod_name}' if lang == 'ar' else f'Download mod {mod_name}')
    except Exception as e:
        logger.error(f"Failed to log mod download for user {user_id}: {e}")


@router.message(F.text == '/gold')
async def handle_gold_command(message: Message):
    """معالجة الأمر المباشر /gold"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    if db.is_user_banned(user_id):
        await message.answer("🚫 تم حظرك من البوت" if lang == 'ar' else "🚫 You are banned", parse_mode='Markdown')
        return
    
    mod_key = 'gold'
    mod_name = "⭐ Gold Mod"
    mod_link = MOD_LINKS.get('gold', 'https://example.com/gold')
    
    text = (
        f"✅ **{mod_name}**\n\n"
        f"🔗 **رابط التحميل:**\n"
        f"`{mod_link}`"
    )
    
    await message.answer(text, parse_mode='Markdown', disable_web_page_preview=True)
    
    try:
        db.log_admin_action(user_id, f'download_mod_{mod_key}', user_id, None, f'تحميل مود {mod_name}' if lang == 'ar' else f'Download mod {mod_name}')
    except Exception as e:
        logger.error(f"Failed to log mod download for user {user_id}: {e}")


# ========== زر الرجوع (Reply Keyboard) ==========
@router.message(F.text.in_({'🔙 رجوع', '🔙 Back'}))
async def back_to_mods(message: Message):
    """العودة إلى قائمة المودات"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await message.answer("🚫 تم حظرك من البوت" if lang == 'ar' else "🚫 You are banned", parse_mode='Markdown')
        return
    
    title = "🎮 **المودات المتاحة**\n\nاختر المود الذي تريد تحميله:" if lang == 'ar' else "🎮 **Available Mods**\n\nChoose the mod you want to download:"
    
    await message.answer(
        title,
        reply_markup=get_mods_keyboard(user_id, lang),
        parse_mode='Markdown'
    )


def register_mods_handlers(dp):
    """تسجيل معالجات المودات"""
    dp.include_router(router)
    logger.info("تم تسجيل معالجات المودات بنجاح")
