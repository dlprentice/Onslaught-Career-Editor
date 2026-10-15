# Brief for Peer B: the occupancy grids and pathfinder in the parity core (from Peer J, rebuild lead)

Status: approved by the lead 2026-10-15 (after storage incident #2).

## Goal
Port COccupancyGrid and COccupancy so level 100's ground vehicles steer exactly as retail's: the same grids after
the load, the same paths, the same cell tests. Integer code mostly; float only in path start/end conversions.

## Where
- WHILE ARCHIVE B IS READ-ONLY: write the port into /var/tmp/bea-scratch/peer-b/occupancy/ (internal disk), as
  standalone .cs files plus a tiny scratch test project if you want to compile (dotnet on /var/tmp is fine; ONE heavy
  job machine-wide, ask the lead first for anything big). No reads or writes on the Onslaught checkout until the lead
  clears it. Then:
- Base on `claude/rebuild-20261015` (merge it often). Your branch `claude/rebuild-occupancy-20261015`, your own
  worktree. Push it; I review, reproduce and merge. No force-push, no git stash, no git clean, never stage
  local-lab/ or local-data/.

## Files you own (new)
- `rebuild/OnslaughtRebuild.Parity/World/OccupancyGrid.cs` (COccupancyGrid, the path type CNormalSquadUnknownD4 if
  your Squad.cs does not already own it: then move it there, your call) and `World/Occupancy.cs` (COccupancy's
  statics). Tests `OnslaughtRebuild.Parity.Tests/OccupancyTests.cs`.
- Hooks I own and will wire once you report: WorldLoader's grid load/skip (world.cpp 845-875; level 100 skips its
  own grids and loads base world 1's), CWorld::InitOccupancy/AddToOccupancy/BuildStatic calls (now Context.Skip),
  CUnit::GetOccupancyGrid (Unit.cpp 2056, by unit data mUnknownFC: 0 none, 1 -> grid 0 (35), 2 -> grid 1 (45),
  3/4 -> grid 2 (60)), and the guides' mGrid.

## Sources (bea-decomp, read-only)
src/NavigationMap.cpp (971 lines; every function has its address), src/world.h (COccupancyGrid 64-115, sGrid
00809db8), src/Occupancy.h, world.cpp 845-875 and 940-950, Unit.cpp 2056. Callers: GroundVehicleGuide.cpp
(UnknownCell, Unknown4bc2e0, GetCurrent on the path), SquadNormal.cpp, MechGuide.cpp, InfantryGuide.cpp.
None is in Stuart's release unless you find a sibling in references/Onslaught (grep first): GPL-3.0-or-later
otherwise. File headers name the functions adapted, with addresses. Never copy decompiler output or retail bytes.

## Exactness
- Follow retail's compiled behaviour. (SINT) of a float is X87.Fist (/QIfist: round to nearest; 64-bit fistp keeping
  the low dword for huge values) unless the decomp shows _ftol. Static search state (sGrid and any static arrays) is
  global in retail: keep it static, including whatever a previous search leaves behind.
- Float code passes D's oracle (onslaught-career-editor-f2) before it counts as exact.

## Tests
1. Load base world 1 and level 100 (LevelLoadTests.Level100Run): the three grids' cells hash the same as the native
   port's (ask Peer I for a dump at the end of CWorld::Load(100) and after BuildStatic), and level 100 skips its own.
2. Paths: Unknown4bc2e0 from each level-100 ground vehicle's start to its first destination, compared with a port
   trace (ask Peer I), and focused cases for Flood/StepDown/Simplify edges (blocked start, unreachable end, map edge).

## Report (under 400 words)
Branch and commit, what is ported, the grid/path comparisons, retail quirks found, test count, PROVENANCE rows.
