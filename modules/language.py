import json
from modules.database import db
from bot_instance import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

with open('languages.json', 'r', encoding='utf-8') as f:
    languages = json.load(f)

def setup_user_lang(user_id):
    user_languages = db.get("user_languages") or {}
    if user_languages.get(user_id):
        return True
    languages_keyboard = InlineKeyboardMarkup()
    english_button = InlineKeyboardButton(text="English", callback_data="set_lang_en")
    french_button = InlineKeyboardButton(text="French", callback_data="set_lang_fr")
    languages_keyboard.row(english_button)
    languages_keyboard.row(french_button)
    bot.send_message(user_id, languages["en"]["choose_language"], reply_markup=languages_keyboard)
    return False
