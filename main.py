from bot_instance import bot
from modules import database, language, handlers
from rich import print

if __name__ == '__main__':
    print("Bot started")
    bot.infinity_polling()