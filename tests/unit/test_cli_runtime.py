"""Local cancellation, paths, logs and export hardening without live calls."""

import logging
import signal
from pathlib import Path

import pytest

from app_paths import AppPaths, application_paths
from cli_runtime import (
    ExecutionCancelled, LOG_BACKUP_COUNT, LOG_MAX_BYTES,
    configure_rotating_log, controlled_interrupt,
)
from models.business import Business
from models.normalized_business import NormalizedBusiness
from models.search_query import SearchQuery, Source
from models.search_result import SearchResult
from services._export_directory import export_directory
from services.export_service import ExportFormat, ExportService


def test_app_paths_source_root_is_independent_of_cwd(monkeypatch, tmp_path):
    first = application_paths()
    monkeypatch.chdir(tmp_path)
    second = application_paths()
    assert first == second
    assert second.exports == second.root / "exports"
    assert second.logs == second.root / "logs"


def test_rotating_log_is_bounded_and_reconfigurable(tmp_path):
    path = configure_rotating_log(tmp_path / "logs")
    assert path.exists()
    root = logging.getLogger()
    handler = next(h for h in root.handlers if getattr(h, "_prospector_rotating", False))
    assert handler.maxBytes == LOG_MAX_BYTES == 1_000_000
    assert handler.backupCount == LOG_BACKUP_COUNT == 2
    newer = configure_rotating_log(tmp_path / "other logs")
    assert newer.exists() and newer != path
    for h in list(root.handlers):
        if getattr(h, "_prospector_rotating", False):
            root.removeHandler(h)
            h.close()


def test_ctrl_c_no_continues_and_yes_unwinds():
    calls = []
    original = signal.getsignal(signal.SIGINT)
    with controlled_interrupt(lambda: calls.append("no") or False) as cancellation:
        signal.getsignal(signal.SIGINT)(signal.SIGINT, None)
        assert cancellation.requested is False
        calls.append("continued")
    with pytest.raises(ExecutionCancelled):
        with controlled_interrupt(lambda: calls.append("yes") or True) as cancellation:
            signal.getsignal(signal.SIGINT)(signal.SIGINT, None)
            assert cancellation.requested is True
            cancellation.raise_if_requested()
    assert calls == ["no", "continued", "yes"]
    assert signal.getsignal(signal.SIGINT) is original


def _result():
    query = SearchQuery(Source.GOOGLE_MAPS, "cafe", "Tijuana")
    return SearchResult(query, [NormalizedBusiness("CAFE")], original_businesses=[Business("Cafe")])


def test_cli_export_root_repeated_name_and_no_overwrite(tmp_path, monkeypatch):
    monkeypatch.setattr("services.export_service.build_output_filename", lambda query, ext: f"fixed.{ext}")
    with export_directory(tmp_path / "path with spaces" / "exports"):
        first = Path(ExportService.export(_result(), ExportFormat.CSV))
        second = Path(ExportService.export(_result(), ExportFormat.CSV))
    assert first.parent == second.parent == tmp_path / "path with spaces" / "exports"
    assert first.name == "fixed.csv" and second.name == "fixed_2.csv"
    assert first.read_bytes() == second.read_bytes()


def test_failed_single_export_removes_incomplete_file(tmp_path, monkeypatch):
    def failure(self, result, output_path):
        Path(output_path).write_text("partial", encoding="utf-8")
        raise OSError("disk failed")

    monkeypatch.setattr("services.export_service.CsvExporter.export", failure)
    with export_directory(tmp_path):
        with pytest.raises(OSError, match="disk failed"):
            ExportService.export(_result(), ExportFormat.CSV)
    assert list(tmp_path.iterdir()) == []


def test_hostile_query_text_cannot_escape_export_root(tmp_path):
    result = _result()
    result.query.keyword = "../../outside"
    with export_directory(tmp_path / "exports"):
        path = Path(ExportService.export(result, ExportFormat.CSV))
    assert path.parent == tmp_path / "exports"
    assert path.exists()
