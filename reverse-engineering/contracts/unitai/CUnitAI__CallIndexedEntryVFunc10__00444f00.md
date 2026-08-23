# CUnitAI__CallIndexedEntryVFunc10

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CUnitAI__CallIndexedEntryVFunc10` at `0x00444f00`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00444f00`

## Identity
- Body `[0x00444f00,0x00444f1a]`, 27 bytes. Raw pristine-body SHA-256 `243b46342bcd6f5be8758b893a0fdf04b367274bd7d93cf75cdf9bd504fe4d67`; closure range SHA-256 `6e5b196106a13bc6f4c702fe2d76ca4a494b7d8e2a1b1a141a36c1dddde5617b`; packet range-plus-bytes SHA-256 `c9c987fb15debe87d7a982a77e3d07e7d485d45e7e968d2821d912a81b624c44`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CUnitAI__CallIndexedEntryVFunc10` — packet `nameSource=USER_DEFINED`; counted label/source intent only, never retail semantic proof.
- Campaign grade: `C1_CANDIDATE_PARTIAL` (brief coverage `COVERED`), closure class `SEALED_STATIC_RECEIPT`, packet campaign confidence `MEDIUM_STATIC`.

## Calling convention
Packet records `__thiscall` for `int __thiscall CUnitAI__CallIndexedEntryVFunc10(void * this, int entryIndex)`: the receiver is modeled as `this`; explicit parameters follow the analyzed signature. Parameter labels are counted intent only.

## Prototype and parameter semantics
```c
int __thiscall CUnitAI__CallIndexedEntryVFunc10(void * this, int entryIndex)
```
- `this` — receiver/base pointer whose +4 field points to an indexed pointer table.
- `entryIndex` — signed integer multiplied by four to select an entry pointer; no bounds metadata is present.

## Return value meaning
Returns 0 when the selected pointer is null; otherwise returns the integer result of indirect slot +0x10 on that entry.

## Globals read/written
- not_applicable — no absolute data symbol is used by the displayed body.

## Callees relied on / callers
- Callees (packet structured array): none recorded; any visible indirect dispatch has no structured direct-callee VA.
- Callers (packet structured array): `CDestructableSegmentsMotionController__VFunc_CallUnitAIIndexedEntryVFunc10` `0x00494ff0` ×1 site(s).
- Names on these edges are counted analysis labels; behavioral claims rely on the displayed body/argument flow, not the labels alone.

## Behavior summary
Loads `*(int **)(*(int *)(this+4) + entryIndex*4)`. It returns 0 for a null entry; otherwise it invokes that entry's indirect slot +0x10 and returns the slot result. Indexed-entry wording is counted name/comment intent only.

## Error / edge behavior
No checks protect `this`, the +4 table pointer, or `entryIndex` bounds. The indirect slot contract and return meaning are not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution row in the bounded brief/deep-mine corpus. The cohort-3 brief was checked: `ttd_values` is empty and `sessions` is empty for `0x00444f00`. This bounded absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Digest reconciliation: closure `bodyDigest` `6e5b196106a13bc6f4c702fe2d76ca4a494b7d8e2a1b1a141a36c1dddde5617b` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `c9c987fb15debe87d7a982a77e3d07e7d485d45e7e968d2821d912a81b624c44` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `243b46342bcd6f5be8758b893a0fdf04b367274bd7d93cf75cdf9bd504fe4d67` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00444f00.json` (`bea.re.triage-packet.v1`, status `READY`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`).
- Campaign grade: `C1_CANDIDATE_PARTIAL` / `SEALED_STATIC_RECEIPT`; packet confidence `MEDIUM_STATIC`; cohort brief coverage `COVERED`.
- TTD brief check: `ttd_values` is empty and `sessions` is empty; no TTD execution row in the bounded brief/deep-mine corpus.
- Packet stringRefs: empty.
- Crosswalk: none in the cohort brief.

## Confidence
2 — the table load, null fallback, indirect call, and returned value are explicit; bounds and slot semantics are unknown. Confidence is capped at 2 because this cohort has no citable TTD execution row. Proposed promotion: false.

## Unresolved questions
- Valid range and ownership of the indexed table.
- Contract and result meaning of indirect slot +0x10.
