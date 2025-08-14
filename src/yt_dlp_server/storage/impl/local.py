import pathlib
import tempfile

from pydantic import BaseModel, ConfigDict, PrivateAttr

from yt_dlp_server.storage.base import BaseStorageEngine


class LocalStorageEngine(BaseModel, BaseStorageEngine[pathlib.Path]):
    model_config = ConfigDict(frozen=True)

    _repository: pathlib.Path = PrivateAttr(
        default_factory=lambda: pathlib.Path(tempfile.mkdtemp(prefix="yt-dlp-server-"))
    )

    def __init__(self, repository: pathlib.Path | None = None, **data: object) -> None:
        super().__init__(**data)
        if repository is not None:
            self._repository = repository

    @property
    def repository(self) -> pathlib.Path:
        return self._repository

    def canonicalize_path(self, path: pathlib.Path) -> pathlib.Path:
        return self.repository / path

    def write_bytes_to_path(self, path: pathlib.Path, data: bytes) -> int:
        canonical_path = self.canonicalize_path(path)
        canonical_path.parent.mkdir(parents=True, exist_ok=True)
        with open(canonical_path, "wb") as f:
            return f.write(data)

    def read_bytes_from_path(self, path: pathlib.Path) -> bytes:
        canonical_path = self.canonicalize_path(path)
        with open(canonical_path, "rb") as f:
            return f.read()

    def delete_path(self, path: pathlib.Path) -> None:
        canonical_path = self.canonicalize_path(path)
        if canonical_path.exists():
            canonical_path.unlink()
