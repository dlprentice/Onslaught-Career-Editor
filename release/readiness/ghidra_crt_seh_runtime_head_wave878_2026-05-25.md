# Ghidra CRT/SEH Runtime Head Wave878 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `crt-seh-runtime-head-wave878`

Wave878 CRT/SEH runtime head saved comments and tags for eight adjacent CRT/compiler-runtime rows from `0x0055d731 CRT__SehDispatchWithScopeTable_Thunk_0055d731` through `0x0055dc8a CRT__EhVectorConstructorIterator_Unwind`. The pass verified the existing clean signatures, made no renames, no function-boundary changes, no executable-byte changes, did not launch BEA, and did not mutate the installed game.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0055d731 CRT__SehDispatchWithScopeTable_Thunk_0055d731` | Raw post-Wave877 commentless head; body forwards directly to `CRT__SehDispatchWithScopeTable`; xref export shows 512 callsites, primarily compiler-generated unwind/scope-table callsites in the `0x005d0f2b` tail. |
| `0x0055d767 CRT__SehInvokeCallSettingFrame12` | Xref from `CRT__CallCatchBlock` at `0x005607bb`; installs `CRT__SehCallback_Call_005602d2`, saves/restores `ExceptionList`, and calls `__CallSettingFrame_12`. |
| `0x0055d7e0 CRT__CallExceptionTranslator` | Xref from `CRT__ValidateCatchHandlersForThrow` at `0x00560547`; installs `CRT__SehFilterCppException`, saves/restores `ExceptionList`, gets a thread-local record, and invokes the translator-like callback at record offset `+0x68`. |
| `0x0055da5e CRT__SehStoreFrameGlobals` | Xrefs from `_longjmp`, `__local_unwind2`, and no-function runtime code; stores caller/frame globals into `DAT_006532d4`, `DAT_006532d8`, and `DAT_006532dc`. |
| `0x0055da76 CRT__InitRuntimeFromStoredFrameGlobals` | Computed call evidence from `CFastVB__RunStaticInitRangesWithOptionalCallback` plus DATA row `0x006532e8`; initializes float conversion dispatch, probes processor features, writes `DAT_009d08b8`, and initializes FPU control state. |
| `0x0055da8d CRT__InitFloatConversionDispatchTable` | Initializes float-conversion dispatch globals `0x00653658` through `0x0065366c` to `__cfltcvt`, `__fassign`, `CRT__InsertDecimalSeparatorBeforeExponent`, and two local helper labels. |
| `0x0055db72 CRT__EhVectorDestructorIterator_IfNoException` | Cleanup helper called by `CRT__EhVectorDestructorIterator_WithUnwind`; when the frame-local exception flag is clear, dispatches `eh_vector_destructor_iterator`. |
| `0x0055dc8a CRT__EhVectorConstructorIterator_Unwind` | Cleanup helper called by `eh_vector_constructor_iterator`; when the frame-local exception flag is clear, dispatches `eh_vector_destructor_iterator` for the partially constructed count. |

Read-back evidence:

- `ApplyCrtSehRuntimeHeadWave878.java dry`: `updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyCrtSehRuntimeHeadWave878.java apply`: `updated=8 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyCrtSehRuntimeHeadWave878.java final dry`: `updated=0 skipped=8 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 8 metadata rows, 8 tag rows, 522 xref rows, 150 instruction rows, 8 decompile rows, 14 context metadata rows, and 14 context decompile rows.
- Queue after Wave878: 6113 total, 5901 commented, 212 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed and strict clean-signature proxy `5901/6113 = 96.53%`.
- Next raw commentless row: `0x0055dcb0 OID__AcosWrapper`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-221858_post_wave878_crt_seh_runtime_head_verified`, 19 files, 172690311 bytes, `DiffCount=0`.

What this proves:

- The eight target function rows exist in the saved Ghidra project with the saved comments and `crt-seh-runtime-head-wave878` / `wave878-readback-verified` tags.
- The saved signatures remained clean and were read back unchanged.
- The observed behavior is static retail Ghidra decompile/xref/instruction evidence tied to CRT/SEH dispatch, exception translation, longjmp/local-unwind frame globals, runtime/FPU init, float conversion dispatch, and EH vector cleanup helpers.
- These are high-importance CRT/compiler runtime connector rows with low local evidence density, not low-importance filler.

What remains unproven:

- Exact MSVC helper identity/version and source-body identity.
- Exact SEH/EH frame, TLS, callback, and float-conversion table layouts.
- Runtime exception, translator, unwind, FPU, or numeric formatting behavior.
- BEA patching behavior.
- Rebuild parity.
