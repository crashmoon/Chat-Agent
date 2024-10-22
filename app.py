
import logging
import time
from io import BytesIO

import numpy as np
from chat_agent.config.global_config import mongo_config
from chat_agent.database.chat_database import ChatDatabase
from chat_agent.manager.chat_model import ChatModel
from chat_agent.utils.utils import replace_newlines
from PIL import Image
from wxpyit import *

logging.basicConfig(level=logging.INFO)
chat_database = ChatDatabase()
chat_model = ChatModel(chat_database=chat_database)

bot = Bot(
    cache_path="wechat.pkl",
    console_qr=False,
    qr_callback=None,
    login_callback=None,
    logout_callback=None
)

print(bot.friends())
@bot.register(bot.friends())
def reply_all_friends(msg):
    try:
        sender_name = msg.sender.name  # 获取发送者的名称
        my_friend = bot.friends().search(sender_name)[0]
        reply = chat_model.get_reply(context={"from_user_id": sender_name}, query=msg.text)
        if reply is not None:
            reply = replace_newlines(reply)
            my_friend.send(reply)
    except Exception as e:
        logging.error(f"Error processing message from {msg.sender.name}: {e}")
        return "Sorry, something went wrong."


bot.join()