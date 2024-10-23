import asyncio
import datetime
import json
import os
import time
from collections import defaultdict
from typing import List

import numpy as np
import requests
from chat_agent.config.global_config import chat_config, llm_config
from chat_agent.database.chat_database import ChatDatabase
from chat_agent.llm_as_function.llm_func import LLMFunc
from chat_agent.manager.cot_model import COT_Model
from chat_agent.manager.llm_model import LLM_Model
from chat_agent.utils.logger import logger
from chat_agent.utils.utils import (filter_words,
                                    run_in_threads_and_collect_results)
from pydantic import BaseModel, Field
from rich import print


class SummarySchema(BaseModel):
    summary: str = Field(description="""
        在这里输入您的总结内容。
    """)


class ChatModel:
    def __init__(self, chat_database: ChatDatabase):
        self.chat_database = chat_database
        logger.info("chatModel init finished")

    def update_chat_memo(self, name, chat_memo):
        chat_memo = self.make_summary(chat_memo)
        self.chat_database.save_chat(
            name=name,
            chat_memo=chat_memo,
        )

    def get_chat_memo(self, name):
        return self.chat_database.get_chat_by_name(name=name)

    #  chat_summary & history_messages
    def make_summary(self, chat_memo):
        if len(str(chat_memo["history_messages"])) > chat_config["max_len"]:
            llm_model = LLM_Model()
            llm_info = llm_model.run(
                query=f"""
                    {str(chat_memo["chat_summary"])}
                    {str(chat_memo["history_messages"])}
                """,
                output_schema=SummarySchema,
                system_prompt=chat_config["summary_prompt"],
                open_history=False,
                use_func=False,
            )
            chat_memo["chat_summary"] = llm_info["summary"]
            chat_memo["history_messages"] = []
        return chat_memo

    def get_reply(self, user_name, query):
        cot_model = COT_Model(chat_memo=self.get_chat_memo(user_name))
        cot_info = cot_model.run_cot(user_name=user_name, query=query)
        chat_memo = cot_model.get_chat_memo()
        self.update_chat_memo(user_name, chat_memo)
        return cot_info

    def get_reply_for_group(self, user_name, group_name, query):
        cot_model = COT_Model(chat_memo=self.get_chat_memo(group_name))
        cot_info = cot_model.run_cot(user_name=user_name, query=query, is_group=True)
        chat_memo = cot_model.get_chat_memo()
        self.update_chat_memo(group_name, chat_memo)
        return cot_info

    def active_reply(self, name):
        cot_model = COT_Model(chat_memo=self.get_chat_memo(name))
        cot_info = cot_model.active_thinking(user_name=name)
        chat_memo = cot_model.get_chat_memo()
        self.update_chat_memo(name, chat_memo)
        return cot_info



if __name__ == "__main__":
    from chat_agent.config.global_config import mongo_config
    chat_database = ChatDatabase()
    chat_model = ChatModel(
        chat_database=chat_database,
    )
    print(
        chat_model.get_reply(
            context={"from_user_id": "test"},
            query="可以告诉我今天上海的天气吗？",
        )
    )


