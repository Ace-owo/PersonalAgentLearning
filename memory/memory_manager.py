import sqlite3
from contextlib import closing, contextmanager

from .memory_config import MemoryConfig
from .memory_item import MemoryItem, MemoryType


class MemoryManager:
    def __init__(self, config: MemoryConfig):
        self.config = config
        config.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("""
                CREATE TABLE IF NOT EXISTS memory_items (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    forgotten INTEGER NOT NULL DEFAULT 0,
                    importance REAL NOT NULL DEFAULT 0.5
                )
            """)
            columns = {
                row["name"] for row in db.execute("PRAGMA table_info(memory_items)")
            }
            if "forgotten" not in columns:
                db.execute(
                    "ALTER TABLE memory_items ADD COLUMN forgotten INTEGER NOT NULL DEFAULT 0"
                )

    @contextmanager
    def _connect(self):
        with closing(sqlite3.connect(self.config.db_path)) as db:
            db.row_factory = sqlite3.Row
            with db:
                yield db
                

    def add_memory(
        self,
        user_id: str,
        content: str,
        memory_type: MemoryType = "semantic",
        *,
        session_id: str | None = None,
        importance: float = 0.5,
    ) -> MemoryItem:
        item = MemoryItem(
            user_id=user_id,
            content=content,
            memory_type=memory_type,
            session_id=session_id,
            importance=importance,
        )
        with self._connect() as db:
            db.execute(
                """
                INSERT INTO memory_items
                    (id, user_id, session_id, memory_type, content, importance, created_at)
                VALUES
                    (:id, :user_id, :session_id, :memory_type, :content, :importance,:created_at)
                """,
                item.model_dump(),
            )
        return item

    def search_memories(self, user_id: str, query: str) -> list[MemoryItem]:
        query = query.strip()
        if not query:
            return []

        with self._connect() as db:
            rows = db.execute(
                """
                SELECT id, user_id, session_id, memory_type, content, importance, created_at
                FROM memory_items
                WHERE user_id = ? AND forgotten = 0 AND instr(content, ?) > 0
                ORDER BY importance DESC,created_at DESC
                LIMIT ?
                """,
                (user_id.strip(), query, self.config.search_limit),
            ).fetchall()
        return [MemoryItem.model_validate(dict(row)) for row in rows]

    def forget_memory(self, user_id: str) -> int:
        """把 importance 低于阈值的记忆标记为遗忘，返回遗忘数量。"""
        with self._connect() as db:
            result = db.execute(
                "UPDATE memory_items SET forgotten = 1 "
                "WHERE user_id = ? AND forgotten = 0 AND importance < ?",
                (user_id.strip(), self.config.forget_threshold),
            )
            return result.rowcount

    def delete_memory(self, user_id: str, memory_id: str) -> bool:
        with self._connect() as db:
            result = db.execute(
                "DELETE FROM memory_items WHERE user_id = ? AND id = ?",
                (user_id.strip(), memory_id),
            )
            return result.rowcount == 1