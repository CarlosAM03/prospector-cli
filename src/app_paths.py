"""Portable-aware application paths, separate from prospecting semantics."""

from dataclasses import dataclass
from pathlib import Path
import sys


@dataclass(frozen=True)
class AppPaths:
    root: Path
    resources: Path

    @property
    def exports(self) -> Path:
        return self.root / "exports"

    @property
    def logs(self) -> Path:
        return self.root / "logs"

def application_paths() -> AppPaths:
    if getattr(sys, "frozen", False):
        return AppPaths(Path(sys.executable).resolve().parent,
                        Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent)).resolve())
    return AppPaths(Path(__file__).resolve().parents[1], Path(__file__).resolve().parents[1])
