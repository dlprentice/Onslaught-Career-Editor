# CBattleEngine__GetFloatAt0x118_AsDouble

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__GetFloatAt0x118_AsDouble` at `0x004063a0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004063a0`

## Identity
- Body `[0x004063a0,0x004063a6]`, 7 bytes. Raw pristine-body SHA-256 `2658bac4f7aed0c3264cbaf1577efc2becb3aa109ad1533b5e6aab032cfc4e62`; closure range SHA-256 `0130f6f49fbec0e9abf86264af6c478bd4dc21bce9318dc3b60fe4a07953fbed`; packet range-plus-bytes SHA-256 `98f3ad202a95ce2521c3868941d7343c45be666a36adfd444d10bfbef7b82ef2`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__GetFloatAt0x118_AsDouble` — Ghidra tracked/table name, USER_DEFINED label, COUNTED NAME not a recovered source symbol.
- Campaign grade: C1_CANDIDATE_PARTIAL (COVERED), closure class SEALED_STATIC_RECEIPT (packet campaignGrade confidence HIGH).

## Calling convention
`__fastcall`: single argument (`this`) in ECX.

## Prototype and parameter semantics
```c
double __fastcall CBattleEngine__GetFloatAt0x118_AsDouble(void * this)
```
- `this` — object base; body reads the float at +0x118:
```c
return (double)*(float *)((int)this + 0x118);
```

## Return value meaning
The +0x118 float widened to double via FPU. Packet comment states field semantics remain unproven — unit/meaning unknown.

## Globals read/written
not_applicable

## Callees relied on / callers
Callees: none.
Callers (packet): `CMCBattleEngine__VFunc_11_00492f10` 0x00492f10 ×1 via instruction flow (counted name).

## Behavior summary
Single field read and FPU widen. No branches.

## Error / edge behavior
not_determinable — no guards; NULL `this` behavior outside evidence scope.

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). values.tsv has no rows for 0x004063a0; brief sessions/ttd_values empty.

## Evidence
- Digest reconciliation: closure `bodyDigest` `0130f6f49fbec0e9abf86264af6c478bd4dc21bce9318dc3b60fe4a07953fbed` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `98f3ad202a95ce2521c3868941d7343c45be666a36adfd444d10bfbef7b82ef2` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `2658bac4f7aed0c3264cbaf1577efc2becb3aa109ad1533b5e6aab032cfc4e62` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004063a0.json`
  (bea.re.triage-packet.v1, image 74154bfa…).
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
  (C1_CANDIDATE_PARTIAL, confidence COVERED).
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv`
  sessions: none.

## Confidence
2 — whole body visible; accessor mechanics fully determined, field meaning explicitly open per packet. No promotion is proposed without citable TTD-session corroboration.

## Unresolved questions
- What the +0x118 float stores (units, range) and why the caller widens it to double.
