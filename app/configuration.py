from telethon import TelegramClient
from telethon.sessions import StringSession
import os
import asyncio
from db import retrieve_all_users
import logging
import logging_config


logger = logging.getLogger(__name__)


print(f"DEGBU -> {os.getenv("DEBUG", True)}")


desired_channel = os.getenv("desired_channel") # you can add your desired channel for listening
session_user = os.getenv("session_user")
session_bot = os.getenv("session_bot")
api_id = os.getenv("api_id")
api_hash = os.getenv("api_hash")
bot_token = os.getenv("bot_token")



try:
    client_bot = TelegramClient(StringSession(session_bot), api_id, api_hash
    ).start(bot_token)
    logger.info("client_bot started")
except Exception as e:
    logger.exception("ERROR occured while starting client_bot -> %s", e)

try:
    client_user = TelegramClient(StringSession(session_user), api_id, api_hash, 
    ).start()
    logger.info("client_user started")
except Exception as e:
    logger.exception("ERROR occured while starting client_user -> %s", e)


async def send_sorry_message():
    sorry_message = "⚠️کاربر گرامی. با عرض پوزش، درحال آپدیت سرویس هستیم. ممکن است ربات ساعاتی از ارائه خدمات به شما محروم شود.\n با تشکر ❤️"
    try:
        all_users = await retrieve_all_users()
        for user in all_users:

            try:
                await client_bot.send_message(user[0], sorry_message)
            except Exception as e:
                print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    



if os.getenv("FIXING", "false").lower() == "true":
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(send_sorry_message())