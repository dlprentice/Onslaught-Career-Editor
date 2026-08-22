# CBattleEngine__GetLastValidRangeStep100

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__GetLastValidRangeStep100` at `0x00409880`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00409880`

## Identity
- Body `[0x00409880,0x004098a2]`, 35 bytes. Raw pristine-body SHA-256 `c6134c86904ef66aba43f13793233a45c0295a4851ce106ae3518e5dea0da2c6`; closure range SHA-256 `af4fbf5322385ed8f1988c4d06238dbb61129e9fc95c0e4feaeb41a024457234`; packet range-plus-bytes SHA-256 `dbed940547d8127f83c13ca5be6e870391264b8074da9f582824b542c6baa6f5`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__GetLastValidRangeStep100` — Ghidra tracked/table name, USER_DEFINED label, COUNTED NAME not a recovered source symbol. Packet comment flags ownership naming debt (CMonitor__ unproven).
- Campaign grade: C1_CANDIDATE_PARTIAL (DARK), closure class SEALED_STATIC_RECEIPT (packet campaignGrade confidence MEDIUM_STATIC).

## Calling convention
`__fastcall`: single argument (`monitor`) in ECX.

## Prototype and parameter semantics
```c
int __fastcall CBattleEngine__GetLastValidRangeStep100(void * monitor)
```
- `monitor` — object holding a pointer at +0xa4; five ints are scanned starting at `[+0xa4] + 0xc`.

## Return value meaning
The step value (multiple of 100, range 0..400) of the LAST slot whose entry ≠ -1; 0 when every entry is -1:
```c
do {
  if (*piVar2 != -1) { iVar1 = iVar3; }
  iVar3 = iVar3 + 100;
  piVar2 = piVar2 + 1;
} while (iVar3 < 500);
return iVar1;
```

## Globals read/written
not_applicable

## Callees relied on / callers
Callees: none.
Callers (packet): `CBattleEngine__Move` 0x004081c0 ×1 site.

## Behavior summary
Fixed five-slot scan over `[*(monitor+0xa4)] + 0xc .. +0x1c`, stride 4 bytes, step counter 0→400 by 100; remembers the highest-index valid slot. Sentinel value -1 marks an empty slot. No writes, no branches beyond the loop.

## Error / edge behavior
No null check on `*(monitor+0xa4)` or the dereferenced base — NULL behavior not_determinable from this body. All-sentinel input yields 0 (indistinguishable from "slot 0 valid").

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). values.tsv has no rows for 0x00409880; brief sessions/ttd_values empty.

## Evidence
- Digest reconciliation: closure `bodyDigest` `af4fbf5322385ed8f1988c4d06238dbb61129e9fc95c0e4feaeb41a024457234` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `dbed940547d8127f83c13ca5be6e870391264b8074da9f582824b542c6baa6f5` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `c6134c86904ef66aba43f13793233a45c0295a4851ce106ae3518e5dea0da2c6` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00409880.json`
  (bea.re.triage-packet.v1, image 74154bfa…).
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
  (C1_CANDIDATE_PARTIAL, confidence DARK).
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv`
  sessions: none.

## Confidence
2 — whole loop visible; mechanics fully determined ("last non-sentinel of five slots"). The semantic meaning of the returned step stays open. No promotion is proposed without citable TTD-session corroboration.

## Unresolved questions
- What the five slots record (range buckets? waypoint steps?) and how CBattleEngine__Move consumes the result.
