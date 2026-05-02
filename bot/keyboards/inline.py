from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# ========= Yes / No =========

def get_yes_no_keyboard() -> InlineKeyboardMarkup:
    """Yes/No inline keyboard"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(text="✅ نعم", callback_data="yes"),
        InlineKeyboardButton(text="❌ لا", callback_data="no")
    )
    return markup


def get_continue_keyboard() -> InlineKeyboardMarkup:
    """Confirmation continue keyboard"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(text="✅ نعم", callback_data="continue_yes"),
        InlineKeyboardButton(text="❌ لا", callback_data="continue_no")
    )
    return markup


# ========= Rating =========

def get_rating_keyboard() -> InlineKeyboardMarkup:
    """Rating keyboard (1-5 stars) - Updated version"""
    markup = InlineKeyboardMarkup(row_width=5)
    for i in range(1, 6):
        markup.insert(InlineKeyboardButton(text="⭐" * i, callback_data=f"rate_{i}"))
    return markup


def get_support_rating_keyboard() -> InlineKeyboardMarkup:
    """Support rating keyboard (1-5 stars)"""
    markup = InlineKeyboardMarkup(row_width=5)
    for i in range(1, 6):
        markup.insert(InlineKeyboardButton(text="⭐" * i, callback_data=f"support_rate_{i}"))
    return markup


# ========= الدردشة (Chat) =========

def get_live_chat_keyboard(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Live chat keyboard for users"""
    text = "🔚 إنهاء المحادثة" if lang == 'ar' else "🔚 End Chat"
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text=text, callback_data="end_chat"))
    return markup


def get_end_chat_keyboard() -> InlineKeyboardMarkup:
    """End chat keyboard"""
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text="🔚 إنهاء المحادثة", callback_data="end_chat"))
    return markup


def get_admin_chat_keyboard(user_id: int, chat_session_id: int) -> InlineKeyboardMarkup:
    """Admin chat control keyboard (updated version with complaint handlers)"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(text="💬 رد", callback_data=f"admin_reply_complaint_{user_id}_{chat_session_id}"),
        InlineKeyboardButton(text="🔚 إنهاء", callback_data=f"admin_end_chat_complaint_{user_id}_{chat_session_id}")
    )
    return markup


# ========= أزرار عامة (General) =========

def get_contact_button(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Contact us button"""
    text = "💬 تواصل بنا" if lang == 'ar' else "💬 Contact Us"
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text=text, callback_data="contact_us"))
    return markup


def get_back_button(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Back button - Clean version from new file"""
    text = "🔙 رجوع" if lang == 'ar' else "🔙 Back"
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text=text, callback_data="back_main"))
    return markup


def get_back_to_menu_keyboard(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Back to main menu keyboard"""
    text = "🏠 القائمة الرئيسية" if lang == 'ar' else "🏠 Main Menu"
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text=text, callback_data="back_main"))
    return markup


def get_cancel_keyboard(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Cancel operation keyboard"""
    text = "❌ إلغاء" if lang == 'ar' else "❌ Cancel"
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text=text, callback_data="cancel"))
    return markup


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Language selection keyboard"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(text="🇸🇦 العربية", callback_data="lang_ar"),
        InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en")
    )
    return markup


# ========= المودات (Mods) =========

def get_mods_keyboard(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Mods selection keyboard"""
    markup = InlineKeyboardMarkup(row_width=1)
    
    if lang == 'ar':
        buttons = [
            InlineKeyboardButton(text="☁️ Sky Mod", callback_data="mod_sky"),
            InlineKeyboardButton(text="🐂 Bull Mod", callback_data="mod_bull"),
            InlineKeyboardButton(text="⭐ Gold Mod", callback_data="mod_gold"),
            InlineKeyboardButton(text="🔙 رجوع", callback_data="back_main")
        ]
    else:
        buttons = [
            InlineKeyboardButton(text="☁️ Sky Mod", callback_data="mod_sky"),
            InlineKeyboardButton(text="🐂 Bull Mod", callback_data="mod_bull"),
            InlineKeyboardButton(text="⭐ Gold Mod", callback_data="mod_gold"),
            InlineKeyboardButton(text="🔙 Back", callback_data="back_main")
        ]
    
    for btn in buttons:
        markup.add(btn)
    
    return markup


# ========= الطلبات المجانية (Free Orders) =========

def get_free_orders_keyboard(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Free orders keyboard"""
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(text="✏️ تغيير الاسم" if lang == 'ar' else "✏️ Change Name", callback_data="change_name"),
        InlineKeyboardButton(text="🖼 تغيير الصورة" if lang == 'ar' else "🖼 Change Photo", callback_data="change_photo"),
        InlineKeyboardButton(text="📌 المزيد" if lang == 'ar' else "📌 More", callback_data="more_options"),
        InlineKeyboardButton(text="🔙 رجوع" if lang == 'ar' else "🔙 Back", callback_data="back_main")
    )
    return markup


def get_more_options_keyboard(lang: str = 'ar') -> InlineKeyboardMarkup:
    """More options keyboard"""
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(text="📞 تواصل بنا" if lang == 'ar' else "📞 Contact Us", callback_data="contact_us"),
        InlineKeyboardButton(text="🔙 رجوع" if lang == 'ar' else "🔙 Back", callback_data="back_to_free_orders")
    )
    return markup


# ========= طلبات الشراء (Paid Orders) =========

def get_paid_orders_keyboard(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Paid orders keyboard"""
    markup = InlineKeyboardMarkup(row_width=2)

    buttons = [
        InlineKeyboardButton(text="🟣 شراء كراونز" if lang == 'ar' else "🟣 Buy Crowns", callback_data="buy_crowns"),
        InlineKeyboardButton(text="🟡 شراء كوينز" if lang == 'ar' else "🟡 Buy Coins", callback_data="buy_coins"),
        InlineKeyboardButton(text="💳 شراء عضويات" if lang == 'ar' else "💳 Buy VIP", callback_data="buy_vip"),
        InlineKeyboardButton(text="🤖 تعزيز الحسابات" if lang == 'ar' else "🤖 Boost Account", callback_data="boost_account"),
        InlineKeyboardButton(text="❤️ لايكات ومشاهدات" if lang == 'ar' else "❤️ Likes & Views", callback_data="buy_likes"),
        InlineKeyboardButton(text="🎮 ألعاب أخرى" if lang == 'ar' else "🎮 Other Games", callback_data="other_games"),
        InlineKeyboardButton(text="🔙 رجوع" if lang == 'ar' else "🔙 Back", callback_data="back_main")
    ]

    # إضافة الأزرار في صفوف
    for i in range(0, len(buttons) - 1, 2):
        markup.row(buttons[i], buttons[i + 1])
    if len(buttons) % 2 == 1:
        markup.row(buttons[-1])

    return markup


# ========= قسم الشكاوى (Complaints) =========

def get_complaints_keyboard(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Complaints section keyboard"""
    markup = InlineKeyboardMarkup(row_width=1)
    
    if lang == 'ar':
        buttons = [
            InlineKeyboardButton(text="📝 إنشاء تذكرة شكوى", callback_data="create_ticket"),
            InlineKeyboardButton(text="💬 فتح شات مباشر", callback_data="live_chat"),
            InlineKeyboardButton(text="🔙 رجوع", callback_data="back_main")
        ]
    else:
        buttons = [
            InlineKeyboardButton(text="📝 Create Complaint Ticket", callback_data="create_ticket"),
            InlineKeyboardButton(text="💬 Open Live Chat", callback_data="live_chat"),
            InlineKeyboardButton(text="🔙 Back", callback_data="back_main")
        ]
    
    for btn in buttons:
        markup.add(btn)
    
    return markup


def get_admin_reply_keyboard(user_id: int, ticket_id: int) -> InlineKeyboardMarkup:
    """Admin reply keyboard for tickets"""
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(text="💬 رد", callback_data=f"admin_reply_complaint_{user_id}_{ticket_id}")
    )
    return markup


def get_ticket_admin_keyboard(ticket_number: str, user_id: int) -> InlineKeyboardMarkup:
    """Admin ticket control keyboard (merged version)"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(text="💬 رد على التذكرة", callback_data=f"reply_ticket_{ticket_number}"),
        InlineKeyboardButton(text="🔓 فتح شات مباشر", callback_data=f"open_chat_{ticket_number}_{user_id}"),
        InlineKeyboardButton(text="✅ إغلاق التذكرة", callback_data=f"close_ticket_{ticket_number}")
    )
    return markup


# ========= أزرار الأدمن (Admin) =========

def get_order_admin_keyboard(order_number: str, user_id: int) -> InlineKeyboardMarkup:
    """Admin order control keyboard"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(text="⏳ جاري التنفيذ", callback_data=f"exec_{order_number}_{user_id}"),
        InlineKeyboardButton(text="✅ تم التنفيذ", callback_data=f"done_{order_number}_{user_id}")
    )
    markup.add(
        InlineKeyboardButton(text="❌ إلغاء", callback_data=f"cancel_{order_number}_{user_id}"),
        InlineKeyboardButton(text="💬 تواصل", callback_data=f"chat_{order_number}_{user_id}")
    )
    markup.add(
        InlineKeyboardButton(text="🚫 حظر", callback_data=f"ban_{order_number}_{user_id}")
    )
    return markup


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Confirmation keyboard"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(text="✅ تأكيد", callback_data="confirm"),
        InlineKeyboardButton(text="❌ إلغاء", callback_data="cancel")
    )
    return markup


def get_broadcast_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Broadcast confirmation keyboard"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(text="✅ تأكيد الإرسال", callback_data="confirm_broadcast"),
        InlineKeyboardButton(text="❌ إلغاء", callback_data="cancel_broadcast")
    )
    return markup


# ========= إعدادات (Settings) =========

def get_settings_keyboard(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Settings keyboard"""
    markup = InlineKeyboardMarkup(row_width=1)
    
    if lang == 'ar':
        markup.add(
            InlineKeyboardButton(text="🌍 تغيير اللغة", callback_data="change_lang"),
            InlineKeyboardButton(text="🔙 رجوع", callback_data="back_main")
        )
    else:
        markup.add(
            InlineKeyboardButton(text="🌍 Change Language", callback_data="change_lang"),
            InlineKeyboardButton(text="🔙 Back", callback_data="back_main")
        )
    
    return markup


# ========= قائمة رئيسية إنلاين (Inline Main Menu) =========

def get_main_keyboard_inline(lang: str = 'ar') -> InlineKeyboardMarkup:
    """Inline main menu keyboard"""
    markup = InlineKeyboardMarkup(row_width=2)
    
    if lang == 'ar':
        markup.add(
            InlineKeyboardButton(text="📦 المودات", callback_data="mods"),
            InlineKeyboardButton(text="💰 طلبات الشراء", callback_data="paid_orders"),
            InlineKeyboardButton(text="🎁 الطلبات المجانية", callback_data="free_orders"),
            InlineKeyboardButton(text="📝 الشكاوى", callback_data="complaints"),
            InlineKeyboardButton(text="⭐ تقييم البوت", callback_data="rate_bot"),
            InlineKeyboardButton(text="⚙️ الإعدادات", callback_data="settings")
        )
    else:
        markup.add(
            InlineKeyboardButton(text="📦 Mods", callback_data="mods"),
            InlineKeyboardButton(text="💰 Purchase", callback_data="paid_orders"),
            InlineKeyboardButton(text="🎁 Free Requests", callback_data="free_orders"),
            InlineKeyboardButton(text="📝 Complaints", callback_data="complaints"),
            InlineKeyboardButton(text="⭐ Rate Bot", callback_data="rate_bot"),
            InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")
        )
    
    return markup


# ========= رجوع (Back) =========

def get_back_keyboard(lang: str = "ar") -> InlineKeyboardMarkup:
    """Back keyboard for navigation"""
    text = "🔙 رجوع" if lang == "ar" else "🔙 Back"
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text=text, callback_data="back"))
    return keyboard
