# WinUI Save Goodies State Foundation Evidence - 2026-05-07

## Scope

This pass added the save-state half of the Goodies browser foundation. It does not run BEA, mutate `BEA.exe`, patch the installed game, mutate a Ghidra project, or commit private saves/assets.

## What Changed

- `BesFilePatcher.AnalyzeSave` now records every raw `CGoodie[300]` dword with its true-view file offset.
- Displayable Goodies slots are modeled as indices `0-232`; indices `233-299` remain reserved/preserve rows.
- Save analysis now exposes per-slot state labels: `Locked`, `Instructions`, `New`, `Old`, `Other`, and `Reserved`.
- `SaveAnalyzerService` carries displayable Goodies state rows in the analyzer document and includes active slots in the summary tree.
- Save-format documentation now records the split between catalog identity and save-state lock/new/old state.

## Public-Safe Technical Result

- Goodie slot base offset: `0x1F46`.
- Displayable slots: `233`.
- Reserved/preserve slots: `67`.
- Known retail state values: `0=Locked`, `1=Instructions`, `2=New`, `3=Old`.

## Commands Run

```powershell
dotnet test OnslaughtCareerEditor.AppCore.Tests/OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter SaveAnalyzerServiceTests
```

Result: pass, `13` tests.

```powershell
dotnet build OnslaughtCareerEditor.WinUI/OnslaughtCareerEditor.WinUI.csproj --nologo
```

Result: pass.

```powershell
npm run test:winui-primary-lane
```

Result: pass. The wrapper built `OnslaughtCareerEditor.WinUI.slnx`, ran AppCore tests (`31 / 31`), ran active UiTests (`47 / 47`), and shut down build servers.

```powershell
npm run test:md-links
npm run test:doc-commands
py -3 tools/docsync_check.py
npm run test:repo-hygiene
npm run test:public-allowlist
py -3 tools/release_curated_manifest.py --check
py -3 tools/release_profile_snapshot.py --check
```

Result: pass.

## What This Proves

- AppCore can decode Goodies unlock/view state from a real-shaped save buffer using the true dword view.
- The WinUI analyzer data contract can now support a future save-aware Goodies browser without reinterpreting offsets in the UI layer.
- Reserved Goodies rows are preserved as raw rows instead of being treated as displayable unlocks.

## Not Proven Yet

- A visible WinUI wall/grid that combines the catalog rows with a selected save's state.
- Runtime Goodies unlock behavior.
- Full textured or animated Goodies model viewing.
- Public redistribution of extracted Goodies assets.
