# memory_tool 实现记忆的方法
# 保存记忆 读取记忆 遗忘记忆 添加记忆 删除记忆
from .memory_item import MemoryType
from .memory_manager import MemoryManager

'''
   你的设想（还没实现）：
     记忆的 importance < forget_threshold(0.3)  →  自动 forgotten = 1

   现实（你现在写的）：
     全靠手动调 forget_memory / delete_memory
'''


class MemoryTool:

    def __init__(
        self,
        manager : MemoryManager,
        user_id : str,
        session_id : str | None = None,
    ):
        self.manager = manager
        self.user_id = user_id
        self.session_id = session_id

    def save_memory(
            self,
            content : str,
             memory_type: MemoryType = "semantic",
            *,
            importance: float = 0.5,

        ) -> str :
        """保存用户希望记住的偏好、事实或事件。
        importance 表示这条信息对未来对话有多大用处，取值为 0 到 1。
        只在当前任务有用的细节可给 0.2，之后可能再次用到的信息可给 0.5，
        用户明确希望长期保留的偏好可给 0.8。
        """
        item = self.manager.add_memory(
            user_id = self.user_id,
            content = content,
            memory_type = memory_type,
            session_id = self.session_id,
            importance = importance,
        )

        return f"记忆已保存， ID 为{item.id} 重要性为 {item.importance}"

    def read_memory(self, query : str) -> str:
        """按关键词来查找用户记忆、返回正文和对应ID"""
        items = self.manager.search_memories(self.user_id, query)
        if not items:
            return "没有找到相关记忆"
        return "\n".join(f"{item.id} | {item.content}" for item in items)

    def forget_memory(self) -> str:
        """遗忘所有重要性低于阈值的记忆，返回遗忘数量。"""
        count = self.manager.forget_memory(self.user_id)
        if count:
            return f"已遗忘 {count} 条低重要性记忆。"
        return "没有需要遗忘的记忆。"


    def delete_memory(self, memory_id : str) -> str:
        """按记忆 ID 从当前用户的数据库中删除这个记忆"""
        if self.manager.delete_memory(self.user_id, memory_id):
            return "已从数据库中删除这条记忆"

        return "未找到相关记忆"