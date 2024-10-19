import json
from modules.database import db
from tgram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from bot_instance import bot
from modules.database import get_user_lang

with open("languages.json", "r", encoding="utf-8") as f:
    languages: dict = json.load(f)


async def make_languages_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=f"{language['name']} {language['flag']}",
                    callback_data=f"set_lang_{language['code']}",
                )
            ]
            for language in list(languages.values())
        ]
    )


async def setup_user_lang(user_id: int) -> bool:
    user_languages: dict = await db.get("user_languages") or {}
    if user_languages.get(user_id):
        return True

    await bot.send_message(
        user_id,
        languages["en"]["choose_language"],
        reply_markup=await make_languages_keyboard(),
    )
    return False


async def change_user_lang(message: Message) -> None:
    user_id: int = message.chat.id
    user_lang: str = await get_user_lang(user_id)
    await message.edit_text(
        text=languages[user_lang]["choose_language"],
        reply_markup=await make_languages_keyboard(),
    )
