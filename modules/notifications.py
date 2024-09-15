import threading
import time
from modules.database import clients
from bot_instance import bot
from modules.language import languages
from modules.database import get_user_lang, clients

user_data_lock = threading.Lock()

def enable_notifications(message):
    chat_id=message.chat.id
    user_lang=get_user_lang(chat_id)
    client_credentials = clients.get(chat_id)
    if client_credentials:
        client = client_credentials['client']
    else:
        bot.send_message(chat_id, languages[user_lang]["not_logged_in"])
        return

    try:
        clients[chat_id]["notifications"]['notifications_enabled']
    except KeyError:
        initialize_notifications(message, client)
    
    notifications_settings=clients[chat_id]["notifications"]

    if notifications_settings["notifications_enabled"]:
        bot.reply_to(message, "Notifications are already enabled.")
        return

    with user_data_lock:
        notifications_settings['notifications_enabled'] = True
        bot.reply_to(message, "Notifications have been enabled.")
        # Restart the user's thread if it's not running
        if notifications_settings['thread'] is None:
            start_user_thread(chat_id)

def disable_notifications(message):
    chat_id=message.chat.id
    user_lang=get_user_lang(chat_id)
    client_credentials = clients.get(chat_id)
    if client_credentials:
        client = client_credentials['client']
    else:
        bot.send_message(chat_id, languages[user_lang]["not_logged_in"])
        return
    try:
        clients[chat_id]["notifications"]['notifications_enabled']
    except KeyError:
        initialize_notifications(message, client)

    notifications_settings=clients[chat_id]["notifications"]

    if not notifications_settings["notifications_enabled"]:
        bot.reply_to(message, "Notifications are already disabled.")
        return

    with user_data_lock:
        notifications_settings['notifications_enabled'] = False
        bot.reply_to(message, "Notifications have been disabled.")
        stop_user_thread(chat_id)

def initialize_notifications(message, client):
    grades=get_grades(client)
    known_grades=set(grade for grade in grades)
    stop_event=threading.Event()
    with user_data_lock:
        clients[message.chat.id]["notifications"]={
            'known_grades': known_grades,
            'notifications_enabled': True,
            'interval': 300,
            'stop_event': stop_event,
            'thread': None
        }

def get_grades(client):
    grades=client.current_period.grades
    return grades

def start_user_thread(chat_id):
    user_settings = clients.get(chat_id)["notifications"]
    if user_settings and user_settings['thread'] is None:
        stop_event = user_settings['stop_event']
        # Start the thread
        checking_thread = threading.Thread(target=check_for_new_grades, args=(chat_id, stop_event))
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

def check_for_new_grades(chat_id, stop_event):
    while not stop_event.is_set():
        print("Checking for new grades")
        user_lang=get_user_lang(chat_id)
        with user_data_lock:
            client_credentials = clients.get(chat_id)
            if client_credentials:
                client = client_credentials['client']
            else:
                bot.send_message(chat_id, languages[user_lang]["not_logged_in"])
                break
        
            user_settings = client_credentials["notifications"]
            if not user_settings:
                # User data no longer exists, exit the thread
                break
            notifications_enabled = user_settings['notifications_enabled']
            interval = user_settings['interval']
            known_grades = user_settings['known_grades']

        if notifications_enabled:
            try:
                # Fetch the current grades
                grades = client.current_period.grades
                current_grades = set(grade for grade in grades)

                # Find new grades
                new_grades = current_grades - known_grades

                if new_grades:
                    # Update known grades
                    known_grades.update(new_grades)
                    with user_data_lock:
                        user_settings['known_grades'] = known_grades

                    # Send notifications for new grades
                    for grade in grades:
                        if grade.id in new_grades:
                            message = (
                                f"📢 **New Grade Received!**\n"
                                f"**Subject:** {grade.subject.name}\n"
                                f"**Grade:** {grade.grade}/{grade.out_of}\n"
                                f"**Date:** {grade.date.strftime('%Y-%m-%d')}\n"
                                f"**Comment:** {grade.comment if grade.comment else languages[user_lang]["no_comment"]}"
                            )
                            bot.send_message(chat_id, message, parse_mode='Markdown')
                else:
                    print("No new grades")
            except Exception as e:
                print(f"An error occurred for chat_id {chat_id}: {e}")

        # Sleep for the user's specified interval or until stop_event is set
        stop_event.wait(timeout=interval)

    print(f"Thread for chat_id {chat_id} has been stopped.")