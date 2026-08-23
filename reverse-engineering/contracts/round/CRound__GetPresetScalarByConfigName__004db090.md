# CRound__GetPresetScalarByConfigName

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__GetPresetScalarByConfigName` at `0x004db090`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004db090`

## Identity
- Body `[0x004db090,0x004db127]`, 152 bytes. Raw pristine-body SHA-256 `2fd0d8a20b083b883a5d0917a07c24fc71b930febf0eb07385a7c2a47a0b6a72`; closure range SHA-256 `3913bbab5c046286351dc6f878087f5ec26bdb9942db5b25a9c5c4b746a86539`; packet range-plus-bytes SHA-256 `fba824b5a637d28479e865a0bd4f531ba9702ff32863c7efb60efa845289e901`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name and packet/decompile metadata name: `CRound__GetPresetScalarByConfigName`. The matching labels are counted intent only, not recovered source symbols and not semantic proof.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=USER_DEFINED`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `DARK`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__fastcall` for `double __fastcall CRound__GetPresetScalarByConfigName(void * this)`. Register/stack details beyond that packet declaration are not_determinable; parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
double __fastcall CRound__GetPresetScalarByConfigName(void * this)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `this` — unguarded base pointer used to obtain a nullable byte-string pointer through +0xf0/+8.

## Return value meaning
Returns 0.0 when the input string pointer is null or no equal entry is found; on byte-for-byte equality returns the matched entry's float at +0x38 widened to `double`.

## Globals read/written
- `DAT_008553f8` — read as an iterable root; its +8 cursor-like field is written while traversing entries.

## Callees relied on / callers
- Callees (packet structured array): none recorded; visible indirect calls have no structured direct-callee VA.
- Callers (packet structured array): `CInfantryUnit__VFunc40_HandleCollisionDamageReaction` `0x00489650` ×1 site(s).
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
When the byte-string pointer at `*(this+0xf0)+8` is nonnull, initializes a cursor from `DAT_008553f8`, compares the input and each entry's +0x30 byte string two bytes per loop until difference or NUL, returns the entry +0x38 float on equality, and otherwise advances through the cursor chain. It returns 0.0 on null input or exhaustion.

## Error / edge behavior
`this`, +0xf0, the global root, entry pointers, and both byte strings are largely unguarded. Traversal mutates global cursor state; string termination and concurrency invariants are unknown.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004db090`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `3913bbab5c046286351dc6f878087f5ec26bdb9942db5b25a9c5c4b746a86539` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `fba824b5a637d28479e865a0bd4f531ba9702ff32863c7efb60efa845289e901` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `2fd0d8a20b083b883a5d0917a07c24fc71b930febf0eb07385a7c2a47a0b6a72` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004db090.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `DARK`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
2 — byte comparison, traversal, match return, and zero fallback are explicit; preset/config naming and scalar meaning remain unproven. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Ownership/termination guarantees of both byte strings.
- Meaning and units of entry +0x38 and synchronization of the global cursor.
