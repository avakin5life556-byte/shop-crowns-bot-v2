from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.utils.translations import get_user_language


def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    """
    القائمة الرئيسية للبوت - Main menu keyboard
    """
    lang = get_user_language(user_id)
    
    if lang == 'ar':
        buttons = [
            [KeyboardButton(text='🎮 المودات')],
            [KeyboardButton(text='💰 طلبات الشراء')],
            [KeyboardButton(text='🎁 الطلبات المجانية')],
            [KeyboardButton(text='📝 الشكاوى')],
            [KeyboardButton(text='🌍 تغيير اللغة')],
            [KeyboardButton(text='⭐ تقييم البوت')],
            [KeyboardButton(text='🚀 خدمة شحن كاملة')],
            [KeyboardButton(text='👑 لوحة التحكم')]
        ]
    else:
        buttons = [
            [KeyboardButton(text='🎮 Mods')],
            [KeyboardButton(text='💰 Purchase Requests')],
            [KeyboardButton(text='🎁 Free Requests')],
            [KeyboardButton(text='📝 Complaints')],
            [KeyboardButton(text='🌍 Change Language')],
            [KeyboardButton(text='⭐ Rate Bot')],
            [KeyboardButton(text='🚀 Full Shipping Service')],
            [KeyboardButton(text='👑 Control Panel')]
        ]
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons, 
        resize_keyboard=True,
        input_field_placeholder="اختر من القائمة" if lang == 'ar' else "Choose from the menu"
    )
    return keyboard


def get_admin_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    """
    لوحة تحكم الأدمن - Admin control panel
    """
    lang = get_user_language(user_id)
    
    if lang == 'ar':
        buttons = [
            [KeyboardButton(text='📊 الإحصائيات')],
            [KeyboardButton(text='📢 إذاعة')],
            [KeyboardButton(text='🚫 حظر مستخدم')],
            [KeyboardButton(text='✅ فك حظر')],
            [KeyboardButton(text='📋 الطلبات')],
            [KeyboardButton(text='📝 التذاكر')],
            [KeyboardButton(text='🛒 طلبات الشراء')],
            [KeyboardButton(text='📜 السجلات')],
            [KeyboardButton(text='👥 المستخدمين')],
            [KeyboardButton(text='🎮 تحكم في البوت')],
            [KeyboardButton(text='📊 التقييمات')],
            [KeyboardButton(text='🔙 رجوع')]
        ]
    else:
        buttons = [
            [KeyboardButton(text='📊 Statistics')],
            [KeyboardButton(text='📢 Broadcast')],
            [KeyboardButton(text='🚫 Ban User')],
            [KeyboardButton(text='✅ Unban')],
            [KeyboardButton(text='📋 Orders')],
            [KeyboardButton(text='📝 Tickets')],
            [KeyboardButton(text='🛒 Paid Orders')],
            [KeyboardButton(text='📜 Logs')],
            [KeyboardButton(text='👥 Users')],
            [KeyboardButton(text='🎮 Control Bot')],
            [KeyboardButton(text='📊 Ratings')],
            [KeyboardButton(text='🔙 Back')]
        ]
    
    markup = ReplyKeyboardMarkup(
        keyboard=buttons, 
        resize_keyboard=True,
        input_field_placeholder="اختر إجراء" if lang == 'ar' else "Choose an action"
    )
    return markup


def get_back_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    """
    زر رجوع فقط - Back button only
    """
    lang = get_user_language(user_id)
    
    back_text = "🔙 رجوع" if lang == 'ar' else "🔙 Back"
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=back_text)]], 
        resize_keyboard=True
    )
    return keyboard


def get_language_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    """
    أزرار اختيار اللغة - Language selection buttons
    """
    # Only static buttons, language-independent
    buttons = [
        [KeyboardButton(text="🇸🇦 العربية")],
        [KeyboardButton(text="🇺🇸 English")],
        [KeyboardButton(text="🔙 رجوع" if get_user_language(user_id) == 'ar' else "🔙 Back")]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons, 
        resize_keyboard=True,
        input_field_placeholder="اختر لغتك" if get_user_language(user_id) == 'ar' else "Choose your language"
    )
    return keyboard


def get_cancel_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    """
    زر إلغاء - Cancel button
    """
    lang = get_user_language(user_id)
    
    cancel_text = "❌ إلغاء" if lang == 'ar' else "❌ Cancel"
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=cancel_text)]], 
        resize_keyboard=True
    )
    return keyboard


def get_yes_no_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    """
    أزرار نعم/لا - Yes/No buttons
    """
    lang = get_user_language(user_id)
    
    if lang == 'ar':
        yes_text = "✅ نعم"
        no_text = "❌ لا"
    else:
        yes_text = "✅ Yes"
        no_text = "❌ No"
    
    buttons = [
        [KeyboardButton(text=yes_text), KeyboardButton(text=no_text)]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons, 
        resize_keyboard=True,
        input_field_placeholder="اختر أحد الخيارين" if lang == 'ar' else "Choose one of the options"
    )
    return keyboard


def get_rating_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    """
    أزرار التقييم - Rating buttons (1-5 stars)
    """
    lang = get_user_language(user_id)
    
    if lang == 'ar':
        buttons = [
            [KeyboardButton(text="⭐ 1")],
            [KeyboardButton(text="⭐⭐ 2")],
            [KeyboardButton(text="⭐⭐⭐ 3")],
            [KeyboardButton(text="⭐⭐⭐⭐ 4")],
            [KeyboardButton(text="⭐⭐⭐⭐⭐ 5")],
            [KeyboardButton(text="🔙 رجوع")]
        ]
    else:
        buttons = [
            [KeyboardButton(text="⭐ 1")],
            [KeyboardButton(text="⭐⭐ 2")],
            [KeyboardButton(text="⭐⭐⭐ 3")],
            [KeyboardButton(text="⭐⭐⭐⭐ 4")],
            [KeyboardButton(text="⭐⭐⭐⭐⭐ 5")],
            [KeyboardButton(text="🔙 Back")]
        ]
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons, 
        resize_keyboard=True,
        input_field_placeholder="اختر عدد النجوم" if lang == 'ar' else "Choose number of stars"
    )
    return keyboard


def get_mods_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    """
    أزرار المودات - Mods buttons
    """
    lang = get_user_language(user_id)
    
    if lang == 'ar':
        buttons = [
            [KeyboardButton(text='☁️ سكاي مود')],
            [KeyboardButton(text='🐂 بول مود')],
            [KeyboardButton(text='⭐ جولد مود')],
            [KeyboardButton(text='🔙 رجوع')]
        ]
    else:
        buttons = [
            [KeyboardButton(text='☁️ Sky Mod')],
            [KeyboardButton(text='🐂 Bull Mod')],
            [KeyboardButton(text='⭐ Gold Mod')],
            [KeyboardButton(text='🔙 Back')]
        ]
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons, 
        resize_keyboard=True,
        input_field_placeholder="اختر المود الذي تريد" if lang == 'ar' else "Choose the mod you want"
    )
    return keyboard


def get_complaints_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    """
    أزرار قسم الشكاوى - Complaints section buttons
    """
    lang = get_user_language(user_id)
    
    if lang == 'ar':
        buttons = [
            [KeyboardButton(text='📝 إنشاء تذكرة شكوى')],
            [KeyboardButton(text='💬 فتح شات مباشر')],
            [KeyboardButton(text='🔙 رجوع')]
        ]
    else:
        buttons = [
            [KeyboardButton(text='📝 Create Complaint Ticket')],
            [KeyboardButton(text='💬 Open Live Chat')],
            [KeyboardButton(text='🔙 Back')]
        ]
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons, 
        resize_keyboard=True,
        input_field_placeholder="اختر نوع التواصل" if lang == 'ar' else "Choose communication type"
    )
    return keyboard


def get_paid_orders_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    """
    أزرار طلبات الشراء - Paid orders buttons
    """
    lang = get_user_language(user_id)
    
    if lang == 'ar':
        buttons = [
            [KeyboardButton(text='🟣 شراء كراونز')],
            [KeyboardButton(text='🟡 شراء كوينز')],
            [KeyboardButton(text='💳 شراء عضويات')],
            [KeyboardButton(text='🤖 تعزيز الحسابات')],
            [KeyboardButton(text='❤️ لايكات ومشاهدات')],
            [KeyboardButton(text='🎮 ألعاب أخرى')],
            [KeyboardButton(text='🔙 رجوع')]
        ]
    else:
        buttons = [
            [KeyboardButton(text='🟣 Buy Crowns')],
            [KeyboardButton(text='🟡 Buy Coins')],
            [KeyboardButton(text='💳 Buy VIP')],
            [KeyboardButton(text='🤖 Boost Account')],
            [KeyboardButton(text='❤️ Likes & Views')],
            [KeyboardButton(text='🎮 Other Games')],
            [KeyboardButton(text='🔙 Back')]
        ]
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons, 
        resize_keyboard=True,
        input_field_placeholder="اختر الخدمة التي تريد" if lang == 'ar' else "Choose the service you want"
    )
    return keyboard


def get_free_orders_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    """
    أزرار الطلبات المجانية - Free orders buttons
    """
    lang = get_user_language(user_id)
    
    if lang == 'ar':
        buttons = [
            [KeyboardButton(text='✏️ تغيير الاسم')],
            [KeyboardButton(text='🖼 تغيير الصورة')],
            [KeyboardButton(text='📌 المزيد')],
            [KeyboardButton(text='🔙 رجوع')]
        ]
    else:
        buttons = [
            [KeyboardButton(text='✏️ Change Name')],
            [KeyboardButton(text='🖼 Change Photo')],
            [KeyboardButton(text='📌 More')],
            [KeyboardButton(text='🔙 Back')]
        ]
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons, 
        resize_keyboard=True,
        input_field_placeholder="اختر الخدمة المجانية" if lang == 'ar' else "Choose free service"
    )
    return keyboard


def get_simple_keyboard(user_id: int, buttons: list, row_width: int = 2) -> ReplyKeyboardMarkup:
    """
    لوحة مفاتيح بسيطة مع أزرار مخصصة - Simple keyboard with custom buttons
    """
    lang = get_user_language(user_id)
    
    keyboard_buttons = []
    row = []
    for i, btn in enumerate(buttons):
        row.append(KeyboardButton(text=btn))
        if (i + 1) % row_width == 0 or i == len(buttons) - 1:
            keyboard_buttons.append(row)
            row = []
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_buttons, 
        resize_keyboard=True,
        input_field_placeholder="اختر من القائمة" if lang == 'ar' else "Choose from the menu"
    )
    return keyboard
