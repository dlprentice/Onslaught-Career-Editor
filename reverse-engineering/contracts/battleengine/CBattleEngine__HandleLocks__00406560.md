# CBattleEngine__HandleLocks

Status: active static contract (factory draft)
Last updated: 2026-08-22
Summary: specimen-bound static function contract for `CBattleEngine__HandleLocks` at `0x00406560`; unknown semantics and runtime limits remain explicit.
Evidence: MEASURED — packet/decompile, closure range identity, and independently recomputed pristine body bytes; no TTD-session execution row in the bounded deep-mine corpus.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: references/Onslaught/BattleEngine.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00406560`

## Identity
- Body `[0x00406560,0x00406d12]`, 1971 bytes. Raw pristine-body SHA-256 `7ed9ecb5536b6841a856608668551ed3fcb0c6b945a976b7453fef8cb700b04e`; closure range SHA-256 `86ead03b7b2217b1ef907c0dea6f011ca6f47fe12d301d27d2f30ff6f1af33a3`; packet range-plus-bytes SHA-256 `3feddf31e715810f0a74ae798fdc29b7fa27d98bdef8fcbb56cfcb1b90299920`. All three use the same exact inclusive range; no padding or tail bytes are included.
- Name provenance: `CBattleEngine__HandleLocks` — Ghidra tracked/table name, USER_DEFINED label, COUNTED NAME not a recovered source symbol.
- Campaign grade: C1_CANDIDATE_PARTIAL (PARTIAL), closure class SEALED_STATIC_RECEIPT (packet campaignGrade confidence HIGH).

## Calling convention
`__fastcall`: `this` (battleEngine) in ECX, no explicit stack arguments (packet comment confirms).

## Prototype and parameter semantics
```c
void __fastcall CBattleEngine__HandleLocks(void * this)
```
No parameters beyond `this`.

## Return value meaning
not_applicable (void); several inner paths early-return.

## Globals read/written
- `DAT_009c3df0` — read; allocator/context argument to `CDXMemoryManager__Free`.
- `DAT_00672fd0` — read; global float compared against entry field +8 in the mode-2 branch. Its
  time-base interpretation comes from surrounding counted names and remains unproved here.

## Callees relied on / callers
- Callees (packet structured array; labels are counted names):
  - `Vec3__SetXYZ` `0x00401ec0` ×3 (STATIC_DIRECT).
  - `CSPtrSet__First` `0x00406d20` ×5 (STATIC_DIRECT).
  - `CSPtrSet__Next` `0x00406d30` ×4 (STATIC_DIRECT).
  - `Vec3__NormalizeInPlace` `0x00406d50` ×1 (STATIC_DIRECT).
  - `CBattleEngine__SelectNearestForwardTargetFromGlobalSet` `0x00406da0` ×3 (STATIC_DIRECT).
  - `CBattleEngine__StartLock` `0x00406fc0` ×4 (STATIC_DIRECT).
  - `CBattleEngine__CalcUnitOverCrossHair` `0x0040acc0` ×1 (STATIC_DIRECT).
  - `CBattleEngineJetPart__CanWeaponFire` `0x00412570` ×1 (STATIC_DIRECT).
  - `CBattleEngineJetPart__GetCurrentWeapon` `0x00412610` ×1 (STATIC_DIRECT).
  - `CBattleEngineWalkerPart__GetCurrentWeapon` `0x00414030` ×1 (STATIC_DIRECT).
  - `CBattleEngineWalkerPart__CanWeaponFire` `0x00414630` ×1 (STATIC_DIRECT).
  - `TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit` `0x00414b30` ×2 (STATIC_DIRECT).
  - `CGenericActiveReader__dtor` `0x0044b1d0` ×2 (STATIC_DIRECT).
  - `CSPtrSet__Remove` `0x004e5bd0` ×2 (STATIC_DIRECT).
  - `CUnit__IsCandidateSideCompatibleForTargeting` `0x004fd3d0` ×2 (STATIC_DIRECT).
  - `CWeapon__DoesTargetMaskMatchDistanceProfile` `0x005061f0` ×2 (STATIC_DIRECT).
  - `CWeapon__GetDistanceProfileField90` `0x00506350` ×2 (STATIC_DIRECT).
  - `CWeapon__GetDistanceProfileField94` `0x00506440` ×4 (STATIC_DIRECT).
  - `CWeapon__GetDistanceProfileFieldA8` `0x00506530` ×1 (STATIC_DIRECT).
  - `CWeapon__GetDistanceProfileField98` `0x00506620` ×3 (STATIC_DIRECT).
  - `CWeapon__GetDistanceProfileField9C` `0x00506710` ×4 (STATIC_DIRECT).
  - `CWeapon__GetDistanceProfileFieldA0` `0x00506800` ×1 (STATIC_DIRECT).
  - `TargetProfileContext__IsEligibleByDistanceBucketOrRange` `0x00509f70` ×1 (STATIC_DIRECT).
  - `CDXMemoryManager__Free` `0x00549220` ×2 (STATIC_DIRECT).
- Callers (packet structured array): `CBattleEngine__Move` `0x004081c0` ×1 site (via instruction flow).
- Two indirect virtual calls are visible outside the packet's structured direct-callee array: target vtable slot +0x16c on a locked unit, plus part-level dispatch through the GetCurrentWeapon/CanWeaponFire pairs.

## Behavior summary
Lock maintenance + acquisition for the current weapon:
1. Part select by `*(int*)(this+0x260) == 3` → jet (+0x57c) else walker (+0x578). Abort unless `TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit(part)` is false.
2. Get current weapon + CanWeaponFire for that part; abort if no weapon.
3. Prune pass over set at `+0x294`: remove entries with null reader; compute unit-to-this delta rotated by the matrix at `this+0x3c`, normalize it, and drop entries whose normalized Y-component fails `cos(CWeapon__GetDistanceProfileField98)` deflection test, when weapon can't fire, or whose unit has death bit (`+0x2c & 4`). Removed entries get `CGenericActiveReader__dtor` + free.
4. Count non-null entries; gate acquisition on `count < CWeapon__GetDistanceProfileField90(weapon)`, CanWeaponFire true, and `TargetProfileContext__IsEligibleByDistanceBucketOrRange(weapon)`.
5. Mode switch on `CWeapon__GetDistanceProfileFieldA8(weapon)`:
   - **Mode 0 (direct/crosshair):** candidate = cached `+0x4c8` or `CBattleEngine__CalcUnitOverCrossHair(this,NULL,0,0)`; skip if already locked; require side-compatibility (`CUnit__IsCandidateSideCompatibleForTargeting(this, cand[0x4e])`) and target-mask match; range check vs `Field9C` scaled by the candidate's vtable +0x16c call (percentage), forward-cone check vs `cos(Field98)`; then `StartLock(this,cand,Field94,1)`.
   - **Mode 1 (nearest-forward fill):** loop `CBattleEngine__SelectNearestForwardTargetFromGlobalSet(...)` around this position (+0x1c/+0x20/+0x24/+0x28) within `Field9C`; `StartLock(...,Field94,0)` repeatedly until lock count reaches `Field90` or selection returns null.
   - **Mode 2 (sequence):** if any existing entry's field at +8 (`piVar11[2]`, named "finish" only
     by the counted StartLock context) exceeds `DAT_00672fd0`, return. Otherwise chain from the first
     entry's reader unit via SelectNearestForwardTarget with `FieldA0`, StartLock direct=0; then
     optionally fall back to the cached `+0x4c8` unit (side/mask checks, range vs `Field9C`, cone vs
     `cos(Field98)`) and `StartLock(...,1)`.

Load-bearing fragment (prune-pass deflection test):
```c
dVar19 = CWeapon__GetDistanceProfileField98(this_00);
fVar18 = (float10)fcos((float10)dVar19);
if ((((float10)local_3c < fVar18) || (iVar10 == 0)) ||
   ((*(byte *)(iVar15 + 0x2c) & 4) != 0)) {
  CSPtrSet__Remove((undefined4 *)((int)this + 0x294),piVar11);
```

## Error / edge behavior
All walks are null-guarded; empty-set, no-weapon, timeout-active, count-at-limit, and failed eligibility each short-circuit to plain return. Alloc failure inside StartLock is that callee's concern. Behavior with corrupt set links: not_determinable.

## Runtime corroboration (TTD, bounded)
No TTD execution observed (bounded: deep-mine captures only). values.tsv has no rows for 0x00406560; brief sessions/ttd_values empty.

## Evidence
- Digest reconciliation: closure `bodyDigest` `86ead03b7b2217b1ef907c0dea6f011ca6f47fe12d301d27d2f30ff6f1af33a3` hashes canonical range text only (`tools/ExportFullFunctionInventory.java` lines 121-131); packet `bodyDigest` `3feddf31e715810f0a74ae798fdc29b7fa27d98bdef8fcbb56cfcb1b90299920` hashes that same range text followed by the exact body bytes (`tools/ExportTriagePacket.java` lines 235-261); raw SHA-256 `7ed9ecb5536b6841a856608668551ed3fcb0c6b945a976b7453fef8cb700b04e` hashes only the bytes extracted from the hash-verified pristine specimen.
- Packet `D:/packet-runs/wave1-contracts-20260822/packet-0x00406560.json`
  (bea.re.triage-packet.v1, image 74154bfa…).
- Closure row `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`
  (C1_CANDIDATE_PARTIAL, confidence PARTIAL).
- TTD deep-mine `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/values.tsv`
  sessions: none.
- Crosswalk row: BattleEngine.cpp `CBattleEngine::HandleLocks` line 586 — SOURCE_ANALOG
  (source architecture cite: a HandleLocks routine exists there; source (not proof) of retail behavior).

## Confidence
2 — control flow fully traced and all branches accounted statically, but distance-profile field meanings, mode semantics, and targeting effects rest on counted names; closure PARTIAL, no runtime corroboration.

## Unresolved questions
- Units/ranges of Field90/94/98/9C/A0/A8; meaning of the +0x16c virtual return (percent?); exact gameplay difference between modes 0/1/2; whether DAT_00672fd0 is seconds or frames.
