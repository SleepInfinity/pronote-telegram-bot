import telebot
import uuid

bot_token = 'YOUR_BOT_TOKEN'
bot_username = 'YOUR_BOT_USERNAME'
bot_token = '7103089023:AAFPDuFCuiUwx6IcPD6MRpQepwJkJWSeJZU'
bot_username='qszbot'
bot = telebot.TeleBot(bot_token)

# Data structures to store messages and button states
messages = {}  # Maps message_id to message data
uids = {}      # Maps uid to message_id

# Function to create a button
def create_button(text, command, uid=None):
    if uid is None:
        uid = str(uuid.uuid4())
    button_link = f"[{text}](https://t.me/{bot_username}?start={uid}_{command})"
    return button_link, uid

# Function to send a message with buttons placed anywhere in the text
def send_message_with_buttons(chat_id, text, buttons_info):
    """
    Sends a message with buttons placed at specified placeholders.

    :param chat_id: ID of the chat to send the message to.
    :param text: The message text containing placeholders like {button1}, {button2}, etc.
    :param buttons_info: A dictionary mapping placeholders to button text and commands.
                         Example:
                         {
                             '{button1}': {'text': 'Button 1', 'command': 'command1'},
                             '{button2}': {'text': 'Button 2', 'command': 'command2'}
                         }
    """
    buttons = {}
    for placeholder, info in buttons_info.items():
        button_text = info['text']
        button_command = info['command']
        button_link, uid = create_button(button_text, button_command)
        buttons[uid] = {
            'placeholder': placeholder,
            'text': button_text,
            'command': button_command,
            'link': button_link
        }
        # Map uid to message_id later
        uids[uid] = None  # Will be updated after sending the message

    # Replace placeholders in the text with the button links
    message_text = text
    for uid, data in buttons.items():
        message_text = message_text.replace(data['placeholder'], data['link'])

    # Send the message
    msg = bot.send_message(chat_id, message_text, parse_mode='Markdown', disable_web_page_preview=True)

    # Update mappings with message_id
    for uid in buttons:
        uids[uid] = msg.message_id
    messages[msg.message_id] = {
        'chat_id': chat_id,
        'text_template': text,
        'buttons': buttons
    }

# Handler for the /start command, which is triggered when a button is clicked
@bot.message_handler(commands=['start'])
def start_command(message):
    if "/start " in message.text:
        uid, command = handle_button_click(message)
        handle_command(message, uid, command)
    else:
        # Default action when /start is called without parameters
        text = "Welcome! Please use the buttons below:\n{button1} {button2}"
        buttons_info = {
            '{button1}': {'text': 'Option 1', 'command': 'option1'},
            '{button2}': {'text': 'Option 2', 'command': 'option2'}
        }
        send_message_with_buttons(message.chat.id, text, buttons_info)

# Function to parse the uid and command from the message text
def handle_button_click(message):
    command_data = message.text.split("/start ")[1]
    uid, command = command_data.split("_", 1)
    # Delete the message containing the /start command to keep the chat clean
    bot.delete_message(
        chat_id=message.chat.id,
        message_id=message.message_id
    )
    return uid, command

# Function to handle commands based on button clicks
def handle_command(message, uid, command):
    message_id = uids.get(uid)
    if not message_id:
        return  # Unknown uid, ignore

    msg_data = messages.get(message_id)
    if not msg_data:
        return  # Unknown message_id, ignore

    chat_id = msg_data['chat_id']
    buttons = msg_data['buttons']

    # Perform action based on the command
    # You can define your own actions here
    if command == 'option1':
        response_text = "You selected Option 1!"
    elif command == 'option2':
        response_text = "You selected Option 2!"
    else:
        response_text = f"You clicked a button with command: {command}"

    # Optionally, update the button or message if needed
    # For example, mark the button as selected
    button_data = buttons[uid]
    button_data['text'] = f"✅ {button_data['text']}"
    button_link, _ = create_button(button_data['text'], command, uid)
    button_data['link'] = button_link

    # Rebuild the message text with updated buttons
    text_template = msg_data['text_template']
    message_text = text_template
    for uid, data in buttons.items():
        message_text = message_text.replace(data['placeholder'], data['link'])

    # Edit the original message with the updated text
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=message_text,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )

    # Send a response message to the user
    bot.send_message(chat_id, response_text)

# Start the bot
bot.infinity_polling()
