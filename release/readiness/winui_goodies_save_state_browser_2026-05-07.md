# WinUI Goodies Save-State Browser Evidence - 2026-05-07

## Scope

This pass connected the WinUI Asset Library Goodies tab to explicit save-state analysis. It does not run BEA, mutate `BEA.exe`, patch the installed game, mutate a Ghidra project, or commit private saves/assets/screenshots.

## What Changed

- The Goodies tab now exposes an optional `Save state for Goodies` control.
- By default, Goodies rows remain honest with `State not loaded`.
- Loading a copied `.bes` file analyzes the save through `BesFilePatcher.AnalyzeSave`.
- Goodies list rows and the selected summary now show `Locked`, `Instructions`, `New`, or `Old` only when those states come from the selected save analysis.
- The visible browser remains catalog-backed for identity/title/model/texture/video links and save-backed for lock/view state.

## Visual Evidence

Screenshot stayed ignored/private:

- `ignored local visual QA screenshot (07-asset-library-goodies.png)`

Public-safe screenshot review:

- The Asset Library Goodies tab shows a loaded synthetic save-state fixture.
- The selected Goodie row shows `New; Model; fixture_mesh.msh`.
- The selected summary states `save state: new` and still labels the model preview as a lightweight geometry check, not final material/animation rendering.

## Commands Run

```powershell
dotnet build OnslaughtCareerEditor.WinUI/OnslaughtCareerEditor.WinUI.csproj --nologo
```

Result: pass.

```powershell
dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests|FullyQualifiedName~WinUiAccessibilityAuditTests"
```

Result: pass, `21` tests.

```powershell
dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiVisualSmokeTests.MainWindow_CapturesPrimaryProductScreens"
```

Result: fail once on stale exact expected text for the Asset Library summary after Goodies count was added, then pass after correcting the visual-smoke expectation. Final result: pass, `1` test.

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

- The WinUI Goodies browser can combine generated catalog identity with typed save-state analysis.
- The UI does not pretend save lock state exists until a `.bes` file is loaded.
- The native visual smoke covers the loaded-save-state Goodies path with a deterministic fixture.

## Not Proven Yet

- Runtime Goodies unlock behavior.
- Full textured or animated Goodies model viewing.
- Exhaustive Goodies row-by-row preview against a private real save.
- Public redistribution of extracted Goodies assets.
