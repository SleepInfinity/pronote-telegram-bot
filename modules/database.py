from typing import List
from kvsqlite import Client
from pronotepy import Lesson

db = Client("db.sqlite")

clients = {}


async def get_user_lang(user_id: int) -> str:
    user_languages: dict = (await db.get("user_languages")) or {}
    return user_languages.get(user_id) or "en"


async def set_user_lang(user_id: int, language: str) -> None:
    user_languages: dict = await db.get("user_languages") or {}
    user_languages[user_id] = language
    await db.set("user_languages", user_languages)


async def get_user_lesson(user_id: int, lesson_id: str) -> None | Lesson:
    user_lessons: dict = (await db.get("user_lessons")) or {user_id: {}}
    if user_lessons[user_id]:
        return user_lessons[user_id].get(lesson_id)
    return None


async def set_user_lesson(user_id: int, lesson: Lesson) -> None:
    try:
        user_lessons: dict = await db.get("user_lessons") or {}
    except Exception as _:
        await db.set("user_lessons", {})
        user_lessons: dict = await db.get("user_lessons") or {}
    if user_id not in user_lessons:
        user_lessons[user_id] = {}
    user_lessons[user_id][lesson.id] = lesson
    await db.set("user_lessons", user_lessons)


async def get_user_ids() -> List[int]:
    user_ids = list((await db.get("user_languages")).keys() or [])
    return user_ids
