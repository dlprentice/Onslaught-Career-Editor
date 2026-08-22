# CRound__SetThingType

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__SetThingType` at `0x004d8320`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004d8320`

## Identity
- Body `[0x004d8320,0x004d832e]`, 15 bytes. Raw pristine-body SHA-256 `6ecb411d5107118adc9e1069e90032b6493f6678cd462e47928f644174622d98`; closure range SHA-256 `a9b1c465149988cdd395f8f4fcbc676c58824f3cb9aee0b0bad0fc6b1c7696a9`; packet range-plus-bytes SHA-256 `f7875e94a35bfd0ea05d3c174e3bf2601cf198dacb73c8b8ad17f765575abc94`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name (canonical document identity): `CRound__SetThingType`. Packet/decompile metadata name: `CRound__VFunc_38_004d8320`. They disagree; both are counted analysis/source-intent labels, and neither is semantic proof. The packet metadata name does not replace the canonical tracked name.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=ANALYSIS`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `COVERED`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__thiscall` for `undefined __thiscall CRound__VFunc_38_004d8320(void * this, uint param_1)`: a receiver is modeled as `this`, with explicit stack parameters as shown. Parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
undefined __thiscall CRound__VFunc_38_004d8320(void * this, uint param_1)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `this` — unguarded writable base pointer.
- `param_1` — unsigned value ORed with `0x80000007` before storage.

## Return value meaning
not_applicable — the decompile models a void return.

## Globals read/written
- not_applicable — no absolute data symbol is read or written.

## Callees relied on / callers
- Callees (packet structured array): none recorded; visible indirect calls have no structured direct-callee VA.
- Callers (packet structured array): none recorded.
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
Stores `param_1 | 0x80000007` at receiver offset +0x34 and returns.

## Error / edge behavior
The receiver is unguarded. This operation forces bits 31, 2, 1, and 0 while preserving all other input bits; the field's semantic type is unknown.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004d8320`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `a9b1c465149988cdd395f8f4fcbc676c58824f3cb9aee0b0bad0fc6b1c7696a9` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `f7875e94a35bfd0ea05d3c174e3bf2601cf198dacb73c8b8ad17f765575abc94` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `6ecb411d5107118adc9e1069e90032b6493f6678cd462e47928f644174622d98` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004d8320.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `COVERED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
2 — the bitwise transform and destination are fully explicit; the tracked type-setting interpretation is not proof. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Meaning of receiver +0x34 and each forced bit.
- Whether callers rely on preserved input bits.
