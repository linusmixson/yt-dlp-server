import enum
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, field_validator, model_validator


class TaskStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(BaseModel):
    job_id: str
    url: str


class TaskRecord(BaseModel):
    task: Task
    status: TaskStatus
    created_at: datetime
    claimed_by: int
    claimed_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at", "claimed_at", mode="before")
    @classmethod
    def parse_datetimes(cls, v: Any) -> Any:
        if isinstance(v, str):
            dt = datetime.fromisoformat(v)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=UTC)
            return dt
        return v

    @field_validator("status", mode="before")
    @classmethod
    def parse_status(cls, v: Any) -> Any:
        if isinstance(v, str):
            return TaskStatus(v)
        return v

    @model_validator(mode="before")
    @classmethod
    def build_task(cls, data: Any) -> Any:
        if isinstance(data, dict) and "job_id" in data and "url" in data:
            data["task"] = Task(job_id=data.pop("job_id"), url=data.pop("url"))
        return data
