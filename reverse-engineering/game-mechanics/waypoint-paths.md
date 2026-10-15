# Named waypoint paths: loading, start node and following

Status: active static contract for the rebuild's Level 100 and World 110
Last updated: 2026-09-26 (height adjustments, nearest-node arithmetic, end-of-walk behaviour and the Level 100 lifted heights)
Summary: how the loader builds each named waypoint path, which node `FollowWaypointWait`
starts from, and how following advances and ends. It also gives the resulting routes
for the units that follow paths from their authored positions.
Evidence: MEASURED static reads of the pristine specimen and the interpreted RLWD path
tables. The routes are computed from authored positions before the waypoints' ground
lift; every start choice below wins by a wide margin. No runtime capture.
Specimen: pristine `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`; interpreted
`100_RLWD` JSON SHA-256 prefix `41f33fb6d14201b0` and `110_RLWD` prefix
`495511efc7a8d412`.

## Loading

`CWorld::LoadWorld` calls `CWaypointManager::LoadWaypoints` (`0x00505ae0`) with the
level pass's per-row thing array. It reads a uint16 path count, then each path
(`0x00505960`):
- For file version 33 or later (Level 100 and World 110 are version 50), a path has a
  byte-length name, an int32 node count, then one int16 row ordinal per node.
- Each ordinal is looked up in the thing array. A node is kept only when that thing's
  type has bit `0x1000` (`0x00505a1d-0x00505a35`). Only `CWaypoint` sets that bit
  (`0x004bfb60`: `0x1001`). Units and spawners in a path's table are dropped.
- Each kept node is prepended (`0x004e5a80`), so the retail list runs in reverse file
  order.
- Before version 33, an ordinal counted along the global waypoint list `0x00855120`
  instead (`0x00505a4c-0x00505aa4`).

A waypoint (`CWaypoint::InitAndLink`, `0x005057b0`):
- has collision mask −1;
- joins `0x00855120`;
- binds its row's target as its next node, `+0x3c` (`0x005057f9-0x00505803`).

Its height is adjusted three times, each with a strict compare. z grows downward, so a
smaller z is higher.
1. `CThing::Init` (`0x004f34ea-0x004f3534`): `CWaypoint` slot 44 returns 1, so the
   heightfield is sampled. This is `0x0047eb80` with `ECX` = `0x006fadc8` and `EDX`
   pointing at the position, the same sample `CStart::Init`'s clamp uses. When the
   sample is below z (`fcom`, C0), the waypoint is teleported (slot 20) to x, y and the
   sample.
2. `CThing::Init` (`0x004f353b-0x004f3559`): slot 49 returns 0 (it may not go under
   water). When the water level `0x006fbdfc` is below z, z becomes the water level.
   Only z is stored.
3. `InitAndLink` (`0x005057d4-0x005057f6`) samples again. When the sample is below z,
   it samples once more and stores that result into z.

The result is the highest of the authored z, the ground and the water level. Step 3
cannot change it, since step 1 already raised z to the ground. The heightfield sample
excludes water; water is the separate global.

In Level 100 the lift is not small. The rebuild's Core sampler (commit `4516b7a1` on the
rebuild branch) puts Flyby node 42, authored at z −15 inside the hillside, at the ground
height −18.10, and every node over the sea at the water level −8.84: Flyby 43, Transporter
44 and all four drone nodes. The start choices below still win by wide margins. These
heights are the rebuild's measurement; this page has not re-sampled them.

## Following

- **Start.** `FollowWaypointWait` (`0x00537e40`) finds the named path and takes its node
  nearest the unit (`0x00505c30`):
  - the unit's position `+0x1c`, `+0x20`, `+0x24` is compared with each waypoint's
    position after its height adjustments;
  - distance is squared 3D, computed on the x87 stack in this order: dx, dy, dz, then
    (dx² + dz²) + dy²;
  - the comparison is a strict `<` against a running minimum that starts at 9999999.0,
    walking the list in retail order, so a tie keeps the earlier list entry;
  - each new minimum is stored as a float32 (`fstp`), and the next sum is compared with
    that stored value (`fcom`).
  It sends the unit to that node (slot 61), then suspends the script with a 2000 at −1.
  An unknown path name logs an error and returns without suspending.
- **Each frame.** The script's 2000 runs `UpdateWaypointFollowing` (`0x00538470`).
  - The unit has arrived when its 2D distance to the node is below its radius:
    - 8.0 for `CDropship` (`0x0050ead0`);
    - 5.0 for `CPlane` (`0x0050e8e0`);
    - 2.0 for `CGroundVehicle` and the Unit default (`0x00405e60`).
    A non-unit uses 2.0, or 4.0 when its type has bit `0x20000000`.
  - On arrival the next node is the waypoint's own target (`+0x3c`, `0x005384dc`), not
    the next list entry. A waypoint that targets itself logs an error and ends the walk.
  - With no next node, the unit's slot 64 runs and the script resumes after
    `FollowWaypointWait`. Otherwise the unit is sent to the next node.
  - Slot 64 differs by class:
    - `CDropship` (`0x00459990`) does nothing; the craft keeps its last goal and its
      velocity.
    - `CPlane` (`0x00422750`) resets its guide (`+0x208`, slot 8, `0x0047e3d0`). The
      guide's goal becomes the plane's position, the guide's `+0x1c` is cleared, and the
      plane's `+0x14c` vector is zeroed. Its velocity is kept.
    - `CGroundVehicle` uses the Unit default (`0x004fcf00`). It zeroes `+0x14c` and the
      velocity `+0x7c`, copies `+0x114` into `+0x120`, and resets the guide the same way.
      The fourth word of each zeroed vector is copied from an uninitialized stack slot.
  - The 2000 is filed again at −1 each frame (`0x005385d3`).
- **What the list decides.** A path's list decides only where following starts. The
  route after that is the target chain, which may leave the named path or loop.

## World 110 paths

| Path | File ordinals | Retail list | Dropped |
| --- | --- | --- | --- |
| Lander Path 1 | 23, 22, 21, 15, 11, 10, 8, 24 | 24, 10, 11, 15, 21, 22, 23 | row 8, a landing craft |
| Fighter Path 1 | 25, 33, 32, 31, 30, 29, 28, 27, 26 | 26, 27, 28, 29, 30, 31, 32, 33 | row 25, a fighter |
| Transport Path 1 | 4, 3 | 3, 4 | — |
| Fighter Path 2 | 6, 7, 5 | 7, 6 | row 5, the spawner |

- **Target chains:** 3→4; 6→7; 10→11→15; 21→22→24; 26→29; 27→30→33; 28→31→32. The
  others end the chain.
- **Landing craft.** Both `Lander` scripts follow Lander Path 1 from the craft's
  authored position:
  - row 8 at (215, 422, −20) starts at row 10 (squared distance 725, against 7,782.5 for
    row 11) and flies 10 → 11 → 15;
  - row 20 at (170, 505, −25) starts at row 21 (706, against 12,942 for row 10) and flies
    21 → 22 → 24.
  Row 23 is on the list but neither craft reaches it.
- **Fighters.** Fighter Path 1 holds three separate chains. A fighter scripted to follow
  it (`MuspellFighter`, `MuspellFighter1`; no World 110 row carries either script)
  takes the chain of its nearest node.

## Level 100 paths

| Path | File ordinals | Retail list | Chain |
| --- | --- | --- | --- |
| Flyby Path | 43, 42, 41 | 41, 42, 43 | 41→42→43 |
| Transporter Path | 44, 22, 23 | 23, 22, 44 | 22→23→44 |
| Target Tank Path 1 | 18, 6, 7 | 7, 6, 18 | 6→7→18 |
| Target Tank Path 2 | 38, 37, 8, 10, 24 | 24, 10, 8, 37, 38 | 38→37→10→24→8→38, a loop |
| Target Truck Path 1 | 25, 26, 27, 28 | 28, 27, 26, 25 | 25→26→27→28 |
| Target Truck Path 2 | 32, 31, 30, 29 | 29, 30, 31, 32 | 29→30→31→32 |
| Target Truck Path 3 | 36, 35, 34, 33 | 33, 34, 35, 36 | 33→34→35→36 |
| Drone Path 1 | 1, 2, 3, 4 | 4, 3, 2, 1 | 1→2→3→4→1, a loop |

- **Air Trainer.** The Air Trainer (row 40, `Flyby`) at (265.5, 392.5, −15) starts at
  row 42 (10,430.8, against 21,186.1 for row 41) and flies 42 → 43. It never visits
  row 41.
- **U-17.** The U-17 (row 21, `Transporter`) at (218.5, 297.5, −15) starts at row 22
  (846.3, against 3,486.0 for row 23) and flies 22 → 23 → 44.
- **Spawned units.** Target tanks, trucks and drones follow from the point where they
  are spawned.

## Open questions

| Question | Cheapest falsifier |
| --- | --- |
| Whether each unit really starts at the node computed here, including the height adjustments | Log `0x00505c30`'s return and the unit position at each `FollowWaypointWait` in a copied runtime |
