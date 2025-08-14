import sqlite3
from datetime import UTC, datetime

from yt_dlp_server.db.base import BaseDB
from yt_dlp_server.db.errors import TaskNotFoundError
from yt_dlp_server.db.models import Task, TaskRecord, TaskStatus


class SQLiteDB(BaseDB[str]):
    def __init__(self) -> None:
        self.connection: sqlite3.Connection | None = None

    def connect(self, parameters: str) -> None:
        self.connection = sqlite3.connect(parameters)
        # Configure row factory for key-based record access
        self.connection.row_factory = sqlite3.Row

    def create_tables(self) -> None:
        if self.connection is None:
            raise RuntimeError("Database is not connected")
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
        # Use second-granularity to match SQLite's datetime('now','utc') trigger/defaults
        now_utc = datetime.now(UTC).replace(microsecond=0).isoformat()
        if self.connection is None:
            raise RuntimeError("Database is not connected")
        self.connection.execute(
            "INSERT INTO task (job_id, url, status, created_at, claimed_by, claimed_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                task.job_id,
                task.url,
                TaskStatus.PENDING.value,
                now_utc,
                claimed_by,
                now_utc,
                now_utc,
            ),
        )
        self.connection.commit()
        task_record = self.get_task(task)
        if task_record is None:
            raise TaskNotFoundError(task)
        return task_record

    def get_task(self, task: Task) -> TaskRecord | None:
        if self.connection is None:
            raise RuntimeError("Database is not connected")
        cursor = self.connection.execute(
            "SELECT job_id, url, status, created_at, claimed_by, claimed_at, updated_at "
            "FROM task WHERE job_id = ? AND url = ?",
            (task.job_id, task.url),
        )
        row = cursor.fetchone()
        if row:
            return TaskRecord(
                **dict(row)
            )
        return None

    def update_task(self, task: Task, status: TaskStatus) -> None:
        # Use second-granularity to match SQLite's datetime('now','utc') trigger/defaults
        now_utc = datetime.now(UTC).replace(microsecond=0).isoformat()
        if self.connection is None:
            raise RuntimeError("Database is not connected")
        self.connection.execute(
            "UPDATE task SET status = ?, updated_at = ? WHERE job_id = ? AND url = ?",
            (status.value, now_utc, task.job_id, task.url),
        )
        self.connection.commit()

    def claim_task(
        self, task: Task, claimed_by: int, timeout_seconds: int = 1800
    ) -> TaskRecord | None:
        # Use second-granularity to match SQLite's datetime('now','utc') trigger/defaults
        now_utc = datetime.now(UTC).replace(microsecond=0).isoformat()

        # Perform atomic update: only update if claimed_by matches or timeout has expired
        if self.connection is None:
            raise RuntimeError("Database is not connected")
        cursor = self.connection.execute(
            """
            UPDATE task
            SET claimed_by = ?, claimed_at = ?, updated_at = ?
            WHERE job_id = ? AND url = ?
              AND (
                claimed_by = ?
                OR (
                    claimed_at IS NOT NULL
                    AND strftime('%s', ?) - strftime('%s', claimed_at) > ?
                )
              )
            """,
            (
                claimed_by,
                now_utc,
                now_utc,
                task.job_id,
                task.url,
                claimed_by,
                now_utc,
                timeout_seconds,
            ),
        )
        self.connection.commit()

        claimed = cursor.rowcount > 0

        task_record = self.get_task(task)

        if task_record is None:
            raise TaskNotFoundError(task)

        if claimed:
            return task_record
        else:
            return None
