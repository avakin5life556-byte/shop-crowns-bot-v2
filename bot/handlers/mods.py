from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.database import db
from bot.keyboards.inline import get_mods_keyboard, get_back_keyboard, get_back_button
from bot.keyboards.reply import get_main_keyboard
from bot.config import MOD_LINKS
from bot.utils.helpers import is_rate_limited

router = Router()

#      
MODS = {
    'sky': {
        'ar': ' Sky Mod',
        'en': ' Sky Mod',
        'link': MOD_LINKS['sky']
    },
    'bull': {
        'ar': ' Bull Mod',
        'en': ' Bull Mod',
        'link': f"{MOD_LINKS['bull']}\n{MOD_LINKS['bull_alt']}"
    },
    'gold': {
        'ar': ' Gold Mod',
        'en': ' Gold Mod',
        'link': MOD_LINKS['gold']
    }
}


# ==========    ==========
@router.message(F.text.in_({' ', ' Mods'}))
async def show_mods(message: Message):
    """   """
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    if db.is_user_banned(user_id):
        await message.answer("    " if lang == 'ar' else " You are banned", parse_mode='Markdown')
        return
    
    await message.answer(
        " ** **\n\n    :" if lang == 'ar' else " **Available Mods**\n\nChoose the mod you want to download:",
        reply_markup=get_mods_keyboard(lang),
        parse_mode='Markdown'
    )


# ==========    ==========
@router.callback_query(F.data.in_(['mod_sky', 'mod_bull', 'mod_gold']))
async def handle_mod_selection(callback: CallbackQuery):
    """    """
    user_id = callback.from_user.id
    mod_key = callback.data.split('_')[1]
    lang = db.get_user_language(user_id)
    
    #   
    if db.is_user_banned(user_id):
        await callback.answer("    " if lang == 'ar' else " You are banned", show_alert=True)
        return
    
    #    
    if is_rate_limited(user_id, 'mod_download', limit=10, window=60):
        await callback.answer("     " if lang == 'ar' else " Too many requests, wait", show_alert=True)
        return
    
    #    
    mod_info = MODS.get(mod_key)
    if not mod_info:
        await callback.answer("   ", show_alert=True)
        return
    
    mod_name = mod_info['ar'] if lang == 'ar' else mod_info['en']
    mod_link = mod_info['link']
    
    #   
    message_text = (
        f" **{mod_name}**\n\n"
        f" ** :**\n"
        f"`{mod_link}`\n\n"
        f"          "
        if lang == 'ar' else
        f" **{mod_name}**\n\n"
        f" **Download Link:**\n"
        f"`{mod_link}`\n\n"
        f" Long press on the link then select open in browser"
    )
    
    #    
    await callback.message.edit_text(
        " **   **" if lang == 'ar' else " **Mod selected successfully**",
        reply_markup=get_back_keyboard(lang),
        parse_mode='Markdown'
    )
    
    await callback.message.answer(
        message_text,
        parse_mode='Markdown'
    )
    
    #   
    db.log_admin_action(user_id, f'download_mod_{mod_key}', user_id, None, f'  {mod_name}')
    
    await callback.answer()


# ==========      ( ) ==========
@router.message(F.text.in_({' ', 'Sky Mod', '/sky'}))
async def send_sky_mod(message: Message):
    """   """
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    if db.is_user_banned(user_id):
        await message.answer("    " if lang == 'ar' else " You are banned", parse_mode='Markdown')
        return
    
    mod_name = " Sky Mod"
    mod_link = MOD_LINKS['sky']
    
    text = (
        f" **{mod_name}**\n\n"
        f" ** :**\n"
        f"`{mod_link}`"
    )
    
    await message.answer(text, parse_mode='Markdown')


@router.message(F.text.in_({' ', 'Bull Mod', '/bull'}))
async def send_bull_mod(message: Message):
    """   """
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    if db.is_user_banned(user_id):
        await message.answer("    " if lang == 'ar' else " You are banned", parse_mode='Markdown')
        return
    
    mod_name = " Bull Mod"
    mod_link = f"{MOD_LINKS['bull']}\n{MOD_LINKS['bull_alt']}"
    
    text = (
        f" **{mod_name}**\n\n"
        f" ** :**\n"
        f"`{mod_link}`"
    )
    
    await message.answer(text, parse_mode='Markdown')


@router.message(F.text.in_({' ', 'Gold Mod', '/gold'}))
async def send_gold_mod(message: Message):
    """   """
    user_id = message.from_user.id
    lang = db.get_user_language(user_id)
    
    if db.is_user_banned(user_id):
        await message.answer("    " if lang == 'ar' else " You are banned", parse_mode='Markdown')
        return
    
    mod_name = " Gold Mod"
    mod_link = MOD_LINKS['gold']
    
    text = (
        f" **{mod_name}**\n\n"
        f" ** :**\n"
        f"`{mod_link}`"
    )
    
    await message.answer(text, parse_mode='Markdown')


# ==========   ==========
@router.callback_query(F.data == "back_to_mods")
async def back_to_mods(callback: CallbackQuery):
    """   """
    user_id = callback.from_user.id
    lang = db.get_user_language(user_id)
    
    await callback.message.edit_text(
        " ** **\n\n    :" if lang == 'ar' else " **Available Mods**\n\nChoose the mod you want to download:",
        reply_markup=get_mods_keyboard(lang),
        parse_mode='Markdown'
    )
    await callback.answer()


def register_mods_handlers(dp):
    """  """
    dp.include_router(router)
