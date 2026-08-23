# CRound__RemoveActiveReaderById

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__RemoveActiveReaderById` at `0x004dab50`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004dab50`

## Identity
- Body `[0x004dab50,0x004dab9c]`, 77 bytes. Raw pristine-body SHA-256 `6012c426d6d300c00b15c879c624bb156f5cbfc61b1dcbc37b19c6cf010f1615`; closure range SHA-256 `72531003c3718e1b5d154911689205291d73b5de1789831cae2ed8f0aefacb8e`; packet range-plus-bytes SHA-256 `974363850edc79b03eeae4e7e20b32b6ad6dc567227788f6f82596a3589aec12`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name and packet/decompile metadata name: `CRound__RemoveActiveReaderById`. The matching labels are counted intent only, not recovered source symbols and not semantic proof.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=USER_DEFINED`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `void __fastcall CRound__RemoveActiveReaderById(void * this)`. Register/stack details beyond that packet declaration are not_determinable; parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
void __fastcall CRound__RemoveActiveReaderById(void * this)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `this` — unguarded receiver/base pointer whose +0xe8/+0xec fields participate in all displayed calls.

## Return value meaning
not_applicable — the packet/decompile signature is void.

## Globals read/written
- `DAT_008551a0` — its address is passed to the packet-listed remove callee when the +0xe8 value has bit 0x08 at +0x34.

## Callees relied on / callers
- Callees (packet structured array): `CGenericActiveReader__SetReader` `0x00401000` ×1 (STATIC_DIRECT); `CBattleEngine__LockHit` `0x00407140` ×1 (STATIC_DIRECT); `CSPtrSet__Remove` `0x004e5bd0` ×1 (STATIC_DIRECT).
- Callers (packet structured array): `VFuncSlot_66_004d8e40` `0x004d8e40` ×1 site(s); `CRound__SelectBestTargetReaderAndSyncAimState` `0x004dac90` ×2 site(s); `CRound__SpawnConfiguredProjectile` `0x004db150` ×1 site(s).
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
If +0xec is nonnull and has bit 0x08 at +0x34, calls the listed +0xec/+0xe8 callee. If +0xe8 is nonnull and has the same bit, calls the listed remove callee with `(&DAT_008551a0, this)`. It then calls the listed setter with `(this+0xe8, null)`.

## Error / edge behavior
`this` is unguarded; +0xe8/+0xec nested dereferences are protected only by nonnull tests. Active-reader/removal wording is counted intent, and ownership/list invariants remain unknown.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004dab50`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `72531003c3718e1b5d154911689205291d73b5de1789831cae2ed8f0aefacb8e` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `974363850edc79b03eeae4e7e20b32b6ad6dc567227788f6f82596a3589aec12` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `6012c426d6d300c00b15c879c624bb156f5cbfc61b1dcbc37b19c6cf010f1615` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004dab50.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
2 — both bit-gated calls and final clear call are explicit; ownership and high-level reader semantics remain unproven. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Concrete layouts and ownership of +0xe8/+0xec.
- Meaning of +0x34 bit 0x08 and `DAT_008551a0` membership.
