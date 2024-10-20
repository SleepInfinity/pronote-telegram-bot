from pronotepy import Homework
from tgram import TgBot
from tgram.types import Message
from ai.chat import model
import google.generativeai as genai
from google.generativeai.generative_models import ChatSession
from google.generativeai.types.generation_types import GenerateContentResponse
from google.generativeai.types.file_types import File as GoogleFile
from google.generativeai.protos import Part
from io import BytesIO
from ai.chat import tools_dict
from tgram.types import PhotoSize, Document, File as TgramFile
from babel.dates import format_date
from modules.language import languages
from typing import List, Tuple

user_chats: dict = {}


async def get_user_chat(user_id: int) -> ChatSession:
    if user_id in user_chats and isinstance(user_chats[user_id], ChatSession):
        return user_chats[user_id]
    chat: ChatSession = model.start_chat(enable_automatic_function_calling=False)
    return chat


async def set_user_chat(user_id: int, chat: ChatSession) -> None:
    user_chats[user_id] = chat


async def clear_user_chat(user_id: int) -> None:
    if user_id in user_chats:
        del user_chats[user_id]


async def call_functions(response: GenerateContentResponse, user_id: int) -> List[Part]:
    responses: dict = {}
    for part in response.parts:
        if fn := part.function_call:
            if fn.name == "get_homework":
                fn.args["user_id"] = user_id
            responses[fn.name] = await tools_dict[fn.name](**fn.args)
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


async def format_homework(homeworks: Homework) -> str:
    formatted_homeworks: str = ""
    locale: str = languages["en"]["locale"]
    for homework in homeworks:
        formatted_homeworks += f"To do for {format_date(homework.date, format='EEEE dd/MM/YYYY', locale=locale)}\n"
        formatted_homeworks += f"Subject: {homework.subject.name}\n"
        formatted_homeworks += f"Description: {homework.description}\n"
        formatted_homeworks += f"Is done: {'Yes' if homework.done else 'No'}\n\n"
    return formatted_homeworks


async def resolve_media(bot: TgBot, message: Message) -> GoogleFile:
    """
    Converts a message media to a gemini compatible file object
    """
    downloaded_file: BytesIO
    mime_type: str
    downloaded_file, mime_type = await download_file(bot, message)
    file: GoogleFile = await upload_file(downloaded_file, mime_type)
    return file


async def download_file(bot: TgBot, message: Message) -> Tuple[BytesIO, str]:
    if message.photo:
        await bot.send_chat_action(message.chat.id, "upload_photo")
        file: PhotoSize = message.photo[-1]
        mime_type: str = "image/png"
    else:
        await bot.send_chat_action(message.chat.id, "upload_document")
        file: Document = message.document
        mime_type: str = file.mime_type

    file_id: str = file.file_id
    file_info: TgramFile = await bot.get_file(file_id)
    downloaded_file: BytesIO = await bot.download_file(
        file_id=file_id, file_path=file_info.file_path, in_memory=True
    )
    return downloaded_file, mime_type


async def upload_file(file: BytesIO, mime_type: str) -> GoogleFile:
    uploaded_file: GoogleFile = genai.upload_file(file, mime_type=mime_type)
    file.close()
    return uploaded_file
