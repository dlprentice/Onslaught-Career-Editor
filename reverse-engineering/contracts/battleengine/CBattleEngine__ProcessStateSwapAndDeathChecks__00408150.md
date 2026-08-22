# CBattleEngine__ProcessStateSwapAndDeathChecks

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__ProcessStateSwapAndDeathChecks` at `0x00408150`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00408150`

## Identity
- Body `[0x00408150,0x004081b0]`, 97 bytes. Raw pristine-body SHA-256 `6e7e57ae2e597dec7e1cd17ae60b1733beb0907623d349f276464965edb37883`; closure range SHA-256 `fe660ac93b4e9829c75f26432ea4e35430f65b1afc7029260d86c83840342ce4`; packet range-plus-bytes SHA-256 `2b5566debf192b042f2b6de621c1386f8d41f3494f9ae93795d306e1d705a47a`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__ProcessStateSwapAndDeathChecks` — Ghidra tracked/table name, USER_DEFINED label, COUNTED NAME not a recovered source symbol.
- Campaign grade: C1_CANDIDATE_PARTIAL (PARTIAL), closure class SEALED_STATIC_RECEIPT (packet campaignGrade confidence MEDIUM_STATIC).

## Calling convention
`__fastcall`: single argument (`unit`) in ECX.

## Prototype and parameter semantics
```c
void __fastcall CBattleEngine__ProcessStateSwapAndDeathChecks(void * unit)
```
- `unit` — object with death-flag byte at +0x2c, float at +0x24, gate int at +0x15c.

## Return value meaning
not_applicable (void).

## Globals read/written
- `DAT_006fbdfc` — read; float compared as `*(float*)(unit+0x24) - DAT_006fbdfc > -0.2f` (time-like base by shape).
- `DAT_00662dd0` — read; integer gate OR'd into the second condition (`+0x15c != 0 || DAT_00662dd0 == 0`).

## Callees relied on / callers
Callees (packet): `CBattleEngine__SwapPrimarySecondaryPartReadersForState` 0x00406460 ×1, `CGeneralVolume__SpawnPickupAndDispatch` 0x0040dfb0 ×1, `CActor__SetFieldD0ToNow_00402010` 0x00402010 ×2 — STATIC_DIRECT; counted names. Two indirect virtual calls on `*unit`: slot +0x38 (death path) and slot +200/0xc8 (alive path) — targets unresolved statically.
Callers: none recorded in packet.

## Behavior summary
```c
CBattleEngine__SwapPrimarySecondaryPartReadersForState(unit);
if ((*(byte *)((int)unit + 0x2c) & 4) != 0) {
  CGeneralVolume__SpawnPickupAndDispatch(unit);
  (**(code **)(*(int *)unit + 0x38))();
  CActor__SetFieldD0ToNow_00402010(unit);
  return;
}
if ((-0.2 < *(float *)((int)unit + 0x24) - DAT_006fbdfc) &&
   ((*(int *)((int)unit + 0x15c) != 0 || (DAT_00662dd0 == 0)))) {
  (**(code **)(*(int *)unit + 200))();
}
CActor__SetFieldD0ToNow_00402010(unit);
```
1. Always swaps primary/secondary part readers for state.
2. Death-bit path (+0x2c & 4): spawn pickup/dispatch, invoke vtable slot +0x38, stamp +0xd0 via SetFieldD0ToNow, return.
3. Alive path: if the +0x24 float is within 0.2 of (or above) global DAT_006fbdfc AND (+0x15c non-zero or global gate zero), invoke vtable slot +0xc8; then stamp +0xd0 unconditionally.
The death/pickup reading of branch 2 rests on counted callee names; only the call structure is proven.

## Error / edge behavior
Both virtual dispatches assume a valid vtable at `*unit`; no guards. Behavior with a NULL or stale
vtable is not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). values.tsv has no rows for 0x00408150; brief sessions/ttd_values empty.

## Evidence
- Digest reconciliation: closure `bodyDigest` `fe660ac93b4e9829c75f26432ea4e35430f65b1afc7029260d86c83840342ce4` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `2b5566debf192b042f2b6de621c1386f8d41f3494f9ae93795d306e1d705a47a` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `6e7e57ae2e597dec7e1cd17ae60b1733beb0907623d349f276464965edb37883` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00408150.json`
  (bea.re.triage-packet.v1, image 74154bfa…).
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
  (C1_CANDIDATE_PARTIAL, confidence PARTIAL).
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv`
  sessions: none.

## Confidence
2 — control flow fully visible; but both indirect dispatch targets are unresolved and the flag/gate semantics rest on counted names (PARTIAL closure).

## Unresolved questions
- Targets of vtable slots +0x38 and +0xc8; meaning of DAT_006fbdfc/DAT_00662dd0; whether the -0.2 comparison is a time window.
