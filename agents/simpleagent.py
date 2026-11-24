# 实现简单模型调用
'''
问题清楚，能直接回答，
或者一次工具调用就能拿到足够的信息。
适合日常问答、简单计算、查一个明确的事实。
'''
import json
from tools import TOOL_DEFINITION, TOOL_REGISTRY
from messages import Messages
from agents.baseagent import BaseAgent

class SimpleAgent(BaseAgent):

    def run(self, user_input : str) -> str | None:

        messages : list[Messages] = self._build_initial_messages(user_input)

        reply = self.llm.invoke_with_tools(
            [message.to_api_dict() for message in messages], 
            TOOL_DEFINITION,
        )

        if not reply.tool_calls:
            return reply.content or ""

        messages = self._handle_tool_calls(reply, messages)

        final_reply = self.llm.invoke_with_tools(
            [message.to_api_dict() for message in messages],
            TOOL_DEFINITION,
            tool_choice = "none"
        )
    
        return final_reply.content or ""

        

               
