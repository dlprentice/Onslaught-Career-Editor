# CBattleEngine__IsWalkerGroundedOrCollision

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__IsWalkerGroundedOrCollision` at `0x004080f0`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004080f0`

## Identity
- Body `[0x004080f0,0x0040811d]`, 46 bytes. Raw pristine-body SHA-256 `bf5f42c464845bdf82baa577478cd6ec96e4de51eb260e11f117834a5f3873af`; closure range SHA-256 `e6fb549b4ff20d55186c1f4ff9116ef9337adb919036f671f73af96690f55670`; packet range-plus-bytes SHA-256 `d0dde5e4630d83a8be9f224b52be264c850201b79e0e30f6fb440c739375c24e`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__IsWalkerGroundedOrCollision` — Ghidra tracked/table name, USER_DEFINED label, COUNTED NAME not a recovered source symbol. Packet comment flags ownership naming debt ("CGame__ ownership unproven"); rename applied in wave1188.
- Campaign grade: C1_CANDIDATE_PARTIAL (OPEN_EXECUTED), closure class PREEXISTING_GEN19_C1_OR_C2 (packet campaignGrade confidence CANDIDATE_CONTRACT).

## Calling convention
`__fastcall`: single argument (`battleEngine`) in ECX.

## Prototype and parameter semantics
```c
bool __fastcall CBattleEngine__IsWalkerGroundedOrCollision(void * battleEngine)
```
- `battleEngine` — object with mode word at +0x260 and vtable at *this.

## Return value meaning
Boolean predicate. FALSE when mode ≠ 2; otherwise TRUE when either (a) the vtable slot at +0x10c returns non-zero, or (b) `ElapsedTime__BelowThreshold_D4(this)` is true:
```c
if (*(int *)((int)battleEngine + 0x260) != 2) {
  return false;
}
iVar2 = (**(code **)(*(int *)battleEngine + 0x10c))();
if ((iVar2 == 0) &&
   (bVar1 = ElapsedTime__BelowThreshold_D4(battleEngine), CONCAT31(extraout_var,bVar1) == 0)) {
  return false;
}
return true;
```
The "grounded or collision" reading of the OR comes from the counted label; only the logic above is proven. What the +0x10c slot tests and the threshold compared inside ElapsedTime__BelowThreshold_D4 are outside this body.

## Globals read/written
not_applicable

## Callees relied on / callers
Callees (packet): `ElapsedTime__BelowThreshold_D4` 0x00401fd0 ×1 (STATIC_DIRECT; counted name); one indirect virtual call via vtable slot +0x10c — target unresolved statically.
Callers (packet): `CGame__Update` 0x0046e910 ×1, `CPlayer__ReceiveButtonAction` 0x004d3110 ×1 (via instruction flow).

## Behavior summary
Mode gate then two-way contact test as above; single boolean return, no state writes.

## Error / edge behavior
Mode ≠ 2 short-circuits to FALSE before any dereference of the vtable slot. Behavior for NULL this under mode 2: not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). values.tsv has no rows for 0x004080f0; brief sessions/ttd_values empty. Brief closure OPEN_EXECUTED is carried from the closure row without per-VA deep-mine rows to cite.

## Evidence
- Digest reconciliation: closure `bodyDigest` `e6fb549b4ff20d55186c1f4ff9116ef9337adb919036f671f73af96690f55670` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `d0dde5e4630d83a8be9f224b52be264c850201b79e0e30f6fb440c739375c24e` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `bf5f42c464845bdf82baa577478cd6ec96e4de51eb260e11f117834a5f3873af` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x004080f0.json`
  (bea.re.triage-packet.v1, image 74154bfa…).
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
  (C1_CANDIDATE_PARTIAL, confidence OPEN_EXECUTED).
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv`
  sessions: none.

## Confidence
2 — complete body visible; branch semantics fully determined. The physical meaning of the two contact tests stays open (counted-name dependent). No promotion is proposed without citable TTD-session corroboration.

## Unresolved questions
- Which vtable implementation serves slot +0x10c and what it detects; the elapsed-time threshold constant inside ElapsedTime__BelowThreshold_D4.
