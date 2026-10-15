# CUnitAI__scalar_deleting_dtor

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__scalar_deleting_dtor` at `0x00415060`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00415060`

## Identity
- Body `[0x00415060,0x0041507f]`, 32 bytes. Raw pristine-body SHA-256 `5e00bf48aec09f63236bef67b4ff29a344d2f1e9cfd3f83a277c8b9e3dd333b4`; closure range SHA-256 `9ebca3ebe6201635f1463cd94fa037db8a4b33228e83e43b99511fa115df24c3`; packet range-plus-bytes SHA-256 `84bb8f523e78c61eafc54746b82df86c04c36fa57857aafc72677451df5966cd`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__scalar_deleting_dtor` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `COVERED`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `HIGH_STATIC`.

## Calling convention
Packet records `__thiscall` for `void * __thiscall CUnitAI__scalar_deleting_dtor(void * this, int flags)`: the receiver is modeled as `this`; explicit parameters follow the analyzed signature. Parameter labels are counted intent only.

## Prototype and parameter semantics
```c
void * __thiscall CUnitAI__scalar_deleting_dtor(void * this, int flags)
```
- `this` — pointer passed to both packet-listed direct callees and returned unchanged.
- `flags` — integer whose low bit controls the second direct call.

## Return value meaning
Returns the input `this` pointer after the calls shown by the decompile; ownership/lifetime meaning is unknown.

## Globals read/written
- `DAT_009c3df0` — its address is passed as the first argument to the conditional second direct callee.

## Callees relied on / callers
- Callees (packet structured array): `CUnitAI__dtor_body` `0x00415080` ×1 (STATIC_DIRECT); `CDXMemoryManager__Free` `0x00549220` ×1 (STATIC_DIRECT).
- Callers (packet structured array): none recorded.
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
Calls the packet-listed body helper with `this`; when `(flags & 1) != 0`, calls the packet-listed free helper with `(&DAT_009c3df0, this)`; then returns `this`. Destructor and allocator wording is counted name/comment intent only.

## Error / edge behavior
No null check protects `this`. The returned numeric pointer value is still emitted after the conditional free call; whether callers may use it is not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00415060`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `9ebca3ebe6201635f1463cd94fa037db8a4b33228e83e43b99511fa115df24c3` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `84bb8f523e78c61eafc54746b82df86c04c36fa57857aafc72677451df5966cd` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `5e00bf48aec09f63236bef67b4ff29a344d2f1e9cfd3f83a277c8b9e3dd333b4` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00415060.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `HIGH_STATIC`; cohort brief coverage `COVERED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
2 — the two-call flag gate and pointer return are explicit, while class and ownership semantics are not proven. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Exact class hierarchy and object ownership contract.
- Meaning of flag bits other than bit 0.
