"""Private CLI-selected export root; programmatic service defaults remain unchanged."""

from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path


_directory: ContextVar[Path | None] = ContextVar("prospector_export_directory", default=None)


@contextmanager
def export_directory(path: Path):
    token = _directory.set(path)
    try:
        yield
    finally:
        _directory.reset(token)


def active_export_directory() -> Path | None:
    return _directory.get()
