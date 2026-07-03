# Internal Viewer/Editor Command-Boundary Proof Plan

Status: source-only public-safe proof plan, not command authorization
Last updated: 2026-07-03
Scope: `internal-viewer-editor-command-boundary`

This plan answers one bounded question from
[original-system-internal-tooling-vocabulary-map.md](original-system-internal-tooling-vocabulary-map.md):
what evidence is required before source/internal viewer and editor vocabulary
such as `-modelviewer` and `-cutsceneeditor` can affect any executable command
surface?

Current answer: the names remain source/internal vocabulary and blocked product
flags. The current public-safe proof class is Tier C source vocabulary plus
tracked Tier B static command-boundary docs. This is not command authorization,
not command dispatch, not runtime proof, and not evidence that the Steam retail
build exposes either tool.

## Evidence Class

| Tier | Current use in this plan | Boundary |
| --- | --- | --- |
| Tier C source vocabulary | Names the internal tool labels and `DEV_VERSION` guard vocabulary from source docs. | Candidate labels only; not executable behavior. |
| Tier B static command-boundary docs | Records current tracked retail/static posture that these source/internal flags stay out of product launch allowlists. | Static command-boundary context only; not runtime behavior. |
| Tier A runtime evidence | Not used in this slice. | Any executable or runtime claim needs a separate authorized proof class. |

## Public Anchors

| Anchor | Current boundary used here |
| --- | --- |
| [source-code/_index.md](_index.md) | Lists `-modelviewer` and `-cutsceneeditor` as internal tools under `DEV_VERSION`; this is source/internal context only. |
| [engine-system.md](core/engine-system.md) | Describes `EditorD3DApp`, Model Viewer, Cutscene Editor, Particle Editor, and build defines as internal development tooling. |
| [platform-system.md](core/platform-system.md) | Describes the `DEV_VERSION` window/fullscreen split where model viewer and cutscene editor are source-side exceptions. |
| [source-file-inventory.md](source-file-inventory.md) | Marks `EditorD3DApp.cpp` as an internal dev tool stripped from the retail binary debug-path surface. |
| [CLIParams.cpp/_index.md](../binary-analysis/functions/CLIParams.cpp/_index.md) | Records `-modelviewer` and `-cutsceneeditor` under parameters not present in the retail parser, while separately proven retail parameters remain distinct. |
| [d3dapp.cpp/_index.md](../binary-analysis/functions/d3dapp.cpp/_index.md) | Provides retail D3D application-shell static context without proving internal viewer/editor activation. |
| [windowed-mode-analysis.md](../binary-analysis/windowed-mode-analysis.md) | Keeps source fullscreen-flow references separate from current retail parser/startup behavior. |
| [mod-patch-runtime-rebuild-register.md](../../roadmap/mod-patch-runtime-rebuild-register.md) | Keeps source-only, dev-only, and file-writing flags such as `-modelviewer` blocked in the product launch surface. |

## Boundary Rows

| Row | Question | Current public-safe answer | Higher authority still required |
| --- | --- | --- | --- |
| 1 | Can `-modelviewer` be treated as a supported Steam retail launch flag? | No. Current tracked docs keep it source/internal and blocked. | New retail static evidence plus explicit product command-boundary review before any product surface change. |
| 2 | Can `-cutsceneeditor` be treated as a supported Steam retail launch flag? | No. Current tracked docs keep it source/internal and blocked. | New retail static evidence plus explicit product command-boundary review before any product surface change. |
| 3 | Can `EditorD3DApp` guide clean-room tool vocabulary? | Yes, as source-only vocabulary for future planning. | Retail/static or runtime proof before any claim about a shipped tool. |
| 4 | Can model viewer or cutscene editor vocabulary drive app UI or AppCore allowlists? | No. This plan requires those terms to stay blocked unless a later authorized proof changes the product boundary. | Separate implementation task, owner review, security/safety review, validation gates, and product acceptance. |
| 5 | Can this plan support runtime, visual, asset, or rebuild claims? | No. It only records command-boundary planning and non-claims. | Separate runtime, visual, asset, or rebuild proof contract. |

## Allowed Inputs

This checker-backed slice may read only tracked public Markdown and package
metadata. It may validate mirror parity, links, required boundary wording, and
package-script registration.

Allowed source classes:

- tracked source-code docs;
- tracked retail/static command-boundary docs;
- tracked product/register docs that keep these flags blocked;
- package metadata for a local public checker.

## Out Of Scope

This slice must not:

- run, arm, materialize, dispatch, or recommend any command using these flags;
- launch BEA, attach CDB, mutate Ghidra, patch an executable, or mutate an installed game;
- add AppCore, WinUI, CLI, release, installer, or packaging support for these flags;
- read ignored payload overlays, private assets, raw manifests, raw proof bundles, copied executables, screenshots, frame dumps, auth/session/log/cache material, or secrets;
- publish raw local paths, hashes, private filenames, command traces, or generated payloads;
- claim runtime behavior, tool availability, visual output, gameplay behavior, rebuild parity, or no-noticeable-difference parity.

## Exit Gate

This planning slice is complete only when:

- this document and its lore-book mirror match byte-for-byte;
- source-code indexes link this plan as a source-only command-boundary plan;
- `roadmap/rebuild-front-door-chain-map.md` links this plan as a bounded
  internal-tooling side guard, without changing the active rebuild proof scope;
- `tools/internal_viewer_editor_command_boundary_proof_plan_probe.py --check`
  passes;
- the existing original-system vocabulary-map checker still passes;
- public documentation, Markdown link, hard-payload, and public-allowlist gates pass.

After this exit gate, the next safe action is still planning or retail/static
review. No executable use, product exposure, runtime proof, or release action is
authorized by this plan.
