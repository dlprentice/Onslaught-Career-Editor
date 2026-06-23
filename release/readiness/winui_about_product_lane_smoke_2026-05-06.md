# WinUI About Product-Lane Smoke - 2026-05-06

Status: pass

Source commit: 09a610ca
Evidence-report commit: 2b5d187596c0bdc4580fc379cbd86e0a7b0bca84

## Objective

Prove the WinUI About page is not only visually present, but testable through native UI Automation and aligned with the current product strategy:

1. launch the WinUI app in an isolated test profile
2. open About directly
3. verify the page identifies WinUI as the primary Windows product lane
4. verify the page keeps archived/historical app lanes out of primary product copy
5. verify the version field is reachable through automation
6. capture private visual evidence without committing screenshots

## Product Changes Covered

- Added stable automation IDs to the About page title, product summary, section headings, product-lane note, retail-behavior note, and version text.
- Added a native WinUI About interaction smoke that launches the app, opens About through the initial-tag route, verifies product-lane copy through UI Automation, and captures an ignored screenshot.
- Extended the static accessibility audit so About page automation IDs are guarded alongside the shell, Save Lab, Patch Bench, Media, Asset Library, Lore, and Settings controls.

No game files, saves, executable files, AppCore formats, archived app lanes, runtime behavior, or release scope changed.

## Focused Smoke Result

Command:

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiAboutInteractionSmokeTests"
```

Working directory:

```text
repo root
```

Result: pass

Important output:

```text
Passed! - Failed: 0, Passed: 1, Skipped: 0, Total: 1, Duration: 3 s
```

What it proves:

- the native WinUI app launches into the About page
- the About page title, product summary, product-lane note, and version text are reachable through UI Automation
- primary About copy describes the app as the primary Windows product and mentions safe copied-executable patching
- the About page does not present Electron, the old Python app, or WPF as primary product lanes
- a screenshot is captured under ignored local evidence storage

## Build And Accessibility Guard Results

Command:

```powershell
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
```

Result: pass

Important output:

```text
Build succeeded.
0 Warning(s)
0 Error(s)
```

Command:

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests|FullyQualifiedName~WinUiAccessibilityAuditTests.PrimaryShellAndLongWorkflowControls_ExposeStableAutomationIds|FullyQualifiedName~WinUiAboutInteractionSmokeTests"
```

Result: pass

Important output:

```text
Passed! - Failed: 0, Passed: 13, Skipped: 0, Total: 13
```

Command:

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName!~LegacyWpf"
```

Result: pass

Important output:

```text
Passed! - Failed: 0, Passed: 39, Skipped: 0, Total: 39, Duration: 29 s
```

What they prove:

- the WinUI product lane still builds after the About automation IDs were added
- the static product-lane and accessibility guard coverage remains green
- active WinUI/runtime/parity UI tests remain green after the About smoke was added

## Visual Evidence

Ignored screenshot:

```text
01-about-product-summary.png
```

Screenshot review summary:

- About opens in the native WinUI shell with the About navigation item selected.
- The first viewport shows the product summary, core capabilities, project notes, and the start of retail behavior notes.
- The version section is below the fold on the captured laptop-sized viewport, but the smoke verifies it through UI Automation.
- The page does not expose archived Electron, old Python GUI/CLI, or WPF lanes as product alternatives.

Screenshots stay ignored under `subagents/` and are not release artifacts.

## Known Notes

- This smoke writes only isolated app configuration and screenshot output under ignored local evidence storage.
- It does not mutate the installed game, original `BEA.exe`, saves, media, or any archived app lane.
- It does not prove signed/trusted installer identity; that remains a packaging proof gap.
