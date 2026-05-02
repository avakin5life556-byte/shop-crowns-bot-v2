from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# ========= Yes / No =========

def get_yes_no_keyboard() -> InlineKeyboardMarkup:
    """Yes/No inline keyboard"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ نعم", callback_data="yes")
    builder.button(text="❌ لا", callback_data="no")
    builder.adjust(2)
    return builder.as_markup()


def get_continue_keyboard() -> InlineKeyboardMarkup:
    """Confirmation continue keyboard"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ نعم", callback_data="continue_yes")
    builder.button(text="❌ لا", callback_data="continue_no")
    builder.adjust(2)
    return builder.as_markup()


# ========= Rating =========

def get_rating_keyboard() -> InlineKeyboardMarkup:
    """Rating keyboard (1-5 stars)"""
    builder = InlineKeyboardBuilder()
    for i in range(1, 6):
        builder.button(text="⭐" * i, callback_data=f"rate_{i}")
    builder.adjust(5)
    return builder.as_markup()


def get_support_rating_keyboard() -> InlineKeyboardMarkup:
    """Support rating keyboard (1-5 stars)"""
    builder = InlineKeyboardBuilder()
    for i in range(1, 6):
        builder.button(text="⭐" * i, callback_data=f"support_rate_{i}")
    builder.adjust(5)
    return builder.as_markup()


# ========= الدردشة (Chat) =========

def get_live_chat_keyboard(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Live chat keyboard for users"""
    text = "🔚 إنهاء المحادثة" if lang == 'ar' else "🔚 End Chat"
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data="end_chat")
    builder.adjust(1)
    return builder.as_markup()


def get_end_chat_keyboard() -> InlineKeyboardMarkup:
    """End chat keyboard"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔚 إنهاء المحادثة", callback_data="end_chat")
    builder.adjust(1)
    return builder.as_markup()


def get_admin_chat_keyboard(user_id: int, chat_session_id: int) -> InlineKeyboardMarkup:
    """Admin chat control keyboard"""
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 رد", callback_data=f"admin_reply_complaint_{user_id}_{chat_session_id}")
    builder.button(text="🔚 إنهاء", callback_data=f"admin_end_chat_complaint_{user_id}_{chat_session_id}")
    builder.adjust(2)
    return builder.as_markup()


# ========= أزرار عامة (General) =========

def get_contact_button(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Contact us button"""
    text = "💬 تواصل بنا" if lang == 'ar' else "💬 Contact Us"
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data="contact_us")
    builder.adjust(1)
    return builder.as_markup()


def get_back_button(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Back button"""
    text = "🔙 رجوع" if lang == 'ar' else "🔙 Back"
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data="back_main")
    builder.adjust(1)
    return builder.as_markup()


def get_back_to_menu_keyboard(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Back to main menu keyboard"""
    text = "🏠 القائمة الرئيسية" if lang == 'ar' else "🏠 Main Menu"
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data="back_main")
    builder.adjust(1)
    return builder.as_markup()


def get_cancel_keyboard(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Cancel operation keyboard"""
    text = "❌ إلغاء" if lang == 'ar' else "❌ Cancel"
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data="cancel")
    builder.adjust(1)
    return builder.as_markup()


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Language selection keyboard"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🇸🇦 العربية", callback_data="lang_ar")
    builder.button(text="🇺🇸 English", callback_data="lang_en")
    builder.adjust(2)
    return builder.as_markup()


# ========= المودات (Mods) =========

def get_mods_keyboard(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Mods selection keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="☁️ Sky Mod", callback_data="mod_sky")
    builder.button(text="🐂 Bull Mod", callback_data="mod_bull")
    builder.button(text="⭐ Gold Mod", callback_data="mod_gold")
    
    back_text = "🔙 رجوع" if lang == 'ar' else "🔙 Back"
    builder.button(text=back_text, callback_data="back_main")
    
    builder.adjust(1)
    return builder.as_markup()


# ========= الطلبات المجانية (Free Orders) =========

def get_free_orders_keyboard(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Free orders keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="✏️ تغيير الاسم" if lang == 'ar' else "✏️ Change Name", callback_data="change_name")
    builder.button(text="🖼 تغيير الصورة" if lang == 'ar' else "🖼 Change Photo", callback_data="change_photo")
    builder.button(text="📌 المزيد" if lang == 'ar' else "📌 More", callback_data="more_options")
    
    back_text = "🔙 رجوع" if lang == 'ar' else "🔙 Back"
    builder.button(text=back_text, callback_data="back_main")
    
    builder.adjust(1)
    return builder.as_markup()


def get_more_options_keyboard(lang: str = 'ar') -> InlineKeyboardMarkup:
    """More options keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📞 تواصل بنا" if lang == 'ar' else "📞 Contact Us", callback_data="contact_us")
    
    back_text = "🔙 رجوع" if lang == 'ar' else "🔙 Back"
    builder.button(text=back_text, callback_data="back_to_free_orders")
    
    builder.adjust(1)
    return builder.as_markup()


# ========= طلبات الشراء (Paid Orders) =========

def get_paid_orders_keyboard(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Paid orders keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🟣 شراء كراونز" if lang == 'ar' else "🟣 Buy Crowns", callback_data="buy_crowns")
    builder.button(text="🟡 شراء كوينز" if lang == 'ar' else "🟡 Buy Coins", callback_data="buy_coins")
    builder.button(text="💳 شراء عضويات" if lang == 'ar' else "💳 Buy VIP", callback_data="buy_vip")
    builder.button(text="🤖 تعزيز الحسابات" if lang == 'ar' else "🤖 Boost Account", callback_data="boost_account")
    builder.button(text="❤️ لايكات ومشاهدات" if lang == 'ar' else "❤️ Likes & Views", callback_data="buy_likes")
    builder.button(text="🎮 ألعاب أخرى" if lang == 'ar' else "🎮 Other Games", callback_data="other_games")
    
    back_text = "🔙 رجوع" if lang == 'ar' else "🔙 Back"
    builder.button(text=back_text, callback_data="back_main")
    
    builder.adjust(2)
    return builder.as_markup()


# ========= قسم الشكاوى (Complaints) =========

def get_complaints_keyboard(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Complaints section keyboard"""
    builder = InlineKeyboardBuilder()
    
    if lang == 'ar':
        builder.button(text="📝 إنشاء تذكرة شكوى", callback_data="create_ticket")
        builder.button(text="💬 فتح شات مباشر", callback_data="live_chat")
        builder.button(text="🔙 رجوع", callback_data="back_main")
    else:
        builder.button(text="📝 Create Complaint Ticket", callback_data="create_ticket")
        builder.button(text="💬 Open Live Chat", callback_data="live_chat")
        builder.button(text="🔙 Back", callback_data="back_main")
    
    builder.adjust(1)
    return builder.as_markup()


def get_admin_reply_keyboard(user_id: int, ticket_id: int) -> InlineKeyboardMarkup:
    """Admin reply keyboard for tickets"""
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 رد", callback_data=f"admin_reply_complaint_{user_id}_{ticket_id}")
    builder.adjust(1)
    return builder.as_markup()


def get_ticket_admin_keyboard(ticket_number: str, user_id: int) -> InlineKeyboardMarkup:
    """Admin ticket control keyboard"""
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 رد على التذكرة", callback_data=f"reply_ticket_{ticket_number}")
    builder.button(text="🔓 فتح شات مباشر", callback_data=f"open_chat_{ticket_number}_{user_id}")
    builder.button(text="✅ إغلاق التذكرة", callback_data=f"close_ticket_{ticket_number}")
    builder.adjust(2)
    return builder.as_markup()


# ========= أزرار الأدمن (Admin) =========

def get_order_admin_keyboard(order_number: str, user_id: int) -> InlineKeyboardMarkup:
    """Admin order control keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="⏳ جاري التنفيذ", callback_data=f"exec_{order_number}_{user_id}")
    builder.button(text="✅ تم التنفيذ", callback_data=f"done_{order_number}_{user_id}")
    builder.button(text="❌ إلغاء", callback_data=f"cancel_{order_number}_{user_id}")
    builder.button(text="💬 تواصل", callback_data=f"chat_{order_number}_{user_id}")
    builder.button(text="🚫 حظر", callback_data=f"ban_{order_number}_{user_id}")
    
    builder.adjust(2)
    return builder.as_markup()


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Confirmation keyboard"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ تأكيد", callback_data="confirm")
    builder.button(text="❌ إلغاء", callback_data="cancel")
    builder.adjust(2)
    return builder.as_markup()


def get_broadcast_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Broadcast confirmation keyboard"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ تأكيد الإرسال", callback_data="confirm_broadcast")
    builder.button(text="❌ إلغاء", callback_data="cancel_broadcast")
    builder.adjust(2)
    return builder.as_markup()


# ========= إعدادات (Settings) =========

def get_settings_keyboard(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Settings keyboard"""
    builder = InlineKeyboardBuilder()
    
    if lang == 'ar':
        builder.button(text="🌍 تغيير اللغة", callback_data="change_lang")
        builder.button(text="🔙 رجوع", callback_data="back_main")
    else:
        builder.button(text="🌍 Change Language", callback_data="change_lang")
        builder.button(text="🔙 Back", callback_data="back_main")
    
    builder.adjust(1)
    return builder.as_markup()


# ========= قائمة رئيسية إنلاين (Inline Main Menu) =========

def get_main_keyboard_inline(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Inline main menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    if lang == 'ar':
        builder.button(text="📦 المودات", callback_data="mods")
        builder.button(text="💰 طلبات الشراء", callback_data="paid_orders")
        builder.button(text="🎁 الطلبات المجانية", callback_data="free_orders")
        builder.button(text="📝 الشكاوى", callback_data="complaints")
        builder.button(text="⭐ تقييم البوت", callback_data="rate_bot")
        builder.button(text="⚙️ الإعدادات", callback_data="settings")
    else:
        builder.button(text="📦 Mods", callback_data="mods")
        builder.button(text="💰 Purchase", callback_data="paid_orders")
        builder.button(text="🎁 Free Requests", callback_data="free_orders")
        builder.button(text="📝 Complaints", callback_data="complaints")
        builder.button(text="⭐ Rate Bot", callback_data="rate_bot")
        builder.button(text="⚙️ Settings", callback_data="settings")
    
    builder.adjust(2)
    return builder.as_markup()


# ========= رجوع (Back) =========

def get_back_keyboard(lang: str = "ar") -> InlineKeyboardMarkup:
    """Back keyboard for navigation"""
    text = "🔙 رجوع" if lang == "ar" else "🔙 Back"
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data="back")
    builder.adjust(1)
    return builder.as_markup()
