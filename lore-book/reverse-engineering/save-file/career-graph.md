# Career Graph (Nodes + Links) and Safe Unlocking

This doc describes how the campaign graph is represented inside the fixed-size Steam `.bes` save and what to change to unlock missions **without** corrupting the career structure.

Primary sources:
- `references/Onslaught/Career.h` / `references/Onslaught/Career.cpp` (graph structure + `ReCalcLinks` rules)
- Retail `BEA.exe` mappings in `reverse-engineering/binary-analysis/functions/Career.cpp/*`
- Save layout: `reverse-engineering/save-file/struct-layouts.md` (true dword view)

---

## What “Complete” Means (Node vs Link)

There are two separate progress signals:

1. **Node completion** (`CCareerNode.mComplete`, `+0x04` in each 64-byte node)
   - Indicates a mission/world has been *completed* (win recorded).
   - Used by several unlock checks (e.g. `CCareer__IsEpisodeAvailable` checks completion for specific world numbers).

2. **Link completion** (`CCareerNodeLink.mLinkType`, `+0x00` in each 8-byte link)
   - Indicates an *edge* in the mission tree has become available/solid after a win.
   - This is how the game records “which branch got unlocked” (primary vs secondary path).

If you want to “unlock missions” without faking mission completion, you typically modify **links**, not nodes.

---

## Link Types (ECNLinkType)

From `references/Onslaught/Career.h`:

| Value | Name | Meaning |
|------:|------|---------|
| 0 | `CN_NOT_COMPLETE` | Locked / not yet unlocked |
| 1 | `CN_COMPLETE` | Unlocked (“solid” path) |
| 2 | `CN_COMPLETE_BROKEN` | Unused alternate parent path (“broken” line in UI) |

`CN_COMPLETE_BROKEN` is **not** save corruption. It’s expected bookkeeping from `CCareer::ReCalcLinks()`:
- When a link becomes `CN_COMPLETE`, the game looks at the destination node’s *other* parent links.
- Any other parent link already marked `CN_COMPLETE` is downgraded to `CN_COMPLETE_BROKEN` so only the “active” route stays solid.

Practical patching implication:
- If you are writing a save editor, you generally don’t need to write `CN_COMPLETE_BROKEN` at all.
- For “unlock everything” operations, prefer setting relevant links to `CN_COMPLETE` and leaving everything else untouched.

---

## Retail Unlock Gate (Steam `BEA.exe`)

In the Steam retail binary, mission availability on the career map is gated by:
- `Career_IsWorldUnlocked` @ `0x00461a50`

Observed behavior (decompile):
- If `IsCheatActive(..., 1)` (TURKEY) is enabled, it returns **true** for any world.
- World `100` (training) is always treated as **unlocked**.
- Otherwise it resolves the node by world number and checks **incoming** links:
  1. `node = CCareer__GetNodeFromWorld(&CAREER, world)` (`0x0041b8f0`)
  2. `parent_links = CCareerNode__GetParentLinks(node)` (`0x0041b9f0`)
  3. Returns **true** if any `CCareerNodeLink` in `parent_links` has `mLinkType == CN_COMPLETE (1)`.

Implications:
- `CN_COMPLETE_BROKEN (2)` does **not** satisfy this gate; a node with only broken parent links will be treated as locked.
- For editor unlock operations, setting at least one incoming link to `CN_COMPLETE` is sufficient for availability, without touching `CCareerNode.mComplete`.

Caller argument provenance (retail xrefs to `0x00461a50`):
- `0x004608ff`: pushes world value loaded from a world-table slot (`push eax` after `mov eax,[...+0xCC]`)
- `0x00460a7f`: pushes world value from loop table (`push eax` after `mov eax,[ebp]`)
- `0x00460fbf`: pushes dereferenced world pointer (`mov ecx,[eax] ; push ecx`)
- `0x004610d1`: pushes `edi` (world id in register)
- `0x0046110d`: pushes `edi` (world id in register)
- `0x0046138d`: pushes dereferenced world pointer (`mov edx,[ecx] ; push edx`)
- `0x004616b6`: uses earlier `push edx` (loaded from world-table slot) and calls with stack arg still live
- `0x00461889`: pushes world value from world-table slot (`push eax` after `mov eax,[...+0xCC]`)

So the gate is called with **world ids**, not node indices.

Retail post-load behavior note (inferred from decompile):
- `CCareer__Load(..., flag!=0)` calls `FUN_00460a40` (with `ECX=0x0089dab8`, likely a frontend map object) to scan the map table backward and pick the most recent world where `Career_IsWorldUnlocked(world)` is true.
- This means link-state edits can influence not only visibility but also which map world is auto-selected after a career load.

## Link-Type Write Sites (Retail `BEA.exe`)

The primary `mLinkType` mutation logic is concentrated in the `CCareer__Update -> CCareer__ReCalcLinks` chain:

1. `CCareer__Update` (`0x0041bd00`)
   - Called after mission-end update flow.
   - Marks the current node complete and then calls `CCareer__ReCalcLinks()`.

2. `CCareer__ReCalcLinks` (`0x0041bdf0`)
   - Iterates child links for the current world/node.
   - Promotes qualifying links to `CN_COMPLETE (1)` via `*link = 1`.
   - For the destination node, scans other parent links and downgrades any already-complete alternate parents to `CN_COMPLETE_BROKEN (2)` via `*other_parent = 2`.
   - Handles world-500 branch special cases using slot bits 61/62.

3. `CCareer__Blank` (`0x0041b7c0`)
   - Seeds initial node/link graph fields from compiled static career tables during reset/blanking.

Observed callsite behavior:
- Current xrefs show `CCareer__ReCalcLinks` is reached from `CCareer__Update` (call at `0x0041bdd4` in `CCareer__Update`).
- `CCareer__Load` does not show a direct call to `CCareer__ReCalcLinks`; loaded link types are consumed by unlock checks and map selection as-is until the next update/recalc pass.

---

## Where This Lives In The `.bes` File (Steam Build)

True dword view reminder: retail `BEA.exe` bulk-copies CCareer from/to `file + 2`.

- Nodes: `CCareerNode[100]` at file `0x0006` (64 bytes each)
- Links: `CCareerNodeLink[200]` at file `0x1906` (8 bytes each)

Offsets:
- Node `i` starts at: `0x0006 + i * 0x40`
- Link `j` starts at: `0x1906 + j * 0x08`

See `reverse-engineering/save-file/struct-layouts.md` for field-level offsets.

---

## Campaign Graph Structure (level_structure)

The canonical campaign structure is baked into `references/Onslaught/Career.cpp` as `level_structure[NUM_LEVELS][5]` with `num_nodes = 43`.

Columns:
- `world`: world number (mission id)
- `lower_idx`: index of the lower-tier child node (or `-1`)
- `higher_idx`: index of the higher-tier child node (or `-1`)
- `base_update_primary_world`: base-world state snapshot target when primary completes (or `-1`)
- `base_update_secondary_world`: base-world state snapshot target when secondary completes (or `-1`)

This is the “shape” of the graph. Save files store the derived node/link indices and targets; you should not modify the structural fields (`mLowerLink/mHigherLink/mToNode`) when unlocking.

| Node Idx | World | Lower Child (Idx/World) | Higher Child (Idx/World) | Base Update (Primary) | Base Update (Secondary) |
|---------:|------:|--------------------------|---------------------------|------------------------|--------------------------|
| 0 | 100 | 1 / 110 | - | 110 | - |
| 1 | 110 | 2 / 200 | - | - | - |
| 2 | 200 | 3 / 211 | 4 / 212 | 211 | 212 |
| 3 | 211 | 5 / 221 | 6 / 222 | 231 | 232 |
| 4 | 212 | 5 / 221 | 6 / 222 | 231 | 232 |
| 5 | 221 | 7 / 231 | 8 / 232 | - | - |
| 6 | 222 | 7 / 231 | 8 / 232 | - | - |
| 7 | 231 | 9 / 300 | - | - | - |
| 8 | 232 | 9 / 300 | - | - | - |
| 9 | 300 | 10 / 311 | 11 / 312 | 311 | 312 |
| 10 | 311 | 12 / 321 | 13 / 322 | 321 | 322 |
| 11 | 312 | 12 / 321 | 13 / 322 | 321 | 322 |
| 12 | 321 | 14 / 331 | 15 / 332 | - | - |
| 13 | 322 | 14 / 331 | 15 / 332 | - | - |
| 14 | 331 | 16 / 400 | - | - | - |
| 15 | 332 | 16 / 400 | - | - | - |
| 16 | 400 | 17 / 411 | 18 / 412 | 411 | 412 |
| 17 | 411 | 19 / 421 | 20 / 422 | 431 | 432 |
| 18 | 412 | 19 / 421 | 20 / 422 | 431 | 432 |
| 19 | 421 | 21 / 431 | 22 / 432 | - | - |
| 20 | 422 | 21 / 431 | 22 / 432 | - | - |
| 21 | 431 | 23 / 500 | - | - | - |
| 22 | 432 | 23 / 500 | - | - | - |
| 23 | 500 | 24 / 511 | 25 / 512 | - | - |
| 24 | 511 | 26 / 521 | 27 / 522 | - | - |
| 25 | 512 | 28 / 523 | 29 / 524 | - | - |
| 26 | 521 | 30 / 600 | - | - | - |
| 27 | 522 | 30 / 600 | - | - | - |
| 28 | 523 | 30 / 600 | - | - | - |
| 29 | 524 | 30 / 600 | - | - | - |
| 30 | 600 | 31 / 611 | 32 / 612 | - | - |
| 31 | 611 | 33 / 621 | 34 / 622 | 621 | 622 |
| 32 | 612 | 33 / 621 | 34 / 622 | 621 | 622 |
| 33 | 621 | 35 / 700 | - | - | - |
| 34 | 622 | 35 / 700 | - | - | - |
| 35 | 700 | 36 / 710 | - | - | - |
| 36 | 710 | 37 / 720 | - | 720 | - |
| 37 | 720 | 38 / 731 | 39 / 732 | 731 | 732 |
| 38 | 731 | 40 / 741 | - | - | - |
| 39 | 732 | 41 / 742 | - | - | - |
| 40 | 741 | - | - | - | - |
| 41 | 742 | 42 / 800 | - | - | - |
| 42 | 800 | - | - | - | - |

Notes:
- The save reserves 100 nodes / 200 links, but the shipped campaign logic iterates `num_nodes = 43` nodes for the main career tree.
- Some `base_update_*` targets intentionally “skip ahead” (see comments in `CCareer::ReCalcLinks()`), but that impacts base-objective persistence, not the graph structure itself.

---

## On-Disk Structure Validation (Steam Saves)

We validated that the **structural** career graph fields in a real Steam `.bes` save match Stuart’s `level_structure` exactly:
- Verified on `save-attempts/haha-cannon-goes-brrrrr.bes` (10,004 bytes).
- For nodes `0..42`:
  - `CCareerNode.mWorldNumber` matched `level_structure[i][0]`
  - `CCareerNode.mLowerLink == 2*i` and `mHigherLink == 2*i+1`
  - `CCareerNodeLink[2*i].mToNode == level_structure[i][1]` and `[2*i+1].mToNode == level_structure[i][2]`

Implication: we can safely use the Stuart table for **index-level mapping** (node index <-> world number <-> link indices/targets) when writing editor logic for Steam saves. (The *payload* fields like `mBaseThingsExists` still must be preserved.)

---

## Safe Unlocking Strategies (Save Editor Guidance)

### A) Unlock All Missions (Don’t Mark As Completed)

Goal: make later missions selectable without claiming you beat earlier ones.

Recommended:
- For each **used** link where `mToNode != -1`, set `mLinkType = CN_COMPLETE (1)`.
- Leave `CCareerNode.mComplete` and `CCareerNode.mRanking` unchanged.
- Do not modify structural fields:
  - `CCareerNode.mLowerLink` / `mHigherLink`
  - `CCareerNodeLink.mToNode`
  - `CCareerNode.mBaseThingsExists[]` (preserve objective persistence bits)

This is the lowest-risk unlock operation because it changes only the gate state of edges and preserves all per-mission state.

#### Implementation Sketch (Steam `.bes`)

```text
LINKS_BASE = 0x1906
LINK_SIZE  = 8
USED_LINKS = 86   # 43 nodes * 2 links per node (campaign tree)

// For link j:
//   mLinkType @ LINKS_BASE + j*LINK_SIZE + 0x00  (u32)
//   mToNode   @ LINKS_BASE + j*LINK_SIZE + 0x04  (i32)

for j in [0 .. USED_LINKS-1]:
  to = read_i32(file, LINKS_BASE + j*8 + 4)
  if to != -1:
    write_u32(file, LINKS_BASE + j*8 + 0, 1)   # CN_COMPLETE
```

If you want *selective* unlock:
- Find the target node index `i` by scanning `CCareerNode[i].mWorldNumber` in the nodes block (file `0x0006 + i*0x40 + 0x10`).
- Then set **at least one** incoming link with `mToNode == i` to `CN_COMPLETE (1)`.
- For world-by-world incoming-link ids and natural conditions, use `career-unlock-recipes.md`.

### B) Mark All Campaign Missions Completed (Fast “100%”)

Only do this if you explicitly want the save to claim completion:
- Set `CCareerNode.mComplete = 1` for the used campaign nodes.
- Set `CCareerNode.mRanking` to a chosen grade (commonly `S` = float bits `0x3F800000`).
- Also set relevant links to `CN_COMPLETE (1)` so the map remains consistent.

Risk tradeoff:
- This may interact with goodie unlock recomputation, “new goodie” counters, and other progress systems. Prefer doing this on a copy of a known-good save.

### C) World 500 Branch (Special Case)

`CCareer::ReCalcLinks()` has a world-500 special case: instead of secondary objectives, it checks slot flags:
- `SLOT_500_ROCKET` = 61
- `SLOT_500_SUB` = 62

If you want an editor to force-unlock both branches, you can:
- Set both slot bits (61 and 62) in `mSlots`, and set both of world-500’s child links to `CN_COMPLETE`.

Slots are documented in `reverse-engineering/save-file/struct-layouts.md` (true dword view offset `0x240A` for `mSlots[0]`).

### D) Repair “Locked Because Only Broken Parents Exist”

Common failure case in edited saves:
- A node has incoming links, but all of them are `CN_COMPLETE_BROKEN (2)`.
- `Career_IsWorldUnlocked` still returns locked because it only accepts `CN_COMPLETE (1)`.

Safe repair:
1. Identify target world `W` and node index `i` (`mWorldNumber == W`).
2. Find incoming links (`mToNode == i`).
3. Set exactly one incoming link `mLinkType = 1`.
4. Leave other incoming links unchanged (or set to `2` for visual consistency).

Do not touch:
- `mToNode`, `mLowerLink`, `mHigherLink`, `mBaseThingsExists[]`, file size.

World-500 caveat:
- For 500->511/512 branch correctness after in-game recomputation, keep slot bits aligned with intended branch (`61` rocket/higher, `62` sub/lower).

---

## What Not To Touch

Avoid these unless you’re intentionally doing deeper experiments:
- `CCareerNode.state` at `+0x00` (historical/legacy flags; preserve)
- `mBaseThingsExists[9]` (objective persistence bits)
- Any structural indices (`mLowerLink`, `mHigherLink`, `mToNode`)
- File size (must remain `0x2714` for Steam saves)
