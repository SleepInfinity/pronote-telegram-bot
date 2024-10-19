from io import BytesIO
import json
from typing import List
from uuid import uuid4
from pronotepy import Client
from tgram.types import CallbackQuery, Message
from tgram import TgBot
from tgram.handlers import Handlers
from tgram import filters
from pronotepy.ent import lyceeconnecte_aquitaine
from bot_instance import bot
from modules.database import get_user_lang, clients
from modules.language import languages
from pyzbar.pyzbar import decode, Decoded
from PIL import Image
from tgram.types import File
from utils.logger import logger


async def handle_login_qrcode(call: CallbackQuery) -> None:
    user_lang: str = await get_user_lang(call.message.chat.id)
    await call.edit_message_text(languages[user_lang]["send_qrcode"])
    return await bot.ask(
        update_type=Handlers.MESSAGE,
        next_step=process_login_qrcode,
        filters=filters.chat(call.message.chat.id) & filters.photo,
    )


async def process_login_qrcode(bot: TgBot, message: Message, data: dict) -> None | Message:
    user_lang: str = await get_user_lang(message.chat.id)
    if not message.photo:
        return await message.reply_text(languages[user_lang]["please_send_photo"])
    photo_file_id: str = message.photo[-1].file_id
    photo_file_info: File = await bot.get_file(photo_file_id)
    downloaded_photo_file: BytesIO = await bot.download_file(
        file_id=photo_file_id, file_path=photo_file_info.file_path, in_memory=True
    )

    img: Image.Image = Image.open(downloaded_photo_file)
    decoded_objects: List[Decoded] = decode(img)

    try:
        qrcode_data = json.loads(decoded_objects[0].data.decode("utf-8"))
        data["qrcode_data"] = qrcode_data
    except Exception as _:
        return await message.reply_text(languages[user_lang]["qrcode_decode_error"])

    await message.reply_text(languages[user_lang]["send_pin"])
    return await bot.ask(
        update_type=Handlers.MESSAGE,
        next_step=process_login_qrcode_pin_handler,
        filters=filters.chat(message.chat.id) & filters.text,
        data=data,
    )


async def process_login_qrcode_pin_handler(bot: TgBot, message: Message, data: dict) -> None | Message:
    user_lang: str = await get_user_lang(message.chat.id)
    pin: str = message.text
    if len(pin) != 4 or not pin.isdigit():
        return await message.reply_text(languages[user_lang]["please_send_4_digits"])

    try:
        client: Client = Client.qrcode_login(data["qrcode_data"], pin, str(uuid4()))
    except Exception as _:
        return await message.reply_text(languages[user_lang]["login_failed"])

    if client.logged_in:
        credentials: dict = {
            "login_method": "qrcode",
            "client": client,
            "url": client.pronote_url,
            "username": client.username,
            "password": client.password,
            "uuid": client.uuid,
        }
        clients[message.chat.id] = credentials
        await bot.send_message(
            message.chat.id, languages[user_lang]["login_successful"]
        )
    else:
        await bot.send_message(message.chat.id, languages[user_lang]["login_failed"])


async def handle_login_pronote(call: CallbackQuery) -> None:
    user_lang: str = await get_user_lang(call.message.chat.id)
    await call.edit_message_text(languages[user_lang]["send_pronote_credentials"])
    return await bot.ask(
        update_type=Handlers.MESSAGE,
        next_step=process_login_pronote,
        filters=filters.user(call.message.chat.id) & filters.text,
    )


async def process_login_pronote(bot: TgBot, message: Message, data: dict) -> None:
    user_lang: str = await get_user_lang(message.chat.id)
    try:
        url, username, password = message.text.split(",")
        client: Client = Client(url.strip(), username.strip(), password.strip())

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
            await bot.send_message(
                message.chat.id, languages[user_lang]["login_successful"]
            )
        else:
            await bot.send_message(
                message.chat.id, languages[user_lang]["login_failed"]
            )
    except Exception as e:
        await bot.send_message(
            message.chat.id, languages[user_lang]["error_logging_in"]
        )
        logger.error(
            f"[{str(message.chat.id)}] Error while logging in with pronote: {str(e)}"
        )


async def handle_login_lyceeconnecte_aquitaine(call: CallbackQuery) -> None:
    user_lang: str = await get_user_lang(call.from_user.id)
    await call.edit_message_text(languages[user_lang]["send_lyceeconnecte_credentials"])
    return await bot.ask(
        update_type=Handlers.MESSAGE,
        next_step=process_login_lyceeconnecte_aquitaine,
        filters=filters.user(call.from_user.id) & filters.text,
    )


async def process_login_lyceeconnecte_aquitaine(bot: TgBot, message: Message, _) -> None:
    user_lang: str = await get_user_lang(message.chat.id)
    try:
        url, username, password = message.text.split(",")
        client: Client = Client(
            pronote_url=url.strip(),
            username=username.strip(),
            password=password.strip(),
            ent=lyceeconnecte_aquitaine,
        )
        client.username = username
        client.password = password

        if client.logged_in:
            credentials: dict = {
                "login_method": "lyceeconnecte",
                "client": client,
                "url": client.pronote_url,
                "username": client.username,
                "password": client.password,
                "uuid": client.uuid,
            }
            clients[message.chat.id] = credentials
            await bot.send_message(
                message.chat.id, languages[user_lang]["login_successful"]
            )
        else:
            await bot.send_message(
                message.chat.id, languages[user_lang]["login_failed"]
            )
    except Exception as e:
        await bot.send_message(
            message.chat.id, languages[user_lang]["error_logging_in"]
        )
        logger.error(
            f"[{str(message.chat.id)}] Error while logging in with lyceeconnecte: {str(e)}"
        )


async def logout_credentials(user_id: int) -> bool:
    client_credentials: dict | None = clients.get(user_id)
    if client_credentials:
        del clients[user_id]
        return True
    return False
