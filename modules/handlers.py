import datetime
from typing import List
from tgram import TgBot, filters
from tgram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from babel.dates import format_date
from bot_instance import bot
from collections import defaultdict
from modules.auth import (
    handle_login_lyceeconnecte_aquitaine,
    handle_login_pronote,
    handle_login_qrcode,
    logout_credentials,
)
from modules.database import (
    get_user_lang,
    set_user_lang,
    clients,
    get_user_lesson,
    set_user_lesson,
)
from modules.language import setup_user_lang, languages
from pronotepy import Client, Grade, Homework, Lesson
from modules.settings import settings_message
from modules.language import change_user_lang
from modules.notifications import enable_notifications, disable_notifications
from modules.broadcast import get_broadcast_message
from ai.handlers import prompt_handler, clear_chat_handler
from utils.message import is_media, escape_special_chars
from modules.language import TIMEZONE


@bot.on_callback_query(filters.private & filters.regex(r"^set\_lang\_"))
async def setup_user_lang_query_handler(bot: TgBot, call: CallbackQuery) -> None:
    lang: str = call.data.split("set_lang_")[1]
    await set_user_lang(call.from_user.id, lang)
    await call.edit_message_text(languages[lang]["language_set"])


@bot.on_message(filters.private & filters.command("start"))
async def start(bot: TgBot, message: Message) -> None:
    try:
        clients[message.chat.id]
    except KeyError:
        clients[message.chat.id] = {}
    if not await setup_user_lang(message.chat.id):
        return
    user_lang: str = await get_user_lang(message.chat.id)
    await bot.send_message(message.chat.id, languages[user_lang]["welcome"])


async def create_login_methods_keyboard(user_lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=languages[user_lang]["qrcode_login"],
                    callback_data="login_qrcode",
                )
            ],
            [
                InlineKeyboardButton(
                    text=languages[user_lang]["pronote_login"],
                    callback_data="login_pronote",
                )
            ],
            [
                InlineKeyboardButton(
                    text=languages[user_lang]["lycee_connecte_local"],
                    callback_data="login_lyceeconnecte_aquitaine",
                )
            ],
        ]
    )


@bot.on_message(filters.private & filters.command("login"))
async def login(bot: TgBot, message: Message) -> None:
    user_lang: str = await get_user_lang(message.chat.id)
    client_credentials: dict | None = clients.get(message.chat.id)
    if client_credentials:
        client: Client = client_credentials["client"]
        return await message.reply_text(
            languages[user_lang]["already_logged_in"].format(username=client.username)
        )

    await message.reply_text(
        languages[user_lang]["select_login_method"],
        reply_markup=await create_login_methods_keyboard(user_lang),
    )


@bot.on_callback_query(filters.private & filters.regex(r"^login\_"))
async def handle_login_method(_, call: CallbackQuery) -> None:
    handlers: dict = {
        "login_qrcode": handle_login_qrcode,
        "login_pronote": handle_login_pronote,
        "login_lyceeconnecte_aquitaine": handle_login_lyceeconnecte_aquitaine,
    }
    await handlers[call.data](call)


@bot.on_message(filters.private & filters.command("grades"))
async def get_grades(bot: TgBot, message: Message) -> None:
    user_lang: str = await get_user_lang(message.chat.id)
    client_credentials: dict | None = clients.get(message.chat.id)
    if client_credentials:
        client: Client = client_credentials["client"]
        client.session_check()
        grades: List[Grade] = client.current_period.grades

        if not grades:
            return await bot.send_message(
                message.chat.id, languages[user_lang]["no_grades"]
            )

        grades_message: str = languages[user_lang]["grades_header"].format(
            period=client.current_period.name
        )
        for grade in grades:
            grades_message += languages[user_lang]["grade_entry"].format(
                subject=grade.subject.name,
                grade=grade.grade,
                out_of=grade.out_of,
                coefficient=grade.coefficient,
                date=grade.date.strftime("%d/%m/%Y"),
                comment=grade.comment
                if grade.comment
                else languages[user_lang]["no_comment"],
            )

        await bot.send_message(
            message.chat.id,
            escape_special_chars(grades_message, excluded_chars=[">", "*"]),
            parse_mode="MarkdownV2",
        )
    else:
        await bot.send_message(message.chat.id, languages[user_lang]["not_logged_in"])


@bot.on_message(filters.private & filters.command("homework"))
async def get_homework(bot: TgBot, message: Message) -> None:
    user_lang: str = await get_user_lang(message.chat.id)
    client_credentials: dict | None = clients.get(message.chat.id)
    if client_credentials:
        client: Client = client_credentials["client"]
        client.session_check()
        today: datetime._Date = datetime.datetime.now(TIMEZONE).date()
        homeworks: List[Homework] = client.homework(today)
        homeworks.sort(key=lambda homework: homework.date)

        if not homeworks:
            return await bot.send_message(
                message.chat.id, languages[user_lang]["no_homework"]
            )

        user_locale: str = languages[user_lang]["locale"]

        # group homeworks list into sublists of homeworks for each day.
        grouped_data = defaultdict(list)
        for homework in homeworks:
            grouped_data[homework.date].append(homework)
        grouped_homeworks: List[List[Homework]] = list(grouped_data.values())

        del homeworks

        homework_message: str = languages[user_lang]["homework_header"]
        for homeworks in grouped_homeworks:
            homework_message += languages[user_lang]["homework_for"].format(
                date=format_date(
                    homeworks[0].date, format="EEEE d MMMM", locale=user_locale
                )
            )

            for homework in homeworks:
                homework_message += languages[user_lang]["homework_entry"].format(
                    subject=homework.subject.name,
                    description=homework.description,
                    done=languages[user_lang]["done"]
                    if homework.done
                    else languages[user_lang]["not_done"],
                )

        await bot.send_message(
            message.chat.id,
            escape_special_chars(homework_message, excluded_chars=["*"]),
            parse_mode="MarkdownV2",
        )
    else:
        await bot.send_message(message.chat.id, languages[user_lang]["not_logged_in"])


@bot.on_message(filters.private & filters.command("timetable"))
async def get_timetable(bot: TgBot, message: Message) -> None:
    user_lang: str = await get_user_lang(message.chat.id)
    client_credentials: dict = clients.get(message.chat.id)
    if client_credentials:
        client: Client = client_credentials["client"]
        client.session_check()

        timetable: List[Lesson] = await get_today_timetable(client)
        if not timetable or TIMEZONE.localize(
            timetable[-1].end
        ) < datetime.datetime.now(
            TIMEZONE
        ):  # if timetable is empty or the last lesson of the day is alreay passed
            timetable: List[Lesson] = await get_next_day_timetable(client)

        if not timetable:
            return await bot.send_message(
                message.chat.id, languages[user_lang]["no_timetable"]
            )

        user_locale: str = languages[user_lang]["locale"]

        timetable_message: str = languages[user_lang]["timetable_header"].format(
            date=format_date(
                timetable[0].start, format="EEEE d MMMM", locale=user_locale
            )
        )
        tags: List[str] = []
        timetable_buttons: List[List[InlineKeyboardButton]] = []
        for lesson in timetable:
            if (
                lesson.canceled and lesson.modified
            ):  # The lesson with the old classroom number.
                continue
            await set_user_lesson(user_id=message.chat.id, lesson=lesson)
            lesson_tags: List[str] = await get_lesson_tags(lesson)
            tags = list(
                set([*tags, *lesson_tags])
            )  # unpacking every tag in the tags list and removing duplicates.
            timetable_buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{' '.join(lesson_tags)} {lesson.subject.name} - {lesson.start.strftime('%H:%M')} - {lesson.classroom if lesson.classroom else lesson.end.strftime('%H:%M')}",
                        callback_data="lesson_" + str(lesson.id),
                    )
                ]
            )
        timetable_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(
            timetable_buttons
        )
        del timetable_buttons
        tag_hints: str = "\n".join(
            tag + " : " + languages[user_lang][tag] for tag in tags
        )
        timetable_message += tag_hints
        await bot.send_message(
            message.chat.id,
            timetable_message,
            reply_markup=timetable_keyboard,
        )
    else:
        await bot.send_message(message.chat.id, languages[user_lang]["not_logged_in"])


async def get_lesson_tags(lesson: Lesson) -> List[str]:
    tags: list = [
        (lesson.canceled, "🚫"),
        (lesson.modified, "🔄"),
        (lesson.exempted, "🆓"),
        (lesson.outing, "🏖️"),
        (lesson.detention, "🔒"),
        (lesson.test, "🧪"),
    ]

    return [value for key, value in tags if key]


async def get_today_timetable(client: Client) -> List[Lesson]:
    days: int = 1
    for _ in range(10):
        timetable: List[Lesson] = client.lessons(
            datetime.datetime.now(TIMEZONE),
            datetime.datetime.now(TIMEZONE) + datetime.timedelta(days=days),
        )
        if not timetable:
            days += 1
            continue
        break
    timetable.sort(key=lambda lesson: lesson.start)
    return timetable


async def get_next_day_timetable(client: Client) -> List[Lesson]:
    days: int = 1
    for _ in range(10):
        timetable = client.lessons(
            datetime.datetime.now(TIMEZONE) + datetime.timedelta(days=days),
            datetime.datetime.now(TIMEZONE) + datetime.timedelta(days=days + 1),
        )
        if not timetable:
            days += 1
            continue
        break
    timetable.sort(key=lambda lesson: lesson.start)
    return timetable


@bot.on_message(filters.private & filters.command("enable_notifications"))
async def enable_notifications_command(_, message: Message) -> None:
    await enable_notifications(message)


@bot.on_message(filters.private & filters.command("disable_notifications"))
async def disable_notifications_command(_, message: Message) -> None:
    await disable_notifications(message)


@bot.on_callback_query(filters.private & filters.regex(r"^lesson\_"))
async def lesson_button_handler(bot: TgBot, call: CallbackQuery) -> None:
    user_lang: str = await get_user_lang(call.message.chat.id)
    lesson_id: str = call.data.split("lesson_")[1]
    lesson: Lesson | None = await get_user_lesson(
        user_id=call.from_user.id, lesson_id=lesson_id
    )
    popup_text = languages[user_lang]["timetable_entry"].format(
        subject=lesson.subject.name,
        teacher=lesson.teacher_name,
        start_time=lesson.start.strftime("%H:%M"),
        end_time=lesson.end.strftime("%H:%M"),
        room=lesson.classroom if lesson.classroom else languages[user_lang]["no_room"],
    )
    await call.answer(text=popup_text, show_alert=True)


@bot.on_message(filters.private & filters.command("settings"))
async def settings_command(_, message: Message) -> None:
    await settings_message(message)


@bot.on_callback_query(filters.private & filters.regex(r"^settings\_"))
async def setting_callback_handler(_, call: CallbackQuery) -> None:
    setting: str = call.data.split("settings_")[1]

    setting_functions: dict = {
        "set_language": change_user_lang,
    }

    await setting_functions[setting](call.message)


@bot.on_message(filters.private & filters.command("broadcast"))
async def broadcast_handler(bot: TgBot, message: Message) -> None:
    await get_broadcast_message(bot, message)


@bot.on_message(filters.private & filters.command("logout"))
async def logout(bot: TgBot, message: Message) -> None:
    chat_id: int = message.chat.id
    user_lang: str = await get_user_lang(chat_id)
    if await logout_credentials(chat_id):
        await bot.send_message(chat_id, languages[user_lang]["logout_successful"])
    else:
        await bot.send_message(chat_id, languages[user_lang]["not_logged_in"])


@bot.on_message(filters.private & filters.command("privacy_policy"))
async def privacy_policy(bot: TgBot, message: Message) -> None:
    pp_file: str = open("PRIVACY_POLICY.md", "r").read()
    await message.reply_text(text=pp_file)


@bot.on_message(filters.private & filters.command("ai"))
async def ai_handler(bot: TgBot, message: Message) -> None:
    chat_id: int = message.chat.id
    user_lang: str = await get_user_lang(chat_id)

    if len(message.command) == 1:
        return await message.reply_text(languages[user_lang]["ask_question"])

    prompt: str = (message.text or message.caption).split(None, 1)[1]

    await prompt_handler(bot, message, prompt, is_media(message))


@bot.on_message(filters.private & filters.command("clear"))
async def clear_chat(bot: TgBot, message: Message) -> None:
    await clear_chat_handler(bot, message)
