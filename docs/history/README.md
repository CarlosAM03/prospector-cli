# Engineering history

These tracked records preserve the decisions, accepted contracts, release gates and owner acceptance needed to understand the current code after a fresh clone. They are selected snapshots, not a copy of the ignored `temp/Planeacion/` workspace. The files within each version remain historical: a `PENDING` or `BLOCKED` line in an earlier runbook or audit describes that point in time, not the current release state. Later owner decisions and the version's acceptance record supersede earlier planning status.

| Version | Canonical history |
|---|---|
| [v0.7.x](v0.7.x/) | Stabilization plan, architecture/final acceptance audits, checkpoint and matrix |
| [v0.8.0](v0.8.0/) | ADR-008, normalization design/runbook, matrix and owner acceptance with N31 caveat |
| [v0.9.0](v0.9.0/) | ADR-009, multi-query design/runbook, P92 identity evidence, matrix and owner closure |
| [v1.0.0](v1.0.0/) | ADR-010, final design/runbook, R09/R10/R19 evidence, matrix, RC report and [owner acceptance](v1.0.0/OWNER_ACCEPTANCE.md) |

The tracked documents here and in [`docs/releases/`](../releases/) are the durable repository record. Ignored `temp/` copies, raw XML/logs, browser probes, build directories and exports remain local evidence or artifacts; no test or build instruction requires them as source inputs. The accepted Windows ZIP is published as an external [v1.0.0 GitHub Release asset](https://github.com/CarlosAM03/prospector-cli/releases/tag/v1.0.0), not stored in Git history.
