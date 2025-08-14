import abc
from typing import TypeVar

from yt_dlp_server.db.models import Task, TaskRecord, TaskStatus

ConnectionParameters = TypeVar("ConnectionParameters")


class BaseDB[ConnectionParameters](abc.ABC):
    @abc.abstractmethod
    def connect(self, parameters: ConnectionParameters) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def is_connected(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def add_task(self, task: Task, claimed_by: int) -> TaskRecord:
        raise NotImplementedError

    @abc.abstractmethod
    def get_task(self, task: Task) -> TaskRecord | None:
        raise NotImplementedError

    @abc.abstractmethod
    def update_task(self, task: Task, status: TaskStatus) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def claim_task(
        self, task: Task, claimed_by: int, timeout_seconds: int = 1800
    ) -> TaskRecord | None:
        raise NotImplementedError
