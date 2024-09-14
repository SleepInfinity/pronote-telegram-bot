# bot.py

import telebot
from telebot.types import Message
from custom_buttons import CustomButtons

bot_token = 'YOUR_BOT_TOKEN'
bot_username = 'YOUR_BOT_USERNAME'  # Without '@', e.g., 'my_bot'
bot_token = '7103089023:AAFPDuFCuiUwx6IcPD6MRpQepwJkJWSeJZU'
bot_username='qszbot'
bot = telebot.TeleBot(bot_token)

# Instantiate the CustomButtons class
custom_buttons = CustomButtons(bot, bot_username)

# Handler for the /start command
@bot.message_handler(commands=['start'])
def start_command(message: Message):
    if "/start " in message.text:
        custom_buttons.handle_button_click(message)
    else:
        # Default action when /start is called without parameters
        text = "Welcome! Please use the buttons below:\n{button1} {button2}"
        buttons_info = {
            '{button1}': {'text': 'Option 1', 'command': 'option1'},
            '{button2}': {'text': 'Option 2', 'command': 'option2'}
        }
        custom_buttons.send_message_with_buttons(message.chat.id, text, buttons_info)

# Define command handlers using the decorator
@custom_buttons.handler('option1')
def handle_option1(message, uid, command, msg_data):
    # Do something when Option 1 is clicked
    print("You selected Option 1!")

@custom_buttons.handler('option2')
def handle_option2(message, uid, command, msg_data):
    # Do something when Option 2 is clicked
    print("You selected Option 2!")

# Start the bot
bot.infinity_polling()
