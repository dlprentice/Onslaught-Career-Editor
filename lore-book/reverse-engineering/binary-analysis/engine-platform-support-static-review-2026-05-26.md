# Engine / Platform / Math / Memory Static Review - Wave909

Status: complete static review evidence
Date: 2026-05-26
Scope: `engine-platform-support-static-review-wave909`
Classification: static-coherent engine/platform/math/memory support core

Wave909 is a read-only post-100 static review slice. It reviews `425` selected function rows across `23` families after the loaded Ghidra queue reached `6113/6113 = 100.00%` with `0` commentless, `0` exact-undefined signatures, and `0` `param_N` rows.

Family and cluster coverage:

| Cluster | Rows | Families |
| --- | ---: | --- |
| `engine-core` | 115 | `CDXEngine 60`, `CEngine 55` |
| `math-vector` | 84 | `Math 50`, `Vec3 18`, `Mat34 10`, `MathMatrix3x3 4`, `MathMatrix3x4 1`, `CEulerAngles 1` |
| `console-monitor` | 78 | `CConsole 31`, `CMonitor 27`, `CSPtrSet 16`, `CGenericActiveReader 4` |
| `memory-buffer` | 66 | `CMemoryHeap 17`, `CDXMemBuffer 15`, `OID 14`, `CDXMemoryManager 10`, `CFlexArray 10` |
| `platform-app` | 53 | `PCPlatform 19`, `CD3DApplication 18`, `PLATFORM 9`, `Platform 7` |
| `render-state-shared` | 29 | `SharedVFunc 18`, `D3DStateCache 11` |

Representative anchors:

- Engine/render shell: `CDXEngine__UpdateWrappedThingPositionsAndDistance`, `CDXEngine__SetRenderState_AlphaSpriteNoDepthWrite`, `CDXEngine__SetProjectionMatrix`, `CDXEngine__SetWorldMatrixElements`, `CEngine__Init`, `CEngine__Shutdown`, `CEngine__GetViewMatrixFromCamera`.
- Platform/app shell: `CD3DApplication__Init`, `CD3DApplication__Create`, `CD3DApplication__BuildDeviceList`, `Platform__HandleDeviceLostAndRestore`, `Platform__AsyncSaveCareer`, `PLATFORM__ProcessSystemMessages`, `PLATFORM__BeginScene`, `PCPlatform__InitAsyncMusicStream`, `PCPlatform__WriteSaveFile`.
- Console/monitor support: `CConsole__RegisterBuiltinCommands`, `CConsole__ExecuteBufferedCommandSlot`, `CMonitor__AddDeletionEvent`, `CMonitor__Process`, `CGenericActiveReader__SetReader`, `CSPtrSet__Clear`.
- Memory/object support: `CDXMemBuffer__OpenReadMode11`, `CDXMemBuffer__SetBufferSize`, `CDXMemoryManager__Alloc`, `CDXMemoryManager__Free`, `CMemoryHeap__Init`, `CMemoryHeap__FreeTiny`, `CFlexArray__Add`, `OID__CreateObject`, `OID__FreeObject_Callback`.
- Math/state support: `Math__InvLerpClamp01`, `Math__IsFloatDiffOutsideTolerance`, `MathMatrix3x3__Determinant`, `MathMatrix3x4__AssignFromEightScalars`, `Mat34__TransformVec3ByBasisToOut`, `Vec3__NormalizeInPlace`, `Vec3__Dot`, `D3DStateCache__SetStateCached`, `SharedVFunc__ReturnZero_00405930`.

Evidence artifacts:

- `subagents/ghidra-static-reaudit/wave909-engine-platform-support-static-review/engine-platform-support-baseline.json`
- `subagents/ghidra-static-reaudit/wave909-engine-platform-support-static-review/engine-platform-support-family-summary.tsv`
- `subagents/ghidra-static-reaudit/wave909-engine-platform-support-static-review/engine-platform-support-cluster-summary.tsv`
- `subagents/ghidra-static-reaudit/wave909-engine-platform-support-static-review/engine-platform-support-function-anchors.tsv`
- `subagents/ghidra-static-reaudit/wave909-engine-platform-support-static-review/backup-summary.json`

Verified backup: `G:\GhidraBackups\BEA_20260526-120420_post_wave909_engine_platform_support_static_review_verified`, `19` files, `173247367` bytes, `DiffCount=0`.

Source boundary: Stuart source remains architecture/name/logic reference, while the loaded Steam retail Ghidra rows are the authority for this static binary slice.

Transition planning note: [Engine / Platform / Math / Memory Support Proof Plan](engine-platform-math-memory-support-proof-plan.md) turns this Wave909 static-coherent surface plus Wave1041 CRT/FPU evidence, Wave1042 allocator evidence, Wave1095 render-state/matrix evidence, and Wave1214 math/color/screen dispatch evidence into copied-profile/app-owned child proof lanes. The plan is not runtime proof and does not claim device handling, platform I/O, allocator/OOM behavior, console execution, monitor/safe-pointer behavior, FPU/CRT side effects, visual QA, patch behavior, rebuild parity, or no-noticeable-difference parity.

What this proves:

- The selected engine/platform/math/memory/support rows are present in the current static function-quality corpus.
- Every selected row has a non-empty comment and clean signature under the current queue exporter.
- The selected rows form a coherent static support core linking engine init/render shell, platform/message/device handling, console command support, monitor safe-pointer support, allocator/object factory paths, math/vector helpers, and shared render-state/vfunc scaffolding.

What remains separate:

- Runtime device handling.
- Platform filesystem and registry side effects.
- Allocator/OOM/runtime memory behavior.
- Console command execution behavior.
- Monitor/safe-pointer runtime behavior.
- Exact layout/source-body identity.
- BEA patch behavior.
- Clean-room rebuild parity.
