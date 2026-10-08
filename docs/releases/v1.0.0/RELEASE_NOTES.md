# Prospector CLI v1.0.0 — Release Notes

**Status: STABLE / RELEASED**

Tag: `v1.0.0`\
Frozen source: `bd50cf7cbba76ccd75517d06037662dff4797b05`\
Release: [Prospector CLI v1.0.0](https://github.com/CarlosAM03/prospector-cli/releases/tag/v1.0.0)

Portable: `Prospector-CLI-v1.0.0-win64.zip` (53,658,917 bytes)\
SHA-256: `A219F5A2F9A060A16135B4A61DC3CDC940659111EEE1790933E30B7C50245C1C`

Prospector CLI v1.0.0 is the owner-accepted first stable **CLI scope**. The source release is frozen, the independent freeze audit passed, and publication is complete.

The CLI searches Google Maps with either one query or a bounded sequential multi-query batch. It extracts original `Business` values, optionally enriches them from business websites, then applies mandatory deterministic normalization to an independent `NormalizedBusiness` view. Python consumers retain both views. In batches, verified Google Maps place identity supports strict cross-query duplicate suppression; `UNVERIFIED` observations are retained. CSV and XLSX exports use the same seven columns: Name, Category, Address, Phone, Email, Website, Language.

The Rich terminal interface provides input review/edit/back, Visible-by-default or Background browser mode, global/source progress, metrics, summaries, result pagination, independent batch exports, controlled Ctrl+C confirmation and local `exports/` and rotating `logs/`. The Windows portable contains the application and Python runtime but **not a browser executable**: installed Microsoft Edge Stable is required. See [portable usage](../../portable-windows.md) and [known limitations](KNOWN_LIMITATIONS.md).

At owner acceptance, source validation recorded 229 unit, 69 integration and 298 full offline tests passing, with one opt-in live E2E deselected. The owner separately recorded one live E2E PASS. Packaged functional smoke passed on the primary Windows host. Separate clean-machine validation was explicitly waived by the owner for this initial release and deferred to post-release compatibility testing; it is not recorded as PASS. See [known limitations](KNOWN_LIMITATIONS.md) and [the freeze record](FREEZE.md).
