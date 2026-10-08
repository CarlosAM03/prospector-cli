"""CLI-only cancellation and bounded local diagnostics."""

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from pathlib import Path
import logging
import signal


LOG_MAX_BYTES = 1_000_000
LOG_BACKUP_COUNT = 2


class ExecutionCancelled(BaseException):
    """Confirmed user cancellation, deliberately outside normal source errors."""


@dataclass
class CancellationState:
    requested: bool = False

    def raise_if_requested(self) -> None:
        if self.requested:
            raise ExecutionCancelled("User confirmed cancellation")


def configure_rotating_log(log_directory: Path) -> Path:
    log_directory.mkdir(parents=True, exist_ok=True)
    path = log_directory / "prospector.log"
    root = logging.getLogger()
    for handler in root.handlers:
        if getattr(handler, "_prospector_rotating", False):
            if Path(handler.baseFilename) == path:
                return path
            root.removeHandler(handler)
            handler.close()
            break
    handler = RotatingFileHandler(
        path, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    handler._prospector_rotating = True
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root.addHandler(handler)
    if root.level > logging.INFO:
        root.setLevel(logging.INFO)
    return path


@contextmanager
def controlled_interrupt(confirm: Callable[[], bool]) -> Iterator[CancellationState]:
    """Defer confirmed Ctrl+C until a safe boundary outside Playwright calls."""
    previous = signal.getsignal(signal.SIGINT)
    state = CancellationState()

    def handler(signum, frame):
        if state.requested:
            return
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            if confirm():
                state.requested = True
        finally:
            signal.signal(signal.SIGINT, handler)

    signal.signal(signal.SIGINT, handler)
    try:
        yield state
    finally:
        signal.signal(signal.SIGINT, previous)
