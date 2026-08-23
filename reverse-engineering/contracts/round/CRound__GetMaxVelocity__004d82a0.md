# CRound__GetMaxVelocity

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__GetMaxVelocity` at `0x004d82a0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004d82a0`

## Identity
- Body `[0x004d82a0,0x004d82ca]`, 43 bytes. Raw pristine-body SHA-256 `ba0fab8d92af843dba3b9c5f1211ddd201ec160e393f36a42458602847c13b4d`; closure range SHA-256 `17269ab4b95bb37b8dd575d8c64d75bef026fd696749e53be08dd66e5ae746d2`; packet range-plus-bytes SHA-256 `bbdc1813990f3a50476815d358be84e1f804afa3ac42971da808c9e37921d488`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name (canonical document identity): `CRound__GetMaxVelocity`. Packet/decompile metadata name: `VFuncSlot_15_004d82a0`. They disagree; both are counted analysis/source-intent labels, and neither is semantic proof. The packet metadata name does not replace the canonical tracked name.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=USER_DEFINED`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `COVERED`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH_STATIC`.

## Calling convention
Packet records `__fastcall` for `double __fastcall VFuncSlot_15_004d82a0(void * this)`. Register/stack details beyond that packet declaration are not_determinable; parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
double __fastcall VFuncSlot_15_004d82a0(void * this)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `this` — unguarded receiver/base pointer used for indirect slot +0xb4 and to read a pointed-to block through +0xf0.

## Return value meaning
Returns `160.0` when indirect slot +0xb4 yields nonzero; otherwise returns the float at `*(this+0xf0)+0x2c` widened to `double`.

## Globals read/written
- not_applicable — no absolute data symbol is read or written in the displayed body.

## Callees relied on / callers
- Callees (packet structured array): none recorded; visible indirect calls have no structured direct-callee VA.
- Callers (packet structured array): none recorded.
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
Invokes indirect slot +0xb4 once, compares its floating result with zero, and selects either literal 160.0 or one float loaded through +0xf0/+0x2c.

## Error / edge behavior
The receiver, +0xf0 pointer, and indirect slot are unguarded. Units and NaN behavior beyond the machine comparison are not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004d82a0`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `17269ab4b95bb37b8dd575d8c64d75bef026fd696749e53be08dd66e5ae746d2` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `bbdc1813990f3a50476815d358be84e1f804afa3ac42971da808c9e37921d488` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `ba0fab8d92af843dba3b9c5f1211ddd201ec160e393f36a42458602847c13b4d` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004d82a0.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH_STATIC`; cohort brief coverage `COVERED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
2 — the indirect predicate and two numeric return paths are explicit; value units and the slot contract are unknown. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Contract of indirect slot +0xb4.
- Meaning and units of 160.0 and the +0x2c float.
