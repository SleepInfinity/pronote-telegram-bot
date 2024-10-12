from collections import defaultdict
import datetime
from babel.dates import format_date
import os
from dotenv import load_dotenv
import pytz
from modules.database import clients
from modules.language import languages, get_user_lang

load_dotenv()
timezone = pytz.timezone(os.getenv("TIMEZONE") or "UTC")


async def get_current_time() -> str:
    """
    Get the current time and date.
    """
    current_time = datetime.datetime.now(timezone).strftime(
        "Day name: %A, Day: %d, Month: %m, Year: %Y, Hour: %H:%M:%S"
    )
    return current_time


async def get_homework(user_id: str) -> str:
    """
    Get the upcoming homework of the student. Only use this function when the user asks for homework.

    Args:
        user_id: The user identifier linked to the homework of that user. This argument is automatically provided, you can put any number here.
    """
    print(user_id)
    user_lang = await get_user_lang(int(user_id))
    client_credentials = clients.get(int(user_id))
    if client_credentials:
        client = client_credentials["client"]
        client.session_check()
        today = datetime.datetime.now(timezone).date()
        homeworks = client.homework(today)
        homeworks.sort(key=lambda homework: homework.date)
        if not homeworks:
            return "There is no upcoming homework."

        # group homeworks list into sublists of homeworks for each day.
        grouped_data = defaultdict(list)
        for homework in homeworks:
            grouped_data[homework.date].append(homework)
        grouped_homeworks = list(grouped_data.values())

        user_locale = languages[user_lang]["locale"]

        homework_message = languages[user_lang]["homework_header"]
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
        print(homework_message)
        return homework_message
    return "You are not logged in to the pronote account."
