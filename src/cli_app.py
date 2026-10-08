"""Rich presentation adapter for the frozen Prospector Engine contracts."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4
import sys

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from app_paths import application_paths
from cli_runtime import ExecutionCancelled, configure_rotating_log, controlled_interrupt
from engines._observability import ExecutionEvent, observe_execution
from engines.config import EngineConfig, GOOGLE_MAPS_ENGINE_MAX_LIMIT
from engines.errors import BatchInterruptedError, ProspectorError, ProspectorRuntimeError
from engines.prospector_engine import ProspectorEngine
from models.batch import BatchQuery, BatchSearchResult, QueryStatus
from models.search_query import SearchQuery, Source
from services.export_service import ExportFormat, ExportService
from services._export_directory import export_directory
from version import __version__


PAGE_SIZE = 10
DEFAULT_BROWSER_HEADLESS = False  # Edge R04 fallback: two Background navigation failures.
console = Console()


def _prepare_terminal_output(stream) -> None:
    """Keep a legacy Windows code page from aborting result presentation."""
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        try:
            reconfigure(errors="replace")
        except (OSError, ValueError):
            pass


def _ask(prompt: str) -> str:
    try:
        return input(f"{prompt} > ").strip()
    except EOFError:
        console.print("Input closed; exiting Prospector CLI.")
        raise SystemExit(0) from None


def _parse_limit(raw: str) -> int:
    if not raw:
        return 50
    if not raw.isdecimal() or int(raw) <= 0:
        raise ValueError("Limit must be a positive whole number.")
    value = int(raw)
    if value > GOOGLE_MAPS_ENGINE_MAX_LIMIT:
        raise ValueError(f"The maximum permitted limit is {GOOGLE_MAPS_ENGINE_MAX_LIMIT}.")
    return value


@dataclass
class _DraftQuery:
    keyword: str
    location: str
    limit: int

    def as_batch(self) -> BatchQuery:
        return BatchQuery(SearchQuery(Source.GOOGLE_MAPS, self.keyword, self.location), self.limit)


def _capture_query(ordinal: int) -> _DraftQuery | None:
    fields = ["Keyword", "Location", "Limit (default 50, maximum 100)"]
    values = ["", "", ""]
    index = 0
    console.print(f"Search {ordinal} — type 'back' to return to the previous field.")
    while index < len(fields):
        raw = _ask(fields[index])
        if raw.lower() == "back":
            if index == 0:
                return None
            index -= 1
            continue
        if index < 2 and not raw:
            console.print("[yellow]This field is required.[/yellow]")
            continue
        if index == 2:
            try:
                _parse_limit(raw)
            except ValueError as error:
                console.print(f"[yellow]{error}[/yellow]")
                continue
        values[index] = raw
        index += 1
    return _DraftQuery(values[0], values[1], _parse_limit(values[2]))


def _review(drafts: list[_DraftQuery]) -> bool:
    while True:
        table = Table(title="Review searches")
        for heading in ("Query", "Keyword", "Location", "Limit"):
            table.add_column(heading)
        for index, draft in enumerate(drafts, 1):
            table.add_row(f"q{index:02d}", draft.keyword, draft.location, str(draft.limit))
        console.print(table)
        choice = _ask("1) Confirm  2) Edit  3) Back")
        if choice == "1":
            return True
        if choice == "3":
            return False
        if choice != "2":
            console.print("[yellow]Invalid option.[/yellow]")
            continue
        target = 0
        if len(drafts) > 1:
            raw = _ask("Query number to edit")
            if not raw.isdecimal() or not 1 <= int(raw) <= len(drafts):
                console.print("[yellow]Invalid query number.[/yellow]")
                continue
            target = int(raw) - 1
        field = _ask("Edit 1) Keyword  2) Location  3) Limit  4) Back")
        if field == "4":
            continue
        if field not in {"1", "2", "3"}:
            console.print("[yellow]Invalid field.[/yellow]")
            continue
        value = _ask("New value")
        if field in {"1", "2"} and not value:
            console.print("[yellow]This field is required.[/yellow]")
            continue
        if field == "3":
            try:
                drafts[target].limit = _parse_limit(value)
            except ValueError as error:
                console.print(f"[yellow]{error}[/yellow]")
        elif field == "1":
            drafts[target].keyword = value
        else:
            drafts[target].location = value


def _browser_choice() -> bool:
    default = "Background" if DEFAULT_BROWSER_HEADLESS else "Visible"
    while True:
        console.print(f"Browser mode: 1) Background  2) Visible  [Enter: {default}]")
        choice = _ask("Selection")
        if not choice:
            return DEFAULT_BROWSER_HEADLESS
        if choice in {"1", "2"}:
            return choice == "1"
        console.print("[yellow]Invalid browser mode.[/yellow]")


def _effective_configuration(drafts: list[_DraftQuery], headless: bool) -> None:
    table = Table(title="Effective configuration")
    table.add_column("Setting")
    table.add_column("Value")
    table.add_row("Source", "Google Maps")
    table.add_row("Queries", str(len(drafts)))
    for index, draft in enumerate(drafts, 1):
        table.add_row(f"q{index:02d}", f"{draft.keyword} | {draft.location} | limit {draft.limit}")
    table.add_row("Website enrichment", "Enabled")
    table.add_row("Browser", "Background" if headless else "Visible")
    console.print(table)


class _ExecutionView:
    """Translate private events into terminal progress and local summary metrics."""

    def __init__(self, count: int) -> None:
        self.metrics: list[dict[str, int | float | str | bool]] = [dict() for _ in range(count)]
        self.current = 0
        self.progress = Progress(
            SpinnerColumn(), TextColumn("{task.description}"), BarColumn(),
            TimeElapsedColumn(),
            console=console, transient=True,
        )
        self.global_task = self.progress.add_task("Global pipeline: waiting", total=None)
        self.source_task = self.progress.add_task("Source pipeline: waiting", total=None)

    def __enter__(self):
        self.progress.start()
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.progress.stop()

    def __call__(self, event: ExecutionEvent) -> None:
        if event.query_index is not None:
            self.current = event.query_index
        if event.kind == "metric_updated" and event.name and event.value is not None:
            self.metrics[self.current][event.name] = event.value
        if event.kind == "execution_started":
            self.progress.update(
                self.global_task,
                description=f"Global pipeline: search {self.current + 1}/{len(self.metrics)}",
                total=None,
            )
        elif event.kind == "stage_started" and event.stage:
            task = self.source_task if event.stage in {"navigation", "feed", "detail", "website"} else self.global_task
            label = "Source" if task == self.source_task else "Global"
            self.progress.update(task, description=f"{label} pipeline: {event.stage}", total=None)
        elif event.kind == "progress_updated" and event.stage:
            task = self.source_task if event.stage in {"feed", "detail", "website"} else self.global_task
            if event.total is not None:
                self.progress.update(
                    task, description=f"Source pipeline: {event.stage} {event.current or 0}/{event.total}",
                    completed=event.current or 0, total=event.total,
                )
            elif event.current is not None:
                self.progress.update(task, description=f"Source pipeline: {event.stage} ({event.current} observed)", total=None)
        elif event.kind == "stage_completed" and event.stage:
            task = self.source_task if event.stage in {"navigation", "feed", "detail", "website"} else self.global_task
            label = "Source" if task == self.source_task else "Global"
            self.progress.update(task, description=f"{label} pipeline: {event.stage} complete", completed=1, total=1)


def _status_for_result(result) -> str:
    if any(issue.stage == "feed" and issue.code == "partial_results" for issue in result.issues):
        return "PARTIAL"
    return "SUCCESS WITH ISSUES" if result.issues else "SUCCESS"


def _show_metrics(metrics: dict, *, batch: bool = False) -> None:
    names = (
        ("requested_limit", "Requested limit"),
        ("maps_candidates_observed", "Maps candidates observed"),
        ("businesses_extracted", "Businesses extracted"),
        ("businesses_normalized", "Businesses normalized"),
        ("verified_identities", "Verified identities"),
        ("unverified_identities", "Unverified identities"),
        ("duplicates_suppressed", "Duplicates suppressed"),
        ("exportable_businesses", "Exportable businesses"),
        ("recoverable_issue_count", "Recoverable issues"),
        ("query_execution_seconds", "Query time (s)"),
        ("navigation_seconds", "Navigation (s)"),
        ("feed_seconds", "Feed (s)"),
        ("detail_seconds", "Detail (s)"),
        ("website_seconds", "Website (s)"),
    )
    table = Table(show_header=False)
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    for key, label in names:
        if key not in metrics or (key == "duplicates_suppressed" and not batch):
            continue
        value = metrics[key]
        table.add_row(label, f"{value:.2f}" if key.endswith("_seconds") else str(value))
    console.print(table)


def _show_issues(issues) -> None:
    if not issues:
        return
    console.print(f"Recoverable issues: {len(issues)}")
    for issue in issues:
        suffix = f" ({issue.candidate})" if issue.candidate and issue.stage == "normalization" else ""
        console.print(f"  {issue.stage}/{issue.code}{suffix}: {issue.message}")


def _view_rows(rows) -> None:
    if not rows:
        console.print("No exportable results to display.")
        return
    page = 0
    while True:
        start = page * PAGE_SIZE
        table = Table(title=f"Results {start + 1}–{min(start + PAGE_SIZE, len(rows))} of {len(rows)}")
        for heading in ("#", "Name", "Category", "Address", "Phone", "Email", "Website", "Language"):
            table.add_column(heading)
        for index in range(start, min(start + PAGE_SIZE, len(rows))):
            business = rows[index]
            table.add_row(str(index + 1), business.name, business.category or "-", business.address or "-", business.phone or "-", business.email or "-", business.website or "-", business.language or "-")
        console.print(table)
        choices = []
        if start + PAGE_SIZE < len(rows):
            choices.append("N) Next")
        if page > 0:
            choices.append("P) Previous")
        choices.append("B) Back")
        command = _ask("  ".join(choices)).lower()
        if command in {"b", "back"}:
            return
        if command == "n" and start + PAGE_SIZE < len(rows):
            page += 1
        elif command == "p" and page > 0:
            page -= 1
        else:
            console.print("[yellow]No page in that direction.[/yellow]")


def _choose_format() -> ExportFormat | None:
    while True:
        choice = _ask("1) CSV  2) XLSX  3) Back")
        if choice == "1":
            return ExportFormat.CSV
        if choice == "2":
            return ExportFormat.EXCEL
        if choice == "3":
            return None
        console.print("[yellow]Invalid option.[/yellow]")


def _after_export() -> bool:
    return _ask("1) Run another search  2) Main menu") == "1"


def _confirm_cancellation(view: _ExecutionView) -> bool:
    view.progress.stop()
    console.print("[yellow]Cancel current execution?[/yellow]")
    console.print("All unexported results from this execution will be lost.")
    answer = _ask("[y/N]").lower() in {"y", "yes"}
    if not answer:
        view.progress.start()
    else:
        console.print("Cancellation requested; waiting for the current browser operation to finish safely.")
    return answer


def _cancellation_checkpoint(event: ExecutionEvent, cancellation) -> None:
    """Stop between completed source operations, never inside a Playwright call."""
    if event.kind in {"stage_started", "stage_completed", "progress_updated", "checkpoint"}:
        cancellation.raise_if_requested()
    elif event.kind == "metric_updated" and event.name == "cleanup_completed" and event.value is True:
        cancellation.raise_if_requested()


def _single_session(draft: _DraftQuery, headless: bool) -> bool:
    _effective_configuration([draft], headless)
    view = _ExecutionView(1)
    cancellation = None
    try:
        with view, controlled_interrupt(lambda: _confirm_cancellation(view)) as cancellation:
            def observed(event: ExecutionEvent) -> None:
                view(event)
                _cancellation_checkpoint(event, cancellation)

            with observe_execution(observed):
                result = ProspectorEngine(EngineConfig(
                    limit=draft.limit, headless=headless, website_enrichment=True,
                )).search(draft.as_batch().query)
                cancellation.raise_if_requested()
    except ExecutionCancelled as error:
        if getattr(error, "_prospector_cleanup_failed", False):
            console.print("[red]Cancellation cleanup could not be verified. The application will close.[/red]")
            raise SystemExit(1) from error
        console.print("Execution cancelled safely; unexported results were discarded.")
        return False
    except (ValueError, ProspectorError) as error:
        if getattr(error, "_prospector_cleanup_failed", False):
            console.print("[red]Browser cleanup could not be verified. The application will close.[/red]")
            raise SystemExit(1) from error
        if cancellation is not None and cancellation.requested:
            console.print("Execution cancelled safely; unexported results were discarded.")
            return False
        console.print(f"[red]Search failed: {error}[/red]")
        return False
    console.print(Panel(f"{_status_for_result(result)} — {result.total_found} businesses", title="Search summary"))
    _show_metrics(view.metrics[0])
    _show_issues(result.issues)
    while True:
        choice = _ask("1) View Results  2) Export Results  3) Back")
        if choice == "1":
            _view_rows(result.businesses)
        elif choice == "2":
            fmt = _choose_format()
            if fmt is None:
                continue
            try:
                with export_directory(application_paths().exports):
                    filename = ExportService.export(result, fmt)
            except (OSError, ValueError) as error:
                console.print(f"[red]Export failed: {error}[/red]")
                continue
            console.print(f"Export complete ({fmt.value}): {filename}")
            return _after_export()
        elif choice == "3":
            return False
        else:
            console.print("[yellow]Invalid option.[/yellow]")


def _batch_session(drafts: list[_DraftQuery], headless: bool) -> bool:
    _effective_configuration(drafts, headless)
    view = _ExecutionView(len(drafts))
    interrupted = None
    cancellation = None
    try:
        with view, controlled_interrupt(lambda: _confirm_cancellation(view)) as cancellation:
            def observed(event: ExecutionEvent) -> None:
                view(event)
                _cancellation_checkpoint(event, cancellation)

            with observe_execution(observed):
                batch = ProspectorEngine(EngineConfig(headless=headless, website_enrichment=True)).search_many(
                    [draft.as_batch() for draft in drafts],
                )
                cancellation.raise_if_requested()
    except ExecutionCancelled as error:
        if getattr(error, "_prospector_cleanup_failed", False):
            console.print("[red]Cancellation cleanup could not be verified. The application will close.[/red]")
            raise SystemExit(1) from error
        console.print("Batch cancelled safely; unexported results were discarded.")
        return False
    except BatchInterruptedError as error:
        if error.reason_code == "cleanup_failed":
            console.print("[red]Browser cleanup could not be verified. The application will close.[/red]")
            raise SystemExit(1) from error
        if cancellation is not None and cancellation.requested:
            console.print("Batch cancelled safely; unexported results were discarded.")
            return False
        batch = error.completed
        interrupted = error
        console.print(f"[red]BATCH INTERRUPTED at q{error.interrupted_query_index + 1:02d}; remaining queries were not run.[/red]")
        if isinstance(error.__cause__, ProspectorRuntimeError):
            console.print(f"[red]{error.__cause__}[/red]")
            return False
    except (ValueError, ProspectorError) as error:
        if getattr(error, "_prospector_cleanup_failed", False):
            console.print("[red]Browser cleanup could not be verified. The application will close.[/red]")
            raise SystemExit(1) from error
        if cancellation is not None and cancellation.requested:
            console.print("Batch cancelled safely; unexported results were discarded.")
            return False
        console.print(f"[red]Batch failed: {error}[/red]")
        return False
    for index, entry in enumerate(batch.entries):
        console.print(Panel(
            f"q{index + 1:02d} {entry.status.value.upper()} — found {entry.observed_count}, exportable {entry.exportable_count}, suppressed {entry.suppressed_count}",
            title="Query summary",
        ))
        if entry.status is QueryStatus.FAILED:
            console.print(f"  {entry.error.category}: {entry.error.message}")
        else:
            _show_metrics(view.metrics[index], batch=True)
            _show_issues(entry.result.issues)
    console.print(Panel(
        f"Observed {batch.total_observations} | Exportable {batch.total_exportable} | "
        f"Suppressed {batch.duplicates_suppressed} | Unverified {batch.total_unverified} | "
        f"Time {batch.execution_time:.2f}s",
        title="Batch summary",
    ))
    while True:
        choice = _ask("1) View Results  2) Export Results  3) Back")
        if choice == "1":
            for index, entry in enumerate(batch.entries, 1):
                if entry.result is not None:
                    console.print(f"q{index:02d} exportable view")
                    _view_rows([entry.result.businesses[position] for position in entry.export_indices])
        elif choice == "2":
            fmt = _choose_format()
            if fmt is None:
                continue
            operation_id = uuid4().hex
            for index, entry in enumerate(batch.entries, 1):
                if entry.status is QueryStatus.FAILED:
                    console.print(f"q{index:02d}: no file for failed query")
                    continue
                try:
                    with export_directory(application_paths().exports):
                        filename = ExportService.export_batch_entry(entry, fmt, operation_id, index)
                except (OSError, ValueError) as error:
                    console.print(f"[red]q{index:02d}: export failed: {error}[/red]")
                    continue
                console.print(f"q{index:02d}: {filename} ({entry.suppressed_count} duplicates suppressed)")
            if interrupted:
                console.print("Only the safe completed prefix was offered for export; batch is not complete.")
            return _after_export()
        elif choice == "3":
            return False
        else:
            console.print("[yellow]Invalid option.[/yellow]")


def run_app() -> None:
    """Run an interactive session; Engine remains independent of this adapter."""
    _prepare_terminal_output(console.file)
    paths = application_paths()
    try:
        configure_rotating_log(paths.logs)
        paths.exports.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        console.print(f"[red]Application directories are not writable: {error}[/red]")
        return
    while True:
        console.print(Panel(f"Prospector CLI\nv{__version__}", title="Main menu"))
        console.print("1) New Search\n2) Multiple Searches\n3) Exit")
        choice = _ask("Selection")
        if choice == "3":
            console.print("Closing Prospector CLI...")
            return
        if choice not in {"1", "2"}:
            console.print("[yellow]Invalid option.[/yellow]")
            continue
        drafts = []
        count = 1 if choice == "1" else 2
        for ordinal in range(1, count + 1):
            draft = _capture_query(ordinal)
            if draft is None:
                break
            drafts.append(draft)
        if len(drafts) != count:
            continue
        if choice == "2" and _ask("Add a third search? (y/N)").lower() in {"y", "yes"}:
            draft = _capture_query(3)
            if draft is None:
                continue
            drafts.append(draft)
        if not _review(drafts):
            console.print("Search cancelled before execution.")
            continue
        headless = _browser_choice()
        again = _single_session(drafts[0], headless) if choice == "1" else _batch_session(drafts, headless)
        if again:
            continue
