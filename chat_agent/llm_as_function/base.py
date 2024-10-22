import asyncio
import json
import os
import sys

from chat_agent.llm_as_function.fn_calling import (function_to_name,
                                                   get_argument_for_function,
                                                   parse_function)
from chat_agent.llm_as_function.llm_func import LLMFunc
from pydantic import BaseModel, Field


class Result(BaseModel):
    summary: str = Field(description="The response summary sentence")

class Result2(BaseModel):
    res_list: list = Field(description="把结果写在这个 list 里面")

class GetCurrentWeatherRequest(BaseModel):
    location: str = Field(description="The city and state, e.g. San Francisco, CA")


class GetCurrentTimeRequest(BaseModel):
    location: str = Field(description="The city and state, e.g. San Francisco, CA")


def get_current_weather(request: GetCurrentWeatherRequest):
    """
    Get the current weather in a given location
    """
    weather_info = {
        "location": request.location,
        "temperature": "72",
        "forecast": ["sunny", "windy"],
    }
    return json.dumps(weather_info)


def get_current_time(request: GetCurrentTimeRequest):
    """
    Get the current time in a given location
    """
    time_info = {
        "location": request.location,
        "time": "2024/1/1",
    }
    return json.dumps(time_info)

