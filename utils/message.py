from typing import List
from tgram.types import Message
import re


def is_media(message: Message) -> bool:
    if message.photo or message.document:
        return True
    return False


def escape_special_chars(text: str, excluded_chars: List[str]=[]) -> str:
    # List of special characters
    special_chars: List[str] = [
        "_",
        "*",
        "[",
        "]",
        "(",
        ")",
        "~",
        "`",
        ">",
        "#",
        "+",
        "-",
        "=",
        "|",
        "{",
        "}",
        ".",
        "!",
    ]

    # If there are any excluded characters, remove them from the special_chars list
    if excluded_chars:
        special_chars: List[str] = [char for char in special_chars if char not in excluded_chars]

    # Create a regex pattern for the remaining special characters
    if special_chars:
        pattern: str = "[" + re.escape("".join(special_chars)) + "]"
        return re.sub(pattern, r"\\\g<0>", text)
    return text
