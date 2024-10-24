import asyncio
import copy
import datetime
import json
import os
import time
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List

import aiohttp
import numpy as np
import pytz
import requests
from chat_agent.config.global_config import cot_config, llm_config
from chat_agent.llm_as_function.fn_calling import (function_to_name,
                                                   get_argument_for_function,
                                                   parse_function)
from chat_agent.llm_as_function.llm_func import LLMFunc
from chat_agent.manager.bot_model import (AnswerRequest, IgnoreRequest,
                                          SearchRequest, bot_answer,
                                          bot_ignore, bot_search)
from chat_agent.utils.logger import logger
from chat_agent.utils.utils import (filter_words,
                                    run_in_threads_and_collect_results)
from pydantic import BaseModel, Field
from rich import print


class CotSchema(BaseModel):
    thought: str = Field(description="""
        一步一步分析并且思考用户的话，并且给出如何回复或解决用户问题的详细计划。
    """)
    action: str = Field(description="""
        调用的函数名称。(e.g. "bot_search" or "bot_answer")
    """)
    action_input: dict = Field(description="""
        传入函数的内容。
    """)

# 调用函数的输入参数，格式为 JSON 字符串。

class COT_Model:
    def __init__(self, chat_memo=None, llm_model_name=None):
        self.llm_model_name = llm_config["llm_model_name"] if llm_model_name is None else llm_model_name
        logger.info(f"Using LLM model: {self.llm_model_name}")
        self.llm = LLMFunc(
            temperature=llm_config["temperature"],
            model=self.llm_model_name,
            openai_api_key=llm_config["openai_key"],
            openai_base_url=llm_config["openai_base_url"],
            need_print=llm_config["need_print"],
        )
        self.chat_summary = ""
        self.reset_history()
        if chat_memo is not None:
            self.chat_summary = chat_memo["chat_summary"]
            self.set_history_messages(chat_memo["history_messages"])
        self.system_prompt = cot_config["system_prompt"].format(
                chat_summary=self.chat_summary,
                parse_function_bot_search=parse_function(bot_search),
                #parse_function_bot_read=parse_function(bot_read),
                parse_function_bot_answer=parse_function(bot_answer),
                parse_function_bot_ignore=parse_function(bot_ignore),

            )

    def reset_history(self):
        self.llm.reset_history()

    def set_history_messages(self, history_messages):
        self.llm.set_history_messages(history_messages)

    def get_history_messages(self):
        return self.llm.history_messages

    def run(self, query, output_schema, system_prompt, open_history=True, use_func=False):
        return self.llm.run(
            query=query,
            output_schema=output_schema,
            system_prompt=system_prompt,
            open_history=open_history,
            use_func=use_func,
        ).unpack()

    def get_chat_memo(self):
        return dict(
            chat_summary=self.chat_summary,
            history_messages=self.get_history_messages(),
        )

    def active_thinking(self):
        now = datetime.now(pytz.utc)
        utc_8 = now.astimezone(pytz.timezone('Asia/Shanghai'))
        system_time = utc_8.strftime("%Y-%m-%d %H:%M:%S")  # 格式化为字符串
        query = cot_config["active_prompt"].format(system_time=system_time)
        for _ in range(cot_config["max_round"]):
            try:
                cot_info = self.run(query, CotSchema, self.system_prompt, open_history=True, use_func=False)
                logger.info(f"cot_info: {cot_info}")
                if cot_info["action"] == "bot_answer":
                    function_name = cot_info["action"]
                    function_args = AnswerRequest(**cot_info["action_input"])
                    return bot_answer(function_args)
                elif cot_info["action"] == "bot_search":
                    function_name = cot_info["action"]
                    function_args = SearchRequest(**cot_info["action_input"])
                    observation = bot_search(function_args)
                    query = cot_config["continue_prompt"].format(tool_message=observation)
                    logger.info(f"observation: {observation}")
                    continue
                elif cot_info["action"] == "bot_ignore":
                    function_name = cot_info["action"]
                    function_args = IgnoreRequest(**cot_info["action_input"])
                    return bot_ignore(function_args)
                else:
                    logger.error(f"Invalid action: {cot_info['action']}")
                    return cot_info
            except Exception as e:
                logger.error(f"Failed to run COT: {e}")
                return None

    def run_cot(self, user_name, query, is_group=False, is_at=False):
        now = datetime.now(pytz.utc)
        utc_8 = now.astimezone(pytz.timezone('Asia/Shanghai'))
        system_time = utc_8.strftime("%Y-%m-%d %H:%M:%S")  # 格式化为字符串
        if is_group:
            if is_at:
                query = cot_config["query_prompt_group_at"].format(system_time=system_time, user_name=user_name, user_message=query)
            else:
                query = cot_config["query_prompt_group"].format(system_time=system_time, user_name=user_name, user_message=query)
        else:
            query = cot_config["query_prompt"].format(system_time=system_time, user_name=user_name, user_message=query)
        for _ in range(cot_config["max_round"]):
            try:
                cot_info = self.run(query, CotSchema, self.system_prompt, open_history=True, use_func=False)
                logger.info(f"cot_info: {cot_info}")
                if cot_info["action"] == "bot_answer":
                    function_name = cot_info["action"]
                    function_args = AnswerRequest(**cot_info["action_input"])
                    return bot_answer(function_args)
                elif cot_info["action"] == "bot_search":
                    function_name = cot_info["action"]
                    function_args = SearchRequest(**cot_info["action_input"])
                    observation = bot_search(function_args)
                    query = cot_config["continue_prompt"].format(tool_message=observation)
                    logger.info(f"observation: {observation}")
                    continue
                elif cot_info["action"] == "bot_ignore":
                    function_name = cot_info["action"]
                    function_args = IgnoreRequest(**cot_info["action_input"])
                    return bot_ignore(function_args)
                else:
                    logger.error(f"Invalid action: {cot_info['action']}")
                    return cot_info
            except Exception as e:
                logger.error(f"Failed to run COT: {e}")
                return None


if __name__ == "__main__":
    from chat_agent.config.global_config import mongo_config
    from chat_agent.database.chat_database import ChatDatabase
    chat_database = ChatDatabase()
    cot_model = COT_Model()
    cot_model.run_cot("搜索周杰伦最近的新闻")




