import queue

from yt_dlp_server.workers.queue.base import (
    BaseQueue,
    EmptyError,
    FullError,
)
from yt_dlp_server.workers.task import Task


class STLQueue(BaseQueue):
    """
    A queue that uses the standard library's :class:`queue.Queue` under the hood.
    """

    def __init__(self, maxsize: int = 0) -> None:
        self._queue: queue.Queue[Task] = queue.Queue(maxsize=maxsize)

    def get(self, block: bool = True, timeout: float | None = None) -> Task:
        """
        See :meth:`BaseQueue.get`.
        """
        try:
            return self._queue.get(block=block, timeout=timeout)
        except queue.Empty as e:
            raise EmptyError from e

    def put(self, item: Task, block: bool = True, timeout: float | None = None) -> None:
        """
        See :meth:`BaseQueue.put`.
        """
        try:
            self._queue.put(item, block=block, timeout=timeout)
        except queue.Full as e:
            raise FullError from e

    def qsize(self) -> int:
        """
        See :meth:`BaseQueue.qsize`.
        """
        return self._queue.qsize()

    def task_done(self) -> None:
        """
        See :meth:`BaseQueue.task_done`.
        """
        self._queue.task_done()

    def join(self) -> None:
        """
        See :meth:`BaseQueue.join`.
        """
        self._queue.join()
