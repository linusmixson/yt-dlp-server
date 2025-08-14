import sqlite3
from datetime import datetime, timezone

from yt_dlp_server.db.base import BaseDB
from yt_dlp_server.db.models import Task, TaskRecord, TaskStatus


class SQLiteDB(BaseDB[sqlite3.Connection]):
    def __init__(self):
        self.connection: sqlite3.Connection | None = None

    def connect(self, parameters: str) -> None:
        self.connection = sqlite3.connect(parameters)
        # Configure row factory for key-based record access
        self.connection.row_factory = sqlite3.Row

    def create_tables(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS task (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                url TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
                claimed_by INTEGER NOT NULL,
                claimed_at TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
                UNIQUE(job_id, url)
            )
        """
        )
        self.connection.execute(
            """
            CREATE TRIGGER IF NOT EXISTS set_updated_at
            AFTER UPDATE ON task
            FOR EACH ROW
            BEGIN
                UPDATE task SET updated_at = datetime('now', 'utc') WHERE id = OLD.id;
            END;
        """
        )

    def is_connected(self) -> bool:
        return self.connection is not None

    def add_task(self, task: Task, claimed_by: int) -> TaskRecord:
        default_status = TaskStatus.PENDING
        self.connection.execute(
            """
            INSERT INTO task (job_id, url, status, claimed_by, claimed_at) VALUES (?, ?, ?, ?, datetime('now', 'utc'))
        """,
            (task.job_id, task.url, default_status.value, claimed_by),
        )
        self.connection.commit()
        return self.get_task(task)

    def get_task(self, task: Task) -> TaskRecord | None:
        cursor = self.connection.execute(
            """
            SELECT id, job_id, url, status, created_at, claimed_by, claimed_at, updated_at 
            FROM task WHERE job_id = ? AND url = ?
        """,
            (task.job_id, task.url),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return TaskRecord(**dict(row))

    def update_task(self, task: Task, status: TaskStatus) -> None:
        self.connection.execute(
            """
            UPDATE task SET status = ? WHERE job_id = ? AND url = ?
        """,
            (status.value, task.job_id, task.url),
        )
        self.connection.commit()
