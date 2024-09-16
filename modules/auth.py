import io
import json
from uuid import uuid4
import pronotepy
from pronotepy.ent import lyceeconnecte_aquitaine
from bot_instance import bot
from modules.database import get_user_lang, clients
from modules.language import languages
from pyzbar.pyzbar import decode
from PIL import Image
from rich import print

def handle_login_qrcode(call):
    user_lang=get_user_lang(call.message.chat.id)
    msg = bot.edit_message_text(
        message_id=call.message.id,
        chat_id=call.message.chat.id,
        text=languages[user_lang]["send_qrcode"]
    )
    bot.register_next_step_handler(msg, process_login_qrcode)

def process_login_qrcode(message):
    user_lang=get_user_lang(message.chat.id)
    if message.content_type != "photo" or not message.photo:
        bot.reply_to(message, languages[user_lang]["please_send_photo"])
        return
    photo_file_id = message.photo[-1].file_id
    photo_file_info = bot.get_file(photo_file_id)
    downloaded_photo_file = bot.download_file(photo_file_info.file_path)

    image_stream = io.BytesIO(downloaded_photo_file)
    img = Image.open(image_stream)
    decoded_objects = decode(img)

    try:
        qrcode_data = json.loads(decoded_objects[0].data.decode("utf-8"))
    except Exception as e:
        bot.reply_to(message, languages[user_lang]["qrcode_decode_error"])
        return

    msg = bot.reply_to(message, languages[user_lang]["send_pin"])
    bot.register_next_step_handler(msg, process_login_qrcode_pin_handler, qrcode_data)

def process_login_qrcode_pin_handler(message, qrcode_data):
    user_lang=get_user_lang(message.chat.id)
    pin = message.text
    if len(pin) != 4 or not pin.isdigit():
        bot.reply_to(message, languages[user_lang]["please_send_4_digits"])
        return
    
    try:
        client = pronotepy.Client.qrcode_login(qrcode_data, pin, str(uuid4()))
    except Exception as e:
        bot.reply_to(message, languages[user_lang]["login_failed"])
        return
    
    if client.logged_in:
        credentials = {
            "login_method": "qrcode",
            "client": client,
            "url": client.pronote_url,
            "username": client.username,
            "password": client.password,
            "uuid": client.uuid,
        }
        clients[message.chat.id] = credentials
        bot.send_message(message.chat.id, languages[user_lang]["login_successful"])
    else:
        bot.send_message(message.chat.id, languages[user_lang]["login_failed"])

def handle_login_pronote(call):
    user_lang=get_user_lang(call.message.chat.id)
    msg = bot.edit_message_text(
        message_id=call.message.id,
        chat_id=call.message.chat.id,
        text=languages[user_lang]["send_pronote_credentials"]
    )
    bot.register_next_step_handler(msg, process_login_pronote)

def process_login_pronote(message):
    user_lang=get_user_lang(message.chat.id)
    try:
        url, username, password = message.text.split(',')
        client = pronotepy.Client(url.strip(), username.strip(), password.strip())

        if client.logged_in:
            credentials = {
                "login_method": "credentials",
                "client": client,
                "url": client.pronote_url,
                "username": client.username,
                "password": client.password,
                "uuid": client.uuid,
            }
            clients[message.chat.id] = credentials
            bot.send_message(message.chat.id, languages[user_lang]["login_successful"])
        else:
            bot.send_message(message.chat.id, languages[user_lang]["login_failed"])
    except Exception as e:
        bot.send_message(message.chat.id, languages[user_lang]["error_logging_in"])
        print(e)

def handle_login_lyceeconnecte_aquitaine(call):
    user_lang=get_user_lang(call.message.chat.id)
    msg = bot.edit_message_text(
        message_id=call.message.id,
        chat_id=call.message.chat.id,
        text=languages[user_lang]["send_lyceeconnecte_credentials"]
    )
    bot.register_next_step_handler(msg, process_login_lyceeconnecte_aquitaine)

def process_login_lyceeconnecte_aquitaine(message):
    user_lang=get_user_lang(message.chat.id)
    try:
        url, username, password = message.text.split(',')
        client = pronotepy.Client(
            pronote_url=url.strip(),
            username=username.strip(),
            password=password.strip(),
            ent=lyceeconnecte_aquitaine
        )
        client.username = username
        client.password = password

        if client.logged_in:
            credentials = {
                "login_method": "lyceeconnecte",
                "client": client,
                "url": client.pronote_url,
                "username": client.username,
                "password": client.password,
                "uuid": client.uuid,
            }
            clients[message.chat.id] = credentials
            bot.send_message(message.chat.id, languages[user_lang]["login_successful"])
        else:
            bot.send_message(message.chat.id, languages[user_lang]["login_failed"])
    except Exception as e:
        bot.send_message(message.chat.id, languages[user_lang]["error_logging_in"])
        print(e)

def logout_credentials(user_id):
    client_credentials = clients.get(user_id)
    if client_credentials:
        del clients[user_id]
        return True
    return False