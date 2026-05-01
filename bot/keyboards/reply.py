from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.utils.translations import get_user_language, get_text, TRANSLATIONS


def get_main_keyboard(user_id: int, lang: str = None) -> ReplyKeyboardMarkup:
    """
    القائمة الرئيسية للبوت - Main menu keyboard
    Supports both dynamic user language and direct language parameter
    """
    if lang is None:
        lang = get_user_language(user_id)
    
    if lang == 'ar':
        buttons = [
            [KeyboardButton(text='🎮 المودات')],
            [KeyboardButton(text='💰 طلبات الشراء')],
            [KeyboardButton(text='🎁 الطلبات المجانية')],
            [KeyboardButton(text='📝 الشكاوى')],
            [KeyboardButton(text='🌍 تغيير اللغة')],
            [KeyboardButton(text='⭐ تقييم البوت')],
            [KeyboardButton(text='🚀 خدمة شحن كاملة')]
        ]
    else:
        buttons = [
            [KeyboardButton(text='🎮 Mods')],
            [KeyboardButton(text='💰 Purchase Requests')],
            [KeyboardButton(text='🎁 Free Requests')],
            [KeyboardButton(text='📝 Complaints')],
            [KeyboardButton(text='🌍 Change Language')],
            [KeyboardButton(text='⭐ Rate Bot')],
            [KeyboardButton(text='🚀 Full Shipping Service')]
        ]
    
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard


def get_admin_keyboard(user_id: int = None) -> ReplyKeyboardMarkup:
    """
    لوحة تحكم الأدمن (ثابتة بالعربية) - Updated version from new file
    """
    buttons = [
        [KeyboardButton(text='📊 الإحصائيات')],
        [KeyboardButton(text='📢 إذاعة')],
        [KeyboardButton(text='🚫 حظر مستخدم')],
        [KeyboardButton(text='✅ فك حظر')],
        [KeyboardButton(text='📋 الطلبات')],
        [KeyboardButton(text='📝 التذاكر')],
        [KeyboardButton(text='📜 السجلات')],
        [KeyboardButton(text='👥 المستخدمين')],
        [KeyboardButton(text='🎮 تحكم في البوت')],
        [KeyboardButton(text='📊 التقييمات')]
    ]
    markup = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return markup


def get_back_keyboard(user_id: int, lang: str = None) -> ReplyKeyboardMarkup:
    """
    زر رجوع فقط - Back button only
    """
    if lang is None:
        lang = get_user_language(user_id)
    
    back_text = "🔙 رجوع" if lang == 'ar' else "🔙 Back"
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=back_text)]], resize_keyboard=True)
    return keyboard


def get_language_keyboard() -> ReplyKeyboardMarkup:
    """
    أزرار اختيار اللغة - Language selection buttons (static)
    """
    buttons = [
        [KeyboardButton(text="🇸🇦 العربية")],
        [KeyboardButton(text="🇺🇸 English")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard


def get_cancel_keyboard(user_id: int, lang: str = None) -> ReplyKeyboardMarkup:
    """
    زر إلغاء - Cancel button
    """
    if lang is None:
        lang = get_user_language(user_id)
    
    cancel_text = "❌ إلغاء" if lang == 'ar' else "❌ Cancel"
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=cancel_text)]], resize_keyboard=True)
    return keyboard


def get_yes_no_keyboard(user_id: int, lang: str = None) -> ReplyKeyboardMarkup:
    """
    أزرار نعم/لا - Yes/No buttons
    """
    if lang is None:
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
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard


def get_rating_keyboard(lang: str = 'ar') -> ReplyKeyboardMarkup:
    """
    أزرار التقييم - Rating buttons (1-5 stars)
    """
    if lang == 'ar':
        buttons = [
            [KeyboardButton(text="⭐ 1")],
            [KeyboardButton(text="⭐⭐ 2")],
            [KeyboardButton(text="⭐⭐⭐ 3")],
            [KeyboardButton(text="⭐⭐⭐⭐ 4")],
            [KeyboardButton(text="⭐⭐⭐⭐⭐ 5")]
        ]
    else:
        buttons = [
            [KeyboardButton(text="⭐ 1")],
            [KeyboardButton(text="⭐⭐ 2")],
            [KeyboardButton(text="⭐⭐⭐ 3")],
            [KeyboardButton(text="⭐⭐⭐⭐ 4")],
            [KeyboardButton(text="⭐⭐⭐⭐⭐ 5")]
        ]
    
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard


def get_mods_keyboard(user_id: int, lang: str = None) -> ReplyKeyboardMarkup:
    """
    أزرار المودات - Mods buttons
    """
    if lang is None:
        lang = get_user_language(user_id)
    
    if lang == 'ar':
        buttons = [
            [KeyboardButton(text='☁️ مود سكاي')],
            [KeyboardButton(text='🐂 مود الثور')],
            [KeyboardButton(text='👑 مود جولد')],
            [KeyboardButton(text='🔙 رجوع')]
        ]
    else:
        buttons = [
            [KeyboardButton(text='☁️ Sky Mod')],
            [KeyboardButton(text='🐂 Bull Mod')],
            [KeyboardButton(text='👑 Gold Mod')],
            [KeyboardButton(text='🔙 Back')]
        ]
    
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard


def get_complaints_keyboard(user_id: int, lang: str = None) -> ReplyKeyboardMarkup:
    """
    أزرار قسم الشكاوى - Complaints section buttons
    """
    if lang is None:
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
    
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard


def get_paid_orders_keyboard(user_id: int, lang: str = None) -> ReplyKeyboardMarkup:
    """
    أزرار طلبات الشراء - Paid orders buttons
    """
    if lang is None:
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
    
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard


def get_free_orders_keyboard(user_id: int, lang: str = None) -> ReplyKeyboardMarkup:
    """
    أزرار الطلبات المجانية - Free orders buttons
    """
    if lang is None:
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
    
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard


def get_simple_keyboard(buttons: list, row_width: int = 2) -> ReplyKeyboardMarkup:
    """
    لوحة مفاتيح بسيطة مع أزرار مخصصة - Simple keyboard with custom buttons
    """
    keyboard_buttons = []
    row = []
    for i, btn in enumerate(buttons):
        row.append(KeyboardButton(text=btn))
        if (i + 1) % row_width == 0 or i == len(buttons) - 1:
            keyboard_buttons.append(row)
            row = []
    
    keyboard = ReplyKeyboardMarkup(keyboard=keyboard_buttons, resize_keyboard=True)
    return keyboard
