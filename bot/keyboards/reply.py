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
            [KeyboardButton('🎮 المودات')],
            [KeyboardButton('💰 طلبات الشراء')],
            [KeyboardButton('🎁 الطلبات المجانية')],
            [KeyboardButton('📝 الشكاوى')],
            [KeyboardButton('🌍 تغيير اللغة')],
            [KeyboardButton('⭐ تقييم البوت')],
            [KeyboardButton('🚀 خدمة شحن كاملة')]
        ]
    else:
        buttons = [
            [KeyboardButton('🎮 Mods')],
            [KeyboardButton('💰 Purchase Requests')],
            [KeyboardButton('🎁 Free Requests')],
            [KeyboardButton('📝 Complaints')],
            [KeyboardButton('🌍 Change Language')],
            [KeyboardButton('⭐ Rate Bot')],
            [KeyboardButton('🚀 Full Shipping Service')]
        ]
    
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return keyboard


def get_admin_keyboard() -> ReplyKeyboardMarkup:
    """
    لوحة تحكم الأدمن (ثابتة بالعربية) - Updated version from new file
    """
    buttons = [
        [KeyboardButton('📊 الإحصائيات')],
        [KeyboardButton('📢 إذاعة')],
        [KeyboardButton('🚫 حظر مستخدم')],
        [KeyboardButton('✅ فك حظر')],
        [KeyboardButton('📋 الطلبات')],
        [KeyboardButton('📝 التذاكر')],
        [KeyboardButton('📜 السجلات')],
        [KeyboardButton('👥 المستخدمين')],
        [KeyboardButton('🎮 تحكم في البوت')],
        [KeyboardButton('📊 التقييمات')]
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
            [KeyboardButton("⭐ 1")],
            [KeyboardButton("⭐⭐ 2")],
            [KeyboardButton("⭐⭐⭐ 3")],
            [KeyboardButton("⭐⭐⭐⭐ 4")],
            [KeyboardButton("⭐⭐⭐⭐⭐ 5")]
        ]
    else:
        buttons = [
            [KeyboardButton("⭐ 1")],
            [KeyboardButton("⭐⭐ 2")],
            [KeyboardButton("⭐⭐⭐ 3")],
            [KeyboardButton("⭐⭐⭐⭐ 4")],
            [KeyboardButton("⭐⭐⭐⭐⭐ 5")]
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
            [KeyboardButton('☁️ مود سكاي')],
            [KeyboardButton('🐂 مود الثور')],
            [KeyboardButton('👑 مود جولد')],
            [KeyboardButton('🔙 رجوع')]
        ]
    else:
        buttons = [
            [KeyboardButton('☁️ Sky Mod')],
            [KeyboardButton('🐂 Bull Mod')],
            [KeyboardButton('👑 Gold Mod')],
            [KeyboardButton('🔙 Back')]
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
            [KeyboardButton('📝 إنشاء تذكرة شكوى')],
            [KeyboardButton('💬 فتح شات مباشر')],
            [KeyboardButton('🔙 رجوع')]
        ]
    else:
        buttons = [
            [KeyboardButton('📝 Create Complaint Ticket')],
            [KeyboardButton('💬 Open Live Chat')],
            [KeyboardButton('🔙 Back')]
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
            [KeyboardButton('🟣 شراء كراونز')],
            [KeyboardButton('🟡 شراء كوينز')],
            [KeyboardButton('💳 شراء عضويات')],
            [KeyboardButton('🤖 تعزيز الحسابات')],
            [KeyboardButton('❤️ لايكات ومشاهدات')],
            [KeyboardButton('🎮 ألعاب أخرى')],
            [KeyboardButton('🔙 رجوع')]
        ]
    else:
        buttons = [
            [KeyboardButton('🟣 Buy Crowns')],
            [KeyboardButton('🟡 Buy Coins')],
            [KeyboardButton('💳 Buy VIP')],
            [KeyboardButton('🤖 Boost Account')],
            [KeyboardButton('❤️ Likes & Views')],
            [KeyboardButton('🎮 Other Games')],
            [KeyboardButton('🔙 Back')]
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
            [KeyboardButton('✏️ تغيير الاسم')],
            [KeyboardButton('🖼 تغيير الصورة')],
            [KeyboardButton('📌 المزيد')],
            [KeyboardButton('🔙 رجوع')]
        ]
    else:
        buttons = [
            [KeyboardButton('✏️ Change Name')],
            [KeyboardButton('🖼 Change Photo')],
            [KeyboardButton('📌 More')],
            [KeyboardButton('🔙 Back')]
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
