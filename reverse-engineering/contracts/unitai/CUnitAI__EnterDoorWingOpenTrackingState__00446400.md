# CUnitAI__EnterDoorWingOpenTrackingState

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__EnterDoorWingOpenTrackingState` at `0x00446400`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00446400`

## Identity
- Body `[0x00446400,0x00446479]`, 122 bytes. Raw pristine-body SHA-256 `2e751851fbcdf280f9baf78f64f22087271ce50076ec5ee6754fa93e09924e3f`; closure range SHA-256 `03654c7145708db5b88f9f4ede1e9913a1e60366fd63bb10d7539cea735ce125`; packet range-plus-bytes SHA-256 `64a37e9b73d4addb510de07d4162d52e1e0aa6738824c6de3ea317202bde8189`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__EnterDoorWingOpenTrackingState` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH_STATIC`.

## Calling convention
Packet records `__fastcall` for `void __fastcall CUnitAI__EnterDoorWingOpenTrackingState(void * doorWingAI)`. Register/stack details beyond that packet declaration are not_determinable here; parameter labels are counted intent only.

## Prototype and parameter semantics
```c
void __fastcall CUnitAI__EnterDoorWingOpenTrackingState(void * doorWingAI)
```
- `doorWingAI` — analyzed receiver/base pointer read/written at +0x68/+0x70 and linked through +8/+0xc. The label is counted intent only.

## Return value meaning
not_applicable (void).

## Globals read/written
- `DAT_008a9d9c` — passed to the packet-listed random callee when +0x68 is initially zero.

## Callees relied on / callers
- Callees (packet structured array): `CUnitAI__PlayOpenAnimationIfState1Or3` `0x00445570` ×1 (STATIC_DIRECT); `Random__NextLCGAbs` `0x004de8d0` ×1 (STATIC_DIRECT); `CUnit__ForwardAttachedNodeVFunc1CIfPresent` `0x004fcec0` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CUnitAI__UpdateDoorWingEngagement_LongRange` `0x00446150` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
If +0x68 is zero, stores 1 there, calls the packet-listed random callee, masks/adjusts its result, stores `(int(result) * 3.8146973e-05) + 15.0` at +0x70, and calls the packet-listed state/token helper with the +8 pointer. Independently, when +0xc is nonzero, it forwards that object's +0x1c/+0x20/+0x24/+0x28 values with the +8 pointer to the packet-listed attached-node helper.

## Error / edge behavior
The receiver and +8 linked pointer are unguarded. The +0xc coordinate reads are protected by a nonnull test; random range and state meaning are otherwise not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00446400`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `03654c7145708db5b88f9f4ede1e9913a1e60366fd63bb10d7539cea735ce125` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `64a37e9b73d4addb510de07d4162d52e1e0aa6738824c6de3ea317202bde8189` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `2e751851fbcdf280f9baf78f64f22087271ce50076ec5ee6754fa93e09924e3f` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00446400.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
2 — flag gate, random-derived store, state/token call, and guarded coordinate forwarding are explicit; field roles remain unknown. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Range/distribution after masking the random result.
- Meanings/units of +0x68/+0x70 and the forwarded values.
