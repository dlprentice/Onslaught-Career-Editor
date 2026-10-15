# Dropships: flight

Status: active static contract for the rebuild's U-17 and World 110 landing craft
Last updated: 2026-09-26
Summary: how a `CDropship` moves each tick while flying: the order of its Move, the guide's
steering targets and thrust, damping and the speed cap, turning, goal setting and what ends a
leg. Landing, unloading and the AI are in [dropship landing](dropship-landing.md).
Evidence: MEASURED — instruction reads of the pristine specimen and `default physics.dat`,
re-derived by the RE lane from a read-only research pass. No runtime capture of a dropship.
The arithmetic implications in "What the constants imply" are computed, not observed.
Specimen: pristine `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`; `data/default physics.dat`
SHA-256 `e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14`.

z grows downward, so a smaller z is higher. One MOVE runs per 0.05 s tick, and velocities are
in units per tick. "F" is the unit's forward axis, matrix column 1 (`+0x40`, `+0x50`, `+0x60`);
"R" is column 0 (`+0x3c`, `+0x4c`, `+0x5c`).

## Classes and set-up

- Behaviour 12 is `CDropship` (vtable `0x005e1dd8`), with `CDropshipGuide` (`0x005db228`) at
  unit `+0x208` and `CDropshipAI` (`0x005db1f4`) at `+0x13c`.
- `CDropship::Init` (`0x00446d70`) calls `CAirUnit::Init` (`0x00402ad0`), which sets all three
  turn rates (`+0x12c`, `+0x130`, `+0x134`) to the profile's `+0xb8`. It then sets the yaw rate
  to `+0xb8` and the pitch and roll rates to `+0xb8 × 0.25` (`0x00446dc2-0x00446e0c`).
- It then compares the ground height at the craft with its z (`0x00446e14-0x00446e21`):
  airborne gives state `+0x27c` = 0 and `SetAnimMode(wingflat)`; otherwise state 6 and
  `doorclosed`.
- The guide constructor (`0x0047e290`) sets guide mode `+0x1c` = 0 and the goal `+0x08` to the
  spawn position. In mode 0 the craft circles (below) until its first move order.

## Each tick

`CDropship::Move` (`0x00447120`, slot 66):
1. If `+0x168` is 1, it becomes 0 and `+0x1e8` becomes 1 (`0x00447131-0x00447143`).
2. A dying craft spins (`0x00447149-0x004471b5`); not flight.
3. The air-unit step `0x00402fa0` (`0x004471bd`), below. All motion happens here.
4. Thruster effects by state (`0x004471c2-0x0044745e`); presentation only.
5. The state arm (`0x00447461`):
   - state 0 sets `+0x2a4` = 0 (`0x004475cc`);
   - state 2 calls slot 119 (state 3) once `|yaw − +0x2a0| < 0.1` (a double, `0x005d8c38`),
     with the same ±π/2 wrap as the guide (`0x004475dc-0x00447650`);
   - states 1 and 4 re-point the velocity along F when `|v| ≥ +0xb4 × 0.03125`
     (`0x005db250`): v := |v| · F through slot 28 (`0x00447807-0x00447870`).

The air-unit step `0x00402fa0`, in order (all stores float32):
1. `v += A`, where A is the guide's output from the previous tick (`+0x14c`; `0x00402feb`).
2. `vz += slot 45`; for a live dropship slot 45 (`0x00448360`) is 0, so there is no gravity.
3. Damping. If the profile's Big flag `+0x124` is set and `z + 0.2 × radius > water`
   (`[0x006fbdfc]`, radius from slot 16), v × 0.95 (`0x005d8600`). Otherwise v × slot 73,
   which is 0.99 for a dropship (`0x0050eb60` → `0x005d8cc4`). All three profiles are Big.
4. Speed cap. `|v| = sqrt((vx² + vy²) + vz²)`, stored as float32. If it is positive and above
   `vmax = slot 111 × 0.05`, v × (vmax / |v|) (`0x004030d7-0x0040314d`). Slot 111
   (`0x004fe5c0`) is `+0xb4`, times 1.5 while `+0x244` is 1 or 2 (leaving).
5. The unit step `0x004fa8d0`:
   - the guide update (guide slot 3, `0x00448930`) when the guide exists and `+0x214` is
     nonzero or the craft is dying; otherwise the unit's slot 64, a bare `ret`
     (`0x004fa8dc-0x004fa902`). `+0x214` starts at 1;
   - `0x004fa800`, which only handles spawn phases `+0x168` = 1, 2 or 3;
   - `CActor::Move` (`0x004015e0`): position += v (`0x00401757-0x00401775`). While not dying,
     if the ground at the new position is at or below the craft's z (`z ≥ ground`), z becomes
     the ground and the velocity is zeroed through slot 68 (`0x004017a6-0x004017d4`,
     `0x0040189d`). If `z ≥ water`, slot 69 runs (water entry);
   - the Euler step (slot 77, `0x004fa4b0`) when slot 76 allows it and the target Euler
     `+0x120` differs from the current `+0x114` by exact compare (`0x004fa925-0x004fa97a`).

The rebuild's `RetailPlaneMotion` and `RetailUnitEuler` already follow this order and the slot-77
arithmetic for planes. A dropship differs in its guide, its slots 45 and 73, its Move wrapper
and state arm, and its turn rates.

## Steering

The guide update `0x00448930` works from the unit's position before this tick's move.
- **Prelude.** A dying craft gets `+0x174` = 0 and A = 0 (`0x004494f9`). Otherwise:
  - floor = the higher of the ground (`0x0047eb80` at the craft) and the water level;
    `h = floor − z` (`0x00448992-0x004489be`);
  - D = goal − position (3D);
  - `yawGoal = −atan2(Dx, Dy)` (`fpatan`, `0x004489ea-0x00448a2b`);
  - the pitch and roll targets and A start at 0;
  - the state switch (`0x00449540`): 0 and 1 → cruise, 2 → turn round, 3 → descend,
    4 → no thrust, 5 → climb, anything above 5 → no write.
- **Cruise (states 0 and 1, `0x00448a64-0x00448c3d`):**
  1. Yaw target by guide mode: mode 0 is the current yaw + π/2 (a continuous turn); mode 2
     is `yawGoal − π` (fly away); modes 1, 3 and others are `yawGoal`.
  2. Low altitude: if `h < MinAltitude` (profile `+0x15c`), the yaw target becomes the
     current yaw and the pitch target −π/5 (`0xbf20d97c`, nose up) (`0x00448a93-0x00448ab9`).
  3. The yaw target is wrapped into [−π, π].
  4. Δ = |current yaw − target|, where the target is shifted by 2π when the current yaw is
     below −π/2 and the target above π/2, or the reverse (`0x00448afb-0x00448b61`).
  5. `m = min(Δ, π/8)` (`0x005d9440`).
  6. Roll target: `+m` when `(Ry·Dy + Rz·Dz) + Rx·Dx < 0`, otherwise `−m` (`0x00448b78-0x00448bbd`).
  7. `+0x174` = 1.0 when `m > π/6`, else 0; since `m ≤ π/8` it is always 0.
  8. **Thrust A = 0.001 × F** (`0x005d8580`), each component a float32 product
     (`0x00448be4-0x00448c39`). It does not depend on the distance, the speed or the goal's z.
- **Turn round (state 2, `0x00448c42-0x00448d13`):** the yaw target is `+0x2a0`, which slot 118
  sets to the current yaw − π on entering state 2; the roll target follows steps 4-6; the pitch
  target is 0 and A = 0.
- **State 4:** A = 0 and no Euler targets (`0x00449440`). **States 6 and 7:** nothing is written,
  so the old A persists. States 3 and 5 are in [dropship landing](dropship-landing.md).
- **Tail (`0x0044947d`, skipped in states 4, 6 and 7):** `+0x120` = (yaw, pitch, roll) targets
  through `0x00449560`, and `+0x14c` = (Ax, Ay, Az, w), where w is an uninitialized stack word.

There is no desired velocity, braking or hover height: in cruise the craft thrusts along its
nose and turns toward the goal, and it holds whatever altitude it has unless it is below
MinAltitude.

## Turning

Slot 77 (`0x004fa4b0`) steps each Euler angle toward its target by
`min(0.1 × |E − E*|, rate)` (0.1 at `0x005d85c0`), yaw and roll the short way round and wrapped
to [−π, π], pitch unwrapped. It then rebuilds the matrix `+0x3c`. With the dropship's rates this
is at most `+0xb8` of yaw and `+0xb8 / 4` of pitch or roll per tick. The exact operation order
is recorded in [CComplexThing.cpp.md](../binary-analysis/functions/CComplexThing.cpp.md) and
implemented by the rebuild's `RetailUnitEuler`.

## Goals

- **Move orders.** Slot 61 is `0x00403a90`, shared with `CPlane`. It returns when there is no
  guide. It rounds the target's x and y to integers (`fistp`), samples the integer height grid
  `0x0047ea20` there, scales it by `[0x006fbdf4]`, takes the higher of that and the water, and
  clamps the target z so it is at least MinAltitude above that floor (`0x00403aa4-0x00403b19`).
  It then calls guide slot 4 with the target and the caller's flag (`0x00403b48`).
- **Guide slot 4** (`0x0047e2d0`) ignores the order when the flag is 0 and the AI's `+0x20` is
  2; otherwise it sets mode 1 and stores the goal. `SetAIState` writes the unit's `+0x210`, not
  the AI's `+0x20` (`0x004fdcb0`), and a placed unit's AI starts with `+0x20` = −1, so script
  path orders are accepted. Both `FollowWaypointWait` (`0x00537eb7`) and the waypoint follower
  (`0x0053858e`, `edi` = 0) pass flag 0.
- **Guide slots 5-8:** 5 sets mode 2 (fly away) with a goal, 6 sets mode 3 (steered like mode
  1), 7 sets mode 3 or 0, and 8 resets the guide to the unit's position. The dropship's slot 64
  is a bare `ret`, so nothing resets its guide at the end of a path.
- **Planes.** The `CPlane` vtable (`0x005e1930`, 118 slots) holds the same slot 61
  (`0x00403a90`), slot 100 (`0x004fdd00`, Retreat) and slot 116 (`0x004fe5f0`) as `CDropship`
  (`0x005e1dd8`). Its Move (slot 66, `0x004d1cd0`) calls `CAirUnit::Move` (`0x00402fa0`, at
  `0x004d1e8c`), which calls `CUnit::Move` (`0x004fa8d0`, at `0x00403159`). Its arrival radius
  is 5.0 (slot 94, `0x0050e8e0`: `fld [0x005d85d8]`).

## What ends a leg

The guide has no arrival logic. Legs end outside it:
- the waypoint follower's arrival radius, 8.0 for a dropship (slot 94, `0x0050ead0`), tested in
  2D ([waypoint paths](waypoint-paths.md#following)). At the end of a path the craft keeps its
  last goal and its velocity;
- the AI's landing arrival and the leave-mode run-out ([dropship landing](dropship-landing.md));
- ground contact, which sets z to the ground and zeroes the velocity.

## Profile fields

| Field | Offset | Use | U-17 Highside Transporter | Muspell Light Landing Craft | Muspell Light Landing Empty |
| --- | --- | --- | ---: | ---: | ---: |
| 2 `CUnitAirVelocity` | `+0xb4` | speed cap `× 0.05`; alignment threshold `× 0.03125` | 5.0 | 8.0 | 7.0 |
| 6 `CUnitAirTurnRate` | `+0xb8` | yaw rate; pitch and roll rate `× 0.25` | 0.0069813170 | 0.0174532924 | 0.0174532924 |
| 42 `CUnitMinAltitude` | `+0x15c` | nose-up threshold; move-order floor | 4.0 (default) | 4.0 (default) | 4.0 (default) |
| 56 `CUnitBig` | `+0x124` | water damping 0.95 | 1 | 1 | 1 |

Ids 1 and 2 share the `+0xb4` apply body and ids 5 and 6 the `+0xb8` body
([value ids](../binary-analysis/physics-round-value-ids-2026-07-25.md)). The MinAltitude default
4.0 is written at `0x0042f0e9`; none of the three profiles sets field 42. The U-17 is based on
"Base Air Unit", which sets only its behaviour.

## Draws

No shared-stream draw is reached on the per-tick path in states 0, 1 or 2: the direct-call
closure of `0x00447120`, `0x00402fa0`, `0x004fa8d0`, `0x00448930`, `0x004015e0` and `0x004fa4b0`
holds no census site except the guide's two landing draws (`0x00448d4c` in state 3,
`0x004491a1` in state 5), and the research pass checked every dropship slot the path reaches
virtually. The same closure reaches one event site, the spawner wave's (`0x004e43ab`), through
the unloading call in the unit step ([dropship landing](dropship-landing.md#unloading)). The
AI and the turret draw on their own schedules (same page).

## What the constants imply

Computed, not observed:
- Cruise speed tends to `0.99 × 0.001 / 0.01` = 0.099 units per tick (1.98 units/s), reaching
  95% after about 300 ticks. That is below every profile's speed cap (0.25, 0.40 and 0.35 per
  tick) and alignment threshold, so the cap and the alignment only matter if something else
  gives the craft more speed.
- The yaw rate is at most 8°/s for the U-17 and 20°/s for the Muspell craft.

## Open questions

| Question | Cheapest falsifier |
| --- | --- |
| The craft's real speed after spawn | Log `+0x7c` for 30 s after spawn for the Level 100 U-17 and a World 110 lander in a copied runtime |
| The spawn velocity and Euler (init `+0x50`, `+0x44`-`+0x4c`) | Read them at `0x00446d70` in a copied runtime |
| Whether collision response writes position or velocity (`0x004264a0`, base Hit `0x004f4480`) | Static trace of both bodies |
| The FPU control word, which sets the `fistp` rounding of move orders | Read it once in a copied runtime |
