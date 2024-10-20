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

def auto_escape(text: str) -> str:
    text: str = text.replace("**", "*").replace("* *", "- *")
    to_be_escaped: str = ""
    for line in text.split("\n"):
        to_be_escaped += line + "*\n"
    match_md = r"((([_*`]).+?\3[^_*`]*)*)([_*`])"
    escaped: str = re.sub(match_md, "\g<1>\\\\\g<4>", to_be_escaped)

    final_text: str = ""

    inside_code_block: bool = False
    for line in escaped.split("\n"):
        if line.strip().startswith("```") \
        or line.strip().endswith("```"):
            inside_code_block = not inside_code_block

        if inside_code_block:
            final_text += line[:-2].replace("\\", "") + "\n"
        else:
            final_text += line[:-2] + "\n"
    return final_text