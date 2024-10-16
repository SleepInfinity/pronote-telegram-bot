import google.generativeai as genai
from ai.tools import get_current_time, get_homework
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

tools_dict: dict = {"get_current_time": get_current_time, "get_homework": get_homework}

model: genai.GenerativeModel = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    tools=[get_current_time, get_homework],
    system_instruction=open("ai/system_prompt.txt", "r").read(),
)
