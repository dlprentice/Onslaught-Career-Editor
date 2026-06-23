# WinUI Semantic Status Brushes - 2026-05-06

Status: PASS
Branch: `wip/sandbox`
Source commit before this evidence: `8998af2f`

## Purpose

Record a focused WinUI maintainability and accessibility hardening pass that centralizes semantic status colors used by the active product lane.

This follows the theme-resource centralization work. Preview/content-specific colors remain separate because texture canvases, wireframes, and generated audio visualizer bars are content surfaces rather than general status UI.

## What Changed

- Added `OnslaughtCareerEditor.WinUI/Helpers/ThemeBrushes.cs`.
- Replaced scattered Settings status colors with centralized semantic brushes:
  - warning
  - danger
  - success
- Replaced Patch Bench track badge colors in `BinaryPatchItemModel` with the same centralized semantic brushes.
- Added an active UiTests guard:
  - `ThemeContrastAuditTests.WinUiSemanticStatusBrushes_AreCentralized`

## Red / Green Evidence

### Failing Guard

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~ThemeContrastAuditTests.WinUiSemanticStatusBrushes_AreCentralized"
```

Result: FAIL before implementation.

Important output:

- The test failed because `OnslaughtCareerEditor.WinUI/Helpers/ThemeBrushes.cs` did not exist yet.

What this proved:

- Semantic status colors were not centralized before this patch.

### Passing Guard

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~ThemeContrastAuditTests.WinUiSemanticStatusBrushes_AreCentralized"
```

Result: PASS after implementation.

Important output:

- Failed: 0
- Passed: 1
- Skipped: 0
- Total: 1

### Focused Theme Audit

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~ThemeContrastAuditTests"
```

Result: PASS.

Important output:

- Failed: 0
- Passed: 3
- Skipped: 0
- Total: 3

## What This Proves

- General warning/danger/success colors are now defined in one helper instead of being scattered through Settings and Patch Bench model code.
- The active UiTests gate now catches reintroduction of the prior scattered Settings and Patch Bench semantic color patterns.
- Active WinUI shell contrast and page-resource centralization guards still pass.

## What This Does Not Prove

- This is not a complete accessibility certification.
- This does not centralize content-specific preview colors such as texture preview backgrounds, wireframe strokes, or generated audio visualizer bars.
- This does not replace manual high-contrast, tab-order, or screen-reader review.

## Privacy And Release Safety

- No private game files, screenshots, saves, executable paths, raw proof JSON, data URLs, or base64 payloads are included.
