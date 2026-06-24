# WinUI 3 migration record

> **SUPERSEDED — archived/historical (2026-05-26):** Electron is **not** the active product surface. WinUI 3 (`OnslaughtCareerEditor.WinUI/`) is the primary user-facing product lane; `archive/electron-workbench/` is archived/reference only. The product-stack table and rules below include a superseded Electron-first snapshot—do not treat them as current direction. Use [three-lane-product-strategy.md](../../roadmap/three-lane-product-strategy.md) and [status-current.md](../../roadmap/status-current.md).

Status: superseded / archived/historical
Version: 2.1
Last updated: 2026-05-01
Replaced by: [electron-workbench-migration.md](../../roadmap/electron-workbench-migration.md), [status-current.md](../../roadmap/status-current.md), [CURRENT_CAPABILITIES.md](../../CURRENT_CAPABILITIES.md)

## Outcome

The WinUI 3 rewrite was an intermediate desktop productization pass. It is no longer the active app direction.

Current product stack:

| Surface | Role | Status |
|---------|------|--------|
| `archive/electron-workbench/apps/electron` + `archive/electron-workbench/packages/ui` | Community/maintainer desktop workbench | Archived reference (was recorded as active product when this note was written) |
| `archive/electron-workbench/packages/contracts` | Typed IPC/job/data contracts | Archived reference |
| `OnslaughtCareerEditor.AppCore` / `.Host` / `.Cli` | C# parity diagnostics | Active support/reference |
| `OnslaughtCareerEditor.WinUI` | Primary Windows product shell | Active product (current) |
| WPF/Python surfaces | Older implementation references | Archived |

## What This Record Still Explains

- Why `OnslaughtCareerEditor.AppCore` exists as a retail-backed comparison point.
- Why early release docs split UI logic from shared save/config/media/lore logic.
- Which WinUI-era behavior may still be useful when checking Electron feature parity.

## Current Rules

> **Historical snapshot:** These rules applied during the superseded Electron-first transition recorded in this file. Current rules: WinUI 3 is the product roadmap; Electron/WPF/Python app lanes stay archived unless explicitly revived.

- Do not use WinUI as the product roadmap.
- Do not add new WinUI/WPF/Python feature work unless a parity investigation explicitly needs it.
- Keep Electron as the app surface and move native/game/debug/Ghidra work through typed IPC/job boundaries.

## Use These Docs Instead

- Electron-first workbench architecture: [electron-workbench-migration.md](../../roadmap/electron-workbench-migration.md)
- Current repo/program posture: [status-current.md](../../roadmap/status-current.md)
- Public roadmap overview: [ROADMAP-INDEX.md](../../roadmap/ROADMAP-INDEX.md)
- Current app surface: [CURRENT_CAPABILITIES.md](../../CURRENT_CAPABILITIES.md)
