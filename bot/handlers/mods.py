from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging
from bot.database.db import db  # تصحيح المسار
from bot.keyboards.inline import get_mods_keyboard, get_back_keyboard, get_back_button
from bot.keyboards.reply import get_main_keyboard
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
@router.message(F.text.in_({'📦 المودات', '📦 Mods'}))
async def show_mods(message: Message):
    """عرض قائمة المودات المتاحة"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await message.answer("🚫 تم حظرك من البوت" if lang == 'ar' else "🚫 You are banned", parse_mode='Markdown')
        return
    
    title = "📦 **المودات المتاحة**\n\nاختر المود الذي تريد تحميله:" if lang == 'ar' else "📦 **Available Mods**\n\nChoose the mod you want to download:"
    
    await message.answer(
        title,
        reply_markup=get_mods_keyboard(lang),
        parse_mode='Markdown'
    )


# ========== اختيار مود معين ==========
@router.callback_query(F.data.in_(['mod_sky', 'mod_bull', 'mod_gold']))
async def handle_mod_selection(callback: CallbackQuery):
    """معالجة اختيار المستخدم لمود معين"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من وجود callback.data
    if not callback.data:
        await callback.answer("❌ حدث خطأ", show_alert=True)
        return
    
    # استخراج المود المختار مع التحقق
    try:
        parts = callback.data.split('_')
        if len(parts) < 2:
            logger.error(f"Invalid callback data format: {callback.data}")
            await callback.answer("❌ بيانات غير صالحة", show_alert=True)
            return
        mod_key = parts[1]
    except Exception as e:
        logger.error(f"Error parsing callback data {callback.data}: {e}")
        await callback.answer("❌ حدث خطأ", show_alert=True)
        return
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await callback.answer("🚫 تم حظرك من البوت" if lang == 'ar' else "🚫 You are banned", show_alert=True)
        return
    
    # التحقق من معدل الطلبات
    try:
        if is_rate_limited(user_id, 'mod_download', limit=10, window=60):
            await callback.answer("⚠️ عدد كبير من الطلبات، انتظر قليلاً" if lang == 'ar' else "⚠️ Too many requests, wait", show_alert=True)
            return
    except Exception as e:
        logger.error(f"Rate limit error for user {user_id}: {e}")
    
    # التحقق من وجود المود
    mod_info = MODS.get(mod_key)
    if not mod_info:
        logger.warning(f"Mod {mod_key} not found for user {user_id}")
        await callback.answer("❌ المود غير موجود" if lang == 'ar' else "❌ Mod not found", show_alert=True)
        return
    
    # الحصول على اسم ورابط المود
    mod_name = mod_info.get(lang, mod_info.get('ar', 'Mod'))
    mod_link = mod_info.get('link', '#')
    
    # إنشاء رسالة التحميل
    if lang == 'ar':
        message_text = (
            f"✅ **{mod_name}**\n\n"
            f"🔗 **رابط التحميل:**\n"
            f"`{mod_link}`\n\n"
            f"📌 اضغط مع الاستمرار على الرابط ثم اختر فتح في المتصفح"
        )
    else:
        message_text = (
            f"✅ **{mod_name}**\n\n"
            f"🔗 **Download Link:**\n"
            f"`{mod_link}`\n\n"
            f"📌 Long press on the link then select open in browser"
        )
    
    # تعديل رسالة الاختيار
    try:
        await callback.message.edit_text(
            "✅ **تم اختيار المود بنجاح**" if lang == 'ar' else "✅ **Mod selected successfully**",
            reply_markup=get_back_keyboard(lang),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error editing message for user {user_id}: {e}")
        await callback.message.answer(
            "✅ **تم اختيار المود بنجاح**" if lang == 'ar' else "✅ **Mod selected successfully**",
            parse_mode='Markdown'
        )
    
    # إرسال رابط التحميل
    try:
        await callback.message.answer(
            message_text,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Error sending mod link to user {user_id}: {e}")
        await callback.message.answer(
            "❌ حدث خطأ في إرسال الرابط، حاول مرة أخرى" if lang == 'ar' else "❌ Error sending link, try again",
            parse_mode='Markdown'
        )
    
    # تسجيل العملية
    try:
        db.log_admin_action(user_id, f'download_mod_{mod_key}', user_id, None, f'تحميل مود {mod_name}' if lang == 'ar' else f'Download mod {mod_name}')
        logger.info(f"User {user_id} downloaded mod {mod_key}")
    except Exception as e:
        logger.error(f"Failed to log mod download for user {user_id}: {e}")
    
    await callback.answer()


# ========== أوامر مباشرة للمودات (كاحتياطي) ==========
@router.message(F.text.in_({'☁️ سكاي مود', 'Sky Mod', '/sky'}))
async def send_sky_mod(message: Message):
    """إرسال رابط Sky Mod مباشرة"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    if db.is_user_banned(user_id):
        await message.answer("🚫 تم حظرك من البوت" if lang == 'ar' else "🚫 You are banned", parse_mode='Markdown')
        return
    
    mod_name = "☁️ Sky Mod"
    mod_link = MOD_LINKS.get('sky', 'https://example.com/sky')
    
    text = (
        f"✅ **{mod_name}**\n\n"
        f"🔗 **رابط التحميل:**\n"
        f"`{mod_link}`"
    )
    
    await message.answer(text, parse_mode='Markdown', disable_web_page_preview=True)


@router.message(F.text.in_({'🐂 بول مود', 'Bull Mod', '/bull'}))
async def send_bull_mod(message: Message):
    """إرسال رابط Bull Mod مباشرة"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    if db.is_user_banned(user_id):
        await message.answer("🚫 تم حظرك من البوت" if lang == 'ar' else "🚫 You are banned", parse_mode='Markdown')
        return
    
    mod_name = "🐂 Bull Mod"
    mod_link = f"{MOD_LINKS.get('bull', 'https://example.com/bull')}\n{MOD_LINKS.get('bull_alt', 'https://example.com/bull_alt')}"
    
    text = (
        f"✅ **{mod_name}**\n\n"
        f"🔗 **روابط التحميل:**\n"
        f"`{mod_link}`"
    )
    
    await message.answer(text, parse_mode='Markdown', disable_web_page_preview=True)


@router.message(F.text.in_({'⭐ جولد مود', 'Gold Mod', '/gold'}))
async def send_gold_mod(message: Message):
    """إرسال رابط Gold Mod مباشرة"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    if db.is_user_banned(user_id):
        await message.answer("🚫 تم حظرك من البوت" if lang == 'ar' else "🚫 You are banned", parse_mode='Markdown')
        return
    
    mod_name = "⭐ Gold Mod"
    mod_link = MOD_LINKS.get('gold', 'https://example.com/gold')
    
    text = (
        f"✅ **{mod_name}**\n\n"
        f"🔗 **رابط التحميل:**\n"
        f"`{mod_link}`"
    )
    
    await message.answer(text, parse_mode='Markdown', disable_web_page_preview=True)


# ========== زر الرجوع ==========
@router.callback_query(F.data == "back_to_mods")
async def back_to_mods(callback: CallbackQuery):
    """العودة إلى قائمة المودات"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    title = "📦 **المودات المتاحة**\n\nاختر المود الذي تريد تحميله:" if lang == 'ar' else "📦 **Available Mods**\n\nChoose the mod you want to download:"
    
    try:
        await callback.message.edit_text(
            title,
            reply_markup=get_mods_keyboard(lang),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in back_to_mods for user {user_id}: {e}")
        await callback.message.answer(
            title,
            reply_markup=get_mods_keyboard(lang),
            parse_mode='Markdown'
        )
    
    await callback.answer()


def register_mods_handlers(dp):
    """تسجيل معالجات المودات"""
    dp.include_router(router)
    logger.info("تم تسجيل معالجات المودات بنجاح")
