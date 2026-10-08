"""Semantic tests for the v1 Rich adapter, independent of styling."""

from io import BytesIO, TextIOWrapper
import signal
import pytest

from rich.console import Console

import cli_app
from engines._observability import ExecutionEvent, emit
from engines.errors import ProspectorNavigationError, ProspectorRuntimeError
from models.batch import BatchQueryResult, BatchSearchResult, QueryFailure, QueryStatus
from models.business import Business
from models.normalized_business import NormalizedBusiness
from models.search_issue import SearchIssue
from models.search_result import SearchResult


def _answers(monkeypatch, values):
    iterator = iter(values)
    monkeypatch.setattr(cli_app, "_ask", lambda prompt: next(iterator))


def test_main_menu_version_and_exit(monkeypatch, capsys):
    _answers(monkeypatch, ["3"])
    cli_app.run_app()
    output = capsys.readouterr().out
    assert "Prospector CLI" in output
    assert "v1.0.0" in output
    assert "New Search" in output and "Multiple Searches" in output


def test_closed_input_exits_without_traceback(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda prompt: (_ for _ in ()).throw(EOFError()))
    try:
        cli_app.run_app()
    except SystemExit as error:
        assert error.code == 0
    else:
        raise AssertionError("closed input did not exit")
    assert "Input closed" in capsys.readouterr().out


def test_single_edit_confirmation_browser_mode_and_repeated_menu(monkeypatch, capsys):
    _answers(monkeypatch, [
        "1", "cafe", "Tijuana", "", "2", "1", "bakery", "1", "1", "3", "3",
    ])
    calls = []

    class FakeEngine:
        def __init__(self, config):
            calls.append(config)

        def search(self, query):
            calls.append(query)
            return SearchResult(query, [NormalizedBusiness("BAKERY")],
                                original_businesses=[Business("bakery")])

    monkeypatch.setattr(cli_app, "ProspectorEngine", FakeEngine)
    cli_app.run_app()
    assert calls[0].limit == 50 and calls[0].headless is True
    assert calls[1].keyword == "bakery" and calls[1].location == "Tijuana"
    output = capsys.readouterr().out
    assert "Effective configuration" in output
    assert "Search summary" in output
    assert "BAKERY" not in output  # No automatic result flood.


def test_back_before_confirmation_never_constructs_engine(monkeypatch):
    _answers(monkeypatch, ["1", "cafe", "Tijuana", "", "3", "3"])
    monkeypatch.setattr(cli_app, "ProspectorEngine", lambda config: (_ for _ in ()).throw(
        AssertionError("Engine started before confirmation")
    ))
    cli_app.run_app()


def test_batch_two_queries_keeps_engine_limit_and_visible_mode(monkeypatch):
    _answers(monkeypatch, [
        "2", "cafe", "Tijuana", "", "hotel", "Mexicali", "100", "n", "1", "2", "3", "3",
    ])
    calls = []

    class FakeEngine:
        def __init__(self, config):
            calls.append(config)

        def search_many(self, requests):
            calls.append(requests)
            return BatchSearchResult()

    monkeypatch.setattr(cli_app, "ProspectorEngine", FakeEngine)
    cli_app.run_app()
    assert calls[0].headless is False
    assert [request.limit for request in calls[1]] == [50, 100]
    assert len(calls[1]) == 2


def test_edge_launch_failure_is_controlled_in_single_cli(monkeypatch, capsys):
    _answers(monkeypatch, ["1", "cafe", "Tijuana", "", "1", "1", "3"])

    class FakeEngine:
        def __init__(self, config):
            assert config.headless is True

        def search(self, query):
            raise ProspectorRuntimeError("Microsoft Edge Stable is required. Install or restore Edge.")

    monkeypatch.setattr(cli_app, "ProspectorEngine", FakeEngine)
    cli_app.run_app()
    output = capsys.readouterr().out
    assert "Microsoft Edge Stable is required" in output
    assert "Traceback" not in output


def test_confirmed_ctrl_c_defers_until_safe_pipeline_event(monkeypatch, capsys):
    _answers(monkeypatch, ["1", "cafe", "Tijuana", "", "1", "2", "y", "3"])

    class FakeEngine:
        def __init__(self, config):
            pass

        def search(self, query):
            signal.getsignal(signal.SIGINT)(signal.SIGINT, None)
            emit(ExecutionEvent("stage_completed", "navigation"))
            raise AssertionError("cancelled execution continued past safe event")

    monkeypatch.setattr(cli_app, "ProspectorEngine", FakeEngine)
    cli_app.run_app()
    output = capsys.readouterr().out
    assert "Cancellation requested" in output
    assert "Execution cancelled safely" in output


def test_cancellation_checkpoint_ignores_metrics_until_safe_boundary():
    from cli_runtime import CancellationState, ExecutionCancelled

    cancellation = CancellationState(requested=True)
    cli_app._cancellation_checkpoint(
        ExecutionEvent("metric_updated", name="maps_candidates_observed", value=1),
        cancellation,
    )
    with pytest.raises(ExecutionCancelled):
        cli_app._cancellation_checkpoint(
            ExecutionEvent("progress_updated", "detail", current=1), cancellation,
        )
    with pytest.raises(ExecutionCancelled):
        cli_app._cancellation_checkpoint(ExecutionEvent("checkpoint", "feed"), cancellation)


def test_confirmed_cancel_on_bounded_navigation_failure_reports_cancel(monkeypatch, capsys):
    _answers(monkeypatch, ["1", "cafe", "Tijuana", "", "1", "2", "y", "3"])

    class FakeEngine:
        def __init__(self, config):
            pass

        def search(self, query):
            signal.getsignal(signal.SIGINT)(signal.SIGINT, None)
            raise ProspectorNavigationError("bounded navigation failed after cancellation")

    monkeypatch.setattr(cli_app, "ProspectorEngine", FakeEngine)
    cli_app.run_app()
    output = capsys.readouterr().out
    assert "Execution cancelled safely" in output
    assert "Search failed" not in output


def test_cleanup_failure_closes_cli_instead_of_claiming_safe_cancel(monkeypatch, capsys):
    _answers(monkeypatch, ["1", "cafe", "Tijuana", "", "1", "2"])

    class FakeEngine:
        def __init__(self, config):
            pass

        def search(self, query):
            failure = ProspectorRuntimeError("Browser runtime failed")
            failure._prospector_cleanup_failed = True
            raise failure

    monkeypatch.setattr(cli_app, "ProspectorEngine", FakeEngine)
    try:
        cli_app.run_app()
    except SystemExit as error:
        assert error.code == 1
    else:
        raise AssertionError("cleanup failure did not close the CLI")
    output = capsys.readouterr().out
    assert "cleanup could not be verified" in output
    assert "cancelled safely" not in output


def test_edge_r04_visible_default_and_both_modes_offered(monkeypatch, capsys):
    _answers(monkeypatch, [""])
    assert cli_app._browser_choice() is False
    output = capsys.readouterr().out
    assert "Background" in output and "Visible" in output
    assert "Enter: Visible" in output


def test_viewer_paginates_ten_rows(monkeypatch, capsys):
    _answers(monkeypatch, ["n", "n", "p", "b"])
    cli_app._view_rows([NormalizedBusiness(f"BUSINESS {index}") for index in range(21)])
    output = capsys.readouterr().out
    assert "BUSINESS 0" in output and "BUSINESS 20" in output
    assert output.count("BUSINESS 10") >= 1
    assert "BUSINESS 9" in output


def test_viewer_only_offers_available_navigation(monkeypatch, capsys):
    prompts = []
    answers = iter(["n", "n", "b"])

    def ask(prompt):
        prompts.append(prompt)
        return next(answers)

    monkeypatch.setattr(cli_app, "_ask", ask)
    cli_app._view_rows([NormalizedBusiness(f"BUSINESS {index}") for index in range(21)])
    assert prompts == [
        "N) Next  B) Back",
        "N) Next  P) Previous  B) Back",
        "P) Previous  B) Back",
    ]
    output = capsys.readouterr().out
    assert "Results 1–10 of 21" in output
    assert "Results 11–20 of 21" in output
    assert "Results 21–21 of 21" in output


def test_viewer_single_page_only_offers_back(monkeypatch):
    prompts = []
    monkeypatch.setattr(cli_app, "_ask", lambda prompt: prompts.append(prompt) or "b")
    cli_app._view_rows([NormalizedBusiness("ONE")])
    assert prompts == ["B) Back"]


def test_viewer_survives_legacy_windows_code_page(monkeypatch):
    output = TextIOWrapper(BytesIO(), encoding="cp1252", errors="strict")
    cli_app._prepare_terminal_output(output)
    monkeypatch.setattr(cli_app, "console", Console(file=output, force_terminal=False, width=80))
    _answers(monkeypatch, ["b"])
    cli_app._view_rows([NormalizedBusiness("CAFE\u202fCENTRAL")])
    output.flush()
    assert b"CAFE?CENTRAL" in output.buffer.getvalue()


def test_invalid_menu_option_and_third_batch_query(monkeypatch, capsys):
    _answers(monkeypatch, [
        "x", "2", "cafe", "Tijuana", "", "hotel", "Mexicali", "", "y",
        "shop", "Ensenada", "1", "1", "1", "3", "3",
    ])
    calls = []

    class FakeEngine:
        def __init__(self, config):
            pass

        def search_many(self, requests):
            calls.append(requests)
            return BatchSearchResult()

    monkeypatch.setattr(cli_app, "ProspectorEngine", FakeEngine)
    cli_app.run_app()
    assert len(calls[0]) == 3
    assert "Invalid option" in capsys.readouterr().out


def test_single_export_and_repeated_execution(monkeypatch, capsys):
    _answers(monkeypatch, [
        "1", "cafe", "Tijuana", "", "1", "1", "2", "1", "2",
        "1", "hotel", "Mexicali", "", "1", "2", "3", "3",
    ])
    calls = []

    class FakeEngine:
        def __init__(self, config):
            calls.append(("config", config.headless))

        def search(self, query):
            calls.append(("search", query.keyword))
            return SearchResult(query)

    monkeypatch.setattr(cli_app, "ProspectorEngine", FakeEngine)
    monkeypatch.setattr(cli_app.ExportService, "export", lambda result, format: "exports/prospect.csv")
    cli_app.run_app()
    assert [item for item in calls if item[0] == "search"] == [
        ("search", "cafe"), ("search", "hotel"),
    ]
    assert "Export complete" in capsys.readouterr().out


def test_partial_and_failed_statuses_are_visible(monkeypatch, capsys):
    _answers(monkeypatch, [
        "1", "cafe", "Tijuana", "", "1", "1", "3",
        "2", "A", "Tijuana", "", "B", "Tijuana", "", "n", "1", "2", "3", "3",
    ])

    class FakeEngine:
        def __init__(self, config):
            pass

        def search(self, query):
            return SearchResult(query, issues=[SearchIssue("feed", "partial_results", "Safe partial")])

        def search_many(self, requests):
            return BatchSearchResult([
                BatchQueryResult(
                    request=requests[0], status=QueryStatus.FAILED,
                    error=QueryFailure("navigation", "The source could not complete this query."),
                ),
            ])

    monkeypatch.setattr(cli_app, "ProspectorEngine", FakeEngine)
    cli_app.run_app()
    output = capsys.readouterr().out
    assert "PARTIAL" in output
    assert "FAILED" in output
    assert "Safe partial" in output
