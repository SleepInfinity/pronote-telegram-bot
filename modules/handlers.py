import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import locale
from bot_instance import bot
from modules.auth import handle_login_lyceeconnecte_aquitaine, handle_login_pronote, handle_login_qrcode, logout_credentials
from modules.database import get_user_lang, set_user_lang, clients
from modules.language import setup_user_lang, languages

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_lang_"))
def setup_user_lang_query_handler(call):
    lang = call.data.split("set_lang_")[1]
    set_user_lang(call.message.chat.id, lang)
    user_lang=get_user_lang(call.message.chat.id)
    bot.edit_message_text(
        message_id=call.message.id, 
        chat_id=call.message.chat.id, 
        text=languages[user_lang]["language_set"]
    )

@bot.message_handler(commands=['start'])
def start(message):
    if not setup_user_lang(message.chat.id):
        return
    user_lang=get_user_lang(message.chat.id)
    bot.send_message(
        message.chat.id, 
        languages[user_lang]["welcome"]
    )

@bot.message_handler(commands=['login'])
def login(message):
    user_lang=get_user_lang(message.chat.id)
    client_credentials = clients.get(message.chat.id)
    if client_credentials:
        client=client_credentials["client"]
        bot.reply_to(message, languages[user_lang]["already_logged_in"].format(username=client.username))
        return
    available_login_methods_keyboard = InlineKeyboardMarkup()
    qrcode_button = InlineKeyboardButton(text=languages[user_lang]["qrcode_login"], callback_data="login_qrcode")
    pronote_button = InlineKeyboardButton(text=languages[user_lang]["pronote_login"], callback_data="login_pronote")
    lyceeconnecte_aquitaine_button = InlineKeyboardButton(text=languages[user_lang]["lycee_connecte_local"], callback_data="login_lyceeconnecte_aquitaine")
    available_login_methods_keyboard.row(qrcode_button)
    available_login_methods_keyboard.row(pronote_button)
    available_login_methods_keyboard.row(lyceeconnecte_aquitaine_button)
    bot.send_message(
        message.chat.id, 
        languages[user_lang]["select_login_method"],
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

@bot.message_handler(commands=['grades'])
def get_grades(message):
    user_lang=get_user_lang(message.chat.id)
    client_credentials = clients.get(message.chat.id)
    if client_credentials:
        client = client_credentials['client']
        grades = client.current_period.grades

        if not grades:
            bot.send_message(message.chat.id, languages[user_lang]["no_grades"])
            return

        grades_message = languages[user_lang]["grades_header"].format(period=client.current_period.name)
        for grade in grades:
            grades_message += languages[user_lang]["grade_entry"].format(
                subject=grade.subject.name,
                grade=grade.grade,
                out_of=grade.out_of,
                date=grade.date.strftime('%d/%m/%Y'),
                comment=grade.comment if grade.comment else languages[user_lang]["no_comment"]
            )
                
        bot.send_message(message.chat.id, grades_message)
    else:
        bot.send_message(message.chat.id, languages[user_lang]["not_logged_in"])

@bot.message_handler(commands=['homework'])
def get_homework(message):
    user_lang=get_user_lang(message.chat.id)
    client_credentials = clients.get(message.chat.id)
    if client_credentials:
        client = client_credentials['client']
        today=datetime.datetime.now().date()
        homework = client.homework(today)

        if not homework:
            bot.send_message(message.chat.id, languages[user_lang]["no_homework"])
            return

        homework_message = languages[user_lang]["homework_header"]
        for hw in homework:
            homework_message += languages[user_lang]["homework_entry"].format(
                subject=hw.subject.name,
                description=hw.description,
                due_date=hw.date.strftime('%d/%m/%Y'),
                done=languages[user_lang]["done"] if hw.done else languages[user_lang]["not_done"]
            )
        
        bot.send_message(message.chat.id, homework_message)
    else:
        bot.send_message(message.chat.id, languages[user_lang]["not_logged_in"])

@bot.message_handler(commands=['timetable'])
def get_timetable(message):
    user_lang=get_user_lang(message.chat.id)
    client_credentials = clients.get(message.chat.id)
    if client_credentials:
        client = client_credentials['client']
        days=1
        for i in range(10):
            timetable = client.lessons(datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(days=days))
            if not timetable:
                days+=1
                continue
            break

        if not timetable:
            bot.send_message(message.chat.id, languages[user_lang]["no_timetable"])
            return

        user_locale = languages[user_lang]["locale"]
        locale.setlocale(locale.LC_TIME, user_locale)

        timetable_message = languages[user_lang]["timetable_header"].format(date=timetable[0].start.strftime('%A %d %B'))
        for lesson in timetable:
            timetable_message += languages[user_lang]["timetable_entry"].format(
                subject=lesson.subject.name,
                teacher=lesson.teacher_name,
                start_time=lesson.start.strftime('%H:%M'),
                end_time=lesson.end.strftime('%H:%M'),
                room=lesson.classroom if lesson.classroom else languages[user_lang]["no_room"]
            )

        bot.send_message(message.chat.id, timetable_message)
    else:
        bot.send_message(message.chat.id, languages[user_lang]["not_logged_in"])

@bot.message_handler(commands=['logout'])
def logout(message):
    user_lang=get_user_lang(message.chat.id)
    if logout_credentials(message.chat.id):
        bot.send_message(message.chat.id, languages[user_lang]["logout_successful"])
    else:
        bot.send_message(message.chat.id, languages[user_lang]["not_logged_in"])