# 实现大模型调用，返回调用结果

import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
from typing import List, Dict

env_path = Path(__file__).with_name(".env")
load_dotenv(env_path)

class LearnAgent:
    def __init__(self,
        model : str = None,
        api_key : str = None,
        base_url : str = None,
    ):
        self.model = model or os.getenv("MODEL_NAME")
        api_key = api_key or os.getenv("MODEL_API_KEY")
        base_url = base_url or os.getenv("BASE_URL")

        if not all([self.model, api_key, base_url]):
            raise ValueError("模型ID、API密钥和服务地址必须被提供或在.env文件中定义。")

        self.client = OpenAI(api_key = api_key, base_url = base_url)

    def invoke(self,messages : List[Dict[str , str]]) -> str:
        print("大模型正在思考")
        try:
            response = self.client.chat.completions.create(
                model = self.model,
                messages = messages,
                stream = True
            )

            print("大模型响应成功")
            collected_content = []
            for each in response:
                if not each.choices:
                    continue
                content = each.choices[0].delta.content or ""
                collected_content.append(content)
            return "".join(collected_content)
        except Exception as e:
            print("大模型思考失败", e)
            return None

# 什么是流式响应? 
    # 传入注册表，让agent寻找
    def invoke_with_tools(self,messages, tools, tool_choice = "auto"):
        response = self.client.chat.completions.create(
            model = self.model,
            messages = messages,
            tools = tools,
            tool_choice = tool_choice,
            stream = False,
        )

        return response.choices[0].message