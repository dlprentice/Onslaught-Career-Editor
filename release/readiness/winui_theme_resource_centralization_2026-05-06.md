# WinUI Theme Resource Centralization - 2026-05-06

Status: PASS
Branch: `wip/sandbox`
Source commit before this evidence: `2d38d498`

## Purpose

Record a focused WinUI visual/accessibility hardening pass that prevents active page XAML from bypassing shared theme resources with raw hex colors.

This is a public-safe evidence summary. It does not include private screenshots, private game paths, save paths, executable paths, raw proof JSON, or game assets.

## What Changed

- Added an active UiTests guard:
  - `ThemeContrastAuditTests.WinUiPages_UseNamedThemeResourcesInsteadOfRawHexColors`
- Moved active page-local XAML colors into named theme resources in `OnslaughtCareerEditor.WinUI/App.xaml`:
  - `ShellMetricSurfaceBrush`
  - `TexturePreviewNeutralBrush`
  - `MediaVisualizerSurfaceBrush`
  - `MediaOverlaySoftBrush`
  - `MediaOverlayStrongBrush`
- Updated active page XAML to use those resources:
  - `SavesPage.xaml`
  - `MediaPage.xaml`
  - `AssetLibraryPage.xaml`
- Extended the active contrast test so `ShellMetricSurfaceBrush` is also covered by the primary text contrast threshold.

## Red / Green Evidence

### Failing Guard

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~ThemeContrastAuditTests.WinUiPages_UseNamedThemeResourcesInsteadOfRawHexColors"
```

Result: FAIL before the resource centralization.

Important output:

- The test found raw page colors in:
  - `OnslaughtCareerEditor.WinUI\Pages\AssetLibraryPage.xaml`
  - `OnslaughtCareerEditor.WinUI\Pages\MediaPage.xaml`
  - `OnslaughtCareerEditor.WinUI\Pages\SavesPage.xaml`

What this proved:

- Active pages could still bypass the shared theme and contrast review surface.

### Passing Guard

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~ThemeContrastAuditTests"
```

Result: PASS.

Important output:

- Failed: 0
- Passed: 2
- Skipped: 0
- Total: 2

What this proves:

- Active WinUI shared theme colors meet the encoded contrast thresholds.
- Active WinUI page XAML no longer contains raw hex color literals outside the shared resource dictionary.

## What This Proves

- The WinUI lane now has a centralized theme-resource guard for page color usage.
- Future active page XAML color additions will need to go through named resources, making contrast and visual review easier.

## What This Does Not Prove

- This is not a complete accessibility certification.
- This does not audit colors created programmatically in code-behind.
- This does not replace manual high-contrast, screen-reader, or keyboard tab-order review.

## Privacy And Release Safety

- This evidence is source/test/release-policy only.
- No private screenshots, private paths, raw game assets, saves, executable copies, media cache paths, data URLs, or base64 payloads are included.
