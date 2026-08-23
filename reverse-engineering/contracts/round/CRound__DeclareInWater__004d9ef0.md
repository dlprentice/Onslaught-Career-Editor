# CRound__DeclareInWater

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__DeclareInWater` at `0x004d9ef0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004d9ef0`

## Identity
- Body `[0x004d9ef0,0x004d9f2b]`, 60 bytes. Raw pristine-body SHA-256 `cca25281f2ca91e693706e799be2672bd435992e7ed85329ba1f41bda019aacb`; closure range SHA-256 `da47243cb8577ff2e712c14bb66de9a323a9ce9739f745d63d411bd442d39bff`; packet range-plus-bytes SHA-256 `e1ae24c39b9479c665b9a0a2c232194547c65a0b430107240e28d0b3d81861c9`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name (canonical document identity): `CRound__DeclareInWater`. Packet/decompile metadata name: `CRound__UpdateRoundAndTriggerLaunchEffect`. They disagree; both are counted analysis/source-intent labels, and neither is semantic proof. The packet metadata name does not replace the canonical tracked name.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=USER_DEFINED`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `void __fastcall CRound__UpdateRoundAndTriggerLaunchEffect(void * this)`. Register/stack details beyond that packet declaration are not_determinable; parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
void __fastcall CRound__UpdateRoundAndTriggerLaunchEffect(void * this)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `this` — unguarded receiver/base pointer passed to all three packet-listed direct callees and used for one indirect slot +0xc8 call.

## Return value meaning
not_applicable — the packet/decompile signature is void.

## Globals read/written
- not_applicable — no absolute data symbol is directly read or written in the displayed body.

## Callees relied on / callers
- Callees (packet structured array): `CActor__SetFieldD0ToNow_00402010` `0x00402010` ×1 (STATIC_DIRECT); `CRound__UpdateEffectTransformByMode_004d9f30` `0x004d9f30` ×1 (STATIC_DIRECT); `CRound__ArmProjectileAndSpawnTrailEffect` `0x004db630` ×1 (STATIC_DIRECT).
- Callers (packet structured array): none recorded.
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
Calls `CRound__ArmProjectileAndSpawnTrailEffect` and `CActor__SetFieldD0ToNow_00402010`
unconditionally. If dwords at pointed-to offsets `*(this+0xf0)+0x5c` and +0x6c are both zero,
calls `CRound__UpdateEffectTransformByMode_004d9f30` with `(this, 2, null, null)` and invokes
indirect slot +0xc8.

## Error / edge behavior
`this`, +0xf0, and the indirect slot are unguarded. Nonzero at either tested field suppresses the mode-2 call and indirect dispatch; water/launch wording is counted intent only.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004d9ef0`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `da47243cb8577ff2e712c14bb66de9a323a9ce9739f745d63d411bd442d39bff` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `e1ae24c39b9479c665b9a0a2c232194547c65a0b430107240e28d0b3d81861c9` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `cca25281f2ca91e693706e799be2672bd435992e7ed85329ba1f41bda019aacb` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004d9ef0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
2 — unconditional call order and the two-field conjunction controlling the final two actions are explicit; field and high-level meanings remain unknown. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Meaning of the two pointed-to dwords and mode value 2.
- Contract of indirect slot +0xc8 and side effects of the three direct callees.
