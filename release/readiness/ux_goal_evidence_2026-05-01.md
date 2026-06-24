# UX Goal Evidence - 2026-05-01

Status: historical public-safe Electron workbench UX evidence; superseded for product direction

Branch: `wip/sandbox`
Source/base commit: `37102df623092fddad05a594d53d9382a7457628`
Evidence-report commit: `9f4842b5e4ffbe2bdedc3b4e534199fd1c184be8`
Post-review fix commit: `1b57bf4842ea79821bff7de4e6d923d9224501af`
Date/time: 2026-05-01 local desktop session

## Scope

This report records the unified UX goal pass for the then Electron-first Onslaught workbench. It remains useful historical evidence for the archived Electron workbench, but it no longer defines the primary user-facing product direction. The current product lane is WinUI 3. It is public-safe: it does not embed screenshots, raw game media, raw frame captures, data URLs, base64, private absolute Windows paths, private game asset paths, or ignored proof JSON.

The referenced screenshots remain ignored under `subagents/` and are not release artifacts.

## References Used

- Written goal prompt from the supplied superb UX goal package.
- Local ignored image references copied under the ignored UX reference folder:
  - `00_home_start_here.png`
  - `01_save_lab.png`
  - `02_media_library.png`
  - `03_lore_reader.png`
  - `04_patch_bench.png`
  - `05_re_lab.png`
  - `06_game_harness.png`
- Build Web Apps guidance for app-level product structure and React UI discipline.
- Game Studio UI guidance for game-adjacent Harness/RE surfaces.
- Superpowers verification/review guidance for gate discipline.

Browser Use was requested for interactive screenshots, but no Browser Use callable tool was available in this session. The fallback was the existing Electron renderer screenshot harness against `http://127.0.0.1:3000`, with screenshots kept ignored/private.

## What Changed

- Home now routes users by task instead of opening as an operator dashboard.
- Save Lab is a safe save/options editor surface with file summary, validation, copied-target workflow, empty states, and patch actions grouped by purpose.
- Media now behaves as a media browser with a left filter rail, inline audio playback, one selected video panel, human playback status, and texture cards/previews.
- Lore now reads as a document reader with library search, audience filters, readable article layout, outline/details, and authored markdown preserved.
- Patch Bench is a copied-executable workflow: choose/verify executable, choose patches, review/apply to copy.
- RE Lab is a searchable investigation surface with filters, results, inspector, and a bounded "ask the agent" panel.
- Game Harness is a five-stage guided loop: prepare copied profile, apply windowed patch, launch managed game, observe/input/observe, stop and record proof.
- Release is a public-readiness dashboard that summarizes gates, scope, evidence reports, exclusions, and next proof without private evidence leakage.
- Diagnostics and raw technical fields remain available only behind collapsed Details/session panels by default.

## Screenshots

Captured ignored/private screenshots:

- `visible2-home.png`
- `visible2-save-lab.png`
- `visible2-patch-bench.png`
- `visible2-media.png`
- `visible2-media-audio.png`
- `visible2-media-audio-playing.png`
- `visible2-media-video.png`
- `visible2-media-texture.png`
- `visible2-lore.png`
- `visible2-re-lab.png`
- `visible2-game-harness.png`
- `visible2-release.png`

## Command Results

| Command | Result | Notes |
| --- | --- | --- |
| `git status --short --branch` | Passed | Confirmed work occurred on `wip/sandbox`; one pre-existing unrelated directive edit remains outside the UX commit scope. |
| `git rev-parse HEAD` | Passed | Base commit was `37102df623092fddad05a594d53d9382a7457628`. |
| `npx electron subagents/superb-ux-capture.cjs` | Passed | Captured all listed screenshots through the Electron renderer fallback. |
| `npm run typecheck` | Passed after a local cleanup fix | Contracts, Electron, CLI, and UI typechecks completed. A cleanup pass briefly removed needed type imports; the imports were restored and the final rerun passed. |
| `npm run build` | Passed | Contracts, Electron, CLI, and Vite renderer build completed. |
| `npm run test:renderer-smoke` | Passed | Renderer smoke and visible-copy audit returned `ok: true`. |
| `npm run test:cli-smoke` | Passed | CLI catalog/run/list smoke passed with persisted run history. |
| `npm run test:electron-parity` | Passed | Electron parity smoke passed for save/options/executable/release/job-runner surfaces. |
| `npm run test:bundle-policy` | Passed | Electron bundle policy smoke passed. |
| `npm run test:bundle-smoke` | Passed | Disposable portable bundle smoke passed. |
| `dotnet build ".\OnslaughtCareerEditor.Release.slnx" --nologo` | Passed | Retained C# parity solution built with 0 warnings and 0 errors. |
| `dotnet test ".\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj" --nologo` | Passed | AppCore parity tests passed, 19/19. |
| `dotnet test ".\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj" --nologo` | Passed | UiTests passed, 21/21. |
| `py -3 tools\docsync_check.py` | Passed | Docsync policy check passed. |
| `py -3 tools\release_profile_snapshot.py --check` | Passed after regeneration | Initial check found stale generated profile artifacts after doc/report edits; `py -3 tools\release_profile_snapshot.py` regenerated them, then `--check` passed. |
| `py -3 tools\release_curated_manifest.py --check` | Passed after regeneration | Initial check found stale public allowlist entries after manifest/report/component changes; `py -3 tools\release_curated_manifest.py` regenerated the allowlist, then `--check` passed. |
| Public allowlist forbidden-family scan | Passed after path-aware scan | A naive literal scan false-positive matched product UI code under `packages/ui/src/components/media/`; the path-aware scan verified no top-level private/runtime families or denied binary/save suffixes are allowlisted. |
| `node -e "<parse state files>"` | Passed | Developer and documentation state JSON parsed successfully. |
| `git diff --check` | Passed | Whitespace check passed; Git emitted line-ending normalization warnings only. |

## Copy Audit

The renderer smoke visible-copy audit continues to reject default visible UI chrome containing internal terms such as IPC, schema names, payload language, job-run wording, fixture/browser-mock language, mutation wording, command previews, full absolute Windows paths, and raw byte wording. Authored Lore markdown remains excluded from that chrome audit and is rendered faithfully.

## What Did Not Change

- Backend contracts were preserved.
- IPC/preload contracts were preserved.
- Job IDs were preserved.
- Schema IDs were preserved.
- Payload shapes were preserved.
- Safety gates and arm phrases were preserved.
- Private runtime evidence exclusions were preserved.
- Raw screenshots, frame captures, proof JSON, and private game/media assets were not committed.

## Remaining Gaps

- Signed installer-grade release is not proven.
- Packaged portable-bundle runtime media playback is not separately clicked/proven.
- Packaged portable-bundle Game Harness runtime behavior is not separately proven.
- Continuous frame streaming is not proven.
- Semantic gameplay-state interpretation is not proven.
- Open-ended autonomy is not proven.
- Broader real-media row coverage remains future work.
- Ghidra rename-map Java/name preflight/read-back hardening remains future work.
- Full retirement of C# parity oracles remains future work.

## Release Posture

The UX reset supported the Electron-first release candidate posture at the time, but the product lane has since moved to WinUI 3. Packaged Electron runtime proof is no longer the next primary release-facing proof; it is archived workbench validation only. The next product-facing work should harden WinUI and prove a WinUI packaging/signoff path when that lane is ready.
