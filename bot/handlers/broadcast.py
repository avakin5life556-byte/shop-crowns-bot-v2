from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
import logging
import asyncio
from bot.database.db import db
from bot.keyboards.inline import get_broadcast_confirmation_keyboard
from bot.keyboards.reply import get_admin_keyboard
from bot.config import ADMIN_ID, TIMEZONE
from bot.states.broadcast_states import BroadcastStates

# إعداد logging
logger = logging.getLogger(__name__)

router = Router()


# ========== بدء الإذاعة ==========
@router.message(F.text == "📢 إذاعة")
async def start_broadcast(message: Message, state: FSMContext):
    """بدء عملية الإذاعة - اختيار نوع المحتوى"""
    if message.from_user.id != ADMIN_ID:
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text="📝 نص", callback_data="broadcast_text"),
        types.InlineKeyboardButton(text="🖼 صورة", callback_data="broadcast_photo"),
        types.InlineKeyboardButton(text="🎥 فيديو", callback_data="broadcast_video"),
        types.InlineKeyboardButton(text="🔙 إلغاء", callback_data="broadcast_cancel")
    )
    
    await message.answer(
        "📢 **إذاعة عامة**\n\nاختر نوع المحتوى الذي تريد إرساله للمستخدمين:",
        reply_markup=markup,
        parse_mode='Markdown'
    )


# ========== إذاعة نصية ==========
@router.callback_query(F.data == "broadcast_text")
async def broadcast_text_start(callback: CallbackQuery, state: FSMContext):
    """بدء إذاعة نصية"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ غير مصرح", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📝 **إذاعة نصية**\n\nأرسل النص الذي تريد إذاعته لجميع المستخدمين:",
        parse_mode='Markdown'
    )
    await state.set_state(BroadcastStates.WAITING_TEXT)
    await callback.answer()


@router.message(BroadcastStates.WAITING_TEXT)
async def receive_broadcast_text(message: Message, state: FSMContext):
    """استقبال النص وعرض تأكيد"""
    if message.from_user.id != ADMIN_ID:
        return
    
    broadcast_text = message.text
    
    if not broadcast_text:
        await message.answer("⚠️ الرجاء إرسال نص صالح")
        return
    
    await state.update_data(broadcast_type="text", broadcast_content=broadcast_text)
    
    # الحصول على عدد المستخدمين
    users = db.get_all_users()
    users_count = len(users) if users else 0
    
    preview_text = (
        f"📢 **معاينة الإذاعة**\n\n"
        f"📝 **النص:**\n{broadcast_text}\n\n"
        f"👥 **عدد المستخدمين المستهدفين:** {users_count}\n\n"
        f"⚠️ هل أنت متأكد من إرسال هذه الإذاعة؟"
    )
    
    await message.answer(
        preview_text,
        reply_markup=get_broadcast_confirmation_keyboard(),
        parse_mode='Markdown'
    )
    await state.set_state(BroadcastStates.CONFIRMING)


# ========== إذاعة صورة ==========
@router.callback_query(F.data == "broadcast_photo")
async def broadcast_photo_start(callback: CallbackQuery, state: FSMContext):
    """بدء إذاعة صورة"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ غير مصرح", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🖼 **إذاعة صورة**\n\nأرسل الصورة التي تريد إذاعتها لجميع المستخدمين\n(يمكنك إضافة تعليق نصي مع الصورة)",
        parse_mode='Markdown'
    )
    await state.set_state(BroadcastStates.WAITING_PHOTO)
    await callback.answer()


@router.message(BroadcastStates.WAITING_PHOTO, F.photo)
async def receive_broadcast_photo(message: Message, state: FSMContext):
    """استقبال الصورة وعرض تأكيد"""
    if message.from_user.id != ADMIN_ID:
        return
    
    photo = message.photo[-1]
    caption = message.caption or ""
    
    await state.update_data(
        broadcast_type="photo",
        broadcast_file_id=photo.file_id,
        broadcast_caption=caption
    )
    
    users = db.get_all_users()
    users_count = len(users) if users else 0
    
    preview_text = (
        f"📢 **معاينة الإذاعة**\n\n"
        f"🖼 **صورة**\n"
        f"📝 **التعليق:** {caption if caption else 'بدون تعليق'}\n\n"
        f"👥 **عدد المستخدمين المستهدفين:** {users_count}\n\n"
        f"⚠️ هل أنت متأكد من إرسال هذه الإذاعة؟"
    )
    
    # إرسال معاينة الصورة
    await message.answer_photo(
        photo.file_id,
        caption=preview_text,
        reply_markup=get_broadcast_confirmation_keyboard(),
        parse_mode='Markdown'
    )
    await state.set_state(BroadcastStates.CONFIRMING)


@router.message(BroadcastStates.WAITING_PHOTO)
async def invalid_photo(message: Message, state: FSMContext):
    """معالج الرسائل غير الصور"""
    if message.from_user.id != ADMIN_ID:
        return
    
    await message.answer("⚠️ الرجاء إرسال صورة صالحة")


# ========== إذاعة فيديو ==========
@router.callback_query(F.data == "broadcast_video")
async def broadcast_video_start(callback: CallbackQuery, state: FSMContext):
    """بدء إذاعة فيديو"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ غير مصرح", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🎥 **إذاعة فيديو**\n\nأرسل الفيديو الذي تريد إذاعته لجميع المستخدمين\n(يمكنك إضافة تعليق نصي مع الفيديو)",
        parse_mode='Markdown'
    )
    await state.set_state(BroadcastStates.WAITING_VIDEO)
    await callback.answer()


@router.message(BroadcastStates.WAITING_VIDEO, F.video)
async def receive_broadcast_video(message: Message, state: FSMContext):
    """استقبال الفيديو وعرض تأكيد"""
    if message.from_user.id != ADMIN_ID:
        return
    
    video = message.video
    caption = message.caption or ""
    
    await state.update_data(
        broadcast_type="video",
        broadcast_file_id=video.file_id,
        broadcast_caption=caption
    )
    
    users = db.get_all_users()
    users_count = len(users) if users else 0
    
    preview_text = (
        f"📢 **معاينة الإذاعة**\n\n"
        f"🎥 **فيديو**\n"
        f"📝 **التعليق:** {caption if caption else 'بدون تعليق'}\n\n"
        f"👥 **عدد المستخدمين المستهدفين:** {users_count}\n\n"
        f"⚠️ هل أنت متأكد من إرسال هذه الإذاعة؟"
    )
    
    # إرسال معاينة الفيديو
    await message.answer_video(
        video.file_id,
        caption=preview_text,
        reply_markup=get_broadcast_confirmation_keyboard(),
        parse_mode='Markdown'
    )
    await state.set_state(BroadcastStates.CONFIRMING)


@router.message(BroadcastStates.WAITING_VIDEO)
async def invalid_video(message: Message, state: FSMContext):
    """معالج الرسائل غير الفيديو"""
    if message.from_user.id != ADMIN_ID:
        return
    
    await message.answer("⚠️ الرجاء إرسال فيديو صالح")


# ========== تأكيد وإرسال الإذاعة ==========
@router.callback_query(F.data == "confirm_broadcast", BroadcastStates.CONFIRMING)
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext):
    """تأكيد وإرسال الإذاعة لجميع المستخدمين"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ غير مصرح", show_alert=True)
        return
    
    data = await state.get_data()
    broadcast_type = data.get('broadcast_type')
    
    # الحصول على جميع المستخدمين
    users = db.get_all_users()
    if not users:
        await callback.message.edit_text("❌ **لا يوجد مستخدمين لإرسال الإذاعة لهم**", parse_mode='Markdown')
        await state.clear()
        await callback.answer()
        return
    
    total_users = len(users)
    success_count = 0
    failed_count = 0
    
    # إرسال رسالة "جاري الإرسال"
    status_msg = await callback.message.edit_text(
        f"📢 **جاري إرسال الإذاعة...**\n\n"
        f"👥 المستخدمين: {total_users}\n"
        f"⏳ جاري الإرسال...",
        parse_mode='Markdown'
    )
    
    logger.info(f"بدء إذاعة {broadcast_type} لـ {total_users} مستخدم")
    
    # إرسال الإذاعة لكل مستخدم
    for i, user in enumerate(users):
        try:
            # التوافق مع dict أو tuple
            if isinstance(user, dict):
                user_id = user.get('user_id')
            else:
                user_id = user[0] if len(user) > 0 else None
            
            if not user_id:
                failed_count += 1
                continue
            
            if broadcast_type == "text":
                broadcast_text = data.get('broadcast_content')
                await callback.bot.send_message(
                    user_id,
                    f"📢 **إذاعة عامة**\n\n{broadcast_text}",
                    parse_mode='Markdown'
                )
            
            elif broadcast_type == "photo":
                file_id = data.get('broadcast_file_id')
                caption = data.get('broadcast_caption', '')
                await callback.bot.send_photo(
                    user_id,
                    file_id,
                    caption=f"📢 **إذاعة عامة**\n\n{caption}" if caption else "📢 **إذاعة عامة**",
                    parse_mode='Markdown'
                )
            
            elif broadcast_type == "video":
                file_id = data.get('broadcast_file_id')
                caption = data.get('broadcast_caption', '')
                await callback.bot.send_video(
                    user_id,
                    file_id,
                    caption=f"📢 **إذاعة عامة**\n\n{caption}" if caption else "📢 **إذاعة عامة**",
                    parse_mode='Markdown'
                )
            
            success_count += 1
            
            # تحديث رسالة التقدم كل 10 مستخدمين
            if (i + 1) % 10 == 0:
                await status_msg.edit_text(
                    f"📢 **جاري إرسال الإذاعة...**\n\n"
                    f"✅ تم الإرسال: {success_count}\n"
                    f"❌ فشل: {failed_count}\n"
                    f"📊 المتبقي: {total_users - (success_count + failed_count)}",
                    parse_mode='Markdown'
                )
            
            # تجنب الحظر من Telegram (زيادة الوقت إلى 0.1 ثانية)
            await asyncio.sleep(0.1)
            
        except Exception as e:
            failed_count += 1
            logger.error(f"فشل إرسال الإذاعة للمستخدم {user_id if 'user_id' in locals() else 'unknown'}: {e}")
    
    # تسجيل الإذاعة في سجل الأدمن
    try:
        db.log_admin_action(
            callback.from_user.id, 
            'broadcast', 
            None, 
            None, 
            f'type: {broadcast_type}, sent: {success_count}, failed: {failed_count}'
        )
        logger.info(f"تم تسجيل الإذاعة في السجلات: {success_count} نجاح، {failed_count} فشل")
    except Exception as e:
        logger.error(f"فشل تسجيل الإذاعة: {e}")
    
    # إرسال التقرير النهائي
    result_text = (
        f"✅ **تم إرسال الإذاعة بنجاح**\n\n"
        f"📊 **التقرير النهائي:**\n"
        f"✅ تم الإرسال: {success_count} مستخدم\n"
        f"❌ فشل الإرسال: {failed_count} مستخدم\n"
        f"👥 إجمالي المستخدمين: {total_users}\n\n"
        f"📅 {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    await status_msg.edit_text(result_text, parse_mode='Markdown')
    await callback.message.answer(
        "👑 **لوحة التحكم**",
        reply_markup=get_admin_keyboard(callback.from_user.id)  # تمرير user_id
    )
    
    await state.clear()
    await callback.answer()


# ========== إلغاء الإذاعة ==========
@router.callback_query(F.data == "cancel_broadcast")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    """إلغاء الإذاعة"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ غير مصرح", show_alert=True)
        return
    
    await callback.message.edit_text(
        "❌ **تم إلغاء الإذاعة**",
        parse_mode='Markdown'
    )
    await callback.message.answer(
        "👑 **لوحة التحكم**",
        reply_markup=get_admin_keyboard(callback.from_user.id)  # تمرير user_id
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "broadcast_cancel")
async def broadcast_cancel(callback: CallbackQuery, state: FSMContext):
    """إلغاء الإذاعة من القائمة الأولى"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ غير مصرح", show_alert=True)
        return
    
    await callback.message.edit_text(
        "❌ **تم إلغاء الإذاعة**",
        parse_mode='Markdown'
    )
    await callback.message.answer(
        "👑 **لوحة التحكم**",
        reply_markup=get_admin_keyboard(callback.from_user.id)  # تمرير user_id
    )
    await state.clear()
    await callback.answer()


def register_broadcast_handlers(dp):
    """تسجيل معالجات الإذاعة"""
    dp.include_router(router)
    logger.info("تم تسجيل معالجات الإذاعة بنجاح")
