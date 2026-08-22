# CUnitAI__UpdateDoorWingEngagement_CloseRange

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__UpdateDoorWingEngagement_CloseRange` at `0x00445ad0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00445ad0`

## Identity
- Body `[0x00445ad0,0x00445f3e]`, 1135 bytes. Raw pristine-body SHA-256 `78fd3eddc516f66a1c407360410e9e9bc31da14346fee719ac0f6b60625f9949`; closure range SHA-256 `a54e61555ef739227802c098e31dd6b190ffd99145be94c29f941e17f5db85bb`; packet range-plus-bytes SHA-256 `dd9f268915b54f8ee32f1ff87f509305b0503ea59e109e2938c910b663987517`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__UpdateDoorWingEngagement_CloseRange` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `double __fastcall CUnitAI__UpdateDoorWingEngagement_CloseRange(void * doorWingAI)`. Register/stack details beyond that packet declaration are not_determinable here; parameter labels are counted intent only.

## Prototype and parameter semantics
```c
double __fastcall CUnitAI__UpdateDoorWingEngagement_CloseRange(void * doorWingAI)
```
- `doorWingAI` — analyzed receiver/base pointer supplying linked pointers at +8/+0xc, flags at +0x64/+0x68, threshold float +0x70, and indirect dispatch slots. The label is counted intent only.

## Return value meaning
not_determinable — the packet signature says `double`, while the decompile/comment records plain `RET` and inconsistent float/local-address expressions on exits; no structured caller evidence proves an ST0 consumer.

## Globals read/written
- `DAT_008a9d9c` — passed to the packet-listed random callee at all three structured sites.

## Callees relied on / callers
- Callees (packet structured array): `Vec3__SetXYZ` `0x00401ec0` ×2 (STATIC_DIRECT); `Vec3__Add` `0x00401ee0` ×1 (STATIC_DIRECT); `Vec3__NormalizeInPlace` `0x00406d50` ×1 (STATIC_DIRECT); `Vec3__SubtractToOut` `0x0040d120` ×2 (STATIC_DIRECT); `CUnitAI__PlayOpenAnimationIfState1Or3` `0x00445570` ×1 (STATIC_DIRECT); `CUnitAI__PlayCloseAnimationIfState0Or2` `0x004455c0` ×1 (STATIC_DIRECT); `Random__NextLCGAbs` `0x004de8d0` ×3 (STATIC_DIRECT); `CUnit__ForwardAttachedNodeVFunc1CIfPresent` `0x004fcec0` ×1 (STATIC_DIRECT); `CUnit__GetProfileState120` `0x004fda10` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CDiveBomberAI__VFunc_9_00445900` `0x00445900` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
Calls the packet-listed random callee once initially. The body branches on +0xc, indirect predicate results, linked flags, and derived 3D/2D separations with thresholds 55, 40, 15, and 20. It writes +0x64/+0x68, derives +0x70 from additional random-call results, invokes both packet-listed state/token helpers on separate branches, performs displayed vector set/subtract/normalize/add operations through the listed callees, can call the listed attached-node/profile helpers, and dispatches several indirect slots including +0xf4. Concrete engagement/movement meanings remain counted intent only.

## Error / edge behavior
Many receiver, linked, stack, and indirect values are unguarded or only conditionally initialized. Return expressions include local addresses cast through float and `fStack_3c`; exact return and several vector arguments are not_determinable from this decompile.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00445ad0`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `a54e61555ef739227802c098e31dd6b190ffd99145be94c29f941e17f5db85bb` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `dd9f268915b54f8ee32f1ff87f509305b0503ea59e109e2938c910b663987517` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `78fd3eddc516f66a1c407360410e9e9bc31da14346fee719ac0f6b60625f9949` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00445ad0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
1 — major distance/state/random/vector branches and all direct calls are visible, but return ABI, stack values, and indirect targets are materially ambiguous. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Whether any caller consumes an x87 return value.
- Origins of unresolved stack values and exact arguments to indirect +0xf4.
- Meanings/units of thresholds, flags, and +0x70.
