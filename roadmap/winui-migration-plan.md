# WinUI 3 Migration Record

> Status: completed / archived as active planning guidance
> Last updated: 2026-03-11
> Replaced by: [status-current.md](status-current.md), [ROADMAP-INDEX.md](ROADMAP-INDEX.md), [../CURRENT_CAPABILITIES.md](../CURRENT_CAPABILITIES.md)

## Outcome

The WinUI 3 rewrite is now the shipping desktop product direction.

Current product stack:

| Project | Role | Status |
|---------|------|--------|
| `OnslaughtCareerEditor.WinUI` | Shipping Windows desktop app | **Active product** |
| `OnslaughtCareerEditor.AppCore` | Shared retail-backed non-UI logic | **Active** |
| `OnslaughtCareerEditor.Cli` | Supported command-line host | **Active** |

## What This Migration Closed

- WinUI now owns the desktop shell and all primary product surfaces:
  - `Saves`
  - `Media`
  - `Lore`
  - `Binary Patches`
  - `Settings`
  - `About`
- Shared save/config/media/lore logic lives in `OnslaughtCareerEditor.AppCore`.
- CLI responsibility was removed from the legacy desktop host and lives in `OnslaughtCareerEditor.Cli`.
- Public-release shaping now excludes WPF and Python app surfaces.

## Constraints That Carried Forward

These migration rules remain true even though the migration itself is now considered complete:

- `BesFilePatcher.cs` semantics remain authoritative through the shared core.
- `.bes` and `defaultoptions.bea` behavior must stay retail-backed and distinct.
- Binary patch verify/apply/restore remains catalog-driven and byte-verified.
- Save patching continues to preserve known fixes such as packed kill metadata and previously corrected goodie handling.

## Historical Notes

This document is retained to explain why the current structure exists:

- `OnslaughtCareerEditor.AppCore` was introduced to stop UI rewrites from risking retail-backed logic.
- `OnslaughtCareerEditor.Cli` was split out so release validation could stay independent of the desktop shell.
- `Media` and `Lore` required platform-specific adaptation rather than direct WPF porting.
- UI parity work was intentionally treated as a staged productization effort, not a blind XAML reskin.

## Use These Docs Instead Now

- Current repo/program posture: [status-current.md](status-current.md)
- Public roadmap overview: [ROADMAP-INDEX.md](ROADMAP-INDEX.md)
- Current app surface: [../CURRENT_CAPABILITIES.md](../CURRENT_CAPABILITIES.md)
