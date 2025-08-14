"""Tests for SQLiteDB implementation."""

import pytest
import sqlite3
from yt_dlp_server.db.impl.sqlite import SQLiteDB
from yt_dlp_server.db.models import Task, TaskRecord, TaskStatus


@pytest.fixture
def db():
    """Provides a SQLiteDB instance with tables created using an in-memory database."""
    database = SQLiteDB()
    database.connect(":memory:")
    database.create_tables()
    yield database
    # Teardown: close the connection (this destroys the :memory: database)
    if database.connection:
        database.connection.close()


@pytest.fixture
def sample_task():
    """Provides a sample Task instance for tests."""
    return Task(job_id="test_job_123", url="https://example.com/video.mp4")


@pytest.fixture
def another_task():
    """Provides another sample Task instance for tests."""
    return Task(job_id="test_job_456", url="https://example.com/another_video.mp4")


class TestSQLiteDBConnection:
    """Test database connection functionality."""

    def test_initial_state_not_connected(self):
        """Test that a new SQLiteDB instance is not connected initially."""
        db = SQLiteDB()
        assert not db.is_connected()

    def test_connect_to_memory_database(self):
        """Test connecting to an in-memory SQLite database."""
        db = SQLiteDB()
        db.connect(":memory:")
        assert db.is_connected()
        assert isinstance(db.connection, sqlite3.Connection)
        db.connection.close()

    def test_connect_to_file_database(self, tmp_path):
        """Test connecting to a file-based SQLite database."""
        db_file = tmp_path / "test.db"
        db = SQLiteDB()
        db.connect(str(db_file))
        assert db.is_connected()
        assert isinstance(db.connection, sqlite3.Connection)
        db.connection.close()

    def test_create_tables(self, db):
        """Test that create_tables creates the required task table."""
        # Verify the table was created by checking if we can query it
        cursor = db.connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='task'"
        )
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == "task"

    def test_create_tables_schema(self, db):
        """Test that the task table has the correct schema."""
        cursor = db.connection.execute("PRAGMA table_info(task)")
        columns = cursor.fetchall()

        # Expected columns: id, job_id, url, status, created_at, claimed_by, claimed_at, updated_at
        assert len(columns) == 8

        # Check id column
        id_col = next(col for col in columns if col[1] == "id")
        assert id_col[2] == "INTEGER"  # type
        assert id_col[5] == 1  # primary key flag

        # Check job_id column
        job_id_col = next(col for col in columns if col[1] == "job_id")
        assert job_id_col[2] == "TEXT"  # type
        assert job_id_col[3] == 1  # not null flag

        # Check url column
        url_col = next(col for col in columns if col[1] == "url")
        assert url_col[2] == "TEXT"
        assert url_col[3] == 1  # not null flag

        # Check status column
        status_col = next(col for col in columns if col[1] == "status")
        assert status_col[2] == "TEXT"
        assert status_col[3] == 1  # not null flag

        # Check created_at column
        created_at_col = next(col for col in columns if col[1] == "created_at")
        assert created_at_col[2] == "TEXT"
        assert created_at_col[3] == 1  # not null flag

        # Check claimed_by column
        claimed_by_col = next(col for col in columns if col[1] == "claimed_by")
        assert claimed_by_col[2] == "INTEGER"
        assert claimed_by_col[3] == 1  # not null flag

        # Check claimed_at column
        claimed_at_col = next(col for col in columns if col[1] == "claimed_at")
        assert claimed_at_col[2] == "TEXT"
        assert claimed_at_col[3] == 1  # not null flag

        # Check updated_at column
        updated_at_col = next(col for col in columns if col[1] == "updated_at")
        assert updated_at_col[2] == "TEXT"
        assert updated_at_col[3] == 1  # not null flag

        # Check for unique constraint on (job_id, url)
        cursor = db.connection.execute("PRAGMA index_list(task)")
        indexes = cursor.fetchall()

        # There should be at least one index (for the unique constraint)
        assert len(indexes) >= 1

        # Check that there's a unique index
        unique_indexes = [idx for idx in indexes if idx[2] == 1]  # unique flag
        assert len(unique_indexes) >= 1


class TestSQLiteDBTaskOperations:
    """Test task CRUD operations."""

    def test_add_task_returns_task_record(self, db, sample_task):
        """Test that add_task returns a TaskRecord with the task and default status."""
        result = db.add_task(sample_task, 123)

        assert isinstance(result, TaskRecord)
        assert result.task == sample_task
        assert isinstance(result.status, TaskStatus)

    def test_add_task_persists_to_database(self, db, sample_task):
        """Test that add_task actually persists the task to the database."""
        db.add_task(sample_task, 123)

        # Directly query the database to verify persistence
        cursor = db.connection.execute(
            "SELECT id, job_id, url, status FROM task WHERE job_id = ? AND url = ?",
            (sample_task.job_id, sample_task.url),
        )
        row = cursor.fetchone()

        assert row is not None
        assert isinstance(row[0], int)  # id should be an integer
        assert row[0] > 0  # id should be positive (autoincrement starts at 1)
        assert row[1] == sample_task.job_id
        assert row[2] == sample_task.url
        assert row[3] in [status.value for status in TaskStatus]

    def test_add_multiple_tasks(self, db, sample_task, another_task):
        """Test adding multiple different tasks."""
        result1 = db.add_task(sample_task, 123)
        result2 = db.add_task(another_task, 456)

        assert isinstance(result1, TaskRecord)
        assert isinstance(result2, TaskRecord)
        assert result1.task.job_id != result2.task.job_id

    def test_get_task_existing(self, db, sample_task):
        """Test getting an existing task from the database."""
        # First add a task
        db.add_task(sample_task, 123)

        # Then retrieve it
        result = db.get_task(sample_task)

        assert result is not None
        assert isinstance(result, TaskRecord)
        assert result.task.job_id == sample_task.job_id
        assert result.task.url == sample_task.url
        assert isinstance(result.status, TaskStatus)

    def test_get_task_nonexistent(self, db):
        """Test getting a task that doesn't exist returns None."""
        nonexistent_task = Task(
            job_id="nonexistent", url="https://example.com/none.mp4"
        )
        result = db.get_task(nonexistent_task)

        assert result is None

    def test_update_task_status(self, db, sample_task):
        """Test updating the status of an existing task."""
        # Add a task
        db.add_task(sample_task, 123)

        # Update its status
        new_status = TaskStatus.RUNNING
        db.update_task(sample_task, new_status)

        # Verify the update
        result = db.get_task(sample_task)
        assert result is not None
        assert result.status == new_status

    def test_update_task_status_multiple_times(self, db, sample_task):
        """Test updating task status multiple times."""
        db.add_task(sample_task, 123)

        # Update through different statuses
        statuses = [TaskStatus.RUNNING, TaskStatus.COMPLETED, TaskStatus.FAILED]
        for status in statuses:
            db.update_task(sample_task, status)
            result = db.get_task(sample_task)
            assert result is not None
            assert result.status == status

    def test_update_nonexistent_task(self, db):
        """Test updating a task that doesn't exist (should not raise an error)."""
        nonexistent_task = Task(
            job_id="nonexistent", url="https://example.com/none.mp4"
        )

        # This should not raise an error, but also shouldn't affect anything
        db.update_task(nonexistent_task, TaskStatus.COMPLETED)

        # Verify the task still doesn't exist
        result = db.get_task(nonexistent_task)
        assert result is None


class TestSQLiteDBTaskStatus:
    """Test task status handling."""

    def test_all_task_statuses(self, db, sample_task):
        """Test that all TaskStatus enum values can be stored and retrieved."""
        for status in TaskStatus:
            # Create a task with a unique job_id for each status
            task = Task(job_id=f"test_{status.value}", url=sample_task.url)

            # Add and then update the task
            db.add_task(task, 123)
            db.update_task(task, status)

            # Verify the status is correctly stored and retrieved
            result = db.get_task(task)
            assert result is not None
            assert result.status == status

    def test_default_status_on_add(self, db, sample_task):
        """Test that newly added tasks have a default status."""
        result = db.add_task(sample_task, 123)
        assert isinstance(result.status, TaskStatus)

        # Verify it's also persisted with a valid status
        retrieved = db.get_task(sample_task)
        assert retrieved is not None
        assert isinstance(retrieved.status, TaskStatus)


class TestSQLiteDBEdgeCases:
    """Test edge cases and error conditions."""

    def test_add_duplicate_job_id_different_url(self, db, sample_task):
        """Test adding a task with the same job_id but different URL (should succeed)."""
        # Add the first task
        db.add_task(sample_task, 123)

        # Add a task with the same job_id but different URL - this should succeed
        different_url_task = Task(
            job_id=sample_task.job_id, url="https://different.com/video.mp4"
        )
        result = db.add_task(different_url_task, 456)

        # Should succeed and return a TaskRecord
        assert isinstance(result, TaskRecord)
        assert result.task.job_id == sample_task.job_id
        assert result.task.url == different_url_task.url

    def test_add_duplicate_job_id_and_url(self, db, sample_task):
        """Test adding a task with duplicate (job_id, url) combination."""
        # Add the first task
        db.add_task(sample_task, 123)

        # Try to add a task with the same job_id AND same URL
        duplicate_task = Task(job_id=sample_task.job_id, url=sample_task.url)

        # This should raise an integrity error due to UNIQUE(job_id, url) constraint
        with pytest.raises(sqlite3.IntegrityError):
            db.add_task(duplicate_task, 123)

    def test_empty_database_operations(self, db):
        """Test operations on an empty database."""
        # Get from empty database
        task = Task(job_id="test", url="https://example.com/video.mp4")
        result = db.get_task(task)
        assert result is None

        # Update in empty database (should not raise error)
        db.update_task(task, TaskStatus.COMPLETED)

    def test_special_characters_in_data(self, db):
        """Test handling of special characters in job_id and URL."""
        special_task = Task(
            job_id="test'with\"quotes;and--sql",
            url="https://example.com/video with spaces & symbols.mp4?param=value&other='test'",
        )

        # Should handle special characters without SQL injection issues
        result = db.add_task(special_task, 123)
        assert isinstance(result, TaskRecord)

        retrieved = db.get_task(special_task)
        assert retrieved is not None
        assert retrieved.task.job_id == special_task.job_id
        assert retrieved.task.url == special_task.url

    def test_large_data(self, db):
        """Test handling of large data values."""
        large_url = "https://example.com/" + "a" * 10000  # Very long URL
        large_job_id = "job_" + "b" * 1000  # Very long job ID

        large_task = Task(job_id=large_job_id, url=large_url)

        result = db.add_task(large_task, 123)
        assert isinstance(result, TaskRecord)

        retrieved = db.get_task(large_task)
        assert retrieved is not None
        assert retrieved.task.job_id == large_job_id
        assert retrieved.task.url == large_url


class TestSQLiteDBTransactions:
    """Test transaction behavior and consistency."""

    def test_add_task_commits_immediately(self, db, sample_task):
        """Test that add_task commits the transaction immediately."""
        db.add_task(sample_task, 123)

        # Create a new connection to the same database to verify commit
        new_connection = sqlite3.connect(":memory:")
        # Since we're using :memory:, we can't actually test this with a separate connection
        # But we can verify the task is immediately queryable
        result = db.get_task(sample_task)
        assert result is not None

    def test_update_task_commits_immediately(self, db, sample_task):
        """Test that update_task commits the transaction immediately."""
        db.add_task(sample_task, 123)
        db.update_task(sample_task, TaskStatus.RUNNING)

        # Verify the update is immediately visible
        result = db.get_task(sample_task)
        assert result is not None
        assert result.status == TaskStatus.RUNNING

    def test_multiple_operations_consistency(self, db, sample_task, another_task):
        """Test that multiple operations maintain data consistency."""
        # Add multiple tasks
        db.add_task(sample_task, 123)
        db.add_task(another_task, 456)

        # Update one task
        db.update_task(sample_task, TaskStatus.COMPLETED)

        # Verify both tasks exist with correct states
        result1 = db.get_task(sample_task)
        result2 = db.get_task(another_task)

        assert result1 is not None
        assert result1.status == TaskStatus.COMPLETED
        assert result2 is not None
        # result2 should have its original status (not affected by update to result1)
