# Deep Validation Status (Static RE Gate)

> Tracks ownership/type/behavior contract hardening required by the static RE completion program.
> Last updated: 2026-05-26

> **Disclaimer:** This gate doc predates the Wave900 function-quality queue closure. Current loaded-database closure is **6113/6113** with **0** commentless functions (Wave900) plus read-only post-100 subsystem reviews **901-909**. Authoritative queue telemetry lives in [`functions/FUNCTION_COVERAGE_STATE.md`](functions/FUNCTION_COVERAGE_STATE.md) and [`static-reaudit-campaign.md`](static-reaudit-campaign.md). Treat older wave-by-wave "next raw commentless head" lines as archival unless explicitly re-opened.

## Gate Snapshot

| Metric | Value | Source |
|---|---|---|
| Binary function objects | 6113 | `functions/FUNCTION_COVERAGE_STATE.md` (Wave900 closure) |
| Functions with non-empty comments | 6113 (100.00%) | `static-reaudit-campaign.md` |
| Commentless functions | 0 | Wave900 final static tail |
| Export-contract named functions (comment + signature proxy) | 6113 (100.00%) | Wave900 closure; not the same as evidence-grade strong-semantic count below |
| Strong semantic symbols (legacy metric) | 6055 (100.00%) | `functions/FUNCTION_COVERAGE_STATE.md` — weak-regex clean only; not quality-certified |
| Weak-name objects (`FUN_`, `Auto_`, `__Unk_`) | 0 | `functions/FUNCTION_COVERAGE_STATE.md` |
| `param_N` signatures | 0 | Wave900 closure export |
| `undefined` signatures | 0 | Wave900 closure export |
| Helper-placeholder residual target | 0 | Program gate target |
| Helper-placeholder residual observed | 0 (wave217 evidence) | `functions/FUNCTION_COVERAGE_STATE.md` notes |

## Post-100 Static System Reviews (901-909)

| Wave | Slice | Status | Review doc |
|---|---|---|---|
| 901 | Static system review baseline | static review doc | [`static-system-review-2026-05-26.md`](static-system-review-2026-05-26.md) |
| 902 | Save/options/career | static review doc | [`save-options-static-review-2026-05-26.md`](save-options-static-review-2026-05-26.md) |
| 903 | MissionScript/IScript | static review doc | [`missionscript-static-review-2026-05-26.md`](missionscript-static-review-2026-05-26.md) |
| 904 | Texture/resource/decode/render | static review doc | [`texture-render-static-review-2026-05-26.md`](texture-render-static-review-2026-05-26.md) |
| 905 | Mesh/motion/world/particle | static review doc | [`mesh-motion-world-particle-static-review-2026-05-26.md`](mesh-motion-world-particle-static-review-2026-05-26.md) |
| 906 | Unit/BattleEngine/gameplay | static review doc | [`unit-battleengine-gameplay-static-review-2026-05-26.md`](unit-battleengine-gameplay-static-review-2026-05-26.md) |
| 907 | Frontend/input/game-loop | static review doc | [`frontend-input-game-loop-static-review-2026-05-26.md`](frontend-input-game-loop-static-review-2026-05-26.md) |
| 908 | Audio/media/cutscene/camera | static review doc | [`audio-media-cutscene-static-review-2026-05-26.md`](audio-media-cutscene-static-review-2026-05-26.md) |
| 909 | Engine/platform/math/memory support | static review doc | [`engine-platform-support-static-review-2026-05-26.md`](engine-platform-support-static-review-2026-05-26.md) |

Runtime proof, exact layouts, and cross-system interaction maps remain separate from these static reviews.

## Subsystem Contract Matrix

| Priority Subsystem | Deep-Validated Contract Docs (count) | Status | Evidence |
|---|---:|---|---|
| Career/save core (`CCareer__Load/Save/SaveWithFlag`, options propagation) | 7 | static doc slice | `functions/Career.cpp/CCareer__Load.md`, `functions/Career.cpp/CCareer__Save.md`, `functions/Career.cpp/CCareer__SaveWithFlag.md`, plus save-callsite side-effect section in `CCareer__Save.md`; Wave902 static review |
| Frontend/display/windowing and mode selection | 6 | static doc slice | `windowed-mode-analysis.md`, `widescreen-patch-analysis.md`, `widescreen-diff-regions-28.tsv`, `functions/display-settings.md`, `capture-menu-behavior.md` |
| Input/control mapping/remap/capture | 6 | static doc slice | `functions/Controller.cpp/ControlBindings.md`, `functions/Controller.cpp/_index.md`, `functions/CLIParams.cpp/CLIParams__ParseCommandLine.md`, `capture-menu-behavior.md` |
| Render init/device reset/lost-device flow | 5 | static doc slice | `functions/display-settings.md`, `functions/Platform.cpp/_index.md`, `GHIDRA-REFERENCE.md` entries for `CD3DApplication__Resize3DEnvironment` + `Platform__HandleDeviceLostAndRestore` |
| Remaining high-impact subsystems (air/unit/world/frontend tails) | 12 | static doc slice | `high-impact-subsystem-contracts.md` + `high-impact-call-chain-appendix.md` + `scratch/program_2026-03-01/phase5_signature_readback/index.tsv` |

## Function Contract Requirements

Per-function contract completion for this gate requires all fields below:

1. Name
2. Owner proof (vtable/xrefs/field-layout/caller-type evidence)
3. Typed signature (no placeholder types where evidence exists)
4. Behavior summary (inputs/outputs/side effects/error paths)
5. Confidence label (`high`/`medium`/`low`) with rationale
6. Evidence links

Core career/save functions satisfy this structure today (see linked docs above). Post-100 subsystem reviews add static-coherence grouping on top of Wave900 per-function comment closure.

## Residual Uncertainty Queue

| Subsystem | Blocking Gap | Severity | Next Probe |
|---|---|---|---|
| FEPDebriefing | Dedicated xref export now documents data-dispatch caller anchor (`0x005db9c0`, `ref_type=DATA`) | low | Monitor only; expand only if direct caller expansion is explicitly requested |
| PauseMenu/text | Persistence and fallback call-chain appendices are explicit and evidence-backed | low | Monitor only; no blocking action unless regressions appear |
| Signature queue artifact | `phase5_signature_hardening_queue.tsv` executed with post-run read-back `9/9 OK` | low | Keep queue + read-back outputs as static gate evidence; update only if signatures are refined later |
| Runtime behavior | Wave900+ static closure does not certify gameplay, render pixels, audio playback, or patch behavior | medium | Use copied-profile harness, CDB, and targeted runtime probes per subsystem |

## Static Done Gate Decision (Current)

`CLOSED (EXPORT-CONTRACT QUEUE + POST-100 STATIC REVIEW DOCS)`

Export-contract gate criteria satisfied for the loaded Steam retail Ghidra database (not full RE validation):

- Satisfied: Wave900 closure at **6113/6113** commented functions, **0** commentless, **0** `param_N`, **0** `undefined`, weak-name zero, helper-placeholder zero (export-contract naming; strong-semantic legacy metric remains **6055/6055** weak-regex clean, not evidence-grade).
- Satisfied: post-100 read-only subsystem reviews **901-909** documented with verified backups (see table above).
- Remaining non-blocking follow-up: runtime proof, exact struct layouts, cross-system interaction maps, and optional per-function contract expansion beyond static-coherence slices.
