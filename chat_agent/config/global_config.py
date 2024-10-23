import os

import torch
from private_config import Config

current_file_directory = os.path.dirname(os.path.realpath(__file__))


base_config = dict(
    log_path=os.path.join(".", "logs", "log.log"),
    max_repeat_times=3,
)

llm_config = dict(
    openai_base_url = Config.llm_config["openai_base_url"],
    openai_key = Config.llm_config["openai_key"],
    llm_model_name = Config.llm_config["llm_model_name"],
    temperature=0.5,
    max_tokens=1024 * 8,
    need_print=False,
    timeout=60,
    fast_timeout=10,
    JSON_SCHEMA_PROMPT = """
        You MUST respond with the following JSON schema in Chinese:
        {json_schema}
    """,
)

wechat_config = dict(
    group_name_white_list = Config.wechat_config["group_name_white_list"],
)

bot_config = dict(
    api_key = Config.bot_config["api_key"],
    api_url = Config.bot_config["api_url"],
    bot_id_search = Config.bot_config["bot_id_search"],
)

cot_config = dict(
    system_prompt = """
    你的名字叫嘘嘘子, 你是一名能够执行复杂推理的AI助手, 你在协助我和用户聊天, 你和用户历史对话的总结如下：
    {chat_summary}

    你可以使用以下几个函数：
    bot_search(query)：使用此函数可通过输入字符串 query 进行互联网搜索，它返回与查询相关的URL列表或简要摘要，你最好一次搜索一个东西。
    bot_answer(message)：使用此函数可将消息 message 发送给用户。您在完成推理后，使用此函数来给用户提供最终答案。
    bot_ignore(reason): 使用此函数可以保持沉默，不回答用户的问题, reason 是你保持沉默的原因。

    你在回答之前需要思考，一步一步分解问题，
    并且给出回答问题的详细计划，然后按照计划一步一步执行，
    最后，当你认为你已经得到了最终答案时，可以使用 bot_answer 函数给用户发送你的回答，
    否则，请调用函数获得更多信息，并且继续思考。

    请注意：
    你应该主动一点，回复用户的时候要详细一点，还要有感情一点，不要像个机器人一样，你不是机器人，你要幽默一点哦，为用户提供情绪价值。
    你可以主动指出用户的认知存在什么问题，或者分享新的发现和看法。
    Don’t talk so much nonsense. Based on first principles, provide thinking grounded in fundamental logic.

    可用 TOOLS 汇总:
    ------
    You have access to the following tools:
    {parse_function_bot_search}
    {parse_function_bot_answer}
    {parse_function_bot_ignore}
    """,
    query_prompt = """
        现在的时间是<{system_time}>, 用户<{user_name}>说：{user_message}
    """,
    query_prompt_group = """
        现在的时间是<{system_time}>, 用户<{user_name}>在群里说：{user_message}
        群里的发言较多，如果大家没有和你说话，请调用 bot_ignore 保持沉默。
        但是如果用户主动叫你的名字，请回答用户的问题。
        此外，如果用户的认知存在问题，你需要指出。
        在群聊里的发言要尽可能精简，并且要有情感。
    """,
    continue_prompt = """
        以下是函数返回的信息，请仔细阅读：
        -------------------
        {tool_message}
        -------------------
        如果思考好了就调用 bot_answer 回复用户，
        或者调用 bot_ignore 保持沉默，
        否则请继续思考。
    """,
    active_prompt = """
        现在的时间是<{system_time}>
        今天的天气怎么样？今天有什么新闻？
        基于你和用户的聊天内容，作为一个 AI 助手你有什么新的发现或想法？
        请向用户分享你的想法。
    """,
    # allowed_functions = ['bot_search', 'bot_answer', 'bot_ignore'],
    max_round = 10,   # 最长的思考轮数
)

chat_config = dict(
    max_len = 32 * 1024,
    summary_prompt = """
        您是一名善于总结和概括的AI助手。您的任务是阅读一份长篇的聊天记录，并将其内容进行总结，应该包括以下几个方面：
        1.记录用户相关信息、包括用户的性格、偏好、性别、地理位置等等，越详细、越丰富越好。
        2.你和用户聊天内容的总结。
        3.一些其它的，你认为值得记录的东西。
    """
)

mongo_config = dict(
    url="mongodb://localhost:27017/",
    chat_path=os.path.abspath(os.path.join(current_file_directory, "..", "database", "chat_data.json"))
)

hnsw_config = dict(
    space = "cosine",
    dimension = 2048,
    max_elements = int(1e5),
    ef_construction = 200,
    M = 16,
    ef = 50,
)

# audio_config = dict(

# )

