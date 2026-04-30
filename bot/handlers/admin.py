from bot.aiogram import Router, F, types
from bot.aiogram.types import Message, CallbackQuery, FSInputFile
from bot.aiogram.fsm.context import FSMContext
from bot.aiogram.filters import Command
from bot.datetime import datetime
import os
import asyncio
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

router = Router()


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id == ADMIN_ID


# ========== Admin Panel Main ==========
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Admin panel command"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ غير مصرح لك بهذا الأمر", parse_mode='Markdown')
        return
    await message.answer("👑 **لوحة التحكم - الأدمن**\n\nاختر الإجراء المناسب:", parse_mode='Markdown', reply_markup=get_admin_keyboard(message.from_user.id))


@router.message(F.text == "👑 لوحة التحكم")
async def admin_panel(message: Message):
    """Admin panel button handler"""
    if not is_admin(message.from_user.id):
        return
    await message.answer("👑 **لوحة التحكم - الأدمن**\n\nاختر الإجراء المناسب:", parse_mode='Markdown', reply_markup=get_admin_keyboard(message.from_user.id))


# ========== Statistics ==========
@router.message(F.text == "📊 الإحصائيات")
async def show_stats(message: Message):
    """Show bot statistics"""
    if not is_admin(message.from_user.id):
        return
    
    stats = db.get_stats()
    users = db.get_all_users()
    
    text = f"📊 **إحصائيات البوت**\n\n"
    text += f"👥 **المستخدمين:**\n"
    text += f"• نشطين: {stats['active']}\n"
    text += f"• محظورين: {stats['banned']}\n"
    text += f"• إجمالي: {stats['active'] + stats['banned']}\n\n"
    text += f"📦 **الطلبات:**\n"
    text += f"• إجمالي: {stats['total_orders']}\n"
    text += f"• معلقة: {stats['pending_orders']}\n"
    text += f"• منفذة: {stats['total_orders'] - stats['pending_orders']}\n\n"
    text += f"🎫 **تذاكر مفتوحة:** {stats.get('open_tickets', 0)}"
    
    await message.answer(text, parse_mode='Markdown')


# ========== Orders Management ==========
@router.message(F.text == "📋 الطلبات")
async def show_orders(message: Message):
    """Show pending orders"""
    if not is_admin(message.from_user.id):
        return
    
    orders = db.get_pending_orders()
    if not orders:
        await message.answer("📭 **لا توجد طلبات معلقة**", parse_mode='Markdown')
        return
    
    for order in orders[:10]:
        user_info = db.get_user_info(order['user_id'])
        lang = user_info['lang'] if user_info else 'ar'
        
        text = f"📦 **طلب جديد**\n"
        text += f"📌 **رقم الطلب:** `{order['order_number']}`\n"
        text += f"👤 **الاسم:** {user_info['name'] if user_info else 'غير معروف'}\n"
        text += f"🆔 **User ID:** `{order['user_id']}`\n"
        text += f"📝 **Username:** @{user_info['username'] if user_info else 'لا يوجد'}\n"
        text += f"🗣️ **اللغة:** {lang}\n"
        text += f"🌍 **الدولة:** {user_info['country'] if user_info else 'غير معروف'}\n"
        text += f"📦 **نوع الطلب:** {order['order_type']}\n"
        text += f"📅 **التاريخ:** {order['created_at'][:19]}\n"
        
        await message.answer(text, parse_mode='Markdown', reply_markup=get_order_admin_keyboard(order['order_number'], order['user_id']))
    
    if len(orders) > 10:
        await message.answer(f"📌 + {len(orders) - 10} طلب آخر")


@router.callback_query(F.data.startswith(('done_', 'exec_', 'cancel_', 'chat_', 'ban_')))
async def handle_order_actions(callback: CallbackQuery, state: FSMContext):
    """Handle order action buttons"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ غير مصرح", show_alert=True)
        return
    
    action, order_number, user_id = callback.data.split('_')
    user_id = int(user_id)
    lang = db.get_user_language(user_id)
    
    if action == 'done':
        db.update_order_status(order_number, 'completed')
        db.log_admin_action(callback.from_user.id, 'order_completed', user_id, order_number)
        await callback.bot.send_message(user_id, get_text(user_id, "messages.order_completed"), parse_mode='Markdown')
        await callback.message.edit_text(f"✅ **تم تنفيذ الطلب {order_number}**")
        await callback.answer("✅ تم تنفيذ الطلب")
    
    elif action == 'exec':
        db.update_order_status(order_number, 'processing')
        db.log_admin_action(callback.from_user.id, 'order_processing', user_id, order_number)
        await callback.bot.send_message(user_id, get_text(user_id, "messages.order_processing"), parse_mode='Markdown')
        await callback.message.edit_text(f"🔄 **جاري تنفيذ الطلب {order_number}**")
        await callback.answer("⏳ تم بدء التنفيذ")
    
    elif action == 'cancel':
        db.update_order_status(order_number, 'cancelled')
        db.log_admin_action(callback.from_user.id, 'order_cancelled', user_id, order_number)
        await callback.bot.send_message(user_id, get_text(user_id, "messages.order_cancelled"), parse_mode='Markdown')
        await callback.message.edit_text(f"❌ **تم إلغاء الطلب {order_number}**")
        await callback.answer("❌ تم إلغاء الطلب")
    
    elif action == 'chat':
        ticket_number, ticket_id = db.create_ticket(user_id, 'order_chat', f'محادثة حول الطلب {order_number}')
        session_id = db.create_chat_session(user_id, callback.from_user.id, ticket_id)
        await state.update_data(chat_user=user_id, chat_ticket=ticket_id, in_chat=True)
        await callback.message.answer(f"💬 **تم فتح محادثة مع المستخدم {user_id}**\nأرسل رسالتك الآن", parse_mode='Markdown')
        await callback.bot.send_message(user_id, "🔓 **تم فتح محادثة مع الدعم الفني**\nيمكنك كتابة رسالتك الآن", parse_mode='Markdown')
        await callback.answer("💬 تم فتح المحادثة")
    
    elif action == 'ban':
        db.ban_user(user_id)
        db.log_admin_action(callback.from_user.id, 'ban', user_id, order_number)
        await callback.bot.send_message(user_id, "🚫 **تم حظرك من البوت**", parse_mode='Markdown')
        await callback.message.edit_text(f"🚫 **تم حظر المستخدم {user_id}**")
        await callback.answer("🚫 تم حظر المستخدم")


# ========== Users Management ==========
@router.message(F.text == "👥 المستخدمين")
async def show_users(message: Message):
    """Show users list"""
    if not is_admin(message.from_user.id):
        return
    
    users = db.get_all_users_detailed()
    if not users:
        await message.answer("📭 **لا يوجد مستخدمين**", parse_mode='Markdown')
        return
    
    text = "👥 **قائمة المستخدمين الأخيرين**\n\n"
    for user in users[:20]:
        status = "🚫" if user['is_banned'] else "✅"
        text += f"{status} {user['full_name']}\n"
        text += f"🆔 `{user['user_id']}`\n"
        text += f"📝 @{user['username'] if user['username'] else 'لا يوجد'}\n"
        text += f"🗣️ {user['language']}\n"
        text += f"📅 {user['registered_at'][:16] if user['registered_at'] else 'غير معروف'}\n"
        text += "─" * 25 + "\n"
    
    if len(users) > 20:
        text += f"\n... و {len(users) - 20} آخرين"
    
    await message.answer(text, parse_mode='Markdown')


# ========== Ban / Unban ==========
@router.message(F.text == "🚫 حظر مستخدم")
async def ban_user_start(message: Message, state: FSMContext):
    """Start ban user process"""
    if not is_admin(message.from_user.id):
        return
    await message.answer("🚫 **أدخل معرف المستخدم للحظر:**\nمثال: /ban 123456789", parse_mode='Markdown')
    await state.set_state(AdminReplyStates.WAITING_BAN_USER)


@router.message(Command("ban"))
async def ban_user_by_command(message: Message):
    """Ban user by command"""
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("⚠️ **استخدم:** `/ban معرف_المستخدم`", parse_mode='Markdown')
        return
    try:
        user_id = int(parts[1])
        db.ban_user(user_id)
        db.log_admin_action(message.from_user.id, 'ban', user_id)
        await message.bot.send_message(user_id, "🚫 **تم حظرك من البوت**", parse_mode='Markdown')
        await message.answer(f"✅ **تم حظر المستخدم {user_id}**", parse_mode='Markdown')
    except ValueError:
        await message.answer("❌ **معرف المستخدم غير صحيح**", parse_mode='Markdown')


@router.message(F.text == "✅ فك حظر")
async def unban_start(message: Message, state: FSMContext):
    """Start unban user process"""
    if not is_admin(message.from_user.id):
        return
    await message.answer("✅ **أدخل معرف المستخدم لفك الحظر:**\nمثال: /unban 123456789", parse_mode='Markdown')
    await state.set_state(AdminReplyStates.WAITING_UNBAN_USER)


@router.message(Command("unban"))
async def unban_user(message: Message):
    """Unban user by command"""
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("⚠️ **استخدم:** `/unban معرف_المستخدم`", parse_mode='Markdown')
        return
    try:
        user_id = int(parts[1])
        db.unban_user(user_id)
        db.log_admin_action(message.from_user.id, 'unban', user_id)
        await message.bot.send_message(user_id, "✅ **تم فك حظرك، يمكنك استخدام البوت مرة أخرى**", parse_mode='Markdown')
        await message.answer(f"✅ **تم فك حظر المستخدم {user_id}**", parse_mode='Markdown')
    except ValueError:
        await message.answer("❌ **معرف المستخدم غير صحيح**", parse_mode='Markdown')


# ========== Tickets Management ==========
@router.message(F.text == "📝 التذاكر")
async def show_tickets(message: Message):
    """Show open tickets"""
    if not is_admin(message.from_user.id):
        return
    
    tickets = db.get_open_tickets()
    if not tickets:
        await message.answer("📭 **لا توجد تذاكر مفتوحة**", parse_mode='Markdown')
        return
    
    text = "🎫 **التذاكر المفتوحة**\n\n"
    for ticket in tickets[:15]:
        text += f"📌 `{ticket['ticket_number']}`\n"
        text += f"👤 المستخدم: {ticket['user_id']}\n"
        text += f"📦 النوع: {ticket['ticket_type']}\n"
        text += f"📅 {ticket['created_at'][:16]}\n"
        text += "─" * 20 + "\n"
    
    if len(tickets) > 15:
        text += f"\n... و {len(tickets) - 15} تذكرة أخرى"
    
    await message.answer(text, parse_mode='Markdown')


@router.callback_query(F.data.startswith("reply_ticket_"))
async def reply_to_ticket(callback: CallbackQuery, state: FSMContext):
    """Reply to a ticket"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ غير مصرح", show_alert=True)
        return
    
    ticket_number = callback.data.split('_')[2]
    ticket = db.get_ticket(ticket_number)
    if not ticket:
        await callback.answer("التذكرة غير موجودة", show_alert=True)
        return
    
    await state.update_data(reply_ticket_number=ticket_number, reply_ticket_user=ticket['user_id'])
    await state.set_state(AdminReplyStates.WAITING_REPLY)
    await callback.message.answer(f"💬 **اكتب ردك على التذكرة {ticket_number}:**", parse_mode='Markdown')
    await callback.answer()


# ========== Logs ==========
@router.message(F.text == "📜 السجلات")
async def show_logs(message: Message):
    """Show admin logs"""
    if not is_admin(message.from_user.id):
        return
    
    logs = db.get_admin_logs(30)
    if not logs:
        await message.answer("📭 **لا توجد سجلات**", parse_mode='Markdown')
        return
    
    text = "📜 **آخر السجلات**\n\n"
    for log in logs:
        text += f"🕐 {log['timestamp'][:16]}\n"
        text += f"👑 {log['action']}\n"
        if log['target_user']:
            text += f"🎯 المستخدم: {log['target_user']}\n"
        if log['order_number']:
            text += f"📦 الطلب: {log['order_number']}\n"
        text += "─" * 20 + "\n"
    
    await message.answer(text, parse_mode='Markdown')


# ========== Control Bot (Send Messages/Photos/Videos) ==========
@router.message(F.text == "🎮 تحكم في البوت")
async def control_bot_start(message: Message, state: FSMContext):
    """Start bot control menu"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
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
        await message.answer("⚠️ **استخدم:** `/sendtext معرف_المستخدم النص`", parse_mode='Markdown')
        return
    
    try:
        user_id = int(parts[1])
        text = parts[2]
        await message.bot.send_message(user_id, f"📨 **رسالة من الإدارة:**\n\n{text}", parse_mode='Markdown')
        await message.answer(f"✅ **تم إرسال الرسالة للمستخدم {user_id}**", parse_mode='Markdown')
        db.log_admin_action(message.from_user.id, 'send_text', user_id, None, text[:100])
    except Exception as e:
        await message.answer(f"❌ **خطأ:** {e}", parse_mode='Markdown')


@router.message(Command("sendphoto"))
async def send_photo_to_user(message: Message, state: FSMContext):
    """Send photo to specific user"""
    if not is_admin(message.from_user.id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("⚠️ **استخدم:** `/sendphoto معرف_المستخدم`\nثم أرسل الصورة", parse_mode='Markdown')
        return
    
    try:
        user_id = int(parts[1])
        await state.update_data(send_photo_to=user_id)
        await message.answer(f"📸 **أرسل الصورة التي تريد إرسالها للمستخدم {user_id}**", parse_mode='Markdown')
        await state.set_state(AdminControlStates.WAITING_PHOTO)
    except ValueError:
        await message.answer("❌ **معرف المستخدم غير صحيح**", parse_mode='Markdown')


@router.message(AdminControlStates.WAITING_PHOTO, F.photo)
async def handle_send_photo(message: Message, state: FSMContext):
    """Handle sending photo"""
    if not is_admin(message.from_user.id):
        return
    
    data = await state.get_data()
    user_id = data.get('send_photo_to')
    if not user_id:
        await message.answer("❌ **حدث خطأ، حاول مرة أخرى**")
        await state.clear()
        return
    
    photo = message.photo[-1]
    await message.bot.send_photo(user_id, photo.file_id, caption="📸 **صورة من الإدارة**")
    await message.answer(f"✅ **تم إرسال الصورة للمستخدم {user_id}**")
    db.log_admin_action(message.from_user.id, 'send_photo', user_id)
    await state.clear()


@router.message(Command("sendvideo"))
async def send_video_to_user(message: Message, state: FSMContext):
    """Send video to specific user"""
    if not is_admin(message.from_user.id):
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("⚠️ **استخدم:** `/sendvideo معرف_المستخدم`\nثم أرسل الفيديو", parse_mode='Markdown')
        return
    
    try:
        user_id = int(parts[1])
        await state.update_data(send_video_to=user_id)
        await message.answer(f"🎥 **أرسل الفيديو الذي تريد إرساله للمستخدم {user_id}**", parse_mode='Markdown')
        await state.set_state(AdminControlStates.WAITING_VIDEO)
    except ValueError:
        await message.answer("❌ **معرف المستخدم غير صحيح**", parse_mode='Markdown')


@router.message(AdminControlStates.WAITING_VIDEO, F.video)
async def handle_send_video(message: Message, state: FSMContext):
    """Handle sending video"""
    if not is_admin(message.from_user.id):
        return
    
    data = await state.get_data()
    user_id = data.get('send_video_to')
    if not user_id:
        await message.answer("❌ **حدث خطأ، حاول مرة أخرى**")
        await state.clear()
        return
    
    video = message.video
    await message.bot.send_video(user_id, video.file_id, caption="🎥 **فيديو من الإدارة**")
    await message.answer(f"✅ **تم إرسال الفيديو للمستخدم {user_id}**")
    db.log_admin_action(message.from_user.id, 'send_video', user_id)
    await state.clear()


# ========== Admin Reply Handler ==========
@router.message(AdminReplyStates.WAITING_REPLY)
async def send_admin_reply(message: Message, state: FSMContext):
    """Send admin reply"""
    if not is_admin(message.from_user.id):
        return
    
    data = await state.get_data()
    user_id = data.get('reply_to_user') or data.get('reply_ticket_user')
    ticket_number = data.get('reply_ticket_number')
    
    if not user_id:
        await message.answer("❌ حدث خطأ، حاول مرة أخرى")
        await state.clear()
        return
    
    # Send reply to user
    await message.bot.send_message(user_id, f"📨 **رد من الدعم:**\n{message.text}", parse_mode='Markdown')
    await message.answer(f"✅ **تم إرسال الرد للمستخدم {user_id}**")
    
    # Log and clear
    db.log_admin_action(message.from_user.id, 'admin_reply', user_id, ticket_number, message.text[:100])
    await state.clear()


# ========== Chat Session Handlers ==========
@router.message(AdminReplyStates.WAITING_BAN_USER)
async def process_ban(message: Message, state: FSMContext):
    """Process ban from admin panel"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        user_id = int(message.text.strip())
        db.ban_user(user_id)
        db.log_admin_action(message.from_user.id, 'ban', user_id)
        await message.bot.send_message(user_id, "🚫 **تم حظرك من البوت**", parse_mode='Markdown')
        await message.answer(f"✅ **تم حظر المستخدم {user_id}**", parse_mode='Markdown')
    except ValueError:
        await message.answer("❌ **معرف المستخدم غير صحيح**", parse_mode='Markdown')
    finally:
        await state.clear()


@router.message(AdminReplyStates.WAITING_UNBAN_USER)
async def process_unban(message: Message, state: FSMContext):
    """Process unban from admin panel"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        user_id = int(message.text.strip())
        db.unban_user(user_id)
        db.log_admin_action(message.from_user.id, 'unban', user_id)
        await message.bot.send_message(user_id, "✅ **تم فك حظرك، يمكنك استخدام البوت مرة أخرى**", parse_mode='Markdown')
        await message.answer(f"✅ **تم فك حظر المستخدم {user_id}**", parse_mode='Markdown')
    except ValueError:
        await message.answer("❌ **معرف المستخدم غير صحيح**", parse_mode='Markdown')
    finally:
        await state.clear()


def register_admin_handlers(dp):
    """Register all admin handlers"""
    dp.include_router(router)
