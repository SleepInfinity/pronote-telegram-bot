from tgram import TgBot
from tgram.types import Message
from ai.chat import model
import google.generativeai as genai
from ai.chat import functions
from babel.dates import format_date
from modules.language import languages

user_chats = {}

async def get_user_chat(user_id):
    if user_id in user_chats:
        return user_chats[user_id]
    chat = model.start_chat(enable_automatic_function_calling=False)
    return chat


async def set_user_chat(user_id, chat):
    user_chats[user_id] = chat


async def clear_user_chat(user_id):
    if user_id in user_chats:
        del user_chats[user_id]


async def call_functions(response, user_id):
    responses = {}
    for part in response.parts:
        if fn := part.function_call:
            if fn.name == "get_homework":
                fn.args["user_id"] = str(user_id)
            responses[fn.name] = await functions[fn.name](**fn.args)
    if not responses:
        return None
    response_parts = [
        genai.protos.Part(
            function_response=genai.protos.FunctionResponse(
                name=fn, response={"result": val}
            )
        )
        for fn, val in responses.items()
    ]
    return response_parts


async def format_homework(homeworks):
    formatted_homeworks = ""
    locale = languages["en"]["locale"]
    for homework in homeworks:
        formatted_homeworks += f"To do for {format_date(homework.date, format='EEEE dd/MM/YYYY', locale=locale)}\n"
        formatted_homeworks += f"Subject: {homework.subject.name}\n"
        formatted_homeworks += f"Description: {homework.description}\n"
        formatted_homeworks += f"Is done: {'Yes' if homework.done else 'No'}\n\n"
    return formatted_homeworks

async def resolve_media(bot, message):
    """
    Converts a message media to a gemini compatible file object
    """
    downloaded_file, mime_type = await download_file(bot, message)
    file = await upload_file(downloaded_file, mime_type)
    return file


async def download_file(bot: TgBot, message: Message):
    if message.photo:
        file = message.photo[-1]
        mime_type = "image/png"
    else:
        file = message.document
        mime_type = file.mime_type

    file_id = file.file_id
    file_info = await bot.get_file(file_id)
    downloaded_file = await bot.download_file(
        file_id=file_id, file_path=file_info.file_path, in_memory=True
    )
    return downloaded_file, mime_type

async def upload_file(file, mime_type):
    uploaded_file = genai.upload_file(file, mime_type=mime_type)
    file.close()
    return uploaded_file