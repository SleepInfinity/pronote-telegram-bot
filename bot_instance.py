import os
from tgram import TgBot
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_TOKEN")
bot: TgBot = TgBot(TELEGRAM_BOT_TOKEN, parse_mode="Markdown")
