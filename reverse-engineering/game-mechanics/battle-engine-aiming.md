# Battle Engine auto-aim, launch position and Gun emitters

Status: active static contract for the rebuild's player shots
Last updated: 2026-09-26
Summary: how the Battle Engine picks an auto-aim target and blends its aim offsets,
where each player round starts (the cockpit mesh's Gun emitters) and in which
direction, and which state that depends on.
Evidence: MEASURED static reads of the pristine specimen; the shipped cockpit and
drone meshes through the repository CMSH parser; `default physics.dat` and the
Aquila configuration. A read-only research pass traced the functions. The RE lane
re-checked the cone constants, the offset blend, the absence of a fresh trace in
`GetLaunchPosition` and the cockpit mesh name at their addresses. No runtime capture.
Specimen: pristine `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
`m_cockpit2.msh.aya` SHA-256 prefix `008b9292`; `m_FA_F24_training.msh.aya` SHA-256
prefix `48876552`.

Retail `HandleAutoAim` (`0x0040b6d0`) and `UpdateAutoAim` (`0x0040b120`) follow
`BattleEngine.cpp:2446-2613` and `:2366-2443` in order and gates. The event cadence
and draws are in the
[final-wave contract](level100-final-drone-wave.md#crosshair-and-auto-aim-refresh).
Battle Engine fields (`BattleEngine.h:406-416`):
- `+0x4c8` crosshair unit, `+0x4d0` last crosshair line report, `+0x4e0` auto-aim
  target;
- aim offsets, desired / current / old: yaw `+0x4e4`/`+0x4e8`/`+0x4ec`, pitch
  `+0x4f0`/`+0x4f4`/`+0x4f8`;
- tracking `+0x4fc`-`+0x50c`; `+0x528` cockpit; `+0x574` player.

## Which weapons auto-aim

`IsSmart` is weapon-profile `+0x30` (`CWeaponSmart`, default 0), read at
`0x0040b80d`; with 0 the search is skipped. `CanPredict` is current-mode `+0xb0`
(`CWeaponPredictive`, default 0). Only the two Vulcans search:

| Weapon | Smart | Predictive | Round speed |
| --- | ---: | ---: | ---: |
| Mech Vulcan Cannon (jet) | 1 | 1 | 60.0 (Mech Air Bullet) |
| Mech Twin Vulcan Cannon (walker) | 1 | 1 | 60.0 (Mech Bullet) |
| Pulse Cannon Pod | 0 | 0 | — |
| Missile Pod | 0 | 0 | — |

## Candidate search

- **Walk.** MapWho around the Battle Engine's XY (`0x00491ea0`/`0x00492020`):
  - radius = the current mode's maximum range, 100.0 by default for all four
    modes, or 1000.0 when not positive;
  - levels 4 down to 0 (cells 8 to 128);
  - per level, cells from floor-int(c − r − cell/2) to floor-int(c + r + cell/2)
    (`fistp`), y outer and x inner;
  - each cell's list from its head, newest first; no distance filter in the walk.
- **Gates, in source order** (`0x0040b8b9-0x0040b94a`). Each is an inline field read.
  The Target Drone result is given in brackets.
  - side test `0x004fd3d0` [passes once its script sets it enemy];
  - not dying;
  - an air unit (type `0x400`) only with a predictive weapon [passes];
  - IsBig, profile `+0x124` (`CUnitBig`, default 0) [0];
  - active, unit `+0x214` [1];
  - nexus `+0x228` and weakpoint `+0x22c`, from mesh parts [0 and 0];
  - lockable, profile `+0x114` (`CUnitLockable`, default 1) [1].
- **Unit slots used.** 90 is the aim point; for a `CPlane` that is `CThing::GetCentrePos`,
  pos + (0, 0, BBOX-origin z) = pos + (0, 0, −0.02630952) for the drone. 91 is
  stealth (0.0 for units), 105 is on-scanner (1) and 27 is velocity (`+0x7c`).
- **Range.** Accepted when minRange² ≤ dist² ≤ tempMax². tempMax = (1 − stealth ×
  0.01) × maxRange, halved when off the scanner.
- **Cone.** Angles are measured against the body forward, orientation × (0, 1, 0),
  without the aim offsets. angleDiff = |yaw diff| + |pitch diff|, yaw
  −atan2(dx, dy) and pitch asin(dz/|d|), wrapped at ±π/2 by 2π.
  - The bound starts at 0.2, or 0.8 with a predictive weapon (`0x0040b879`/`0x0040b88d`).
  - It falls back to 0.2 when the target's |velocity|² is below 0.010000001.
  - A candidate must be strictly inside the bound, which then becomes its
    angleDiff. The smallest angle wins, and the first visited wins a tie.
- **Visibility.** The winner is kept only when
  `FindFirstThingToHitLine(Battle Engine → aim point, self, level 1, mesh flag 1,
  ignore rounds 0x4)` returns a thing hit, and the thing is that target
  (`0x0040bf1d`). Trees are not ignored here, unlike the crosshair trace.
- **Prediction and tracking** (`UpdateAutoAim`, every Move from `0x00409637`):
  - lead time t = |(target + target velocity) − origin| / |orientation × (0,
    speed, 0)| × 20.0;
  - tracking engages when |yaw| + |pitch| exceeds 0.2;
  - the offsets then move half way: old ← current, then current += (desired −
    current) × 0.5 for yaw and pitch (`0x0040b5f7-0x0040b646`).

Differences from the pinned source are float-level only: stealth × 0.01 instead
of / 100, the 6003 due-time addition order, and summation orders.

## Launch position and direction

`GetLaunchPosition` (`0x0040c990`, Battle Engine slot 75) starts from the Gun
emitter's world pose, then:
- It continues only when (orientation × (0, 1, 0)) · (emitter orientation × (0, 1, 0))
  > 0.9 (`0x005d8bb0`). Battle Engine weapons mount with index −1, so the first
  vector is the plain body orientation.
- It also needs `CWeaponAdjustAim` (weapon-profile `+0x28`), default 1
  (`0x0042f6a9`). None of the four weapons sets it.
- It reuses the last crosshair line report (class `+0x4d8`, distance `+0x4dc`) and
  never traces again. The only writer of that report is the 6002 event.
- The hit point is view + (end − view) × distance / |end − view|, where end =
  view + (view orientation × auto-aim matrix) × (0, 200, 0).
- The launch direction is `FMatrix(−atan2(dx, dy), asin(dz/|d|), 0)` from the
  emitter to that point. With no report (class 0) it is orientation × auto-aim
  matrix, where the auto-aim matrix is `FMatrix(+0x4e8, +0x4f4, 0)`.
- An emitter position of exactly (0, 0, 0) falls back to the Battle Engine's
  position and orientation.

The burst spawner then applies the launch angle and jitter
([burst contract](../contracts/render-platform/ProjectileBurst__SpawnFromCurrentPreset__005069f0.md)).

## Gun emitters

The emitters belong to the cockpit's render mesh: `+0x528` → slot 4 `0x004258f0` →
`[cockpit+0x8c]`, a CRTMesh (vtable `0x005deb1c`). For the Aquila Prototype that
is `cockpit2.msh` (configuration offset `0x3cd`), in both walker and jet modes.
Morphing only changes its animation: `flytowalk`/`walktofly`, then `walk`/`fly`.

- **Lookup.** `0x004dd160` → `0x004aa820` scans the mesh's emitter table (12
  records, stride `0x150`), matching the name case-insensitively and the selector
  exactly.
- **Selectors per weapon:** Pulse Cannon Pod 1; Missile Pod 4, 3, 5, 2, 6; Twin
  Vulcan 9-12; Mech Vulcan 13-14. There are no Gun 7 or 8 emitters.
- **Model-space pose:** each part's HPOS/HORI pose, lerped between the poses VHFM
  selects for floor(frame) and the next frame. Frame = start + count × t, with t
  lerped between cockpit `+0x128` and `+0x124` by the render fraction. The pose is
  composed from the root (R = R_parent·R_local, p = R_parent·p_local + p_parent).
  CPOS/CORI are not read on this path.
- **Animations (CAMD):** walktofly frames 26-50, flytowalk 1-25, walk 25, fly 0.
  A Battle Engine built in jet mode gets frame 0.
- **World pose:** p = M·p_model + P and R = M·R_model, where:
  - P = lerp(old pos `+0x8c` + cockpit `+0x1c`, pos `+0x1c` + cockpit `+0xc`
    (shake), render fraction) (cockpit slot 0 `0x00425430`);
  - M = orthonormalise(lerp(B_old·S_old, B·S, render fraction)), with B the
    orientation `+0x3c` and B_old `+0x9c` (cockpit slot 1 `0x004254f0`);
  - S is the cockpit tilt: identity at start, a walker bob `0x00424ca0`,
    otherwise decaying `0x004250f0`.
- **Measured model-space positions** (x right, y forward, z up):
  - Gun 1 (0.0001, 0.0843, −0.2580);
  - Guns 2-6 from (−0.0884, 0.0540, −0.2103) to (0.0874, 0.0561, −0.2117);
  - Gun 13 (−0.0824, −0.0204, 0.1859) and Gun 14 (0.0788, −0.0204, 0.1859);
  - Guns 9-12 at x ±0.23, z 0.006 or 0.056, y 0.041 in fly and 0.275 in walk.
    They hang from the animated parts Object03 and Object01; every other Gun
    emitter is static.

Launch positions therefore depend on the render fraction (`0x008a9e44`) and the
render counter (`0x008a9aac`), not only on simulation state.


## Open questions

| Question | Cheapest falsifier |
| --- | --- |
| How the render fraction and counter at launch time behave in a fixed-step replay | Log `0x008a9e44` and `0x008a9aac` at the launch call `0x00506bca` in a copied runtime |
| The walker tilt S inside `0x00424ca0` | Static read, or dump cockpit `+0x2c` during a walker capture |
| The second pose path `0x004b0fb0`, used without a pose cache or with render counter ≤ 1 | Static read of `0x004b0fb0` |
| Whether script-spawned drones have `+0x214` = 1 at their first auto-aim query | Read it at spawn in a copied runtime |
| Whether the CRTCutscene object (`0x005dea38`) traced by `cockpit-world-matrix-static-2026-07-26.md` is a second cockpit renderable beside this CRTMesh, or the same object misidentified | Read the cockpit's renderable fields after construction at `0x004244b0` |
