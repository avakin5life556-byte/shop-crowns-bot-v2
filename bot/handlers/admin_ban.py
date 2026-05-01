from aiogram import Router, types
from aiogram.filters import Command
from bot.database.db import db
from bot.config import ADMIN_ID

router = Router()

@router.message(Command("ban"))
async def ban_user(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        user_id = int(message.text.split(maxsplit=1)[1])
    except:
        await message.reply("❌ اكتب ID المستخدم بعد الأمر")
        return

    if hasattr(db, "ban_user"):
        db.ban_user(user_id)

    await message.reply(f"✅ تم حظر المستخدم {user_id}")


def register_ban_handlers(dp):
    dp.include_router(router)
