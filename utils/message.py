from tgram.types import Message
import re


def is_media(message: Message):
    if message.photo or message.document:
        return True
    return False




def escape_special_chars(text, excluded_chars=None):
    # List of special characters
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    # If there are any excluded characters, remove them from the special_chars list
    if excluded_chars:
        special_chars = [char for char in special_chars if char not in excluded_chars]

    # Create a regex pattern for the remaining special characters
    if special_chars:
        pattern = '[' + re.escape(''.join(special_chars)) + ']'
        return re.sub(pattern, r'\\\g<0>', text)
    return text
