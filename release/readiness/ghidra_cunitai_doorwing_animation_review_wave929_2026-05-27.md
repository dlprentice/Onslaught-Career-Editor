# Ghidra CUnitAI Door-Wing Animation Review Wave929 Readiness Note

Status: complete read-only static review
Date: 2026-05-27
Scope: `cunitai-doorwing-animation-review-wave929`

Wave929 re-reviewed three Wave911 focused CUnitAI open/close animation candidates, plus four same-family context helpers and one comparison target. The review made no Ghidra mutation, no rename, no signature change, no function-boundary change, and no executable-byte change.

Primary targets:

| Address | Saved state | Fresh evidence |
| --- | --- | --- |
| `0x00445570 CUnitAI__PlayOpenAnimationIfState1Or3` | `void __fastcall CUnitAI__PlayOpenAnimationIfState1Or3(void * unitAI)` | Xrefs from `0x00445d84 CUnitAI__UpdateDoorWingEngagement_CloseRange` and `0x00446445 CUnitAI__EnterDoorWingOpenTrackingState`; decompile gates state field `+0x280` on `1/3`, sets it to `2`, resolves string `0x00623bb4` (`open`), and dispatches animation vfunc `+0xf0`. |
| `0x004455c0 CUnitAI__PlayCloseAnimationIfState0Or2` | `void __fastcall CUnitAI__PlayCloseAnimationIfState0Or2(void * unitAI)` | Xrefs from `0x00445c3a CUnitAI__UpdateDoorWingEngagement_CloseRange` and `0x004462bb CUnitAI__UpdateDoorWingEngagement_LongRange`; decompile gates state field `+0x280` on `0/2`, sets it to `3`, resolves string `0x006289e4` (`close`), and dispatches animation vfunc `+0xf0`. |
| `0x00445610 CUnitAI__AdvanceOpenCloseShootAnimationState` | `int __fastcall CUnitAI__AdvanceOpenCloseShootAnimationState(void * unitAI)` | DATA xref `0x005e1328`; decompile compares the current attached animation index against `open` and `close`, transitions to strings `0x006289ec` (`shoot`) or `0x0062359c` (`fly`), and updates state field `+0x280` to `0` or `1`. Vtable export places this at `0x005e11b0` slot `94`, separate from the comparison target below. |

Context helpers:

| Address | Saved state | Fresh evidence |
| --- | --- | --- |
| `0x00445ad0 CUnitAI__UpdateDoorWingEngagement_CloseRange` | `double __fastcall CUnitAI__UpdateDoorWingEngagement_CloseRange(void * doorWingAI)` | Caller dispatch row from the door-wing update selector; decompile calls both primary open/close helpers and dispatches movement vfunc `+0xf4`. |
| `0x00445f40 CUnitAI__UpdateDoorWingEngagement_MidRange` | `double __fastcall CUnitAI__UpdateDoorWingEngagement_MidRange(void * doorWingAI)` | Same-family context row; decompile samples target/weapon context, toggles `+0x6c`, can dispatch movement vfunc `+0xf4`, and calls attached-node readiness helpers. |
| `0x00446150 CUnitAI__UpdateDoorWingEngagement_LongRange` | `double __fastcall CUnitAI__UpdateDoorWingEngagement_LongRange(void * doorWingAI)` | Caller dispatch row from the door-wing update selector; decompile calls the close helper and `CUnitAI__EnterDoorWingOpenTrackingState`. |
| `0x00446400 CUnitAI__EnterDoorWingOpenTrackingState` | `void __fastcall CUnitAI__EnterDoorWingOpenTrackingState(void * doorWingAI)` | Xref from `0x004463b6 CUnitAI__UpdateDoorWingEngagement_LongRange`; decompile enters open tracking and calls `CUnitAI__PlayOpenAnimationIfState1Or3`. |

Comparison target:

| Address | Saved state | Fresh evidence |
| --- | --- | --- |
| `0x00447fa0 CUnitAI__AdvanceDoorWingAnimationState` | `int __fastcall CUnitAI__AdvanceDoorWingAnimationState(void * unitAI)` | DATA xref `0x005e1ec4`; vtable export places this at `0x005e1e7c` slot `18`. Decompile recognizes `dooropening`, `doorclosing`, `doorclosed`, `wingfolded`, `wingunfolded`, `wingflat`, and `dooropen` strings, dispatches animation vfunc `+0xf0`, and writes state field `+0x27c`. This comparison keeps `0x00445610`'s `+0x280` open/close/shoot helper distinct from the broader door/wing animation state machine. |

Evidence:

- Primary exports: 3 metadata rows, 3 tag rows, 5 xref rows, 121 instruction rows, and 3 decompile rows.
- Context exports: 4 metadata rows, 4 tag rows, 4 xref rows, 770 instruction rows, and 4 decompile rows.
- Comparison export: 1 metadata row, 1 tag row, 1 xref row, 100 instruction rows, and 1 decompile row for `0x00447fa0`.
- Vtable export: 256 rows across `0x005e11b0` and `0x005e1e7c`, including `0x00445610` at `0x005e11b0` slot `94` and `0x00447fa0` at `0x005e1e7c` slot `18`.
- String dumps verified `0x00623bb4=open`, `0x006289e4=close`, `0x006289ec=shoot`, and `0x0062359c=fly`.
- Wave911 focused re-audit progress after Wave929: `111/1408 = 7.88%`; context helpers are not counted against that progress denominator.
- Static export-contract closure remains `6113/6113 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260527-231046_post_wave929_cunitai_doorwing_animation_review_verified`, 19 files, 173247367 bytes, `DiffCount=0`.

What this proves:

- The saved names, signatures, tags, xrefs, instruction bodies, string literals, and decompiles for the two call-backed open/close helpers and the open/close/shoot helper remain internally consistent with prior wave110 and Wave358 bounded claims.
- Door-wing state field `+0x280` remains distinct from Wave928 deploy-state field `+0x260` and context-helper animation-completion state `+0x244`.
- The same-family context helpers continue to route into the open/close helpers through close-range, long-range, and open-tracking paths.
- The broader `0x00447fa0 CUnitAI__AdvanceDoorWingAnimationState` remains a separate `+0x27c` door/wing animation state machine row in fresh comparison evidence; Wave929 does not merge it with `0x00445610`.

What remains unproven:

- Runtime door-wing animation behavior.
- Runtime targeting behavior.
- Exact `CUnitAI` field names/layout beyond observed offsets.
- Exact source-body identity or source method names.
- Whether `0x00445610` and `0x00447fa0` share higher-level runtime state-machine ownership.
- BEA patch behavior, gameplay outcomes, and rebuild parity.
