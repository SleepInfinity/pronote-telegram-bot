import os
import io
import telebot
import pronotepy
import datetime
import requests
import json
from pyzbar.pyzbar import decode
from PIL import Image
from uuid import uuid4
from dotenv import load_dotenv
from kvsqlite.sync import Client
from pronotepy.ent import lyceeconnecte_aquitaine
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()

db = Client("db.sqlite")

clients = {}

with open('languages.json', 'r') as f:
    languages = json.load(f)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def get_user_lang(user_id):
    user_languages = db.get("user_languages") or {}
    return user_languages.get(user_id)

def set_user_lang(user_id, language):
    user_languages = db.get("user_languages") or {}
    user_languages[user_id] = language
    db.set("user_languages", user_languages)

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

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_lang_"))
def setup_user_lang_query_handler(call):
    lang = call.data.split("set_lang_")[1]
    set_user_lang(call.message.chat.id, lang)
    bot.edit_message_text(
        message_id=call.message.id, 
        chat_id=call.message.chat.id, 
        text=languages[get_user_lang(call.message.chat.id)]["language_set"]
    )

@bot.message_handler(commands=['start'])
def start(message):
    if not setup_user_lang(message.chat.id):
        return
    bot.send_message(
        message.chat.id, 
        languages[get_user_lang(message.chat.id)]["welcome"]
    )

@bot.message_handler(commands=['login'])
def login(message):
    client_credentials = clients.get(message.chat.id)
    if client_credentials:
        client=client_credentials["client"]
        bot.reply_to(message, languages[get_user_lang(message.chat.id)]["already_logged_in"].format(username=client.username))
        return
    available_login_methods_keyboard = InlineKeyboardMarkup()
    qrcode_button = InlineKeyboardButton(text=languages[get_user_lang(message.chat.id)]["qrcode_login"], callback_data="login_qrcode")
    pronote_button = InlineKeyboardButton(text=languages[get_user_lang(message.chat.id)]["pronote_login"], callback_data="login_pronote")
    lyceeconnecte_aquitaine_button = InlineKeyboardButton(text=languages[get_user_lang(message.chat.id)]["lycee_connecte_local"], callback_data="login_lyceeconnecte_aquitaine")
    available_login_methods_keyboard.row(qrcode_button)
    available_login_methods_keyboard.row(pronote_button)
    available_login_methods_keyboard.row(lyceeconnecte_aquitaine_button)
    bot.send_message(
        message.chat.id, 
        languages[get_user_lang(message.chat.id)]["select_login_method"],
        reply_markup=available_login_methods_keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("login_"))
def handle_login_method(call):
    if call.data == "login_qrcode":
        handle_login_qrcode(call)
    elif call.data == "login_pronote":
        handle_login_pronote(call)
    elif call.data == "login_lyceeconnecte_aquitaine":
        handle_login_lyceeconnecte_aquitaine(call)

def handle_login_qrcode(call):
    msg = bot.edit_message_text(
        message_id=call.message.id,
        chat_id=call.message.chat.id,
        text=languages[get_user_lang(call.message.chat.id)]["send_qrcode"]
    )
    bot.register_next_step_handler(msg, process_login_qrcode)

def process_login_qrcode(message):
    if message.content_type != "photo" or not message.photo:
        bot.reply_to(message, languages[get_user_lang(message.chat.id)]["please_send_photo"])
        return
    photo_file_id = message.photo[-1].file_id
    photo_file_info = bot.get_file(photo_file_id)
    downloaded_photo_file = bot.download_file(photo_file_info.file_path)

    image_stream = io.BytesIO(downloaded_photo_file)
    img = Image.open(image_stream)
    decoded_objects = decode(img)

    try:
        qrcode_data = json.loads(decoded_objects[0].data.decode("utf-8"))
    except Exception as e:
        print(languages[get_user_lang(message.chat.id)]["qrcode_decode_error"])
        bot.reply_to(message, languages[get_user_lang(message.chat.id)]["qrcode_decode_error"])
        return

    msg = bot.reply_to(message, languages[get_user_lang(message.chat.id)]["send_pin"])
    bot.register_next_step_handler(msg, process_login_qrcode_pin_handler, qrcode_data)

def process_login_qrcode_pin_handler(message, qrcode_data):
    pin = message.text
    if len(pin) != 4 or not pin.isdigit():
        bot.reply_to(message, languages[get_user_lang(message.chat.id)]["please_send_4_digits"])
        return
    
    try:
        client = pronotepy.Client.qrcode_login(qrcode_data, pin, str(uuid4()))
    except Exception as e:
        bot.reply_to(message, languages[get_user_lang(message.chat.id)]["login_failed"])
        print(languages[get_user_lang(message.chat.id)]["login_failed"])
        return
    
    if client.logged_in:
        credentials = {
            "login_method": "qrcode",
            "client": client,
            "url": client.pronote_url,
            "username": client.username,
            "password": client.password,
            "uuid": client.uuid,
        }
        clients[message.chat.id] = credentials
        bot.send_message(message.chat.id, languages[get_user_lang(message.chat.id)]["login_successful"])
    else:
        bot.send_message(message.chat.id, languages[get_user_lang(message.chat.id)]["login_failed"])

def handle_login_pronote(call):
    msg = bot.edit_message_text(
        message_id=call.message.id,
        chat_id=call.message.chat.id,
        text=languages[get_user_lang(call.message.chat.id)]["send_pronote_credentials"]
    )
    bot.register_next_step_handler(msg, process_login_pronote)

def process_login_pronote(message):
    try:
        url, username, password = message.text.split(',')
        client = pronotepy.Client(url.strip(), username.strip(), password.strip())

        if client.logged_in:
            credentials = {
                "login_method": "credentials",
                "client": client,
                "url": client.pronote_url,
                "username": client.username,
                "password": client.password,
                "uuid": client.uuid,
            }
            clients[message.chat.id] = credentials
            bot.send_message(message.chat.id, languages[get_user_lang(message.chat.id)]["login_successful"])
        else:
            bot.send_message(message.chat.id, languages[get_user_lang(message.chat.id)]["login_failed"])
    except Exception as e:
        bot.send_message(message.chat.id, languages[get_user_lang(message.chat.id)]["error_logging_in"])
        print(e)

def handle_login_lyceeconnecte_aquitaine(call):
    msg = bot.edit_message_text(
        message_id=call.message.id,
        chat_id=call.message.chat.id,
        text=languages[get_user_lang(call.message.chat.id)]["send_lyceeconnecte_credentials"]
    )
    bot.register_next_step_handler(msg, process_login_lyceeconnecte_aquitaine)

def process_login_lyceeconnecte_aquitaine(message):
    try:
        url, username, password = message.text.split(',')
        client = pronotepy.Client(
            pronote_url=url.strip(),
            username=username.strip(),
            password=password.strip(),
            ent=lyceeconnecte_aquitaine
        )
        client.username = username
        client.password = password

        if client.logged_in:
            credentials = {
                "login_method": "lyceeconnecte",
                "client": client,
                "url": client.pronote_url,
                "username": client.username,
                "password": client.password,
                "uuid": client.uuid,
            }
            clients[message.chat.id] = credentials
            bot.send_message(message.chat.id, languages[get_user_lang(message.chat.id)]["login_successful"])
        else:
            bot.send_message(message.chat.id, languages[get_user_lang(message.chat.id)]["login_failed"])
    except Exception as e:
        bot.send_message(message.chat.id, languages[get_user_lang(message.chat.id)]["error_logging_in"])
        print(e)

@bot.message_handler(commands=['grades'])
def get_grades(message):
    client_credentials = clients.get(message.chat.id)
    if client_credentials:
        client = client_credentials['client']
        grades = client.current_period.grades

        if not grades:
            bot.send_message(message.chat.id, languages[get_user_lang(message.chat.id)]["no_grades"])
            return

        grades_message = languages[get_user_lang(message.chat.id)]["grades_header"].format(period=client.current_period.name)
        for grade in grades:
            grades_message += languages[get_user_lang(message.chat.id)]["grade_entry"].format(
                subject=grade.subject.name,
                grade=grade.grade,
                out_of=grade.out_of,
                date=grade.date.strftime('%d/%m/%Y'),
                comment=grade.comment if grade.comment else languages[get_user_lang(message.chat.id)]["no_comment"]
            )
                
        bot.send_message(message.chat.id, grades_message)
    else:
        bot.send_message(message.chat.id, languages[get_user_lang(message.chat.id)]["not_logged_in"])

@bot.message_handler(commands=['homework'])
def get_homework(message):
    client_credentials = clients.get(message.chat.id)
    if client_credentials:
        client = client_credentials['client']
        homework = client.homework(datetime.datetime.now())

        if not homework:
            bot.send_message(message.chat.id, languages[get_user_lang(message.chat.id)]["no_homework"])
            return

        homework_message = languages[get_user_lang(message.chat.id)]["homework_header"]
        for hw in homework:
            homework_message += languages[get_user_lang(message.chat.id)]["homework_entry"].format(
                subject=hw.subject.name,
                description=hw.description,
                due_date=hw.due_date.strftime('%d/%m/%Y'),
                done=languages[get_user_lang(message.chat.id)]["done"] if hw.done else languages[get_user_lang(message.chat.id)]["not_done"]
            )
        
        bot.send_message(message.chat.id, homework_message)
    else:
        bot.send_message(message.chat.id, languages[get_user_lang(message.chat.id)]["not_logged_in"])

@bot.message_handler(commands=['timetable'])
def get_timetable(message):
    client_credentials = clients.get(message.chat.id)
    if client_credentials:
        client = client_credentials['client']
        timetable = client.timetable(datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(days=7))

        if not timetable:
            bot.send_message(message.chat.id, languages[get_user_lang(message.chat.id)]["no_timetable"])
            return

        timetable_message = languages[get_user_lang(message.chat.id)]["timetable_header"]
        for lesson in timetable:
            timetable_message += languages[get_user_lang(message.chat.id)]["timetable_entry"].format(
                subject=lesson.subject.name,
                teacher=lesson.teacher_name,
                start_time=lesson.start.strftime('%d/%m/%Y %H:%M'),
                end_time=lesson.end.strftime('%H:%M'),
                room=lesson.room if lesson.room else languages[get_user_lang(message.chat.id)]["no_room"]
            )

        bot.send_message(message.chat.id, timetable_message)
    else:
        bot.send_message(message.chat.id, languages[get_user_lang(message.chat.id)]["not_logged_in"])

def logout_credentials(user_id):
    client_credentials = clients.get(user_id)
    if client_credentials:
        del client_credentials[user_id]
        return True
    return False

@bot.message_handler(commands=['logout'])
def logout(message):
    if logout_credentials(message.chat.id):
        bot.send_message(message.chat.id, languages[get_user_lang(message.chat.id)]["logout_successful"])
    else:
        bot.send_message(message.chat.id, languages[get_user_lang(message.chat.id)]["not_logged_in"])

if __name__ == '__main__':
    bot.infinity_polling()