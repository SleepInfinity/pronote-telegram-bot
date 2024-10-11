from kvsqlite import Client

db = Client("db.sqlite")

clients = {}


async def get_user_lang(user_id):
    user_languages = (await db.get("user_languages")) or {}
    return user_languages.get(user_id) or "en"


async def set_user_lang(user_id, language):
    user_languages = await db.get("user_languages") or {}
    user_languages[user_id] = language
    await db.set("user_languages", user_languages)


async def get_user_lesson(user_id, lesson_id):
    user_lessons = (await db.get("user_lessons")) or {user_id: {}}
    if user_lessons[user_id]:
        return user_lessons[user_id].get(str(user_id) + "_" + str(lesson_id))
    return None


async def set_user_lesson(user_id, lesson):
    try:
        user_lessons = await db.get("user_lessons") or {}
    except:
        await db.set("user_lessons", {})
        user_lessons = await db.get("user_lessons") or {}
    if user_id not in user_lessons:
        user_lessons[user_id] = {}
    user_lessons[user_id][str(user_id) + "_" + str(lesson.id)] = lesson
    await db.set("user_lessons", user_lessons)


async def get_user_ids():
    user_ids = list((await db.get("user_languages")).keys() or [])
    return user_ids
