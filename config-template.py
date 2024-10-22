class Config:
    ##################  LLM  #####################
    # 这里是 llm 大模型的 API 配置，推荐使用 deepseek-chat 模型
    # 请参考 https://platform.deepseek.com/
    llm_config = dict(
        openai_base_url = "https://api.deepseek.com",
        openai_key = "xxx",   # <---  这里填你的 key
        llm_model_name="deepseek-chat",
    )

    ################# Search Bot ####################
    # 这里需要配置一个带有联网检索功能的 bot，使用火山引擎
    # 请参考 https://console.volcengine.com/
    bot_config = dict(
        api_key = "xxx",   # <---  这里填你的 key
        api_url = "https://ark.cn-beijing.volces.com/api/v3/bots/chat/completions",
        bot_id_search = "xxx",  # <---  这里填你的 bot id
    )

    ################# WeChat ####################
    # 微信的配置，主要是群名白名单
    wechat_config = dict(
        group_name_white_list = ["ChatAgent测试群"],
    )



