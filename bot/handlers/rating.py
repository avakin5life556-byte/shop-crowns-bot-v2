from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
import logging
from bot.database.db import db  # تصحيح المسار
from bot.keyboards.inline import get_rating_keyboard, get_back_keyboard
from bot.keyboards.reply import get_main_keyboard
from bot.utils.translations import get_text
from bot.config import ADMIN_ID, TIMEZONE
from bot.utils.helpers import is_rate_limited

# إعداد logging
logger = logging.getLogger(__name__)

router = Router()


def safe_split_callback(callback_data: str, expected_parts: int = 2) -> list:
    """تقسيم بيانات الكول باك بشكل آمن"""
    try:
        if not callback_data:
            logger.error("Empty callback data")
            return []
        parts = callback_data.split('_')
        if len(parts) < expected_parts:
            logger.error(f"Invalid callback data format: {callback_data}, expected {expected_parts} parts, got {len(parts)}")
            return []
        return parts
    except Exception as e:
        logger.error(f"Error splitting callback data {callback_data}: {e}")
        return []


def safe_get_rating(rating_str: str) -> int:
    """تحويل التقييم إلى رقم صحيح بشكل آمن"""
    try:
        rating = int(rating_str)
        if 1 <= rating <= 5:
            return rating
        else:
            logger.warning(f"Rating {rating} is out of range (1-5)")
            return 5  # Fallback إلى أعلى تقييم
    except (ValueError, TypeError) as e:
        logger.error(f"Error converting rating {rating_str}: {e}")
        return 5  # Fallback إلى أعلى تقييم


def safe_get_text(lang: str, key: str, default_ar: str = "", default_en: str = "") -> str:
    """دالة آمنة للحصول على النصوص مع fallback"""
    if key == 'banned':
        return "🚫 **تم حظرك من البوت**" if lang == 'ar' else "🚫 **You are banned**"
    elif key == 'rate_title':
        return "⭐ **قيم البوت**\n\nكيف تقيم تجربتك معنا؟" if lang == 'ar' else "⭐ **Rate the Bot**\n\nHow would you rate your experience with us?"
    elif key == 'rate_limit':
        return "⚠️ **يمكنك التقييم مرة واحدة فقط كل 24 ساعة**" if lang == 'ar' else "⚠️ **You can only rate once every 24 hours**"
    elif key == 'thanks_rating':
        return "🙏 **شكراً لتقييمك {rating}⭐** ❤️\n\nتقييمك يساعدنا على تحسين الخدمة." if lang == 'ar' else "🙏 **Thank you for your {rating}⭐ rating** ❤️\n\nYour rating helps us improve our service."
    elif key == 'no_ratings':
        return "📭 **لا توجد تقييمات بعد**" if lang == 'ar' else "📭 **No ratings yet**"
    elif key == 'ratings_stats':
        return "📊 **إحصائيات التقييمات**" if lang == 'ar' else "📊 **Ratings Statistics**"
    
    return default_ar if lang == 'ar' else default_en


def get_rating_emoji(rating: int) -> str:
    """الحصول على رمز تعبيري حسب التقييم"""
    if rating >= 5:
        return "🌟 ممتاز"
    elif rating >= 4:
        return "👍 جيد جداً"
    elif rating >= 3:
        return "👌 جيد"
    else:
        return "👎 يحتاج تحسين"


# ========== عرض أزرار التقييم ==========
@router.message(F.text.in_({'⭐ تقييم البوت', '⭐ Rate Bot'}))
async def show_rating(message: Message):
    """عرض أزرار تقييم البوت"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await message.answer(safe_get_text(lang, 'banned'), parse_mode='Markdown')
        return
    
    try:
        rating_title = safe_get_text(lang, 'rate_title')
        await message.answer(
            rating_title,
            reply_markup=get_rating_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error showing rating menu for user {user_id}: {e}")
        await message.answer("❌ حدث خطأ، حاول مرة أخرى", parse_mode='Markdown')


# ========== معالج الضغط على التقييم ==========
@router.callback_query(F.data.startswith("rate_"))
async def handle_rating(callback: CallbackQuery):
    """معالج اختيار التقييم وحفظه"""
    user_id = callback.from_user.id
    
    # التحقق من وجود callback.data
    if not callback.data:
        await callback.answer("❌ حدث خطأ", show_alert=True)
        return
    
    # تقسيم البيانات بشكل آمن
    parts = safe_split_callback(callback.data, 2)
    if not parts or len(parts) < 2:
        await callback.answer("❌ بيانات غير صالحة", show_alert=True)
        return
    
    # استخراج التقييم بشكل آمن
    rating_value = parts[1]
    rating = safe_get_rating(rating_value)
    
    lang = db.get_user_language(user_id)
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await callback.answer(safe_get_text(lang, 'banned'), show_alert=True)
        return
    
    # التحقق من معدل التقييمات (منع التكرار - مرة واحدة كل 24 ساعة)
    try:
        if is_rate_limited(user_id, 'rating', limit=1, window=86400):
            rate_limit_msg = safe_get_text(lang, 'rate_limit')
            await callback.answer(rate_limit_msg, show_alert=True)
            return
    except Exception as e:
        logger.error(f"Rate limit error for user {user_id}: {e}")
    
    # حفظ التقييم في قاعدة البيانات
    try:
        success = db.save_rating(user_id, rating, 'bot', '')
        if not success:
            logger.error(f"Failed to save rating for user {user_id}")
            await callback.answer("❌ حدث خطأ في حفظ التقييم", show_alert=True)
            return
    except Exception as e:
        logger.error(f"Error saving rating for user {user_id}: {e}")
        await callback.answer("❌ حدث خطأ في حفظ التقييم", show_alert=True)
        return
    
    # إشعار المستخدم
    thanks_text = safe_get_text(lang, 'thanks_rating').format(rating=rating)
    
    try:
        await callback.message.edit_text(
            thanks_text,
            reply_markup=get_back_keyboard(lang),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error editing message for user {user_id}: {e}")
        await callback.message.answer(thanks_text, parse_mode='Markdown')
    
    # إرسال التقييم للأدمن
    user_info = db.get_user_info(user_id)
    now = datetime.now(TIMEZONE)
    
    user_name = user_info.get('name', 'غير معروف') if user_info else 'غير معروف'
    user_username = user_info.get('username', 'لا يوجد') if user_info else 'لا يوجد'
    user_country = user_info.get('country', 'غير معروف') if user_info else 'غير معروف'
    
    rating_emoji = get_rating_emoji(rating)
    
    admin_msg = (
        f"⭐ **تقييم جديد**\n\n"
        f"📊 **التقييم:** {rating}/5 {rating_emoji}\n"
        f"👤 **الاسم:** {user_name}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"📝 **Username:** @{user_username}\n"
        f"🗣️ **اللغة:** {lang}\n"
        f"🌍 **الدولة:** {user_country}\n"
        f"📅 **التاريخ:** {now.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    try:
        await callback.bot.send_message(ADMIN_ID, admin_msg, parse_mode='Markdown')
        logger.info(f"Rating notification sent to admin for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to send rating notification to admin: {e}")
    
    # تسجيل إجراء
    try:
        db.log_admin_action(ADMIN_ID, 'rating_received', user_id, None, f'{rating}/5')
    except Exception as e:
        logger.error(f"Failed to log admin action: {e}")
    
    await callback.answer()
    logger.info(f"User {user_id} rated bot {rating}/5")


# ========== عرض التقييمات للأدمن ==========
@router.message(F.text == "📊 التقييمات")
async def show_ratings_admin(message: Message):
    """عرض إحصائيات التقييمات للأدمن"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        ratings = db.get_all_ratings()
        
        if not ratings:
            await message.answer(safe_get_text('ar', 'no_ratings'), parse_mode='Markdown')
            return
        
        # حساب متوسط التقييمات
        total_ratings = len(ratings)
        
        # جمع التقييمات بشكل آمن
        total_score = 0
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for r in ratings:
            try:
                # التعامل مع تنسيقات مختلفة للبيانات
                if isinstance(r, dict):
                    rating_value = r.get('rating', 0)
                    user_id_val = r.get('user_id', 0)
                    created_at_val = r.get('created_at', '')
                elif isinstance(r, (list, tuple)):
                    rating_value = r[2] if len(r) > 2 else 0
                    user_id_val = r[1] if len(r) > 1 else 0
                    created_at_val = r[5] if len(r) > 5 else ''
                else:
                    continue
                
                # التحقق من صحة التقييم
                if 1 <= rating_value <= 5:
                    total_score += rating_value
                    distribution[rating_value] = distribution.get(rating_value, 0) + 1
                else:
                    logger.warning(f"Invalid rating value: {rating_value}")
                    
            except Exception as e:
                logger.error(f"Error processing rating: {e}")
                continue
        
        # حساب المتوسط
        average = total_score / total_ratings if total_ratings > 0 else 0
        stars_count = round(average)
        stars = "⭐" * stars_count if stars_count <= 5 else "⭐⭐⭐⭐⭐"
        
        text = (
            f"📊 **إحصائيات التقييمات**\n\n"
            f"📝 **عدد التقييمات:** {total_ratings}\n"
            f"🎯 **متوسط التقييم:** {average:.1f}/5 {stars}\n\n"
            f"📈 **توزيع التقييمات:**\n"
            f"5⭐: {distribution.get(5, 0)} مستخدم\n"
            f"4⭐: {distribution.get(4, 0)} مستخدم\n"
            f"3⭐: {distribution.get(3, 0)} مستخدم\n"
            f"2⭐: {distribution.get(2, 0)} مستخدم\n"
            f"1⭐: {distribution.get(1, 0)} مستخدم\n\n"
            f"📅 **آخر التقييمات:**"
        )
        
        # إضافة آخر 5 تقييمات
        count = 0
        for rate in ratings[:10]:  # استخدام أول 10 تقييمات
            try:
                if isinstance(rate, dict):
                    rating_value = rate.get('rating', 0)
                    user_id_val = rate.get('user_id', 0)
                    created_at_val = rate.get('created_at', '')
                elif isinstance(rate, (list, tuple)):
                    rating_value = rate[2] if len(rate) > 2 else 0
                    user_id_val = rate[1] if len(rate) > 1 else 0
                    created_at_val = rate[5] if len(rate) > 5 else ''
                else:
                    continue
                
                user_info = db.get_user_info(user_id_val)
                user_name = user_info.get('name', 'مستخدم') if user_info else 'مستخدم'
                created_date = created_at_val[:16] if created_at_val else 'تاريخ غير معروف'
                
                text += f"\n• {rating_value}⭐ من {user_name} - {created_date}"
                count += 1
                if count >= 5:
                    break
            except Exception as e:
                logger.error(f"Error processing rating display: {e}")
                continue
        
        await message.answer(text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error showing ratings for admin: {e}")
        await message.answer("❌ حدث خطأ في عرض التقييمات", parse_mode='Markdown')


def register_rating_handlers(dp):
    """تسجيل معالجات التقييم"""
    dp.include_router(router)
    logger.info("تم تسجيل معالجات التقييم بنجاح")
