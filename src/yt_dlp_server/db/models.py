import enum

import pydantic


class TaskStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(pydantic.BaseModel):
    job_id: str
    url: str


class TaskRecord(pydantic.BaseModel):
    task: Task
    status: TaskStatus
