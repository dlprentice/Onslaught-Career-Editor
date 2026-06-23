# WinUI Settings Interaction Smoke - 2026-05-06

Status: pass

Source commit: 5b63eb22
Evidence-report commit: c0ffa0f5f53a0129ad2eb75c5a925301069d5b60

## Objective

Prove the WinUI Settings page can drive the normal first-run setup path through native UI Automation without mutating the installed game:

1. launch the WinUI app in an isolated test profile
2. open Settings directly
3. auto-detect the read-only Battle Engine Aquila install
4. keep the primary configured-install summary path-safe
5. expose the full install path only in explicit path details
6. confirm save/options detection copy stays public-safe
7. capture private visual evidence without committing screenshots

## Product Changes Covered

- Added stable automation IDs for Settings setup controls, configured-install summary, status text, path-details disclosure, media behavior toggles, reload action, and settings file details.
- Extended the static accessibility audit so Settings and Lore automation IDs are covered alongside existing shell, Save Lab, Patch Bench, Media, and Asset Library controls.

No game files, saves, executable files, AppCore formats, release scope, or archived app lanes changed.

## Focused Smoke Result

Command:

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiSettingsInteractionSmokeTests"
```

Working directory:

```text
repo root
```

Result: pass

Important output:

```text
Passed! - Failed: 0, Passed: 1, Skipped: 0, Total: 1
```

What it proves:

- the WinUI Settings page launches in the native app
- Auto-Detect sets the configured install using isolated app state
- the install is treated as read-only source material in primary copy
- the primary configured-install summary shows the folder name, not the full absolute path
- save/options detection summary does not expose the full install path
- the full path remains available only after opening explicit path details
- a screenshot is captured under ignored local evidence storage

## Build And Accessibility Guard Results

Command:

```powershell
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
```

Result: pass

Command:

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiAccessibilityAuditTests.PrimaryShellAndLongWorkflowControls_ExposeStableAutomationIds"
```

Result: pass

What they prove:

- the WinUI product lane still builds after the Settings automation IDs were added
- static accessibility guard coverage now includes the Settings and Lore workflow controls

## Visual Evidence

Ignored screenshot:

```text
01-settings-auto-detected.png
```

Screenshot review summary:

- Settings opens in the native shell.
- The configured install summary shows the game folder name in the primary card.
- The status text reports a valid detected install with executable.
- Path details can be opened to show the full install path for users who ask for it.
- The screenshot is private/ignored because it intentionally includes a local install path after expanding path details.

Screenshots stay ignored under `subagents/` and are not release artifacts.

## Known Notes

- This smoke reads the local install path and writes only isolated app configuration under ignored `subagents/` output.
- It does not mutate the installed game, original `BEA.exe`, saves, or media.
- It does not prove signed/trusted install identity; that remains a packaging proof gap.
