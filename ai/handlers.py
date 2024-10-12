from ai.chat import model
import google.generativeai as genai
from ai.utils import get_user_chat, set_user_chat, clear_user_chat, call_functions


async def prompt_handler(bot, message, prompt):
    user_id = message.from_user.id
    chat = await get_user_chat(user_id)
    response = chat.send_message(f"{prompt}")
    while True:
        print("running functions")
        response_parts = await call_functions(response, message)
        if response_parts:
            response = chat.send_message(response_parts)
        else:
            break

    await set_user_chat(user_id, chat)
    try:
        await message.reply_text(response.text)
    except:
        await message.reply_text(response.text, parse_mode="disabled")
