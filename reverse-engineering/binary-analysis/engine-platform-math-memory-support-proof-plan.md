# Engine / Platform / Math / Memory Support Proof Plan

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x004081c0` → `CBattleEngine__Move` (was `CMonitor__Process`). Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: active public-safe proof plan, not runtime proof
Last updated: 2026-06-08
Scope: `engine-platform-math-memory-support-proof-plan`

This plan is the next selected static-to-proof slice from `roadmap/static-to-proof-rebuild-transition-backlog.md` after the Audio / Media / Cutscene / Camera Proof Plan. It converts the saved engine, platform, math, memory, monitor, console, render-state, and CRT/FPU static evidence into bounded child proof lanes for later app-owned support-infrastructure work.

This plan does not launch BEA, mutate Ghidra, mutate the installed game, patch an executable, capture screenshots, start Godot work, exercise Direct3D devices, execute console commands, allocate runtime memory under load, test filesystem/registry side effects, or claim runtime device handling, runtime platform I/O, allocator/OOM behavior, console command execution behavior, monitor/safe-pointer behavior, FPU/CRT side effects, visual QA, rebuild parity, or no-noticeable-difference parity.

The plan records static authorities, child proof lanes, copied-profile/app-owned guardrails, layout/ABI unknowns, side-effect boundaries, and stop conditions before any executable proof work can start. The child-lane labels include pure math helper equivalence, render-state/matrix support, allocator harnesses, monitor/safe-pointer behavior, platform/file I/O, console command paths, and CRT/FPU side-effect isolation.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`; it is not the active completion gate.

The percentage front door remains `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md` and `reverse-engineering/binary-analysis/static-reaudit-progress.json`. This proof plan does not create a new static RE percentage.

Primary static contract sources:

- `reverse-engineering/binary-analysis/engine-platform-support-static-review-2026-05-26.md`
- `reverse-engineering/binary-analysis/mapped-systems.md`
- `reverse-engineering/binary-analysis/functions/_index.md`
- `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md`

Relevant retained evidence:

- Wave909 engine/platform support static review (`engine-platform-support-static-review-wave909`): `425` selected function rows across `23` families after queue closure `6113/6113 = 100.00%`, with clusters `engine-core 115`, `math-vector 84`, `console-monitor 78`, `memory-buffer 66`, `platform-app 53`, and `render-state-shared 29`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-120420_post_wave909_engine_platform_support_static_review_verified`.
- Wave1041 CRT/FPU runtime tail review (`crt-fpu-runtime-tail-review-wave1041`): retained static evidence for `CRT__InitRuntimeFromStoredFrameGlobals`, `CRT__FpuIntrinsicDispatch2Thunk`, `CRT__SetErrnoForFpSourceKind`, and `CRT__FloatDispatchAmsgExitCode2Thunk`; no mutation. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-090132_post_wave1041_crt_fpu_runtime_tail_review_verified`.
- Wave1042 memory heap allocator review (`memory-heap-allocator-review-wave1042`): retained static evidence for `CMemoryHeap__Init`, `CMemoryHeap__ReallocTiny`, `CMemoryHeap__Cleanup`, `CMemoryHeap__Alloc`, `CMemoryHeap__ReAlloc`, `CMemoryHeap__Free`, `CMemoryHeap__AddToFreeList`, and `CMemoryHeap__SetMerge`; no mutation. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-094520_post_wave1042_memory_heap_allocator_review_verified`.
- Wave1095 render-state matrix support review (`render-state-matrix-support-review-wave1095`): retained render-state/matrix support evidence for `D3DStateCache__SetSlotMode4or5`, `D3DStateCache__SetStateCached`, `D3DStateCache__SetStateRaw`, `D3DStateCache__ForceSlotMode4or5`, `CDXEngine__SetProjectionMatrix`, `CDXEngine__SetWorldMatrixElements`, `CDXEngine__ApplyPendingRenderState`, and `CDXEngine__ApplyCachedLight`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-171413_post_wave1095_render_state_matrix_support_review_verified`.
- Wave1214 math/color/screen transform dispatch current-risk review (`wave1214-math-color-screen-dispatch-current-risk-review`): retained current-risk evidence for `Color32__LerpArgb`, `Math__InvLerpClamp01`, `CPDSelector__ConvertNormalizedToScreenCoords`, `CRT__AcosDispatch_ST0`, `Math__BuildTranslationMatrix4x4_Dispatch_Thunk`, `Math__BuildQuaternionRotationMatrix_Dispatch_Thunk`, `Math__BuildQuaternionFromEulerAngles_Dispatch_Thunk`, and `Math__InterpolateVec4ByRatio_Dispatch_Thunk`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-081942_post_wave1214_math_color_screen_dispatch_current_risk_review_verified`.

## Static Anchors

The proof plan is built around saved retail Ghidra evidence and public-safe static docs. Stuart source remains useful for names and architecture, but the loaded Steam retail binary remains authority for function names, call edges, comments, and bounded signatures.

| Surface | Static anchor |
| --- | --- |
| Engine shell | `CEngine__Init`, `CEngine__Shutdown`, `CEngine__GetViewMatrixFromCamera`, `CDXEngine__UpdateWrappedThingPositionsAndDistance`, `CDXEngine__SetProjectionMatrix`, and `CDXEngine__SetWorldMatrixElements`. |
| Platform/app shell | `CD3DApplication__Init`, `CD3DApplication__Create`, `CD3DApplication__BuildDeviceList`, `Platform__HandleDeviceLostAndRestore`, `PLATFORM__ProcessSystemMessages`, `PLATFORM__BeginScene`, `Platform__AsyncSaveCareer`, and `PCPlatform__WriteSaveFile`. |
| Console support | `CConsole__RegisterBuiltinCommands` and `CConsole__ExecuteBufferedCommandSlot`. |
| Monitor and safe pointers | `CMonitor__AddDeletionEvent`, `CGenericActiveReader__SetReader`, and `CSPtrSet__Clear`. The historical `CMonitor__Process` label at `0x004081c0` is excluded because current static evidence identifies that body as `CBattleEngine__Move`. |
| Memory/object support | `CDXMemBuffer__OpenReadMode11`, `CDXMemBuffer__SetBufferSize`, `CDXMemoryManager__Alloc`, `CDXMemoryManager__Free`, `CMemoryHeap__Init`, `CMemoryHeap__Alloc`, `CMemoryHeap__Free`, `CMemoryHeap__AddToFreeList`, `OID__CreateObject`, and `OID__FreeObject_Callback`. |
| Math/vector support | `Math__InvLerpClamp01`, `Math__IsFloatDiffOutsideTolerance`, `MathMatrix3x3__Determinant`, `MathMatrix3x4__AssignFromEightScalars`, `Mat34__TransformVec3ByBasisToOut`, `Vec3__NormalizeInPlace`, `Vec3__Dot`, and `Color32__LerpArgb`. |
| Render-state support | `D3DStateCache__SetStateCached`, `D3DStateCache__SetStateRaw`, `D3DStateCache__SetSlotMode4or5`, `D3DStateCache__ForceSlotMode4or5`, `CDXEngine__ApplyPendingRenderState`, and `CDXEngine__ApplyCachedLight`. |
| CRT/FPU support | `CRT__InitRuntimeFromStoredFrameGlobals`, `CRT__FpuIntrinsicDispatch2Thunk`, `CRT__SetErrnoForFpSourceKind`, `CRT__FloatDispatchAmsgExitCode2Thunk`, and `CRT__AcosDispatch_ST0`. |

## Child Proof Lanes

Later executable work should select one child lane at a time. Do not combine device handling, filesystem I/O, allocator behavior, console execution, monitor behavior, math equivalence, and FPU side effects into one runtime slice.

| Row | Planned proof item | Required evidence | Public-safe result |
| --- | --- | --- |
| 1 | Static support-contract extraction | Produce a compact support-infrastructure static contract from Wave909, Wave1041, Wave1042, Wave1095, and Wave1214 anchors. | Function-family checklist, call-edge notes, field-role unknowns, and side-effect boundaries. |
| 2 | Pure math helper equivalence design | Select deterministic scalar/vector/color/screen helpers with no platform, heap, device, or FPU-global side effects. | Input/output fixture plan and tolerance rules; no CPU/FPU dispatch claim unless separately proven. |
| 3 | Render-state/matrix support design | Select one state-cache or matrix handoff path and keep Direct3D device behavior out of scope. | Expected state-slot/matrix call checklist and global-layout unknowns. |
| 4 | Memory allocator proof design | Select copied/app-owned harness-only allocator fixtures after concrete block/header/merge/tiny-list unknowns are declared. | Allocation/free/realloc accounting plan and stop conditions for OOM/mutex ambiguity. |
| 5 | Monitor/safe-pointer proof design | Select one deletion-event or active-reader pointer-set path with explicit lifetime and list-layout unknowns. | Add/remove/process checklist and no runtime crash-safety claim until observed. |
| 6 | Platform/file I/O proof design | Select one copied-file/app-owned path such as a save/write helper only after the file root, side effects, and rollback are explicit. | App-owned I/O checklist and no installed-game mutation. |
| 7 | Console command proof design | Select one non-mutating command-buffer path only after command authority and output side effects are explicit. | Command registration/execution accounting and stop conditions. |
| 8 | CRT/FPU side-effect proof design | Select one pure dispatch or errno row only with isolated FPU/errno process-state guardrails. | Static-to-runtime checklist with process-state side effects marked as deferred unless isolated. |
| 9 | Stop conditions | Stop on installed-game mutation need, device-loss ambiguity, filesystem/registry uncertainty, allocator OOM/mutex uncertainty, monitor lifetime ambiguity, global FPU/process-state uncertainty, unexpected file mutation, or broad support-core scope creep. | Documented blocked/deferred status instead of widening scope. |
| 10 | Rebuild handoff | Translate proven child-lane behavior into clean-room support-runtime notes only after a later proof result identifies what was observed. | Static-to-runtime contract notes with exact runtime and layout gaps marked. |

## Copied/App-Owned Guardrails

Any later proof execution must:

- Use copied profiles, copied files, or app-owned artifact roots for generated outputs, caches, logs, patches, saves, or harness data.
- Never mutate the installed Steam game directory or original executable.
- Keep platform/filesystem/registry side effects explicit and reversible.
- Keep public notes aggregate and sanitized.
- Select one child lane at a time and preserve static/runtime/rebuild claim boundaries.
- Record whether the input is copied retail data, a sanitized fixture, or generated app-owned data.
- Stop if the proof requires broad runtime engine/platform behavior before the static child lane is explicit.

## Not Claimed

This plan is a static-to-proof planning artifact only. It does not prove:

- Runtime device handling.
- Runtime platform filesystem or registry side effects.
- Runtime allocator, OOM, mutex, or memory-pressure behavior.
- Runtime console command execution behavior.
- Runtime monitor/safe-pointer behavior.
- Runtime FPU/CRT errno, exit, dispatch, or processor-feature side effects.
- Exact concrete engine, platform, allocator, monitor, console, state-cache, math, or CRT layouts.
- Exact source-body identity.
- BEA patching behavior.
- Visual QA.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

## Exit Gate For This Planning Slice

This planning slice is complete only when:

- This document and its lore-book mirror match.
- `roadmap/static-to-proof-rebuild-transition-backlog.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, `reverse-engineering/binary-analysis/_index.md`, and `reverse-engineering/RE-INDEX.md` point to this plan.
- `reverse-engineering/binary-analysis/engine-platform-support-static-review-2026-05-26.md` points from the Wave909 static review to this plan.
- `release/readiness/engine_platform_math_memory_support_proof_plan_2026-06-08.md` records the same claim boundaries.
- `tools/engine_platform_math_memory_support_proof_plan_probe.py --check` passes.
- Static closeout probes still pass without changing `static-reaudit-progress.json` or `static-reaudit-current-risk-ledger.json`.
