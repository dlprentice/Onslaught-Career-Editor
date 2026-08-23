# CRound__Shutdown

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__Shutdown` at `0x004d8dc0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004d8dc0`

## Identity
- Body `[0x004d8dc0,0x004d8e38]`, 121 bytes. Raw pristine-body SHA-256 `6115be53ac54c0be415084c24c4b40bf6b8c8e68b67f2f2e96e28feeeaeb45ed`; closure range SHA-256 `2e7a10965d8169ae3d73248c64ac8a3450c3bce2b2ad28e6b5717b2f6e57e53c`; packet range-plus-bytes SHA-256 `064cc1eb64708b2d4383ace9586eaefa53a54e796cd96b51411028ee14c8e290`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name (canonical document identity): `CRound__Shutdown`. Packet/decompile metadata name: `VFuncSlot_02_004d8dc0`. They disagree; both are counted analysis/source-intent labels, and neither is semantic proof. The packet metadata name does not replace the canonical tracked name.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=USER_DEFINED`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `PARTIAL`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `void __fastcall VFuncSlot_02_004d8dc0(void * this)`. Register/stack details beyond that packet declaration are not_determinable; parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
void __fastcall VFuncSlot_02_004d8dc0(void * this)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `this` — unguarded receiver/base pointer whose +0xf0 block and +0xe0/+0xe8/+0xec regions drive the displayed calls.

## Return value meaning
not_applicable — the packet/decompile signature is void.

## Globals read/written
- `DAT_008550f0` — its address is passed to a conditional packet-listed remove call.
- `DAT_008551a0` — its address is passed to a second conditional packet-listed remove call.

## Callees relied on / callers
- Callees (packet structured array): `CGenericActiveReader__SetReader` `0x00401000` ×1 (STATIC_DIRECT); `CBattleEngine__LockHit` `0x00407140` ×1 (STATIC_DIRECT); `ParticleEffectLink_T3_004cb0b0` `0x004cb0b0` ×1 (STATIC_DIRECT); `CSPtrSet__Remove` `0x004e5bd0` ×2 (STATIC_DIRECT); `CComplexThing__Shutdown` `0x004f41b0` ×1 (STATIC_DIRECT).
- Callers (packet structured array): none recorded.
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
Conditionally calls the listed remove callee for `DAT_008550f0` based on a dword at +0xf0/+0x58, calls the listed +0xe0-region callee with zero, conditionally calls the listed +0xec/+0xe8 callee when +0xec has bit 0x08 at +0x34, conditionally removes `this` from `DAT_008551a0` when +0xe8 has that bit, clears the +0xe8 cell through the listed setter, then calls the final listed base-pointer callee.

## Error / edge behavior
`this` and +0xf0 are unguarded; nested +0xec/+0xe8 dereferences are only partially guarded. List membership, reader ownership, and shutdown meaning are counted name intent rather than proven contracts.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004d8dc0`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `2e7a10965d8169ae3d73248c64ac8a3450c3bce2b2ad28e6b5717b2f6e57e53c` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `064cc1eb64708b2d4383ace9586eaefa53a54e796cd96b51411028ee14c8e290` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `6115be53ac54c0be415084c24c4b40bf6b8c8e68b67f2f2e96e28feeeaeb45ed` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004d8dc0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `PARTIAL`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
2 — all direct-call gates and order are explicit; ownership, list invariants, and high-level shutdown semantics remain unknown. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Concrete invariants of +0xe0/+0xe8/+0xec and both global sets.
- Side effects and failure contracts of the five direct callees.
