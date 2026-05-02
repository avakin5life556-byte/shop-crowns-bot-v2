from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
import json
import logging
from bot.database.db import db  # تصحيح المسار
from bot.keyboards.inline import get_paid_orders_keyboard, get_order_admin_keyboard, get_back_keyboard
from bot.keyboards.reply import get_main_keyboard
from bot.states.order_states import PaidOrderStates
from bot.config import ADMIN_ID, TIMEZONE
from bot.utils.helpers import is_rate_limited

# إعداد logging
logger = logging.getLogger(__name__)

router = Router()

# تعريف أزرار طلبات الشراء مع النصوص ثنائية اللغة
PAID_ORDERS = {
    'buy_crowns': {
        'ar': '🟣 شراء كراونز',
        'en': '🟣 Buy Crowns',
        'type': 'شراء كراونز'
    },
    'buy_coins': {
        'ar': '🟡 شراء كوينز',
        'en': '🟡 Buy Coins',
        'type': 'شراء كوينز'
    },
    'buy_vip': {
        'ar': '💳 شراء عضويات',
        'en': '💳 Buy VIP',
        'type': 'شراء عضوية VIP'
    },
    'boost_account': {
        'ar': '🤖 تعزيز الحسابات',
        'en': '🤖 Boost Account',
        'type': 'تعزيز الحساب'
    },
    'buy_likes': {
        'ar': '❤️ لايكات ومشاهدات',
        'en': '❤️ Likes & Views',
        'type': 'لايكات ومشاهدات'
    },
    'other_games': {
        'ar': '🎮 ألعاب أخرى',
        'en': '🎮 Other Games',
        'type': 'ألعاب أخرى'
    }
}


def safe_get_text(lang: str, key: str, default_ar: str = "", default_en: str = "") -> str:
    """دالة آمنة للحصول على النصوص مع fallback"""
    if key == 'banned':
        return "🚫 **تم حظرك من البوت**" if lang == 'ar' else "🚫 **You are banned**"
    elif key == 'rate_limited':
        return "⚠️ **أرسلت طلبات كثيرة، انتظر قليلاً**" if lang == 'ar' else "⚠️ **Too many requests, wait**"
    elif key == 'ticket_created':
        return "✅ **تم فتح تذكرة دعم لطلبك**" if lang == 'ar' else "✅ **Support ticket opened for your request**"
    elif key == 'order_completed':
        return "✅ **تم تنفيذ طلبك بنجاح**\n\nيمكنك مراجعة حسابك الآن.\nشكراً لاستخدامك متجرنا 🤍" if lang == 'ar' else "✅ **Your order has been completed successfully**\n\nYou can check your account now.\nThank you for using our store 🤍"
    elif key == 'order_processing':
        return "🔄 **جاري تنفيذ طلبك**\n\nسيتم إعلامك عند الانتهاء.\nشكراً لانتظارك 🤍" if lang == 'ar' else "🔄 **Your order is being processed**\n\nYou will be notified when completed.\nThank you for your patience 🤍"
    elif key == 'order_cancelled':
        return "❌ **تم إلغاء طلبك**\n\nعذراً، تم إلغاء طلبك.\nيمكنك التواصل مع الدعم الفني لمزيد من المعلومات." if lang == 'ar' else "❌ **Your order has been cancelled**\n\nSorry, your order has been cancelled.\nYou can contact support for more information."
    elif key == 'no_active_ticket':
        return "⚠️ **لا توجد تذكرة نشطة لهذا المستخدم**" if lang == 'ar' else "⚠️ **No active ticket for this user**"
    elif key == 'ticket_reopened':
        return "✅ **تم إعادة فتح التذكرة**" if lang == 'ar' else "✅ **Ticket reopened**"
    
    return default_ar if lang == 'ar' else default_en


def safe_get_order_info(order_key: str, lang: str) -> dict:
    """الحصول على معلومات الطلب بشكل آمن"""
    try:
        order_info = PAID_ORDERS.get(order_key, {})
        return {
            'name': order_info.get(lang, order_info.get('ar', 'طلب')),
            'type': order_info.get('type', 'طلب')
        }
    except Exception as e:
        logger.error(f"Error getting order info for {order_key}: {e}")
        return {'name': 'طلب', 'type': 'طلب'}


def safe_split_callback(callback_data: str, expected_parts: int = 3) -> list:
    """تقسيم بيانات الكول باك بشكل آمن"""
    try:
        parts = callback_data.split('_')
        if len(parts) < expected_parts:
            logger.error(f"Invalid callback data format: {callback_data}, expected {expected_parts} parts, got {len(parts)}")
            return []
        return parts
    except Exception as e:
        logger.error(f"Error splitting callback data {callback_data}: {e}")
        return []


# ========== القائمة الرئيسية لطلبات الشراء ==========
@router.message(F.text.in_({'💰 طلبات الشراء', '💰 Purchase Requests'}))
async def show_paid_orders(message: Message):
    """عرض قائمة طلبات الشراء"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await message.answer(safe_get_text(lang, 'banned'), parse_mode='Markdown')
        return
    
    title = "💰 **طلبات الشراء**\n\nاختر الخدمة التي تريدها:" if lang == 'ar' else "💰 **Purchase Requests**\n\nChoose the service you want:"
    
    await message.answer(
        title,
        reply_markup=get_paid_orders_keyboard(lang),
        parse_mode='Markdown'
    )


# ========== معالج اختيار أي زر من أزرار الشراء ==========
@router.callback_query(F.data.in_(PAID_ORDERS.keys()))
async def handle_paid_order(callback: CallbackQuery, state: FSMContext):
    """معالج اختيار خدمة مدفوعة - فتح تذكرة دعم"""
    user_id = callback.from_user.id
    order_key = callback.data
    lang = db.get_user_language(user_id)
    
    # التحقق من وجود callback.data
    if not callback.data:
        await callback.answer("❌ حدث خطأ", show_alert=True)
        return
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await callback.answer(safe_get_text(lang, 'banned'), show_alert=True)
        return
    
    # التحقق من معدل الطلبات
    try:
        if is_rate_limited(user_id, 'paid_order', limit=5, window=300):
            await callback.answer(safe_get_text(lang, 'rate_limited'), show_alert=True)
            return
    except Exception as e:
        logger.error(f"Rate limit error for user {user_id}: {e}")
    
    # الحصول على معلومات الطلب
    order_info = safe_get_order_info(order_key, lang)
    order_name = order_info['name']
    order_type = order_info['type']
    
    # إنشاء تذكرة دعم
    ticket_data = db.create_ticket(user_id, 'paid_order', f'طلب {order_type} - تم فتح تذكرة')
    
    if not ticket_data or not ticket_data[0] or not ticket_data[1]:
        logger.error(f"Failed to create ticket for user {user_id}")
        await callback.answer("❌ حدث خطأ في فتح التذكرة", show_alert=True)
        return
    
    ticket_number, ticket_id = ticket_data
    
    # تخزين معلومات الطلب في FSM
    await state.update_data(
        order_key=order_key,
        order_type=order_type,
        ticket_id=ticket_id,
        ticket_number=ticket_number
    )
    
    # إرسال تأكيد للمستخدم
    success_text = (
        f"✅ **تم فتح تذكرة دعم لطلبك**\n\n"
        f"📦 **الخدمة:** {order_name}\n"
        f"🎫 **رقم التذكرة:** `{ticket_number}`\n\n"
        f"💬 سيتم التواصل معك قريباً لإتمام الطلب.\n"
        f"يمكنك متابعة طلبك عبر الدعم الفني."
    )
    
    try:
        await callback.message.edit_text(
            success_text,
            reply_markup=get_back_keyboard(lang),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error editing message for user {user_id}: {e}")
        await callback.message.answer(success_text, parse_mode='Markdown')
    
    # إرسال إشعار للأدمن
    user_info = db.get_user_info(user_id)
    now = datetime.now(TIMEZONE)
    
    user_name = user_info.get('name', 'غير معروف') if user_info else 'غير معروف'
    user_username = user_info.get('username', 'لا يوجد') if user_info else 'لا يوجد'
    user_country = user_info.get('country', 'غير معروف') if user_info else 'غير معروف'
    
    admin_msg = (
        f"💰 **طلب شراء جديد**\n\n"
        f"🎫 **رقم التذكرة:** `{ticket_number}`\n"
        f"📦 **الخدمة:** {order_type}\n"
        f"👤 **الاسم:** {user_name}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"📝 **Username:** @{user_username}\n"
        f"🗣️ **اللغة:** {lang}\n"
        f"🌍 **الدولة:** {user_country}\n"
        f"📅 **التاريخ:** {now.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"استخدم الأزرار أدناه للتحكم في الطلب:"
    )
    
    # إنشاء رقم طلب وهمي للتتبع (سيتم إنشاء طلب حقيقي عند التنفيذ)
    temp_order_number = f"PO-{now.strftime('%Y%m%d%H%M%S')}"
    
    try:
        await callback.bot.send_message(
            ADMIN_ID,
            admin_msg,
            reply_markup=get_order_admin_keyboard(temp_order_number, user_id),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Failed to send admin notification for user {user_id}: {e}")
    
    # تسجيل إجراء الأدمن
    try:
        db.log_admin_action(ADMIN_ID, 'paid_order_request', user_id, None, f'طلب {order_type}')
    except Exception as e:
        logger.error(f"Failed to log admin action: {e}")
    
    await callback.answer()
    logger.info(f"User {user_id} created paid order ticket {ticket_number} for {order_type}")


# ========== معالج أزرار التحكم في الطلبات للأدمن ==========
@router.callback_query(F.data.startswith(('done_', 'exec_', 'cancel_')))
async def handle_paid_order_actions(callback: CallbackQuery, state: FSMContext):
    """معالج أزرار التحكم في طلبات الشراء"""
    # التحقق من صلاحيات الأدمن
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ غير مصرح لك بهذا الأمر", show_alert=True)
        return
    
    # تقسيم البيانات بشكل آمن
    parts = safe_split_callback(callback.data, 3)
    if not parts or len(parts) < 3:
        await callback.answer("❌ بيانات غير صالحة", show_alert=True)
        return
    
    action = parts[0]
    order_number = parts[1]
    
    # تحويل user_id إلى int مع التحقق
    try:
        user_id = int(parts[2])
    except (ValueError, IndexError) as e:
        logger.error(f"Error converting user_id in callback {callback.data}: {e}")
        await callback.answer("❌ معرف المستخدم غير صالح", show_alert=True)
        return
    
    lang = db.get_user_language(user_id)
    
    # الحصول على معلومات التذكرة المفتوحة للمستخدم
    active_ticket = db.get_active_ticket_by_user(user_id)
    
    if not active_ticket:
        await callback.answer(safe_get_text(lang, 'no_active_ticket'), show_alert=True)
        return
    
    ticket_number = active_ticket.get('ticket_number')
    if not ticket_number:
        await callback.answer("❌ رقم التذكرة غير موجود", show_alert=True)
        return
    
    # تنفيذ الإجراء المطلوب
    try:
        if action == 'done':
            # تحديث حالة التذكرة
            db.update_ticket_status(ticket_number, 'completed')
            
            # تسجيل الإجراء
            db.log_admin_action(ADMIN_ID, 'order_completed', user_id, order_number, f'طلب شراء')
            
            # إرسال إشعار للمستخدم
            await callback.bot.send_message(
                user_id,
                safe_get_text(lang, 'order_completed'),
                parse_mode='Markdown'
            )
            
            await callback.message.edit_text(f"✅ **تم تنفيذ طلب الشراء للمستخدم {user_id}**")
            await callback.answer("✅ تم تنفيذ الطلب")
            logger.info(f"Admin completed order {order_number} for user {user_id}")
        
        elif action == 'exec':
            # تحديث حالة التذكرة
            db.update_ticket_status(ticket_number, 'processing')
            
            # تسجيل الإجراء
            db.log_admin_action(ADMIN_ID, 'order_processing', user_id, order_number, f'طلب شراء')
            
            # إرسال إشعار للمستخدم
            await callback.bot.send_message(
                user_id,
                safe_get_text(lang, 'order_processing'),
                parse_mode='Markdown'
            )
            
            await callback.message.edit_text(f"🔄 **جاري تنفيذ طلب الشراء للمستخدم {user_id}**")
            await callback.answer("⏳ تم بدء التنفيذ")
            logger.info(f"Admin started processing order {order_number} for user {user_id}")
        
        elif action == 'cancel':
            # تحديث حالة التذكرة
            db.update_ticket_status(ticket_number, 'cancelled')
            
            # تسجيل الإجراء
            db.log_admin_action(ADMIN_ID, 'order_cancelled', user_id, order_number, f'طلب شراء')
            
            # إرسال إشعار للمستخدم
            await callback.bot.send_message(
                user_id,
                safe_get_text(lang, 'order_cancelled'),
                parse_mode='Markdown'
            )
            
            await callback.message.edit_text(f"❌ **تم إلغاء طلب الشراء للمستخدم {user_id}**")
            await callback.answer("❌ تم إلغاء الطلب")
            logger.info(f"Admin cancelled order {order_number} for user {user_id}")
        
        else:
            await callback.answer("❌ إجراء غير معروف", show_alert=True)
            return
        
        # تحديث واجهة الأدمن
        user_info = db.get_user_info(user_id)
        now = datetime.now(TIMEZONE)
        
        user_name = user_info.get('name', 'غير معروف') if user_info else 'غير معروف'
        
        status_text = {
            'done': '✅ مكتمل',
            'exec': '🔄 قيد التنفيذ',
            'cancel': '❌ ملغي'
        }
        
        await callback.message.edit_text(
            f"💰 **تحديث طلب شراء**\n\n"
            f"📌 **الحالة:** {status_text[action]}\n"
            f"👤 **المستخدم:** {user_name}\n"
            f"🆔 **المعرف:** {user_id}\n"
            f"📅 **التاريخ:** {now.strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error in handle_paid_order_actions for {action}: {e}")
        await callback.answer("❌ حدث خطأ أثناء معالجة الطلب", show_alert=True)


# ========== عرض تذاكر الشراء المفتوحة ==========
@router.message(F.text == "🛒 طلبات الشراء")
async def show_paid_orders_admin(message: Message):
    """عرض تذاكر طلبات الشراء المفتوحة للأدمن"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        tickets = db.get_open_tickets_by_type('paid_order')
        
        if not tickets:
            await message.answer("📭 **لا توجد طلبات شراء مفتوحة حالياً**", parse_mode='Markdown')
            return
        
        text = "🛒 **طلبات الشراء المفتوحة**\n\n"
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
            text += f"\n... و {len(tickets) - 15} طلب آخر"
        
        await message.answer(text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error showing paid orders for admin: {e}")
        await message.answer("❌ حدث خطأ في عرض الطلبات", parse_mode='Markdown')


# ========== إعادة فتح تذكرة ==========
@router.callback_query(F.data.startswith("reopen_ticket_"))
async def reopen_ticket(callback: CallbackQuery):
    """إعادة فتح تذكرة مغلقة"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ غير مصرح", show_alert=True)
        return
    
    # تقسيم البيانات بشكل آمن
    parts = safe_split_callback(callback.data, 2)
    if not parts or len(parts) < 2:
        await callback.answer("❌ بيانات غير صالحة", show_alert=True)
        return
    
    ticket_number = parts[1] if len(parts) > 1 else None
    
    if not ticket_number:
        await callback.answer("❌ رقم التذكرة غير موجود", show_alert=True)
        return
    
    try:
        db.update_ticket_status(ticket_number, 'open')
        await callback.answer("✅ تم إعادة فتح التذكرة")
        await callback.message.edit_text(f"✅ **تم إعادة فتح التذكرة {ticket_number}**")
        logger.info(f"Admin reopened ticket {ticket_number}")
    except Exception as e:
        logger.error(f"Error reopening ticket {ticket_number}: {e}")
        await callback.answer("❌ حدث خطأ في إعادة فتح التذكرة", show_alert=True)


def register_paid_orders_handlers(dp):
    """تسجيل معالجات طلبات الشراء"""
    dp.include_router(router)
    logger.info("تم تسجيل معالجات طلبات الشراء بنجاح")
