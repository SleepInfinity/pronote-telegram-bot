import threading
import time
import pytz
import os
import datetime
from modules.database import clients
from babel.dates import format_date
from bot_instance import bot
from modules.language import languages
from dotenv import load_dotenv
from modules.database import get_user_lang, clients
from utils.logger import logger

user_data_lock = threading.Lock()
load_dotenv()
timezone = pytz.timezone(os.getenv('TIMEZONE') or "UTC")
polling_interval=int(os.getenv('POLLING_INTERVAL') or 300)

def get_client(chat_id):
    user_lang=get_user_lang(chat_id)
    client_credentials = clients.get(chat_id)
    if client_credentials:
        client = client_credentials['client']
        return client
    bot.send_message(chat_id, languages[user_lang]["not_logged_in"])

def enable_notifications(message):
    chat_id=message.chat.id
    user_lang=get_user_lang(chat_id)
    client=get_client(chat_id)
    if not client:
        return
    
    initialize_notifications(message, client)
    
    notifications_settings=clients[chat_id]["notifications"]

    if notifications_settings["notifications_enabled"]:
        bot.reply_to(message, languages[user_lang]["notifications_already_enabled"])
        return

    with user_data_lock:
        notifications_settings['notifications_enabled'] = True
        bot.reply_to(message, languages[user_lang]["notifications_enabled"])
        # Restart the user's thread if it's not running
        if notifications_settings['thread'] is None:
            start_user_thread(chat_id)

def disable_notifications(message):
    chat_id=message.chat.id
    user_lang=get_user_lang(chat_id)
    client=get_client(chat_id)
    if not client:
        return
    
    initialize_notifications(message, client)

    notifications_settings=clients[chat_id]["notifications"]

    if not notifications_settings["notifications_enabled"]:
        bot.reply_to(message, languages[user_lang]["notifications_already_disabled"])
        return

    with user_data_lock:
        notifications_settings['notifications_enabled'] = False
        bot.reply_to(message, languages[user_lang]["notifications_disabled"])
        stop_user_thread(chat_id)

def is_notifications_initialized(chat_id):
    try:
        clients[chat_id]["notifications"]['notifications_enabled']
        return True
    except KeyError:
        return False


def initialize_notifications(message, client):
    chat_id=message.chat.id
    if is_notifications_initialized(chat_id):
        return
    grades=get_grades(client)
    known_grades=set(grade.id for grade in grades)
    homework=get_homework(client)
    known_homework=set(hw.id for hw in homework)
    stop_event=threading.Event()
    with user_data_lock:
        clients[message.chat.id]["notifications"]={
            'known_grades': known_grades,
            'known_homework': known_homework,
            'notifications_enabled': False,
            'interval': polling_interval,
            'stop_event': stop_event,
            'thread': None
        }

def get_grades(client):
    grades=client.current_period.grades
    return grades

def get_homework(client):
    today=datetime.datetime.now(timezone).date()
    homework = client.homework(today)
    return homework

def start_user_thread(chat_id):
    user_settings = clients.get(chat_id)["notifications"]
    if user_settings and user_settings['thread'] is None:
        stop_event = user_settings['stop_event']
        # Start the thread
        checking_thread = threading.Thread(target=check_for_new_notifications, args=(chat_id, stop_event))
        checking_thread.daemon = True
        user_settings['thread'] = checking_thread
        checking_thread.start()

def stop_user_thread(chat_id):
    user_settings = clients.get(chat_id)["notifications"]
    if user_settings and user_settings['thread'] is not None:
        # Signal the thread to stop
        user_settings['stop_event'].set()
        # Wait for the thread to finish
        user_settings['thread'].join()
        # Clean up
        user_settings['thread'] = None
        user_settings['stop_event'] = threading.Event()

def check_for_new_grades(chat_id, client, known_grades, user_settings):
    logger.debug("Checking for new grades")
    # Fetch the current grades
    grades = get_grades(client)
    current_grades = set(grade.id for grade in grades)

    # Find new grades
    new_grades = current_grades - known_grades

    if new_grades:
        # Update known grades
        known_grades.update(new_grades)
        user_settings['known_grades'] = known_grades

        # Send notifications for new grades
        for grade in grades:
            if grade.id in new_grades:
                send_grade_notification(grade, chat_id)      
    else:
        logger.info("No new grades")

def check_for_new_homework(chat_id, client, known_homework, user_settings):
    logger.debug("Checking for new homework")
    homework=get_homework(client)
    current_homework=set(hw.id for hw in homework)

    new_homework=current_homework-known_homework

    if new_homework:
        known_homework.update(new_homework)
        user_settings['known_homework'] = known_homework

        for hw in homework:
            if hw.id in new_homework:
                send_homework_notification(hw, chat_id)
    else:
        logger.info("No new homework")

def send_grade_notification(grade, chat_id):
    user_lang=get_user_lang(chat_id)
    message=languages[user_lang]["new_grade_notification"].format(
        subject=grade.subject.name,
        grade=grade.grade,
        out_of=grade.out_of,
        date=grade.date.strftime('%Y-%m-%d'),
        comment=grade.comment if grade.comment else languages[user_lang]['no_comment']
    )
    bot.send_message(chat_id, message, parse_mode='Markdown')

def send_homework_notification(homework, chat_id):
    user_lang=get_user_lang(chat_id)
    user_locale = languages[user_lang]["locale"]
    message=languages[user_lang]["new_homework_notification"].format(
        subject=homework.subject.name,
        date=format_date(
            homework.date,
            format="EEEE d MMMM",
            locale=user_locale
        ),
        description=homework.description
    )
    bot.send_message(chat_id, message, parse_mode='Markdown')

def check_for_new_notifications(chat_id, stop_event):
    while not stop_event.is_set():
        with user_data_lock:
            client_credentials = clients.get(chat_id)
            client=get_client(chat_id)
            if not client:
                stop_user_thread(chat_id)
                break
            client.session_check()

            user_settings = client_credentials["notifications"]
            if not user_settings:
                # User data no longer exists, exit the thread
                stop_user_thread(chat_id)
                break
            notifications_enabled = user_settings['notifications_enabled']
            interval = user_settings['interval']

            known_grades = user_settings['known_grades']
            known_homework = user_settings['known_homework']

        if notifications_enabled:
            try:
                check_for_new_grades(chat_id, client, known_grades, user_settings)
                check_for_new_homework(chat_id, client, known_homework, user_settings)
            except Exception as e:
                logger.error(f"An error occurred for chat_id {chat_id}: {e}")
        else:
            # exit the thread as the notifications are disabled.
            stop_user_thread(chat_id)
            break

        # Sleep for the user's specified interval or until stop_event is set
        stop_event.wait(timeout=interval)

    logger.info(f"Thread for chat_id {chat_id} has been stopped.")