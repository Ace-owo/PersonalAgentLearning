# memory 配置信息
# 保存存储的地址

from pathlib import Path

from pydantic import BaseModel, Field

'''
default=5 表示默认最多返回 5 条。
搜到 3 条就返回 3 条，搜到 8 条就取最新的 5 条。
ge=1 表示值必须大于或等于 1。
'''

class MemoryConfig(BaseModel):
    db_path : Path = Path.home() / ".myagent" / "memort.db"
    search_limit : int = Field(default = 5, ge = 1)
    forget_threshold: float = Field(default=0.3, ge=0.0, le=1.0)