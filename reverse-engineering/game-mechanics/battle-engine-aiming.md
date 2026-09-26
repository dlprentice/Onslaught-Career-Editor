# Battle Engine auto-aim, launch position and Gun emitters

Status: active static contract for the rebuild's player shots
Last updated: 2026-09-26 (exact Gun emitter table; no-report launch orientation)
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
  emitter to that point, so it carries no roll.
- With no report (class 0) it is the full orientation matrix `+0x3c` times the
  auto-aim matrix `FMatrix(+0x4e8, +0x4f4, 0)` (`0x0040d0b7-0x0040d0c7`, product
  `0x0040d320`, orientation on the left).
  - `+0x3c` is rebuilt every Move by `UpdateRotation` (`0x00407a50`, called at
    `0x004095d1`) as `FMatrix(yaw + cos(R)·yawShake, pitch + cos(R)·pitchShake,
    roll + cos(R)·rollShake)` (`0x00408000-0x0040806a`), so it includes the jet's
    roll and the shake term (`BattleEngine.cpp:1222-1224`).
  - Element [i][j] sums the three terms O[i][k]·A[k][j] on the x87 in this k
    order, then stores a float: [0][0] (1 + 0) + 2; [1][1], [1][2] and [2][1]
    (0 + 2) + 1; every other element (2 + 1) + 0.
- A third branch (`0x0040cad7-0x0040cef7`) serves ballistic rounds
  (`CRoundGravity` nonzero, not beam or torpedo, `0x0040d0f0`):
  `FMatrix(yaw +0x114 + +0x4e8, solved or −π/4 pitch, 0)`. No Aquila round sets
  gravity, so the Aquila never takes it.
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
- **Model-space positions.** The emitter's pose is its part's cached pose,
  indexed by the record's part index (`0x004b4e86-0x004b4ecc`); the record adds
  no offset. Composed from HPOS/HORI at virtual frame 0 (fly) and 25 (walk) and
  rounded to single precision (x right, y forward, z up):

  | Gun | Part | Fly (frame 0) | Walk (frame 25) |
  | ---: | --- | --- | --- |
  | 1 | Emit01 | (9.170048e-05, 0.0842639282, −0.25803259) | same |
  | 2 | Emit02 | (−0.0883527175, 0.0539725572, −0.210329518) | same |
  | 3 | Emit03 | (−0.0564851314, 0.0684210137, −0.227710307) | same |
  | 4 | Emit04 | (0.000359148398, 0.0829063728, −0.247448772) | same |
  | 5 | Emit05 | (0.0454145856, 0.0701522902, −0.228438199) | same |
  | 6 | Emit06 | (0.0874229595, 0.0560657121, −0.211728841) | same |
  | 9 | Emit09 | (−0.234618425, 0.0414116606, 0.00570841506) | (−0.23461841, 0.274871588, 0.00570840016) |
  | 10 | Emit10 | (−0.235591888, 0.0416897312, 0.0558486059) | (−0.235591874, 0.275149643, 0.055848591) |
  | 11 | Emit11 | (0.224845171, 0.0414696708, 0.00569987856) | (0.224845186, 0.274929583, 0.00569986831) |
  | 12 | Emit12 | (0.223871738, 0.0416897163, 0.0558485687) | (0.223871753, 0.275149643, 0.0558485575) |
  | 13 | Emit13 | (−0.0824229494, −0.0204110984, 0.185880587) | same |
  | 14 | Emit14 | (0.0788260475, −0.0204110984, 0.185880199) | same |

  Guns 1-6 hang from `hood`, Guns 9-10 from `Object03`, Guns 11-12 from
  `Object01`, Guns 13-14 from the root. Only Guns 9-12 move between the poses.
  Every emitter's forward axis stays within about 10° of the body's (y ≥ 0.984),
  so the 0.9 dot test passes unless the cockpit tilt is large. The values were
  composed in double precision by `rebuild/tools/cmsh_static_preview.py`; the
  runtime pose cache (`0x004b4cd0`) composes on the x87 and may differ in the
  last bits.

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
