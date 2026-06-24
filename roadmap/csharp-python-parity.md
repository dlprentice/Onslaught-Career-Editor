# C# / Python Parity Tracker

> **SUPERSEDED:** Historical parity tracking for archived Python GUI and Electron lanes. WinUI 3 + AppCore is the active product path.

Status: superseded
Version: 2.1
Last updated: 2026-05-04

This tracker is historical only.

Replaced by:
- [three-lane-product-strategy.md](three-lane-product-strategy.md)
- [status-current.md](status-current.md)
- [ROADMAP-INDEX.md](ROADMAP-INDEX.md)

Current truth:
- WinUI 3 is the primary user-facing Windows product lane.
- Electron workbench code is archived/reference under `archive/electron-workbench/`; do not treat it as an active product app unless a later explicit strategy decision reactivates it.
- The historical Python GUI/CLI parity app under `archive/legacy-python/` is archived/reference, not an active product or CLI lane.
- `OnslaughtCareerEditor.AppCore`, `OnslaughtCareerEditor.AppCore.Host`, and `OnslaughtCareerEditor.Cli` remain shared correctness/reference support while the Windows lane and automation coverage are stabilized.
- Active Python work should happen as script/tooling work under active utility paths, not by reviving the archived Python app.

Historical validity:
- Keep this file only as a reference for older WPF/Python/C# comparison work.
- Do not use it as a release tracker, app direction document, staffing plan, or validation source.
