from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
import logging
from bot.database.db import db  # تصحيح المسار
from bot.keyboards.inline import get_complaints_keyboard, get_live_chat_keyboard, get_back_keyboard, get_support_rating_keyboard
from bot.keyboards.reply import get_main_keyboard
from bot.states.complaint_states import ComplaintStates
from bot.config import ADMIN_ID, TIMEZONE
from bot.utils.helpers import is_rate_limited, sanitize_input

# إعداد logging
logger = logging.getLogger(__name__)

router = Router()

# تخزين مؤقت لتذاكر الشكاوى النشطة
active_complaint_sessions = {}


# ========== عرض قسم الشكاوى ==========
@router.message(F.text.in_({'📝 الشكاوى', '📝 Complaints'}))
async def show_complaints(message: Message):
    """عرض خيارات قسم الشكاوى"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    if db.is_user_banned(user_id):
        await message.answer("🚫 تم حظرك من البوت" if lang == 'ar' else "🚫 You are banned", parse_mode='Markdown')
        return
    
    await message.answer(
        "📝 **قسم الشكاوى**\n\nاختر نوع التواصل:" if lang == 'ar' else "📝 **Complaints Section**\n\nChoose communication type:",
        reply_markup=get_complaints_keyboard(lang),
        parse_mode='Markdown'
    )


# ========== 1. إنشاء تذكرة شكوى ==========
@router.callback_query(F.data == "create_ticket")
async def create_ticket(callback: CallbackQuery, state: FSMContext):
    """إنشاء تذكرة شكوى جديدة"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    if db.is_user_banned(user_id):
        await callback.answer("🚫 تم حظرك" if lang == 'ar' else "🚫 You are banned", show_alert=True)
        return
    
    # التحقق من معدل الطلبات
    try:
        if is_rate_limited(user_id, 'complaint_ticket', limit=2, window=600):
            await callback.answer("⚠️ أرسلت شكاوى كثيرة، انتظر قليلاً" if lang == 'ar' else "⚠️ Too many complaints, wait", show_alert=True)
            return
    except Exception as e:
        logger.error(f"Rate limit check error for user {user_id}: {e}")
    
    # التحقق من وجود تذكرة نشطة
    active_ticket = db.get_active_ticket_by_user(user_id)
    if active_ticket and active_ticket.get('ticket_type') == 'complaint':
        await callback.answer("⚠️ لديك تذكرة شكوى مفتوحة بالفعل" if lang == 'ar' else "⚠️ You already have an open complaint ticket", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📝 **اكتب شكواك أو استفسارك بالتفصيل:**" if lang == 'ar' else "📝 **Write your complaint or inquiry in detail:**",
        parse_mode='Markdown'
    )
    await state.set_state(ComplaintStates.WAITING_MESSAGE)
    await callback.answer()


@router.message(ComplaintStates.WAITING_MESSAGE)
async def receive_ticket_message(message: Message, state: FSMContext):
    """استقبال رسالة الشكوى وإنشاء التذكرة"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من وجود نص
    if not message.text:
        await message.answer(
            "⚠️ **الرجاء كتابة شكوى صالحة**" if lang == 'ar' else "⚠️ **Please write a valid complaint**",
            parse_mode='Markdown'
        )
        return
    
    complaint_text = sanitize_input(message.text, max_length=1000)
    if not complaint_text:
        await message.answer(
            "⚠️ **الرجاء كتابة شكوى صالحة**" if lang == 'ar' else "⚠️ **Please write a valid complaint**",
            parse_mode='Markdown'
        )
        return
    
    # إنشاء تذكرة جديدة
    ticket_data = db.create_ticket(user_id, 'complaint', complaint_text)
    
    if not ticket_data or not ticket_data[0] or not ticket_data[1]:
        await message.answer(
            "❌ **حدث خطأ أثناء إنشاء التذكرة، حاول مرة أخرى**" if lang == 'ar' else "❌ **Error creating ticket, try again**",
            parse_mode='Markdown'
        )
        await state.clear()
        return
    
    ticket_number, ticket_id = ticket_data
    
    # تحديث حالة FSM
    await state.update_data(
        ticket_id=ticket_id,
        ticket_number=ticket_number,
        in_chat=False
    )
    
    # إرسال تأكيد للمستخدم
    await message.answer(
        f"✅ **تم إنشاء تذكرة الشكوى بنجاح**\n\n"
        f"🎫 **رقم التذكرة:** `{ticket_number}`\n"
        f"📝 **شكواك:** {complaint_text[:200]}...\n\n"
        f"سيتم الرد عليك في أقرب وقت ممكن.\n"
        f"يمكنك متابعة التذكرة عبر قسم الشكاوى.",
        reply_markup=get_back_keyboard(lang),
        parse_mode='Markdown'
    )
    
    # إرسال إشعار للأدمن
    user_info = db.get_user_info(user_id)
    now = datetime.now(TIMEZONE)
    
    user_name = user_info.get('name', 'غير معروف') if user_info else 'غير معروف'
    user_username = user_info.get('username', 'لا يوجد') if user_info else 'لا يوجد'
    user_country = user_info.get('country', 'غير معروف') if user_info else 'غير معروف'
    
    admin_msg = (
        f"📝 **شكوى جديدة**\n\n"
        f"🎫 **رقم التذكرة:** `{ticket_number}`\n"
        f"👤 **الاسم:** {user_name}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"📝 **Username:** @{user_username}\n"
        f"🗣️ **اللغة:** {lang}\n"
        f"🌍 **الدولة:** {user_country}\n"
        f"📅 **التاريخ:** {now.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"💬 **رسالة الشكوى:**\n{complaint_text}\n\n"
        f"استخدم الأزرار أدناه للتحكم:"
    )
    
    from bot.keyboards.inline import get_ticket_admin_keyboard
    try:
        await message.bot.send_message(
            ADMIN_ID,
            admin_msg,
            reply_markup=get_ticket_admin_keyboard(ticket_number, user_id),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Failed to send admin notification for ticket {ticket_number}: {e}")
    
    # تسجيل إجراء
    try:
        db.log_admin_action(ADMIN_ID, 'complaint_ticket_created', user_id, None, ticket_number)
    except Exception as e:
        logger.error(f"Failed to log admin action: {e}")
    
    await state.clear()


# ========== 2. فتح شات مباشر (دعم فوري) ==========
@router.callback_query(F.data == "live_chat")
async def open_live_chat(callback: CallbackQuery, state: FSMContext):
    """فتح شات مباشر مع الدعم الفني"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    if db.is_user_banned(user_id):
        await callback.answer("🚫 تم حظرك" if lang == 'ar' else "🚫 You are banned", show_alert=True)
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
    await callback.message.edit_text(
        "🔓 **تم فتح محادثة مباشرة مع الدعم الفني**\n\n"
        "✅ يمكنك كتابة رسالتك الآن\n"
        "🔚 اضغط على زر إنهاء المحادثة عند الانتهاء",
        reply_markup=get_live_chat_keyboard(lang),
        parse_mode='Markdown'
    )
    
    # إشعار الأدمن
    user_info = db.get_user_info(user_id)
    now = datetime.now(TIMEZONE)
    
    user_name = user_info.get('name', 'غير معروف') if user_info else 'غير معروف'
    user_username = user_info.get('username', 'لا يوجد') if user_info else 'لا يوجد'
    
    admin_msg = (
        f"💬 **محادثة مباشرة جديدة**\n\n"
        f"🎫 **رقم التذكرة:** `{ticket_number}`\n"
        f"👤 **الاسم:** {user_name}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"📝 **Username:** @{user_username}\n"
        f"🗣️ **اللغة:** {lang}\n"
        f"📅 **التاريخ:** {now.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"المستخدم ينتظر الرد..."
    )
    
    from bot.keyboards.inline import get_admin_chat_keyboard
    try:
        await callback.bot.send_message(
            ADMIN_ID,
            admin_msg,
            reply_markup=get_admin_chat_keyboard(user_id, session_id),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Failed to send admin notification for live chat: {e}")
    
    await callback.answer()


# ========== استقبال رسائل المستخدم في الشات المباشر ==========
@router.message(ComplaintStates.LIVE_CHAT)
async def handle_live_chat_message(message: Message, state: FSMContext):
    """معالجة رسائل المستخدم في الشات المباشر وإرسالها للأدمن"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    data = await state.get_data()
    if not data.get('in_chat'):
        await message.answer(
            "⚠️ **لا توجد محادثة نشطة**\nاستخدم زر 'فتح شات مباشر' للبدء" if lang == 'ar' else "⚠️ **No active chat**\nUse 'Open Live Chat' to start",
            parse_mode='Markdown'
        )
        return
    
    ticket_id = data.get('ticket_id')
    if not ticket_id:
        await message.answer("❌ حدث خطأ، حاول مرة أخرى")
        await state.clear()
        return
    
    # التحقق من وجود نص
    message_text = message.text if message.text else "⚠️ المستخدم أرسل محتوى غير نصي"
    
    # حفظ الرسالة
    try:
        db.add_ticket_message(ticket_id, user_id, message_text)
    except Exception as e:
        logger.error(f"Failed to save ticket message: {e}")
    
    # إرسال تأكيد للمستخدم
    await message.answer("✅ **تم إرسال رسالتك إلى الدعم**", parse_mode='Markdown')
    
    # إرسال الرسالة للأدمن
    admin_msg = (
        f"💬 **رسالة جديدة من المستخدم**\n\n"
        f"🆔 **المستخدم:** {user_id}\n"
        f"🎫 **التذكرة:** {data.get('ticket_number', 'غير معروف')}\n"
        f"💬 **الرسالة:**\n{message_text}\n\n"
        f"⏰ {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    from bot.keyboards.inline import get_admin_reply_keyboard
    try:
        await message.bot.send_message(
            ADMIN_ID,
            admin_msg,
            reply_markup=get_admin_reply_keyboard(user_id, ticket_id),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Failed to forward message to admin: {e}")


# ========== رد الأدمن على المستخدم ==========
@router.callback_query(F.data.startswith("admin_reply_complaint_"))
async def admin_reply_start(callback: CallbackQuery, state: FSMContext):
    """بدء رد الأدمن على المستخدم"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ غير مصرح", show_alert=True)
        return
    
    parts = callback.data.split('_')
    
    if len(parts) < 5:
        await callback.answer("❌ بيانات غير صالحة", show_alert=True)
        return
    
    try:
        user_id = int(parts[3])
        ticket_id = int(parts[4])
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing admin_reply_complaint callback: {callback.data} - {e}")
        await callback.answer("❌ حدث خطأ", show_alert=True)
        return
    
    await state.update_data(
        reply_to_user=user_id,
        reply_ticket_id=ticket_id
    )
    await state.set_state(ComplaintStates.ADMIN_REPLYING)
    
    await callback.message.answer(f"💬 **اكتب ردك للمستخدم {user_id}:**", parse_mode='Markdown')
    await callback.answer()


@router.message(ComplaintStates.ADMIN_REPLYING)
async def send_admin_reply(message: Message, state: FSMContext):
    """إرسال رد الأدمن للمستخدم"""
    if message.from_user.id != ADMIN_ID:
        return
    
    # التحقق من وجود نص
    if not message.text:
        await message.answer("❌ **الرجاء كتابة رد صالح**", parse_mode='Markdown')
        return
    
    data = await state.get_data()
    user_id = data.get('reply_to_user')
    ticket_id = data.get('reply_ticket_id')
    
    if not user_id or not ticket_id:
        await message.answer("❌ حدث خطأ، حاول مرة أخرى")
        await state.clear()
        return
    
    # حفظ رسالة الأدمن
    try:
        db.add_ticket_message(ticket_id, ADMIN_ID, message.text)
    except Exception as e:
        logger.error(f"Failed to save admin message: {e}")
    
    # إرسال الرد للمستخدم
    lang = db.get_user_language(user_id)
    
    try:
        await message.bot.send_message(
            user_id,
            f"📨 **رد من الدعم الفني:**\n\n{message.text}",
            reply_markup=get_live_chat_keyboard(lang),
            parse_mode='Markdown'
        )
        
        await message.answer(f"✅ **تم إرسال الرد للمستخدم {user_id}**", parse_mode='Markdown')
        
        # تحديث حالة التذكرة
        try:
            db.update_ticket_status_by_id(ticket_id, 'in_progress')
        except Exception as e:
            logger.error(f"Failed to update ticket status: {e}")
    except Exception as e:
        logger.error(f"Failed to send admin reply to {user_id}: {e}")
        await message.answer(f"❌ فشل إرسال الرد: {e}", parse_mode='Markdown')
    
    await state.clear()


# ========== إنهاء المحادثة من المستخدم ==========
@router.callback_query(F.data == "end_chat")
async def end_chat_user(callback: CallbackQuery, state: FSMContext):
    """إنهاء المحادثة من قبل المستخدم"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    # الحصول على الجلسة النشطة
    chat_session = db.get_active_chat(user_id)
    
    if chat_session and chat_session.get('id'):
        try:
            # إغلاق الجلسة
            db.close_chat_session(chat_session['id'])
            
            # تحديث حالة التذكرة
            if chat_session.get('ticket_number'):
                db.update_ticket_status(chat_session['ticket_number'], 'closed')
            
            # إشعار الأدمن
            await callback.bot.send_message(
                ADMIN_ID,
                f"🔒 **المستخدم {user_id} أنهى المحادثة**\n📅 {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error ending chat for user {user_id}: {e}")
    
    # إرسال رسالة شكر
    try:
        await callback.message.edit_text(
            "🙏 **شكراً لتواصلك معنا**\n\nلا تتردد في الاتصال بنا مرة أخرى",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error editing message for user {user_id}: {e}")
    
    # عرض القائمة الرئيسية
    try:
        await callback.message.answer(
            "اهلاً بك في متجر Shop Crowns 🎉🎁\nاختر من القائمة 👇",
            reply_markup=get_main_keyboard(lang)
        )
    except Exception as e:
        logger.error(f"Error sending main keyboard to user {user_id}: {e}")
    
    # مسح الحالة
    await state.clear()
    await callback.answer()


# ========== إنهاء المحادثة من الأدمن ==========
@router.callback_query(F.data.startswith("admin_end_chat_complaint_"))
async def admin_end_chat(callback: CallbackQuery, state: FSMContext):
    """إنهاء المحادثة من قبل الأدمن"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ غير مصرح", show_alert=True)
        return
    
    parts = callback.data.split('_')
    
    if len(parts) < 6:
        await callback.answer("❌ بيانات غير صالحة", show_alert=True)
        return
    
    try:
        user_id = int(parts[4])
        chat_session_id = int(parts[5])
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing admin_end_chat_complaint callback: {callback.data} - {e}")
        await callback.answer("❌ حدث خطأ", show_alert=True)
        return
    
    lang = db.get_user_language(user_id)
    
    # إغلاق الجلسة
    try:
        db.close_chat_session(chat_session_id)
    except Exception as e:
        logger.error(f"Failed to close chat session {chat_session_id}: {e}")
    
    # إرسال رسالة شكر للمستخدم
    try:
        await callback.bot.send_message(
            user_id,
            "🙏 **تم إنهاء المحادثة من قبل الدعم**\n\nشكراً لتواصلك معنا\nلا تتردد في الاتصال بنا مرة أخرى",
            parse_mode='Markdown'
        )
        
        # عرض القائمة الرئيسية للمستخدم
        await callback.bot.send_message(
            user_id,
            "اهلاً بك في متجر Shop Crowns 🎉🎁\nاختر من القائمة 👇",
            reply_markup=get_main_keyboard(lang)
        )
    except Exception as e:
        logger.error(f"Failed to send end chat message to user {user_id}: {e}")
    
    await callback.message.edit_text(f"✅ **تم إنهاء المحادثة مع المستخدم {user_id}**", parse_mode='Markdown')
    await callback.answer()


# ========== عرض التذاكر ==========
@router.message(F.text == "📝 التذاكر")
async def show_tickets_admin(message: Message):
    """عرض تذاكر الشكاوى للأدمن"""
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
            text += f"🎫 `{ticket.get('ticket_number', 'غير معروف')}`\n"
            text += f"👤 {user_info.get('name', 'غير معروف') if user_info else 'غير معروف'}\n"
            text += f"🆔 `{ticket.get('user_id', 'غير معروف')}`\n"
            created_at = ticket.get('created_at', 'غير معروف')
            text += f"📅 {created_at[:16] if created_at else 'غير معروف'}\n"
            text += "─" * 20 + "\n"
        
        if len(tickets) > 15:
            text += f"\n... و {len(tickets) - 15} تذكرة أخرى"
        
        await message.answer(text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error showing tickets for admin: {e}")
        await message.answer("❌ حدث خطأ في عرض التذاكر", parse_mode='Markdown')


# ========== رد على تذكرة معينة ==========
@router.callback_query(F.data.startswith("reply_ticket_"))
async def reply_to_ticket(callback: CallbackQuery, state: FSMContext):
    """الرد على تذكرة معينة"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ غير مصرح", show_alert=True)
        return
    
    parts = callback.data.split('_')
    
    if len(parts) < 3:
        await callback.answer("❌ بيانات غير صالحة", show_alert=True)
        return
    
    ticket_number = parts[2]
    
    # الحصول على معلومات التذكرة
    ticket = db.get_ticket_by_number(ticket_number)
    if not ticket:
        await callback.answer("التذكرة غير موجودة", show_alert=True)
        return
    
    await state.update_data(
        reply_ticket_number=ticket_number,
        reply_ticket_user=ticket.get('user_id')
    )
    await state.set_state(ComplaintStates.ADMIN_REPLYING)
    
    await callback.message.answer(f"💬 **اكتب ردك على التذكرة {ticket_number}:**", parse_mode='Markdown')
    await callback.answer()


def register_complaints_handlers(dp):
    """تسجيل معالجات الشكاوى"""
    dp.include_router(router)
    logger.info("تم تسجيل معالجات الشكاوى بنجاح")
