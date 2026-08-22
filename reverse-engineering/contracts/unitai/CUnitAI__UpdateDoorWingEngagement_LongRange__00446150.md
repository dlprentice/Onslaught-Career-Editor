# CUnitAI__UpdateDoorWingEngagement_LongRange

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__UpdateDoorWingEngagement_LongRange` at `0x00446150`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00446150`

## Identity
- Body `[0x00446150,0x004463ff]`, 688 bytes. Raw pristine-body SHA-256 `287165cd51768ddceb8e91dfcb0216e2a43b4757a2f9e2c9acd83571ca17224e`; closure range SHA-256 `69b23a8b9e4a475d62f3c3c537da6acc98dff3ef221f51433d4814f3d40c3516`; packet range-plus-bytes SHA-256 `fca3e2f9e8c6df830c7796fc849c0fcba293b44615742fbdf6a07d6180981daf`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__UpdateDoorWingEngagement_LongRange` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `double __fastcall CUnitAI__UpdateDoorWingEngagement_LongRange(void * doorWingAI)`. Register/stack details beyond that packet declaration are not_determinable here; parameter labels are counted intent only.

## Prototype and parameter semantics
```c
double __fastcall CUnitAI__UpdateDoorWingEngagement_LongRange(void * doorWingAI)
```
- `doorWingAI` — analyzed receiver/base pointer supplying linked pointers at +8/+0xc, flag +0x68, threshold +0x70, and indirect dispatch slots. The label is counted intent only.

## Return value meaning
not_determinable — the packet signature says `double`, while the decompile/comment records plain `RET` and residual stack-float returns without a proven structured caller consumer.

## Globals read/written
- `DAT_008a9d9c` — passed to the packet-listed random callee at both structured sites.

## Callees relied on / callers
- Callees (packet structured array): `CUnitAI__PlayCloseAnimationIfState0Or2` `0x004455c0` ×1 (STATIC_DIRECT); `CUnitAI__EnterDoorWingOpenTrackingState` `0x00446400` ×1 (STATIC_DIRECT); `Random__NextLCGAbs` `0x004de8d0` ×2 (STATIC_DIRECT); `CUnit__ForwardAttachedNodeVFunc1CIfPresent` `0x004fcec0` ×1 (STATIC_DIRECT); `CUnit__GetProfileState120` `0x004fda10` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CDiveBomberAI__VFunc_9_00445900` `0x00445900` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
Calls the packet-listed random callee initially, then branches on +0xc and indirect predicate/profile results. With a linked +0xc pointer it derives 3D separation minus two indirect scalar results. When +0x68 is zero it dispatches a position derived from linked matrix/position fields and calls the packet-listed state-entry helper if separation exceeds +0x70. When +0x68 is nonzero it calls the listed attached-node helper; if separation falls below +0x70, it clears +0x68, derives a new +0x70 from the second random call, invokes the packet-listed close-token helper, and dispatches another derived position.

## Error / edge behavior
Receiver/linked pointers and indirect calls are largely unguarded. Several stack values and all residual return values lack stable provenance, so exact output/return semantics are not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00446150`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `69b23a8b9e4a475d62f3c3c537da6acc98dff3ef221f51433d4814f3d40c3516` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `fca3e2f9e8c6df830c7796fc849c0fcba293b44615742fbdf6a07d6180981daf` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `287165cd51768ddceb8e91dfcb0216e2a43b4757a2f9e2c9acd83571ca17224e` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00446150.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
1 — separation/threshold state transitions and all direct calls are visible, but indirect scalar sources, stack values, and return ABI are ambiguous. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Whether any residual x87 value is consumed.
- Contracts of indirect scalar/position slots and profile predicate.
- Meaning and units of +0x68/+0x70 and separation values.
