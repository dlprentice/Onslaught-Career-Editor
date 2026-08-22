# CBattleEngine__VFunc_101_0040a560

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__VFunc_101_0040a560` at `0x0040a560`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040a560`

## Identity
- Body `[0x0040a560,0x0040a57f]`, 32 bytes. Raw pristine-body SHA-256 `30d9fb72b3e31be7aaea1ef89f535ba7d77b0bd8ea5cdf2452f3b6e96d8ef18c`; closure range SHA-256 `af0cc4f7f97549c3ae9bcde07518934b2ce9bf2158185a9dfb5d8ad9a8c2b5f6`; packet range-plus-bytes SHA-256 `075c0cb5b76e6182df341857ea98824efef6f0a9785e6c29557bb4bd300d5af5`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__VFunc_101_0040a560` — Ghidra tracked/table name, USER_DEFINED label, counted name, not a recovered source symbol.
- Campaign grade: C1_CANDIDATE_PARTIAL (DARK), closure class SEALED_STATIC_RECEIPT (packet confidence MEDIUM_STATIC).

## Calling convention
`__thiscall` per packet. `this` is in ECX and `param_1` is a pointer stack argument.

## Prototype and parameter semantics
```c
undefined __thiscall CBattleEngine__VFunc_101_0040a560(void * this, void * param_1)
```
- `this` — receiver whose pointer field at +0x574 is conditionally read.
- `param_1` — object whose signed 32-bit field at +0x138 is compared with 1 and which is forwarded unchanged to the callee. Exact type and field meaning are unknown.

## Return value meaning
not_applicable — the decompiled body returns without a value. The packet signature's `undefined` return type is analysis metadata, not evidence of a meaningful returned value.

## Globals read/written
not_applicable — the decompile references no named globals.

## Callees relied on / callers
Callee: `CInfluenceMap__AccumulateThingFlags` 0x004d30d0 ×1 (STATIC_DIRECT). Callers: none recorded in the packet.

## Behavior summary
The function calls `CInfluenceMap__AccumulateThingFlags(*(this + 0x574), param_1)` only when both conditions hold: `*(int *)(param_1 + 0x138) == 1` and `*(void **)(this + 0x574) != NULL`. Otherwise it returns immediately without a direct write shown in this body.

## Error / edge behavior
The null check protects the +0x574 pointer before the direct call. `param_1` itself is dereferenced without a null guard. The callee's failure behavior is not_determinable from this packet.

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). The lane brief has no sessions or `ttd_values` rows for 0x0040a560.

## Evidence
- Digest reconciliation: closure `bodyDigest` `af0cc4f7f97549c3ae9bcde07518934b2ce9bf2158185a9dfb5d8ad9a8c2b5f6` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `075c0cb5b76e6182df341857ea98824efef6f0a9785e6c29557bb4bd300d5af5` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `30d9fb72b3e31be7aaea1ef89f535ba7d77b0bd8ea5cdf2452f3b6e96d8ef18c` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040a560.json` (bea.re.triage-packet.v1, image 74154bfa…). Its `bodyDigest` hashes canonical range text plus raw body bytes, per `tools/ExportTriagePacket.java` lines 235-261.
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv` (C1_CANDIDATE_PARTIAL, confidence DARK). Its `bodyDigest` hashes canonical range text only, per `tools/ExportFullFunctionInventory.java` lines 121-131.
- Raw-body hash recomputed from `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` over the exact packet range; specimen SHA-256 74154bfa… verified before extraction.
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv` sessions: none.

## Confidence
2 — the two guards and sole call are fully visible, but parameter/field meanings and runtime execution are unresolved.

## Unresolved questions
- The semantic meaning of `param_1 + 0x138 == 1` and the concrete owner stored at `this + 0x574`.
- Which vtable slot uses this counted-name body and when the call is reached naturally.
