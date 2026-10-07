"""P95 controlled menu interaction never executes before confirmation."""

import pytest
import csv
from openpyxl import load_workbook

import main as cli
from engines import prospector_engine
from engines.errors import ProspectorNavigationError
from models.batch import BatchSearchResult
from models.business import Business
from models.source_identity import SourceIdentityEvidence, VerificationState, VerifiedSourceIdentity
from models.search_query import Source
from scraper.google_maps.scraper import _SourceResult


def answers(monkeypatch, values):
    iterator = iter(values)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(iterator))


@pytest.mark.parametrize("third", [False, True])
def test_cli_confirms_two_or_three_queries_before_one_engine_call(monkeypatch, capsys, third):
    values = ["cafes", "Tijuana", "", "hoteles", "Mexicali", "100"]
    if third:
        values += ["y", "restaurantes", "Ensenada", "1"]
    else:
        values += ["n"]
    values += ["y", "3"]  # confirm, skip export
    answers(monkeypatch, values)
    calls = []

    class FakeEngine:
        def __init__(self, config):
            calls.append(("init", config.limit))

        def search_many(self, requests):
            calls.append(("search_many", [(r.query.keyword, r.limit) for r in requests]))
            return BatchSearchResult()

    monkeypatch.setattr(cli, "ProspectorEngine", FakeEngine)
    cli.execute_multiple_searches()
    assert calls == [
        ("init", 50),
        ("search_many", [("cafes", 50), ("hoteles", 100)]
         + ([("restaurantes", 1)] if third else [])),
    ]
    output = capsys.readouterr().out
    assert "q01" in output and "q02" in output
    assert ("q03" in output) is third


def test_cancel_before_confirmation_never_constructs_engine_or_file(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    answers(monkeypatch, ["cafes", "Tijuana", "", "hoteles", "Tijuana", "", "n", "n"])
    monkeypatch.setattr(cli, "ProspectorEngine", lambda config: pytest.fail("Engine started"))
    cli.execute_multiple_searches()
    assert "cancelled" in capsys.readouterr().out
    assert list(tmp_path.iterdir()) == []


def test_invalid_third_limit_rejects_whole_batch_before_engine(monkeypatch, capsys):
    answers(monkeypatch, ["cafes", "Tijuana", "", "hoteles", "Tijuana", "", "y", "bars", "Tijuana", "101"])
    monkeypatch.setattr(cli, "ProspectorEngine", lambda config: pytest.fail("Engine started"))
    cli.execute_multiple_searches()
    assert "maximum permitted limit is 100" in capsys.readouterr().out


def test_menu_offers_multiple_and_keeps_single_search(monkeypatch, capsys):
    answers(monkeypatch, ["3"])
    cli.main()
    output = capsys.readouterr().out
    assert "1) New Search" in output
    assert "2) Multiple Searches" in output
    assert "3) Exit" in output


@pytest.mark.parametrize("format_choice,extension", [("2", "csv"), ("1", "xlsx")])
def test_cli_exports_separate_files_and_empty_suppressed_view(
    monkeypatch, tmp_path, capsys, format_choice, extension,
):
    monkeypatch.chdir(tmp_path)
    answers(monkeypatch, [
        "cafes", "Tijuana", "", "cafes", "Tijuana", "", "n", "y", format_choice,
    ])
    identity = SourceIdentityEvidence(
        VerifiedSourceIdentity(Source.GOOGLE_MAPS, "google_place_id", "same-branch"),
        VerificationState.VERIFIED, "place_id_verified",
    )
    calls = []

    def source(request, limit, **kwargs):
        calls.append(request.keyword)
        return _SourceResult(request, [Business("Cafe")], identities=[identity])

    monkeypatch.setattr(prospector_engine, "_run_google_maps", source)
    cli.execute_multiple_searches()
    assert calls == ["cafes", "cafes"]
    files = sorted(tmp_path.glob(f"*.{extension}"))
    assert len(files) == 2 and files[0].name != files[1].name
    assert any("q01" in path.name for path in files)
    assert any("q02" in path.name for path in files)
    for path in files:
        if extension == "csv":
            with path.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.reader(handle))
        else:
            workbook = load_workbook(path, read_only=True)
            try:
                rows = list(workbook["Businesses"].values)
            finally:
                workbook.close()
        assert len(rows[0]) == 7
        assert len(rows) == (1 if "q02" in path.name else 2)
    assert "1 duplicates suppressed" in capsys.readouterr().out


def test_cli_failed_query_creates_no_file_but_later_query_exports(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    answers(monkeypatch, [
        "A", "Tijuana", "", "B", "Tijuana", "", "y",
        "C", "Tijuana", "", "y", "2",
    ])

    def source(request, limit, **kwargs):
        if request.keyword == "B":
            raise ProspectorNavigationError("sensitive source failure")
        return _SourceResult(
            request, [Business(request.keyword)],
            identities=[SourceIdentityEvidence.unverified()],
        )

    monkeypatch.setattr(prospector_engine, "_run_google_maps", source)
    cli.execute_multiple_searches()
    files = list(tmp_path.glob("*.csv"))
    assert len(files) == 2
    assert not any("q02" in path.name for path in files)
    output = capsys.readouterr().out
    assert "q02: no file for failed query" in output
    assert "sensitive source failure" not in output


def test_cli_io_failure_identifies_query_without_claiming_export_success(monkeypatch, capsys):
    answers(monkeypatch, ["A", "Tijuana", "", "B", "Tijuana", "", "n", "y", "2"])
    monkeypatch.setattr(
        prospector_engine, "_run_google_maps",
        lambda request, limit, **kwargs: _SourceResult(
            request, [Business(request.keyword)],
            identities=[SourceIdentityEvidence.unverified()],
        ),
    )
    monkeypatch.setattr(
        cli.ExportService, "export_batch_entry",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("disk full")),
    )
    cli.execute_multiple_searches()
    output = capsys.readouterr().out
    assert "q01: export failed" in output
    assert "q02: export failed" in output
    assert "q01: google_maps" not in output


def test_cli_interruption_exports_only_safe_prefix(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    answers(monkeypatch, ["A", "Tijuana", "", "B", "Tijuana", "", "n", "y", "2"])

    def source(request, limit, **kwargs):
        if request.keyword == "B":
            raise RuntimeError("internal sensitive detail")
        return _SourceResult(
            request, [Business("A")], identities=[SourceIdentityEvidence.unverified()],
        )

    monkeypatch.setattr(prospector_engine, "_run_google_maps", source)
    cli.execute_multiple_searches()
    assert len(list(tmp_path.glob("*.csv"))) == 1
    output = capsys.readouterr().out
    assert "Batch interrupted at q02" in output
    assert "batch is not complete" in output
    assert "internal sensitive detail" not in output
