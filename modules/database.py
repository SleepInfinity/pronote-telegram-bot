from kvsqlite.sync import Client

db = Client("db.sqlite")

clients={}

def get_user_lang(user_id):
    user_languages = db.get("user_languages") or {}
    return user_languages.get(user_id)

def set_user_lang(user_id, language):
    user_languages = db.get("user_languages") or {}
    user_languages[user_id] = language
    db.set("user_languages", user_languages)