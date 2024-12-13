import ahocorasick
from db import retrieve_all_keywords, retrieve_message
from configuration import client_bot, desired_channel


def generate_link(id):
    """generate message's link using their id.

    Args:
        id(int): the message's id.
    """
    return f"https://t.me/{desired_channel.split("@")[1]}/{id}"



async def search(event, New=False, Updated=False, Deleted=False):
    automaton = ahocorasick.Automaton()

    keywords = await retrieve_all_keywords()
    keywords = [(keyword[0], keyword[1].strip()) for keyword in keywords]
    

    for user_id, key in keywords:
        automaton.add_word(key, (user_id, key))  # Include user_id in the payload

    automaton.make_automaton()
    try :
        message_text = event.message.message 
        text = ' '.join(message_text.split()) #removing extra spaces.
    except :
        message_id = event.deleted_id
        message_text = await retrieve_message(message_id)
        if message_text:
            message = message_text[0][0]
            text = ' '.join(message.split()) #removing extra spaces.
        else:
            return


    results = {}


    for end_index, (user_id, matched_keyword) in automaton.iter(text):#iter throw the text you wanna find.
        if user_id not in results:
            results[user_id] = matched_keyword
    
    for user_id, matched_keyword in results.items():
        if New:
            message = f"کلمه کلیدی `{matched_keyword}` در پیام زیر مشاهده گردید : \n \n ⬇️ \n ```{message_text}``` \n  [لینک اطلاعیه]({generate_link(event.id)}) "
            await client_bot.send_message(user_id, message, link_preview=False)
        elif Updated:
            message = f"⚠️اطلاعیه ی زیر ویرایش شد⚠️ \n \n ⬇️ \n ```{message_text}``` \n  **[لینک اطلاعیه]**({generate_link(event.id)})"
            await client_bot.send_message(user_id, message, link_preview=False)
        elif Deleted:
            message = f"🔴اطلاعیه ی زیر حذف شد🔴 \n \n ⬇️ \n  ```{message_text[0][0]}``` "
            await client_bot.send_message(user_id, message, link_preview=False)

