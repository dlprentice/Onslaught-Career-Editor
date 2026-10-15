# Dropships: landing, unloading and leaving

Status: active static contract for the rebuild's U-17 and World 110 landing craft
Last updated: 2026-09-26 (descent below HAS 10 and climb below HAS 5 traced; event 2000 read)
Summary: the landing-state machine of a `CDropship`, what `Land()` starts, how the landing craft
unload their spawners, how a craft withdraws and is removed, what its turret does, and the AI
event schedule in each AI state. Flight is in [dropship flight](dropship-flight.md).
Evidence: MEASURED — instruction reads of the pristine specimen and `default physics.dat`,
re-derived by the RE lane from a read-only research pass. Items the research traced but the RE
lane has not re-derived are listed as such. No runtime capture of a dropship.
Specimen: pristine `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`; `data/default physics.dat`
SHA-256 `e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14`.

"HAS" is the height above the surface, `surface − z`, where the surface is the higher of the
ground and the water (`0x004485c8-0x004485ea`, `0x00448992-0x004489be`); z grows downward.

## Landing states

The state is `+0x27c`. `Init` starts an airborne craft in state 0 and a grounded one in state 6.

| State | Meaning | Entered by | Left when |
| --- | --- | --- | --- |
| 0 | flying | `Init` (airborne); the AI think in state 5 | `Land()` → 2; the AI's move to 1 (never, for these craft) |
| 1 | flying to an AI-chosen landing point | the AI think in state 0 (`0x0044864f`) | within 10.0 (2D) of a valid point → 2 |
| 2 | turning round | slot 118 (`0x00447a6c`) | Move: `|yaw − +0x2a0| < 0.1` → slot 119 → 3 |
| 3 | descending | slot 119 (`0x00447aca`) | AI think: can continue and touched ground in the last 0.15 s → 6; cannot continue → slot 120 → 5 |
| 6 | doors opening | `0x00448110`; `Init` (grounded) | Move → 4 when the doors reach the ground or finish opening |
| 4 | doors open, unloading | Move, from state 6 | AI think: spawners empty and none in use → 7 |
| 7 | doors closing | `0x00448120` (`+0x2a4` := 1 − `+0x2a4`) | Move: door progress ≥ 1 → slot 120 → 5 |
| 5 | taking off | slot 120 (`0x00447b3d`) | AI think: HAS > 35 → 0 (`0x0044873e-0x00448753`) |

- **`Land()`** is native `0x005361d0` → slot 93 (`0x00447f50`). It sets `+0x294` (landed by the
  script) and `+0x290` (landing point set) to 1, `+0x244` to 0, and the landing point
  `+0x280` to the current position, then calls slot 118.
- **Slot 118** (`0x00447a40`) skips the landing-point check when `+0x294` is set, sets state 2
  and `+0x2a0 = yaw − π`, wrapped into [−π, π].
- **Slot 119** (`0x00447ac0`) sets state 3, clears `+0x290`, adds the craft to the landing
  occupancy grid (`0x0050b010`) and plays `wingfolded`.
- **Slot 120** (`0x00447b10`) plays `wingunfolded`, sets state 5 and removes the craft from the
  grid (`0x0050b020`).
- **"Can continue"** (`0x004480c0`) is 1 when `+0x294` is set; otherwise it needs spawners not
  yet empty, an AI target (slot 81) and `0x004fb500(target, 1)`.
- **Touched ground** is slot 67 (`0x00401f70`): `now − +0xcc < 0.15` (`0x005d8588`), where `+0xcc`
  is stamped when the actor move clamps the craft to the ground.
- **Doors (state 6, `0x00447489-0x0044754c`).** Without a `dooropening` animation the craft goes
  to state 4 at once. Otherwise each tick it tests the mesh's type-27 point (slot 88): when
  that point is at or below the ground there minus 0.1, or the door progress `+0x2a4` has
  reached 1.0, the state becomes 4; otherwise the progress grows by the animation's
  per-tick step (0.00625 per the research pass, about 160 ticks) and is capped at 1.0.
- **State 1 is unreachable for these craft.** The state-0 think moves to 1 only when
  `0x004fb500(target, 1)` succeeds, and that needs a weapon (`+0x140`) or deploy spawner
  (`+0x144`); the landers have neither (research pass, `0x004fb519-0x004fb590`). They land only
  through `Land()`.

## What each state does to motion

The guide (`0x00448930`) sets thrust A and the Euler targets; see
[dropship flight](dropship-flight.md#steering).
- **State 2:** thrust 0, yaw target `+0x2a0`, roll toward the goal as in cruise, pitch 0.
- **State 3, HAS > 10:** thrust (0, 0, +0.005), which pushes down; pitch −0.15; yaw held; roll
  `(r mod 65536) × 2⁻¹⁸ − 0.5` from one shared draw at `0x00448d4c` every tick
  (`0x00448d18-0x00448da3`).
- **State 3, HAS ≤ 10: attitude** (`0x00448da8-0x00449031`, traced by the RE lane). The game
  thread runs the x87 at single precision ([walker dash](walker-dash.md#the-window)), so every
  operation below rounds to float32.
  - The yaw target is held at the current yaw ψ (`+0x114`, stored at `0x00448d33`).
  - The heading A is `(−sin ψ, cos ψ, 0)`: the second column of the rows
    `(cos ψ, −sin ψ, 0)`, `(sin ψ, cos ψ, 0)`, `(0, 0, 1)` built at `0x00448da8-0x00448ebb`.
  - N is the heightfield normal at the craft's position (`0x0047ec60` on `0x006fadc8`, at
    `0x00448ec0-0x00448ed1`; see
    [its note](../binary-analysis/functions/HeightField.cpp/CMonitor__SampleHeightfieldNormalAtXY.md)).
  - `B = A × N`, as `(A.y·N.z − A.z·N.y, A.z·N.x − N.z·A.x, N.y·A.x − A.y·N.x)`
    (`0x00448ed6-0x00448f1c`).
  - `C = B × N`, as `(B.y·N.z − B.z·N.y, B.z·N.x − N.z·B.x, N.y·B.x − B.y·N.x)`
    (`0x00448f21-0x00448f67`).
  - C is normalised with `|C|² = (C.x² + C.z²) + C.y²`, left as is when `|C|` is 0, and the
    pitch target is `−C.z` (`0x00448f6c-0x00448fc7`).
  - The roll target is `B.z × (1 / |B|)`, with `|B|² = (B.x² + B.z²) + B.y²`, or `B.z` when
    `|B|` is 0 (`0x00448fcb-0x00449031`).
- **State 3, HAS ≤ 10: thrust** (`0x00449035-0x00449144`).
  - The horizontal brake is `(v.x × −0.05, v.y × −0.05)` when HAS < 4.0; `v` is the unit's
    velocity from its slot 27 (`GetVelocity`, `0x00449060`). Otherwise the brake is 0.
  - With HAS ≤ 0.075 (`0x005db260`), the thrust is `(brake.x, brake.y, 0.002)`.
  - Otherwise, while `v.z > HAS × 0.022222223` (`0x005db264`, a second slot-27 read at
    `0x0044908b`), the thrust is `(brake.x, brake.y, HAS × −0.0005)`, upward.
  - Otherwise the thrust is `(0, 0, 0.005)`.
  - The tail (`0x0044947d-0x004494eb`) stores the targets (yaw, pitch, roll) at `+0x120` and
    the thrust at `+0x14c`. Every state-3 tick also clears the unit's `+0x174` (`0x00448d29`).
- **State 3 downwash, in Move:** it queries things within 25.0; trees within distance² 100 are
  knocked over (`0x004f69b0`), and a Battle Engine (thing flag `0x8`) within 7.0 and not more
  than 2.0 above the craft takes `0.9 / d` damage through its slot 40 (`0x0044765b-0x004477dd`).
- **State 4:** thrust 0. **States 6 and 7:** nothing is written, so the last thrust persists.
- **State 5:** thrust (0, 0, −0.001), upward, at every height; the unit's `+0x174` is cleared
  (`0x00449149-0x00449182`).
  - Above HAS 5, the pitch target is −0.1 and the roll is `(r mod 65536) × 0.1 × 2⁻¹⁶ − 0.2`,
    from one draw at `0x004491a1` every tick.
  - At or below HAS 5 (`0x004491d9-0x0044943e`), the attitude follows the state-3 law with
    two differences in rounding order. First, `|C|²` is summed `(C.z² + C.y²) + C.x²`
    (`0x0044939d-0x004493b7`). Second, B is normalised by `0x00406d50`, which sums
    `(x² + y²) + z²`, leaves a zero vector unchanged and otherwise multiplies each component
    by `1 / |B|`; the roll target is the normalised `B.z` (`0x00449426-0x00449436`). The
    remaining cross-product terms differ only in operand order, and IEEE multiplication is
    commutative.

## Unloading

For a craft landed by its script (both World 110 `Lander` scripts):
1. In state 4, each AI think with spawners not empty sets the unit's `+0x1f0` through slot 82
   (`0x00448704`, `0x00405e10`).
2. Every tick, the unit step calls `DoSpawn` (`0x004e3c60`) for each spawner in `+0x18c`,
   SpawnerA then SpawnerB, while the craft is not dying, its life is not negative and `+0x1f0`
   is set (`0x004facb1-0x004facfe`).
3. `DoSpawn` admits one squad cycle at a time, and each cycle emits its members one wave event
   apart, as in the [spawner squad-cycle contract](spawner-squad-cycle.md): a member every
   `Delay`, then `SquadDelay` before the next cycle, until `Amount` cycles have run.
4. The spawners' data (`default physics.dat`):

   | Spawner | Unit (class selector) | Amount | SquadSize | Delay | SquadDelay |
   | --- | --- | ---: | ---: | ---: | ---: |
   | Dropship Light Gun Tank Spawner (SpawnerA) | Light Gun Tank (2, `CGroundVehicle`) | 5 | 5 | 4.0 | 10.0 |
   | Dropship Grunt Spawner (SpawnerB) | Muspell Grunt (3, `CInfantryUnit`) | 2 | 10 | 0.5 | 10.0 |

   The spawner constructor clamps SquadSize to 1 only for class selectors 4-20 and 22-24
   (`0x004e39ab-0x004e39c4` → `0x0050f680`), so both sizes stand: a full unload is
   **25 tanks and 20 grunts**. The tank squads are `CNormalSquad` and the grunt squads
   `CRelaxedSquad`. The Empty craft has no spawners.
5. `SpawnersEmpty()` (native `0x00535a90` → `0x004fd7e0`) is true when every spawner has
   completed and none has a wave running, including when there are no spawners.

Traced by the research pass, not re-derived here:
- the squad forms at the SpawnerA or SpawnerB mount point plus 15 along its forward axis, and
  each member spawns at mount point 1 (the mesh has only `SpawnerA1` and `SpawnerB1`);
- a member's spawn can be blocked by other units near the point, which retries after `Delay`;
- each new member walks out along the craft's `WaypointA` points while the craft stays in
  state 4, using the spawner-exit routine documented in
  [CComplexThing.cpp.md](../binary-analysis/functions/CComplexThing.cpp.md) (arrival
  distance² 0.5625 for ground units); the mesh has no `WaypointB`, so grunts skip the walk.

## Leaving

- After unloading the craft goes 4 → 7 → 5 → 0. In state 0 under AI_ON, the think runs
  target selection (AI slot 4). With a target it sets the goal to the target (slot 61); with
  none it calls Retreat (slot 100, `0x00448660`).
- **Retreat** (`0x004fdd00`, also the `Retreat()` native `0x00535d30`) does nothing if `+0x244`
  is already 1 or 2. Otherwise it orders a move to the point `0x004fd910` returns and sets
  `+0x244` = 1. The research pass traced that point as the nearest same-side object in list
  `0x00855160` when one is nearer than the world origin, else the origin.
- **Run-out and removal.** The unit step checks the 2D distance to the goal: within 4.0
  (`0x005d85bc`) it sets `+0x244` = 2 and orders a move to its position plus 300
  (`0x005db520`) times its forward axis in x and y; while `+0x244` is 2 it posts event 2000 at
  −1 through slot 116
  (`0x004fb050-0x004fb12f`).
- **Event 2000 (SHUTDOWN)** reaches `CComplexThing::HandleEvent`. At `0x004f438c-0x004f439e`,
  when the game state (`0x008a9ac0`) is at most 3 and the thing has a mission script
  (`+0x74`), it calls the script's slot 2 (`0x00533810`), which runs the script's
  `shutdown()` ("Lander Escaped"; [IScript](../binary-analysis/functions/IScript.cpp.md)).
  This matches `thing.cpp:677-683`. The thing's own shutdown follows.
  - For a `CDropship` that shutdown is slot 2, `0x00447100`. It removes the craft from the
    landing grid (`0x0050b020` on `0x00855090`), then calls `0x00402d30`.
- **Reported by the rebuild lane** (their byte reads, not re-derived here):
  - The shutdown chain continues into `CUnit::Shutdown` (`0x004f95d0`).
  - The retreat walk visits the side's list newest first, because `0x004e5a80` prepends.
  - The SHUTDOWN is posted on the tick after the run-out starts and delivered on the tick
    after that.
  - In Level 100 the U-17 retreats to row 20, (501, 296).
- While `+0x244` is 1 or 2 the speed cap is 1.5 × `+0xb4` × 0.05.

## The U-17 in Level 100

Its script is `SetAIState(AI_OFF); FollowWaypointWait("Transporter Path"); Retreat();`.
Under AI_OFF every AI 3000 only polls (below), so the think never runs: the U-17 never lands
and its Trooper Spawner never fires. It flies the path (22 → 23 → 44, see
[waypoint paths](waypoint-paths.md#level-100-paths)), then retreats, runs out and is removed.

## The AI

`CDropshipAI` events go through the unit AI dispatcher (`0x004ff330`):
- **AI_ONF (4), any event:** the AI update (slot 3, `0x004487e0`, one draw at `0x0044880f`),
  then a poll: one draw at `0x004ff371` and event 3003 at `now + 2.0 + (r mod 65536) × 2⁻¹⁵`.
- **Retreating (`+0x244` 1 or 2):** every event polls.
- **3000:** under AI_ON and active (`+0x214`), the think (slot 9, `0x00448580`); otherwise a poll.
  The think ends with one draw (`0x00448763`) and requeues 3000 at
  `now + 1.0 + (r mod 65536) × 2⁻¹⁶`; it returns early, without requeueing, when the AI's
  mode `+0x20` is 0 or the craft is dying.
- **3001:** path following (slot 8) when active, otherwise a poll. **3002:** slot 10.
  **3003:** reposts 3000, 3001 or 3002 at −1 by the AI's mode (1, 0 or 2).
- The think's per-state arms: 0 → target or retreat; 1 → landing arrival or a move to the
  landing point; 2 → nothing; 3 → state 6 or take-off; 4 → the spawn request or state 7;
  5 → state 0 above HAS 35; 6 and 7 → nothing.
- `SetAIState` writes the unit's `+0x210` (`0x004fdcb0`); AI_OFF also clears the AI's target.
  It does not reach the turret.

## The turret

The "Dropship Gun Turret" (`CComponent`) is built after the parent and attached at the parent
mesh's Component point. Each tick its update (`0x00428110`) calls `CUnit::Move` and takes one
shared draw at `0x004284a1`. It carries a Hive Machine Gun, but its turn rate is written to
`+0xb8` rather than the turret turn rate `+0xbc`, so its fire control never starts and it never
fires ([World 110](world-110-construction-order.md#landing-craft-and-their-turrets)). The
research pass traced the parent's dying routine (slot 50, `0x00403690`) releasing its children,
so the turret dies with it.

## Draw sites

| Site | Where | When |
| --- | --- | --- |
| `0x0044880f` | AI update | each AI event under AI_ONF |
| `0x004ff371` | dispatcher poll | AI_ONF, AI_OFF, inactive or retreating events |
| `0x00448763` | AI think | each 3000 under AI_ON |
| `0x00448d4c` | guide, state 3 | each tick while HAS > 10 |
| `0x004491a1` | guide, state 5 | each tick while HAS > 5 |
| `0x004284a1` | turret update | each tick |
| `0x004f9924` | unit event 4003 | every 3.0 + (r mod 65536) × 2⁻¹⁶ s, for the craft, the turret and each spawned unit |

## Open questions

| Question | Cheapest falsifier |
| --- | --- |
| The unload counts (25 tanks, 20 grunts) and their timing | Count Light Gun Tanks and Muspell Grunts created after "Landing Started" in World 110, in a copied runtime |
| The spawn placement, clearance and exit-walk details listed as research-traced | Static trace of `0x004e3f90` and `0x004ffbb0`, or a runtime log of member positions |
| Whether the door-stop test uses the moving door or the rest pose | Log slot 88's type-27 output during state 6 in a copied runtime |
