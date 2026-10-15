# CBattleEngine__ResetAndSetActiveReader

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__ResetAndSetActiveReader` at `0x0040c720`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040c720`

## Identity
- Body `[0x0040c720,0x0040c745]`, 38 bytes. Raw pristine-body SHA-256 `95e6415647a0a4cfc47fd06d329c70dab7ad09a5f1cebed0bde25a31b2d2e5ae`; closure range SHA-256 `a8bfa4fc9f04265f77c5d6e32381cfd04ed866df605b2811b6c960842a05daed`; packet range-plus-bytes SHA-256 `22293d9ba3b978d89d890fc6e2d18102e4962b1fa52ef14d98543eeaf1272aba`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__ResetAndSetActiveReader` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `OPEN_EXECUTED`), closure class `PREEXISTING_GEN19_C1_OR_C2`, packet campaign confidence `CANDIDATE_CONTRACT`.

## Calling convention
`__thiscall`: receiver in ECX; one explicit pointer argument is modeled on the stack. The signature is USER_DEFINED, not a recovered source declaration.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngine__ResetAndSetActiveReader(void * this, void * activeReaderTarget)
```
- `this` — receiver passed to the first and third callees; `this+0x264` is passed as the first argument to the reader setter.
- `activeReaderTarget` — forwarded unchanged to the reader setter and to the packet-listed `CActor__SetFieldD4ToNow_00402020`; exact type/ownership is unknown.

## Return value meaning
not_applicable (void).

## Globals read/written
not_applicable — no absolute global read/write is visible in this body.

## Callees relied on / callers
- Callees (packet structured array): `CGenericActiveReader__SetReader` `0x00401000` ×1 (STATIC_DIRECT); `CActor__SetFieldD4ToNow_00402020` `0x00402020` ×1 (STATIC_DIRECT); `CBattleEngine__SwapPrimarySecondaryPartReadersForState` `0x00406460` ×1 (STATIC_DIRECT).
- Callers (packet structured array): none recorded; virtual dispatch may not appear as a structured direct caller.
- Names on these edges are counted analysis labels; semantic claims above rely on the visible body and argument flow, not the labels alone.

## Behavior summary
Performs three direct calls in order: swaps the receiver's primary/secondary part readers, calls the reader setter on `this+0x264` with the explicit argument, then calls the packet-listed +0x00402020 helper with `(this, activeReaderTarget)`. The packet comment's different high-level wording is not substituted for the structured callee/decompile evidence.

## Error / edge behavior
No null validation is visible for either pointer. Failure/exception behavior of all three callees is outside this packet.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded deep-mine corpus. The cohort-2 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x0040c720`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `a8bfa4fc9f04265f77c5d6e32381cfd04ed866df605b2811b6c960842a05daed` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `22293d9ba3b978d89d890fc6e2d18102e4962b1fa52ef14d98543eeaf1272aba` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `95e6415647a0a4cfc47fd06d329c70dab7ad09a5f1cebed0bde25a31b2d2e5ae` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040c720.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `PREEXISTING_GEN19_C1_OR_C2`; packet confidence `CANDIDATE_CONTRACT`; cohort brief coverage `OPEN_EXECUTED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
2 — call order and forwarded arguments are explicit; target semantics and callee effects are only partially known. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Concrete type and ownership rules for `activeReaderTarget`.
- Exact state changed by each callee, especially the +0x00402020 helper.
- Callers/virtual slot context, since no structured caller is recorded.
