import os
from tgram import TgBot, filters
from dotenv import load_dotenv
from modules.database import get_user_ids
from tgram.types import Message
from tgram.handlers import Handlers

load_dotenv()


async def get_broadcast_message(bot: TgBot, message: Message):
    admin_id = os.getenv("ADMIN_ID")
    if admin_id:
        if str(message.from_user.id) == str(admin_id):
            await message.reply_text("Send the broadcast message:\nSend /c to cancel.")
            return await bot.ask(
                update_type=Handlers.MESSAGE,
                next_step=broadcast_message_handler,
                cancel=cancel,
                filters=filters.user(message.from_user.id) & filters.private,
            )
        return await message.reply_text("You are not an admin!")
    return await message.reply_text("Broadcast is disabled.")


async def broadcast_message_handler(bot: TgBot, message: Message, _):
    broadcast_message = message.text
    user_ids = await get_user_ids()
    m = await message.reply_text(f"sending to {len(user_ids)} users...")
    sent_to_users = 0
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, broadcast_message)
            sent_to_users += 1
        except Exception as _:
            pass
    await m.edit_text(f"Message sent to {sent_to_users} users successfully.")


async def cancel(_, m: Message) -> bool:
    if m.text.lower() == "/c":
        await m.reply_text("Cancelled.")
        return True
    return False
