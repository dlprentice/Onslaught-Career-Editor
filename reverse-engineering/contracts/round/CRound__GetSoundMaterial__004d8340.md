# CRound__GetSoundMaterial

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__GetSoundMaterial` at `0x004d8340`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004d8340`

## Identity
- Body `[0x004d8340,0x004d834c]`, 13 bytes. Raw pristine-body SHA-256 `3f59723d13c058fc8da764b0c39e4e3724e16109ceec8b0b8d9720d03aa46e2b`; closure range SHA-256 `c531255a11ea29849b7c5e0afb404fe519969bf2fb82fb5b0acf0dc6fbcb7591`; packet range-plus-bytes SHA-256 `c227327cf3ad4fa7401c1d45027b2722bea6d49b310ec15a4fcadc9c6b696f87`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name (canonical document identity): `CRound__GetSoundMaterial`. Packet/decompile metadata name: `CRound__VFunc_43_004d8340`. They disagree; both are counted analysis/source-intent labels, and neither is semantic proof. The packet metadata name does not replace the canonical tracked name.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=ANALYSIS`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `COVERED`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `undefined4 __fastcall CRound__VFunc_43_004d8340(int param_1)`. Register/stack details beyond that packet declaration are not_determinable; parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
undefined4 __fastcall CRound__VFunc_43_004d8340(int param_1)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `param_1` — unguarded base address used to follow +0xf0 and read a dword at the pointed-to block's +0x80.

## Return value meaning
Returns the unchanged dword at `*(param_1+0xf0)+0x80`.

## Globals read/written
- not_applicable — no absolute data symbol is read or written.

## Callees relied on / callers
- Callees (packet structured array): none recorded; visible indirect calls have no structured direct-callee VA.
- Callers (packet structured array): none recorded.
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
Performs one nested pointer load and returns one dword; no branch, call, or write is displayed.

## Error / edge behavior
Both pointer dereferences are unguarded. Material/category interpretation implied by the tracked name is not proven.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004d8340`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `c531255a11ea29849b7c5e0afb404fe519969bf2fb82fb5b0acf0dc6fbcb7591` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `c227327cf3ad4fa7401c1d45027b2722bea6d49b310ec15a4fcadc9c6b696f87` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `3f59723d13c058fc8da764b0c39e4e3724e16109ceec8b0b8d9720d03aa46e2b` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004d8340.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `COVERED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
2 — the dword load is fully visible; the field's type and descriptive meaning remain unknown. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Concrete type and value domain of the +0x80 field.
- How callers consume the returned dword.
