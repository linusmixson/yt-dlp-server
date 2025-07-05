import pytest

from yt_dlp_server.workers.task import Task


def test_task_creation():
    """Test that a Task can be created with a URL."""
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    task = Task(url=url)
    assert task.url == url


def test_task_json_serialization():
    """Test that a Task can be serialized to JSON."""
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    task = Task(url=url)
    json_data = task.model_dump_json()
    expected_json = f'{{"url":"{url}"}}'
    assert json_data == expected_json


def test_task_json_deserialization():
    """Test that a Task can be deserialized from JSON."""
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    json_data = f'{{"url":"{url}"}}'
    task = Task.model_validate_json(json_data)
    assert task.url == url


def test_task_serialization_roundtrip():
    """Test that a Task can be serialized and deserialized back to an equivalent object."""
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    original_task = Task(url=url)
    json_data = original_task.model_dump_json()
    new_task = Task.model_validate_json(json_data)
    assert original_task == new_task 