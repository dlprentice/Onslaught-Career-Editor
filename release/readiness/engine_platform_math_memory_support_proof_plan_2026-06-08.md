# Engine / Platform / Math / Memory Support Proof Plan Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x004081c0` → `CBattleEngine__Move` (was `CMonitor__Process`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: proof plan complete, not runtime proof
Date: 2026-06-08
Scope: `engine-platform-math-memory-support-proof-plan`

This readiness note records a public-safe static-to-proof planning slice for the engine/platform/math/memory support surface. It is not a new static re-audit wave, not a runtime test, not a screenshot/capture proof, not a Direct3D device proof, not an allocator/OOM proof, not a console execution proof, not a platform filesystem/registry proof, not a BEA patch, not a Godot slice, and not a rebuild parity claim.

Primary static source: `engine-platform-support-static-review-2026-05-26.md`. The plan records static authorities, child proof lanes, copied/app-owned guardrails, layout/ABI unknowns, side-effect boundaries, and stop conditions before any executable proof work can start.

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`.

Static source evidence:

- Wave909 (`engine-platform-support-static-review-wave909`): `425` selected rows across `23` families with clusters `engine-core 115`, `math-vector 84`, `console-monitor 78`, `memory-buffer 66`, `platform-app 53`, and `render-state-shared 29`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-120420_post_wave909_engine_platform_support_static_review_verified`.
- Wave1041 (`crt-fpu-runtime-tail-review-wave1041`): retained `CRT__InitRuntimeFromStoredFrameGlobals`, `CRT__FpuIntrinsicDispatch2Thunk`, `CRT__SetErrnoForFpSourceKind`, and `CRT__FloatDispatchAmsgExitCode2Thunk`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-090132_post_wave1041_crt_fpu_runtime_tail_review_verified`.
- Wave1042 (`memory-heap-allocator-review-wave1042`): retained `CMemoryHeap__Init`, `CMemoryHeap__ReallocTiny`, `CMemoryHeap__Cleanup`, `CMemoryHeap__Alloc`, `CMemoryHeap__ReAlloc`, `CMemoryHeap__Free`, `CMemoryHeap__AddToFreeList`, and `CMemoryHeap__SetMerge`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-094520_post_wave1042_memory_heap_allocator_review_verified`.
- Wave1095 (`render-state-matrix-support-review-wave1095`): retained `D3DStateCache__SetSlotMode4or5`, `D3DStateCache__SetStateCached`, `D3DStateCache__SetStateRaw`, `D3DStateCache__ForceSlotMode4or5`, `CDXEngine__SetProjectionMatrix`, `CDXEngine__SetWorldMatrixElements`, `CDXEngine__ApplyPendingRenderState`, and `CDXEngine__ApplyCachedLight`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-171413_post_wave1095_render_state_matrix_support_review_verified`.
- Wave1214 (`wave1214-math-color-screen-dispatch-current-risk-review`): retained `Color32__LerpArgb`, `Math__InvLerpClamp01`, `CPDSelector__ConvertNormalizedToScreenCoords`, `CRT__AcosDispatch_ST0`, `Math__BuildTranslationMatrix4x4_Dispatch_Thunk`, `Math__BuildQuaternionRotationMatrix_Dispatch_Thunk`, `Math__BuildQuaternionFromEulerAngles_Dispatch_Thunk`, and `Math__InterpolateVec4ByRatio_Dispatch_Thunk`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-081942_post_wave1214_math_color_screen_dispatch_current_risk_review_verified`.

Representative anchors:

| Surface | Static anchor |
| --- | --- |
| Engine shell | `CEngine__Init`, `CEngine__Shutdown`, `CDXEngine__SetProjectionMatrix`, `CDXEngine__SetWorldMatrixElements` |
| Platform/app shell | `CD3DApplication__BuildDeviceList`, `Platform__HandleDeviceLostAndRestore`, `PLATFORM__ProcessSystemMessages`, `PCPlatform__WriteSaveFile` |
| Console/monitor | `CConsole__RegisterBuiltinCommands`, `CConsole__ExecuteBufferedCommandSlot`, `CMonitor__AddDeletionEvent`, `CMonitor__Process`, `CSPtrSet__Clear` |
| Memory/object support | `CDXMemoryManager__Alloc`, `CDXMemoryManager__Free`, `CMemoryHeap__Init`, `CMemoryHeap__Alloc`, `CMemoryHeap__Free`, `OID__CreateObject`, `OID__FreeObject_Callback` |
| Math/vector/color | `Math__InvLerpClamp01`, `MathMatrix3x3__Determinant`, `Mat34__TransformVec3ByBasisToOut`, `Vec3__NormalizeInPlace`, `Vec3__Dot`, `Color32__LerpArgb` |
| Render state | `D3DStateCache__SetStateCached`, `D3DStateCache__SetSlotMode4or5`, `CDXEngine__ApplyPendingRenderState`, `CDXEngine__ApplyCachedLight` |
| CRT/FPU | `CRT__InitRuntimeFromStoredFrameGlobals`, `CRT__FpuIntrinsicDispatch2Thunk`, `CRT__SetErrnoForFpSourceKind`, `CRT__FloatDispatchAmsgExitCode2Thunk`, `CRT__AcosDispatch_ST0` |

Proof-plan boundaries:

- The plan is limited to future copied-profile, copied-file, or app-owned artifact-root work.
- Any future proof must select one child lane at a time: pure math equivalence, render-state/matrix support, allocator harness, monitor/safe-pointer behavior, platform/file I/O, console command path, or CRT/FPU side-effect isolation.
- Any future proof must keep platform/filesystem/registry side effects explicit and reversible.
- Any future proof must record whether inputs are copied retail data, sanitized fixtures, or generated app-owned data.
- Any future proof must stop on installed-game mutation need, device-loss ambiguity, filesystem/registry uncertainty, allocator OOM/mutex uncertainty, monitor lifetime ambiguity, global FPU/process-state uncertainty, unexpected file mutation, or broad support-core scope creep.
- Stop on installed-game mutation need is an explicit gate, not a warning to handle later.
- The plan explicitly does not include runtime device handling, runtime platform filesystem or registry side effects, runtime allocator/OOM behavior, runtime console command execution behavior, runtime monitor/safe-pointer behavior, runtime FPU/CRT side effects, visual QA, patch behavior, rebuild parity, or no-noticeable-difference parity.

No runtime device handling, runtime platform I/O, allocator/OOM behavior, console command execution behavior, monitor/safe-pointer behavior, FPU/CRT side effects, exact concrete layouts, exact source-body identity, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity claim is made.
