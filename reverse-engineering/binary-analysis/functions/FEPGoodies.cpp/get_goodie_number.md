# get_goodie_number

> Address: `0x0045cb80`
> Source: `references/Onslaught/FEPGoodies.cpp` (static `get_goodie_number`)

## Status
- Named in Ghidra: Yes
- Signature set: Yes
- Verified vs source: Yes

## Signature

```c
int get_goodie_number(int x, int y)
```

## Behavior

- Maps goodies-grid coordinates `(x,y)` to a flattened goody id.
- Applies category/range-specific remap offsets.
- Returns `-1` when the requested grid position is invalid/unmapped.

## Headless Read-Back Detail (2026-05-07)

Read-only headless Ghidra export rechecked the compiled retail helper at `0x0045cb80` and confirmed the visible wall mapping:

| Grid row | X range | Return range | Meaning |
| --- | ---: | ---: | --- |
| `y == 0` | `0..7` | `0..7` | character bios |
| `y == 0` | `8..12` | `66..70` | race-level unlocks |
| `y == 0` | `13..16` | `74..77` | developer items |
| `y == 1` | `0..57` | `8..65` | unit/model gallery |
| `y == 2` | `0..31` | `201..232` | FMV slots |
| `y == 3` | `0..122` | `78..200` | concept art |

This mapping still leaves shipped `goodie_71_res_PC.aya` through `goodie_73_res_PC.aya` outside the known visible wall coordinates. Asset metadata confirms those three archives are texture-only `GDIE` descriptors resolving to `ca_be_final01`, `ca_be_final02`, and `ca_bea_battle_pic` texture payloads, with no mesh references. It also confirms slot `232` is displayable as an FMV mapping even though the PC resource folder has no separate `goodie_232_res_PC.aya`.

Follow-up read-back exported `get_goodie_number`, `CFEPGoodies__StartLoadingGoody`, `CFEPGoodies__LoadingGoodyPoll`, `CFEPGoodies__ButtonPressed`, `CFEPGoodies__Process`, and `CFEPGoodies__BuildStaticGoodieDataTable` with all six functions present.

The same pass exported xrefs to `get_goodie_number`: 13 rows, with named callers `CFEPGoodies__StartLoadingGoody`, `CFEPGoodies__LoadingGoodyPoll`, `CFEPGoodies__ButtonPressed`, and `CFEPGoodies__Process`. A dry-run then headless apply recovered and named the `CFEPGoodies__ButtonPressed` function boundary at `0x0045cde0`, moving the eight previously no-function xref rows (`0x0045ce53`, `0x0045ce87`, `0x0045cf2a`, `0x0045cf4c`, `0x0045d03b`, `0x0045d070`, `0x0045d0be`, `0x0045d0cd`) under that function. A follow-up signature pass set `void __thiscall CFEPGoodies__ButtonPressed(void * this, int button, float val)`. Follow-up instruction export classifies those call sites as source-correlated Goodies wall navigation, selected-coordinate load gating, post-load state checks, and selected-state update paths. They are not proof of a hidden 71-73 path.

Follow-up verifier hardening now checks the `ButtonPressed`, `Process`, and `LoadingGoodyPoll` decompile exports for direct `0x47`/`0x48`/`0x49` target constants. Current result: `PASS hits=0`. Constants for 71-73 remain expected in the unlock recomputation read-back and source/asset topology, not in these selected-coordinate handlers.

## Runtime Replay Note (2026-05-07)

A copied-profile, windowed retail replay loaded an all-Goodies copied save through the Load Game UI and walked the Goodies top row. Private captures confirmed the visible sequence `66..70` as Race Challenge 1-5, then the next visible slot jumped to `74` (`Battle Engine Aquila Picture`) and continued through `75` (`Intro Storyboard Sequence`), `76` (`Team Photo`), and `77` (`Development`). This supports the compiled mapping above for normal wall navigation. It does not prove that 71-73 have no hidden/non-grid runtime path.

Read-only asset inspection after the runtime replay confirmed 71-73 are not missing resources; they are shipped, tiny texture-only archives. Source inspection also confirms they are not merely accidental archive rows: `CCareer::UpdateGoodieStates()` marks all three new when `COMPLETE_LEVEL_OR_EVO(741)` is true, and episode-instruction logic can mark 71 in episode 7 and 72/73 in episode 8. The remaining RE question is whether any direct-selection, developer, cheat, or non-wall branch can request those ids at runtime.

## Source Reachability Note (2026-05-07)

`references/Onslaught/FEPGoodies.cpp` still lists `CGoodieData(GOODIES_71)`, `CGoodieData(GOODIES_72)`, and `CGoodieData(GOODIES_73)`, and `get_goodie_type_hack` classifies `goodie_num <= 73` as `GT_IMAGE` after the race-level ids 66-70. The source texture lookup also contains explicit cases for 71-73. `references/Onslaught/Career.cpp` sets 71, 72, and 73 new from the same `COMPLETE_LEVEL_OR_EVO(741)` condition and sets instruction hints for 71 in episode 7 plus 72/73 in episode 8.

The ordinary source selection path does not use those ids directly. `StartLoadingGoody`, `LoadingGoodyPoll`, FMV/level handling, and selection rendering all ask `get_goodie_number(mCX, mCY)` for the active coordinate. `ButtonPressed` changes `mCX/mCY`, clamps or walks across invalid coordinates, and the render loop skips coordinates where `get_goodie_number(...) == -1`. The disabled `STRESS_TEST_GOODIES` branch in the source randomizes coordinates, not ids. This source pass therefore found valid assets/types/unlock hooks for 71-73, but no normal coordinate path to select them.

## Wave395 Saved-Ghidra Read-Back (2026-05-14)

- Saved signature preserved as `int __cdecl get_goodie_number(int x, int y)`.
- Saved function comment now records the row-by-row Goodies wall coordinate map and explicitly keeps hidden reachability/UI navigation behavior unproven.
- Saved tags include `static-reaudit`, `goodies-wave395`, `frontend-goodies`, `goodie-grid`, `goodie-id-map`, `retail-binary-evidence`, and `comment-hardened`.
- Read-back includes constants `0x3a`, `0x4a`, `0xc9`, and `0x4e`, plus xrefs from `CFEPGoodies__StartLoadingGoody`, `CFEPGoodies__LoadingGoodyPoll`, `CFEPGoodies__ButtonPressed`, and `CFEPGoodies__Process`.
- This does not prove hidden Goodies 71-73 reachability, runtime wall behavior, or rebuild parity.

## Notes

- Used by `CFEPGoodies__StartLoadingGoody`, `CFEPGoodies__LoadingGoodyPoll`, and `CFEPGoodies__Process`.
