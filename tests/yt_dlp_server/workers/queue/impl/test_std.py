import threading
import time

import pytest

from yt_dlp_server.workers.queue.base import Empty, Full
from yt_dlp_server.workers.queue.impl.std import STDQueue
from yt_dlp_server.workers.task import Task


@pytest.fixture
def task() -> Task:
    """Provides a simple Task instance for tests."""
    return Task(url="https://example.com/video.mp4")


@pytest.fixture
def queue() -> STDQueue:
    """Provides an empty STDQueue instance for each test."""
    return STDQueue()


def test_qsize(queue: STDQueue, task: Task):
    """Test that qsize correctly reflects the number of items in the queue."""
    assert queue.qsize() == 0
    queue.put(task)
    assert queue.qsize() == 1
    queue.get()
    assert queue.qsize() == 0


def test_put_and_get(queue: STDQueue, task: Task):
    """Test basic put and get functionality."""
    queue.put(task)
    retrieved_task = queue.get()
    assert retrieved_task is task


def test_get_nowait_on_empty_raises_empty(queue: STDQueue):
    """Test that get_nowait raises Empty on an empty queue."""
    with pytest.raises(Empty):
        queue.get_nowait()


def test_put_nowait_on_full_raises_full(task: Task):
    """Test that put_nowait raises Full on a full queue."""
    q = STDQueue(maxsize=1)
    q.put_nowait(task)
    with pytest.raises(Full):
        q.put_nowait(task)


def test_get_with_timeout_on_empty_queue(queue: STDQueue):
    """Test that a blocking get with a timeout raises Empty after the timeout."""
    timeout = 0.01
    start_time = time.monotonic()
    with pytest.raises(Empty):
        queue.get(timeout=timeout)
    duration = time.monotonic() - start_time
    assert duration == pytest.approx(timeout, abs=0.01)


def test_put_with_timeout_on_full_queue(task: Task):
    """Test that a blocking put with a timeout raises Full after the timeout."""
    q = STDQueue(maxsize=1)
    q.put(task)
    timeout = 0.01
    start_time = time.monotonic()
    with pytest.raises(Full):
        q.put(task, timeout=timeout)
    duration = time.monotonic() - start_time
    assert duration == pytest.approx(timeout, abs=0.01)


def test_task_done_and_join(task: Task):
    """
    Tests that join() blocks until task_done() is called for all items,
    using a worker thread to process items.
    """
    q = STDQueue()
    num_tasks = 5

    def worker():
        for _ in range(num_tasks):
            q.get()
            time.sleep(0.01)  # Simulate work
            q.task_done()

    for _ in range(num_tasks):
        q.put(task)

    worker_thread = threading.Thread(target=worker)
    worker_thread.start()

    join_start_time = time.monotonic()
    q.join()  # This should block until the worker is done
    join_duration = time.monotonic() - join_start_time

    # The join should have taken at least as long as the work
    assert join_duration >= (0.01 * num_tasks)
    assert q.qsize() == 0

    worker_thread.join()  # Clean up the thread


def test_join_on_empty_queue_returns_immediately(queue: STDQueue):
    """Test that join() on an empty queue returns immediately."""
    queue.join()  # Should not block


def test_task_done_without_get_raises_value_error(queue: STDQueue):
    """Test that calling task_done() without a corresponding get() raises ValueError."""
    with pytest.raises(ValueError):
        queue.task_done()


def test_multithreaded_consumers(task: Task):
    """
    Tests thread safety with multiple consumer threads processing items
    from the queue concurrently.
    """
    q = STDQueue()
    num_tasks = 50
    num_consumers = 5
    items_processed = []
    lock = threading.Lock()

    def consumer_worker():
        while True:
            try:
                # Use a short timeout to prevent blocking forever if the test fails
                item = q.get(timeout=0.1)
                with lock:
                    items_processed.append(item)
                q.task_done()
            except Empty:
                break  # No more items

    for _ in range(num_tasks):
        q.put(task)

    threads = [
        threading.Thread(target=consumer_worker) for _ in range(num_consumers)
    ]
    for t in threads:
        t.start()

    q.join()  # Wait for all tasks to be processed

    for t in threads:
        t.join()  # Ensure all threads have finished

    assert len(items_processed) == num_tasks
    assert q.qsize() == 0
