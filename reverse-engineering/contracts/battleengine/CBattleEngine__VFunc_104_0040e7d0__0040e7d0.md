# CBattleEngine__VFunc_104_0040e7d0

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__VFunc_104_0040e7d0` at `0x0040e7d0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: unknown — no SOURCE_* crosswalk row in lane brief | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0040e7d0`

## Identity
- Body `[0x0040e7d0,0x0040e832]`, 99 bytes. Raw pristine-body SHA-256 `32cfd7dcf39df7cf0c9a0b0e4bb497b4b9a2cf4a4cd2c2147c6fa3f6acb9351f`; closure range SHA-256 `0f4d46360781eebd9bce4a6a8659e50046e04020b8b02d556d36fe379086195f`; packet range-plus-bytes SHA-256 `c8eab0755290966f1eb628cf4e9d19381ddc9c1db1d4255edf9df2273f9760b3`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: CBattleEngine__VFunc_104_0040e7d0 — Ghidra tracked/table name (USER_DEFINED label,
  counted name, not a recovered source symbol). Packet `name` field agrees with the tracked name.
- Campaign grade: C1_CANDIDATE_PARTIAL (PARTIAL), closure class SEALED_STATIC_RECEIPT
  (packet gradeBefore OPAQUE → gradeAfter C1_CANDIDATE_PARTIAL, confidence MEDIUM_STATIC).

## Calling convention
`__fastcall` per packet. Single `int param_1`; decompile treats it as `this`. No stack args, no ret-n evidence.

## Prototype and parameter semantics
```c
undefined4 __fastcall CBattleEngine__VFunc_104_0040e7d0(int param_1)
```
- `param_1` — ECX receiver; used with engine-object offsets (+0x260 mode int, +0x57c/+0x578 part
  pointers, +0x5d8 float). Exact struct layout unknown.
- Tracked slot number "104" is naming-table metadata, not decompile-derived vtable math.

## Return value meaning
Boolean-shaped int per the decompile: `0` on every guard hit, `1` when all guards pass.
What the caller does with it is not shown by this packet (no callers listed).

## Globals read/written
not_applicable — decompile references no DAT_/g_ symbols.

## Callees relied on / callers
- Callee: `CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove` @ `0x004135d0` (STATIC_DIRECT, 1 site),
  called with the pointer read from `param_1 + 0x578`.
- Callers: none recorded in the packet (likely reached via vtable; packet shows no referencing functions).

## Behavior summary
Four early-out conditions in three branch groups, then success:
```c
if (0.0 < *(float *)(param_1 + 0x5d8)) { return 0; }
if (*(int *)(param_1 + 0x260) == 3) {
    if (*(int *)(*(int *)(param_1 + 0x57c) + 0x2c) != 0) { return 0; }
    if (0.0 < *(float *)(*(int *)(param_1 + 0x57c) + 0x48)) { return 0; }
}
```
A third branch returns `0` when `+0x260 == 2` and the WalkerPart predicate at `+0x578` reports a
special walker move in progress; otherwise returns `1`. Semantics of the mode int at `+0x260`
(2 vs 3) and of the probed fields are unknown beyond these comparisons.

## Error / edge behavior
- Positive float at `+0x5d8` short-circuits everything to `0`.
- Mode `3` probes the part at `+0x57c`; mode `2` probes the part at `+0x578` — two different offsets;
  whether that asymmetry is intentional layout or decompiler artifact is not_determinable here.
- No null checks on the part pointers before dereference.

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). The VA has no row in
`ttd-deep-mine/values.tsv`.

## Evidence
- Digest reconciliation: closure `bodyDigest` `0f4d46360781eebd9bce4a6a8659e50046e04020b8b02d556d36fe379086195f` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `c8eab0755290966f1eb628cf4e9d19381ddc9c1db1d4255edf9df2273f9760b3` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `32cfd7dcf39df7cf0c9a0b0e4bb497b4b9a2cf4a4cd2c2147c6fa3f6acb9351f` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x0040e7d0.json`
  (bea.re.triage-packet.v1, image 74154bfa…).
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
  (C1_CANDIDATE_PARTIAL, confidence PARTIAL).
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv`
  sessions: none.

## Confidence
2 — control flow fully visible in a small decompile, but zero runtime observation and no caller
context, so rule-7 level 3 ("runtime corroborates execution") is not met.

## Unresolved questions
- Meaning of the mode int at `+0x260` and the identity of the parts at `+0x57c`/`+0x578`.
- Which vtable slot this occupies (tracked suffix "104" is counted-name metadata, not proof).
