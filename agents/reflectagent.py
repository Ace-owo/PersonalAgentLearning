 # reflection agent

'''
已经能产出初稿，但交付前还需要按明确标准检查和改进。
适合代码优化、报告审查、内容润色。
'''

import json
from tools import TOOL_DEFINITION, TOOL_REGISTRY
from messages import Messages
from agents.baseagent import BaseAgent

class ReflectAgent(BaseAgent):

    def run(self, user_input : str, max_rounds : int = 5):
        messages = self._build_initial_messages(user_input)

        draft_reply = self.llm.invoke_with_tools(
            [msg.to_api_dict() for msg in messages],
            TOOL_DEFINITION,
            tool_choice="auto",
        )

        if draft_reply.tool_calls:
            messages = self._handle_tool_calls(draft_reply, messages)
            draft_reply = self.llm.invoke_with_tools(
                [msg.to_api_dict() for msg in messages],
                TOOL_DEFINITION,
                tool_choice="none",
            )

        draft = draft_reply.content
        if not draft or not draft.strip():
            raise ValueError("模型没有生成初稿")

        messages.append(Messages(role="assistant", content=draft))

        for _ in range(max_rounds):
            # 2. 审阅当前稿件
            messages.append(Messages(
                role = "user",
                content = (
                    "请对照原始任务审阅最新稿件，检查是否遗漏要求，"
                    "以及有没有逻辑或计算错误。"
                    "符合要求时只回复 PASS，需要改进时给出具体修改意见。"
                ),
            ))

            review_reply = self.llm.invoke_with_tools(
                [msg.to_api_dict() for msg in messages],
                TOOL_DEFINITION,
                tool_choice = "none",
            )

            feedback = (review_reply.content or "").strip()

            if not feedback:
                raise ValueError("模型没有返回审阅意见")
            if feedback == "PASS":
                break

            # 3. 加入意见，再让模型修订
            messages.append(Messages(role = "assistant", content = feedback))
            messages.append(Messages(
                role = "user",
                content = "请根据刚才的审阅意见修订最新稿件，输出符合原任务要求的完整修订版。",
            ))

            revised_reply = self.llm.invoke_with_tools(
                [msg.to_api_dict() for msg in messages],
                TOOL_DEFINITION,
                tool_choice = "none",
            )

            revised = revised_reply.content

            if not revised or not revised.strip():
                raise ValueError("模型没有返回修订稿")

            draft = revised
            messages.append(Messages(role = "assistant", content = draft))

        return draft

