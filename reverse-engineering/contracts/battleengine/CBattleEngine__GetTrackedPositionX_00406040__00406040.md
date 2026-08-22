# CBattleEngine__GetTrackedPositionX_00406040

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__GetTrackedPositionX_00406040` at `0x00406040`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (no crosswalk row in lane brief) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00406040`

## Identity
- Body `[0x00406040,0x00406049]`, 10 bytes. Raw pristine-body SHA-256 `5bf935eaef5a8805fe1b382c2d01b31a5414dd55479608177d7fa7c1ea79542a`; closure range SHA-256 `12e0a712e2ce852a7be9d8f148cf3fe9ffc24c714a13dd221a4ef6141f9b53f4`; packet range-plus-bytes SHA-256 `19b88279b1f94c0eae48458787bd3c4b8fdaf0d0250a265723e3104ccd1aab60`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__GetTrackedPositionX_00406040` — Ghidra tracked/table name, USER_DEFINED label, COUNTED NAME not a recovered source symbol. Packet comment flags name debt: sole ownership contested ("CDXCompass__" vs unit/BattleEngine-shaped span); rename applied in a prior wave.
- Campaign grade: C1_CANDIDATE_PARTIAL (OPEN_EXECUTED), closure class PREEXISTING_GEN19_C1_OR_C2 (packet campaignGrade confidence CANDIDATE_CONTRACT).

## Calling convention
`__fastcall` per packet: single argument (`context`) in ECX.

## Prototype and parameter semantics
```c
double __fastcall CBattleEngine__GetTrackedPositionX_00406040(void * context)
```
- `context` — object holding a tracked pointer at +0x4b0; body:
```c
return (double)*(float *)(*(int *)((int)context + 0x4b0) + 0x1c);
```
Dereferences `[context+0x4b0]` unguarded and reads the float at target+0x1c. Target type and coordinate-frame meaning are unknown.

## Return value meaning
The float at tracked-object+0x1c widened to double via FPU. Packet tags say `tracked-position` / `fpu-return`; which component (X per counted label) is a counted-name claim, not recovered semantics.

## Globals read/written
not_applicable

## Callees relied on / callers
Callees: none.
Callers (packet): `CDXCompass__Render` 0x00427210 ×2, `CDXCompass__UpdateDynamicOverlayTexture` 0x0053c510 ×1 — both via instruction flow; caller names are counted names.

## Behavior summary
Single indirection: read pointer at context+0x4b0, load float at +0x1c of that object, return as double. No branches.

## Error / edge behavior
Unguarded double dereference; NULL or stale +0x4b0 behavior is not_determinable from static evidence.

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). values.tsv has no rows for 0x00406040; brief sessions/ttd_values empty. Brief closure OPEN_EXECUTED is carried from the closure row without per-VA deep-mine rows to cite.

## Evidence
- Digest reconciliation: closure `bodyDigest` `12e0a712e2ce852a7be9d8f148cf3fe9ffc24c714a13dd221a4ef6141f9b53f4` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `19b88279b1f94c0eae48458787bd3c4b8fdaf0d0250a265723e3104ccd1aab60` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `5bf935eaef5a8805fe1b382c2d01b31a5414dd55479608177d7fa7c1ea79542a` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00406040.json`
  (bea.re.triage-packet.v1, image 74154bfa…).
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
  (C1_CANDIDATE_PARTIAL, confidence OPEN_EXECUTED).
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv`
  sessions: none.

## Confidence
2 — whole body visible and mechanically determined; ownership naming debt and coordinate semantics stay open. No promotion is proposed without citable TTD-session corroboration.

## Unresolved questions
- Owning class of the body (contested per packet), type/layout of the +0x4b0 target, and whether +0x1c is an X coordinate.
