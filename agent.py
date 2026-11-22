# 用于组装消息，执行函数调用

class Agent:
    def __init__(self, llm):
        self.llm = llm

    def run(self, user_input : str = None) -> str | None:
        messages = [{"role" : "system", "content" : "你是一个学习助手"},
                    {"role" : "user", "content" : user_input}]
        return self.llm.invoke(messages)
    