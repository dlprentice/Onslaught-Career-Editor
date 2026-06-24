# Career Unlock Recipes (Steam)

Deterministic unlock guidance for each campaign world (`NUM_LEVELS=43`), derived from `references/Onslaught/Career.cpp` `level_structure` and retail `CCareer::ReCalcLinks` behavior.

This page is for **editor behavior design** and recovery planning, not live mutation instructions.

Legend:
- **Manual patch path**: minimal direct link-state edit to make the world available on the career map.
- **Natural path**: mission-completion condition that makes the link become `CN_COMPLETE` via game logic.
- Link indices use `CCareerNodeLink[200]` at file `0x1906`; link `j` fields are `mLinkType @ +0`, `mToNode @ +4`.

| World | Node Idx | Incoming Link(s) | Minimal Manual Patch Path | Natural Unlock Path(s) |
|------:|---------:|------------------|---------------------------|------------------------|
| 100 | 0 | *(none)* | None (always unlocked special-case) | None (always unlocked special-case) |
| 110 | 1 | `0` | set link `0` `mLinkType=1` | complete world `100` (primary path) |
| 200 | 2 | `2` | set link `2` `mLinkType=1` | complete world `110` (primary path) |
| 211 | 3 | `4` | set link `4` `mLinkType=1` | complete world `200` (primary path) |
| 212 | 4 | `5` | set link `5` `mLinkType=1` | complete world `200` + all secondary objectives complete |
| 221 | 5 | `6`, `8` | set link `6` `mLinkType=1` OR set link `8` `mLinkType=1` | complete world `211` (primary path) OR complete world `212` (primary path) |
| 222 | 6 | `7`, `9` | set link `7` `mLinkType=1` OR set link `9` `mLinkType=1` | complete world `211` + all secondary objectives complete OR complete world `212` + all secondary objectives complete |
| 231 | 7 | `10`, `12` | set link `10` `mLinkType=1` OR set link `12` `mLinkType=1` | complete world `221` (primary path) OR complete world `222` (primary path) |
| 232 | 8 | `11`, `13` | set link `11` `mLinkType=1` OR set link `13` `mLinkType=1` | complete world `221` + all secondary objectives complete OR complete world `222` + all secondary objectives complete |
| 300 | 9 | `14`, `16` | set link `14` `mLinkType=1` OR set link `16` `mLinkType=1` | complete world `231` (primary path) OR complete world `232` (primary path) |
| 311 | 10 | `18` | set link `18` `mLinkType=1` | complete world `300` (primary path) |
| 312 | 11 | `19` | set link `19` `mLinkType=1` | complete world `300` + all secondary objectives complete |
| 321 | 12 | `20`, `22` | set link `20` `mLinkType=1` OR set link `22` `mLinkType=1` | complete world `311` (primary path) OR complete world `312` (primary path) |
| 322 | 13 | `21`, `23` | set link `21` `mLinkType=1` OR set link `23` `mLinkType=1` | complete world `311` + all secondary objectives complete OR complete world `312` + all secondary objectives complete |
| 331 | 14 | `24`, `26` | set link `24` `mLinkType=1` OR set link `26` `mLinkType=1` | complete world `321` (primary path) OR complete world `322` (primary path) |
| 332 | 15 | `25`, `27` | set link `25` `mLinkType=1` OR set link `27` `mLinkType=1` | complete world `321` + all secondary objectives complete OR complete world `322` + all secondary objectives complete |
| 400 | 16 | `28`, `30` | set link `28` `mLinkType=1` OR set link `30` `mLinkType=1` | complete world `331` (primary path) OR complete world `332` (primary path) |
| 411 | 17 | `32` | set link `32` `mLinkType=1` | complete world `400` (primary path) |
| 412 | 18 | `33` | set link `33` `mLinkType=1` | complete world `400` + all secondary objectives complete |
| 421 | 19 | `34`, `36` | set link `34` `mLinkType=1` OR set link `36` `mLinkType=1` | complete world `411` (primary path) OR complete world `412` (primary path) |
| 422 | 20 | `35`, `37` | set link `35` `mLinkType=1` OR set link `37` `mLinkType=1` | complete world `411` + all secondary objectives complete OR complete world `412` + all secondary objectives complete |
| 431 | 21 | `38`, `40` | set link `38` `mLinkType=1` OR set link `40` `mLinkType=1` | complete world `421` (primary path) OR complete world `422` (primary path) |
| 432 | 22 | `39`, `41` | set link `39` `mLinkType=1` OR set link `41` `mLinkType=1` | complete world `421` + all secondary objectives complete OR complete world `422` + all secondary objectives complete |
| 500 | 23 | `42`, `44` | set link `42` `mLinkType=1` OR set link `44` `mLinkType=1` | complete world `431` (primary path) OR complete world `432` (primary path) |
| 511 | 24 | `46` | set link `46` `mLinkType=1` | complete world `500` with slot `62` (SLOT_500_SUB) set |
| 512 | 25 | `47` | set link `47` `mLinkType=1` | complete world `500` with slot `61` (SLOT_500_ROCKET) set |
| 521 | 26 | `48` | set link `48` `mLinkType=1` | complete world `511` (primary path) |
| 522 | 27 | `49` | set link `49` `mLinkType=1` | complete world `511` + all secondary objectives complete |
| 523 | 28 | `50` | set link `50` `mLinkType=1` | complete world `512` (primary path) |
| 524 | 29 | `51` | set link `51` `mLinkType=1` | complete world `512` + all secondary objectives complete |
| 600 | 30 | `52`, `54`, `56`, `58` | set link `52` `mLinkType=1` OR set link `54` `mLinkType=1` OR set link `56` `mLinkType=1` OR set link `58` `mLinkType=1` | complete world `521` (primary path) OR complete world `522` (primary path) OR complete world `523` (primary path) OR complete world `524` (primary path) |
| 611 | 31 | `60` | set link `60` `mLinkType=1` | complete world `600` (primary path) |
| 612 | 32 | `61` | set link `61` `mLinkType=1` | complete world `600` + all secondary objectives complete |
| 621 | 33 | `62`, `64` | set link `62` `mLinkType=1` OR set link `64` `mLinkType=1` | complete world `611` (primary path) OR complete world `612` (primary path) |
| 622 | 34 | `63`, `65` | set link `63` `mLinkType=1` OR set link `65` `mLinkType=1` | complete world `611` + all secondary objectives complete OR complete world `612` + all secondary objectives complete |
| 700 | 35 | `66`, `68` | set link `66` `mLinkType=1` OR set link `68` `mLinkType=1` | complete world `621` (primary path) OR complete world `622` (primary path) |
| 710 | 36 | `70` | set link `70` `mLinkType=1` | complete world `700` (primary path) |
| 720 | 37 | `72` | set link `72` `mLinkType=1` | complete world `710` (primary path) |
| 731 | 38 | `74` | set link `74` `mLinkType=1` | complete world `720` (primary path) |
| 732 | 39 | `75` | set link `75` `mLinkType=1` | complete world `720` + all secondary objectives complete |
| 741 | 40 | `76` | set link `76` `mLinkType=1` | complete world `731` (primary path) |
| 742 | 41 | `78` | set link `78` `mLinkType=1` | complete world `732` (primary path) |
| 800 | 42 | `82` | set link `82` `mLinkType=1` | complete world `742` (primary path) |

## Notes
- For map availability, `Career_IsWorldUnlocked` requires at least one incoming parent link with `mLinkType == 1` (`CN_COMPLETE`).
- `CN_COMPLETE_BROKEN (2)` does not satisfy the unlock gate.
- `mLinkType` normalization/promotion in retail is driven by `CCareer__Update` (`0x0041bd00`) calling `CCareer__ReCalcLinks` (`0x0041bdf0`); load flow consumes existing link states and does not directly recalc links.
- World-500 branch bits are in `mSlots[1]` (file `0x240E`): bit 29 = slot 61 (`SLOT_500_ROCKET`, unlocks higher link `47` -> world `512`), bit 30 = slot 62 (`SLOT_500_SUB`, unlocks lower link `46` -> world `511`).
- This mapping does not alter rank/goodie/kill semantics; it only describes world-availability gates.
