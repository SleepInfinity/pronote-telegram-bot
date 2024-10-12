from collections import defaultdict
from ai.chat import model
import google.generativeai as genai
from ai.tools import get_current_time, get_homework

user_chats = {}
functions = {"get_current_time": get_current_time, "get_homework": get_homework}


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


async def call_functions(response, message):
    responses = {}
    for part in response.parts:
        if fn := part.function_call:
            if fn.name == "get_homework":
                fn.args["user_id"] = str(message.from_user.id)
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
    print(response_parts)
    return response_parts


async def format_homework(homeworks):
    # group homeworks list into sublists of homeworks for each day.
    grouped_data = defaultdict(list)
    for homework in homeworks:
        grouped_data[homework.date].append(homework)
    grouped_homeworks = list(grouped_data.values())
    for homework in grouped_homeworks:
        pass
