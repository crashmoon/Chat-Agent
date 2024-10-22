import asyncio
import copy
import inspect
import json
from dataclasses import dataclass, field

from chat_agent.llm_as_function.errors import (InvalidFunctionParameters,
                                               InvalidLLMResponse)
from chat_agent.llm_as_function.fn_calling import (function_to_name,
                                                   get_argument_for_function,
                                                   parse_function)
from chat_agent.llm_as_function.models import JSON_SCHEMA_PROMPT, chat
from chat_agent.llm_as_function.utils import (GlobalGPTBin, clean_output_parse,
                                              generate_schema_prompt, logger)
from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletionMessage
from pydantic import BaseModel, ValidationError


@dataclass
class Final:
    pack: dict = None
    raw_response: str = None

    def ok(self):
        return self.pack is not None

    def unpack(self):
        if self.pack is not None:
            return self.pack
        else:
            return self.raw_response


@dataclass
class LLMFunc:
    max_retry: int = 3
    parse_mode: str = "error"
    output_schema: BaseModel = None
    output_json: dict = None
    temperature: float = 0.1
    model: str = "gpt-3.5-turbo-1106"
    openai_api_key: str = None
    openai_base_url: str = None
    async_max_time: int = None
    async_wait_time: float = 0.1
    runtime_options: dict = field(default_factory=dict)
    history_messages: list = field(default_factory=list)
    need_print: bool = False

    def __post_init__(self):
        assert self.parse_mode in [
            "error",
            "accept_raw",
        ], f"Parse mode must in ['error', 'accept_raw'], not {self.parse_mode}"
        self.make_chat = chat
        self.config: dict = dict(
            model=self.model,
            temperature=self.temperature,
            need_print=self.need_print,
        )
        self.config["api_key"] = self.openai_api_key
        self.config["openai_base_url"] = self.openai_base_url
        self._bp_runtime_options = copy.copy(self.runtime_options)
        self.fn_callings = {}
        self.async_models = {}

    def reset(self):
        self.output_schema = None
        self.output_json = None
        self.runtime_options = copy.copy(self._bp_runtime_options)
        self.func_callings = []
        self.fn_callings = {}

    def func(self, func, real_func=None, tool_choice="auto"):
        if real_func is None:
            real_func = func
        self.fn_callings[function_to_name(func)] = real_func

        func_desc = parse_function(func)
        if self.runtime_options.get("tools", None) is None:
            self.runtime_options["tools"] = []
        self.runtime_options["tools"].append(func_desc)
        self.runtime_options["tool_choice"] = "auto"

    def output(self, output_schema):
        self.output_schema = output_schema
        self.output_json = generate_schema_prompt(output_schema)

    def parse_output(self, output, output_schema):
        try:
            json_str = clean_output_parse(output)
            output = output_schema(**json.loads(json_str)).model_dump()
            return Final(pack=output)
        except:
            logger.error(f"Failed to parse output: {output}")
            if self.parse_mode == "error":
                raise InvalidLLMResponse(f"Failed to parse output: {output}")
            elif self.parse_mode == "accept_raw":
                return Final(raw_response=output)
            raise InvalidLLMResponse(f"Failed to parse output: {output}")

    def _form_function_messages(
        self,
        tool_message: ChatCompletionMessage,
        fn_callings={},
        function_messages=[],
    ):
        function_messages = function_messages + [tool_message]
        tool_calls = tool_message.tool_calls
        if tool_calls is None:
            raise ValueError("tool_calls is None")
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            try:
                function_to_call = fn_callings[function_name]
            except KeyError as e:
                logger.error(f"function name is never added: {function_name}")
                raise e

            function_args_json = tool_call.function.arguments
            logger.debug(
                f"Calling function {function_name} with args {function_args_json}"
            )
            validate_type: BaseModel = get_argument_for_function(function_to_call)
            try:
                function_args_parsed = validate_type.model_validate_json(
                    function_args_json
                )
            except (ValueError, ValidationError):
                raise InvalidFunctionParameters(function_name, function_args_json)

            try:
                if inspect.iscoroutinefunction(function_to_call):
                    function_response = asyncio.run(function_to_call(function_args_parsed))
                else:
                    function_response = function_to_call(function_args_parsed)
            except Exception as e:
                logger.error(f"Occur error when running {function_name}")
                raise e

            assert isinstance(
                function_response, str
            ), f"Expect function [{function_name}] to return str, not {type(function_response)}"
            function_messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
        return function_messages

    def _provider_response(
        self,
        system_prompt,
        history_messages,
        query,
        runtime_options={},
        fn_callings={}
    ):
        raw_result: ChatCompletionMessage = (
            self.make_chat(
                system_prompt=system_prompt,
                history_messages=history_messages,
                query=query,
                runtime_options=runtime_options,
                **self.config,
            )
            .choices[0]
            .message
        )
        if raw_result.tool_calls is None:
            return raw_result.content
        else:
            return self._function_call_branch(
                system_prompt=system_prompt,
                history_messages=history_messages,
                query=query,
                tool_message=raw_result,
                runtime_options=runtime_options,
                fn_callings=fn_callings,
            )

    def _function_call_branch(
        self,
        system_prompt,
        history_messages,
        query,
        tool_message: ChatCompletionMessage,
        runtime_options={},
        fn_callings={},
        function_messages=[],
    ):
        function_messages = self._form_function_messages(tool_message, fn_callings, function_messages)
        raw_result: ChatCompletionMessage = (
            self.make_chat(
                system_prompt=system_prompt,
                history_messages=history_messages,
                query=query,
                function_messages=function_messages,
                **self.config,
            ).choices[0].message
        )
        if raw_result.tool_calls is None:
            return raw_result.content
        else:
            return self._function_call_branch(
                system_prompt=system_prompt,
                history_messages=history_messages,
                query=query,
                tool_message=raw_result,
                runtime_options=runtime_options,
                fn_callings=fn_callings,
                function_messages=function_messages,
            )

    def _append_json_schema(self, prompt, output_json):
        append_prompt = JSON_SCHEMA_PROMPT.format(json_schema=output_json)
        return prompt + append_prompt

    def reset_history(self):
        self.history_messages = []

    def set_history_messages(self, history_messages):
        self.history_messages = copy.deepcopy(history_messages)

    def run(self, query, output_schema, system_prompt, open_history=False, use_func=False):
        self.output(output_schema)
        system_prompt=self._append_json_schema(system_prompt, self.output_json)
        history_messages=self.history_messages if open_history else []
        runtime_options=self.runtime_options if use_func else {}
        for _ in range(self.max_retry):
            try:
                raw_result = self._provider_response(
                    system_prompt=system_prompt,
                    history_messages=history_messages,
                    query=query,
                    runtime_options=runtime_options,
                    fn_callings=self.fn_callings,
                )
                result = self.parse_output(raw_result, self.output_schema)
            except Exception as e:
                logger.error(f"Failed to run, retrying: {e}")
                continue
            else:
                self.history_messages.append({"role": "user", "content": query})
                self.history_messages.append({"role": "assistant", "content": raw_result})
                return result
        raise ValueError(f"Failed to run after {self.max_retry} retries")



if __name__ == "__main__":
    from chat_agent.config.global_config import cnfanews_config, llm_config
    llm = LLMFunc(
        temperature=llm_config["temperature"],
        model=llm_config["openai_model_name"],
        openai_api_key=llm_config["openai_key"],
        openai_base_url=llm_config["openai_base_url"],
        need_print=llm_config["need_print"],
    )
    # 测试 llm.run
    query = "强化学习是什么？"
    output_schema = BaseModel
    system_prompt = "你好"
    result = llm.run(query, output_schema, system_prompt)
    #print(re)
