from bot_instance import bot
from utils.logger import logger
from modules import database, language, handlers

if __name__ == "__main__":
    logger.info("Bot started")
    bot.run_for_updates()
