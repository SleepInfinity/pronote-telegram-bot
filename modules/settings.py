from modules.database import get_user_lang
from modules.language import languages
from tgram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

async def make_settings_keyboard(user_lang: str):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=languages[user_lang]["set_language"],
                    callback_data="settings_set_language"
                )
            ]
        ]
    )

async def settings_message(message: Message):
    user_lang=await get_user_lang(message.chat.id)
    await message.reply_text(
        text=languages[user_lang]["settings"],
        reply_markup=await make_settings_keyboard(user_lang)
    )
