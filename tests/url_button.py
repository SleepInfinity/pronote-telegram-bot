import telebot
import uuid

bot_token = '2061500826:AAHLN5kWSmXO5e-NqUjJQB5fCEWGTl7FvAM'
bot_username='Accounttt_pubggg_bot'
bot = telebot.TeleBot(bot_token)

user_messages = {}


@bot.message_handler(commands=['start'])
def start_command(message):
    if "/start " in message.text:
        uid, command=handle_button_click(message)
        command_handler(message, uid, command)
    else:
        button, uid=create_button(text="⬜", command="check")
        msg=bot.send_message(message.chat.id, f"Button: {button}", parse_mode='Markdown')
        user_messages[uid]=msg.id

def create_button(text, command):
    uid=str(uuid.uuid4())
    return f"[{text}](t.me/{bot_username}?start={uid}_{command}).", uid

def handle_button_click(message):
    command_data=message.text.split("/start ")[1]
    uid, command=command_data.split("_")
    bot.delete_message(
        message_id=message.id,
        chat_id=message.chat.id
    )
    return uid, command

def command_handler(message, uid, command):
    message_id=user_messages[uid]
    if command=="check":
        button, uid=create_button(text="✅", command="uncheck")
        msg=bot.edit_message_text(
            message_id=message_id,
            chat_id=message.chat.id,
            text=f"Button: {button}",
            parse_mode='Markdown'
        )
        user_messages[uid]=msg.id
    elif command=="uncheck":
        button, uid=create_button(text="⬜", command="check")
        msg=bot.edit_message_text(
            message_id=message_id,
            chat_id=message.chat.id,
            text=f"Button: {button}",
            parse_mode='Markdown'
        )
        user_messages[uid]=msg.id

def send_message_with_button(text, chat_id, button_text, button_command):
    button, uid=create_button(text=button_text, command=button_command)
    msg=bot.send_message(chat_id, f"Button: {button}", parse_mode='Markdown')
    user_messages[uid]=msg.id


bot.infinity_polling()
