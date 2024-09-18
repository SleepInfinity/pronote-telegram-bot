import json
from modules.database import db
from bot_instance import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from modules.database import get_user_lang

with open('languages.json', 'r', encoding='utf-8') as f:
    languages = json.load(f)

def make_languages_keyboard():
    languages_keyboard = InlineKeyboardMarkup()
    for language in list(languages.values()):
        lang_button=InlineKeyboardButton(text=f"{language['name']} {language['flag']}", callback_data=f"set_lang_{language['code']}")
        languages_keyboard.row(lang_button)
    return languages_keyboard

def setup_user_lang(user_id):
    user_languages = db.get("user_languages") or {}
    if user_languages.get(user_id):
        return True
    
    bot.send_message(user_id, languages["en"]["choose_language"], reply_markup=make_languages_keyboard())
    return False

def change_user_lang(message):
    user_id=message.chat.id
    user_lang=get_user_lang(user_id)
    bot.edit_message_text(
        message_id=message.id,
        chat_id=message.chat.id,
        text=languages[user_lang]["choose_language"],
        reply_markup=make_languages_keyboard()
    )
