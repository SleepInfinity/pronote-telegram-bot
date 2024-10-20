from typing import List
from modules.language import languages
from modules.database import get_user_lang
from tgram.types import Message
from google.generativeai.generative_models import ChatSession
from google.generativeai.types.file_types import File
from google.generativeai.types.generation_types import GenerateContentResponse
from google.generativeai.protos import Part
from utils.message import auto_escape
from tgram import TgBot
from ai.utils import (
    get_user_chat,
    resolve_media,
    set_user_chat,
    clear_user_chat,
    call_functions,
)


async def prompt_handler(
    bot: TgBot, message: Message, prompt: str, is_media: bool
) -> None:
    user_id: int = message.from_user.id
    chat: ChatSession = await get_user_chat(user_id)
    if is_media:
        file: File = await resolve_media(bot, message)
        response: GenerateContentResponse = chat.send_message([file, prompt])
    else:
        response: GenerateContentResponse = chat.send_message(prompt)
    while True:
        response_parts: List[Part] = await call_functions(
            response, message.from_user.id
        )
        if response_parts:
            response: GenerateContentResponse = chat.send_message(response_parts)
        else:
            break

    await set_user_chat(user_id, chat)
    text: str = auto_escape(response.text)
    try:
        await message.reply_text(text)
    except Exception as _:
        await message.reply_text(text, parse_mode="disabled")


async def clear_chat_handler(bot: TgBot, message: Message):
    user_id: int = message.from_user.id
    user_lang: str = await get_user_lang(user_id)
    await clear_user_chat(user_id)
    await message.reply_text(languages[user_lang]["chat_cleared"])
