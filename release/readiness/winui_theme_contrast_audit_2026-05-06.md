# WinUI Theme Contrast Audit - 2026-05-06

Status: PASS
Branch: `wip/sandbox`
Source commit before this evidence: `28c155aa`

## Purpose

Record an automated contrast guard for the active WinUI 3 product shell. The repo already had a legacy WPF contrast audit, but that test is archived/reference-only and explicit. This wave adds active coverage for the WinUI theme resources that the current product shell uses.

This is a public-safe evidence summary. It does not include private screenshots, private game paths, save paths, executable paths, raw proof JSON, or game assets.

## What Changed

- Updated `OnslaughtCareerEditor.UiTests/ThemeContrastAuditTests.cs`.
- Added `WinUiShellThemeColors_MeetMinimumContrastThresholds`.
- The test parses `OnslaughtCareerEditor.WinUI/App.xaml` and checks the `Default`, `Dark`, and `Light` theme dictionaries.
- The test verifies minimum contrast ratios for:
  - shell primary text against page and card surfaces
  - muted text against card and muted-card surfaces
  - hero text against hero background
  - accent color against page and card surfaces

## Command

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~ThemeContrastAuditTests.WinUiShellThemeColors_MeetMinimumContrastThresholds"
```

Result: PASS.

Important output:

- Failed: 0
- Passed: 1
- Skipped: 0
- Total: 1

## What This Proves

- Active WinUI shell theme resources meet the encoded minimum contrast thresholds.
- Future changes to `ShellTextBrush`, `ShellMutedTextBrush`, `ShellHeroTextBrush`, `ShellAccentBrush`, and the primary shell surface brushes will be caught by the active UiTests gate if they drop below those thresholds.
- The current product-lane contrast guard no longer depends on archived WPF reference resources.

## What This Does Not Prove

- This is not a complete accessibility certification.
- This does not inspect every page-local color or every transient control state.
- This does not replace visual review, high-contrast Windows theme review, keyboard tab-order review, or screen-reader review.

## Next Recommended QA

- Keep adding focused active WinUI accessibility tests where they map to real product surfaces.
- Consider a later page-local contrast audit if future pages introduce custom colors outside the shared shell theme resources.
- Keep manual accessibility tooling for release-candidate review instead of treating this automated guard as certification.
