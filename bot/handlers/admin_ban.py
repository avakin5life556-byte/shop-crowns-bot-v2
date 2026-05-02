from aiogram import Router, types
from aiogram.filters import Command
from bot.database.db import db
from bot.config import ADMIN_ID
import logging

# إعداد logging
logger = logging.getLogger(__name__)

router = Router()


def is_admin(user_id: int) -> bool:
    """التحقق من صلاحيات الأدمن"""
    return user_id == ADMIN_ID


@router.message(Command("ban_simple"))
async def ban_user(message: types.Message):
    """
    نسخة مبسطة من الحظر (احتياطية)
    تم تغيير الأمر إلى ban_simple لتجنب التعارض مع admin.py
    """
    # التحقق من الصلاحيات
    if not is_admin(message.from_user.id):
        logger.warning(f"محاولة غير مصرح بها من المستخدم {message.from_user.id} لأمر ban_simple")
        return
    
    # تحليل الأمر
    parts = message.text.split(maxsplit=1)
    
    if len(parts) < 2:
        await message.reply("❌ **خطأ:** اكتب ID المستخدم بعد الأمر\n\nمثال:\n`/ban_simple 123456789`", parse_mode='Markdown')
        return
    
    # محاولة تحويل ID إلى رقم
    try:
        user_id = int(parts[1])
    except ValueError:
        await message.reply("❌ **خطأ:** ID المستخدم غير صالح\n\nيجب أن يكون رقماً فقط", parse_mode='Markdown')
        return
    
    # التأكد من أن المستخدم موجود في قاعدة البيانات
    user_info = db.get_user_info(user_id) if hasattr(db, "get_user_info") else None
    if not user_info:
        await message.reply(f"⚠️ **تحذير:** المستخدم `{user_id}` غير موجود في قاعدة البيانات\n\nسيتم حظره مع ذلك", parse_mode='Markdown')
    
    # تنفيذ الحظر
    try:
        if hasattr(db, "ban_user"):
            result = db.ban_user(user_id)
            if result:
                logger.info(f"تم حظر المستخدم {user_id} بواسطة الأدمن {message.from_user.id} (ban_simple)")
            else:
                logger.error(f"فشل حظر المستخدم {user_id}")
                await message.reply(f"❌ **فشل الحظر:** حدث خطأ أثناء حظر المستخدم `{user_id}`", parse_mode='Markdown')
                return
        else:
            logger.error("دالة ban_user غير موجودة في قاعدة البيانات")
            await message.reply("❌ **خطأ داخلي:** دالة الحظر غير متوفرة", parse_mode='Markdown')
            return
    except Exception as e:
        logger.error(f"استثناء أثناء حظر المستخدم {user_id}: {e}")
        await message.reply(f"❌ **حدث خطأ:** {str(e)}", parse_mode='Markdown')
        return
    
    # تسجيل العملية في سجل الأدمن
    try:
        if hasattr(db, "log_admin_action"):
            db.log_admin_action(message.from_user.id, 'ban_simple', user_id, None, f"تم الحظر عبر أمر ban_simple")
            logger.info(f"تم تسجيل عملية حظر المستخدم {user_id} في السجلات")
    except Exception as e:
        logger.error(f"فشل تسجيل عملية الحظر: {e}")
    
    # إرسال رسالة للمستخدم المحظور
    try:
        await message.bot.send_message(
            user_id, 
            "🚫 **تم حظر حسابك من البوت**\n\nإذا كنت تعتقد أن هذا خطأ، يرجى التواصل مع الدعم الفني.", 
            parse_mode='Markdown'
        )
        logger.info(f"تم إرسال إشعار الحظر للمستخدم {user_id}")
    except Exception as e:
        # المستخدم قد يكون حظر البوت أو ليس لديه حساب
        logger.warning(f"فشل إرسال إشعار الحظر للمستخدم {user_id}: {e}")
        await message.reply(f"⚠️ **ملاحظة:** لم يتم إرسال إشعار للمستخدم `{user_id}` (ربما قام بحظر البوت)", parse_mode='Markdown')
    
    # تأكيد الحظر للأدمن
    user_name = user_info.get('full_name', 'غير معروف') if user_info else 'غير معروف'
    await message.reply(
        f"✅ **تم حظر المستخدم بنجاح**\n\n"
        f"📌 **المستخدم:** `{user_id}`\n"
        f"👤 **الاسم:** {user_name}\n"
        f"🕐 **بواسطة:** الأدمن {message.from_user.id}",
        parse_mode='Markdown'
    )


def register_ban_handlers(dp):
    """تسجيل معالج الحظر"""
    dp.include_router(router)
    logger.info("تم تسجيل معالج ban_simple بنجاح")
