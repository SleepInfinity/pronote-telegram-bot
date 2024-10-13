import datetime
import os
from dotenv import load_dotenv
import pytz
from modules.database import clients

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


async def get_homework(user_id: str = "0") -> str:
    """
    Get the upcoming homework of the student with the due date for each homework.

    Args:
        user_id: The user identifier linked to the homework of that user. This argument is automatically provided, you can put any number here.
    """
    from ai.utils import format_homework
    client_credentials = clients.get(int(user_id))
    if client_credentials:
        client = client_credentials["client"]
        client.session_check()
        today = datetime.datetime.now(timezone).date()
        homeworks = client.homework(today)
        homeworks.sort(key=lambda homework: homework.date)
        if not homeworks:
            return "There is no upcoming homework."

        formatted_homeworks = await format_homework(homeworks)
        return formatted_homeworks
    return "You are not logged in to the pronote account."
