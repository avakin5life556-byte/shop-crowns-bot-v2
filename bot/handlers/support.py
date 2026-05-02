from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
import logging
from bot.database.db import db
from bot.keyboards.inline import get_live_chat_keyboard, get_support_rating_keyboard, get_back_keyboard
from bot.keyboards.reply import get_main_keyboard
from bot.states.support_states import ComplaintStates
from bot.config import ADMIN_ID, TIMEZONE
from bot.utils.helpers import sanitize_input, is_rate_limited
from bot.utils.translations import get_text

# إعداد logging
logger = logging.getLogger(__name__)

router = Router()


def safe_get_text(user_id: int, key: str, default_ar: str = "", default_en: str = "") -> str:
    """دالة آمنة للحصول على النصوص مع fallback"""
    try:
        text = get_text(user_id, key)
        if text and isinstance(text, str) and len(text) > 0:
            return text
    except Exception as e:
        logger.error(f"Error getting text for key {key} for user {user_id}: {e}")
    
    # Fallback حسب اللغة
    lang = db.get_user_language(user_id)
    
    if default_ar and default_en:
        return default_ar if lang == 'ar' else default_en
    
    # Fallback افتراضي حسب المفتاح
    if key == "complaint_title":
        return "📝 **قسم الشكاوى**\n\nاختر نوع التواصل:" if lang == 'ar' else "📝 **Complaints Section**\n\nChoose communication type:"
    elif key == "complaint_prompt":
        return "📝 **اكتب شكواك أو استفسارك بالتفصيل:**" if lang == 'ar' else "📝 **Write your complaint or inquiry in detail:**"
    elif key == "complaint_thanks":
        return "🙏 **شكراً لتواصلك معنا**\n\nسيتم الرد عليك في أقرب وقت ممكن." if lang == 'ar' else "🙏 **Thank you for contacting us**\n\nWe will respond to you as soon as possible."
    elif key == "complaint_error":
        return "❌ **حدث خطأ، حاول مرة أخرى**" if lang == 'ar' else "❌ **An error occurred, try again**"
    elif key == "complaint_rate_limit":
        return "⚠️ **أرسلت شكاوى كثيرة، انتظر قليلاً**" if lang == 'ar' else "⚠️ **Too many complaints, wait a moment**"
    elif key == "banned":
        return "🚫 **تم حظرك من البوت**" if lang == 'ar' else "🚫 **You are banned**"
    elif key == "invalid_complaint":
        return "⚠️ **الرجاء كتابة شكوى صالحة**" if lang == 'ar' else "⚠️ **Please write a valid complaint**"
    
    return default_ar if lang == 'ar' else default_en


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


# ========== عرض قسم الشكاوى ==========
@router.message(F.text.in_({'📝 الشكاوى', '📝 Complaints'}))
async def show_complaints(message: Message, state: FSMContext):
    """عرض خيارات قسم الشكاوى"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await message.answer(safe_get_text(user_id, "banned"), parse_mode='Markdown')
        return
    
    # التحقق من وجود نص في الرسالة
    if not message.text:
        return
    
    # عرض قائمة الشكاوى
    try:
        from bot.keyboards.inline import get_complaints_keyboard
        title = safe_get_text(user_id, "complaint_title")
        await message.answer(
            title,
            reply_markup=get_complaints_keyboard(lang),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error showing complaints menu for user {user_id}: {e}")
        await message.answer(safe_get_text(user_id, "complaint_error"), parse_mode='Markdown')


# ========== بدء كتابة شكوى جديدة ==========
@router.callback_query(F.data == "create_ticket")
async def create_complaint_ticket(callback: CallbackQuery, state: FSMContext):
    """بدء إنشاء تذكرة شكوى جديدة"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await callback.answer(safe_get_text(user_id, "banned"), show_alert=True)
        return
    
    # التحقق من وجود callback.data
    if not callback.data:
        await callback.answer("❌ حدث خطأ", show_alert=True)
        return
    
    # التحقق من معدل الطلبات
    try:
        if is_rate_limited(user_id, 'complaint_ticket', limit=2, window=600):
            await callback.answer(safe_get_text(user_id, "complaint_rate_limit"), show_alert=True)
            return
    except Exception as e:
        logger.error(f"Rate limit error for user {user_id}: {e}")
    
    # التحقق من وجود تذكرة نشطة
    active_ticket = db.get_active_ticket_by_user(user_id)
    if active_ticket and active_ticket.get('ticket_type') == 'complaint':
        await callback.answer("⚠️ لديك تذكرة شكوى مفتوحة بالفعل" if lang == 'ar' else "⚠️ You already have an open complaint ticket", show_alert=True)
        return
    
    # عرض رسالة طلب كتابة الشكوى
    prompt_text = safe_get_text(user_id, "complaint_prompt")
    
    try:
        await callback.message.edit_text(
            prompt_text,
            parse_mode='Markdown'
        )
        await state.set_state(ComplaintStates.WAITING_MESSAGE)
        await callback.answer()
    except Exception as e:
        logger.error(f"Error starting complaint ticket for user {user_id}: {e}")
        await callback.answer(safe_get_text(user_id, "complaint_error"), show_alert=True)


# ========== استقبال رسالة الشكوى وإنشاء التذكرة ==========
@router.message(ComplaintStates.WAITING_MESSAGE)
async def receive_complaint_message(message: Message, state: FSMContext):
    """استقبال رسالة الشكوى وإنشاء التذكرة"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await message.answer(safe_get_text(user_id, "banned"), parse_mode='Markdown')
        await state.clear()
        return
    
    # التحقق من وجود نص
    if not message.text:
        await message.answer(safe_get_text(user_id, "invalid_complaint"), parse_mode='Markdown')
        return
    
    # تنظيف النص
    complaint_text = sanitize_input(message.text, max_length=1000)
    if not complaint_text:
        await message.answer(safe_get_text(user_id, "invalid_complaint"), parse_mode='Markdown')
        return
    
    # إنشاء تذكرة جديدة
    try:
        ticket_data = db.create_ticket(user_id, 'complaint', complaint_text)
        
        if not ticket_data or not ticket_data[0] or not ticket_data[1]:
            logger.error(f"Failed to create complaint ticket for user {user_id}")
            await message.answer(safe_get_text(user_id, "complaint_error"), parse_mode='Markdown')
            await state.clear()
            return
        
        ticket_number, ticket_id = ticket_data
        
        # تحديث حالة FSM
        await state.update_data(
            ticket_id=ticket_id,
            ticket_number=ticket_number
        )
        
        # إرسال رسالة شكر للمستخدم
        thanks_text = safe_get_text(user_id, "complaint_thanks")
        
        await message.answer(
            thanks_text,
            reply_markup=get_back_keyboard(lang),
            parse_mode='Markdown'
        )
        
        # إرسال إشعار للأدمن
        user_info = db.get_user_info(user_id)
        now = datetime.now(TIMEZONE)

        user_name = user_info.get('name', 'غير معروف') if user_info else 'غير معروف'
        user_username = user_info.get('username') if user_info else None
        username_display = f"@{user_username}" if user_username else "لا يوجد"
        user_country = user_info.get('country', 'غير معروف') if user_info else 'غير معروف'
        
       from aiogram.utils.markdown import escape_md
       safe_text = escape_md(complaint_text)
       admin_msg = (
            f"📝 **شكوى جديدة**\n\n"
            f"🎫 **رقم التذكرة:** `{ticket_number}`\n"
            f"👤 **الاسم:** {user_name}\n"
            f"🆔 **User ID:** `{user_id}`\n"
            f"📝 **Username:** {username_display}\n"
            f"🗣️ **اللغة:** {lang}\n"
            f"🌍 **الدولة:** {user_country}\n"
            f"📅 **التاريخ:** {now.strftime('%Y-%m-%d %H:%M:%S')}\n\n"                
            f"💬 **رسالة الشكوى:**\n{safe_text}"
        )
        
        from bot.keyboards.inline import get_ticket_admin_keyboard
        await message.bot.send_message(
            ADMIN_ID,
            admin_msg,
            reply_markup=get_ticket_admin_keyboard(ticket_number, user_id),
            parse_mode='Markdown'
        )
        
        # تسجيل الإجراء
        db.log_admin_action(ADMIN_ID, 'complaint_ticket_created', user_id, None, ticket_number)
        
        logger.info(f"User {user_id} created complaint ticket {ticket_number}")
        
    except Exception as e:
        logger.error(f"Error creating complaint ticket for user {user_id}: {e}")
        await message.answer(safe_get_text(user_id, "complaint_error"), parse_mode='Markdown')
    
    finally:
        await state.clear()


# ========== عرض تذاكر الشكاوى للأدمن ==========
@router.message(F.text == "📝 التذاكر")
async def show_complaint_tickets_admin(message: Message):
    """عرض تذاكر الشكاوى المفتوحة للأدمن"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        tickets = db.get_open_tickets_by_type('complaint')
        
        if not tickets:
            await message.answer("📭 **لا توجد تذاكر شكاوى مفتوحة**", parse_mode='Markdown')
            return
        
        text = "📝 **تذاكر الشكاوى المفتوحة**\n\n"
        for ticket in tickets[:15]:
            user_info = db.get_user_info(ticket.get('user_id', 0))
            user_name = user_info.get('name', 'غير معروف') if user_info else 'غير معروف'
            
            text += f"🎫 `{ticket.get('ticket_number', 'غير معروف')}`\n"
            text += f"👤 {user_name}\n"
            text += f"🆔 `{ticket.get('user_id', 'غير معروف')}`\n"
            created_at = ticket.get('created_at', 'غير معروف')
            text += f"📅 {created_at[:16] if created_at else 'غير معروف'}\n"
            text += "─" * 20 + "\n"
        
        if len(tickets) > 15:
            text += f"\n... و {len(tickets) - 15} تذكرة أخرى"
        
        await message.answer(text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error showing complaint tickets for admin: {e}")
        await message.answer("❌ حدث خطأ في عرض التذاكر", parse_mode='Markdown')


# ========== فتح شات مباشر ==========
@router.callback_query(F.data == "live_chat")
async def open_live_chat(callback: CallbackQuery, state: FSMContext):
    """فتح شات مباشر مع الدعم الفني"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await callback.answer(safe_get_text(user_id, "banned"), show_alert=True)
        return
    
    # التحقق من وجود شات نشط
    existing_chat = db.get_active_chat(user_id)
    if existing_chat:
        await callback.answer("⚠️ لديك محادثة نشطة بالفعل" if lang == 'ar' else "⚠️ You already have an active chat", show_alert=True)
        return
    
    # إنشاء تذكرة جديدة للمحادثة
    ticket_data = db.create_ticket(user_id, 'live_chat', 'فتح محادثة دعم مباشر')
    
    if not ticket_data or not ticket_data[0] or not ticket_data[1]:
        await callback.answer("❌ حدث خطأ أثناء فتح المحادثة" if lang == 'ar' else "❌ Error opening chat", show_alert=True)
        return
    
    ticket_number, ticket_id = ticket_data
    
    # إنشاء جلسة محادثة
    session_id = db.create_chat_session(user_id, None, ticket_id)
    
    if not session_id:
        await callback.answer("❌ حدث خطأ أثناء فتح المحادثة" if lang == 'ar' else "❌ Error opening chat", show_alert=True)
        return
    
    # تخزين معلومات الجلسة
    await state.update_data(
        ticket_id=ticket_id,
        ticket_number=ticket_number,
        session_id=session_id,
        in_chat=True
    )
    await state.set_state(ComplaintStates.LIVE_CHAT)
    
    # إرسال تأكيد للمستخدم
    live_chat_text = (
        "🔓 **تم فتح محادثة مباشرة مع الدعم الفني**\n\n"
        "✅ يمكنك كتابة رسالتك الآن\n"
        "🔚 اضغط على زر إنهاء المحادثة عند الانتهاء"
    )
    
    await callback.message.edit_text(
        live_chat_text if lang == 'ar' else (
            "🔓 **Live chat opened with support**\n\n"
            "✅ You can now send your message\n"
            "🔚 Press end chat button when finished"
        ),
        reply_markup=get_live_chat_keyboard(lang),
        parse_mode='Markdown'
    )
    
    # إشعار الأدمن
    user_info = db.get_user_info(user_id)
    now = datetime.now(TIMEZONE)
    
    user_name = user_info.get('name', 'غير معروف') if user_info else 'غير معروف'
    user_username = user_info.get('username') if user_info else None
    username_display = f"@{user_username}" if user_username else "لا يوجد"
    
    admin_msg = (
        f"💬 **محادثة مباشرة جديدة**\n\n"
        f"🎫 **رقم التذكرة:** `{ticket_number}`\n"
        f"👤 **الاسم:** {user_name}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"📝 **Username:** {username_display}\n"
        f"🗣️ **اللغة:** {lang}\n"
        f"📅 **التاريخ:** {now.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"المستخدم ينتظر الرد..."
    )
    
    from bot.keyboards.inline import get_admin_chat_keyboard
    await callback.bot.send_message(
        ADMIN_ID,
        admin_msg,
        reply_markup=get_admin_chat_keyboard(user_id, session_id),
        parse_mode='Markdown'
    )
    
    await callback.answer()
    logger.info(f"User {user_id} opened live chat {ticket_number}")


# ========== العودة إلى قائمة الشكاوى ==========
@router.callback_query(F.data == "back_to_complaints")
async def back_to_complaints(callback: CallbackQuery):
    """العودة إلى قائمة الشكاوى الرئيسية"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    title = safe_get_text(user_id, "complaint_title")
    
    try:
        from bot.keyboards.inline import get_complaints_keyboard
        await callback.message.edit_text(
            title,
            reply_markup=get_complaints_keyboard(lang),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error returning to complaints menu for user {user_id}: {e}")
        await callback.message.answer(title, parse_mode='Markdown')
    
    await callback.answer()


def register_support_handlers(dp):
    """تسجيل معالجات الدعم الفني والشكاوى"""
    dp.include_router(router)
    logger.info("تم تسجيل معالجات الدعم الفني والشكاوى بنجاح")
