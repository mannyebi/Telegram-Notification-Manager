import ahocorasick
from db import retrieve_all_keywords, retrieve_message
from configuration import client_bot, desired_channel
import logging


logger = logging.getLogger(__name__)


def generate_link(id):
    """generate message's link using their id.

    Args:
        id(int): the message's id.
    """
    return f"https://t.me/{desired_channel.split("@")[1]}/{id}"



async def search(event, New=False, Updated=False, Deleted=False):
    users_list = list()
    keywords = await retrieve_all_keywords() # get all keywords from database
    for keywrod in keywords:
        users_id = keywrod[0]
        uesrs_keyword = str(keywrod[1]).strip()
        users_list.append([users_id, uesrs_keyword])



    try:
        message_text = event.message.message
        text = ' '.join(message_text.split())  # removing extra spaces
    except:
        message_id = event.deleted_id
        message_text = await retrieve_message(message_id)
        if message_text:
            message = message_text[0][0]
            text = ' '.join(message.split())  # removing extra spaces
        else:
            return

    # Use defaultdict to collect all matches for each user
    results = []
    added_users = [] # storing users who have one keyword, so we don't check their other keywords.

    for user_id, key in users_list:
        if user_id not in added_users: # check if user has no matched keyword before.
            if key in text:
                results.append([user_id, key])
                added_users.append(user_id)


    for user_id, matched_keywords in results:
        if New:
            message = (
                f"کلمه کلیدی `{matched_keywords}` در پیام زیر مشاهده گردید : \n \n ⬇️ \n "
                f"```{message_text}``` \n  [link🔗]({generate_link(event.id)})"
            )
            await client_bot.send_message(user_id, message, link_preview=False)
            logger.info(f"new message notification sent to {user_id}")
        elif Updated:
            message = (
                f"⚠️اطلاعیه ی زیر ویرایش شد⚠️ \n \n ⬇️ \n ```{message_text}``` \n "
                f"**[link🔗]**({generate_link(event.id)})"
            )
            await client_bot.send_message(user_id, message, link_preview=False)
            logger.info(f"edited message notification sent to {user_id}")
        elif Deleted:
            message = f"🔴اطلاعیه ی زیر حذف شد🔴 \n \n ⬇️ \n  ```{message_text[0][0]}``` "
            await client_bot.send_message(user_id, message, link_preview=False)
            logger.info(f"deleted message notification sent to {user_id}")