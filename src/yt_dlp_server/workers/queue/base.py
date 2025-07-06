import abc

from yt_dlp_server.workers.task import Task


class EmptyError(Exception):
    """Exception raised by non-blocking get() on an empty queue."""


class FullError(Exception):
    """Exception raised by non-blocking put() on a full queue."""


class BaseQueue(abc.ABC):
    """
    Abstract base class for a worker queue.

    This class defines the interface for a queue that can be used by workers
    to get tasks and report results. It is designed to be a generic interface
    that can be implemented by various queueing systems, such as
    `queue.Queue`, `multiprocessing.Queue`, or a distributed queue like SQS.
    """

    @abc.abstractmethod
    def get(self, block: bool = True, timeout: float | None = None) -> Task:
        """
        Remove and return an item from the queue.

        If optional args `block` is true and `timeout` is None (the default),
        block if necessary until an item is available. If `timeout` is a
        positive number, it blocks at most `timeout` seconds and raises
        the :class:`EmptyError` exception if no item was available within that
        time. Otherwise (`block` is false), return an item if one is
        immediately available, else raise the :class:`EmptyError` exception
        (`timeout` is ignored in that case).
        """
        raise NotImplementedError

    @abc.abstractmethod
    def put(self, item: Task, block: bool = True, timeout: float | None = None) -> None:
        """
        Put an item into the queue.

        If optional args `block` is true and `timeout` is None (the default),
        block if necessary until a free slot is available. If `timeout` is a
        positive number, it blocks at most `timeout` seconds and raises the
        :class:`FullError` exception if no free slot was available within that
        time. Otherwise (`block` is false), put an item if a free slot is
        immediately available, else raise the :class:`FullError` exception
        (`timeout` is ignored in that case).
        """
        raise NotImplementedError

    def get_nowait(self) -> Task:
        """
        Remove and return an item from the queue without blocking.

        :return: An item from the queue.
        :raises EmptyError: If the queue is empty.
        """
        return self.get(block=False)

    def put_nowait(self, item: Task) -> None:
        """
        Put an item into the queue without blocking.

        :param item: The item to put into the queue.
        :raises FullError: If the queue is full.
        """
        self.put(item, block=False)

    @abc.abstractmethod
    def qsize(self) -> int:
        """
        Return the approximate size of the queue.

        Note, qsize() > 0 doesn't guarantee that a subsequent get()
        will not block.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def task_done(self) -> None:
        """
        Indicate that a formerly enqueued task is complete.

        Used by queue consumers. For each :meth:`get` used to fetch a task,
        a subsequent call to :meth:`task_done` tells the queue that the
        processing on the task is complete.

        If a :meth:`join` is currently blocking, it will resume when all
        items have been processed (meaning that a :meth:`task_done` call was
        received for every item that had been :meth:`put` into the queue).

        Raises a :exc:`ValueError` if called more times than there were
        items placed in the queue.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def join(self) -> None:
        """
        Block until all items in the queue have been gotten and processed.

        The count of unfinished tasks goes up whenever an item is added to
        the queue. The count goes down whenever a consumer calls
        :meth:`task_done` to indicate that the item was retrieved and all
        work on it is complete. When the count of unfinished tasks drops
        to zero, :meth:`join` unblocks.
        """
        raise NotImplementedError
