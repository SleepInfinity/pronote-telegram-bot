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
