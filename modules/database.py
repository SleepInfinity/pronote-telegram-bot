from kvsqlite.sync import Client

db = Client("db.sqlite")

clients={}

def get_user_lang(user_id):
    user_languages = db.get("user_languages") or {}
    return user_languages.get(user_id) or "en"

def set_user_lang(user_id, language):
    user_languages = db.get("user_languages") or {}
    user_languages[user_id] = language
    db.set("user_languages", user_languages)

def get_user_lesson(user_id, lesson_id):
    user_lessons=db.get("user_lessons") or {}
    if user_lessons[user_id]:
        return user_lessons[user_id].get(str(user_id)+"_"+str(lesson_id))
    return None

def set_user_lesson(user_id, lesson):
    user_lessons=db.get("user_lessons") or {}
    user_lessons[user_id][str(user_id)+"_"+str(lesson.id)]=lesson
    db.set("user_lessons", user_lessons)