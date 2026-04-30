from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.datetime import datetime
import json
import pytz
from bot.database import db
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

router = Router()

# تخزين مؤقت لبيانات الطلب
temp_order_data = {}


# ========== القائمة الرئيسية للطلبات المجانية ==========
@router.message(F.text.in_({'🎁 الطلبات المجانية', '🎁 Free Requests'}))
async def show_free_orders(message: Message):
    """عرض قائمة الطلبات المجانية"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    if db.is_user_banned(user_id):
        await message.answer(get_text(user_id, "messages.banned"), parse_mode='Markdown')
        return
    
    await message.answer(
        get_text(user_id, "free_orders_title") if 'free_orders_title' in get_text(user_id, "free_orders_title") else ("🎁 **الطلبات المجانية**\n\nاختر الخدمة التي تريدها:" if lang == 'ar' else "🎁 **Free Requests**\n\nChoose the service you want:"),
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
    if is_rate_limited(user_id, 'change_name', limit=3, window=300):
        await callback.answer(get_text(user_id, "messages.rate_limited"), show_alert=True)
        return
    
    await callback.message.edit_text(
        get_text(user_id, "balance_q"),
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
        get_text(user_id, "send_name"),
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
        get_text(user_id, "no_balance"),
        reply_markup=get_back_keyboard(lang),
        parse_mode='Markdown'
    )
    await callback.answer()


@router.message(ChangeNameStates.WAITING_NAME)
async def change_name_get_name(message: Message, state: FSMContext):
    """استقبال الاسم الجديد"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    new_name = sanitize_input(message.text, max_length=50)
    if not new_name:
        await message.answer(
            get_text(user_id, "invalid_name"),
            parse_mode='Markdown'
        )
        return
    
    await state.update_data(new_name=new_name)
    await message.answer(
        get_text(user_id, "ask_email"),
        parse_mode='Markdown'
    )
    await state.set_state(ChangeNameStates.WAITING_EMAIL)


@router.message(ChangeNameStates.WAITING_EMAIL)
async def change_name_get_email(message: Message, state: FSMContext):
    """استقبال البريد الإلكتروني"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    email = sanitize_input(message.text, max_length=100)
    if not validate_email(email):
        await message.answer(
            get_text(user_id, "invalid_email"),
            parse_mode='Markdown'
        )
        return
    
    await state.update_data(email=email)
    await message.answer(
        get_text(user_id, "ask_password"),
        parse_mode='Markdown'
    )
    await state.set_state(ChangeNameStates.WAITING_PASSWORD)


@router.message(ChangeNameStates.WAITING_PASSWORD)
async def change_name_get_password(message: Message, state: FSMContext):
    """استقبال كلمة المرور وإنشاء الطلب"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    password = sanitize_input(message.text, max_length=100)
    if not password:
        await message.answer(
            get_text(user_id, "invalid_password") if 'invalid_password' in str(get_text(user_id, "invalid_password")) else "⚠️ **كلمة المرور غير صالحة، حاول مرة أخرى**" if lang == 'ar' else "⚠️ **Invalid password, try again**",
            parse_mode='Markdown'
        )
        return
    
    # الحصول على البيانات من FSM
    data = await state.get_data()
    new_name = data.get('new_name')
    email = data.get('email')
    
    if not new_name or not email:
        await message.answer(
            get_text(user_id, "messages.error"),
            reply_markup=get_main_keyboard(lang),
            parse_mode='Markdown'
        )
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
    
    # إرسال تأكيد للمستخدم
    await message.answer(
        get_text(user_id, "processing"),
        reply_markup=get_main_keyboard(lang),
        parse_mode='Markdown'
    )
    
    # إرسال الطلب للأدمن
    user_info = db.get_user_info(user_id)
    now = datetime.now(TIMEZONE)
    
    admin_msg = (
        f"📦 **طلب تغيير اسم جديد**\n\n"
        f"📌 **رقم الطلب:** `{order_number}`\n"
        f"👤 **الاسم:** {user_info['name'] if user_info else 'غير معروف'}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"📝 **Username:** @{user_info['username'] if user_info else 'لا يوجد'}\n"
        f"🗣️ **اللغة:** {lang}\n"
        f"🌍 **الدولة:** {user_info['country'] if user_info else 'غير معروف'}\n"
        f"📛 **الاسم الجديد:** {new_name}\n"
        f"📧 **البريد:** {email}\n"
        f"🔑 **كلمة المرور:** {password}\n"
        f"📅 **التاريخ:** {now.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    from bot.keyboards.inline import get_order_admin_keyboard
    await message.bot.send_message(
        ADMIN_ID,
        admin_msg,
        reply_markup=get_order_admin_keyboard(order_number, user_id),
        parse_mode='Markdown'
    )
    
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
    
    if is_rate_limited(user_id, 'change_photo', limit=3, window=300):
        await callback.answer(get_text(user_id, "messages.rate_limited"), show_alert=True)
        return
    
    await callback.message.edit_text(
        get_text(user_id, "change_photo_q") if 'change_photo_q' in str(get_text(user_id, "change_photo_q")) else ("🖼 **هل تريد تغيير صورتك؟**" if lang == 'ar' else "🖼 **Do you want to change your photo?**"),
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
    
    await callback.message.edit_text(
        get_text(user_id, "send_photo") if 'send_photo' in str(get_text(user_id, "send_photo")) else ("📸 **أرسل الصورة الجديدة:**" if lang == 'ar' else "📸 **Send your new photo:**"),
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
    await callback.message.edit_text(
        get_text(user_id, "cancelled"),
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
    await message.answer(
        get_text(user_id, "ask_email"),
        parse_mode='Markdown'
    )
    await state.set_state(ChangePhotoStates.WAITING_EMAIL)


@router.message(ChangePhotoStates.WAITING_PHOTO)
async def change_photo_invalid(message: Message, state: FSMContext):
    """الرسالة ليست صورة"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    await message.answer(
        get_text(user_id, "invalid_photo"),
        parse_mode='Markdown'
    )


@router.message(ChangePhotoStates.WAITING_EMAIL)
async def change_photo_get_email(message: Message, state: FSMContext):
    """استقبال البريد الإلكتروني لتغيير الصورة"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    email = sanitize_input(message.text, max_length=100)
    if not validate_email(email):
        await message.answer(
            get_text(user_id, "invalid_email"),
            parse_mode='Markdown'
        )
        return
    
    await state.update_data(email=email)
    await message.answer(
        get_text(user_id, "ask_password"),
        parse_mode='Markdown'
    )
    await state.set_state(ChangePhotoStates.WAITING_PASSWORD)


@router.message(ChangePhotoStates.WAITING_PASSWORD)
async def change_photo_get_password(message: Message, state: FSMContext):
    """استقبال كلمة المرور وإنشاء الطلب"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    password = sanitize_input(message.text, max_length=100)
    if not password:
        await message.answer(
            get_text(user_id, "invalid_password") if 'invalid_password' in str(get_text(user_id, "invalid_password")) else "⚠️ **كلمة المرور غير صالحة، حاول مرة أخرى**" if lang == 'ar' else "⚠️ **Invalid password, try again**",
            parse_mode='Markdown'
        )
        return
    
    # الحصول على البيانات من FSM
    data = await state.get_data()
    photo_id = data.get('photo_id')
    email = data.get('email')
    
    if not photo_id or not email:
        await message.answer(
            get_text(user_id, "messages.error"),
            reply_markup=get_main_keyboard(lang),
            parse_mode='Markdown'
        )
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
    
    # إرسال تأكيد للمستخدم
    await message.answer(
        get_text(user_id, "processing"),
        reply_markup=get_main_keyboard(lang),
        parse_mode='Markdown'
    )
    
    # إرسال الطلب للأدمن
    user_info = db.get_user_info(user_id)
    now = datetime.now(TIMEZONE)
    
    admin_msg = (
        f"🖼 **طلب تغيير صورة جديد**\n\n"
        f"📌 **رقم الطلب:** `{order_number}`\n"
        f"👤 **الاسم:** {user_info['name'] if user_info else 'غير معروف'}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"📝 **Username:** @{user_info['username'] if user_info else 'لا يوجد'}\n"
        f"🗣️ **اللغة:** {lang}\n"
        f"🌍 **الدولة:** {user_info['country'] if user_info else 'غير معروف'}\n"
        f"📧 **البريد:** {email}\n"
        f"🔑 **كلمة المرور:** {password}\n"
        f"📅 **التاريخ:** {now.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    from bot.keyboards.inline import get_order_admin_keyboard
    await message.bot.send_message(
        ADMIN_ID,
        admin_msg,
        reply_markup=get_order_admin_keyboard(order_number, user_id),
        parse_mode='Markdown'
    )
    
    # مسح الحالة
    await state.clear()


# ========== 3. المزيد ==========
@router.callback_query(F.data == "more_options")
async def show_more_options(callback: CallbackQuery):
    """عرض خيارات المزيد"""
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    await callback.message.edit_text(
        get_text(user_id, "more_title") if 'more_title' in str(get_text(user_id, "more_title")) else ("📌 **المزيد من الخيارات**\n\nاختر ما تريد:" if lang == 'ar' else "📌 **More options**\n\nChoose what you want:"),
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
    
    await callback.message.edit_text(
        get_text(user_id, "free_orders_title") if 'free_orders_title' in str(get_text(user_id, "free_orders_title")) else ("🎁 **الطلبات المجانية**\n\nاختر الخدمة التي تريدها:" if lang == 'ar' else "🎁 **Free Requests**\n\nChoose the service you want:"),
        reply_markup=get_free_orders_keyboard(lang),
        parse_mode='Markdown'
    )
    await callback.answer()


def register_free_orders_handlers(dp):
    """تسجيل معالجات الطلبات المجانية"""
    dp.include_router(router)
