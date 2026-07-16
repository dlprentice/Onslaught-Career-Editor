# App delivery phases

> **SUPERSEDED:** Historical phased delivery plan. Current truth: [three-lane-product-strategy.md](three-lane-product-strategy.md) and [status-current.md](status-current.md).

Status: superseded
Last updated: 2026-05-04

This document used to track the older WinUI/AppCore/CLI shipping plan. It remains historical, but the current strategy has returned WinUI 3 to the primary product lane while archiving Electron/WPF/Python GUI app detours and keeping active Python scripts as lab/tooling support.

Current delivery truth lives in:

- [three-lane-product-strategy.md](three-lane-product-strategy.md)
- [status-current.md](status-current.md)
- [RELEASE_SCOPE_AND_TEST_COMMANDS.md](/RELEASE_SCOPE_AND_TEST_COMMANDS.md)
- [release/readiness/release_readiness_checklist.md](/release/readiness/release_readiness_checklist.md)

## Historical summary

The old plan completed useful work:

- hardened AppCore and CLI validation against retail-backed save/options rules
- established a WinUI shell with saves, media, lore, patch, settings, and about areas
- archived WPF app material and Python scripts under `archive/`
- produced release allowlist tooling that still helps classify public/private paths

That work now serves as historical context for the reactivated WinUI lane. The current roadmap is the three-lane strategy, not this older phased plan.

## Current replacement plan

The three-lane strategy owns the active app surface:

- WinUI 3 product lane: primary user-facing Windows app
- archived Electron workbench: historical typed workbench/reference material under `archive/electron-workbench/`
- Python script/tooling lane: RE/tooling/lab support through active utility paths
- public safety/export lane: curated source/export boundary with private families denied

## Validation replacement

Use lane gates intentionally. WinUI health starts with:

```powershell
dotnet build ".\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj"
dotnet test ".\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj"
```

Use archived Electron gates only when intentionally inspecting that archive:

```powershell
npm run typecheck
npm run archive:electron:build:main
npm run archive:electron:test:parity
npm run archive:electron:build
```

Run C# support/parity gates while AppCore/CLI/AppCore.Host remain useful:

```powershell
dotnet build ".\OnslaughtCareerEditor.Release.slnx"
dotnet test ".\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj"
dotnet test ".\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj"
```

Archived WinUI bundle validation is reference-only and must not be confused with current WinUI product-lane health.
