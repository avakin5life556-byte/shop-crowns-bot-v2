from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.datetime import datetime
import pytz
from bot.database import db
from bot.keyboards.inline import get_rating_keyboard, get_back_keyboard
from bot.keyboards.reply import get_main_keyboard
from bot.utils.translations import get_text
from bot.config import ADMIN_ID, TIMEZONE
from bot.utils.helpers import is_rate_limited

router = Router()


# ========== عرض أزرار التقييم ==========
@router.message(F.text.in_({'⭐ تقييم البوت', '⭐ Rate Bot'}))
async def show_rating(message: Message):
    """عرض أزرار تقييم البوت"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    if db.is_user_banned(user_id):
        await message.answer(get_text(user_id, 'banned'), parse_mode='Markdown')
        return
    
    await message.answer(
        get_text(user_id, 'rate_title'),
        reply_markup=get_rating_keyboard(),
        parse_mode='Markdown'
    )


# ========== معالج الضغط على التقييم ==========
@router.callback_query(F.data.startswith("rate_"))
async def handle_rating(callback: CallbackQuery):
    """معالج اختيار التقييم وحفظه"""
    user_id = callback.from_user.id
    rating = int(callback.data.split('_')[1])
    lang = db.get_user_language(user_id)
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await callback.answer(get_text(user_id, 'banned'), show_alert=True)
        return
    
    # التحقق من معدل التقييمات (منع التكرار)
    if is_rate_limited(user_id, 'rating', limit=1, window=86400):  # مرة واحدة كل 24 ساعة
        await callback.answer("⚠️ يمكنك التقييم مرة واحدة فقط كل 24 ساعة" if lang == 'ar' else "⚠️ You can only rate once every 24 hours", show_alert=True)
        return
    
    # حفظ التقييم في قاعدة البيانات
    db.save_rating(user_id, rating, 'bot', '')
    
    # إشعار المستخدم
    await callback.message.edit_text(
        f"🙏 **شكراً لتقييمك {rating}⭐** ❤️\n\n"
        f"تقييمك يساعدنا على تحسين الخدمة." if lang == 'ar' else
        f"🙏 **Thank you for your {rating}⭐ rating** ❤️\n\n"
        f"Your rating helps us improve our service.",
        reply_markup=get_back_keyboard(lang),
        parse_mode='Markdown'
    )
    
    # إرسال التقييم للأدمن
    user_info = db.get_user_info(user_id)
    now = datetime.now(TIMEZONE)
    
    # تحديد الرموز التعبيرية حسب التقييم
    if rating >= 4:
        emoji = "🌟 ممتاز"
    elif rating >= 3:
        emoji = "👍 جيد"
    else:
        emoji = "👎 يحتاج تحسين"
    
    admin_msg = (
        f"⭐ **تقييم جديد**\n\n"
        f"📊 **التقييم:** {rating}/5 {emoji}\n"
        f"👤 **الاسم:** {user_info['name'] if user_info else 'غير معروف'}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"📝 **Username:** @{user_info['username'] if user_info else 'لا يوجد'}\n"
        f"🗣️ **اللغة:** {lang}\n"
        f"📅 **التاريخ:** {now.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    await callback.bot.send_message(ADMIN_ID, admin_msg, parse_mode='Markdown')
    
    # تسجيل إجراء
    db.log_admin_action(ADMIN_ID, 'rating_received', user_id, None, f'{rating}/5')
    
    await callback.answer()


# ========== عرض التقييمات للأدمن ==========
@router.message(F.text == "📊 التقييمات")
async def show_ratings_admin(message: Message):
    """عرض إحصائيات التقييمات للأدمن"""
    if message.from_user.id != ADMIN_ID:
        return
    
    ratings = db.get_all_ratings()
    
    if not ratings:
        await message.answer("📭 **لا توجد تقييمات بعد**", parse_mode='Markdown')
        return
    
    # حساب متوسط التقييمات
    total_ratings = len(ratings)
    total_score = sum(r['rating'] for r in ratings)
    average = total_score / total_ratings if total_ratings > 0 else 0
    
    # توزيع التقييمات
    distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for r in ratings:
        distribution[r['rating']] += 1
    
    stars = "⭐" * round(average)
    
    text = (
        f"📊 **إحصائيات التقييمات**\n\n"
        f"📝 **عدد التقييمات:** {total_ratings}\n"
        f"🎯 **متوسط التقييم:** {average:.1f}/5 {stars}\n\n"
        f"📈 **توزيع التقييمات:**\n"
        f"5⭐: {distribution[5]} مستخدم\n"
        f"4⭐: {distribution[4]} مستخدم\n"
        f"3⭐: {distribution[3]} مستخدم\n"
        f"2⭐: {distribution[2]} مستخدم\n"
        f"1⭐: {distribution[1]} مستخدم\n\n"
        f"📅 **آخر التقييمات:**"
    )
    
    # إضافة آخر 5 تقييمات
    for rate in ratings[:5]:
        user_info = db.get_user_info(rate['user_id'])
        text += f"\n• {rate['rating']}⭐ من {user_info['name'] if user_info else 'مستخدم'} - {rate['created_at'][:16]}"
    
    await message.answer(text, parse_mode='Markdown')


def register_rating_handlers(dp):
    """تسجيل معالجات التقييم"""
    dp.include_router(router)
