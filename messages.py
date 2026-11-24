# 实现对消息的封装, 判断消息是否格式正确
from typing import Literal, Self

from openai.types.chat import ChatCompletionMessageFunctionToolCallParam
from pydantic import BaseModel, model_validator

# 类型注解，表示这个字段的值只能从列出来的几个值里选。
MessageRole = Literal["system", "user", "assistant", "tool"]


class Messages(BaseModel):
    role : MessageRole
    content : str | None = None
    tool_calls : list[ChatCompletionMessageFunctionToolCallParam] | None = None
    tool_call_id : str | None = None

    # model_validator 让你编写同时检查多个字段的校验规则
    # mode="after" 表示 Pydantic 先完成字段自身的类型校验，再运行这段代码
    @model_validator(mode = "after")
    def check_fields(self) -> Self:
        if self.role == "tool" and not self.tool_call_id:
            raise ValueError("工具结果必须包含 tool_call_id")
        if self.role != "tool" and self.tool_call_id is not None:
            raise ValueError("只有工具结果可以包含 tool_call_id")
        if self.role != "assistant" and self.tool_calls is not None:
            raise ValueError("只有助手消息可以包含 tool_calls")
        if self.content is None and not (
            self.role == "assistant" and self.tool_calls
        ):
            raise ValueError("消息必须包含 content，或由助手提出工具调用")

        return self
    def to_api_dict(self) -> dict:
        return self.model_dump(exclude_none = True)

