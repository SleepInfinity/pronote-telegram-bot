import datetime
import os
from dotenv import load_dotenv
import pytz
from pytz.tzinfo import DstTzInfo
from modules.database import clients
from pronotepy import Client, Homework

load_dotenv()

timezone_config: str = os.getenv("TIMEZONE") or "UTC"

timezone: DstTzInfo = pytz.timezone(timezone_config)


async def get_current_time() -> str:
    """
    Get the current time and date.
    """
    current_time: str = datetime.datetime.now(timezone).strftime(
        "Day name: %A, Day: %d, Month: %m, Year: %Y, Hour: %H:%M:%S"
    )
    print(current_time)
    return current_time


async def get_homework(user_id: int = 0) -> str:
    """
    Get the upcoming homework of the student with the due date for each homework.

    Args:
        user_id: The user identifier linked to the homework of that user. This argument is automatically provided, you can put any number here.
    """
    from ai.utils import format_homework

    client_credentials: dict | None = clients.get(user_id)
    if client_credentials:
        client: Client = client_credentials["client"]
        client.session_check()
        today = datetime.datetime.now(timezone).date()
        homeworks: Homework = client.homework(today)
        if not homeworks:
            return "There is no upcoming homework."

        homeworks.sort(key=lambda homework: homework.date)

        formatted_homeworks: str = await format_homework(homeworks)
        return formatted_homeworks
    return "You are not logged in to the pronote account."
