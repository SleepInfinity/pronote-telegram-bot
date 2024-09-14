# custom_buttons.py

import uuid
from telebot import TeleBot
from telebot.types import Message


class CustomButtons:
    def __init__(self, bot: TeleBot, bot_username: str):
        self.bot = bot
        self.bot_username = bot_username
        self.messages = {}  # Maps (chat_id, message_id) to message data
        self.uids = {}      # Maps uid to (chat_id, message_id)
        self.command_handlers = {}  # Maps command to handler function

    def create_button(self, text, command, uid=None):
        if uid is None:
            uid = str(uuid.uuid4())
        button_link = f"[{text}](https://t.me/{self.bot_username}?start={uid}_{command})"
        return button_link, uid

    def send_message_with_buttons(self, chat_id, text, buttons_info):
        """
        Sends a message with buttons placed at specified placeholders.

        :param chat_id: ID of the chat to send the message to.
        :param text: The message text containing placeholders like {button1}, {button2}, etc.
        :param buttons_info: A dictionary mapping placeholders to button text and commands.
        """
        buttons = {}
        for placeholder, info in buttons_info.items():
            button_text = info['text']
            button_command = info['command']
            button_link, uid = self.create_button(button_text, button_command)
            buttons[uid] = {
                'placeholder': placeholder,
                'text': button_text,
                'command': button_command,
                'link': button_link
            }
            self.uids[uid] = (chat_id, None)  # Message ID will be updated after sending

        # Replace placeholders in the text with the button links
        message_text = text
        for uid, data in buttons.items():
            message_text = message_text.replace(data['placeholder'], data['link'])

        # Send the message
        msg = self.bot.send_message(chat_id, message_text, parse_mode='Markdown', disable_web_page_preview=True)

        # Update mappings with message_id
        for uid in buttons:
            self.uids[uid] = (chat_id, msg.message_id)
        self.messages[(chat_id, msg.message_id)] = {
            'text_template': text,
            'buttons': buttons
        }

    def handle_button_click(self, message: Message):
        # Extract uid and command
        try:
            command_data = message.text.split("/start ")[1]
            uid, command = command_data.split("_", 1)
        except (IndexError, ValueError):
            # Invalid format, ignore
            return

        # Delete the message containing the /start command to keep the chat clean
        self.bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id
        )

        chat_id = message.chat.id
        key = self.uids.get(uid)
        if not key:
            # Unknown uid, ignore
            return

        msg_chat_id, message_id = key
        if msg_chat_id != chat_id:
            # Uid does not match chat_id, ignore
            return

        msg_data = self.messages.get((chat_id, message_id))
        if not msg_data:
            # Unknown message_id, ignore
            return

        # Call the registered handler for the command
        handler = self.command_handlers.get(command)
        if handler:
            # Pass the message, uid, command, and message data to the handler
            handler(message, uid, command, msg_data)
        else:
            # No handler registered for this command
            pass

    def register_command_handler(self, command, handler):
        """
        Register a handler function for a specific command.

        :param command: The command string.
        :param handler: The handler function to call when the command is received.
                        The function should have the signature:
                        handler(message, uid, command, msg_data)
        """
        self.command_handlers[command] = handler

    def handler(self, command):
        """
        Decorator to register a command handler.

        Usage:
        @custom_buttons.handler('command_name')
        def handler_function(message, uid, command, msg_data):
            # Handle the command
            pass
        """
        def decorator(func):
            self.register_command_handler(command, func)
            return func
        return decorator

    def update_message(self, chat_id, message_id, msg_data):
        """
        Rebuilds and updates the message text with updated buttons.

        :param chat_id: The chat ID.
        :param message_id: The message ID.
        :param msg_data: The message data containing text_template and buttons.
        """
        text_template = msg_data['text_template']
        buttons = msg_data['buttons']
        message_text = text_template
        for uid, data in buttons.items():
            message_text = message_text.replace(data['placeholder'], data['link'])
        # Edit the original message with the updated text
        self.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=message_text,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
