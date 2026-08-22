import sqlite3
from typing import Any
from app.core.config import settings

try:
    from langgraph.checkpoint.sqlite import SqliteSaver
    HAS_SQLITE_SAVER = True
except ImportError:
    from langgraph.checkpoint.memory import MemorySaver as SqliteSaver
    HAS_SQLITE_SAVER = False

def get_sqlite_checkpointer() -> Any:
    """Initializes and returns SQLite checkpointer for LangGraph conversation memory."""
    db_path = getattr(settings, "CHECKPOINT_DB_PATH", "checkpoints.db")
    if HAS_SQLITE_SAVER:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        checkpointer = SqliteSaver(conn)
        checkpointer.setup()
        return checkpointer
    else:
        return SqliteSaver()

sqlite_checkpointer = get_sqlite_checkpointer()
