# Prospector CLI v1.0.0 — Owner acceptance and repository freeze handoff

Owner decision: **R20 OWNER ACCEPTED** for the intended first stable CLI scope. The independent branch freeze audit subsequently passed; see [the canonical freeze record](../../releases/v1.0.0/FREEZE.md). Publication was completed afterward; this preserves the original acceptance decision and records the later publication state below.

| Item | Accepted record |
|---|---|
| Implementation source commit | `0499f9f308617b68a859925759e389fca6b3cc8e` |
| Portable artifact | `Prospector-CLI-v1.0.0-win64.zip` |
| Size | 53,658,917 bytes |
| SHA-256 | `A219F5A2F9A060A16135B4A61DC3CDC940659111EEE1790933E30B7C50245C1C` |
| Offline regression at acceptance | 229 unit, 69 integration, 298 full PASS; one live E2E deselected; compileall and diff check PASS |
| Gate state | R01–R07, R09–R14, R16–R19 PASS; R15 OPTIONAL_SKIPPED; **R08 OWNER_WAIVED / DEFERRED_POST_RELEASE**; **R20 OWNER ACCEPTED** |

The owner explicitly accepted the risk of no separate clean/isolated Windows-machine test before the first release. R08 was **not executed and is not PASS**. The package was validated on the primary Windows host and by relocation there; future machine-specific Windows, Microsoft Edge or enterprise-policy issues are post-release compatibility/maintenance matters. Installed Microsoft Edge Stable is required, Visible is the default and Background remains available; no browser executable is redistributed. R10 forced-console-close cleanup is best effort. Google Maps can return partial results; exact verified-identity deduplication deliberately retains `UNVERIFIED` observations that may appear commercially duplicated. There is no persistence, checkpoint/resume or auto-update.

This repository-closure phase changed documentation and Git attributes only. Public Engine/model/result/error/export contracts and the seven-column CSV/XLSX schema were not modified; the durable v1.0.0 regression remains entirely under `tests/` and was rerun offline at 229/69/298 PASS with one E2E deselected.

At acceptance time, the artifact was a local owner-tested ZIP. Earlier `ReleaseCandidateReport.md` records pre-R20/pre-freeze-audit state; the RC report's machine-specific absolute ZIP path was replaced by its artifact filename for portability. The owner decision and [freeze record](../../releases/v1.0.0/FREEZE.md) supersede those historical pending labels.

## Publication closure

- Tag: `v1.0.0`
- Freeze audit: **PASS**
- GitHub Release: **PUBLISHED** — [Prospector CLI v1.0.0](https://github.com/CarlosAM03/prospector-cli/releases/tag/v1.0.0)
- Windows portable: **PUBLISHED** — `Prospector-CLI-v1.0.0-win64.zip`
- Publication: **COMPLETE**

See the canonical [release closure](../../releases/v1.0.0/RELEASED.md).
