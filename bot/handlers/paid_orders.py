from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
import json
import pytz
from bot.database import db
from bot.keyboards.inline import get_paid_orders_keyboard, get_order_admin_keyboard, get_back_keyboard
from bot.keyboards.reply import get_main_keyboard
from bot.states.order_states import PaidOrderStates
from bot.config import ADMIN_ID, TIMEZONE
from bot.utils.helpers import is_rate_limited

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


# ========== القائمة الرئيسية لطلبات الشراء ==========
@router.message(F.text.in_({'💰 طلبات الشراء', '💰 Purchase Requests'}))
async def show_paid_orders(message: Message):
    """عرض قائمة طلبات الشراء"""
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    if db.is_user_banned(user_id):
        await message.answer("🚫 تم حظرك من البوت" if lang == 'ar' else "🚫 You are banned", parse_mode='Markdown')
        return
    
    await message.answer(
        "💰 **طلبات الشراء**\n\nاختر الخدمة التي تريدها:" if lang == 'ar' else "💰 **Purchase Requests**\n\nChoose the service you want:",
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
    
    # التحقق من الحظر
    if db.is_user_banned(user_id):
        await callback.answer("🚫 تم حظرك من البوت" if lang == 'ar' else "🚫 You are banned", show_alert=True)
        return
    
    # التحقق من معدل الطلبات
    if is_rate_limited(user_id, 'paid_order', limit=5, window=300):
        await callback.answer("⚠️ أرسلت طلبات كثيرة، انتظر قليلاً" if lang == 'ar' else "⚠️ Too many requests, wait", show_alert=True)
        return
    
    # الحصول على معلومات الطلب
    order_info = PAID_ORDERS[order_key]
    order_name_ar = order_info['ar']
    order_name_en = order_info['en']
    order_type = order_info['type']
    
    # إنشاء تذكرة دعم
    ticket_number, ticket_id = db.create_ticket(
        user_id, 
        'paid_order', 
        f'طلب {order_type} - تم فتح تذكرة'
    )
    
    # تخزين معلومات الطلب في FSM
    await state.update_data(
        order_key=order_key,
        order_type=order_type,
        ticket_id=ticket_id,
        ticket_number=ticket_number
    )
    
    # إرسال تأكيد للمستخدم
    await callback.message.edit_text(
        f"✅ **تم فتح تذكرة دعم لطلبك**\n\n"
        f"📦 **الخدمة:** {order_name_ar if lang == 'ar' else order_name_en}\n"
        f"🎫 **رقم التذكرة:** `{ticket_number}`\n\n"
        f"💬 سيتم التواصل معك قريباً لإتمام الطلب.\n"
        f"يمكنك متابعة طلبك عبر الدعم الفني.",
        reply_markup=get_back_keyboard(lang),
        parse_mode='Markdown'
    )
    
    # إرسال إشعار للأدمن
    user_info = db.get_user_info(user_id)
    now = datetime.now(TIMEZONE)
    
    admin_msg = (
        f"💰 **طلب شراء جديد**\n\n"
        f"🎫 **رقم التذكرة:** `{ticket_number}`\n"
        f"📦 **الخدمة:** {order_name_ar}\n"
        f"👤 **الاسم:** {user_info['name'] if user_info else 'غير معروف'}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"📝 **Username:** @{user_info['username'] if user_info else 'لا يوجد'}\n"
        f"🗣️ **اللغة:** {lang}\n"
        f"🌍 **الدولة:** {user_info['country'] if user_info else 'غير معروف'}\n"
        f"📅 **التاريخ:** {now.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"استخدم الأزرار أدناه للتحكم في الطلب:"
    )
    
    # إنشاء رقم طلب وهمي للتتبع (سيتم إنشاء طلب حقيقي عند التنفيذ)
    temp_order_number = f"PO-{now.strftime('%Y%m%d%H%M%S')}"
    
    await callback.bot.send_message(
        ADMIN_ID,
        admin_msg,
        reply_markup=get_order_admin_keyboard(temp_order_number, user_id),
        parse_mode='Markdown'
    )
    
    # تسجيل إجراء الأدمن
    db.log_admin_action(ADMIN_ID, 'paid_order_request', user_id, None, f'طلب {order_type}')
    
    await callback.answer()


# ========== معالج أزرار التحكم في الطلبات للأدمن ==========
@router.callback_query(F.data.startswith(('done_', 'exec_', 'cancel_')))
async def handle_paid_order_actions(callback: CallbackQuery, state: FSMContext):
    """معالج أزرار التحكم في طلبات الشراء"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ غير مصرح لك بهذا الأمر", show_alert=True)
        return
    
    action, order_number, user_id = callback.data.split('_')
    user_id = int(user_id)
    lang = db.get_user_language(user_id)
    
    # الحصول على معلومات التذكرة المفتوحة للمستخدم
    active_ticket = db.get_active_ticket_by_user(user_id)
    
    if not active_ticket:
        await callback.answer("⚠️ لا توجد تذكرة نشطة لهذا المستخدم", show_alert=True)
        return
    
    ticket_number = active_ticket['ticket_number']
    
    # ✅ تم التنفيذ
    if action == 'done':
        # تحديث حالة التذكرة
        db.update_ticket_status(ticket_number, 'completed')
        
        # تسجيل الإجراء
        db.log_admin_action(ADMIN_ID, 'order_completed', user_id, order_number, f'طلب شراء')
        
        # إرسال إشعار للمستخدم
        await callback.bot.send_message(
            user_id,
            "✅ **تم تنفيذ طلبك بنجاح**\n\nيمكنك مراجعة حسابك الآن.\nشكراً لاستخدامك متجرنا 🤍",
            parse_mode='Markdown'
        )
        
        await callback.message.edit_text(f"✅ **تم تنفيذ طلب الشراء للمستخدم {user_id}**")
        await callback.answer("✅ تم تنفيذ الطلب")
    
    # ⏳ جاري التنفيذ
    elif action == 'exec':
        # تحديث حالة التذكرة
        db.update_ticket_status(ticket_number, 'processing')
        
        # تسجيل الإجراء
        db.log_admin_action(ADMIN_ID, 'order_processing', user_id, order_number, f'طلب شراء')
        
        # إرسال إشعار للمستخدم
        await callback.bot.send_message(
            user_id,
            "🔄 **جاري تنفيذ طلبك**\n\nسيتم إعلامك عند الانتهاء.\nشكراً لانتظارك 🤍",
            parse_mode='Markdown'
        )
        
        await callback.message.edit_text(f"🔄 **جاري تنفيذ طلب الشراء للمستخدم {user_id}**")
        await callback.answer("⏳ تم بدء التنفيذ")
    
    # ❌ إلغاء
    elif action == 'cancel':
        # تحديث حالة التذكرة
        db.update_ticket_status(ticket_number, 'cancelled')
        
        # تسجيل الإجراء
        db.log_admin_action(ADMIN_ID, 'order_cancelled', user_id, order_number, f'طلب شراء')
        
        # إرسال إشعار للمستخدم
        await callback.bot.send_message(
            user_id,
            "❌ **تم إلغاء طلبك**\n\nعذراً، تم إلغاء طلبك.\nيمكنك التواصل مع الدعم الفني لمزيد من المعلومات.",
            parse_mode='Markdown'
        )
        
        await callback.message.edit_text(f"❌ **تم إلغاء طلب الشراء للمستخدم {user_id}**")
        await callback.answer("❌ تم إلغاء الطلب")
    
    # تحديث واجهة الأدمن
    user_info = db.get_user_info(user_id)
    now = datetime.now(TIMEZONE)
    
    status_text = {
        'done': '✅ مكتمل',
        'exec': '🔄 قيد التنفيذ',
        'cancel': '❌ ملغي'
    }
    
    await callback.message.edit_text(
        f"💰 **تحديث طلب شراء**\n\n"
        f"📌 **الحالة:** {status_text[action]}\n"
        f"👤 **المستخدم:** {user_info['name'] if user_info else 'غير معروف'}\n"
        f"🆔 **المعرف:** {user_id}\n"
        f"📅 **التاريخ:** {now.strftime('%Y-%m-%d %H:%M:%S')}",
        parse_mode='Markdown'
    )


# ========== عرض تذاكر الشراء المفتوحة ==========
@router.message(F.text == "🛒 طلبات الشراء")
async def show_paid_orders_admin(message: Message):
    """عرض تذاكر طلبات الشراء المفتوحة للأدمن"""
    if message.from_user.id != ADMIN_ID:
        return
    
    tickets = db.get_open_tickets_by_type('paid_order')
    
    if not tickets:
        await message.answer("📭 **لا توجد طلبات شراء مفتوحة حالياً**", parse_mode='Markdown')
        return
    
    text = "🛒 **طلبات الشراء المفتوحة**\n\n"
    for ticket in tickets[:15]:
        user_info = db.get_user_info(ticket['user_id'])
        text += f"🎫 `{ticket['ticket_number']}`\n"
        text += f"👤 {user_info['name'] if user_info else 'غير معروف'}\n"
        text += f"🆔 `{ticket['user_id']}`\n"
        text += f"📅 {ticket['created_at'][:16]}\n"
        text += "─" * 20 + "\n"
    
    if len(tickets) > 15:
        text += f"\n... و {len(tickets) - 15} طلب آخر"
    
    await message.answer(text, parse_mode='Markdown')


# ========== إعادة فتح تذكرة ==========
@router.callback_query(F.data.startswith("reopen_ticket_"))
async def reopen_ticket(callback: CallbackQuery):
    """إعادة فتح تذكرة مغلقة"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("⛔ غير مصرح", show_alert=True)
        return
    
    ticket_number = callback.data.split('_')[2]
    db.update_ticket_status(ticket_number, 'open')
    
    await callback.answer("✅ تم إعادة فتح التذكرة")
    await callback.message.edit_text(f"✅ **تم إعادة فتح التذكرة {ticket_number}**")


def register_paid_orders_handlers(dp):
    """تسجيل معالجات طلبات الشراء"""
    dp.include_router(router)
