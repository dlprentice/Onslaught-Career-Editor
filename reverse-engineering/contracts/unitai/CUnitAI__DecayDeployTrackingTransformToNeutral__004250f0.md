# CUnitAI__DecayDeployTrackingTransformToNeutral

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__DecayDeployTrackingTransformToNeutral` at `0x004250f0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004250f0`

## Identity
- Body `[0x004250f0,0x0042540f]`, 800 bytes. Raw pristine-body SHA-256 `6602de444b25495ff896eb6decd554b8194a466a14ce75e469dd3a59b594a9d6`; closure range SHA-256 `aefaa63b2533ef37ad78711d7f14a674d5ced43df0defe6218e1ea0806159af3`; packet range-plus-bytes SHA-256 `d5c85a41b35d4820e3ee180430732d33df72451f0a727dc14350a7761c45e542`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__DecayDeployTrackingTransformToNeutral` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `void __fastcall CUnitAI__DecayDeployTrackingTransformToNeutral(void * this)`. Register/stack details beyond that packet declaration are not_determinable here; parameter labels are counted intent only.

## Prototype and parameter semantics
```c
void __fastcall CUnitAI__DecayDeployTrackingTransformToNeutral(void * this)
```
- `this` — receiver/base pointer with a linked pointer at +0x110, source/destination matrix-like blocks, and scalars +0xa4/+0xa8.

## Return value meaning
not_applicable (void).

## Globals read/written
- not_applicable — no absolute data symbol is used by the displayed body.

## Callees relied on / callers
- Callees (packet structured array): `Vec3__SetXYZ` `0x00401ec0` ×3 (STATIC_DIRECT); `Mat34__SetRows` `0x00401f10` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CUnitAI__UpdateDeployAimAndScheduleEvent` `0x00424a20` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
When +0x110 is nonzero and linked bit 2 at +0x2c is clear, copies twelve floats from +0xb0 to +0x2c. It moves +0xa4 and +0xa8 toward zero by 0.01 per call, derives trigonometric coefficients from receiver and linked floats, invokes the packet-listed vector setter three times and matrix row setter once, then copies twelve floats from the local result back to +0x2c.

## Error / edge behavior
The body is skipped for a null linked pointer or set bit 2. The decompile passes `row0` without a visible assignment and obtains other row pointers through `extraout_EAX` values, so exact row provenance is not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x004250f0`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `aefaa63b2533ef37ad78711d7f14a674d5ced43df0defe6218e1ea0806159af3` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `d5c85a41b35d4820e3ee180430732d33df72451f0a727dc14350a7761c45e542` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `6602de444b25495ff896eb6decd554b8194a466a14ce75e469dd3a59b594a9d6` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004250f0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
1 — the gate, decay steps, trigonometric rebuild, and final copy are visible, but local row provenance is unresolved. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Origin of `row0` and the vector-setter extraout pointers.
- Concrete interpretation of the matrix-like blocks and linked +0x278/+0x280 fields.
