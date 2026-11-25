# memory 数据类型

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

MemoryType = Literal["semantic", "episodic"]

class MemoryItem(BaseModel):
    # str_strip_whitespace=True 会去掉普通字符串字段首尾的空白
    model_config = ConfigDict(str_strip_whitespace=True)

    id : str = Field(default_factory = lambda : uuid4().hex)
    user_id : str = Field(min_length = 1)
    session_id : str | None = None
    memory_type : MemoryType
    content : str = Field(min_length = 1)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)


    # `datetime.now(timezone.utc)` 获取创建记录时的 UTC 时间，
    # `.isoformat(timespec="microseconds")` 
    # 把它转成带微秒的字符串，方便存入 SQLite 和排序。
    created_at : str = Field(
        default_factory = lambda: datetime.now(timezone.utc).isoformat(
            timespec = "microseconds"
        )
    )
