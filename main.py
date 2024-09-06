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

db=Client("db.sqlite")

clients={}

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def get_session(user_id):
	user_sessions=db.get("user_sessions") or {}
	return user_sessions.get(user_id)

def set_session(user_id, client):
	user_sessions=db.get("user_sessions") or {}
	user_sessions[user_id]=client
	db.set("user_sessions", user_sessions)

def delete_session(user_id):
	user_sessions=db.get("user_sessions") or {}
	if user_id in user_sessions:
		del user_sessions[user_id]
		db.set("user_sessions", user_sessions)
		return True
	return False

# Command to start the bot
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id, 
        "Welcome to the Pronote Bot! Please use /login to connect to your Pronote account."
    )

# Command to login
@bot.message_handler(commands=['login'])
def login(message):
    client=get_session(message.chat.id)
    if client:
        bot.reply_to(message, f"You are already logged in as {client.username}\nSend /logout if you want to change the account.")
        return
    available_login_methods_keyboard=InlineKeyboardMarkup()
    qrcode_button=InlineKeyboardButton(text="QR Code (Recommended)", callback_data="login_qrcode")
    pronote_button=InlineKeyboardButton(text="Pronote", callback_data="login_pronote")
    lyceeconnecte_aquitaine_button=InlineKeyboardButton(text="Lycée Connecté (Local)", callback_data="login_lyceeconnecte_aquitaine")
    available_login_methods_keyboard.row(qrcode_button)
    available_login_methods_keyboard.row(pronote_button)
    available_login_methods_keyboard.row(lyceeconnecte_aquitaine_button)
    bot.send_message(
        message.chat.id, 
        "Please select your login method from the buttons below :",
        reply_markup=available_login_methods_keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("login_"))
def handle_login_method(call):
    if call.data=="login_qrcode":
        handle_login_qrcode(call)
    elif call.data=="login_pronote":
        handle_login_pronote(call)
    elif call.data=="login_lyceeconnecte_aquitaine":
        handle_login_lyceeconnecte_aquitaine(call)

def handle_login_qrcode(call):
    msg=bot.edit_message_text(
        message_id=call.message.id,
        chat_id=call.message.chat.id,
        text="Please send your QR Code image provided by the pronote desktop website:\nNote : you can screenshot the QR code and send it."
    )
    bot.register_next_step_handler(msg, process_login_qrcode)

def process_login_qrcode(message):
    if message.content_type!="photo" or not message.photo:
        bot.reply_to(message, "Please send photo.")
        return
    photo_file_id = message.photo[-1].file_id
    photo_file_info = bot.get_file(photo_file_id)
    downloaded_photo_file = bot.download_file(photo_file_info.file_path)

    image_stream = io.BytesIO(downloaded_photo_file)
    img = Image.open(image_stream)
    decoded_objects = decode(img)

    try:
        qrcode_data=json.loads(decoded_objects[0].data.decode("utf-8"))
    except Exception as e:
        print("Can not decode QR code, make sure the QR code is entirly visible in the photo.")
        bot.reply_to(message, "Can not decode QR code, make sure the QR code is entirly visible in the photo.")
        return

    msg=bot.reply_to(message, "Send your 4-digits PIN:")
    bot.register_next_step_handler(msg, process_login_qrcode_pin_handler, qrcode_data)

def process_login_qrcode_pin_handler(message, qrcode_data):
    pin=message.text
    if len(pin)!=4 or not pin.isdigit():
        bot.reply_to(message, "Please send only 4-digits PIN.")
        return
    
    try:
        client=pronotepy.Client.qrcode_login(qrcode_data, pin, str(uuid4()))
    except Exception as e:
        bot.reply_to(message, "Can not login with QR code, make sure the QR code and the PIN are valid.")
        print("Can not login with QR code, make sure the QR code and the PIN are valid.")
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
        clients[message.chat.id]=credentials
        bot.send_message(message.chat.id, "Login successful! Use /grades, /homework, or /timetable to access your data.")
    else:
        bot.send_message(message.chat.id, "Login failed. Please check your credentials and try again.")
    

def handle_login_pronote(call):
    msg=bot.edit_message_text(
        message_id=call.message.id,
        chat_id=call.message.chat.id,
        text="Please enter your Pronote URL, username, and password separated by commas \n(e.g., url,username,password):"
    )
    bot.register_next_step_handler(msg, process_login_pronote)

def process_login_pronote(message):
    try:
        url, username, password = message.text.split(',')
        client = pronotepy.Client(url.strip(), username.strip(), password.strip())

        if client.logged_in:
            credentials = {
                "login_method": "qrcode",
                "client": client,
                "url": client.pronote_url,
                "username": client.username,
                "password": client.password,
                "uuid": client.uuid,
            }
            clients[message.chat.id]=credentials
            bot.send_message(message.chat.id, "Login successful! Use /grades, /homework, or /timetable to access your data.")
        else:
            bot.send_message(message.chat.id, "Login failed. Please check your credentials and try again.")
    except Exception as e:
        bot.send_message(message.chat.id, "There was an error logging in. Please try again.")
        print(e)

def handle_login_lyceeconnecte_aquitaine(call):
    msg=bot.edit_message_text(
        message_id=call.message.id,
        chat_id=call.message.chat.id,
        text="Please enter your Pronote url and Lycée connecté (Local account) username, and password separated by commas \n(e.g., url,username,password):"
    )
    bot.register_next_step_handler(msg, process_login_lyceeconnecte_aquitaine)

def process_login_lyceeconnecte_aquitaine(message):
    try:
        url, username, password = message.text.split(',')
        client = pronotepy.Client(
            pronote_url=url,
            username=username.strip(),
            password=password.strip(),
            ent=lyceeconnecte_aquitaine
        )
        client.username=username
        client.password=password

        if client.logged_in:
            credentials = {
                "login_method": "qrcode",
                "client": client,
                "url": client.pronote_url,
                "username": client.username,
                "password": client.password,
                "uuid": client.uuid,
            }
            clients[message.chat.id]=credentials
            bot.send_message(message.chat.id, "Login successful! Use /grades, /homework, or /timetable to access your data.")
        else:
            bot.send_message(message.chat.id, "Login failed. Please check your credentials and try again.")
    except Exception as e:
        bot.send_message(message.chat.id, "There was an error logging in. Please try again.")
        print(e)


# Command to get grades
@bot.message_handler(commands=['grades'])
def get_grades(message):
    client_credentials = clients.get(message.chat.id)
    if client_credentials:
        client=client_credentials["client"]
        client.session_check()
        grades = client.current_period.grades
        response = "Your Grades:\n" + "\n".join([f"{grade.grade}: {grade.subject.name}" for grade in grades])
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "You are not logged in. Please use /login first.")

# Command to get homework
@bot.message_handler(commands=['homework'])
def get_homework(message):
    client_credentials = clients.get(message.chat.id)
    if client_credentials:
        client=client_credentials["client"]
        client.session_check()
        homeworks = client.homework(
            date_from=client.start_day,
            #date_to=client.start_day+datetime.timedelta(days=22)
        )
        response = "Your Homework:\n\n" + "\n\n".join([f"Pour le : {hw.date}\n*{hw.subject.name}*: {hw.description}" for hw in homeworks])
        bot.send_message(message.chat.id, response, parse_mode="MarkDown")
    else:
        bot.send_message(message.chat.id, "You are not logged in. Please use /login first.")

# Command to get timetable
@bot.message_handler(commands=['timetable'])
def get_timetable(message):
    client_credentials = clients.get(message.chat.id)
    if client_credentials:
        client=client_credentials["client"]
        client.session_check()
        timetable = client.lessons(client.start_day + datetime.timedelta(days=4))

        response = "Your Timetable:\n" + "\n".join([f"{lesson.start.strftime('%A %d %B %Y %H:%M')}: {lesson.subject.name}" for lesson in timetable])
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "You are not logged in. Please use /login first.")

# Command to logout
@bot.message_handler(commands=['logout'])
def logout(message):
    deleted=delete_session(message.chat.id)
    if deleted:
        bot.send_message(message.chat.id, "You have been logged out.")
    else:
        bot.send_message(message.chat.id, "You are not logged in.")


if __name__ == '__main__':
    # Start polling
    bot.infinity_polling()