from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.utils.translations import get_user_language, get_text, TRANSLATIONS


def get_main_keyboard(user_id: int, lang: str = None) -> ReplyKeyboardMarkup:
    """
    القائمة الرئيسية للبوت - Main menu keyboard
    Supports both dynamic user language and direct language parameter
    """
    if lang is None:
        lang = get_user_language(user_id)
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    if lang == 'ar':
        buttons = [
            KeyboardButton('🎮 المودات'),
            KeyboardButton('💰 طلبات الشراء'),
            KeyboardButton('🎁 الطلبات المجانية'),
            KeyboardButton('📝 الشكاوى'),
            KeyboardButton('🌍 تغيير اللغة'),
            KeyboardButton('⭐ تقييم البوت'),
            KeyboardButton('🚀 خدمة شحن كاملة')
        ]
    else:
        buttons = [
            KeyboardButton('🎮 Mods'),
            KeyboardButton('💰 Purchase Requests'),
            KeyboardButton('🎁 Free Requests'),
            KeyboardButton('📝 Complaints'),
            KeyboardButton('🌍 Change Language'),
            KeyboardButton('⭐ Rate Bot'),
            KeyboardButton('🚀 Full Shipping Service')
        ]
    
    keyboard.add(*buttons)
    return keyboard


def get_admin_keyboard() -> ReplyKeyboardMarkup:
    """
    لوحة تحكم الأدمن (ثابتة بالعربية) - Updated version from new file
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        KeyboardButton('📊 الإحصائيات'),
        KeyboardButton('📢 إذاعة'),
        KeyboardButton('🚫 حظر مستخدم'),
        KeyboardButton('✅ فك حظر'),
        KeyboardButton('📋 الطلبات'),
        KeyboardButton('📝 التذاكر'),
        KeyboardButton('📜 السجلات'),
        KeyboardButton('👥 المستخدمين'),
        KeyboardButton('🎮 تحكم في البوت'),
        KeyboardButton('📊 التقييمات')
    ]
    markup.add(*buttons)
    return markup


def get_back_keyboard(user_id: int, lang: str = None) -> ReplyKeyboardMarkup:
    """
    زر رجوع فقط - Back button only
    """
    if lang is None:
        lang = get_user_language(user_id)
    
    back_text = "🔙 رجوع" if lang == 'ar' else "🔙 Back"
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text=back_text))
    return keyboard


def get_language_keyboard() -> ReplyKeyboardMarkup:
    """
    أزرار اختيار اللغة - Language selection buttons (static)
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton(text="🇸🇦 العربية"),
        KeyboardButton(text="🇺🇸 English")
    )
    return keyboard


def get_cancel_keyboard(user_id: int, lang: str = None) -> ReplyKeyboardMarkup:
    """
    زر إلغاء - Cancel button
    """
    if lang is None:
        lang = get_user_language(user_id)
    
    cancel_text = "❌ إلغاء" if lang == 'ar' else "❌ Cancel"
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text=cancel_text))
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
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(KeyboardButton(text=yes_text), KeyboardButton(text=no_text))
    return keyboard


def get_rating_keyboard(lang: str = 'ar') -> ReplyKeyboardMarkup:
    """
    أزرار التقييم - Rating buttons (1-5 stars)
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=5)
    
    if lang == 'ar':
        buttons = [
            KeyboardButton("⭐ 1"),
            KeyboardButton("⭐⭐ 2"),
            KeyboardButton("⭐⭐⭐ 3"),
            KeyboardButton("⭐⭐⭐⭐ 4"),
            KeyboardButton("⭐⭐⭐⭐⭐ 5"),
        ]
    else:
        buttons = [
            KeyboardButton("⭐ 1"),
            KeyboardButton("⭐⭐ 2"),
            KeyboardButton("⭐⭐⭐ 3"),
            KeyboardButton("⭐⭐⭐⭐ 4"),
            KeyboardButton("⭐⭐⭐⭐⭐ 5")
        ]
    
    keyboard.add(*buttons)
    return keyboard


def get_mods_keyboard(user_id: int, lang: str = None) -> ReplyKeyboardMarkup:
    """
    أزرار المودات - Mods buttons
    """
    if lang is None:
        lang = get_user_language(user_id)
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    if lang == 'ar':
        buttons = [
            KeyboardButton('☁️ مود سكاي'),
            KeyboardButton('🐂 مود الثور'),
            KeyboardButton('👑 مود جولد'),
            KeyboardButton('🔙 رجوع')
        ]
    else:
        buttons = [
            KeyboardButton('☁️ Sky Mod'),
            KeyboardButton('🐂 Bull Mod'),
            KeyboardButton('👑 Gold Mod'),
            KeyboardButton('🔙 Back')
        ]
    
    keyboard.add(*buttons)
    return keyboard


def get_complaints_keyboard(user_id: int, lang: str = None) -> ReplyKeyboardMarkup:
    """
    أزرار قسم الشكاوى - Complaints section buttons
    """
    if lang is None:
        lang = get_user_language(user_id)
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    if lang == 'ar':
        buttons = [
            KeyboardButton('📝 إنشاء تذكرة شكوى'),
            KeyboardButton('💬 فتح شات مباشر'),
            KeyboardButton('🔙 رجوع')
        ]
    else:
        buttons = [
            KeyboardButton('📝 Create Complaint Ticket'),
            KeyboardButton('💬 Open Live Chat'),
            KeyboardButton('🔙 Back')
        ]
    
    keyboard.add(*buttons)
    return keyboard


def get_paid_orders_keyboard(user_id: int, lang: str = None) -> ReplyKeyboardMarkup:
    """
    أزرار طلبات الشراء - Paid orders buttons
    """
    if lang is None:
        lang = get_user_language(user_id)
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    if lang == 'ar':
        buttons = [
            KeyboardButton('🟣 شراء كراونز'),
            KeyboardButton('🟡 شراء كوينز'),
            KeyboardButton('💳 شراء عضويات'),
            KeyboardButton('🤖 تعزيز الحسابات'),
            KeyboardButton('❤️ لايكات ومشاهدات'),
            KeyboardButton('🎮 ألعاب أخرى'),
            KeyboardButton('🔙 رجوع')
        ]
    else:
        buttons = [
            KeyboardButton('🟣 Buy Crowns'),
            KeyboardButton('🟡 Buy Coins'),
            KeyboardButton('💳 Buy VIP'),
            KeyboardButton('🤖 Boost Account'),
            KeyboardButton('❤️ Likes & Views'),
            KeyboardButton('🎮 Other Games'),
            KeyboardButton('🔙 Back')
        ]
    
    for i in range(0, len(buttons) - 1, 2):
        keyboard.row(buttons[i], buttons[i + 1])
    if len(buttons) % 2 == 1:
        keyboard.row(buttons[-1])
    
    return keyboard


def get_free_orders_keyboard(user_id: int, lang: str = None) -> ReplyKeyboardMarkup:
    """
    أزرار الطلبات المجانية - Free orders buttons
    """
    if lang is None:
        lang = get_user_language(user_id)
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    if lang == 'ar':
        buttons = [
            KeyboardButton('✏️ تغيير الاسم'),
            KeyboardButton('🖼 تغيير الصورة'),
            KeyboardButton('📌 المزيد'),
            KeyboardButton('🔙 رجوع')
        ]
    else:
        buttons = [
            KeyboardButton('✏️ Change Name'),
            KeyboardButton('🖼 Change Photo'),
            KeyboardButton('📌 More'),
            KeyboardButton('🔙 Back')
        ]
    
    keyboard.add(*buttons)
    return keyboard


def get_simple_keyboard(buttons: list, row_width: int = 2) -> ReplyKeyboardMarkup:
    """
    لوحة مفاتيح بسيطة مع أزرار مخصصة - Simple keyboard with custom buttons
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=row_width)
    keyboard.add(*buttons)
    return keyboard
