# CRound__scalar_deleting_dtor

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound conservative function contract for canonical tracked identity `CRound__scalar_deleting_dtor` at `0x004d8350`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in cohort-4 brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004d8350`

## Identity
- Body `[0x004d8350,0x004d836f]`, 32 bytes. Raw pristine-body SHA-256 `cc3c5c24e3a9c75514c53cf6edfa97bdb111d0d804931c77582c91573c359022`; closure range SHA-256 `92089d40811d25ad1a6f24c727e51d4400ae795ea413e16c4546581f8a633010`; packet range-plus-bytes SHA-256 `d49ce12e2317957ab984c74ae7dd320775339ef7a4088d6bada7968ccda141aa`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Closure tracked name and packet/decompile metadata name: `CRound__scalar_deleting_dtor`. The matching labels are counted intent only, not recovered source symbols and not semantic proof.
- Packet name provenance: `nameSource=USER_DEFINED` and `signatureSource=USER_DEFINED`; these are analysis metadata, not recovered retail source declarations.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `COVERED`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH_STATIC`.

## Calling convention
Packet records `__thiscall` for `void * __thiscall CRound__scalar_deleting_dtor(void * this, int flags)`: a receiver is modeled as `this`, with explicit stack parameters as shown. Parameter labels remain counted intent only.

## Prototype and parameter semantics
```c
void * __thiscall CRound__scalar_deleting_dtor(void * this, int flags)
```
- The signature is reproduced exactly from packet metadata; its function and parameter names are counted intent only, not semantic proof.
- `this` — pointer passed to both packet-listed direct callees and returned unchanged.
- `flags` — integer whose low bit controls the second direct call.

## Return value meaning
Returns the input `this` pointer after the unconditional first call and optional second call.

## Globals read/written
- `DAT_009c3df0` — its address is passed as the first argument to the conditional second direct callee.

## Callees relied on / callers
- Callees (packet structured array): `CRound__ShutdownAndDetachReaders` `0x004d8370` ×1 (STATIC_DIRECT); `CDXMemoryManager__Free` `0x00549220` ×1 (STATIC_DIRECT).
- Callers (packet structured array): none recorded.
- Edge names are counted analysis labels only; call-edge VAs/sites come from the packet arrays, and behavior claims rely on displayed control/data flow rather than labels.

## Behavior summary
Calls the first packet-listed callee with `this`; if `(flags & 1) != 0`, calls the second listed callee with `(&DAT_009c3df0, this)`; then returns `this`. Destructor/free wording is counted edge/name intent only.

## Error / edge behavior
`this` is not null-checked. A pointer is returned even after the optional second call; ownership and post-call usability are not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded cohort-4 brief/deep-mine corpus. For `0x004d8350`, `ttd_values` is empty and `sessions` is empty. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `92089d40811d25ad1a6f24c727e51d4400ae795ea413e16c4546581f8a633010` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `d49ce12e2317957ab984c74ae7dd320775339ef7a4088d6bada7968ccda141aa` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `cc3c5c24e3a9c75514c53cf6edfa97bdb111d0d804931c77582c91573c359022` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004d8350.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH_STATIC`; cohort brief coverage `COVERED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in this bounded cohort brief.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort-4 brief.

## Confidence
2 — the call order, low-bit gate, arguments, and pointer return are explicit; lifetime semantics remain unproven. Confidence is capped at 2 because this row has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Ownership/lifetime effect of each direct call.
- Meaning of flag bits other than bit 0.
