# 实现agent基本发方法
from abc import ABC, abstractmethod
from messages import Messages
from tools import TOOL_DEFINITION, TOOL_REGISTRY
import json


SYSTEM_PROMPT = """
你是我的个人助手。默认用中文，帮助我理解问题、获取信息和完成任务。按我本次指定的范围和格式交付结果。

**理解任务**

先明确用户要得到的结果。已有信息足以交付，且任务只需要解释、分析或生成内容时，直接完成。
任务还需要获取信息、验证事实或执行操作时，先确定当前缺少什么。

**选择工具**

从程序为本轮提供的工具中选择。根据工具说明里的用途、
使用条件、所需参数和返回结果，选择能直接满足当前需要的工具。
用户指定来源或操作方式时，将其作为选择条件。

优先用用户已提供的信息、当前上下文和已确认的工具结果填写参数。
缺少会影响结果的必要参数时，先从已有信息中查找，仍无法确定再问一个具体的问题。
当前工具无法满足要求时，完成可交付的部分，并说明还需要什么能力或信息。

**根据工具结果推进**

每次收到工具结果后，核对操作状态以及结果是否满足任务需要。
下一步依赖这个结果时，用实际返回的内容确定下一步和参数。
结果不完整且有可行的补充方法时，调整输入或换用合适的工具。
遇到当前无法解决的错误时，说明具体障碍。
满足用户要求后结束工具调用。根据实际结果说明已完成的操作、已确认的信息和仍待解决的问题。

**交付答案**

先给结论或结果，再按需要补充依据。
多个问题逐项回答。
讲解代码时，指出具体位置、解释数据如何变化，并给出验证方法。
引用外部资料时，提供实际获取的出处。

"""

class BaseAgent(ABC):
    def __init__(self, llm, system_prompt : str = SYSTEM_PROMPT):
        self.llm = llm
        self.system_prompt = system_prompt

    def _build_initial_messages(self, user_input : str) -> list[Messages]:
        return [
            Messages(role = "system", content = self.system_prompt),
            Messages(role = "user", content = user_input),
        ]

    def _build_initial_messages(
        self,
        user_input : str,
        extra_system_prompt : str = ""
    ) -> list[Messages]:
        system_prompt = self.system_prompt

        if extra_system_prompt:
            system_prompt = f"{system_prompt}\n\n{extra_system_prompt}"

        return [
            Messages(role = "system", content = system_prompt),
            Messages(role = "user", content = user_input)
        ]

    def _handle_tool_calls(
        self, reply, messages: list[Messages]
    ) -> list[Messages]:
        if not reply.tool_calls:
            return messages

        # 先保存助手发出的工具请求
        messages.append(Messages.model_validate(
            reply.model_dump(include={"role", "content", "tool_calls"})
        ))

        # 再执行每个工具，并写回与请求 ID 对应的结果
        for call in reply.tool_calls:
            name = call.function.name
            tool = TOOL_REGISTRY.get(name)

            if tool is None:
                result = f"工具未注册: {name}"
            else:
                try:
                    arguments = json.loads(call.function.arguments)
                    result = tool(**arguments)
                except (ValueError, TypeError) as exc:
                    result = f"工具参数错误: {exc}"

            print(f"工具调用 {name} -> {result}")
            messages.append(Messages(
                role="tool",
                tool_call_id=call.id,
                content=str(result),
            ))

        return messages

    @abstractmethod
    def run(self, user_input : str) -> str:
        '''根据用户输入，返回最终回答'''
        raise NotImplementedError
