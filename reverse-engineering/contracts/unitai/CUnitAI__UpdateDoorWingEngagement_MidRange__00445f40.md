# CUnitAI__UpdateDoorWingEngagement_MidRange

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__UpdateDoorWingEngagement_MidRange` at `0x00445f40`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00445f40`

## Identity
- Body `[0x00445f40,0x00446141]`, 514 bytes. Raw pristine-body SHA-256 `d89783b997787d34ed7977ba7977ded668719928c420f948174549add7ea2338`; closure range SHA-256 `2a7f19004c7d52b72fb89ee362e004a5e07817d0cb1cd66da166dc7ccf08533f`; packet range-plus-bytes SHA-256 `2a87157c1525e5fcd6e082bf3f47b115cb4906d173e95ca17eafa8660cc08402`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__UpdateDoorWingEngagement_MidRange` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `double __fastcall CUnitAI__UpdateDoorWingEngagement_MidRange(void * doorWingAI)`. Register/stack details beyond that packet declaration are not_determinable here; parameter labels are counted intent only.

## Prototype and parameter semantics
```c
double __fastcall CUnitAI__UpdateDoorWingEngagement_MidRange(void * doorWingAI)
```
- `doorWingAI` — analyzed receiver/base pointer supplying linked pointers at +8/+0xc, flag +0x6c, and indirect dispatch slots. The label is counted intent only.

## Return value meaning
not_determinable — the packet signature says `double`, while the decompile/comment records plain `RET` and different residual float values on exits; no structured caller evidence proves an ST0 consumer.

## Globals read/written
- `DAT_008a9d9c` — passed to the packet-listed random callee once.

## Callees relied on / callers
- Callees (packet structured array): `Random__NextLCGAbs` `0x004de8d0` ×1 (STATIC_DIRECT); `CUnit__ForwardAttachedNodeVFunc14IfPresent` `0x004fce40` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CDiveBomberAI__VFunc_9_00445900` `0x00445900` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
Derives a float from one packet-listed random call and can replace it with an indirect result. If +0xc is null, it follows two indirect predicate/dispatch paths. Otherwise it computes 2D separation from linked +0x1c/+0x20 fields, sets +0x6c for distance above 35, may clear it for a 5-to-35 range when a wrapped angular difference exceeds 1.5707964, obtains additional values through indirect slot +0x168, subtracts 30 from one component, and either dispatches indirect +0xf4 or calls the one packet-listed attached-node helper according to +0x6c.

## Error / edge behavior
Receiver/linked pointers and indirect calls are largely unguarded. `fStack_28` and the exported return vary by path, so return meaning is not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00445f40`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `2a7f19004c7d52b72fb89ee362e004a5e07817d0cb1cd66da166dc7ccf08533f` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `2a87157c1525e5fcd6e082bf3f47b115cb4906d173e95ca17eafa8660cc08402` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `d89783b997787d34ed7977ba7977ded668719928c420f948174549add7ea2338` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00445f40.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
1 — distance/angle flag logic and final branch are visible, but indirect outputs and return ABI remain ambiguous. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Whether the residual x87 value is consumed.
- Contracts of indirect predicates, +0x168, and +0xf4.
- Meaning of +0x6c and units of distance/angle fields.
