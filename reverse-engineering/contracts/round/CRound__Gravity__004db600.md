# CRound__Gravity

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__Gravity` at `0x004db600`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004db600`

## Identity
- Body `[0x004db600,0x004db627]`, 40 bytes. Raw pristine-body SHA-256 `7f549e893dcde13ddd86f75f080144f76b173910a0d4dea4153b0007134bb967`; closure range SHA-256 `8bcc218c7db23e206e1f51b7dbb0edc6737d76ed4fa8afbdff7ce708b971b55d`; packet range-plus-bytes SHA-256 `15750d5333c5bd4505987c2fa0e200a662ea426999612ccba865969cd37b60b8`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name (canonical document identity): `CRound__Gravity`. Packet/decompile metadata name: `CRound__VFunc_45_004db600`. They disagree; both are counted analysis/source-intent labels, and neither is semantic proof. The packet metadata name does not replace the canonical tracked name.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=ANALYSIS`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `COVERED`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `float10 __fastcall CRound__VFunc_45_004db600(int param_1)`. Register/stack details beyond that packet declaration are not_determinable; parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
float10 __fastcall CRound__VFunc_45_004db600(int param_1)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `param_1` — unguarded base address used to follow +0xf0, inspect receiver +0x12c, and read pointed-to floats/dwords.

## Return value meaning
Returns 0.0 exactly when the dword at pointed-to +0x6c is nonzero and receiver +0x12c is nonzero; otherwise returns the pointed-to +0x3c float multiplied by 0.025.

## Globals read/written
- not_applicable — 0.025 is a literal; no absolute data symbol is read or written.

## Callees relied on / callers
- Callees (packet structured array): none recorded; visible indirect calls have no structured direct-callee VA.
- Callers (packet structured array): none recorded.
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
Evaluates a two-dword conjunction and selects either zero or one scaled nested float.

## Error / edge behavior
Both pointer levels are unguarded. Gravity wording and units are counted intent only; NaN/overflow follow ordinary floating-point behavior.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004db600`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `8bcc218c7db23e206e1f51b7dbb0edc6737d76ed4fa8afbdff7ce708b971b55d` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `15750d5333c5bd4505987c2fa0e200a662ea426999612ccba865969cd37b60b8` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `7f549e893dcde13ddd86f75f080144f76b173910a0d4dea4153b0007134bb967` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004db600.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `COVERED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
2 — the exact conjunction and numeric return expression are visible; units and descriptive interpretation remain unproven. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Meanings of pointed-to +0x6c, receiver +0x12c, and pointed-to +0x3c.
- Units represented by the 0.025 scale.
