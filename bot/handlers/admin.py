from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from datetime import datetime
import os
import asyncio
import logging
from bot.database.db import db
from bot.keyboards.reply import get_admin_keyboard, get_main_keyboard
from bot.keyboards.inline import (
    get_order_admin_keyboard,
    get_ticket_admin_keyboard,
    get_admin_chat_keyboard,
    get_broadcast_confirmation_keyboard
)
from bot.states.admin_states import AdminControlStates, AdminReplyStates
from bot.utils.translations import get_text
from bot.config import ADMIN_ID, TIMEZONE

logger = logging.getLogger(__name__)

router = Router()


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id == ADMIN_ID


def safe_send_message(bot, chat_id: int, text: str, **kwargs):
    """إرسال رسالة آمن مع try/except"""
    try:
        return bot.send_message(chat_id, text, **kwargs)
    except Exception as e:
        logger.error(f"Failed to send message to {chat_id}: {e}")
        return None


# ========== Admin Panel Main ==========
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Admin panel command"""
    if not is_admin(message.from_user.id):
        await safe_send_message(message.bot, message.from_user.id, "⛔ غير مصرح لك بهذا الأمر", parse_mode='Markdown')
        return
    await safe_send_message(message.bot, message.from_user.id, "👑 **لوحة التحكم - الأدمن**\n\nاختر الإجراء المناسب:", parse_mode='Markdown', reply_markup=get_admin_keyboard(message.from_user.id))


@router.message(F.text == "👑 لوحة التحكم")
async def admin_panel(message: Message):
    """Admin panel button handler"""
    if not is_admin(message.from_user.id):
        return
    await safe_send_message(message.bot, message.from_user.id, "👑 **لوحة التحكم - الأدمن**\n\nاختر الإجراء المناسب:", parse_mode='Markdown', reply_markup=get_admin_keyboard(message.from_user.id))


# ========== Statistics ==========
@router.message(F.text == "📊 الإحصائيات")
async def show_stats(message: Message):
    """Show bot statistics"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        stats = db.get_stats()
        users = db.get_all_users()
        
        text = f"📊 **إحصائيات البوت**\n\n"
        text += f"👥 **المستخدمين:**\n"
        text += f"• نشطين: {stats.get('active', 0)}\n"
        text += f"• محظورين: {stats.get('banned', 0)}\n"
        text += f"• إجمالي: {stats.get('active', 0) + stats.get('banned', 0)}\n\n"
        text += f"📦 **الطلبات:**\n"
        text += f"• إجمالي: {stats.get('total_orders', 0)}\n"
        text += f"• معلقة: {stats.get('pending_orders', 0)}\n"
        text += f"• منفذة: {stats.get('total_orders', 0) - stats.get('pending_orders', 0)}\n\n"
        text += f"🎫 **تذاكر مفتوحة:** {stats.get('open_tickets', 0)}"
        
        await safe_send_message(message.bot, message.from_user.id, text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in show_stats: {e}")
        await safe_send_message(message.bot, message.from_user.id, "❌ حدث خطأ في جلب الإحصائيات", parse_mode='Markdown')


# ========== Orders Management ==========
@router.message(F.text == "📋 الطلبات")
async def show_orders(message: Message):
    """Show pending orders"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        orders = db.get_pending_orders()
        if not orders:
            await safe_send_message(message.bot, message.from_user.id, "📭 **لا توجد طلبات معلقة**", parse_mode='Markdown')
            return
        
        for order in orders[:10]:
            try:
                user_info = db.get_user_info(order['user_id'])
                lang = user_info.get('lang', 'ar') if user_info else 'ar'
                
                text = f"📦 **طلب جديد**\n"
                text += f"📌 **رقم الطلب:** `{order['order_number']}`\n"
                text += f"👤 **الاسم:** {user_info.get('name', 'غير معروف') if user_info else 'غير معروف'}\n"
                text += f"🆔 **User ID:** `{order['user_id']}`\n"
                text += f"📝 **Username:** @{user_info.get('username', 'لا يوجد') if user_info else 'لا يوجد'}\n"
                text += f"🗣️ **اللغة:** {lang}\n"
                text += f"🌍 **الدولة:** {user_info.get('country', 'غير معروف') if user_info else 'غير معروف'}\n"
                text += f"📦 **نوع الطلب:** {order['order_type']}\n"
                text += f"📅 **التاريخ:** {order['created_at'][:19] if order.get('created_at') else 'غير معروف'}\n"
                
                await safe_send_message(message.bot, message.from_user.id, text, parse_mode='Markdown', reply_markup=get_order_admin_keyboard(order['order_number'], order['user_id']))
            except Exception as e:
                logger.error(f"Error displaying order: {e}")
                continue
        
        if len(orders) > 10:
            await safe_send_message(message.bot, message.from_user.id, f"📌 + {len(orders) - 10} طلب آخر", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in show_orders: {e}")
        await safe_send_message(message.bot, message.from_user.id, "❌ حدث خطأ في جلب الطلبات", parse_mode='Markdown')


@router.callback_query(F.data.startswith(('done_', 'exec_', 'cancel_', 'chat_', 'ban_')))
async def handle_order_actions(callback: CallbackQuery, state: FSMContext):
    """Handle order action buttons"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ غير مصرح", show_alert=True)
        return
    
    # استخدام split مع maxsplit=2 للحصول على 3 أجزاء كحد أقصى
    try:
        parts = callback.data.split('_', 2)
        if len(parts) < 3:
            await callback.answer("❌ بيانات غير صالحة", show_alert=True)
            return
        
        action = parts[0]
        order_number = parts[1]
        user_id = int(parts[2])
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing callback data: {callback.data} - {e}")
        await callback.answer("❌ حدث خطأ في معالجة البيانات", show_alert=True)
        return
    
    try:
        lang = db.get_user_language(user_id)
        
        if action == 'done':
            if db.update_order_status(order_number, 'completed'):
                db.log_admin_action(callback.from_user.id, 'order_completed', user_id, order_number)
                await safe_send_message(callback.bot, user_id, get_text(user_id, "messages.order_completed"), parse_mode='Markdown')
                await callback.message.edit_text(f"✅ **تم تنفيذ الطلب {order_number}**")
                await callback.answer("✅ تم تنفيذ الطلب")
            else:
                await callback.answer("❌ فشل تحديث حالة الطلب", show_alert=True)
        
        elif action == 'exec':
            if db.update_order_status(order_number, 'processing'):
                db.log_admin_action(callback.from_user.id, 'order_processing', user_id, order_number)
                await safe_send_message(callback.bot, user_id, get_text(user_id, "messages.order_processing"), parse_mode='Markdown')
                await callback.message.edit_text(f"🔄 **جاري تنفيذ الطلب {order_number}**")
                await callback.answer("⏳ تم بدء التنفيذ")
            else:
                await callback.answer("❌ فشل تحديث حالة الطلب", show_alert=True)
        
        elif action == 'cancel':
            if db.update_order_status(order_number, 'cancelled'):
                db.log_admin_action(callback.from_user.id, 'order_cancelled', user_id, order_number)
                await safe_send_message(callback.bot, user_id, get_text(user_id, "messages.order_cancelled"), parse_mode='Markdown')
                await callback.message.edit_text(f"❌ **تم إلغاء الطلب {order_number}**")
                await callback.answer("❌ تم إلغاء الطلب")
            else:
                await callback.answer("❌ فشل تحديث حالة الطلب", show_alert=True)
        
        elif action == 'chat':
            ticket_data = db.create_ticket(user_id, 'order_chat', f'محادثة حول الطلب {order_number}')
            if ticket_data and ticket_data[0] and ticket_data[1]:
                ticket_number, ticket_id = ticket_data
                session_id = db.create_chat_session(user_id, callback.from_user.id, ticket_id)
                await state.update_data(chat_user=user_id, chat_ticket=ticket_id, in_chat=True)
                await safe_send_message(callback.bot, callback.from_user.id, f"💬 **تم فتح محادثة مع المستخدم {user_id}**\nأرسل رسالتك الآن", parse_mode='Markdown')
                await safe_send_message(callback.bot, user_id, "🔓 **تم فتح محادثة مع الدعم الفني**\nيمكنك كتابة رسالتك الآن", parse_mode='Markdown')
                await callback.answer("💬 تم فتح المحادثة")
            else:
                await callback.answer("❌ فشل فتح المحادثة", show_alert=True)
        
        elif action == 'ban':
            if db.ban_user(user_id):
                db.log_admin_action(callback.from_user.id, 'ban', user_id, order_number)
                await safe_send_message(callback.bot, user_id, "🚫 **تم حظرك من البوت**", parse_mode='Markdown')
                await callback.message.edit_text(f"🚫 **تم حظر المستخدم {user_id}**")
                await callback.answer("🚫 تم حظر المستخدم")
            else:
                await callback.answer("❌ فشل حظر المستخدم", show_alert=True)
    except Exception as e:
        logger.error(f"Error in handle_order_actions: {e}")
        await callback.answer("❌ حدث خطأ", show_alert=True)


# ========== Users Management ==========
@router.message(F.text == "👥 المستخدمين")
async def show_users(message: Message):
    """Show users list"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        users = db.get_all_users_detailed()
        if not users:
            await safe_send_message(message.bot, message.from_user.id, "📭 **لا يوجد مستخدمين**", parse_mode='Markdown')
            return
        
        text = "👥 **قائمة المستخدمين الأخيرين**\n\n"
        for user in users[:20]:
            status = "🚫" if user.get('is_banned') else "✅"
            text += f"{status} {user.get('full_name', 'غير معروف')}\n"
            text += f"🆔 `{user.get('user_id', 'غير معروف')}`\n"
            text += f"📝 @{user.get('username', 'لا يوجد') if user.get('username') else 'لا يوجد'}\n"
            text += f"🗣️ {user.get('language', 'ar')}\n"
            text += f"📅 {user.get('registered_at', 'غير معروف')[:16] if user.get('registered_at') else 'غير معروف'}\n"
            text += "─" * 25 + "\n"
        
        if len(users) > 20:
            text += f"\n... و {len(users) - 20} آخرين"
        
        await safe_send_message(message.bot, message.from_user.id, text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in show_users: {e}")
        await safe_send_message(message.bot, message.from_user.id, "❌ حدث خطأ في جلب المستخدمين", parse_mode='Markdown')


# ========== Ban / Unban ==========
@router.message(F.text == "🚫 حظر مستخدم")
async def ban_user_start(message: Message, state: FSMContext):
    """Start ban user process"""
    if not is_admin(message.from_user.id):
        return
    await safe_send_message(message.bot, message.from_user.id, "🚫 **أدخل معرف المستخدم للحظر:**\nمثال: /ban 123456789", parse_mode='Markdown')
    await state.set_state(AdminReplyStates.WAITING_BAN_USER)


@router.message(Command("ban"))
async def ban_user_by_command(message: Message):
    """Ban user by command"""
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await safe_send_message(message.bot, message.from_user.id, "⚠️ **استخدم:** `/ban معرف_المستخدم`", parse_mode='Markdown')
        return
    try:
        user_id = int(parts[1])
        if db.ban_user(user_id):
            db.log_admin_action(message.from_user.id, 'ban', user_id)
            await safe_send_message(message.bot, user_id, "🚫 **تم حظرك من البوت**", parse_mode='Markdown')
            await safe_send_message(message.bot, message.from_user.id, f"✅ **تم حظر المستخدم {user_id}**", parse_mode='Markdown')
        else:
            await safe_send_message(message.bot, message.from_user.id, f"❌ **فشل حظر المستخدم {user_id}**", parse_mode='Markdown')
    except ValueError:
        await safe_send_message(message.bot, message.from_user.id, "❌ **معرف المستخدم غير صحيح**", parse_mode='Markdown')


@router.message(F.text == "✅ فك حظر")
async def unban_start(message: Message, state: FSMContext):
    """Start unban user process"""
    if not is_admin(message.from_user.id):
        return
    await safe_send_message(message.bot, message.from_user.id, "✅ **أدخل معرف المستخدم لفك الحظر:**\nمثال: /unban 123456789", parse_mode='Markdown')
    await state.set_state(AdminReplyStates.WAITING_UNBAN_USER)


@router.message(Command("unban"))
async def unban_user(message: Message):
    """Unban user by command"""
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await safe_send_message(message.bot, message.from_user.id, "⚠️ **استخدم:** `/unban معرف_المستخدم`", parse_mode='Markdown')
        return
    try:
        user_id = int(parts[1])
        if db.unban_user(user_id):
            db.log_admin_action(message.from_user.id, 'unban', user_id)
            await safe_send_message(message.bot, user_id, "✅ **تم فك حظرك، يمكنك استخدام البوت مرة أخرى**", parse_mode='Markdown')
            await safe_send_message(message.bot, message.from_user.id, f"✅ **تم فك حظر المستخدم {user_id}**", parse_mode='Markdown')
        else:
            await safe_send_message(message.bot, message.from_user.id, f"❌ **فشل فك حظر المستخدم {user_id}**", parse_mode='Markdown')
    except ValueError:
        await safe_send_message(message.bot, message.from_user.id, "❌ **معرف المستخدم غير صحيح**", parse_mode='Markdown')


# ========== Tickets Management ==========
@router.message(F.text == "📝 التذاكر")
async def show_tickets(message: Message):
    """Show open tickets"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        tickets = db.get_open_tickets()
        if not tickets:
            await safe_send_message(message.bot, message.from_user.id, "📭 **لا توجد تذاكر مفتوحة**", parse_mode='Markdown')
            return
        
        text = "🎫 **التذاكر المفتوحة**\n\n"
        for ticket in tickets[:15]:
            text += f"📌 `{ticket.get('ticket_number', 'غير معروف')}`\n"
            text += f"👤 المستخدم: {ticket.get('user_id', 'غير معروف')}\n"
            text += f"📦 النوع: {ticket.get('ticket_type', 'غير معروف')}\n"
            text += f"📅 {ticket.get('created_at', 'غير معروف')[:16] if ticket.get('created_at') else 'غير معروف'}\n"
            text += "─" * 20 + "\n"
        
        if len(tickets) > 15:
            text += f"\n... و {len(tickets) - 15} تذكرة أخرى"
        
        await safe_send_message(message.bot, message.from_user.id, text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in show_tickets: {e}")
        await safe_send_message(message.bot, message.from_user.id, "❌ حدث خطأ في جلب التذاكر", parse_mode='Markdown')


@router.callback_query(F.data.startswith("reply_ticket_"))
async def reply_to_ticket(callback: CallbackQuery, state: FSMContext):
    """Reply to a ticket"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ غير مصرح", show_alert=True)
        return
    
    try:
        ticket_number = callback.data.split('_', 2)[2]
        ticket = db.get_ticket(ticket_number)
        if not ticket:
            await callback.answer("التذكرة غير موجودة", show_alert=True)
            return
        
        await state.update_data(reply_ticket_number=ticket_number, reply_ticket_user=ticket.get('user_id'))
        await state.set_state(AdminReplyStates.WAITING_REPLY)
        await safe_send_message(callback.bot, callback.from_user.id, f"💬 **اكتب ردك على التذكرة {ticket_number}:**", parse_mode='Markdown')
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in reply_to_ticket: {e}")
        await callback.answer("❌ حدث خطأ", show_alert=True)


# ========== Logs ==========
@router.message(F.text == "📜 السجلات")
async def show_logs(message: Message):
    """Show admin logs"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        logs = db.get_admin_logs(30)
        if not logs:
            await safe_send_message(message.bot, message.from_user.id, "📭 **لا توجد سجلات**", parse_mode='Markdown')
            return
        
        text = "📜 **آخر السجلات**\n\n"
        for log in logs[:20]:
            text += f"🕐 {log.get('timestamp', 'غير معروف')[:16] if log.get('timestamp') else 'غير معروف'}\n"
            text += f"👑 {log.get('action', 'غير معروف')}\n"
            if log.get('target_user'):
                text += f"🎯 المستخدم: {log['target_user']}\n"
            if log.get('order_number'):
                text += f"📦 الطلب: {log['order_number']}\n"
            text += "─" * 20 + "\n"
        
        await safe_send_message(message.bot, message.from_user.id, text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in show_logs: {e}")
        await safe_send_message(message.bot, message.from_user.id, "❌ حدث خطأ في جلب السجلات", parse_mode='Markdown')


# ========== Control Bot (Send Messages/Photos/Videos) ==========
@router.message(F.text == "🎮 تحكم في البوت")
async def control_bot_start(message: Message, state: FSMContext):
    """Start bot control menu"""
    if not is_admin(message.from_user.id):
        return
    
    await safe_send_message(
        message.bot, message.from_user.id,
        "🎮 **تحكم في البوت**\n\n"
        "اختر نوع الإرسال:\n"
        "1️⃣ **رسالة نصية:** /sendtext معرف_المستخدم الرسالة\n"
        "2️⃣ **إذاعة للجميع:** /broadcast رسالتك\n"
        "3️⃣ **صورة:** /sendphoto معرف_المستخدم\n"
        "4️⃣ **فيديو:** /sendvideo معرف_المستخدم\n\n"
        "لإرسال صورة أو فيديو، اتبع الأمر ثم قم بإرسال الملف",
        parse_mode='Markdown'
    )


@router.message(Command("sendtext"))
async def send_text_to_user(message: Message):
    """Send text message to specific user"""
    if not is_admin(message.from_user.id):
        return
    
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await safe_send_message(message.bot, message.from_user.id, "⚠️ **استخدم:** `/sendtext معرف_المستخدم النص`", parse_mode='Markdown')
        return
    
    try:
        user_id = int(parts[1])
        text = parts[2]
        await safe_send_message(message.bot, user_id, f"📨 **رسالة من الإدارة:**\n\n{text}", parse_mode='Markdown')
        await safe_send_message(message.bot, message.from_user.id, f"✅ **تم إرسال الرسالة للمستخدم {user_id}**", parse_mode='Markdown')
        db.log_admin_action(message.from_user.id, 'send_text', user_id, None, text[:100])
    except Exception as e:
        logger.error(f"Error in send_text_to_user: {e}")
        await safe_send_message(message.bot, message.from_user.id, f"❌ **خطأ:** {e}", parse_mode='Markdown')


@router.message(Command("sendphoto"))
async def send_photo_to_user(message: Message, state: FSMContext):
    """Send photo to specific user"""
    if not is_admin(message.from_user.id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await safe_send_message(message.bot, message.from_user.id, "⚠️ **استخدم:** `/sendphoto معرف_المستخدم`\nثم أرسل الصورة", parse_mode='Markdown')
        return
    
    try:
        user_id = int(parts[1])
        await state.update_data(send_photo_to=user_id)
        await safe_send_message(message.bot, message.from_user.id, f"📸 **أرسل الصورة التي تريد إرسالها للمستخدم {user_id}**", parse_mode='Markdown')
        await state.set_state(AdminControlStates.WAITING_PHOTO)
    except ValueError:
        await safe_send_message(message.bot, message.from_user.id, "❌ **معرف المستخدم غير صحيح**", parse_mode='Markdown')


@router.message(AdminControlStates.WAITING_PHOTO, F.photo)
async def handle_send_photo(message: Message, state: FSMContext):
    """Handle sending photo"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        data = await state.get_data()
        user_id = data.get('send_photo_to')
        if not user_id:
            await safe_send_message(message.bot, message.from_user.id, "❌ **حدث خطأ، حاول مرة أخرى**")
            await state.clear()
            return
        
        photo = message.photo[-1]
        await safe_send_message(message.bot, user_id, "📸 **صورة من الإدارة**")
        await message.bot.send_photo(user_id, photo.file_id)
        await safe_send_message(message.bot, message.from_user.id, f"✅ **تم إرسال الصورة للمستخدم {user_id}**")
        db.log_admin_action(message.from_user.id, 'send_photo', user_id)
    except Exception as e:
        logger.error(f"Error in handle_send_photo: {e}")
        await safe_send_message(message.bot, message.from_user.id, f"❌ **حدث خطأ:** {e}")
    finally:
        await state.clear()


@router.message(Command("sendvideo"))
async def send_video_to_user(message: Message, state: FSMContext):
    """Send video to specific user"""
    if not is_admin(message.from_user.id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await safe_send_message(message.bot, message.from_user.id, "⚠️ **استخدم:** `/sendvideo معرف_المستخدم`\nثم أرسل الفيديو", parse_mode='Markdown')
        return
    
    try:
        user_id = int(parts[1])
        await state.update_data(send_video_to=user_id)
        await safe_send_message(message.bot, message.from_user.id, f"🎥 **أرسل الفيديو الذي تريد إرساله للمستخدم {user_id}**", parse_mode='Markdown')
        await state.set_state(AdminControlStates.WAITING_VIDEO)
    except ValueError:
        await safe_send_message(message.bot, message.from_user.id, "❌ **معرف المستخدم غير صحيح**", parse_mode='Markdown')


@router.message(AdminControlStates.WAITING_VIDEO, F.video)
async def handle_send_video(message: Message, state: FSMContext):
    """Handle sending video"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        data = await state.get_data()
        user_id = data.get('send_video_to')
        if not user_id:
            await safe_send_message(message.bot, message.from_user.id, "❌ **حدث خطأ، حاول مرة أخرى**")
            await state.clear()
            return
        
        video = message.video
        await safe_send_message(message.bot, user_id, "🎥 **فيديو من الإدارة**")
        await message.bot.send_video(user_id, video.file_id)
        await safe_send_message(message.bot, message.from_user.id, f"✅ **تم إرسال الفيديو للمستخدم {user_id}**")
        db.log_admin_action(message.from_user.id, 'send_video', user_id)
    except Exception as e:
        logger.error(f"Error in handle_send_video: {e}")
        await safe_send_message(message.bot, message.from_user.id, f"❌ **حدث خطأ:** {e}")
    finally:
        await state.clear()


# ========== Admin Reply Handler ==========
@router.message(AdminReplyStates.WAITING_REPLY)
async def send_admin_reply(message: Message, state: FSMContext):
    """Send admin reply"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        data = await state.get_data()
        user_id = data.get('reply_to_user') or data.get('reply_ticket_user')
        ticket_number = data.get('reply_ticket_number')
        
        if not user_id:
            await safe_send_message(message.bot, message.from_user.id, "❌ حدث خطأ، حاول مرة أخرى")
            await state.clear()
            return
        
        # Send reply to user
        await safe_send_message(message.bot, user_id, f"📨 **رد من الدعم:**\n{message.text}", parse_mode='Markdown')
        await safe_send_message(message.bot, message.from_user.id, f"✅ **تم إرسال الرد للمستخدم {user_id}**")
        
        # Log and clear
        db.log_admin_action(message.from_user.id, 'admin_reply', user_id, ticket_number, message.text[:100])
    except Exception as e:
        logger.error(f"Error in send_admin_reply: {e}")
        await safe_send_message(message.bot, message.from_user.id, f"❌ حدث خطأ: {e}")
    finally:
        await state.clear()


# ========== Chat Session Handlers ==========
@router.message(AdminReplyStates.WAITING_BAN_USER)
async def process_ban(message: Message, state: FSMContext):
    """Process ban from admin panel"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        user_id = int(message.text.strip())
        if db.ban_user(user_id):
            db.log_admin_action(message.from_user.id, 'ban', user_id)
            await safe_send_message(message.bot, user_id, "🚫 **تم حظرك من البوت**", parse_mode='Markdown')
            await safe_send_message(message.bot, message.from_user.id, f"✅ **تم حظر المستخدم {user_id}**", parse_mode='Markdown')
        else:
            await safe_send_message(message.bot, message.from_user.id, f"❌ **فشل حظر المستخدم {user_id}**", parse_mode='Markdown')
    except ValueError:
        await safe_send_message(message.bot, message.from_user.id, "❌ **معرف المستخدم غير صحيح**", parse_mode='Markdown')
    finally:
        await state.clear()


@router.message(AdminReplyStates.WAITING_UNBAN_USER)
async def process_unban(message: Message, state: FSMContext):
    """Process unban from admin panel"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        user_id = int(message.text.strip())
        if db.unban_user(user_id):
            db.log_admin_action(message.from_user.id, 'unban', user_id)
            await safe_send_message(message.bot, user_id, "✅ **تم فك حظرك، يمكنك استخدام البوت مرة أخرى**", parse_mode='Markdown')
            await safe_send_message(message.bot, message.from_user.id, f"✅ **تم فك حظر المستخدم {user_id}**", parse_mode='Markdown')
        else:
            await safe_send_message(message.bot, message.from_user.id, f"❌ **فشل فك حظر المستخدم {user_id}**", parse_mode='Markdown')
    except ValueError:
        await safe_send_message(message.bot, message.from_user.id, "❌ **معرف المستخدم غير صحيح**", parse_mode='Markdown')
    finally:
        await state.clear()


def register_admin_handlers(dp):
    """Register all admin handlers"""
    dp.include_router(router)
