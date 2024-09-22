import os
import datetime
import pytz
from tgram import TgBot, filters
from tgram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from babel.dates import format_date
from bot_instance import bot
from collections import defaultdict
from modules.auth import handle_login_lyceeconnecte_aquitaine, handle_login_pronote, handle_login_qrcode, logout_credentials
from modules.database import get_user_lang, set_user_lang, clients, get_user_lesson, set_user_lesson
from modules.language import setup_user_lang, languages
from dotenv import load_dotenv
from modules.settings import settings_message
from modules.language import change_user_lang
from modules.notifications import enable_notifications, disable_notifications

load_dotenv()
timezone = pytz.timezone(os.getenv('TIMEZONE') or "UTC")

@bot.on_callback_query(filters.private & filters.regex(r"^set\_lang\_"))
async def setup_user_lang_query_handler(bot: TgBot, call: CallbackQuery):
    lang = call.data.split("set_lang_")[1]
    await set_user_lang(call.from_user.id, lang)
    user_lang=await get_user_lang(call.from_user.id)
    await call.edit_message_text(languages[user_lang]["language_set"])

@bot.on_message(filters.private & filters.command("start"))
async def start(bot: TgBot, message: Message):
    try:
        clients[message.chat.id]
    except KeyError:
        clients[message.chat.id]={}
    if not await setup_user_lang(message.chat.id):
        return
    user_lang=await get_user_lang(message.chat.id)
    await bot.send_message(
        message.chat.id, 
        languages[user_lang]["welcome"]
    )

async def create_login_methods_keyboard(user_lang):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=languages[user_lang]["qrcode_login"],
                    callback_data="login_qrcode"
                )
            ],
            [
                InlineKeyboardButton(
                    text=languages[user_lang]["pronote_login"],
                    callback_data="login_pronote"
                )
            ],
            [
                InlineKeyboardButton(
                    text=languages[user_lang]["lycee_connecte_local"],
                    callback_data="login_lyceeconnecte_aquitaine"
                )
            ]
        ]
    )

@bot.on_message(filters.private & filters.command("login"))
async def login(bot: TgBot, message: Message):
    user_lang=await get_user_lang(message.chat.id)
    client_credentials = clients.get(message.chat.id)
    if client_credentials:
        client=client_credentials["client"]
        return await message.reply_text(languages[user_lang]["already_logged_in"].format(username=client.username))

    await message.reply_text(
        languages[user_lang]["select_login_method"],
        reply_markup=await create_login_methods_keyboard(user_lang)
    )

@bot.on_callback_query(filters.private & filters.regex(r"^login\_"))
async def handle_login_method(_, call: CallbackQuery):
    handlers={
        "login_qrcode": handle_login_qrcode,
        "login_pronote": handle_login_pronote,
        "login_lyceeconnecte_aquitaine": handle_login_lyceeconnecte_aquitaine
    }
    await handlers.get(call.data)(call)

@bot.on_message(filters.private & filters.command("grades"))
async def get_grades(bot: TgBot, message: Message):
    user_lang=await get_user_lang(message.chat.id)
    client_credentials = clients.get(message.chat.id)
    if client_credentials:
        client = client_credentials['client']
        client.session_check()
        grades = client.current_period.grades

        if not grades:
            await bot.send_message(message.chat.id, languages[user_lang]["no_grades"])
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
                
        await bot.send_message(message.chat.id, grades_message)
    else:
        await bot.send_message(message.chat.id, languages[user_lang]["not_logged_in"])

@bot.on_message(filters.private & filters.command("homework"))
async def get_homework(bot: TgBot, message: Message):
    user_lang=await get_user_lang(message.chat.id)
    client_credentials = clients.get(message.chat.id)
    if client_credentials:
        client = client_credentials['client']
        client.session_check()
        today=datetime.datetime.now(timezone).date()
        homeworks = client.homework(today)
        homeworks.sort(key=lambda homework: homework.date)

        if not homeworks:
            await bot.send_message(message.chat.id, languages[user_lang]["no_homework"])
            return
        
        user_locale = languages[user_lang]["locale"]

        # group homeworks list into sublists of homeworks for each day.
        grouped_data = defaultdict(list)
        for homework in homeworks:
            grouped_data[homework.date].append(homework)
        grouped_homeworks = list(grouped_data.values())


        homework_message = languages[user_lang]["homework_header"]
        for homeworks in grouped_homeworks:
            homework_message += languages[user_lang]["homework_for"].format(date=format_date(homeworks[0].date, format="EEEE d MMMM", locale=user_locale))

            for homework in homeworks:
                homework_message += languages[user_lang]["homework_entry"].format(
                    subject=homework.subject.name,
                    description=homework.description,
                    done=languages[user_lang]["done"] if homework.done else languages[user_lang]["not_done"]
                )
        
        await bot.send_message(message.chat.id, homework_message)
    else:
        await bot.send_message(message.chat.id, languages[user_lang]["not_logged_in"])

@bot.on_message(filters.private & filters.command("timetable"))
async def get_timetable(bot: TgBot, message: Message):
    user_lang=await get_user_lang(message.chat.id)
    client_credentials = clients.get(message.chat.id)
    if client_credentials:
        client = client_credentials['client']
        client.session_check()
        
        timetable=await get_today_timetable(client)
        if not timetable or timezone.localize(timetable[-1].end)<datetime.datetime.now(timezone): # if timetable is empty or the last lesson of the day is alreay passed
            timetable=await get_next_day_timetable(client)

        if not timetable:
            await bot.send_message(message.chat.id, languages[user_lang]["no_timetable"])
            return

        user_locale = languages[user_lang]["locale"]

        timetable_message = languages[user_lang]["timetable_header"].format(date=format_date(timetable[0].start, format="EEEE d MMMM", locale=user_locale))
        
        for lesson in timetable:
            await set_user_lesson(user_id=message.chat.id, lesson=lesson)
        timetable_keyboard=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"{"🚫 " if lesson.canceled else ""}{lesson.subject.name} - {lesson.start.strftime('%H:%M')} - {lesson.classroom if lesson.classroom else lesson.end.strftime('%H:%M')}",
                        callback_data="lesson_"+str(lesson.id)
                    ) 
                ] for lesson in timetable
            ]
        )
        await bot.send_message(message.chat.id, timetable_message, reply_markup=timetable_keyboard)
    else:
        await bot.send_message(message.chat.id, languages[user_lang]["not_logged_in"])

async def get_today_timetable(client):
    days=1
    for i in range(10):
        timetable = client.lessons(datetime.datetime.now(timezone), datetime.datetime.now(timezone) + datetime.timedelta(days=days))
        if not timetable:
            days+=1
            continue
        break
    timetable.sort(key=lambda lesson: lesson.start)
    return timetable

async def get_next_day_timetable(client):
    days=1
    for i in range(10):
        timetable = client.lessons(datetime.datetime.now(timezone)+datetime.timedelta(days=days), datetime.datetime.now(timezone) + datetime.timedelta(days=days+1))
        if not timetable:
            days+=1
            continue
        break
    timetable.sort(key=lambda lesson: lesson.start)
    return timetable

@bot.on_message(filters.private & filters.command("enable_notifications"))
async def enable_notifications_command(_, message: Message):
    await enable_notifications(message)

@bot.on_message(filters.private & filters.command("disable_notifications"))
async def disable_notifications_command(_, message: Message):
    await disable_notifications(message)

@bot.on_callback_query(filters.private & filters.regex(r"^lesson\_"))
async def lesson_button_handler(bot: TgBot, call: CallbackQuery):
    user_lang=await get_user_lang(call.message.chat.id)
    lesson_id=call.data.split("lesson_")[1]
    lesson=await get_user_lesson(user_id=call.from_user.id, lesson_id=lesson_id)
    text=languages[user_lang]["timetable_entry"].format(
        subject=lesson.subject.name,
        teacher=lesson.teacher_name,
        start_time=lesson.start.strftime('%H:%M'),
        end_time=lesson.end.strftime('%H:%M'),
        room=lesson.classroom if lesson.classroom else languages[user_lang]["no_room"]
    )
    await call.answer(text=text, show_alert=True)

@bot.on_message(filters.private & filters.command("settings"))
async def settings_command(_, message: Message):
    await settings_message(message)

@bot.on_callback_query(filters.private & filters.regex(r"^settings\_"))
async def setting_callback_handler(_, call:CallbackQuery):
    setting=call.data.split("settings_")[1]
    if setting=="set_language":
        await change_user_lang(call.message)

@bot.on_message(filters.private & filters.command("logout"))
async def logout(bot: TgBot, message: Message):
    chat_id=message.chat.id
    user_lang=await get_user_lang(chat_id)
    if await logout_credentials(chat_id):
        await bot.send_message(chat_id, languages[user_lang]["logout_successful"])
    else:
        await bot.send_message(chat_id, languages[user_lang]["not_logged_in"])

@bot.on_message(filters.private & filters.command("privacy_policy"))
async def privacy_policy(bot: TgBot, message: Message):
    pp_file=open("PRIVACY_POLICY.md", "r").read()
    await message.reply_text(text=pp_file, parse_mode="MarkDown")

