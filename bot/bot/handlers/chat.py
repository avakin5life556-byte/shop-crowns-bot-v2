from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
import asyncio
import pytz
from database import db
from keyboards.inline import get_live_chat_keyboard, get_end_chat_keyboard, get_admin_chat_keyboard
from states.chat_states import ChatStates
from config import ADMIN_ID, TIMEZONE, CHAT_TIMEOUT_MINUTES

router = Router()

# تخزين مؤقت للمؤقتات النشطة
active_timeouts = {}


async def start_chat_timeout(chat_session_id: int, user_id: int, bot):
    """بدء مؤقت للمحادثة (20 دقيقة)"""
    
    async def timeout_callback():
        if chat_session_id in active_timeouts:
            # الحصول على معلومات الجلسة
            session = db.get_chat_session(chat_session_id)
            if session and session['status'] == 'active':
                # تحديث حالة التذكرة
                db.update_ticket_status(session['ticket_number'], 'timeout')
                
                # إرسال رسالة للمستخدم
                lang = db.get_user_language(user_id)
                timeout_msg = "⏰ **لم يتم قبول طلبك حالياً بسبب ضغط الطلبات**" if lang == 'ar' else "⏰ **Your request has timed out due to high load**"
                await bot.send_message(user_id, timeout_msg, parse_mode='Markdown')
                
                # إغلاق الجلسة
                db.close_chat_session(chat_session_id)
                
                # إشعار الأدمن
                await bot.send_message(
                    ADMIN_ID,
                    f"⏰ **انتهت مهلة المحادثة**\n👤 المستخدم: {user_id}\n📅 {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')}",
                    parse_mode='Markdown'
                )
                
                # حذف المؤقت
                del active_timeouts[chat_session_id]
    
    # تخزين المؤقت
    task = asyncio.create_task(timeout_callback())
    active_timeouts[chat_session_id] = {
        'task': task,
        'user_id': user_id,
        'expires_at': datetime.now(TIMEZONE) + timedelta(minutes=CHAT_TIMEOUT_MINUTES)
    }


async def cancel_chat_timeout(chat_session_id: int):
    """إلغاء مؤقت المحادثة"""
    if chat_session_id in active_timeouts:
        active_timeouts[chat_session_id]['task'].cancel()
        del active_timeouts[chat_session_id]


# ========== فتح محادثة جديدة ==========
@router.callback_query(F.data == "open_chat")
async def open_chat(callback: CallbackQuery, state: FSMContext):
    """فتح محادثة جديدة من المستخدم"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من وجود محادثة نشطة
    existing_session = db.get_active_chat(user_id)
    if existing_session:
        await callback.answer("⚠️ لديك محادثة مفتوحة بالفعل", show_alert=True)
        return
    
    # إنشاء تذكرة جديدة
    ticket_number, ticket_id = db.create_ticket(user_id, 'live_chat', 'فتح محادثة دعم مباشر')
    
    # إنشاء جلسة محادثة
    session_id = db.create_chat_session(user_id, None, ticket_id)
    
    # بدء المؤقت
    await start_chat_timeout(session_id, user_id, callback.bot)
    
    # تحديث حالة FSM
    await state.update_data(
        chat_session_id=session_id,
        chat_ticket_id=ticket_id,
        chat_ticket_number=ticket_number,
        in_chat=True
    )
    await state.set_state(ChatStates.ACTIVE)
    
    # إرسال تأكيد للمستخدم
    await callback.message.edit_text(
        "🔓 **تم فتح محادثة مع الدعم الفني**\n\n"
        "✅ يمكنك كتابة رسالتك الآن\n"
        "⏰ المهلة: 20 دقيقة\n"
        "🔚 اضغط على زر إنهاء المحادثة عند الانتهاء",
        reply_markup=get_live_chat_keyboard(lang),
        parse_mode='Markdown'
    )
    
    # إشعار الأدمن
    user_info = db.get_user_info(user_id)
    admin_msg = (
        f"💬 **محادثة جديدة**\n\n"
        f"🎫 **رقم التذكرة:** {ticket_number}\n"
        f"👤 **المستخدم:** {user_info['name'] if user_info else 'غير معروف'}\n"
        f"🆔 **المعرف:** {user_id}\n"
        f"📝 **اليوزر:** @{user_info['username'] if user_info else 'لا يوجد'}\n"
        f"📅 **الوقت:** {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    admin_markup = types.InlineKeyboardMarkup(row_width=2)
    admin_markup.add(
        types.InlineKeyboardButton(text="💬 رد", callback_data=f"admin_reply_{user_id}_{ticket_id}"),
        types.InlineKeyboardButton(text="🔚 إنهاء", callback_data=f"admin_end_chat_{user_id}_{session_id}")
    )
    
    await callback.bot.send_message(ADMIN_ID, admin_msg, reply_markup=admin_markup, parse_mode='Markdown')
    await callback.answer()


# ========== استقبال رسائل المستخدم في المحادثة ==========
@router.message(ChatStates.ACTIVE)
async def handle_user_message(message: Message, state: FSMContext):
    """معالجة رسائل المستخدم وإرسالها للأدمن"""
    user_id = message.from_user.id
    data = await state.get_data()
    
    if not data.get('in_chat'):
        return
    
    chat_session_id = data.get('chat_session_id')
    ticket_id = data.get('chat_ticket_id')
    
    if not chat_session_id or not ticket_id:
        return
    
    # تحديث المؤقت (إعادة تعيين المهلة)
    await cancel_chat_timeout(chat_session_id)
    await start_chat_timeout(chat_session_id, user_id, message.bot)
    
    # حفظ رسالة المستخدم
    db.add_ticket_message(ticket_id, user_id, message.text)
    
    # إرسال للمستخدم تأكيد
    await message.answer("✅ **تم إرسال رسالتك إلى الدعم**", parse_mode='Markdown')
    
    # إرسال رسالة للأدمن
    admin_msg = (
        f"💬 **رسالة جديدة من المستخدم**\n\n"
        f"🆔 **المعرف:** {user_id}\n"
        f"💬 **الرسالة:**\n{message.text}\n\n"
        f"⏰ {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    admin_markup = types.InlineKeyboardMarkup(row_width=2)
    admin_markup.add(
        types.InlineKeyboardButton(text="💬 رد", callback_data=f"admin_reply_{user_id}_{ticket_id}"),
        types.InlineKeyboardButton(text="🔚 إنهاء", callback_data=f"admin_end_chat_{user_id}_{chat_session_id}")
    )
    
    await message.bot.send_message(ADMIN_ID, admin_msg, reply_markup=admin_markup, parse_mode='Markdown')


# ========== رد الأدمن على المستخدم ==========
@router.callback_query(F.data.startswith("admin_reply_"))
async def admin_reply_start(callback: CallbackQuery, state: FSMContext):
    """بدء رد الأدمن على المستخدم"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ غير مصرح", show_alert=True)
        return
    
    parts = callback.data.split('_')
    user_id = int(parts[2])
    ticket_id = int(parts[3])
    
    await state.update_data(
        reply_to_user=user_id,
        reply_ticket_id=ticket_id
    )
    await state.set_state(ChatStates.ADMIN_REPLYING)
    
    await callback.message.answer(f"💬 **اكتب ردك للمستخدم {user_id}:**", parse_mode='Markdown')
    await callback.answer()


@router.message(ChatStates.ADMIN_REPLYING)
async def send_admin_reply(message: Message, state: FSMContext):
    """إرسال رد الأدمن للمستخدم"""
    if message.from_user.id != ADMIN_ID:
        return
    
    data = await state.get_data()
    user_id = data.get('reply_to_user')
    ticket_id = data.get('reply_ticket_id')
    
    if not user_id or not ticket_id:
        await message.answer("❌ حدث خطأ، حاول مرة أخرى")
        await state.clear()
        return
    
    # حفظ رسالة الأدمن
    db.add_ticket_message(ticket_id, ADMIN_ID, message.text)
    
    # إرسال الرد للمستخدم
    lang = db.get_user_language(user_id)
    
    await message.bot.send_message(
        user_id,
        f"📨 **رد من الدعم الفني:**\n\n{message.text}",
        reply_markup=get_live_chat_keyboard(lang),
        parse_mode='Markdown'
    )
    
    await message.answer(f"✅ **تم إرسال الرد للمستخدم {user_id}**", parse_mode='Markdown')
    
    # تحديث المؤقت للمستخدم (عند الرد، يتم تحديث المهلة)
    chat_session = db.get_active_chat(user_id)
    if chat_session:
        await cancel_chat_timeout(chat_session['id'])
        await start_chat_timeout(chat_session['id'], user_id, message.bot)
    
    await state.clear()


# ========== إنهاء المحادثة من المستخدم ==========
@router.callback_query(F.data == "end_chat")
async def end_chat_user(callback: CallbackQuery, state: FSMContext):
    """إنهاء المحادثة من قبل المستخدم"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    # الحصول على الجلسة النشطة
    chat_session = db.get_active_chat(user_id)
    
    if chat_session:
        # إلغاء المؤقت
        await cancel_chat_timeout(chat_session['id'])
        
        # إغلاق الجلسة
        db.close_chat_session(chat_session['id'])
        
        # تحديث حالة التذكرة
        db.update_ticket_status(chat_session['ticket_number'], 'closed')
        
        # إشعار الأدمن
        await callback.bot.send_message(
            ADMIN_ID,
            f"🔒 **المستخدم {user_id} أنهى المحادثة**\n📅 {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode='Markdown'
        )
    
    # مسح حالة FSM
    await state.clear()
    
    # إرسال رسالة شكر للمستخدم
    await callback.message.edit_text(
        "🙏 **شكراً لتواصلك معنا**\n\nلا تتردد في الاتصال بنا مرة أخرى",
        parse_mode='Markdown'
    )
    
    # إظهار القائمة الرئيسية
    from keyboards.reply import get_main_keyboard
    await callback.message.answer(
        "اهلاً بك في متجر Shop Crowns 🎉🎁\nاختر من القائمة 👇",
        reply_markup=get_main_keyboard(lang)
    )
    
    await callback.answer()


# ========== إنهاء المحادثة من الأدمن ==========
@router.callback_query(F.data.startswith("admin_end_chat_"))
async def admin_end_chat(callback: CallbackQuery, state: FSMContext):
    """إنهاء المحادثة من قبل الأدمن"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ غير مصرح", show_alert=True)
        return
    
    parts = callback.data.split('_')
    user_id = int(parts[3])
    chat_session_id = int(parts[4])
    
    lang = db.get_user_language(user_id)
    
    # إلغاء المؤقت
    await cancel_chat_timeout(chat_session_id)
    
    # إغلاق الجلسة
    db.close_chat_session(chat_session_id)
    
    # إرسال رسالة شكر للمستخدم
    await callback.bot.send_message(
        user_id,
        "🙏 **تم إنهاء المحادثة من قبل الدعم**\n\nشكراً لتواصلك معنا\nلا تتردد في الاتصال بنا مرة أخرى",
        parse_mode='Markdown'
    )
    
    # إظهار القائمة الرئيسية للمستخدم
    from keyboards.reply import get_main_keyboard
    await callback.bot.send_message(
        user_id,
        "اهلاً بك في متجر Shop Crowns 🎉🎁\nاختر من القائمة 👇",
        reply_markup=get_main_keyboard(lang)
    )
    
    await callback.message.edit_text(f"✅ **تم إنهاء المحادثة مع المستخدم {user_id}**", parse_mode='Markdown')
    await callback.answer()


# ========== Timeout التحقق الدوري ==========
async def check_timeouts_periodically():
    """التحقق الدوري من انتهاء مهلات المحادثات"""
    while True:
        try:
            now = datetime.now(TIMEZONE)
            expired = []
            
            for session_id, data in active_timeouts.items():
                if now >= data['expires_at']:
                    expired.append(session_id)
            
            for session_id in expired:
                if session_id in active_timeouts:
                    # تنفيذ timeout
                    task = active_timeouts[session_id]['task']
                    if not task.done():
                        # سيتم تنفيذ timeout_callback
                        pass
            
            await asyncio.sleep(60)  # التحقق كل دقيقة
        except Exception as e:
            print(f"Timeout check error: {e}")
            await asyncio.sleep(60)


def register_chat_handlers(dp):
    """تسجيل معالجات الدردشة"""
    dp.include_router(router)