import asyncio
import copy
import datetime
import json
import time
from typing import List

import aiohttp
import numpy as np
import requests
from chat_agent.config.global_config import llm_config
#from chat_agent.embedding.hnsw_model import HnswModel
from chat_agent.llm_as_function.fn_calling import (function_to_name,
                                                   get_argument_for_function,
                                                   parse_function)
from chat_agent.llm_as_function.llm_func import LLMFunc
from chat_agent.utils.logger import logger
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, Field
from rich import print


# 所有方法均为异步
class LLM_Model:
    def __init__(self, llm_model_name=None):
        self.llm_model_name = llm_config["llm_model_name"] if llm_model_name is None else llm_model_name
        logger.info(f"Using LLM model: {self.llm_model_name}")
        self.llm = LLMFunc(
            temperature=llm_config["temperature"],
            model=self.llm_model_name,
            openai_api_key=llm_config["openai_key"],
            openai_base_url=llm_config["openai_base_url"],
            need_print=llm_config["need_print"],
        )
        self.reset_history()

    def reset_history(self):
        self.llm.reset_history()

    def get_function_info(self):
        return self.llm.function_info_list

    def run(self, query, output_schema, system_prompt, open_history=False, use_func=False):
        return self.llm.run(
            query=query,
            output_schema=output_schema,
            system_prompt=system_prompt,
            open_history=open_history,
            use_func=use_func,
        ).unpack()

    def set_history_messages(self, history_messages):
        self.llm.set_history_messages(history_messages)

    def get_history_messages(self):
        return self.llm.history_messages

