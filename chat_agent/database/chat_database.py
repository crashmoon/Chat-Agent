import copy
import datetime
import json
import re
import time
from collections import defaultdict, deque

import pymongo
import requests
from bs4 import BeautifulSoup
from bson.objectid import ObjectId
from chat_agent.config.global_config import mongo_config
from chat_agent.utils.logger import logger


class ChatDatabase:
    def __init__(self, url=mongo_config["url"]):
        self.client = pymongo.MongoClient(url)
        self.database = self.client["chat_database"]
        '''
        Chat {
            _id                 String
            name                String
            chat_memo           JSON
        }
        '''
        self.chat_table = self.database["chat_table"]
        try:
            self.chat_table.create_index([('name', pymongo.ASCENDING)])  # 从小到大
        except Exception as e:
            logger.error(f"create_index: {e}")

    def reset_chat(self):
        while True:
            try:
                self.chat_table.delete_many({})
            except Exception as e:
                logger.error(f"reset_chat: {e}")
                time.sleep(1)
                continue
            else:
                logger.info("reset_chat success!")
                return

    def save_chat(self, name, chat_memo):
        while True:
            try:
                self.chat_table.update_one(
                    {"name": name},
                    {"$set": {
                        "chat_memo": chat_memo,
                    }},
                    upsert=True,
                )
            except Exception as e:
                logger.error(f"save_chat: {e}")
                time.sleep(1)
                continue
            else:
                logger.info(f"save_chat success, name={name}")
                return

    def delete_chat_by_name(self, name):
        while True:
            try:
                self.chat_table.delete_one({"name": name})
            except Exception as e:
                logger.error(f"delete_chat_by_name: {e}")
                time.sleep(1)
                continue
            else:
                logger.info(f"delete_chat_by_name success, name={name}")
                return

    def get_chat_by_name(self, name):
        while True:
            try:
                chat = self.chat_table.find_one({"name": name})
                if chat is None:
                    logger.warning("get_chat_by_name: chat not found")
                    return None
                return chat["chat_memo"]
            except Exception as e:
                logger.error(f"get_chat_by_name: {e}")
                time.sleep(1)
                continue

    def save_json(self, the_path, the_json):
        with open(the_path, 'w', encoding='utf-8') as f:
            json.dump(the_json, f, ensure_ascii=False, indent=4)

    def get_all_chat(self):
        while True:
            try:
                chat_list = self.chat_table.find({}, {"_id": 0})
                if chat_list is None:
                    logger.warning("get_all_chat: chat_list not found")
                    return []
                return list(chat_list)
            except Exception as e:
                logger.error(f"get_all_chat: {e}")
                time.sleep(1)
                continue

    def export_chat(self):
        chat_list = self.get_all_chat()
        self.save_json(mongo_config["chat_path"], chat_list)
        logger.info(f"export_chat success")


if __name__ == "__main__":
    chat_database = ChatDatabase()
    chat_database.export_chat()



