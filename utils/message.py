from tgram.types import Message


def is_media(message: Message):
    if message.photo or message.document:
        return True
    return False
