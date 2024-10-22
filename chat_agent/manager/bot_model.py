import requests
from bs4 import BeautifulSoup, Comment
from chat_agent.config.global_config import bot_config, llm_config
from chat_agent.llm_as_function.fn_calling import (function_to_name,
                                                   get_argument_for_function,
                                                   parse_function)
from newspaper import Article
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_fixed


class ChatBotAPI:
    def __init__(self):
        self.api_url = bot_config["api_url"]
        self.headers = {
            'Authorization': f'Bearer {bot_config["api_key"]}',
            'Content-Type': 'application/json'
        }

    @retry(stop=stop_after_attempt(2), wait=wait_fixed(1))  # 重试三次，每次间隔2秒
    def _bot_search(self, content):
        payload = {
            "model": bot_config["bot_id_search"],
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": content,
                }
            ]
        }
        response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=llm_config["timeout"])
        response.raise_for_status()
        return response.json()

    # @retry(stop=stop_after_attempt(1), wait=wait_fixed(1))  # 重试三次，每次间隔2秒
    # def _bot_read(self, url):
    #     article = Article(url, language="zh")
    #     article.download()
    #     article.parse()
    #     return dict(
    #         title=article.title.strip(),
    #         content=article.text.strip(),
    #     )


class SearchRequest(BaseModel):
    query: str = Field(description="搜索的内容")
def bot_search(request: SearchRequest):
    """
    调用这个函数可以从互联网检索内容，最好一次搜索一个内容。
    """
    chatbot = ChatBotAPI()
    try:
        return chatbot._bot_search(request.query)["choices"][0]["message"]["content"]
    except Exception as e:
        print(e)
        return None

# class ReadRequest(BaseModel):
#     url: str = Field(description="网页链接")
# def bot_read(request: ReadRequest):
#     """
#     调用这个函数可以读取 URL 的内容。
#     """
#     chatbot = ChatBotAPI()
#     try:
#         return chatbot._bot_read(request.url)
#     except Exception as e:
#         print(e)
#         return None

class AnswerRequest(BaseModel):
    message: str = Field(description="回答的内容")
def bot_answer(request: AnswerRequest):
    """
    调用这个函数把你的回答发送给用户。
    """
    return request.message

class IgnoreRequest(BaseModel):
    reason: str = Field(description="""你保持沉默的原因""")
def bot_ignore(request: IgnoreRequest):
    """
    调用这个函数代表你保持沉默。
    """
    return None



# 使用示例
if __name__ == "__main__":
    pass
    # # 获取搜索结果
    # results = bot_search(SearchRequest(query="云南这周的天气怎么样？"))
    # print(results)

    # 获取特定网页内容
    # url = "https://blog.csdn.net/weixin_44023658/article/details/105843701"
    #content = bot_read(ReadRequest(url=url))
    #print(content)

