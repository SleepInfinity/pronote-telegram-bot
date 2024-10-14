import google.generativeai as genai
from modules.language import languages
from modules.database import get_user_lang
from tgram.types import Message
from tgram import TgBot
from ai.utils import get_user_chat, resolve_media, set_user_chat, clear_user_chat, call_functions


async def prompt_handler(bot: TgBot, message: Message, prompt: str, is_media: bool):
    user_id = message.from_user.id
    chat = await get_user_chat(user_id)
    if is_media:
        file = await resolve_media(bot, message)
        response = chat.send_message([file, prompt])
    else:
        response = chat.send_message(prompt)
    while True:
        response_parts = await call_functions(response, message.from_user.id)
        if response_parts:
            response = chat.send_message(response_parts)
        else:
            break

    await set_user_chat(user_id, chat)
    text = response.text.replace("\\", "")
    try:
        await message.reply_text(text)
    except:
        await message.reply_text(text, parse_mode="disabled")

async def clear_chat_handler(bot, message):
    user_id = message.from_user.id
    user_lang = await get_user_lang(user_id)
    await clear_user_chat(user_id)
    await message.reply_text(languages[user_lang]["chat_cleared"])