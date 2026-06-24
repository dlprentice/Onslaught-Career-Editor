---
status: archived/historical
last_updated: 2026-05-26
doc_version: 1.1
---

# UI Action Inventory - 2026-05-01

> **SUPERSEDED — archived/historical (2026-05-26):** This inventory documents the **archived** Electron workbench under `archive/electron-workbench/`. Electron is **not** the active product surface; WinUI 3 is the primary product lane. Keep this file for historical UX/action reference only.

## Purpose

This inventory records the major visible actions in the Electron workbench after the unified UX reset and the Ralph-loop hardening pass. It is public-safe and does not include private screenshots, raw game paths, proof JSON, frame captures, data URLs, or game assets.

Proof labels:

- `renderer-smoke`: covered by `npm run archive:electron:test:renderer-smoke`.
- `browser-preview`: covered only by deterministic browser/Electron preview-mode behavior.
- `desktop-required`: native filesystem/game/debug/media behavior needs Electron desktop, CLI, or packaged runtime proof.
- `code-inspection`: reviewed in component/API code but not independently exercised in this pass.
- `planned`: intentionally non-operational with visible copy.

## Summary

| Area | Result | Notes |
| --- | --- | --- |
| App shell | Works | Navigation and command search stay renderer-testable; no raw native access is exposed. |
| Home | Works | Task routing is primary; deeper workflows remain screen-specific. |
| Save Lab | Works with native caveat | Browser proof is preview-only; real save/options writes remain copy-first native jobs. |
| Media | Works with native caveat | Inline audio, selected video panel, and texture preview are smoke-tested; real Bink cache/runtime coverage is desktop/package-specific. |
| Lore | Fixed in this pass | Markdown internal, heading, external, and unknown links are now handled in the reader without rewriting authored markdown. |
| Patch Bench | Works with native caveat | Guided copied-executable workflow is present; actual patch writes remain typed copy-target jobs. |
| RE Lab | Fixed in this pass | Sample rows are honestly labeled and local filter/search/selection/plan controls now update visible state. |
| Game Harness | Fixed in this pass | Launch/stop remain typed jobs; scoped input send now has an explicit visible exact-target confirmation before the button can run. |
| Release | Works | Public/private lane messaging is visible; runtime packaged proof remains an explicit gap. |

## App Shell

| Action | Owner | Intended behavior | Status | Proof | Follow-up/fix |
| --- | --- | --- | --- | --- | --- |
| Left navigation | `WorkbenchShell` | Switch to Home, Save Lab, Patch Bench, Media, Lore, RE Lab, Game Harness, and Release. | Works | `renderer-smoke` | Keep smoke route coverage when adding screens. |
| Command search | `WorkbenchShell` | Find user-facing sections and safe job surfaces without exposing raw shell access. | Works | `renderer-smoke`, `code-inspection` | Continue hiding job details behind Diagnostics/Details. |
| Session details disclosure | `WorkbenchShell` | Show environment/status details only when expanded. | Works | `renderer-smoke` copy audit | Keep internal values collapsed by default. |

## Home

| Action | Owner | Intended behavior | Status | Proof | Follow-up/fix |
| --- | --- | --- | --- | --- | --- |
| Task cards | `HomeSection` | Route users to core workflows such as saves, media, lore, RE, and runtime investigation. | Works | `renderer-smoke` | Add click-level smoke for every task card if Home grows new routes. |
| Setup/status cards | `HomeSection` | Summarize readiness in plain language. | Works | `renderer-smoke`, `code-inspection` | Keep status copy honest about preview-mode versus native proof. |
| Agentic loop explainer | `HomeSection` | Explain the bounded observe/decide/act/review model without implying open-ended autonomy. | Works | `renderer-smoke` | No current code change needed. |

## Save Lab

| Action | Owner | Intended behavior | Status | Proof | Follow-up/fix |
| --- | --- | --- | --- | --- | --- |
| Open/inspect save/options file | `SaveLabSection`, typed preload | Read a selected `.bes`/`.bea`/`defaultoptions.bea` through the typed inspector. | Works | `renderer-smoke`, `desktop-required` for real file chooser | Browser proof uses preview-mode sample files; desktop proof is required for real local files. |
| Search/filter goodies | `SaveLabSection` | Filter rows and select a specific save item for inspection. | Works | `renderer-smoke` | Continue avoiding raw offset-first presentation. |
| Goodie media lookup | `SaveLabSection` -> Media | Route a selected goodie/media hint into the Media browser. | Works | `renderer-smoke` | No backend contract change. |
| Copy/plan/preview/apply/restore save patch | `SaveLabSection`, job runner | Mutate only copied targets after preview and required policy gates. | Works with native caveat | `code-inspection`, prior parity evidence | Add deeper smoke around copy/apply/restore preview-mode flows when Save Lab becomes the next release blocker. |
| Options copy/plan/preview/apply | `SaveLabSection`, job runner | Apply options edits only through typed copy/preview/apply boundaries. | Works with native caveat | `renderer-smoke` for controls, prior parity evidence | The current pass did not rerun native save mutation. |

## Media

| Action | Owner | Intended behavior | Status | Proof | Follow-up/fix |
| --- | --- | --- | --- | --- | --- |
| Category filter | `MediaSection` | Switch between All, Audio, Videos, Textures, Meshes/Models, and Language views. | Works | `renderer-smoke` | Keep labels user-facing if catalog kind names change. |
| Audio Play | `MediaSection` | Expand the active row and render playback controls locally. | Works | `renderer-smoke` | Real OGG playback remains renderer/native dependent. |
| Video Prepare/Play | `MediaSection`, media IPC | Use one selected-player panel and hide backend/cache/command details. | Works with native caveat | `renderer-smoke`, prior desktop proof | Packaged portable-bundle video proof remains missing. |
| Texture Preview | `MediaSection` | Render selected preview near the row/card. | Works | `renderer-smoke`, prior desktop proof | Some sample textures may look dark; this is visual polish, not an action blocker. |
| Mesh/language rows | `MediaSection` | Show read-only catalog rows without implying playback. | Works | `code-inspection` | Add explicit smoke if these become a release-critical lane. |

## Lore

| Action | Owner | Intended behavior | Status | Proof | Follow-up/fix |
| --- | --- | --- | --- | --- | --- |
| Search and audience filter | `DocumentLibrary` | Narrow the curated document list. | Works | `renderer-smoke` | No current fix needed. |
| Select document | `LoreSection`, content IPC | Load an allowlisted document into the reader. | Works | `renderer-smoke` | Authored markdown remains unmodified. |
| Internal markdown document link | `MarkdownRenderer`, `LoreSection` | Select the matching allowlisted Lore/content document in place. | Fixed | `renderer-smoke` | Resolver matches ids, relative paths, basenames, and title slugs. |
| Markdown heading link | `MarkdownRenderer`, `LoreSection` | Scroll inside the current article. | Fixed | `renderer-smoke` | Uses the same heading ids as the outline. |
| External markdown link | `MarkdownRenderer`, shell boundary | Open through the existing external-link boundary. | Fixed | `renderer-smoke` | Unsupported schemes are blocked. |
| Unknown markdown link | `MarkdownRenderer`, `LoreSection` | Stay in the reader and show a clear notice. | Fixed | `renderer-smoke` | Unknown links no longer navigate Home/default routes. |
| Unsafe markdown link | `MarkdownRenderer`, `LoreSection` | Fail closed with visible notice. | Fixed by code | `code-inspection` | Add a dedicated smoke click if a stable fixture link is added later. |

## Patch Bench

| Action | Owner | Intended behavior | Status | Proof | Follow-up/fix |
| --- | --- | --- | --- | --- | --- |
| Verify executable | `PatchBenchSection`, patch jobs | Verify a selected specimen without mutating it. | Works with native caveat | `renderer-smoke`, prior parity evidence | Real verification needs desktop/CLI. |
| Prepare executable copy | `PatchBenchSection`, patch jobs | Copy the executable to an app/user artifact root before mutation. | Works with native caveat | prior job evidence | Keep original-executable safety copy prominent. |
| Preview/plan patch | `PatchBenchSection`, patch jobs | Show the selected catalog patch plan before writes. | Works | `code-inspection`, prior tests | Add deeper fixture action smoke when Patch Bench is next in scope. |
| Apply to copy | `PatchBenchSection`, patch jobs | Apply only catalog-selected patches to copied targets with gates. | Works with native caveat | prior runtime/job evidence | Do not broaden patch ids in this goal. |
| Restore backup | `PatchBenchSection`, patch jobs | Restore copied target from verified backup. | Works with native caveat | prior parity evidence | No runtime rerun in this pass. |

## RE Lab

| Action | Owner | Intended behavior | Status | Proof | Follow-up/fix |
| --- | --- | --- | --- | --- | --- |
| Check tools | `ReLabSection` | Refresh Ghidra/debug/harness/job readiness through typed APIs. | Works | `code-inspection`, prior renderer smoke | Native tool truth remains desktop/CLI dependent. |
| Data source filter | `ReLabSection` | Change the visible sample investigation source filter. | Fixed | `code-inspection` | Local state now updates rows and plan state. |
| Type filter | `ReLabSection` | Change the visible sample investigation type. | Fixed | `code-inspection` | Sample nature remains clearly labeled. |
| Search | `ReLabSection` | Filter sample investigation rows locally. | Fixed | `renderer-smoke` | Real catalog-backed RE search remains future work. |
| Select result | `ReLabSection` | Update inspector and objective copy to the selected sample row. | Fixed | `code-inspection` | Live extracted results must be wired in a later slice before removing sample labels. |
| Create bounded plan | `ReLabSection` | Create a visible local plan-ready state without starting uncontrolled automation. | Fixed | `renderer-smoke` | Future maintainer feature should connect to real objective/job plans. |
| Run safe tool | `ReLabSection`, job runner | Run the first available read-only job through the typed job runner. | Works with native caveat | `code-inspection` | Keep write/runtime jobs gated separately. |

## Game Harness

| Action | Owner | Intended behavior | Status | Proof | Follow-up/fix |
| --- | --- | --- | --- | --- | --- |
| Prepare copied profile | `GameHarnessSection`, `game.prepareSafeProfile` | Create a copied profile before runtime work. | Works with native caveat | prior desktop proof | No BEA launch was run in this pass. |
| Apply display patch | `GameHarnessSection`, patch jobs | Apply the display/windowed patch only to the copied executable. | Works with native caveat | prior desktop proof | The UI labels the copy prerequisite. |
| Launch managed game | `GameHarnessSection`, `game.launchProfile` | Launch only the copied profile as a managed process. | Works with safety gate | `renderer-smoke` wiring, prior desktop proof | Button requires prerequisites and copied-profile confirmation. |
| Plan/capture frame | `GameHarnessSection`, capture jobs | Plan and capture bounded observations through typed jobs. | Works with native caveat | `renderer-smoke`, prior desktop proof | Continuous streaming remains future work. |
| Plan input | `GameHarnessSection`, `game.planWindowInput` | Build a bounded exact-target input plan. | Works with native caveat | `renderer-smoke`, prior desktop proof | No raw/unbounded input is exposed. |
| Send input | `GameHarnessSection`, `game.sendWindowInput` | Send only after launch and exact-target confirmation. | Fixed | `renderer-smoke` | This pass added visible exact-target arming before the send button can run. |
| Stop managed process | `GameHarnessSection`, `runtime.stopManagedProcess` | Stop the managed process and keep cleanup visible. | Works with safety gate | `renderer-smoke` wiring, prior desktop proof | No runtime proof rerun in this pass. |
| Create investigation | `GameHarnessSection` | Future custom objective builder. | Planned | visible disabled copy | Button is intentionally disabled; copy states guided proof exists and custom planning is future maintainer work. |

## Release

| Action | Owner | Intended behavior | Status | Proof | Follow-up/fix |
| --- | --- | --- | --- | --- | --- |
| Refresh policy | `ReleaseSection`, release IPC | Refresh source/bundle/public-private release policy summaries. | Works | `code-inspection`, prior renderer smoke | Keep generated artifacts current after manifest changes. |
| Evidence report links/list | `ReleaseSection` | Show public-safe evidence posture without exposing private proof. | Works | `renderer-smoke`, release docs | Link/open behavior should use the same safe external/content boundary if made clickable later. |
| Gate summary | `ReleaseSection` | Show recorded gate posture and remaining blockers. | Works | `renderer-smoke` | Do not imply signed/installer readiness or packaged runtime proof until proven. |

## Applied Fixes In This Pass

- Lore markdown renderer now intercepts links without altering authored markdown.
- Lore internal document links resolve to curated content ids/paths/slugs instead of navigating the browser route.
- Lore heading links scroll inside the current article.
- Lore external links use the existing safe external-link boundary.
- Lore unknown/unsafe links stay in the reader and show a clear notice.
- RE Lab sample filters/search/result selection now update local visible state.
- RE Lab `Create bounded plan` now produces a visible local plan-ready state without starting automation.
- Game Harness input send now requires a visible exact-target confirmation and a launched managed process before the button can run.
- Game Harness custom investigation planning is disabled honestly as future maintainer work rather than appearing as a no-op action.

## Remaining Follow-Ups

- Add deeper Save Lab copy/preview/apply/restore fixture smoke when the next save-editing slice starts.
- Add Patch Bench fixture action smoke for prepare/preview/apply/restore if patch UX becomes the next blocker.
- Replace RE Lab sample rows with real catalog/function/search-backed results before presenting it as live extracted data.
- Prove packaged portable-bundle media playback and Game Harness runtime behavior separately from renderer/browser proof.
- Keep continuous frame streaming, semantic gameplay-state interpretation, open-ended autonomy, and signed installer readiness explicitly out of current claims.
