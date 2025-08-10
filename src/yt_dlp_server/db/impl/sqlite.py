import sqlite3

from yt_dlp_server.db.base import BaseDB
from yt_dlp_server.db.models import Task, TaskRecord, TaskStatus


class SQLiteDB(BaseDB[sqlite3.Connection]):
    def __init__(self):
        self.connection: sqlite3.Connection | None = None

    def connect(self, parameters: str) -> None:
        self.connection = sqlite3.connect(parameters)

    def create_tables(self) -> None:
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS task (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT,
                url TEXT,
                status TEXT,
                UNIQUE(job_id, url)
            )
        """)

    def is_connected(self) -> bool:
        return self.connection is not None
    
    def add_task(self, task: Task) -> TaskRecord:
        default_status = TaskStatus.PENDING
        self.connection.execute("""
            INSERT INTO task (job_id, url, status) VALUES (?, ?, ?)
        """, (task.job_id, task.url, default_status.value))
        self.connection.commit()
        return TaskRecord(task=task, status=default_status)

    def get_task(self, task: Task) -> TaskRecord | None:
        cursor = self.connection.execute("""
            SELECT job_id, url, status FROM task WHERE job_id = ? AND url = ?
        """, (task.job_id, task.url))
        row = cursor.fetchone()
        if row is None:
            return None
        retrieved_task = Task(job_id=row[0], url=row[1])
        status = TaskStatus(row[2])
        return TaskRecord(task=retrieved_task, status=status)
    
    def update_task(self, task: Task, status: TaskStatus) -> None:
        self.connection.execute("""
            UPDATE task SET status = ? WHERE job_id = ? AND url = ?
        """, (status.value, task.job_id, task.url))
        self.connection.commit()
