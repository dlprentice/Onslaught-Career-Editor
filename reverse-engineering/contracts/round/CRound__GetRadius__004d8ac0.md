# CRound__GetRadius

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__GetRadius` at `0x004d8ac0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004d8ac0`

## Identity
- Body `[0x004d8ac0,0x004d8adb]`, 28 bytes. Raw pristine-body SHA-256 `c986f432cbada785b922a589cef8b7ed95fe96df48d1cb41090a06326e6e9382`; closure range SHA-256 `261bf76b8d99bec2670845875f7e4a2792c2de1a7ea267bfd0b6197ee4b5df3d`; packet range-plus-bytes SHA-256 `0e04ae655602d2f4bc1f507d03343f68dc6674904c71c10a1981184c8b1d603e`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name (canonical document identity): `CRound__GetRadius`. Packet/decompile metadata name: `VFuncSlot_16_004d8ac0`. They disagree; both are counted analysis/source-intent labels, and neither is semantic proof. The packet metadata name does not replace the canonical tracked name.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=USER_DEFINED`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `COVERED`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH_STATIC`.

## Calling convention
Packet records `__fastcall` for `double __fastcall VFuncSlot_16_004d8ac0(void * this)`. Register/stack details beyond that packet declaration are not_determinable; parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
double __fastcall VFuncSlot_16_004d8ac0(void * this)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `this` — unguarded base pointer used to follow +0xf0 and read floats at pointed-to offsets +0x2c and +0x8c.

## Return value meaning
Returns `(*(this+0xf0)+0x2c) * 0.05 * 0.5 + (*(this+0xf0)+0x8c)` as `double` after float arithmetic shown by the decompile.

## Globals read/written
- not_applicable — the displayed multipliers are literals; no absolute data symbol is read or written.

## Callees relied on / callers
- Callees (packet structured array): none recorded; visible indirect calls have no structured direct-callee VA.
- Callers (packet structured array): none recorded.
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
Loads two floats through +0xf0, scales the +0x2c value by 0.025, adds the +0x8c value, and returns the result.

## Error / edge behavior
Both pointer dereferences are unguarded. Units, overflow, NaN handling beyond ordinary floating-point operations, and radius wording are not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004d8ac0`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `261bf76b8d99bec2670845875f7e4a2792c2de1a7ea267bfd0b6197ee4b5df3d` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `0e04ae655602d2f4bc1f507d03343f68dc6674904c71c10a1981184c8b1d603e` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `c986f432cbada785b922a589cef8b7ed95fe96df48d1cb41090a06326e6e9382` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004d8ac0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH_STATIC`; cohort brief coverage `COVERED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
2 — the exact arithmetic expression is visible; units and descriptive interpretation remain unproven. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Meanings and units of the +0x2c and +0x8c floats.
- Whether the returned precision is constrained by the x87 ABI.
