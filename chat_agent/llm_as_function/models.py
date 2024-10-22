import json

import openai
from chat_agent.config.global_config import llm_config
from openai import AsyncOpenAI, OpenAI
from rich import print

from .utils import logger

JSON_SCHEMA_PROMPT = """
    You MUST respond with the following JSON schema in Chinese:
    {json_schema}
"""


def chat(
    system_prompt,
    history_messages,
    query,
    model="deepseek-chat",
    max_retry=3,
    temperature=0.5,
    function_messages=[],
    runtime_options={},
    api_key=None,
    openai_base_url=None,
    need_print=True,
):
    client = OpenAI(api_key=api_key, base_url=openai_base_url)
    for retry in range(max_retry):
        try:
            if need_print:
                print("messages:")
                print(
                    [{"role": "system", "content": system_prompt}]
                    + history_messages
                    + [{"role": "user", "content": query}]
                    + function_messages
                )
                print("runtime_options:")
                print(runtime_options)
            response = client.chat.completions.create(
                model=model,
                messages= (
                    [{"role": "system", "content": system_prompt}]
                    + history_messages
                    + [{"role": "user", "content": query}]
                    + function_messages
                ),
                temperature=temperature,
                #response_format={"type": "json_object"},
                timeout=llm_config["timeout"],
                **runtime_options,
            )
            return response
        except Exception as e:
            logger.error(e)
            logger.warning(f"Failed {retry} times, retrying...")
            continue
    raise openai.APIConnectionError("Max retry is reached")

