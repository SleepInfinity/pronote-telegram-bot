import google.generativeai as genai
import google.ai.generativelanguage as glm
from ai.tools import get_current_time, get_homework
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

functions = {
    "get_current_time": get_current_time, 
    "get_homework": get_homework
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest", tools=functions.values(),
    system_instruction=open("ai/system_prompt.txt", "r").read()
)
