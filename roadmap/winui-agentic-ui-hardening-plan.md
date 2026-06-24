# WinUI Agentic UI Hardening Plan

Status: active
Last updated: 2026-06-24

## Decision

Keep WinUI 3 as the flagship Windows product lane. Do not rewrite the app into
Blazor Hybrid, Tauri, Electron, Avalonia, or Python at this time.

The current architecture already has the right product boundary: WinUI 3 is the
native Windows shell, and `OnslaughtCareerEditor.AppCore` owns the reusable
save, patch, copied-profile, media, asset, and runtime-support logic. The next
agentic-workflow improvement is not a framework migration. It is to make the
existing WinUI shell easier for agents to inspect, modify, launch, visually
verify, and reason about.

## Why This Is The Current Call

- WinUI 3 matches the product's real work: Windows game folders, copied
  executables, local process launch/stop, UI Automation, screenshots, and
  packaged Windows distribution.
- AppCore is already a strong reusable backend. A UI rewrite would mostly
  rebuild presentation and test infrastructure, not improve the binary, save,
  patch, or runtime-proof core.
- The app already has stable automation IDs, FlaUI/UIA tests, screenshot smokes,
  accessibility/contrast checks, and release/package probes.
- The real current UI maintainability weakness is large XAML/code-behind pages,
  especially dense workflows such as Windowed & Mods. That should be fixed by
  extracting ViewModels, splitting overloaded pages, and adding agent-readable
  UIA snapshot artifacts.
- DOM/CSS stacks are easier for agents to inspect, but they add WebView/IPC,
  packaging, security, and native-integration costs that do not remove the
  project's hardest Windows-native requirements.

## What To Improve First

1. Add deterministic UIA tree snapshots for representative WinUI surfaces so an
   agent can inspect the app like a DOM-style artifact.
2. Extract ViewModels for the worst code-behind-heavy pages, keeping existing
   automation IDs stable.
3. Add one documented command path that runs build, UIA inspection, screenshot
   capture, and artifact summary for a focused UI slice.
4. Split Windowed & Mods into clearer safe-copy, mods, music, launch options,
   and diagnostics surfaces before adding more player-facing patch complexity.

The first concrete command is:

```powershell
npm run test:winui-agentic-ui-snapshot
```

That command launches the app in an interactive Windows desktop session and
writes path-redacted UI Automation tree JSON under:

```text
subagents/winui-agentic-ui-snapshot/current/
```

The snapshot is ignored evidence, not public release payload.

## Metrics Baseline

The second concrete command is:

```powershell
npm run test:winui-agentic-ui-hardening-metrics
```

For an ignored JSON report:

```powershell
npm run report:winui-agentic-ui-hardening-metrics
```

That report is written under:

```text
subagents/winui-agentic-ui-hardening-metrics/current/metrics.json
```

Current baseline from 2026-06-24:

| Metric | Count |
| --- | ---: |
| WinUI pages measured | 8 |
| Logical code-behind lines | 9,177 |
| Routed handler methods | 178 |
| `async void` handlers | 41 |
| Direct UI writes | 704 |
| XAML event attributes | 246 |
| Automation IDs | 374 |
| Pages with ViewModel files | 0 |

Top advisory refactor candidates:

| Rank | Page | Evidence |
| ---: | --- | --- |
| 1 | `BinaryPatchesPage` | 2,700 code-behind lines, 55 routed handlers, 15 `async void` handlers, 227 direct UI writes. |
| 2 | `SavesPage` | 1,631 logical code-behind lines across primary and partial files, 50 routed handlers, 9 `async void` handlers, 145 direct UI writes. |
| 3 | `AssetLibraryPage` | 1,911 code-behind lines, 32 routed handlers, 3 `async void` handlers, 195 direct UI writes. |
| 4 | `MediaPage` | 1,840 code-behind lines, 26 routed handlers, 3 `async void` handlers, 87 direct UI writes. |
| 5 | `LorePage` | 823 code-behind lines, 10 routed handlers, 10 `async void` handlers, 33 direct UI writes. |

Interpretation rules:

- These metrics are an advisory locator, not a product-quality score and not a
  release gate.
- Logical page accounting includes partial code-behind files such as
  `SavesPage.Configuration.cs` and `SavesPage.SaveEditorAdvanced.cs`.
- Do not use exact heuristic rank counts as a brittle pass/fail rule.
- Use the baseline to choose bounded ViewModel/page-decomposition slices, then
  compare future reports for directional improvement while keeping automation
  IDs and visible behavior stable.
- The next recommended extraction target remains `BinaryPatchesPage`, starting
  with safe-copy/launch state. The next likely candidates are `SavesPage`
  editor/configuration state and `AssetLibraryPage` catalog/filter/selection
  state. Defer `MediaPage` until VLC/NAudio lifecycle risk is isolated.

## Migration Triggers

Reconsider a migration or hybrid shell only if one of these becomes true:

- A required user-facing workflow cannot be made agent-inspectable through
  UIA snapshots, ViewModels, AppCore/CLI support, and screenshot evidence.
- Windows is no longer the only practical target.
- WinUI/Windows App SDK packaging or signing blocks acceptable distribution
  after a focused installer/signing effort.
- A new rich visual surface, such as a full 3D viewer, proves materially easier
  and safer as a web/Blazor island than as native WinUI.

## Candidate Future Spikes

- **WinUI baseline hardening:** continue first. Measure time and failures for
  agent-authored UI changes using UIA snapshots plus visual smoke.
- **Blazor Hybrid / WinUI-hosted WebView island:** only as a challenger for one
  narrow, high-churn page after WinUI hardening is measured.
- **Tauri 2:** only if browser-first automation becomes more important than
  AppCore/.NET/native Windows continuity.
- **Electron revival:** do not revive broadly. Use archived Electron workbench
  ideas as reference only.
- **Python GUI:** do not revive as product UI. Keep Python for tools and RE lab
  support.

## Acceptance Bar For This Track

- An agent can inspect page structure and state from a deterministic snapshot
  artifact without reading the full code-behind file.
- UI changes retain stable automation IDs and accessible names.
- Focused UI changes produce machine-checkable UIA output plus screenshots.
- ViewModel extraction reduces imperative code-behind in high-risk pages.
- Release/public safety remains unchanged: no private proof, local paths, game
  files, saves, or private assets leak into public payloads.
