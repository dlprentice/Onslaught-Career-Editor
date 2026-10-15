# CUnitAI__UpdateDeployTrackingTransformTowardTarget

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__UpdateDeployTrackingTransformTowardTarget` at `0x00424ca0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00424ca0`

## Identity
- Body `[0x00424ca0,0x004250e6]`, 1095 bytes. Raw pristine-body SHA-256 `9c0c097738a1b1a62fa75666dce81a683bc07f2495d999fd4b894b928598d1db`; closure range SHA-256 `bc0f2bfa1f6aa4912063d70f26643ab9ebcd8b1bccc002588f7ae781010dfcaa`; packet range-plus-bytes SHA-256 `91698ff09460f49b59fa912634f5f819161797399acf5bd8173bc70cf45b4e70`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__UpdateDeployTrackingTransformTowardTarget` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `void __fastcall CUnitAI__UpdateDeployTrackingTransformTowardTarget(void * this)`. Register/stack details beyond that packet declaration are not_determinable here; parameter labels are counted intent only.

## Prototype and parameter semantics
```c
void __fastcall CUnitAI__UpdateDeployTrackingTransformTowardTarget(void * this)
```
- `this` — receiver/base pointer with a linked pointer at +0x110, matrix-like dword blocks at +0x2c/+0xb0, scalar fields +0x9c..+0xa8, and current output storage.

## Return value meaning
not_applicable (void).

## Globals read/written
- `DAT_006fadc8` — its address is passed to the packet-listed sampling callee.

## Callees relied on / callers
- Callees (packet structured array): `vector_constructor_iterator_nothrow` `0x004011b0` ×1 (STATIC_DIRECT); `Vec3__SetXYZ` `0x00401ec0` ×2 (STATIC_DIRECT); `ElapsedTime__BelowThreshold_D4` `0x00401fd0` ×1 (STATIC_DIRECT); `Mat34__SetFromEulerAngles_004062d0` `0x004062d0` ×1 (STATIC_DIRECT); `SharedUnitVFunc_T3_00408120` `0x00408120` ×1 (STATIC_DIRECT); `Mat34__MultiplyBasisToOut` `0x0040d320` ×1 (STATIC_DIRECT); `CMonitor__SampleHeightfieldNormalAtXY` `0x0047ec60` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CUnitAI__UpdateDeployAimAndScheduleEvent` `0x00424a20` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
When +0x110 is nonzero and bit 2 of linked +0x2c is clear, copies twelve dwords from +0xb0 to +0x2c. It derives scalars from receiver +0x9c/+0xa0 and linked +0x114/+0x278/+0x280, optionally adjusts them after one packet-listed predicate, chooses either `(0,0,-1)` or a sampled three-float value after another indirect/predicate gate, derives cross products and normalized components, moves +0xa4 and +0xa8 toward derived targets in 0.01 steps, constructs matrices through the packet-listed vector/matrix callees, multiplies them, and copies twelve result dwords to +0x2c.

## Error / edge behavior
The body is skipped for a null linked pointer or set bit 2. Decompiler values `extraout_var`, `extraout_EAX`, and `extraout_EAX_00` participate in control/data flow, so exact vector construction and boolean interpretation are not_determinable without lower-level review.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00424ca0`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `bc0f2bfa1f6aa4912063d70f26643ab9ebcd8b1bccc002588f7ae781010dfcaa` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `91698ff09460f49b59fa912634f5f819161797399acf5bd8173bc70cf45b4e70` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `9c0c097738a1b1a62fa75666dce81a683bc07f2495d999fd4b894b928598d1db` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00424ca0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
1 — the gate, matrix copies, stepwise scalar updates, sampler, and final matrix write are visible, but extraout values and indirect calls materially limit exact semantics. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Machine-level sources of the `extraout_*` values.
- Contracts of the linked-object indirect calls and concrete matrix/vector layouts.
- Meaning and units of +0xa4/+0xa8 target adjustments.
