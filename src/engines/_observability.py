"""Private, presentation-neutral execution events for the synchronous pipeline."""

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
import logging


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ExecutionEvent:
    kind: str
    stage: str | None = None
    name: str | None = None
    value: int | float | str | bool | None = None
    current: int | None = None
    total: int | None = None
    query_index: int | None = None


_observer: ContextVar[Callable[[ExecutionEvent], None] | None] = ContextVar(
    "prospector_execution_observer", default=None,
)


@contextmanager
def observe_execution(observer: Callable[[ExecutionEvent], None] | None) -> Iterator[None]:
    """Bind one internal listener without changing public Engine signatures."""
    token = _observer.set(observer)
    try:
        yield
    finally:
        _observer.reset(token)


def emit(event: ExecutionEvent) -> None:
    """Presentation failure must not alter extraction or public results."""
    listener = _observer.get()
    if listener is None:
        return
    try:
        listener(event)
    except Exception:
        logger.exception("Execution observer failed; source execution continues")
