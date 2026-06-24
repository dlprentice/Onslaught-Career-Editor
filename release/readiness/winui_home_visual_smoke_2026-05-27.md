# WinUI visual + Home smoke (2026-05-27)

Status: public-safe evidence summary (screenshots remain private/local)
Date: 2026-05-27
Branch: `main` (debug build on operator workstation)

## What was run

```powershell
dotnet build OnslaughtCareerEditor.WinUI/OnslaughtCareerEditor.WinUI.csproj --nologo
# Primary + scrolled visual captures
dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo `
  --filter "FullyQualifiedName~MainWindow_CapturesPrimaryProductScreens|FullyQualifiedName~MainWindow_CapturesScrolledWorkflowSections" `
  -- NUnit.IncludeExplicit=true NUnit.NumberOfTestWorkers=1
# Home navigation UIA
dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --nologo `
  --filter "FullyQualifiedName~WinUiHomeNavigationSmokeTests" `
  -- NUnit.IncludeExplicit=true NUnit.NumberOfTestWorkers=1
```

## Result

- **PASS** — primary visual (11 PNGs), scrolled visual (7 PNGs), Home navigation UIA (8 tests).
- Evidence dirs aligned to **`2026-05-27`** in `WinUiVisualSmokeTests` (`PrimaryVisualQaDate` / `ScrolledVisualQaDate`).

## Private evidence locations (R4 — do not publish)

| Suite | Path | Files |
| --- | --- | --- |
| Primary tabs | `ignored local visual QA artifact folder` | `01-home.png` … `11-about.png` |
| Scrolled sections | `subagents/winui-scrolled-visual-qa/2026-05-27/` | `01-home-scrolled.png` … `07-about-scrolled.png` |

## What this proves vs does not

| Proves | Does not prove |
| --- | --- |
| Debug WinUI build launches on desktop session | Packaged Release ZIP layout (see ZIP probe docs) |
| Home + primary tabs reachable with expected anchor text | Every Home card workflow end-to-end in retail game |
| Scrolled sections visible after UIA scroll on long pages | Full pixel-perfect layout sign-off |
| Home navigation UIA markers on debug build | MSIX/installer/trusted install readiness |

## Related evidence

- ZIP extracted Release home navigation: `release/readiness/winui_zip_package_probe_2026-05-27.md`
- Lane on `main`: `release/readiness/winui_primary_lane_on_main_2026-05-27.md`
