from bot_instance import bot
from modules.database import get_user_lang
from modules.language import languages
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def settings_message(message):
    user_id=message.chat.id
    user_lang=get_user_lang(user_id)
    settings_keyboard=InlineKeyboardMarkup()
    set_language_button=InlineKeyboardButton(
        text=languages[user_lang]["set_language"],
        callback_data="settings_set_language"
    )
    settings_keyboard.row(set_language_button)
    bot.reply_to(
        message,
        text=languages[user_lang]["settings"],
        reply_markup=settings_keyboard
    )
