# 一个真正执行的函数、一张按名字查函数的表、一份给模型看的工具说明。
from openai.types.chat import ChatCompletionFunctionToolParam

def add(a : int,b : int) -> int:
    return a + b

def multiply(a : int,b : int) -> int:
    return a * b

TOOL_REGISTRY = {
    "add" : add,
    "multiply" : multiply,
}

TOOL_DEFINITION : list[ChatCompletionFunctionToolParam] = [
    {
        "type" : "funcion",
        "function" : {
            "name" : "add",
            "description" : "计算两个整数的和",
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "a" : {"type" : "inteagr"},
                    "b" : {"type" : "inteagr"},
                },
                "required" : ["a", "b"],
                "additionalProperties" : False,
            },
        },
    },
    {
        "type" : " function",
        "function" : {
            "name" : "multiply",
            "description" : "两个整数相乘",
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "a" : {"type" : "inteagr"},
                    "b" : {"type" : "inteagr"},
                },
                "required" : ["a", "b"],
                "additionalProperties": False,
            },
        },
    }
]

if __name__ == "__main__":
    arguments = {"a": 15, "b": 32}
    result = TOOL_REGISTRY["add"](**arguments)
    print(result)