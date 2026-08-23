# CRound__ArmProjectileAndSpawnTrailEffect

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__ArmProjectileAndSpawnTrailEffect` at `0x004db630`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004db630`

## Identity
- Body `[0x004db630,0x004db84c]`, 541 bytes. Raw pristine-body SHA-256 `b97b52f13468ab6628bd40d89c284f1e923a3a1d7efdd9ddab7113c472c707dc`; closure range SHA-256 `4a2ba9ab4c982cf5c4ca63415c7eb3535b882bdc1750e4f619ea597ce64f25f6`; packet range-plus-bytes SHA-256 `420bc0862e4edfb72511a3fd207c8064a4fb02afe0185990aec1b9ec5ae0b72e`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name and packet/decompile metadata name: `CRound__ArmProjectileAndSpawnTrailEffect`. The matching labels are counted intent only, not recovered source symbols and not semantic proof.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=USER_DEFINED`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `void __fastcall CRound__ArmProjectileAndSpawnTrailEffect(void * this)`. Register/stack details beyond that packet declaration are not_determinable; parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
void __fastcall CRound__ArmProjectileAndSpawnTrailEffect(void * this)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `this` — unguarded receiver/base pointer with +0xf0 gating data, +0x12c state, scalar/vector fields, and linked +0xe0/+0xe4 state.

## Return value meaning
not_applicable — the packet/decompile signature is void.

## Globals read/written
- `DAT_006fbdfc` — read, reduced by 0.05, and stored at receiver +0x24.
- `DAT_0083cc88`, `DAT_0083cc8c`, `DAT_0083cc90`, and `DAT_0083cc94` — forwarded to the conditional displayed effect-creation call.
- `DAT_00672fd0` — conditionally written into linked object word index 0x2b.

## Callees relied on / callers
- Callees (packet structured array): `ParticleEffectLink_T3_004cb0b0` `0x004cb0b0` ×1 (STATIC_DIRECT); `CParticleManager__CreateEffect` `0x004cb3d0` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CRound__UpdateRoundAndTriggerLaunchEffect` `0x004d9ef0` ×1 site(s).
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
Runs only when receiver +0x12c is zero and the dword at pointed-to +0x6c is nonzero. It sets +0x12c to 1, stores `DAT_006fbdfc-0.05` at +0x24, normalizes receiver floats +0x7c/+0x80/+0x84 when their magnitude is nonzero, clears +0x84, scales the three floats by pointed-to +0x2c times 0.05, and calls the listed +0xe0-region helper with zero. If pointed-to +4 is nonzero, it clears +0xe4, calls the listed creation helper, conditionally copies receiver position/transform-like dwords and time-like data into the linked object, copies twelve receiver dwords into linked +0x10, and writes 1 at linked +0xa0.

## Error / edge behavior
`this`, +0xf0, and most linked fields are unguarded. A zero vector skips reciprocal normalization before +0x84 is cleared; a null linked +0xe4 value skips copy/update work. Projectile/trail/arming wording is counted intent, not semantic proof.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004db630`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `4a2ba9ab4c982cf5c4ca63415c7eb3535b882bdc1750e4f619ea597ce64f25f6` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `420bc0862e4edfb72511a3fd207c8064a4fb02afe0185990aec1b9ec5ae0b72e` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `b97b52f13468ab6628bd40d89c284f1e923a3a1d7efdd9ddab7113c472c707dc` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004db630.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
1 — outer gate, state/height writes, normalization/scaling, link clear, conditional creation, and copies are visible; linked-object layout and high-level effects remain unknown. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Concrete meanings/units of +0x12c, +0x24, +0x7c..+0x84, and pointed-to scalars.
- Linked +0xe0/+0xe4 object layout and sentinel/time field at word 0x2b.
- Creation and link-helper failure/ownership contracts.
