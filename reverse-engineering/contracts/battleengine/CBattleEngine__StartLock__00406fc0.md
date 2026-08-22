# CBattleEngine__StartLock

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__StartLock` at `0x00406fc0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngine.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00406fc0`

## Identity
- Body `[0x00406fc0,0x0040705a]`, 155 bytes. Raw pristine-body SHA-256 `bed3568af6e5d031d1be9c4a0aa339ccd06bf3b5877094fc385757937780d21f`; closure range SHA-256 `b4f1db7c510031576e984fe98465c33517f6b135f7bcc43cb2ea552059ae630c`; packet range-plus-bytes SHA-256 `4af89a5d2492759afebe4f7f48f6155aa43815949fd85f614de37499b3945d80`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__StartLock` — Ghidra tracked/table name, USER_DEFINED label, COUNTED NAME not a recovered source symbol.
- Campaign grade: C1_CANDIDATE_PARTIAL (DARK), closure class SEALED_STATIC_RECEIPT (packet campaignGrade confidence HIGH).

## Calling convention
`__thiscall`: `this` in ECX, three 4-byte stack arguments (packet comment: RET 0xC proves three explicit args) — `inUnit` pointer, `inLockTime` float, `inDirectLock` int.

## Prototype and parameter semantics
```c
void __thiscall CBattleEngine__StartLock(void * this, void * inUnit, float inLockTime, int inDirectLock)
```
- `inUnit` — target unit; tested for death-flag bit (`*(byte*)(inUnit+0x2c) & 4`) and duplicate membership in the +0x294 set; stored into the new entry via `CGenericActiveReader__SetReader`.
- `inLockTime` — added to global time base `DAT_00672fd0` for the finish field (`puVar4[2] = fVar1 + inLockTime`); start field gets `DAT_00672fd0` directly (`puVar4[1]`). Units unknown (frames vs seconds not determinable from this body).
- `inDirectLock` — stored verbatim at entry offset +0x10 (`puVar4[4]`).

## Return value meaning
not_applicable (void).

## Globals read/written
- `DAT_009c3df0` — read; allocator/context argument to `CDXMemoryManager__Alloc`.
- `DAT_00672fd0` — read; time base for start/finish stores.
- `s_C__dev_ONSLAUGHT2_BattleEngine_c_006230bc` ("C:\dev\ONSLAUGHT2\BattleEngine.cpp") and line constant 0x332 (818) — read; debug-alloc tag arguments.

## Callees relied on / callers
Callees (packet): `CDXMemoryManager__Alloc` 0x005490e0 ×1, `CGenericActiveReader__SetReader` 0x00401000 ×1, `CSPtrSet__AddToTail` 0x004e5b20 ×1 — STATIC_DIRECT; counted names.
Callers (packet): `CBattleEngine__HandleLocks` 0x00406560 ×4 sites.

## Behavior summary
Appends a lock entry for `inUnit` unless gated:
1. Guard: `(*(byte*)(inUnit+0x2c) & 4) == 0` — dying units are refused (early return).
2. Duplicate scan: walks set at `+0x294` (iterator at `+0x29c`); if any entry's reader equals `inUnit`, return.
3. Allocate 0x14 bytes via debug-tagged `CDXMemoryManager__Alloc(&DAT_009c3df0,0x14,0x15,<file>,0x332)`; on success zero offsets +0x0 and +0xc.
```c
puVar3 = CDXMemoryManager__Alloc(&DAT_009c3df0,0x14,0x15,s_C__dev_ONSLAUGHT2_BattleEngine_c_006230bc,0x332);
```
4. `CGenericActiveReader__SetReader(entry, inUnit)`; `entry[1] = DAT_00672fd0` (start), `entry[4] = inDirectLock`, `entry[2] = DAT_00672fd0 + inLockTime` (finish).
5. `CSPtrSet__AddToTail((char*)this + 0x294, entry)`.

## Error / edge behavior
Dying-unit and duplicate guards return silently without allocating. If `CDXMemoryManager__Alloc` returns NULL, `SetReader` is still called with NULL and the subsequent `puVar4[...]` stores proceed on a NULL base — the decompile shows no post-alloc NULL guard on the store path; downstream effect not_determinable from this body alone.

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). values.tsv has no rows for 0x00406fc0; brief sessions/ttd_values empty. Packet comment separately records that Level-521 take-4 raw boundary rows observed zero calls in their bound window — explicitly not a dormancy claim; no session ids are available in lane inputs to cite further.

## Evidence
- Digest reconciliation: closure `bodyDigest` `b4f1db7c510031576e984fe98465c33517f6b135f7bcc43cb2ea552059ae630c` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `4af89a5d2492759afebe4f7f48f6155aa43815949fd85f614de37499b3945d80` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `bed3568af6e5d031d1be9c4a0aa339ccd06bf3b5877094fc385757937780d21f` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00406fc0.json`
  (bea.re.triage-packet.v1, image 74154bfa…).
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
  (C1_CANDIDATE_PARTIAL, confidence DARK).
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv`
  sessions: none.
- Crosswalk row: BattleEngine.cpp `CBattleEngine::StartLock` line 801 — SOURCE_ANALOG
  (packet comment claims retail/source body match for lines 801-825; source (not proof)).

## Confidence
2 — body fully visible and mechanically accounted (guards, alloc, field stores, append); CLockInfo field meanings beyond the matched start/finish/direct stores and the alloc-NULL store path stay open. No promotion is proposed without citable TTD-session corroboration.

## Unresolved questions
- Time units of `DAT_00672fd0`/`inLockTime`; full CLockInfo layout; whether Alloc-NULL can occur and what the stores then corrupt.
