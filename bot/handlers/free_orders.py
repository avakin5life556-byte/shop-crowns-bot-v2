from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
import json
import logging
from bot.database.db import db  # تصحيح المسار
from bot.keyboards.inline import (
    get_yes_no_keyboard, 
    get_continue_keyboard, 
    get_free_orders_keyboard, 
    get_more_options_keyboard,
    get_back_keyboard
)
from bot.keyboards.reply import get_main_keyboard
from bot.states.order_states import ChangeNameStates, ChangePhotoStates
from bot.config import ADMIN_ID, TIMEZONE
from bot.utils.helpers import validate_email, sanitize_input, is_rate_limited
from bot.utils.translations import get_text

# إعداد logging
logger = logging.getLogger(__name__)

router = Router()

# تخزين مؤقت لبيانات الطلب
temp_order_data = {}


def safe_get_text(user_id: int, key: str, default_ar: str = "", default_en: str = "") -> str:
    """دالة آمنة للحصول على النصوص مع fallback"""
    try:
        text = get_text(user_id, key)
        if text and isinstance(text, str) and len(text) > 0:
            return text
    except Exception as e:
        logger.error(f"Error getting text for key {key}: {e}")
    
    # Fallback بناءً على لغة المستخدم
    lang = db.get_user_language(user_id)
    return default_ar if lang == 'ar' else default_en


# ========== القائمة الرئيسية للطلبات المجانية ==========
@router.message(F.text.in_({'🎁 الطلبات المجانية', '🎁 Free Requests'}))
async def show_free_orders(message: Message):
    """عرض قائمة الطلبات المجانية"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    if db.is_user_banned(user_id):
        await message.answer(get_text(user_id, "messages.banned"), parse_mode='Markdown')
        return
    
    title = safe_get_text(
        user_id, 
        "free_orders_title",
        "🎁 **الطلبات المجانية**\n\nاختر الخدمة التي تريدها:",
        "🎁 **Free Requests**\n\nChoose the service you want:"
    )
    
    await message.answer(
        title,
        reply_markup=get_free_orders_keyboard(lang),
        parse_mode='Markdown'
    )


# ========== 1. تغيير الاسم ==========
@router.callback_query(F.data == "change_name")
async def change_name_start(callback: CallbackQuery, state: FSMContext):
    """بداية عملية تغيير الاسم - سؤال عن الـ 5000 كوينز"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    if db.is_user_banned(user_id):
        await callback.answer(get_text(user_id, "messages.banned"), show_alert=True)
        return
    
    # التحقق من معدل الطلبات
    try:
        if is_rate_limited(user_id, 'change_name', limit=3, window=300):
            await callback.answer(get_text(user_id, "messages.rate_limited"), show_alert=True)
            return
    except Exception as e:
        logger.error(f"Rate limit error for user {user_id}: {e}")
    
    balance_text = safe_get_text(
        user_id,
        "balance_q",
        "💰 **هل لديك 5000 كوينز في حسابك؟**",
        "💰 **Do you have 5000 coins in your account?**"
    )
    
    await callback.message.edit_text(
        balance_text,
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
    
    send_name_text = safe_get_text(
        user_id,
        "send_name",
        "📝 **أرسل الاسم الجديد:**",
        "📝 **Send your new name:**"
    )
    
    await callback.message.edit_text(
        send_name_text,
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
    
    no_balance_text = safe_get_text(
        user_id,
        "no_balance",
        "⚠️ **عذراً، لا يمكنك تغيير الاسم بدون رصيد كافٍ**",
        "⚠️ **Sorry, you cannot change your name without sufficient balance**"
    )
    
    await callback.message.edit_text(
        no_balance_text,
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
        invalid_text = safe_get_text(
            user_id,
            "invalid_name",
            "⚠️ **الاسم غير صالح، حاول مرة أخرى**",
            "⚠️ **Invalid name, try again**"
        )
        await message.answer(invalid_text, parse_mode='Markdown')
        return
    
    new_name = sanitize_input(message.text, max_length=50)
    if not new_name:
        invalid_text = safe_get_text(
            user_id,
            "invalid_name",
            "⚠️ **الاسم غير صالح، حاول مرة أخرى**",
            "⚠️ **Invalid name, try again**"
        )
        await message.answer(invalid_text, parse_mode='Markdown')
        return
    
    await state.update_data(new_name=new_name)
    
    ask_email_text = safe_get_text(
        user_id,
        "ask_email",
        "📧 **أرسل بريدك الإلكتروني:**",
        "📧 **Send your email:**"
    )
    
    await message.answer(ask_email_text, parse_mode='Markdown')
    await state.set_state(ChangeNameStates.WAITING_EMAIL)


@router.message(ChangeNameStates.WAITING_EMAIL)
async def change_name_get_email(message: Message, state: FSMContext):
    """استقبال البريد الإلكتروني"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من وجود نص
    if not message.text:
        invalid_email_text = safe_get_text(
            user_id,
            "invalid_email",
            "⚠️ **البريد الإلكتروني غير صالح، حاول مرة أخرى**",
            "⚠️ **Invalid email, try again**"
        )
        await message.answer(invalid_email_text, parse_mode='Markdown')
        return
    
    email = sanitize_input(message.text, max_length=100)
    if not validate_email(email):
        invalid_email_text = safe_get_text(
            user_id,
            "invalid_email",
            "⚠️ **البريد الإلكتروني غير صالح، حاول مرة أخرى**",
            "⚠️ **Invalid email, try again**"
        )
        await message.answer(invalid_email_text, parse_mode='Markdown')
        return
    
    await state.update_data(email=email)
    
    ask_password_text = safe_get_text(
        user_id,
        "ask_password",
        "🔑 **أرسل كلمة المرور:**",
        "🔑 **Send your password:**"
    )
    
    await message.answer(ask_password_text, parse_mode='Markdown')
    await state.set_state(ChangeNameStates.WAITING_PASSWORD)


@router.message(ChangeNameStates.WAITING_PASSWORD)
async def change_name_get_password(message: Message, state: FSMContext):
    """استقبال كلمة المرور وإنشاء الطلب"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من وجود نص
    if not message.text:
        invalid_password_text = safe_get_text(
            user_id,
            "invalid_password",
            "⚠️ **كلمة المرور غير صالحة، حاول مرة أخرى**",
            "⚠️ **Invalid password, try again**"
        )
        await message.answer(invalid_password_text, parse_mode='Markdown')
        return
    
    password = sanitize_input(message.text, max_length=100)
    if not password:
        invalid_password_text = safe_get_text(
            user_id,
            "invalid_password",
            "⚠️ **كلمة المرور غير صالحة، حاول مرة أخرى**",
            "⚠️ **Invalid password, try again**"
        )
        await message.answer(invalid_password_text, parse_mode='Markdown')
        return
    
    # الحصول على البيانات من FSM
    data = await state.get_data()
    new_name = data.get('new_name')
    email = data.get('email')
    
    if not new_name or not email:
        error_text = safe_get_text(
            user_id,
            "messages.error",
            "❌ **حدث خطأ، حاول مرة أخرى**",
            "❌ **An error occurred, try again**"
        )
        await message.answer(error_text, reply_markup=get_main_keyboard(lang), parse_mode='Markdown')
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
        error_text = safe_get_text(
            user_id,
            "messages.error",
            "❌ **حدث خطأ في إنشاء الطلب، حاول مرة أخرى**",
            "❌ **Error creating order, try again**"
        )
        await message.answer(error_text, reply_markup=get_main_keyboard(lang), parse_mode='Markdown')
        await state.clear()
        return
    
    # إرسال تأكيد للمستخدم
    processing_text = safe_get_text(
        user_id,
        "processing",
        "⏳ **جاري معالجة طلبك...**",
        "⏳ **Processing your request...**"
    )
    
    await message.answer(processing_text, reply_markup=get_main_keyboard(lang), parse_mode='Markdown')
    
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
    if user_id in temp_order_data:
        del temp_order_data[user_id]


# ========== 2. تغيير الصورة ==========
@router.callback_query(F.data == "change_photo")
async def change_photo_start(callback: CallbackQuery, state: FSMContext):
    """بداية عملية تغيير الصورة"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    if db.is_user_banned(user_id):
        await callback.answer(get_text(user_id, "messages.banned"), show_alert=True)
        return
    
    try:
        if is_rate_limited(user_id, 'change_photo', limit=3, window=300):
            await callback.answer(get_text(user_id, "messages.rate_limited"), show_alert=True)
            return
    except Exception as e:
        logger.error(f"Rate limit error for user {user_id}: {e}")
    
    change_photo_text = safe_get_text(
        user_id,
        "change_photo_q",
        "🖼 **هل تريد تغيير صورتك؟**",
        "🖼 **Do you want to change your photo?**"
    )
    
    await callback.message.edit_text(
        change_photo_text,
        reply_markup=get_yes_no_keyboard(),
        parse_mode='Markdown'
    )
    await state.set_state(ChangePhotoStates.CHECK_BALANCE)
    await callback.answer()


@router.callback_query(F.data == "yes", ChangePhotoStates.CHECK_BALANCE)
async def change_photo_yes(callback: CallbackQuery, state: FSMContext):
    """المستخدم يريد تغيير الصورة - طلب الصورة"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    send_photo_text = safe_get_text(
        user_id,
        "send_photo",
        "📸 **أرسل الصورة الجديدة:**",
        "📸 **Send your new photo:**"
    )
    
    await callback.message.edit_text(
        send_photo_text,
        parse_mode='Markdown'
    )
    await state.set_state(ChangePhotoStates.WAITING_PHOTO)
    await callback.answer()


@router.callback_query(F.data == "no", ChangePhotoStates.CHECK_BALANCE)
async def change_photo_no(callback: CallbackQuery, state: FSMContext):
    """المستخدم لا يريد تغيير الصورة"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    await state.clear()
    
    cancelled_text = safe_get_text(
        user_id,
        "cancelled",
        "❌ **تم الإلغاء**",
        "❌ **Cancelled**"
    )
    
    await callback.message.edit_text(
        cancelled_text,
        reply_markup=get_back_keyboard(lang),
        parse_mode='Markdown'
    )
    await callback.answer()


@router.message(ChangePhotoStates.WAITING_PHOTO, F.photo)
async def change_photo_get_photo(message: Message, state: FSMContext):
    """استقبال الصورة"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    photo = message.photo[-1]
    photo_id = photo.file_id
    
    await state.update_data(photo_id=photo_id)
    
    ask_email_text = safe_get_text(
        user_id,
        "ask_email",
        "📧 **أرسل بريدك الإلكتروني:**",
        "📧 **Send your email:**"
    )
    
    await message.answer(ask_email_text, parse_mode='Markdown')
    await state.set_state(ChangePhotoStates.WAITING_EMAIL)


@router.message(ChangePhotoStates.WAITING_PHOTO)
async def change_photo_invalid(message: Message, state: FSMContext):
    """الرسالة ليست صورة"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    invalid_photo_text = safe_get_text(
        user_id,
        "invalid_photo",
        "⚠️ **الرجاء إرسال صورة صالحة**",
        "⚠️ **Please send a valid photo**"
    )
    
    await message.answer(invalid_photo_text, parse_mode='Markdown')


@router.message(ChangePhotoStates.WAITING_EMAIL)
async def change_photo_get_email(message: Message, state: FSMContext):
    """استقبال البريد الإلكتروني لتغيير الصورة"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من وجود نص
    if not message.text:
        invalid_email_text = safe_get_text(
            user_id,
            "invalid_email",
            "⚠️ **البريد الإلكتروني غير صالح، حاول مرة أخرى**",
            "⚠️ **Invalid email, try again**"
        )
        await message.answer(invalid_email_text, parse_mode='Markdown')
        return
    
    email = sanitize_input(message.text, max_length=100)
    if not validate_email(email):
        invalid_email_text = safe_get_text(
            user_id,
            "invalid_email",
            "⚠️ **البريد الإلكتروني غير صالح، حاول مرة أخرى**",
            "⚠️ **Invalid email, try again**"
        )
        await message.answer(invalid_email_text, parse_mode='Markdown')
        return
    
    await state.update_data(email=email)
    
    ask_password_text = safe_get_text(
        user_id,
        "ask_password",
        "🔑 **أرسل كلمة المرور:**",
        "🔑 **Send your password:**"
    )
    
    await message.answer(ask_password_text, parse_mode='Markdown')
    await state.set_state(ChangePhotoStates.WAITING_PASSWORD)


@router.message(ChangePhotoStates.WAITING_PASSWORD)
async def change_photo_get_password(message: Message, state: FSMContext):
    """استقبال كلمة المرور وإنشاء الطلب"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من وجود نص
    if not message.text:
        invalid_password_text = safe_get_text(
            user_id,
            "invalid_password",
            "⚠️ **كلمة المرور غير صالحة، حاول مرة أخرى**",
            "⚠️ **Invalid password, try again**"
        )
        await message.answer(invalid_password_text, parse_mode='Markdown')
        return
    
    password = sanitize_input(message.text, max_length=100)
    if not password:
        invalid_password_text = safe_get_text(
            user_id,
            "invalid_password",
            "⚠️ **كلمة المرور غير صالحة، حاول مرة أخرى**",
            "⚠️ **Invalid password, try again**"
        )
        await message.answer(invalid_password_text, parse_mode='Markdown')
        return
    
    # الحصول على البيانات من FSM
    data = await state.get_data()
    photo_id = data.get('photo_id')
    email = data.get('email')
    
    if not photo_id or not email:
        error_text = safe_get_text(
            user_id,
            "messages.error",
            "❌ **حدث خطأ، حاول مرة أخرى**",
            "❌ **An error occurred, try again**"
        )
        await message.answer(error_text, reply_markup=get_main_keyboard(lang), parse_mode='Markdown')
        await state.clear()
        return
    
    # إنشاء الطلب
    order_data = json.dumps({
        'type': 'change_photo',
        'photo_id': photo_id,
        'email': email,
        'password': password
    }, ensure_ascii=False)
    
    order_number = db.create_order(user_id, 'تغيير الصورة', order_data)
    
    if not order_number:
        error_text = safe_get_text(
            user_id,
            "messages.error",
            "❌ **حدث خطأ في إنشاء الطلب، حاول مرة أخرى**",
            "❌ **Error creating order, try again**"
        )
        await message.answer(error_text, reply_markup=get_main_keyboard(lang), parse_mode='Markdown')
        await state.clear()
        return
    
    # إرسال تأكيد للمستخدم
    processing_text = safe_get_text(
        user_id,
        "processing",
        "⏳ **جاري معالجة طلبك...**",
        "⏳ **Processing your request...**"
    )
    
    await message.answer(processing_text, reply_markup=get_main_keyboard(lang), parse_mode='Markdown')
    
    # إرسال الطلب للأدمن
    user_info = db.get_user_info(user_id)
    now = datetime.now(TIMEZONE)
    
    user_name = user_info.get('name', 'غير معروف') if user_info else 'غير معروف'
    user_username = user_info.get('username', 'لا يوجد') if user_info else 'لا يوجد'
    user_country = user_info.get('country', 'غير معروف') if user_info else 'غير معروف'
    
    admin_msg = (
        f"🖼 **طلب تغيير صورة جديد**\n\n"
        f"📌 **رقم الطلب:** `{order_number}`\n"
        f"👤 **الاسم:** {user_name}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"📝 **Username:** @{user_username}\n"
        f"🗣️ **اللغة:** {lang}\n"
        f"🌍 **الدولة:** {user_country}\n"
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


# ========== 3. المزيد ==========
@router.callback_query(F.data == "more_options")
async def show_more_options(callback: CallbackQuery):
    """عرض خيارات المزيد"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    more_title_text = safe_get_text(
        user_id,
        "more_title",
        "📌 **المزيد من الخيارات**\n\nاختر ما تريد:",
        "📌 **More options**\n\nChoose what you want:"
    )
    
    await callback.message.edit_text(
        more_title_text,
        reply_markup=get_more_options_keyboard(lang),
        parse_mode='Markdown'
    )
    await callback.answer()


@router.callback_query(F.data == "contact_us")
async def contact_us(callback: CallbackQuery, state: FSMContext):
    """تواصل بنا - فتح الدعم المباشر"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    from bot.handlers.chat import open_chat
    await open_chat(callback, state)


@router.callback_query(F.data == "back_to_free_orders")
async def back_to_free_orders(callback: CallbackQuery):
    """العودة إلى قائمة الطلبات المجانية"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    title = safe_get_text(
        user_id, 
        "free_orders_title",
        "🎁 **الطلبات المجانية**\n\nاختر الخدمة التي تريدها:",
        "🎁 **Free Requests**\n\nChoose the service you want:"
    )
    
    await callback.message.edit_text(
        title,
        reply_markup=get_free_orders_keyboard(lang),
        parse_mode='Markdown'
    )
    await callback.answer()


def register_free_orders_handlers(dp):
    """تسجيل معالجات الطلبات المجانية"""
    dp.include_router(router)
    logger.info("تم تسجيل معالجات الطلبات المجانية بنجاح")
