import abc
import pathlib
from typing import TypeVar

PathType = TypeVar("PathType")


class BaseStorageEngine[PathType](abc.ABC):
    @property
    @abc.abstractmethod
    def repository(self) -> PathType:
        raise NotImplementedError

    @abc.abstractmethod
    def canonicalize_path(self, path: pathlib.Path) -> PathType:
        raise NotImplementedError

    @abc.abstractmethod
    def write_bytes_to_path(self, path: pathlib.Path, data: bytes) -> int:
        raise NotImplementedError

    def write_text_to_path(
        self,
        path: pathlib.Path,
        data: str,
        encoding: str = "utf-8",
        errors: str = "strict",
    ) -> int:
        return self.write_bytes_to_path(path, data.encode(encoding, errors))

    @abc.abstractmethod
    def read_bytes_from_path(self, path: pathlib.Path) -> bytes:
        raise NotImplementedError

    def read_text_from_path(
        self,
        path: pathlib.Path,
        encoding: str = "utf-8",
        errors: str = "strict",
    ) -> str:
        return self.read_bytes_from_path(path).decode(encoding, errors)

    @abc.abstractmethod
    def delete_path(self, path: pathlib.Path) -> None:
        raise NotImplementedError
