# Ghidra CUnit Active-Reader Targeting Review Wave927 Readiness Note

Status: complete read-only static review
Date: 2026-05-27
Scope: `cunit-active-reader-targeting-review-wave927`

Wave927 re-reviewed five Wave911 focused candidates in the CUnit/CUnitAI active-reader targeting lane, plus one context helper from Wave523. The review made no Ghidra mutation, no rename, no signature change, no function-boundary change, and no executable-byte change.

Primary targets:

| Address | Saved state | Fresh evidence |
| --- | --- | --- |
| `0x00428b50 CUnit__SetReaderAndComputeRelativeYaw` | `void __thiscall CUnit__SetReaderAndComputeRelativeYaw(void * this, void * reader, void * readerContext, int unusedMode)` | Xref from `0x004f8d7c CUnit__Init`; decompile stores the active reader at `this+0x26c`, stores context at `this+0x270`, computes relative yaw into `this+0x274`, and mirrors flag `0x100000`. |
| `0x00428bc0 CUnitAI__GetTargetHeadingWithOffset` | `double __fastcall CUnitAI__GetTargetHeadingWithOffset(void * this)` | Xref from `0x004292c7 CUnitAI__UpdateHeadingTowardTargetClamped`; decompile returns active-reader heading `+0x114` plus relative-yaw offset `this+0x274`, or zero-heading fallback when no reader exists. |
| `0x00429270 CUnitAI__UpdateHeadingTowardTargetClamped` | `void __fastcall CUnitAI__UpdateHeadingTowardTargetClamped(void * turnContext)` | DATA slot xref `0x005d9660`; fresh decompile starts at the corrected true entry and includes the prologue loading the UnitAI pointer from `turnContext+0x18` before heading/clamp logic. |
| `0x004e97e0 CGenericActiveReader__SwapWithCandidateIfFormationCloser` | `bool __thiscall CGenericActiveReader__SwapWithCandidateIfFormationCloser(void * this, void * candidate_reader)` | Xref from `0x004e8640 CSquadNormal__ResolveFormationSlotConflicts`; decompile compares current and cross-assigned formation offsets, then swaps reader cells through `CGenericActiveReader__SetReader` only when the candidate pairing is closer. |
| `0x004fd3d0 CUnit__IsCandidateSideCompatibleForTargeting` | `bool __thiscall CUnit__IsCandidateSideCompatibleForTargeting(void * this, int candidate_side)` | 19 call xrefs across BattleEngine, targeting, round, unit, and component paths; decompile remains one explicit `candidate_side` argument and gates side/team values through `this+0x138` plus profile field `this+0x164 -> +0x128`. |

Context helper:

| Address | Saved state | Fresh evidence |
| --- | --- | --- |
| `0x004fb650 CUnit__ForwardAimTransformAndAttachTargetReader` | `void __thiscall CUnit__ForwardAimTransformAndAttachTargetReader(void * this, void * target_transform, void * target_reader)` | Context export confirms Wave523's generic CUnit-family aim/reader forwarder: xrefs include `CGillMHeadAI__UpdateAimTransformAndTargetReader` and `CWarspite__Update`; decompile null-gates `this+0x140` before forwarding to `OID__UpdateAimTransformAndAttachTargetReader`. |

Evidence:

- Primary exports: 5 metadata rows, 5 tag rows, 23 xref rows, 464 instruction rows, and 5 decompile rows.
- Context export: 1 metadata row, 1 tag row, 13 xref rows, 9 instruction rows, and 1 decompile row.
- Wave911 focused re-audit progress after Wave927: `103/1408 = 7.32%`; the context helper is not counted against that progress denominator.
- Static export-contract closure remains `6113/6113 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260527-223748_post_wave927_cunit_active_reader_targeting_review_verified`, 19 files, 173247367 bytes, `DiffCount=0`.

What this proves:

- The saved names, signatures, tags, xrefs, instruction bodies, and decompiles for these five primary rows remain internally consistent with their prior Wave325, Wave509, and Wave540 bounded claims.
- The `0x004fb650` context helper still supports the generic CUnit-family aim/reader forwarding bridge documented by Wave523.

What remains unproven:

- Runtime targeting, steering, side/team, or formation behavior.
- Exact `CUnit`, `CUnitAI`, and active-reader layouts.
- Exact source-body identity or source method names.
- BEA patch behavior, gameplay outcomes, and rebuild parity.
