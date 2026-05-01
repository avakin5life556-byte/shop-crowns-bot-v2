from aiogram import types, Dispatcher
from bot.database.db import db
from bot.config import ADMIN_ID


def register_ban_handlers(dp: Dispatcher):

    @dp.message_handler(commands=['ban'])
    async def ban_user(message: types.Message):
        if message.from_user.id != ADMIN_ID:
            return

        try:
            user_id = int(message.get_args())
        except:
            await message.reply("❌ اكتب ID المستخدم بعد الأمر")
            return

        # محاولة حظر المستخدم
        if hasattr(db, "ban_user"):
            db.ban_user(user_id)

        await message.reply(f"✅ تم حظر المستخدم {user_id}")
