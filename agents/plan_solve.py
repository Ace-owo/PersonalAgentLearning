
# plan-agent
'''
目标明确，任务能提前拆成有顺序的步骤。
先生成计划，再带着前面步骤的结果逐步执行。
'''
import json
from tools import TOOL_DEFINITION, TOOL_REGISTRY
from messages import Messages
from agents.baseagent import BaseAgent

# 单独写一个提示词，来解决返回 计划 的问题
PLANNER_PROMPT = """
你的任务是为用户制定执行计划。
把原问题拆成按顺序执行的步骤，每一步写清楚要做什么。
最后一步根据前面的结果给出完整答案。

只输出一个 JSON 字符串数组。
输出从 [ 开始，以 ] 结束，每个步骤用双引号包裹。
"""

class PlanAndSolve(BaseAgent):

    def run(self,user_input : str):
        plan_messages = self._build_initial_messages(
            user_input,
            extra_system_prompt=PLANNER_PROMPT,
        )

        reply = self.llm.invoke_with_tools(
            [message.to_api_dict() for message in plan_messages], 
            TOOL_DEFINITION,
            tool_choice = "none",
        )

        final_result = []

        plan_text = reply.content
        try:
            steps = json.loads(plan_text)
        except (json.JSONDecodeError, TypeError) as exc:
            raise ValueError(f"计划解析失败，模型未返回合法 JSON 数组: {exc}")

        if not isinstance(steps, list) or not steps:
            raise ValueError("计划为空或格式错误，无法执行")

        step_input = user_input
        for num,step in enumerate(steps,start = 1):
            print(f"第{num}步 {step}")
            step_input = (
                f"原任务：{user_input}\n"
                f"已完成步骤的结果：{final_result}\n"
                f"当前步骤（{num}/{len(steps)}）：{step}"
            )
            step_messages = self._build_initial_messages(
                step_input,
                extra_system_prompt=(
                    "本轮只判断当前步骤是否需要工具。"
                    "需要且有合适工具时发起工具调用，其余情况回复 NO_TOOL。"
                ),
            )

            reply = self.llm.invoke_with_tools(
                [message.to_api_dict() for message in step_messages], 
                TOOL_DEFINITION,
                tool_choice = "auto",
            )

            step_messages = self._handle_tool_calls(reply, step_messages)

            step_messages[0] = Messages(
                role="system",
                content=(
                    f"{self.system_prompt}\n\n"
                    "完成当前步骤，使用已有信息及工具返回的结果。"
                    "最后一步结合前面结果给出原任务的完整答案。"
                ),
            )

            reply = self.llm.invoke_with_tools(
                [message.to_api_dict() for message in step_messages], 
                TOOL_DEFINITION,
                tool_choice = "none",
            )

            step_output = reply.content or ""
            final_result.append(step_output)
            print(step_output)

        return final_result[-1] if final_result else ""


