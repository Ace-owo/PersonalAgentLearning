# 实现模型的重复调用，边行动边决定下一步
'''
下一步要看上一步查到了什么才能决定。 
适合资料探索、故障排查、工具失败后调整参数或换工具。
'''

import json
from tools import TOOL_DEFINITION, TOOL_REGISTRY
from messages import Messages
from agents.baseagent import BaseAgent

class ReactAgent(BaseAgent):

    def run(self, user_input : str, max_tool_rounds : int = 3) -> str | None:

        messages : list[Messages] = self._build_initial_messages(user_input)

        for round_index in range(max_tool_rounds):
            reply = self.llm.invoke_with_tools(
                [message.to_api_dict() for message in messages],
                TOOL_DEFINITION,
                tool_choice = "auto",
            )

            if not reply.tool_calls:
                return reply.content or ""

            messages = self._handle_tool_calls(reply, messages)

        # 达到工具上线后 基于已有结果生成最终回答
        final_reply = self.llm.invoke_with_tools(
            [message.to_api_dict() for message in messages],
            TOOL_DEFINITION,
            tool_choice = "none",
        )

        return final_reply.content or ""

            