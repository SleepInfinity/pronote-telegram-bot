import asyncio
import pytz
import os
import datetime
from tgram.types import Message
import asyncio
from asyncio import CancelledError
from modules.database import clients
from babel.dates import format_date
from bot_instance import bot
from modules.language import languages
from dotenv import load_dotenv
from modules.database import get_user_lang, clients
from utils.hashing import get_grade_unique_id, get_homework_unique_id
from utils.logger import logger

user_data_lock = asyncio.Lock()
load_dotenv()
timezone = pytz.timezone(os.getenv("TIMEZONE") or "UTC")
polling_interval = int(os.getenv("POLLING_INTERVAL") or 300)


async def get_client(chat_id):
    user_lang = await get_user_lang(chat_id)
    client_credentials = clients.get(chat_id)
    if client_credentials:
        client = client_credentials["client"]
        return client
    await bot.send_message(chat_id, languages[user_lang]["not_logged_in"])


async def start_user_task(chat_id):
    notifications_settings = clients[chat_id]["notifications"]
    if notifications_settings and notifications_settings.get("task") is None:
        task = asyncio.create_task(check_for_new_notifications(chat_id))
        notifications_settings["task"] = task


async def stop_user_task(chat_id):
    notifications_settings = clients[chat_id]["notifications"]
    if notifications_settings and notifications_settings.get("task") is not None:
        task = notifications_settings["task"]
        task.cancel()
        try:
            await task
        except CancelledError:
            pass

        notifications_settings["task"] = None


async def enable_notifications(message: Message):
    chat_id = message.chat.id
    user_lang = await get_user_lang(chat_id)
    client = await get_client(chat_id)
    if not client:
        return

    await initialize_notifications(message, client)

    notifications_settings = clients[chat_id]["notifications"]

    if notifications_settings["notifications_enabled"]:
        return await message.reply_text(
            languages[user_lang]["notifications_already_enabled"]
        )

    async with user_data_lock:
        notifications_settings["notifications_enabled"] = True
        await message.reply_text(languages[user_lang]["notifications_enabled"])
        await start_user_task(chat_id)


async def disable_notifications(message: Message):
    chat_id = message.chat.id
    user_lang = await get_user_lang(chat_id)
    client = await get_client(chat_id)
    if not client:
        return

    await initialize_notifications(message, client)

    notifications_settings = clients[chat_id]["notifications"]

    if not notifications_settings["notifications_enabled"]:
        return await message.reply_text(
            languages[user_lang]["notifications_already_disabled"]
        )

    async with user_data_lock:
        notifications_settings["notifications_enabled"] = False
        await message.reply_text(languages[user_lang]["notifications_disabled"])
        await stop_user_task(chat_id)


async def is_notifications_initialized(chat_id):
    try:
        clients[chat_id]["notifications"]["notifications_enabled"]
        return True
    except KeyError:
        return False


async def initialize_notifications(message: Message, client):
    chat_id = message.chat.id
    if await is_notifications_initialized(chat_id):
        return
    logger.debug(f"[{str(chat_id)}] Notifications initialization executed.")
    grades = await get_grades(client)
    known_grades = set(get_grade_unique_id(grade) for grade in grades)
    homework = await get_homework(client)
    known_homework = set(get_homework_unique_id(hw) for hw in homework)
    async with user_data_lock:
        clients[message.chat.id]["notifications"] = {
            "known_grades": known_grades,
            "known_homework": known_homework,
            "notifications_enabled": False,
            "interval": polling_interval,
            "task": None,
        }


async def get_grades(client):
    grades = client.current_period.grades
    return grades


async def get_homework(client):
    today = datetime.datetime.now(timezone).date()
    homework = client.homework(today)
    return homework


async def check_for_new_grades(chat_id, client, known_grades, user_settings):
    logger.debug(f"[{str(chat_id)}] Checking for new grades")
    # Fetch the current grades
    grades = await get_grades(client)
    current_grades = set(get_grade_unique_id(grade) for grade in grades)

    # Find new grades
    new_grades = current_grades - known_grades

    if new_grades:
        # Update known grades
        known_grades.update(new_grades)
        user_settings["known_grades"] = known_grades

        # Send notifications for new grades
        for grade in grades:
            if get_grade_unique_id(grade) in new_grades:
                await send_grade_notification(grade, chat_id)
    else:
        logger.info(f"[{str(chat_id)}] No new grades")


async def check_for_new_homework(chat_id, client, known_homework, user_settings):
    logger.debug(f"[{str(chat_id)}] Checking for new homework")
    homework = await get_homework(client)
    current_homework = set(get_homework_unique_id(hw) for hw in homework)

    new_homework = current_homework - known_homework

    if new_homework:
        known_homework.update(new_homework)
        user_settings["known_homework"] = known_homework

        for hw in homework:
            if get_homework_unique_id(hw) in new_homework:
                await send_homework_notification(hw, chat_id)
    else:
        logger.info(f"[{str(chat_id)}] No new homework")


async def send_grade_notification(grade, chat_id):
    user_lang = await get_user_lang(chat_id)
    message = languages[user_lang]["new_grade_notification"].format(
        subject=grade.subject.name,
        grade=grade.grade,
        out_of=grade.out_of,
        date=grade.date.strftime("%Y-%m-%d"),
        comment=grade.comment if grade.comment else languages[user_lang]["no_comment"],
    )
    await bot.send_message(chat_id, message)


async def send_homework_notification(homework, chat_id):
    user_lang = await get_user_lang(chat_id)
    user_locale = languages[user_lang]["locale"]
    message = languages[user_lang]["new_homework_notification"].format(
        subject=homework.subject.name,
        date=format_date(homework.date, format="EEEE d MMMM", locale=user_locale),
        description=homework.description,
    )
    await bot.send_message(chat_id, message)


async def check_for_new_notifications(chat_id):
    try:
        while True:
            async with user_data_lock:
                client_credentials = clients.get(chat_id)
                client = await get_client(chat_id)
                if not client:
                    await stop_user_task(chat_id)
                    break
                client.session_check()

                user_settings = client_credentials["notifications"]
                if not user_settings:
                    # User data no longer exists, exit the thread
                    await stop_user_task(chat_id)
                    break
                notifications_enabled = user_settings["notifications_enabled"]
                interval = user_settings["interval"]

                known_grades = user_settings["known_grades"]
                known_homework = user_settings["known_homework"]

            if notifications_enabled:
                try:
                    await check_for_new_grades(
                        chat_id, client, known_grades, user_settings
                    )
                    await check_for_new_homework(
                        chat_id, client, known_homework, user_settings
                    )
                except Exception as e:
                    logger.error(f"[{str(chat_id)}] An error occurred: {e}")
            else:
                await stop_user_task(chat_id)
                break

            await asyncio.sleep(interval)
    except CancelledError:
        logger.info(f"[{str(chat_id)}] Task has been cancelled.")
    finally:
        logger.info(f"[{str(chat_id)}] Task has been stopped.")
