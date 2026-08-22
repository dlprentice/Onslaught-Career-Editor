# CBattleEngine__VFunc_85_00405f20

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__VFunc_85_00405f20` at `0x00405f20`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00405f20`

## Identity
- Body `[0x00405f20,0x00405f3b]`, 28 bytes. Raw pristine-body SHA-256 `335c8b87b75179ced576d66d0211844735dcb5bf48744ee2bdee1d1ace16512b`; closure range SHA-256 `26f58565f892666ae839da17cffd421e57ef8d79fdefdfc4cde02ebc604561e3`; packet range-plus-bytes SHA-256 `de0834311e4c985ffd259fe642b1225efb44715b99d45ff9bab0fb22b94c7f40`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__VFunc_85_00405f20` — Ghidra tracked/table name, USER_DEFINED label, COUNTED NAME not a recovered source symbol. Packet decompile comment: RTTI-derived vtable slot 85 of CBattleEngine's primary sub-object; asserts membership/slot only.
- Campaign grade: C1_CANDIDATE_PARTIAL (DARK), closure class SEALED_STATIC_RECEIPT (packet campaignGrade confidence MEDIUM_STATIC).

## Calling convention
`__thiscall` per packet: `this` in ECX, one stack argument.

## Prototype and parameter semantics
```c
undefined __thiscall CBattleEngine__VFunc_85_00405f20(void * this, undefined4 param_1)
```
- `param_1` — stored verbatim into `*(this+0x160)`:
```c
*(undefined4 *)((int)this + 0x160) = param_1;
*(undefined4 *)((int)this + 0xfc) = *(undefined4 *)(*(int *)((int)this + 0x4b0) + 0x20);
```
- Second store copies a dword from `[this+0x4b0] + 0x20` into `this+0xfc`. The pointer at +0x4b0 is dereferenced without a null check; its target type and the semantic role of both destinations are unknown.

## Return value meaning
not_applicable — decompile models no meaningful return.

## Globals read/written
not_applicable

## Callees relied on / callers
Callees: none. Callers: none recorded in packet; entry is an RTTI vtable-slot target (virtual dispatch).

## Behavior summary
Two stores: latch the argument at +0x160, then refresh +0xfc from an object reached through the tracked pointer at +0x4b0 (offset +0x20). No branches.

## Error / edge behavior
Dereferences `*(this+0x4b0)` unguarded; behavior when that pointer is NULL is not_determinable from static evidence (no in-function check).

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). values.tsv has no rows for 0x00405f20; brief sessions/ttd_values empty.

## Evidence
- Digest reconciliation: closure `bodyDigest` `26f58565f892666ae839da17cffd421e57ef8d79fdefdfc4cde02ebc604561e3` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `de0834311e4c985ffd259fe642b1225efb44715b99d45ff9bab0fb22b94c7f40` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `335c8b87b75179ced576d66d0211844735dcb5bf48744ee2bdee1d1ace16512b` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00405f20.json`
  (bea.re.triage-packet.v1, image 74154bfa…).
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
  (C1_CANDIDATE_PARTIAL, confidence DARK).
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv`
  sessions: none.

## Confidence
2 — both stores fully visible and mechanically unambiguous; field meanings are partial (unknown), which bounds interpretation rather than the mechanics. No promotion is proposed without citable TTD-session corroboration.

## Unresolved questions
- Semantic role of +0x160, +0xfc, and the object at +0x4b0; whether +0x4b0 can be NULL at any call site.
