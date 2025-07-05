import pathlib
import shutil
import tempfile

import pytest

from yt_dlp_server.storage.impl.local import LocalStorageEngine


@pytest.fixture
def temp_repo_path() -> pathlib.Path:
    """Create a temporary directory for the repository and clean it up afterward."""
    path = pathlib.Path(tempfile.mkdtemp(prefix="yt-dlp-server-test-"))
    yield path
    shutil.rmtree(path)


class TestLocalStorageEngine:
    def test_init_with_default_repository(self):
        """Test that a temporary directory is created when no repository is provided."""
        engine = LocalStorageEngine()
        assert engine.repository.is_dir()
        assert engine.repository.name.startswith("yt-dlp-server-")
        # Clean up the created directory
        shutil.rmtree(engine.repository)

    def test_init_with_specific_repository(self, temp_repo_path: pathlib.Path):
        """Test that the provided repository path is used."""
        engine = LocalStorageEngine(repository=temp_repo_path)
        assert engine.repository == temp_repo_path
        assert engine.repository.is_dir()

    def test_get_repository(self, temp_repo_path: pathlib.Path):
        """Test that get_repository returns the correct path."""
        engine = LocalStorageEngine(repository=temp_repo_path)
        assert engine.repository == temp_repo_path

    def test_canonicalize_path(self, temp_repo_path: pathlib.Path):
        """Test that canonicalize_path correctly resolves paths."""
        engine = LocalStorageEngine(repository=temp_repo_path)

        # Test with a simple path
        simple_path = pathlib.Path("test_file.txt")
        assert engine.canonicalize_path(simple_path) == temp_repo_path / simple_path

        # Test with a nested path
        nested_path = pathlib.Path("subdir/another_file.txt")
        assert engine.canonicalize_path(nested_path) == temp_repo_path / nested_path

        # Test with an empty path
        empty_path = pathlib.Path("")
        assert engine.canonicalize_path(empty_path) == temp_repo_path

    def test_write_and_read_bytes(self, temp_repo_path: pathlib.Path):
        """Test writing and reading bytes to/from a path."""
        engine = LocalStorageEngine(repository=temp_repo_path)
        path = pathlib.Path("data.bin")
        data = b"test_data_123"

        # Write data
        bytes_written = engine.write_bytes_to_path(path, data)
        assert bytes_written == len(data)

        # Check that file exists
        canonical_path = engine.canonicalize_path(path)
        assert canonical_path.exists()
        assert canonical_path.is_file()

        # Read data back and verify
        read_data = engine.read_bytes_from_path(path)
        assert read_data == data

    def test_write_to_nested_path(self, temp_repo_path: pathlib.Path):
        """Test that writing to a nested path creates subdirectories."""
        engine = LocalStorageEngine(repository=temp_repo_path)
        path = pathlib.Path("some/nested/dir/file.txt")
        data = b"deeply nested data"

        engine.write_bytes_to_path(path, data)

        canonical_path = engine.canonicalize_path(path)
        assert canonical_path.exists()
        assert canonical_path.parent.is_dir()

        read_data = engine.read_bytes_from_path(path)
        assert read_data == data

    def test_overwrite_existing_file(self, temp_repo_path: pathlib.Path):
        """Test that writing to an existing path overwrites the file."""
        engine = LocalStorageEngine(repository=temp_repo_path)
        path = pathlib.Path("file_to_overwrite.txt")
        initial_data = b"initial"
        new_data = b"overwritten"

        # Write initial data
        engine.write_bytes_to_path(path, initial_data)
        assert engine.read_bytes_from_path(path) == initial_data

        # Overwrite with new data
        engine.write_bytes_to_path(path, new_data)
        assert engine.read_bytes_from_path(path) == new_data

    def test_read_nonexistent_file(self, temp_repo_path: pathlib.Path):
        """Test that reading a non-existent file raises FileNotFoundError."""
        engine = LocalStorageEngine(repository=temp_repo_path)
        path = pathlib.Path("nonexistent_file.txt")

        with pytest.raises(FileNotFoundError):
            engine.read_bytes_from_path(path)

    def test_delete_path(self, temp_repo_path: pathlib.Path):
        """Test deleting a path."""
        engine = LocalStorageEngine(repository=temp_repo_path)
        path = pathlib.Path("file_to_delete.txt")
        data = b"some data"

        # Write a file to be deleted
        engine.write_bytes_to_path(path, data)
        canonical_path = engine.canonicalize_path(path)
        assert canonical_path.exists()

        # Delete the file
        engine.delete_path(path)
        assert not canonical_path.exists()

    def test_delete_nonexistent_path(self, temp_repo_path: pathlib.Path):
        """Test that deleting a non-existent path does not raise an error."""
        engine = LocalStorageEngine(repository=temp_repo_path)
        path = pathlib.Path("nonexistent_file_to_delete.txt")
        canonical_path = engine.canonicalize_path(path)
        assert not canonical_path.exists()

        try:
            engine.delete_path(path)
        except Exception as e:
            pytest.fail(f"Deleting a non-existent path raised an exception: {e}")
