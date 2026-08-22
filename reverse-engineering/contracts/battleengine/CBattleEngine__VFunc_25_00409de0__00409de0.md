# CBattleEngine__VFunc_25_00409de0

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__VFunc_25_00409de0` at `0x00409de0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00409de0`

## Identity
- Body `[0x00409de0,0x00409e52]`, 115 bytes. Raw pristine-body SHA-256 `887ecdf87740b9424d66e12ef2a98b63122c349c009a8de9161fa8c6421589df`; closure range SHA-256 `dcd78c3ebbddb446b6ed9d3621ebc5ffa6012f42fa9d0d108b5717d828e10632`; packet range-plus-bytes SHA-256 `a7e371b24310a36b3be3668c055318c291b0d6621c797001ade513370cb16f01`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__VFunc_25_00409de0` — Ghidra tracked/table name, USER_DEFINED label, counted name, not a recovered source symbol.
- Campaign grade: C1_CANDIDATE_PARTIAL (OPEN_EXECUTED), closure class PREEXISTING_GEN19_C1_OR_C2 (packet confidence CANDIDATE_CONTRACT).

## Calling convention
`__thiscall` per packet. `this` is in ECX and `param_1` is a pointer stack argument.

## Prototype and parameter semantics
```c
undefined __thiscall CBattleEngine__VFunc_25_00409de0(void * this, float * param_1)
```
- `this` — receiver read at float offsets +0x1c/+0x20/+0x24, +0x8c/+0x90/+0x94, and +0x268/+0x26c/+0x270. Exact field names and units are unknown.
- `param_1` — writable output pointer. The body writes four consecutive float lanes; no length or null check is visible.

## Return value meaning
not_applicable — the decompiled body returns without a value. The packet signature's `undefined` return type is analysis metadata, not evidence of a meaningful returned value.

## Globals read/written
not_applicable — the decompile references no named globals.

## Callees relied on / callers
Callees: none. Callers: none recorded in the packet.

## Behavior summary
The body writes three component-wise differences to `param_1[0..2]`:
```c
param_1[0] = (this[+0x1c] - this[+0x8c]) - this[+0x268];
param_1[1] = (this[+0x20] - this[+0x90]) - this[+0x26c];
param_1[2] = (this[+0x24] - this[+0x94]) - this[+0x270];
```
It then writes the decompiler local `local_4` to `param_1[3]`. The packet decompile shows no assignment to `local_4`, so the fourth-lane value is indeterminate in this static rendering; no semantic value is inferred.

## Error / edge behavior
No null or output-length guard is visible before the four stores. Aliasing behavior and the concrete value written to lane 3 are not_determinable from the packet decompile.

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). The lane brief has no sessions or `ttd_values` rows for 0x00409de0.

## Evidence
- Digest reconciliation: closure `bodyDigest` `dcd78c3ebbddb446b6ed9d3621ebc5ffa6012f42fa9d0d108b5717d828e10632` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `a7e371b24310a36b3be3668c055318c291b0d6621c797001ade513370cb16f01` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `887ecdf87740b9424d66e12ef2a98b63122c349c009a8de9161fa8c6421589df` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00409de0.json` (bea.re.triage-packet.v1, image 74154bfa…). Its `bodyDigest` hashes canonical range text plus raw body bytes, per `tools/ExportTriagePacket.java` lines 235-261.
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv` (C1_CANDIDATE_PARTIAL, confidence OPEN_EXECUTED). Its `bodyDigest` hashes canonical range text only, per `tools/ExportFullFunctionInventory.java` lines 121-131.
- Raw-body hash recomputed from `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` over the exact packet range; specimen SHA-256 74154bfa… verified before extraction.
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv` sessions: none.

## Confidence
2 — all stores and input offsets are visible in the packet decompile, but field meanings, units, callers, runtime execution, and the fourth output lane remain unresolved.

## Unresolved questions
- The semantic identities and units of the three source-vector groups.
- Whether the fourth store reflects a real uninitialized lane, a decompiler stack-model artifact, or a typed four-component output whose final value comes from omitted calling context.
- Which vtable slot uses this counted-name body and what output shape its caller expects.
