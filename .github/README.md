# GitHub governance

Prospector CLI v1.0.0 is frozen. Preserve source, tests, dependency pins, historical release documents, annotated tag, release notes and portable asset. Never move/recreate the tag, rewrite history, rebuild/replace the asset or publish a new version during CI maintenance. Product changes need separate authorization.

## Branches and protection

Fetch origin, branch from current main and update by fast-forward only. Submit focused PRs to main, inspect the whole diff and wait for green CI. Preserve local environments, logs and exports outside Git. Never bypass existing review policies.

Ruleset **Protect main: PR and CI**: Active, target **refs/heads/main**, no bypass actors. Require a PR (zero mandatory approvals for this owner-maintained repository unless a stricter existing policy applies), strict up-to-date GitHub Actions checks **quality** and **offline-regression**, block force pushes and deletion. Unit/integration are steps, not independent check contexts.

Verify actual enforcement in Settings > Rules > Rulesets; this document alone does not prove protection. If administration access is unavailable, the owner must create the branch ruleset above, choose Active, enable Restrict deletions, Require a pull request before merging, Require status checks to pass (quality and offline-regression, source GitHub Actions), Require branches to be up to date before merging, and Block force pushes. Leave bypass empty, save and reopen to verify.

## Offline CI

[workflows/ci.yml](workflows/ci.yml) runs on push/PR to main and workflow_dispatch. Full-SHA actions; persist-credentials:false; contents:read only; no secrets, pull_request_target or continue-on-error. Setup downloads require network; tests use controlled fixtures and localhost.

Windows Server 2022 x64, Python **3.13.4**, existing requirements-dev.txt including runtime requirements, Playwright **1.61.0** and pytest **9.1.1**. No dependency upgrade or build dependencies. Effective environment versions are logged. Runner images and Edge Stable evolve. Linux support is not certified.

- **quality**: install existing dependencies, compileall and application import smoke.
- **offline-regression**: verify Edge Stable (official Playwright msedge installer only if absent), production BrowserRuntime offline smoke in Visible/Background modes, unit, integration, full offline suite and process closure check.

The unchanged test_controlled_website_engine.py explicitly launches Chromium against localhost, so CI also installs its headless shell. This does not replace production msedge. test_website_engine.py is an interactive __main__ script, not a collected test; other integration browser paths are mocked. Tests and collection semantics remain unchanged.

Unit/integration share one runner/install to reduce cost. The full python -m pytest -q -m "not e2e" remains the gate. Every pytest invocation gets a fresh UUID basetemp in RUNNER_TEMP outside exports. No live E2E opt-in is set.

Historical release counts (229 unit, 69 integration, 298 offline, one owner-run live E2E) remain historical. Read each CI log for actual results and exclusions. Never report unexecuted tests as PASS.

## Reproduce and investigate

Use a clean checkout and fresh environment:

```powershell
py -3.13 -m venv .git/ci-env
& .git/ci-env/Scripts/Activate.ps1
python -m pip install -r requirements-dev.txt
python -m playwright install chromium --only-shell
# Microsoft Edge Stable must be installed; preserve msedge.
Remove-Item Env:PROSPECTOR_RUN_E2E -ErrorAction SilentlyContinue
$env:PYTHONPATH = Join-Path (Get-Location) "src"
python -m compileall -q src
python -c "import cli_app, cli_runtime, main; from engines.browser_runtime import BrowserRuntime; from engines.prospector_engine import ProspectorEngine; from services.export_service import ExportService"
$base = Join-Path $env:TEMP ("prospector-ci-" + [guid]::NewGuid().ToString("N"))
python -m pytest tests/unit -q -m "not e2e" --basetemp="${base}-unit"
python -m pytest tests/integration -q -m "not e2e" --basetemp="${base}-integration"
python -m pytest -q -m "not e2e" --basetemp="${base}-all"
```

Use short checkout and TEMP paths on Windows. Deep paths can exceed MAX_PATH during relative CSV/XLSX exports even with extended import/compile paths. Check extended paths before diagnosing absent remote files. Do not change frozen product code to hide environment limitations.

Open PR checks or Actions > Prospector CLI offline CI; select the exact commit/attempt and inspect every job/step log. Use Run workflow for manual offline CI. Fix setup failures only in governance files; never suppress failing tests. Record product failures separately for owner authorization; rerun after understanding the cause.

Live Maps E2E remains a separately authorized opt-in (PROSPECTOR_RUN_E2E=1, -m e2e), never automatically triggered or required to merge. CI does not replace owner acceptance.

## Release identity

Baseline: `63e018d0d7ce574f24f3233beadcccd63af5a876`.
Annotated tag object: `35088b4d53c31bb4fdde6c079b5e3d2f31873a32`.
Frozen source: `bd50cf7cbba76ccd75517d06037662dff4797b05`.
Published release ID: `407174696`; asset ID: `622745431`.
Asset: `Prospector-CLI-v1.0.0-win64.zip`, 53,658,917 bytes.
SHA-256: `a219f5a2f9a060a16135b4a61dc3cdc940659111eee1790933e30b7c50245c1c`.
Verify tag target, published state and asset identity after governance changes. Never edit notes or assets. New main CI does not alter original acceptance evidence.
