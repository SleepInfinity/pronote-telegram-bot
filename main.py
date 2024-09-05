import os
import telebot
import pronotepy
import datetime
import requests
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
    pronote_button=InlineKeyboardButton(text="Pronote", callback_data="login_pronote")
    lyceeconnecte_aquitaine_button=InlineKeyboardButton(text="Lycée Connecté (Local)", callback_data="login_lyceeconnecte_aquitaine")
    available_login_methods_keyboard.row(pronote_button)
    available_login_methods_keyboard.row(lyceeconnecte_aquitaine_button)
    bot.send_message(
        message.chat.id, 
        "Please select your login method from the buttons below :",
        reply_markup=available_login_methods_keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("login_"))
def handle_login_method(call):
	if call.data=="login_pronote":
		handle_login_pronote(call)
	elif call.data=="login_lyceeconnecte_aquitaine":
		handle_login_lyceeconnecte_aquitaine(call)

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
        #client.session_check()

        if client.logged_in:
            set_session(message.chat.id, client)
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
        print(client.username)
        print(client.password)
        #client.session_check()

        if client.logged_in:
            set_session(message.chat.id, client)
            #clients[message.chat.id]=client
            bot.send_message(message.chat.id, "Login successful! Use /grades, /homework, or /timetable to access your data.")
        else:
            bot.send_message(message.chat.id, "Login failed. Please check your credentials and try again.")
    except Exception as e:
        bot.send_message(message.chat.id, "There was an error logging in. Please try again.")
        print(e)


# Command to get grades
@bot.message_handler(commands=['grades'])
def get_grades(message):
    client = get_session(message.chat.id)
    #client=clients[message.chat.id]
    if client:
        #client.session_check()
        grades = client.current_period.grades
        response = "Your Grades:\n" + "\n".join([f"{grade.grade}: {grade.subject.name}" for grade in grades])
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "You are not logged in. Please use /login first.")

# Command to get homework
@bot.message_handler(commands=['homework'])
def get_homework(message):
    client = get_session(message.chat.id)
    if client:
        #client.session_check()
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
    client = get_session(message.chat.id)
    if client:
        #client.session_check()
        #timetable = client.timetable()
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