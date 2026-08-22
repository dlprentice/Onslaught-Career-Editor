# CBattleEngine__VFunc_38_00405f00

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__VFunc_38_00405f00` at `0x00405f00`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00405f00`

## Identity
- Body `[0x00405f00,0x00405f11]`, 18 bytes. Raw pristine-body SHA-256 `5aba0bf9a9875527cf0958712e553783493b94288c160bd35cbbf59c8ff97190`; closure range SHA-256 `05a3666f94ec51531f98a9ce705d999c1c8e600eb9d6d40858d213943641dbc9`; packet range-plus-bytes SHA-256 `e528e39121ab3020de073b7a5283327ecd779e15b558d4db07f562464a6a28e5`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__VFunc_38_00405f00` — Ghidra tracked/table name, USER_DEFINED label, COUNTED NAME not a recovered source symbol. Packet decompile comment: name derived from the binary's own MSVC RTTI (vtable 0x005d89c4 slot 38 of the primary sub-object); asserts class membership and vtable slot only, no method name.
- Campaign grade: C1_CANDIDATE_PARTIAL (OPEN_EXECUTED), closure class PREEXISTING_GEN19_C1_OR_C2 (packet campaignGrade confidence CANDIDATE_CONTRACT).

## Calling convention
`__thiscall` per packet: `this` in ECX, one stack argument; callee cleans the stack (decompile shows no caller-side arg cleanup model beyond thiscall).

## Prototype and parameter semantics
```c
undefined __thiscall CBattleEngine__VFunc_38_00405f00(void * this, uint param_1)
```
- `this` — passed through unchanged as first argument to `CUnit__SetCollisionAndDamageFlags`.
- `param_1` — flag word OR-ed with constant mask before the call:
```c
CUnit__SetCollisionAndDamageFlags(this,param_1 | 0x220e08);
```
Bit meanings inside the mask are unknown (callee is itself a tracked counted name).

## Return value meaning
not_applicable — decompile models no meaningful return (`undefined`; body ends in plain `return`).

## Globals read/written
not_applicable

## Callees relied on / callers
Callees: `CUnit__SetCollisionAndDamageFlags` 0x004fcdc0 ×1 (STATIC_DIRECT; counted name). Callers: none recorded in packet; entry is an RTTI vtable-slot target (virtual dispatch — inbound calls are vtable-mediated and not listed).

## Behavior summary
Single-call wrapper: ORs the incoming flag word with 0x220e08 and forwards `(this, masked)` to the CUnit collision/damage-flag setter. No other state touched.

## Error / edge behavior
None visible — unconditional single call, no guards.

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). values.tsv has no rows for 0x00405f00; brief sessions/ttd_values empty. Brief closure OPEN_EXECUTED is carried from the closure row without per-VA deep-mine rows to cite.

## Evidence
- Digest reconciliation: closure `bodyDigest` `05a3666f94ec51531f98a9ce705d999c1c8e600eb9d6d40858d213943641dbc9` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `e528e39121ab3020de073b7a5283327ecd779e15b558d4db07f562464a6a28e5` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `5aba0bf9a9875527cf0958712e553783493b94288c160bd35cbbf59c8ff97190` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00405f00.json`
  (bea.re.triage-packet.v1, image 74154bfa…).
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
  (C1_CANDIDATE_PARTIAL, confidence OPEN_EXECUTED).
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv`
  sessions: none.

## Confidence
2 — complete body visible; the mask-and-forward mechanics are fully determined. Flag-bit semantics rest on a counted callee name and stay open. No promotion is proposed without citable TTD-session corroboration.

## Unresolved questions
- Meaning of individual bits in mask 0x220e08.
- Whether any caller invokes this slot other than via virtual dispatch.
