# 一个真正执行的函数、一张按名字查函数的表、一份给模型看的工具说明。
from openai.types.chat import ChatCompletionFunctionToolParam
import os
import httpx
from inspect import Parameter, getdoc, signature
from typing import get_type_hints
from pydantic import ConfigDict, create_model

# 工具注册需要记录参数类型，返回值类型，和工具解析
def add(a : int,b : int) -> int:
    '''计算两个整数的和'''
    return a + b

def multiply(a : int,b : int) -> int:
    '''计算两个整数的积'''
    return a * b

def search(query : str) -> str:
    '''搜索公开网页，返回标题，摘要，链接'''
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return "请在 .env里配置 SERPAPI_API_KEY"

    try:
        response = httpx.get(
            "https://serpapi.com/search.json",
            params = {"engine" : "google" , "q" : query, "api_key" : api_key},
            timeout = 15.0,
        )
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPStatusError as exc:
        return f"搜索失败， HTTP 状态码为 {exc.response.status_code}"
    except httpx.RequestError as exc:
        return f"搜索请求失败 {type(exc).__name__}"
    except ValueError as exc:
        return f"搜索响应解析失败 {type(exc).__name__}"

    results = data.get("organic_results") or []
    summaries = []

    for item in results:
        title = item.get("title")
        link = item.get("link")
        snippet = item.get("snippet")

        if not title or not link or not snippet or title == link:
            continue

        summaries.append(f"{title}\n{link}\n{snippet}")

        if len(summaries) == 3:
            break

    return "\n\n".join(summaries) or "没有找到网页结果"

TOOL_REGISTRY = {}
TOOL_DEFINITION : list[ChatCompletionFunctionToolParam] = []

class Tool:
    def __init__(self, function):
        self.function = function
        self.name = function.__name__
        self.description = getdoc(function) or ""

        hints = get_type_hints(function) # 读取函数类型的注解， 参数和返回值
        fields = {}

        for param in signature(function).parameters.values():
            if param.kind not in (
                Parameter.POSITIONAL_OR_KEYWORD,
                Parameter.KEYWORD_ONLY,
            ):
                raise TypeError(f"{self.name}.{param.name} 必须能传入参数名")

            # 整理每个参数的类型和默认值
            default = ... if param.default is Parameter.empty else param.default
            fields[param.name] = (hints[param.name], default)

        # 把 fields 变成模型能读的参数表
        args_model = create_model(
            f"{self.name}Argments",
            __config__=ConfigDict(extra = "forbid"),
            **fields,
        )
        self.parameters = args_model.model_json_schema()

    def to_definition(self) -> ChatCompletionFunctionToolParam:
        return {
            "type" : "function",
            "function" : {
                "name" : self.name,
                "description" : self.description,
                "parameters" : self.parameters,
            },
        }


registered_tools = [Tool(add), Tool(multiply), Tool(search)]
TOOL_REGISTRY = {tool.name: tool.function for tool in registered_tools}
TOOL_DEFINITION = [tool.to_definition() for tool in registered_tools]


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    print(search("claude是什么"))