from typing import Dict, List, Union, Optional
from bot.database.db import db

# ========== النظام القديم (الكامل) ==========
# يحتوي على جميع النصوص والترجمات المستخدمة في البوت

TRANSLATIONS: Dict[str, Dict[str, Union[Dict, str, List]]] = {
    "ar": {
        "main_menu": {
            "title": "🏪 Shop Crowns",
            "buttons": [
                ["🎮 المودات", "💰 طلبات الشراء"],
                ["🎁 الطلبات المجانية", "📝 الشكاوى"],
                ["🌍 تغيير اللغة", "⭐ تقييم البوت"],
                ["🚀 خدمة شحن كاملة"]
            ]
        },
        "admin_menu": {
            "title": "👑 لوحة التحكم - الأدمن",
            "buttons": [
                ["📊 الإحصائيات", "📢 إذاعة"],
                ["🚫 حظر مستخدم", "✅ فك حظر"],
                ["📋 الطلبات", "📝 التذاكر"],
                ["📜 السجلات", "👥 المستخدمين"],
                ["🎮 تحكم في البوت", "📊 التقييمات"]
            ]
        },
        "messages": {
            "welcome": "🌟 أهلاً بك {name} في متجر SHOP CROWNS 🌟\nاختر خدمة:",
            "welcome_new": "🎉 **اهلاً بك في متجرك المميز Shop Crowns!** 🎉\nاختر من القائمة أدناه 👇",
            "startup_notification": "✅ **البوت شغال بكفاءة عالية**\n\n📊 **المراقبة نشطة**\n🔒 **الأمان مفعل**\n⏰ **المهلات تعمل**\n🚀 جاهز للاستخدام",
            "new_user_notification": "👾 **شخص جديد دخل البوت**\n\n👤 **معلومات العضو الجديد:**\n• الاسم: {name}\n• المعرف: @{username}\n• الآيدي: `{user_id}`\n• 🌐 اللغة: {language}\n\n📊 **إجمالي المستخدمين:** {total_users}",
            "admin_new_order": "📦 **طلب جديد**\n\n📌 **رقم الطلب:** `{order_number}`\n👤 **الاسم:** {name}\n🆔 **User ID:** `{user_id}`\n📝 **Username:** @{username}\n🗣️ **اللغة:** {language}\n🌍 **الدولة:** {country}\n📦 **نوع الطلب:** {order_type}\n📅 **التاريخ:** {date}\n\nاستخدم الأزرار أدناه للتحكم:",
            "order_completed": "✅ **تم تنفيذ طلبك بنجاح**\n\nيمكنك مراجعة حسابك الآن.\nشكراً لاستخدامك متجرنا 🤍",
            "order_processing": "🔄 **جاري تنفيذ طلبك**\n\nسيتم إعلامك عند الانتهاء.\nشكراً لانتظارك 🤍",
            "order_cancelled": "❌ **تم إلغاء طلبك**\n\nعذراً، تم إلغاء طلبك.\nيمكنك التواصل مع الدعم الفني لمزيد من المعلومات.",
            "error": "⚠️ عذراً، حدث خطأ. يرجى المحاولة مرة أخرى.",
            "banned": "🚫 تم حظرك من البوت",
            "rate_limited": "⚠️ أرسلت طلبات كثيرة، انتظر قليلاً",
            "language_changed": "✅ **تم تغيير اللغة بنجاح**",
            "choose_language": "🌐 **اختر لغتك:**",
            "ticket_created": "✅ **تم فتح تذكرة دعم لطلبك**\n\n📦 **الخدمة:** {service}\n🎫 **رقم التذكرة:** `{number}`\n\n💬 سيتم التواصل معك قريباً لإتمام الطلب.",
            "chat_opened": "🔓 **تم فتح محادثة مباشرة مع الدعم الفني**\n\n✅ يمكنك كتابة رسالتك الآن\n🔚 اضغط على زر إنهاء المحادثة عند الانتهاء",
            "chat_message_sent": "✅ **تم إرسال رسالتك إلى الدعم**",
            "chat_ended": "🙏 **شكراً لتواصلك معنا**\n\nلا تتردد في الاتصال بنا مرة أخرى",
            "chat_ended_admin": "🙏 **تم إنهاء المحادثة من قبل الدعم**\n\nشكراً لتواصلك معنا",
            "no_active_chat": "⚠️ **لا توجد محادثة نشطة**\nاستخدم 'فتح شات مباشر' للبدء",
            "rating_title": "⭐ **قيم تجربتك مع البوت:**",
            "rating_thanks": "🙏 **شكراً لتقييمك {rating}⭐** ❤️\n\nتقييمك يساعدنا على تحسين الخدمة.",
            "broadcast_start": "📢 **إذاعة عامة**\n\nاختر نوع المحتوى الذي تريد إرساله للمستخدمين:",
            "broadcast_text_prompt": "📝 **إذاعة نصية**\n\nأرسل النص الذي تريد إذاعته لجميع المستخدمين:",
            "broadcast_photo_prompt": "🖼 **إذاعة صورة**\n\nأرسل الصورة التي تريد إذاعتها لجميع المستخدمين\n(يمكنك إضافة تعليق نصي مع الصورة)",
            "broadcast_video_prompt": "🎥 **إذاعة فيديو**\n\nأرسل الفيديو الذي تريد إذاعته لجميع المستخدمين\n(يمكنك إضافة تعليق نصي مع الفيديو)",
            "broadcast_preview_text": "📢 **معاينة الإذاعة**\n\n📝 **النص:**\n{text}\n\n👥 **عدد المستخدمين المستهدفين:** {count}\n\n⚠️ هل أنت متأكد من إرسال هذه الإذاعة؟",
            "broadcast_preview_photo": "📢 **معاينة الإذاعة**\n\n🖼 **صورة**\n📝 **التعليق:** {caption}\n\n👥 **عدد المستخدمين المستهدفين:** {count}\n\n⚠️ هل أنت متأكد من إرسال هذه الإذاعة؟",
            "broadcast_preview_video": "📢 **معاينة الإذاعة**\n\n🎥 **فيديو**\n📝 **التعليق:** {caption}\n\n👥 **عدد المستخدمين المستهدفين:** {count}\n\n⚠️ هل أنت متأكد من إرسال هذه الإذاعة؟",
            "broadcast_sending": "📢 **جاري إرسال الإذاعة...**\n\n👥 المستخدمين: {total}\n⏳ جاري الإرسال...",
            "broadcast_report": "✅ **تم إرسال الإذاعة بنجاح**\n\n📊 **التقرير النهائي:**\n✅ تم الإرسال: {success} مستخدم\n❌ فشل الإرسال: {failed} مستخدم\n👥 إجمالي المستخدمين: {total}\n\n📅 {date}",
            "broadcast_cancelled": "❌ **تم إلغاء الإذاعة**",
            "no_balance": "❌ **لا يمكنك استخدام هذه الخدمة**\nيمكنك شحن الرصيد عبر قسم طلبات الشراء.",
            "invalid_name": "⚠️ **الاسم غير صالح، حاول مرة أخرى**",
            "invalid_email": "⚠️ **البريد الإلكتروني غير صالح، أعد المحاولة**",
            "invalid_photo": "⚠️ **الرجاء إرسال صورة صالحة**",
            "invalid_video": "⚠️ **الرجاء إرسال فيديو صالح**",
            "processing": "⚡ **جاري تنفيذ طلبك...**\nسيتم إعلامك عند الانتهاء.",
            "back_button": "🔙 رجوع",
            "arabic": "🇸🇦 العربية",
            "english": "🇺🇸 English"
        }
    },
    "en": {
        "main_menu": {
            "title": "🏪 Shop Crowns",
            "buttons": [
                ["🎮 Mods", "💰 Purchase Requests"],
                ["🎁 Free Requests", "📝 Complaints"],
                ["🌍 Change Language", "⭐ Rate Bot"],
                ["🚀 Full Shipping Service"]
            ]
        },
        "admin_menu": {
            "title": "👑 Admin Panel",
            "buttons": [
                ["📊 Statistics", "📢 Broadcast"],
                ["🚫 Ban User", "✅ Unban"],
                ["📋 Orders", "📝 Tickets"],
                ["📜 Logs", "👥 Users"],
                ["🎮 Control Bot", "📊 Ratings"]
            ]
        },
        "messages": {
            "welcome": "🌟 Welcome {name} to SHOP CROWNS 🌟\nChoose a service:",
            "welcome_new": "🎉 **Welcome to your special store Shop Crowns!** 🎉\nChoose from the menu below 👇",
            "startup_notification": "✅ **Bot is running at high efficiency**\n\n📊 **Monitoring active**\n🔒 **Security enabled**\n⏰ **Timeouts working**\n🚀 Ready to use",
            "new_user_notification": "👾 **New user joined the bot**\n\n👤 **New member info:**\n• Name: {name}\n• Username: @{username}\n• ID: `{user_id}`\n• 🌐 Language: {language}\n\n📊 **Total users:** {total_users}",
            "admin_new_order": "📦 **New Order**\n\n📌 **Order Number:** `{order_number}`\n👤 **Name:** {name}\n🆔 **User ID:** `{user_id}`\n📝 **Username:** @{username}\n🗣️ **Language:** {language}\n🌍 **Country:** {country}\n📦 **Order Type:** {order_type}\n📅 **Date:** {date}\n\nUse the buttons below to control:",
            "order_completed": "✅ **Your order has been completed successfully**\n\nYou can check your account now.\nThank you for using our store 🤍",
            "order_processing": "🔄 **Your order is being processed**\n\nYou will be notified when completed.\nThank you for waiting 🤍",
            "order_cancelled": "❌ **Your order has been cancelled**\n\nSorry, your order has been cancelled.\nYou can contact support for more information.",
            "error": "⚠️ Sorry, an error occurred. Please try again.",
            "banned": "🚫 You are banned from the bot",
            "rate_limited": "⚠️ Too many requests, please wait",
            "language_changed": "✅ **Language changed successfully**",
            "choose_language": "🌐 **Choose your language:**",
            "ticket_created": "✅ **Support ticket opened for your request**\n\n📦 **Service:** {service}\n🎫 **Ticket Number:** `{number}`\n\n💬 We will contact you soon to complete the request.",
            "chat_opened": "🔓 **Live chat opened with support**\n\n✅ You can write your message now\n🔚 Press End Chat when finished",
            "chat_message_sent": "✅ **Your message has been sent to support**",
            "chat_ended": "🙏 **Thank you for contacting us**\n\nFeel free to contact us again",
            "chat_ended_admin": "🙏 **Chat ended by support**\n\nThank you for contacting us",
            "no_active_chat": "⚠️ **No active chat**\nUse 'Open Live Chat' to start",
            "rating_title": "⭐ **Rate your experience with the bot:**",
            "rating_thanks": "🙏 **Thank you for your {rating}⭐ rating** ❤️\n\nYour rating helps us improve our service.",
            "broadcast_start": "📢 **General Broadcast**\n\nChoose the content type you want to send to users:",
            "broadcast_text_prompt": "📝 **Text Broadcast**\n\nSend the text you want to broadcast to all users:",
            "broadcast_photo_prompt": "🖼 **Photo Broadcast**\n\nSend the photo you want to broadcast to all users\n(You can add a text caption with the photo)",
            "broadcast_video_prompt": "🎥 **Video Broadcast**\n\nSend the video you want to broadcast to all users\n(You can add a text caption with the video)",
            "broadcast_preview_text": "📢 **Broadcast Preview**\n\n📝 **Text:**\n{text}\n\n👥 **Target Users:** {count}\n\n⚠️ Are you sure you want to send this broadcast?",
            "broadcast_preview_photo": "📢 **Broadcast Preview**\n\n🖼 **Photo**\n📝 **Caption:** {caption}\n\n👥 **Target Users:** {count}\n\n⚠️ Are you sure you want to send this broadcast?",
            "broadcast_preview_video": "📢 **Broadcast Preview**\n\n🎥 **Video**\n📝 **Caption:** {caption}\n\n👥 **Target Users:** {count}\n\n⚠️ Are you sure you want to send this broadcast?",
            "broadcast_sending": "📢 **Sending broadcast...**\n\n👥 Users: {total}\n⏳ Sending...",
            "broadcast_report": "✅ **Broadcast sent successfully**\n\n📊 **Final Report:**\n✅ Sent: {success} users\n❌ Failed: {failed} users\n👥 Total users: {total}\n\n📅 {date}",
            "broadcast_cancelled": "❌ **Broadcast cancelled**",
            "no_balance": "❌ **You cannot use this service**\nYou can recharge via Purchase Requests.",
            "invalid_name": "⚠️ **Invalid name, try again**",
            "invalid_email": "⚠️ **Invalid email, try again**",
            "invalid_photo": "⚠️ **Please send a valid photo**",
            "invalid_video": "⚠️ **Please send a valid video**",
            "processing": "⚡ **Processing your request...**\nYou will be notified when completed.",
            "back_button": "🔙 Back",
            "arabic": "🇸🇦 Arabic",
            "english": "🇺🇸 English"
        }
    }
}


# ========== النظام الجديد (المبسط) للتوافق ==========
# يتم الاحتفاظ به للتوافق مع الكود الجديد

NEW_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "ar": {
        "welcome_new": "🎉 **اهلاً بك في متجرك المميز Shop Crowns!** 🎉\nاختر من القائمة أدناه 👇",
        "back_button": "🔙 رجوع",
        "choose_language": "🌐 **اختر لغتك:**",
        "language_changed": "✅ **تم تغيير اللغة بنجاح**",
        "arabic": "🇸🇦 العربية",
        "english": "🇺🇸 English",
        "error": "⚠️ حدث خطأ، حاول مرة أخرى",
        "banned": "🚫 تم حظرك من البوت"
    },
    "en": {
        "welcome_new": "🎉 **Welcome to your special store Shop Crowns!** 🎉\nChoose from the menu below 👇",
        "back_button": "🔙 Back",
        "choose_language": "🌐 **Choose your language:**",
        "language_changed": "✅ **Language changed successfully**",
        "arabic": "🇸🇦 Arabic",
        "english": "🇺🇸 English",
        "error": "⚠️ Error, please try again",
        "banned": "🚫 You are banned from the bot"
    }
}


# ========== دوال الوصول الموحدة ==========

def get_user_language(user_id: int) -> str:
    """Get user language from database"""
    try:
        return db.get_user_language(user_id)
    except Exception:
        return "ar"


def get_text(user_id: int, key: str, lang: Optional[str] = None, **kwargs) -> str:
    """
    Get translated text by key for user (النظام القديم - الكامل)
    
    Args:
        user_id: User ID to get language preference
        key: Translation key (supports dot notation like 'messages.welcome_new')
        lang: Optional direct language override
        **kwargs: Format parameters
    
    Returns:
        Translated string
    """
    language = lang if lang else get_user_language(user_id)
    
    if language not in TRANSLATIONS:
        language = "ar"
    
    parts = key.split('.')
    current = TRANSLATIONS[language]
    
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part, TRANSLATIONS["ar"].get(part, part))
        else:
            break
    
    text = str(current) if not isinstance(current, dict) else str(current)
    
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    
    return text


def get_simple_text(user_id: int, key: str, **kwargs) -> str:
    """
    Get translated text from the new simplified system
    (للتوافق مع الكود الجديد - يستخدم النظام المبسط)
    """
    lang = get_user_language(user_id)
    if lang not in NEW_TRANSLATIONS:
        lang = "ar"
    
    text = NEW_TRANSLATIONS[lang].get(key, key)
    
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    
    return text


def get_main_menu_buttons(lang: str = "ar") -> List[List[str]]:
    """Get main menu buttons for language"""
    return TRANSLATIONS.get(lang, TRANSLATIONS["ar"])["main_menu"]["buttons"]


def get_admin_menu_buttons(lang: str = "ar") -> List[List[str]]:
    """Get admin menu buttons for language"""
    return TRANSLATIONS.get(lang, TRANSLATIONS["ar"])["admin_menu"]["buttons"]


def get_menu_title(lang: str = "ar", menu: str = "main_menu") -> str:
    """Get menu title for language"""
    return TRANSLATIONS.get(lang, TRANSLATIONS["ar"])[menu]["title"]


def get_supported_languages() -> List[str]:
    """Get list of supported languages"""
    return list(TRANSLATIONS.keys())
