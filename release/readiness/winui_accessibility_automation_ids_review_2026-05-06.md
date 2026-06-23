# WinUI Accessibility Automation IDs Review - 2026-05-06

Status: public-safe automation review

## Scope

This note records a focused WinUI accessibility/testability pass. It does not redesign the UI and does not claim a complete accessibility certification. The goal was to make the native WinUI product easier to drive reliably through UI Automation, especially on scroll-heavy pages where controls may be outside the first viewport.

## What Changed

- Added explicit UI Automation IDs to the shell setup action and top navigation items.
- Added explicit UI Automation IDs to Save Lab task-router buttons and Save Lab subtab buttons.
- Added `WinUiAccessibilityAuditTests` to guard the primary shell IDs, long-workflow IDs, and the current anti-flake test patterns.
- Preserved the existing WinUI layout, page structure, backend behavior, save behavior, patch behavior, and release policy.

## Why This Matters

Functional desktop automation can interact with offscreen controls through the accessibility tree, but only when the app exposes stable targets. This pass strengthens that contract without relying on fragile text matching or focus-dependent keyboard input.

## Commands

| Command | Result | Important output |
| --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiAccessibilityAuditTests"` | PASS | 2/2 accessibility audit tests passed. |
| `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` | PASS | Build succeeded with 0 warnings and 0 errors. |

## What Is Proven

- Shell navigation and long-workflow controls now have a guarded stable-ID surface for UI Automation.
- Save/Patch runtime smokes are guarded against regressing to focus-dependent path typing.
- Scrolled workflow smokes retain `ScrollItem.ScrollIntoView()` usage for long-page action/output regions.

## What Is Not Proven

- This is not a complete screen-reader audit.
- This is not a complete keyboard-only tab-order audit.
- This does not prove every WinUI control has a perfect accessible name.
- This does not replace manual accessibility review or later tooling such as Accessibility Insights if a release candidate requires that level of certification.
