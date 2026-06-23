# WinUI Lore Reader Interaction Smoke - 2026-05-06

Status: pass

Source commit: 2b45b97e
Evidence-report commit: 9d82b231cb2161889248995a5d8e5b75e7dcc534

## Objective

Prove the primary WinUI Lore reader can be driven through native UI Automation for a normal read workflow:

1. launch the WinUI app in an isolated test profile
2. open the Lore lane directly
3. search the curated lore library
4. select a filtered document
5. show the selected document in the in-app reader
6. keep primary source summaries public-safe
7. capture private visual evidence without committing screenshots

## Product Changes Covered

- Added stable automation IDs and accessible names for the Lore search box, refresh action, library status, document tree, navigation actions, selected-document title, selected-document summary, reader panel, WebView, and reader placeholder.
- Made the selected document header visible above the embedded reader so the page clearly states what is being read.
- Changed the selected-document summary from a raw/relative path-style label to a filename plus curated-library label.
- Kept the full local source path out of the primary UI; the source path is available as a tooltip only.
- Guarded duplicate TreeView selection/invocation loads so a successful document selection cannot leave the shell footer in a stale "load failed" state.

No Lore markdown content, AppCore content schema, file format, backend behavior, or release scope changed.

## Focused Smoke Result

Command:

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiLoreInteractionSmokeTests"
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

- the WinUI Lore page launches in the native app
- `LoreSearchBox` accepts a query
- the filtered document tree exposes `Battle Engine Tech`
- selecting that tree row updates `LoreCurrentDocumentTitle`
- the current document summary does not expose a drive-qualified local path
- Back and Open External actions are available after selection
- a screenshot is captured under ignored local evidence storage

## Build Result

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

What it proves:

- the WinUI product lane still builds after the Lore reader automation and status fixes

## Visual Evidence

Ignored screenshot:

```text
01-lore-reader-selected.png
```

Screenshot review summary:

- Lore opens on a stable native shell.
- The left library is searchable and visibly filtered.
- `Battle Engine Tech` is selected in the document tree.
- The selected-document header is visible above the reader.
- The embedded reader displays the authored article.
- The shell footer reports `Lore: loaded Battle Engine Tech`.
- No raw private absolute path is visible in the primary screenshot.

Screenshots stay ignored under `subagents/` and are not release artifacts.

## Known Notes

- An early accidental parallel `.NET` build/test attempt produced a transient file-lock warning and launched stale output. Final validation was rerun serially per repo rules and passed.
- WebView article body automation remains a deeper future target; this smoke proves selection and visible reader state through native UI Automation plus private screenshot inspection.
- The Lore reader still uses WebView2 for markdown rendering; this slice did not replace or redesign that renderer.
