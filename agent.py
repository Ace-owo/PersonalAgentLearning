# 用于组装消息，执行函数调用
import json
from tools import TOOL_DEFINITION, TOOL_REGISTRY

class Agent:
    def __init__(self, llm):
        self.llm = llm

    def run(self, user_input : str = None) -> str | None:
        ''' 
        没有使用工具注册表
        messages = [{"role" : "system", "content" : "你是一个学习助手"},
                    {"role" : "user", "content" : user_input}]
        return self.llm.invoke(messages)
        '''

        messages = [{"role" : "system", "content" : "你是一个学习助手"},
            {"role" : "user", "content" : user_input}]

        reply = self.llm.invoke_with_tools(messages, TOOL_DEFINITION)
        if not reply.tool_calls:
            return reply.content or ""

        '''
        reply.model_dump(...) 把 SDK 返回的对象转成 Python 字典，里面嵌套的工具调用对象也会一起转换。
        include={"role", "content", "tool_calls"} 只保留这三个字段。
        exclude_none=True 跳过值为 None 的字段。比如模型这轮只请求了乘法工具，`reply.content` 是 None，转出的字典就省略 content。
        messages.append(...) 把转换后的字典加到消息列表末尾。
        '''
        messages.append(reply.model_dump(
            include = {"role", "content", "tool_calls"},
            exclude_none = True,
        ))

        for call in reply.tool_calls:
            name = call.function.name
            tool = TOOL_REGISTRY.get(name)

            if tool is None:
                result = f"工具未注册:{name}"
            else:
                try:
                    argments = json.loads(call.function.arguments)
                    result = tool(**argments)
                except (ValueError, TypeError) as exc:
                    result = f"工具参数错误:{exc}"

            print(f"工具调用 {name} -> {result}")
            messages.append({
                "role" : "tool",
                "tool_call_id" : call.id,
                "content" : str(result),
            })

        final_reply = self.llm.invoke_with_tools(
            messages, TOOL_DEFINITION, tool_choice = "none"
        )
        
        return final_reply.content or ""

        

               
