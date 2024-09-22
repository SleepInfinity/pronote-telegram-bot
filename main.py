from bot_instance import bot
from modules import database, language, handlers
from utils.logger import logger

if __name__ == '__main__':
    logger.info("Bot started")
    bot.run_for_updates()