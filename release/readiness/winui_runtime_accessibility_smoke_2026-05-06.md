# WinUI Runtime Accessibility Smoke - 2026-05-06

Status: PASS
Branch: `wip/sandbox`
Source commit before this evidence: `f5925cad`
Latest validation refresh: 2026-05-06
Latest source commit: `6f98a931af422b4f608c1c50cce18885095d8b87`
Latest evidence-update commit: `5ff32035ad1d68b33fe7b18d7c9db4dc8ab4e1b8`

## Purpose

Record a focused native WinUI UI Automation smoke that proves the primary shell navigation is not only visible in screenshots, but also named, enabled, and invokable through the Windows accessibility tree.

This is a public-safe evidence summary. It does not include private screenshots, private game paths, save paths, executable paths, raw proof JSON, or game assets.

## What Changed

- Added `OnslaughtCareerEditor.UiTests/WinUiRuntimeAccessibilitySmokeTests.cs`.
- The explicit runtime test launches the WinUI app in an isolated app-data root under ignored `subagents/`.
- The test finds the primary shell controls by automation id, verifies useful accessible names, verifies enabled state, and drives shell navigation through UI Automation invoke/selection patterns.
- The test covers top-level navigation into:
  - Save Lab
  - Media
  - Asset Library
  - Lore
  - Patch Bench
  - Settings
  - About
- The test also invokes `Review Setup` and confirms it routes to Settings.

## Commands

### Focused Runtime Smoke - First Attempt

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiRuntimeAccessibilitySmokeTests"
```

Result: FAIL, then corrected.

Important output:

- The new test launched and drove several shell routes.
- It failed on an incorrect test expectation for Asset Library page text:
  - expected `Load a generated catalog`
  - actual stable page label is `Load generated catalog`

What this proved:

- The new smoke reached the live WinUI app through UI Automation.
- The failure was a test-contract wording mismatch, not a product-code accessibility regression.

### Focused Runtime Smoke - Final

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiRuntimeAccessibilitySmokeTests"
```

Result: PASS.

Important output:

- Failed: 0
- Passed: 1
- Skipped: 0
- Total: 1

Latest rerun result at `6f98a931af422b4f608c1c50cce18885095d8b87`: PASS.

Important output:

- Failed: 0
- Passed: 1
- Skipped: 0
- Total: 1
- Duration: 5 s

Process cleanup check after the latest rerun reported no lingering `OnslaughtCareerEditor.WinUI`, `dotnet`, `MSBuild`, `vstest.console`, `testhost`, `java`, or `javaw` processes.

What this proves:

- Primary WinUI shell controls expose stable automation ids.
- Primary shell controls expose useful accessible names.
- Primary shell controls are enabled.
- Shell routes are invokable through native UI Automation, not just mouse/screenshot observation.
- The app can be launched, driven, and closed cleanly for this accessibility smoke.

## What Is Proven

- Runtime UI Automation can drive the WinUI shell without depending on browser tooling.
- Primary navigation is accessible enough for automation to identify and invoke by name/id.
- The current native test strategy can cover first-viewport and non-browser interaction confidence.

## What Is Not Proven

- This is not a full screen-reader certification.
- This is not a complete keyboard tab-order audit.
- This does not prove every offscreen workflow control on every page.
- This does not prove Windows high-contrast or color-filter compliance.
- This does not prove localization/access-key behavior beyond the already-recorded static shell access-key guard.

## Privacy And Release Safety

- No private game install, save, options, media, executable, screenshot, or frame path is included in this report.
- Runtime artifacts created under ignored `subagents/` remain private and are not public release content.

## Next Recommended QA

- Add a focused keyboard/tab-order smoke only if it can be made stable in native UI Automation.
- Use Accessibility Insights or equivalent manual tooling for a later release-candidate accessibility review.
- Keep distinguishing static accessibility guards, UI Automation runtime proof, visual screenshot proof, and manual accessibility review.
