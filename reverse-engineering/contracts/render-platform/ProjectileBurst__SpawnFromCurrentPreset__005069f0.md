# ProjectileBurst__SpawnFromCurrentPreset

Status: active static contract, instruction-level (replaces the 2026-08-23 factory draft)
Last updated: 2026-09-25
Summary: one burst event of a weapon: the Battle Engine spend gate, then per round of the volley the emitter, aim, launch angle, two inaccuracy draws, target, locks, round Init, effects, clip ejection and recoil, in retail order.
Evidence: MEASURED — objdump of the pristine body with every callee, slot and constant read at its address on 2026-09-25; field meanings from the physics value maps; no runtime replay of this body.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not in the pinned GPL drop (no `Weapon.cpp`); Battle Engine callees crosswalk to `references/Onslaught/BattleEngine.cpp:1094-1113` and `:2713-2737` | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x005069f0`

## Identity
- Body `[0x005069f0,0x005078ab]`, 3,772 bytes ending in `ret` (`c3`); raw pristine-body SHA-256 `124b166f80acecc01ae2bf18b876c7c1202015aea1ba2b8303414fde973f8e5d`, recomputed 2026-09-25.
- Callers: `CWeapon__HandleFireBurstEvent` (`0x005069b6`) and `ProjectileBurst__SpawnFromPercentBucketFallback` (`0x00506143`).
- The saved names of four Battle Engine callees describe them poorly: `CBattleEngine__CanSpawnBurstForResolvedEntry` is `WeaponFired`, `CBattleEngine__RandomizeBurstOffsetsAndAccumulateRange` is `RecoilWeapon`, `CBattleEngine__RandomizeOffsets4B8_4C0` is `AddShockShake` and `CBattleEngine__DisplayLock` tests whether the weapon is the current part's weapon. `CRT__AcosDispatch_ST0` is the CRT asin.

## Calling convention
`__thiscall` with the firing `CWeapon` in `ecx` (kept in `ebp`), no stack arguments, one `ret`. Returns in `eax`.

## Prototype and parameter semantics
```c
int __thiscall ProjectileBurst__SpawnFromCurrentPreset(CWeapon *weapon);
```
- `weapon+0x08` owner; `+0xa0` current mode, the charge-level mode record; `+0x70` launch-sequence counter; `+0x74` launch-angle counter; `+0x80` fixed-orientation flag; `+0x30` weapon orientation (12 dwords); `+0x2c` weapon target; `+0x84` a four-dword vector copied into the round's init payload.
- Mode fields use the weapon-mode map in `reverse-engineering/binary-analysis/physics-round-value-ids-2026-07-25.md`: `+0x00` `CWeaponClip`, `+0x18` round, `+0x34` `CWeaponInaccuracy`, `+0x40` `CWeaponPower`, `+0x48` `CWeaponVolleySize`, `+0xac` `CWeaponTrack`, `+0xb4` `CWeaponSoundPerBurst`, `+0xb8`/`+0xbc` muzzle light and radius.

## Return value meaning
1 when at least one round of the volley was created and initialised; 0 when the Battle Engine spend gate refuses, the weapon has no mode, the volley size is not positive, or every `CreateProjectile` returned null.

## Globals read/written
- `0x008a9d9c`: the gameplay generator for every `Random__NextLCGAbs` call here, and for the three draws of `AddShockShake`.
- `0x00896988` sound manager (`CSoundManager__PlayEffect` `0x004e1940`), `0x009c63e8` particle manager (`0x004cb3d0`), `0x0089c9a0` muzzle-light owner (`0x0044a610`), `0x00855040`-`0x0085504c` a four-float vector passed to the particle manager, `0x00672fd0` event time (through callees).

## Callees relied on / callers
- Gate and recoil: `0x0040c2e0` (`WeaponFired`: jet part `0x00412050`, then walker part `0x004140d0`; success clears `+0x5d8`, the source's `mStealth = 0`), `0x0040c340` (`RecoilWeapon`), which calls `0x00407940` (`AddShockShake`).
- Rounds: `CWorldPhysicsManager__CreateProjectile` `0x0050f7a0`, `CInitThing__ctor` `0x0048dcf0`, round slot 9 Init, `CRound__SetTargetReaderIfAllowed` `0x004daab0`.
- Aim: owner slot 75 (Battle Engine `CBattleEngine__GetLaunchPosition` `0x0040c990`; units `0x004fc3c0`), owner slot 27 (`0x00404120`, the velocity `+0x7c`), owner slot 81 (Battle Engine `0x004071b0` `GetCurrentTarget`; units `0x004175e0`, AI `+0x13c` target `+0xc` or null), `ProjectileBurstPreset__GetListEntryIdByIndex` `0x005078b0`, `CThing__GetCentrePos` `0x004f3ac0`, asin `0x0055dcb0`, `0x005099a0` (beam speed), Euler matrices `0x004062d0` and `0x004f8140`.
- Locks: `0x00407310` then `CBattleEngine__FireLock` `0x00407060`.
- Effects: `0x004cb3d0`, `0x004097a0`, `0x0044a610`, `OID__CreateObject` `0x004bf090` (clip), `0x0044a930`.

## Behavior summary
One call is one burst event. In order:

1. A Battle Engine owner (thing type bit `0x8`) must pass `WeaponFired` (`0x00506a1f`); a refusal returns 0 before any draw, round, lock or recoil.
2. No mode: return 0. A mode with a launch sample (`+0xc`) and `CWeaponSoundPerBurst` 0 plays it once (`0x00506a96`).
3. `CWeaponVolleySize` not positive: return. Otherwise, for each round of the volley (`0x00506aaa`-`0x0050788b`):
   1. `CreateProjectile(mode round)`; null skips to the next round with no draw.
   2. Launch-sequence counter +1, wrapping at the sequence count `+0x58`; its entry is the emitter index. Launch-angle counter +1, wrapping at `+0x68`.
   3. Owner slot 75 fills the launch position and orientation for that emitter.
   4. With weapon `+0x80`, the weapon orientation `+0x30` replaces it. It is first re-aimed at the weapon target's centre (yaw −atan2(dx, dy), pitch asin(dz/|d|)) when `CWeaponTrack` is set, a target exists and the round is gravity-free, beam or torpedo.
   5. The launch-angle entry gives an Euler matrix. Speed is `CRoundVelocity` × 0.05, or `0x005099a0` for a beam.
   6. Two draws, pitch then yaw (`0x00506e0a`, `0x00506e3e`): ((r mod 65536) × 2/65536 − 1) × `CWeaponInaccuracy`, taken whatever the inaccuracy.
   7. Start position = launch position + owner velocity (slot 27); orientation and velocity from steps 3-6; allegiance = owner `+0x138`; life = `CRoundLifeSpan`.
   8. Target = owner slot 81. The round's owner reader `+0xec` = owner.
   9. `CRoundFlak` round (`+0x4c`) with a target and speed × life > distance: one draw resets the life (`0x00507453`).
   10. Battle Engine owner: player `+0x574` → `+0x34` += 1, then `FireLock(target)` (`0x005074c9`) when `0x00407310` finds this weapon current.
   11. `SetTargetReaderIfAllowed(target, 0)`, then the round's Init with the payload.
   12. Muzzle effect per emitter slot, then the muzzle light when `+0xb8` is not −1.
   13. `CWeaponClip`: create object `0x15` and take three draws (`0x005076f6`-`0x00507710`).
   14. Battle Engine owner: `RecoilWeapon` (`0x00507871`).

`RecoilWeapon` calls `AddShockShake(CWeaponPower)` and adds 2 × power to `+0x604` (`BattleEngine.cpp:2732-2737`). `AddShockShake` (`BattleEngine.cpp:1094-1113`):
- returns when the amount is below the double 0.001 (`0x00407944`, constant `0x005d8bc8`);
- caps the amount at 0.75 (`0x005d8bc4`);
- takes three draws, each (r mod 32)/(16/amount) − amount, into yaw `+0x4b8`, pitch `+0x4bc` and roll `+0x4c0`, and zeroes `+0x4c4`;
- calls the cockpit object `+0x528` when present (`0x004247a0`, which draws from CRT `rand` `0x0055dbfe`, not the gameplay stream), then the rumble.

`CWeaponPower` defaults to 0 (`CWeaponModeStatement__Create`, `0x0042fb81`), so the Mech Vulcan Cannon and Mech Twin Vulcan Cannon take no shake draws. Mech Pulse Cannon Charged (0.03), Charged 2 (0.05) and both Micro Missile modes (0.01) take three per round.

`CBattleEngine::Damage` (`0x0040ab75`-`0x0040abc2`) computes the other shake:
- diff = (life before − life after) × 0.125, halved when shields `+0x100` are nonzero and capped at 0.25;
- `AddShockShake(diff)` takes three draws once diff ≥ 0.001, a life loss of at least 0.008 without shields;
- vibration then adds min(diff, 0.05) × 50;
- life, shields and energy are restored after the shake when `+0x15c` (`mVulnerable`) is 0.

## Error / edge behavior
- A null `CreateProjectile` result skips that round's draws, lock, Init and recoil, and the loop continues.
- The flak draw and the three clip draws occur only as stated. None of the Level 100 player, drone or turret weapons names a clip or fires a flak round.
- `WeaponFired`'s store spending is the parts' own (`0x00412050`, `0x004140d0`) and is outside this body.

## Runtime corroboration (TTD, bounded)
- The 2026-08-23 draft recorded coverage presence of this body in 7/10, 7/10, 8/10, 2/10, 5/10, 5/11, 2/7, 1/4 and 2/3 sessions of `contract-round-impact` batches 1-9 (level openings, Level 521 native runs and the Level 742 pilot); batch 10 had no coverage bitmap. Coverage proves execution only.
- No capture has replayed the per-round order, the draw count or the recoil in this contract.

## Evidence
- Pristine specimen objdump over the body and the callees named above, 2026-09-25.
- Constants read at their addresses: 0.05 `0x005d8584`, 2/65536 `0x005d8de4`, 1.0 `0x005d8568`, 0.001 (double) `0x005d8bc8`, 0.75 `0x005d8bc4`, 16.0 `0x005d8bc0`, 0.125 `0x005d8c4c`, 0.25 `0x005d858c`, 0.5 `0x005d85ec`, 50.0 `0x005d85d0`.
- Mode defaults: `CWeaponModeStatement__Create` `0x0042fa80` (burst and volley 1, power 0, yaw tolerance 0.5, maximum locks 5, lock range 40, lock radius 10, sound per burst 1, muzzle light −1).
- Weapon-mode field offsets: `reverse-engineering/binary-analysis/physics-round-value-ids-2026-07-25.md`.
- Level 100 use: `reverse-engineering/game-mechanics/level100-final-drone-wave.md`.

## Confidence
2 — every branch, draw site and callee named here was read from the pristine body; the exact matrix composition order in steps 4-7 and the payload field layout were not re-derived, and nothing here has been replayed.

## Unresolved questions
- The exact product order of the launch orientation (weapon or emitter orientation, launch angle and jitter) and the full init-payload layout. Cheapest falsifier: an original-code run of this body with a synthetic weapon, owner and round, comparing the payload against a model.
- The launch-position providers `0x0040c990` and `0x004fc3c0` and the parts' `WeaponFired` stores are separate contracts.
