# CRound__FindNearbyHostileWithinProjectileRadius

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__FindNearbyHostileWithinProjectileRadius` at `0x004daba0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004daba0`

## Identity
- Body `[0x004daba0,0x004dac8f]`, 240 bytes. Raw pristine-body SHA-256 `e4098c15e6daf348b5c0dd010aabaf56b47b4a68943b42c1af8307946ddb4e96`; closure range SHA-256 `d52c7fe5d51fec8a9dd2c5314b26b4a173fdf6eb82b74dd6f4c8506405bbda0d`; packet range-plus-bytes SHA-256 `e304bce0c9f9382de03a06baf0f62c021ecb9c6b7d155c6440cbeb3c76e9dd92`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name and packet/decompile metadata name: `CRound__FindNearbyHostileWithinProjectileRadius`. The matching labels are counted intent only, not recovered source symbols and not semantic proof.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=USER_DEFINED`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `DARK`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `void * __fastcall CRound__FindNearbyHostileWithinProjectileRadius(void * this)`. Register/stack details beyond that packet declaration are not_determinable; parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
void * __fastcall CRound__FindNearbyHostileWithinProjectileRadius(void * this)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `this` — unguarded receiver/base pointer supplying four floats at +0x1c..+0x28, one excluded pointer at +0xe8, and a radius-like scalar through +0xf0/+0x90.

## Return value meaning
Returns the first iterated nonnull owner pointer that differs from +0xe8, has bit 0x10 set at +0x34, has bit 0x04 clear at +0x2c, and whose displayed squared three-component separation is `< r*r` and `> 0.25`; returns null when iteration ends.

## Globals read/written
- `DAT_00704200` — its address is passed to the packet-listed first/next iteration callees.

## Callees relied on / callers
- Callees (packet structured array): `CMapWho__GetFirstEntryWithinRadius` `0x00491ea0` ×1 (STATIC_DIRECT); `CMapWho__GetNextEntryWithinRadius` `0x00492020` ×1 (STATIC_DIRECT); `CMapWhoEntry__GetOwner` `0x00492c90` ×1 (STATIC_DIRECT); `CThing__GetCentrePos` `0x004f3ac0` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `CRound__SpawnConfiguredProjectile` `0x004db150` ×1 site(s).
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
Starts an iteration with receiver floats and the +0xf0/+0x90 scalar, returns null at end, obtains each owner through the listed callee, applies pointer and bit tests, calls the listed position-output callee for passing owners, computes a squared three-component separation from receiver +0x1c/+0x20/+0x24, and returns the first pointer within the strict numeric bounds; otherwise advances the iteration.

## Error / edge behavior
`this`, +0xf0, returned owners, and the position output contract are only partially guarded. NaN fails the strict comparisons. Hostile/projectile wording is counted name intent and is not independently proven.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004daba0`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `d52c7fe5d51fec8a9dd2c5314b26b4a173fdf6eb82b74dd6f4c8506405bbda0d` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `e304bce0c9f9382de03a06baf0f62c021ecb9c6b7d155c6440cbeb3c76e9dd92` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `e4098c15e6daf348b5c0dd010aabaf56b47b4a68943b42c1af8307946ddb4e96` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004daba0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `DARK`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
2 — iteration, pointer/bit filters, squared-distance bounds, and first-match/null returns are explicit; owner categories and units remain unknown. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Units/roles of receiver and owner coordinates and +0x90 scalar.
- Meanings of bits 0x10 and 0x04 and the excluded +0xe8 pointer.
