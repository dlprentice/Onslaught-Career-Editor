# Deep Validation Status (Static RE Gate)

> Tracks ownership/type/behavior contract hardening required by the static RE completion program.
> Last updated: 2026-03-01

## Gate Snapshot

| Metric | Value | Source |
|---|---|---|
| Binary function objects | 5,861 | `functions/FUNCTION_COVERAGE_STATE.md` |
| Strong semantic names | 5,861 (100.00%) | `functions/FUNCTION_COVERAGE_STATE.md` |
| Weak-name objects (`FUN_`, `Auto_`, `__Unk_`) | 0 | `functions/FUNCTION_COVERAGE_STATE.md` |
| Helper-placeholder residual target | 0 | Program gate target |
| Helper-placeholder residual observed | 0 (wave217 evidence) | `functions/FUNCTION_COVERAGE_STATE.md` notes |

## Subsystem Contract Matrix

| Priority Subsystem | Deep-Validated Contract Docs (count) | Status | Evidence |
|---|---:|---|---|
| Career/save core (`CCareer__Load/Save/SaveWithFlag`, options propagation) | 7 | complete | `functions/Career.cpp/CCareer__Load.md`, `functions/Career.cpp/CCareer__Save.md`, `functions/Career.cpp/CCareer__SaveWithFlag.md`, plus save-callsite side-effect section in `CCareer__Save.md` |
| Frontend/display/windowing and mode selection | 6 | complete | `windowed-mode-analysis.md`, `widescreen-patch-analysis.md`, `widescreen-diff-regions-28.tsv`, `functions/display-settings.md`, `capture-menu-behavior.md` |
| Input/control mapping/remap/capture | 6 | complete | `functions/Controller.cpp/ControlBindings.md`, `functions/Controller.cpp/_index.md`, `functions/CLIParams.cpp/CLIParams__ParseCommandLine.md`, `capture-menu-behavior.md` |
| Render init/device reset/lost-device flow | 5 | complete | `functions/display-settings.md`, `functions/Platform.cpp/_index.md`, `GHIDRA-REFERENCE.md` entries for `CD3DApplication__Resize3DEnvironment` + `Platform__HandleDeviceLostAndRestore` |
| Remaining high-impact subsystems (air/unit/world/frontend tails) | 12 | complete | `high-impact-subsystem-contracts.md` + `high-impact-call-chain-appendix.md` + `scratch/program_2026-03-01/phase5_signature_readback/index.tsv` |

## Function Contract Requirements

Per-function contract completion for this gate requires all fields below:

1. Name
2. Owner proof (vtable/xrefs/field-layout/caller-type evidence)
3. Typed signature (no placeholder types where evidence exists)
4. Behavior summary (inputs/outputs/side effects/error paths)
5. Confidence label (`high`/`medium`/`low`) with rationale
6. Evidence links

Core career/save functions satisfy this structure today (see linked docs above). Remaining high-impact subsystems are tracked below.

## Residual Uncertainty Queue

| Subsystem | Blocking Gap | Severity | Next Probe |
|---|---|---|---|
| FEPDebriefing | Dedicated xref export now documents data-dispatch caller anchor (`0x005db9c0`, `ref_type=DATA`) | low | Monitor only; expand only if direct caller expansion is explicitly requested |
| PauseMenu/text | Persistence and fallback call-chain appendices are explicit and evidence-backed | low | Monitor only; no blocking action unless regressions appear |
| Signature queue artifact | `phase5_signature_hardening_queue.tsv` executed with post-run read-back `9/9 OK` | low | Keep queue + read-back outputs as static gate evidence; update only if signatures are refined later |

## Static Done Gate Decision (Current)

`CLOSED (STATIC VALIDATION THRESHOLD MET)`

Gate criteria are satisfied for static validation:

- Satisfied: full strong semantic naming coverage, weak-name zero, helper-placeholder zero, no unresolved critical doc contradictions in Phase 1 outputs.
- Remaining non-blocking follow-up: maintain signature/read-back artifacts and optionally expand caller-chain evidence only if future tasks require it.
