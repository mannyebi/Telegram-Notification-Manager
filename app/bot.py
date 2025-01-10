from telethon import events, Button
from configuration import client_bot, client_user, desired_channel
from telethon.tl.types import PeerUser, PeerChat
from db import add_user, add_keyword, retireve_keywords, retireve_keyword, delete_keyword, add_newMessage, update_message, delete_message, count_user_keywords
import datetime
from keyword_matches import search
import os
import logging


logger = logging.getLogger(__name__)


user_state = {}
keyword_limit = int(os.getenv("keyword_limit", 5))
add_keyword_btn_inline = [
        [Button.inline("➕ اضافه کردن کلمه کلیدی", b"add_keyword_btn")]
]


async def generate_keyword_list(user_id):
    """Generate a list of keywords for user requested

    Args:
        user_id(int): the id of the user

    Returns:
        list:returns list contains button of keywords.
    """
    keywords = await retireve_keywords(user_id)
    keyword_buttons = []
    for idx, keyword in enumerate(keywords, start=1):
        numberEmoji = number_to_emoji(idx)
        button = Button.inline(f"{numberEmoji} - {keyword[1].strip()}", f"keyword_menu:{keyword[0]}")
        if idx % 2 == 1:  # Start a new row on odd index
            keyword_buttons.append([button])
        else:  # Add to the last row for even index
            keyword_buttons[-1].append(button)
    return keyword_buttons



async def repetitive_or_not(New_keyword, user_id):
    """Checks if the keyword is repetitive for that user or not.

    Args:
        New_keyword(str): the keyword which user wants to add.
        user_id(int): the Id of the user.

    Returns:
        bool: False if repetitive, True if not repetitive.
    """
    fetched_keywords = await retireve_keywords(user_id)
    user_keyowrds = [keyword[1].strip() for keyword in fetched_keywords]
    if New_keyword.strip() in user_keyowrds:
        return False
    else:
        return True



def number_to_emoji(number):
    """Return the emoji of the number

    Args: 
        number(int): the number you want to convert to emoji.

    Returns:
        string: the emoji of the number.
    """

    Number_to_emoji = {
        1:"1️⃣",
        2:"2️⃣",
        3:"3️⃣",
        4:"4️⃣",
        5:"5️⃣",
        6:"6️⃣",
        7:"7️⃣",
        8:"8️⃣",
        9:"9️⃣",
        10:"1️⃣0️⃣",
        11:"1️⃣1️⃣",
        12:"1️⃣2️⃣",
        13:"1️⃣3️⃣",
        14:"1️⃣4️⃣",
        15:"1️⃣5️⃣",
        16:"1️⃣6️⃣",
        17:"1️⃣7️⃣",
        18:"1️⃣8️⃣",
        19:"1️⃣9️⃣",
        20:"2️⃣0️⃣",
    }
    return Number_to_emoji.get(number)



async def keyword_actions(event, keyword_id):
    """show some option for opertaing on keywords

    Args:
    event(telethon_event): -
    keyword_id(int): the keyword's Id
    """
    options = {"Delete":"❌حذف"}
    buttons = []
    for option in options:
        button = Button.inline(options.get(option), f"{option}:{keyword_id}")
        buttons.append(button)
    keyword = await retireve_keyword(keyword_id)
    await event.edit(f"میخوای با کلمه ی کلیدی `{keyword[0][1].strip()}` چیکار کنی ؟", buttons=buttons)



def decodeData(data):
    """docde data.

    Args:
        data(str): the data you wan to decode.

    Returns:
        str: Decoded data
    """
    return data.decode()
    


async def check_keyword_limit(user_id):
    """check if the user's keywords count are above the limit or not.

    Args:
        user_id(int): the id of the user.
    
    Returns:
        bool: Returns True if keywords count is under the limit and False if above the limit.
    """
    user_keyword_counts = [count[0] for count in await count_user_keywords(user_id)][0]
    if user_keyword_counts >= keyword_limit:
        return False
    else:
        return True



@client_bot.on(events.CallbackQuery)
async def callback_handler(event):
    """call the specific function of each callback.

    Args:
        event: the event which carries the call back data.
    """

    data = decodeData(event.data)
    

    if event.data == b"add_keyword_btn": #Dialog that make user aware of how to add a keyword
        await keyword_adding_dialog(event)
        logger.info("add keywrod button got pushed by %s", event.sender_id)

    elif data.startswith("save_keyword"): #Save recieved keyword
        keyword = data.split("save_keyword:")[1]
        check_repetitive = await repetitive_or_not(keyword, event.sender_id)
        if await check_keyword_limit(event.sender_id):
            if check_repetitive:
                result = await add_keyword(keyword, event.sender_id)
                if result:
                    keywords_list_buttons = await generate_keyword_list(event.sender_id)
                    await event.edit("کلمه کلیدی با موفقیت اضافه شد ✅", buttons=keywords_list_buttons)
                    logger.info("save keyword button pushed by %s and keyword added succesfully.", event.sender_id)
                else:
                    await event.edit("مشکلی پیش آمده ⚠️")
                    logger.exception("a problem occured while saving keyword !")
            else:
                await event.edit("این کلمه ی کلیدی قبلا ثبت شده است. ⚠️", buttons=add_keyword_btn_inline)
        else:
            await event.edit("شما از همه ی محدودیت کلمات کلیدی استفاده کرده اید ⚠️")
            


    elif data.startswith("keyword_menu"): #Show a keyword's options ->  حذف
        keywordid = data.split("keyword_menu:")[1]
        await keyword_actions(event, keywordid)

    elif data.startswith("Delete"):
        keyword_id = data.split("Delete:")[1]
        result = await delete_keyword(keyword_id)
        if result:
            keywords_list_buttons = await generate_keyword_list(event.sender_id)
            await event.edit("کلمه کلیدی با موفقیت حذف شد ✅", buttons=keywords_list_buttons)
            logger.info("keyword successfully deleted by user %s", event.sender_id)
        else:
            await event.edit("مشکلی پیش آمده.")
            logger.exception("An ERROR occured while deleting keyword by user %s", event.sender_id)

    elif data.startswith("add_again"):
        await keyword_adding_dialog(event)

            


@client_bot.on(event=events.NewMessage(pattern='/start'))
async def handle_start_command(event):
    """Create a user record if not exists after receiving /start command . show the welcome text
    Args:
        Event : ...
    """
    sender = await event.get_sender()
    #create user's record in database
    chat_id = event.message.peer_id
    first_name = sender.first_name if sender.first_name is not None else ""
    last_name = sender.last_name if sender.last_name is not None else ""

    if isinstance(chat_id, (PeerUser, PeerChat)):
        await client_bot.send_message(chat_id, f"""**سلام {first_name} {last_name} عزیز** \n اسم اساتید یا واحد هات رو به عنوان کلمه ی کلیدی اضافه کن. هر اطلاعیه ی جدیدی مطابق با کلمات کلیدی ثبت شده ی شما در کانال دانشگاه گذاشته شود این ربات به شما خبر میدهد 😉""", 
        buttons=add_keyword_btn_inline)

        result = await add_user(sender.id, sender.username, sender.first_name, sender.last_name, sender.phone)
        if result:
            logger.info('user added succesfully to database')
        else:
            logger.exception("an ERROR occured while adding user to database !")
    
    else:
        logger.warning("but started in a place which is not a user chat!")



async def keyword_adding_dialog(event):
    global user_state
    user_state[event.sender_id] = "waiting_for_keyword"
    try:
        await event.edit("کلمه کلیدی مد نظرت رو بعد از این پیام بنویس : ⬇️")
    except:
        await event.respond("کلمه کلیدی مد نظرت رو بعد از این پیام بنویس : ⬇️")



@client_bot.on(events.NewMessage)
async def handle_new_message(event):
    user_id = event.sender_id
    
    if user_state.get(user_id) == "waiting_for_keyword":
        keyword = event.message.text
        user_state[event.sender_id] = None
        buttons = [
            [ Button.inline("🟡 نه منصرف شدم", f"add_again") , Button.inline("✅ ثبت کلمه کلیدی", f"save_keyword:{keyword}")]
        ]
        await event.respond(f"کلمه کلیدی دریافت شد: {keyword}", buttons=buttons)

    elif event.message.text == "لیست کلمات کلیدی 📃":
        
        keyword_buttons = await generate_keyword_list(event.sender_id)
        if len(keyword_buttons) > 0:
            await client_bot.send_message(event.sender_id, "کلمات کلیدی شما :" ,buttons=keyword_buttons)
        else:
            await client_bot.send_message(event.sender_id, "شما هیچ کلمه ی کلیدی ثبت نکرده اید !" ,buttons=add_keyword_btn_inline)

    elif event.message.text == "➕ اضافه کردن کلمه کلیدی":
        await keyword_adding_dialog(event)

    elif event.message.text == "یه قهوه مهمونم کن ☕":
        button = Button.url("☕خرید قهوه", "http://www.coffeete.ir/MANNY")
        await event.respond("بعد از کلیک روی دکمه خرید قهوه وارد سایت خرید قهوه میشی. خوشحال میشم اگه اسمت رو توی بخش توضیحات بنویسی ❤️", buttons=button)
        logger.info("user %s clicked on DONATE button", event.sender_id)




@client_bot.on(event=events.NewMessage(pattern="/menu"))
async def menu(event):
    """a menu which displays some menu buttons
    """
    buttons = [
        [Button.text("➕ اضافه کردن کلمه کلیدی", resize=True), Button.text("لیست کلمات کلیدی 📃", resize=True)],[Button.text("یه قهوه مهمونم کن ☕", resize=True)]
    ]
    await event.respond("📃", buttons=buttons)





@client_user.on(events.NewMessage(chats=desired_channel))
async def new_message_handler(event):
    logger.info("New message from %s tracked.", desired_channel)
    try:
        result = await add_newMessage(event.id, event.message.message, "new", datetime.datetime.now())
        if result:
            logger.info("The message added to database successfully.")
            await search(event, New=True)
            logger.info("The sent to searching algorithm.")
        else:
            logger.exception("an ERROR occured while adding message to database")

    except Exception as e:
        logger.exception("ERROR occured in one of [reading - adding to db - sending to search()] setps (new_message_handler) -> %s", e)



@client_user.on(events.MessageEdited(chats=desired_channel))
async def edited_message_handler(event):
    logger.info("An edited message from %s tracked.", desired_channel)
    try:
        result = await update_message(event.id, event.message.message, "new", datetime.datetime.now())

        if result:
            logger.info("message status and date update in database to UPDATED.")
            await search(event, Updated=True)
            logger.info("Updated message sent to searching algorithm.")
        else:
            logger.exception("an ERROR occured while updating and edited message to database.")

    except Exception as e:
        logger.exception("ERROR occured in one of [reading - adding to db - sending to search()] setps (edited_message_handler) -> %s", e)
    await update_message(event.id, event.text, "updated", datetime.datetime.now())



@client_user.on(events.MessageDeleted(chats=desired_channel))
async def deleted_message_handler(event):
    logger.info("A DELETED message from %s tracked.", desired_channel)
    try:
        result = await delete_message(event.deleted_id, datetime.datetime.now())
        if result:
            logger.info("message status and date update in database to DELETED.")
            await search(event, Deleted=True)
            logger.info("DELETED message sent to searching algorithm.")
        else:
            logger.exception("ERROR occured in one of [reading - adding to db - sending to search()] setps (deleted_message_handler) -> %s", e)
    except Exception as e:
        logger.exception("ERROR occured in one of [reading - adding to db - sending to search()] setps (edited_message_handler) -> %s", e)


client_bot.run_until_disconnected()
client_user.run_until_disconnected()