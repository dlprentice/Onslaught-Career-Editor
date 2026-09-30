# Level inventory: the 95 MissionScripts folders

Status: active reference
Last updated: 2026-09-30
Summary: which of the 95 numbered `data/MissionScripts` folders are playable levels, how the retail game reaches
each one, and what the 29 folders that cannot load contain.
Evidence: MEASURED — the pristine specimen's `data/` tree: the folder listing, `data/resources/*_res_PC.aya`,
`data/WorldHeaders.dat` (all 97 records parsed, 4,783 of 4,783 bytes) and `data/language/english.dat`
(`tools/language_dat_decode.py` with `text/text.stf`). The code paths cite
[bea-decomp](https://github.com/dlprentice/bea-decomp) functions that match retail byte for byte, named with their
addresses; the multiplayer lock test is read from retail's disassembly (0051d28c..0051d2d6) because its function
does not match yet. RUNTIME — the 2026-08-15 native coverage census
(`local-lab/native-corpus-coverage-20260815-v1/native-coverage.tsv`) records script natives executed in
three-minute level-opening traces of each of the 66 archived levels, on the retired Windows capture setup. Nothing
was launched for this document.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, and the `data/` tree beside it.

## In short

- `data/MissionScripts` holds 95 numbered folders (`level000` to `level958`; five are spelt `Level`), `onsldef.msl`
  and `text/`.
- **66 are playable levels.** Each has a world archive `data/resources/NNN_res_PC.aya` and a record in
  `data/WorldHeaders.dat`, and each one's scripts ran in the 2026-08 level-opening traces: the 43 campaign levels,
  201 for the playable demo, 17 two-player levels (850–866) and 5 race levels (901–905).
- **The other 29 cannot load.** Without an archive there is no world data: the world loader's only other source is
  `data\worlds\world%03d.wrd` (`CWorld::Load` 0050b520; both path strings are in the executable), and the retail
  install has no `data\worlds`. 19 folders are empty shells. The other 10 hold scripts: six early prototypes (003,
  004, 010, 020, 021, 022), an unfinished level (530), a flagship-duel test (888), and two copies of the hidden
  co-op script (956, 958).
- **The game does not read these folders.** A level's compiled scripts are part of the world data in its archive:
  `CWorld::DeserializeWorld` (0050b780) records where the world sits in the resource file, and
  `CWorld::LoadScripts` (0050ac70) reads each script's name and object code into `CMissionScriptObjectCode`
  (00538ec0). Nothing in the executable compiles scripts: its only script-related strings are the runtime VM's own
  `__FILE__` names (`MissionScript\AsmInstruction.cpp`, `IScript.cpp`, `ScriptObjectCode.cpp`, `Symtab.cpp` and
  so on) and class names. It has no `data\MissionScripts` path and no language keyword (`end_vars`, `do_once`) in
  ASCII or UTF-16. So the `.msl` and `English.txt` files are shipped source, and `text/text.stf` is the generated
  text-id header that the C++ source and the scripts `#include`.
- **Two playable levels are on no menu:** 856 and 858, co-op levels that only `-level` reaches.

## How the game reaches a level

| Route | Levels | Evidence |
| --- | --- | --- |
| Campaign | the 43 campaign nodes | `level_structure` in `Career.cpp`, compared word for word with retail's table at `0x00623e28` ([career graph](../save-file/career-graph.md)); `CCareer::GetNodeFromWorldNo` (0041b8f0) |
| Playable demo | 201 | `-playabledemo` sets `PLAYABLE_DEMO`; the demo's main page starts 201 (`CFEPDemoMain::DoAction` 00457ee0). 201's archive was the only level archive in the 2003 PC demo ([LVLR archive](../asset-formats/lvlr-archive.md#exact-pc-demo-shelf)) |
| Two-player grid | 15 of the 17 two-player levels | the cell table in `CFEPMultiplayer::Init` (0051ca70); the cursor's row picks the mode text (retail 0051d8c9 passes it to `GetMultiplayerLevelDescription` 0046a220) |
| Goodies wall | 901–905 | Goodies 66–70 start races 1–5 (`CFEPGoodies::Process` 0045d7e0); a race returns to the Goodies page (`CFrontEnd::Init` 004662a0) |
| Command line | any number | `-level N` runs `GAME.RunLevel(N)` without the frontend (`CSystem::Run` 004f0330). A co-operative or versus world gets two players (`CGame::LoadLevel` 0046cdf0 asks `CWorld::IsMultiplayer` 0050d7d0) |

Only the campaign levels and 201 have names and briefings (`CFrontEndText::GetLevelName` 00469550,
`GetBriefingTextId` 00469cf0), and 201 uses 200's. Any other number gets the fallback name "Unnamed Level".

## Playable levels (66)

### Campaign (43)

English names from `english.dat` (`FETX_LEVEL_NAME_*`). The graph's links, grades and base-world bitmaps are in the
[career graph](../save-file/career-graph.md). The career opens a level's "(Evo)" version when the level before it is
won with every secondary objective complete ([career links](../save-file/career-links.md)). 500 branches instead to
two different missions, 511 and 512, by save slot (62 for the submarine, 61 for the rocket). 7.41 ends the
campaign. 7.42 (Evo) leads on to 8.00, which the career reaches from nowhere else.

| Episode | Levels |
| --- | --- |
| 1 | 100 Training Level; 110 Blackout |
| 2 | 200 Interception; 211/212 Assault On Apollo; 221/222 Escort Duty; 231/232 Counterstrike |
| 3 | 300 Liberation of Russo; 311/312 Muspell Counterattack; 321/322 The Wake Of The Venturer; 331/332 Thunderhead! |
| 4 | 400 Beach Head; 411/412 Weathering The Storm; 421/422 Naval Ambush; 431/432 Battle For Yenya |
| 5 | 500 Split second; 511 Death From Above; 512 Silent Running; 521/522 Versus The Hive; 523/524 Enter The Gill-M |
| 6 | 600 Back to Castellian; 611/612 Castellian Assault; 621/622 Air Raid |
| 7 | 700 Crushing Blow; 710 Blinding The Enemy; 720 Rescue Attempt; 731/732 Assault Force Fenrir; 741/742 The Fall Of The Fenrir |
| 8 | 800 The Sentinel Awakes |

### Playable demo (1)

201 is the demo's version of 200 Interception. It shows 200's name and briefing, but its level script and lander
scripts differ from 200's (it has no vital buildings, and it waits for the invasion to start before it counts the
enemy down), and its archive differs too. With `-playabledemo` the retail executable shows the demo's main page, whose first choice starts 201. That is a
static reading; nobody has run the flag on the full install.

### Two-player (17)

The grid has three rows, one per mode, and six columns (`CFEPMultiplayer::Init` 0051ca70; mode text 0046a220):

| Mode (row) | Columns 1–3 | Columns 4–6 |
| --- | --- | --- |
| Co-Op | 850, 853, 859 | 864, 865, 866 |
| Skirmish | 851, 855, 860 | 861, 862, 863 |
| Versus | 852, 854, 857 | — |

- Columns 4–6 open once world 800 or 741 is complete (retail 0051d2a7..0051d2d6 asks the career for node 800, then
  node 741).
- `-e3` closes one cell, 859, the third Co-Op column (0051d28c..0051d2a2). The E3 build also quits on inactivity
  (`CController::InactivityMeansQuitGame` 0042d810) and asks for a `vectorlosttoyssplash.tga` splash
  (`CSystem::Init` 004efb10), which the retail install does not ship.
- **856 and 858 are on no grid cell.** Both have archives and world-header records of the co-operative type, and
  both ran in the 2026-08 opening traces. Their script folders are byte-identical. The players defend a base
  against landers: the level is lost when fewer than ten buildings stand, and won once every lander and enemy
  ground unit is destroyed. The script borrows its counter and messages from campaign levels 512, 312 and 231. Only
  `-level 856` or `-level 858` reaches them.
- The text data has no per-level names for these levels. The grid shows mode descriptions only: "Co-Op Mode",
  "Skirmish Mode" and "Versus Mode".

### Race (5)

901–905 are checkpoint races flown with the "Racer" Battle Engine configuration, run by a `LapMonitor.msl` and
`LapTimer.msl` in each folder. Row 0 of the Goodies wall holds them as Goodies 66–70 (`get_goodie_number`
0045cb80):

- Goodie 66 (the first race, 901) is unlocked by `UpdateGoodieStates`, which counts C-or-better campaign grades.
  Its label says A grades; see [the Goodies system](../save-file/goodies-system.md).
- Each later race is unlocked by the previous race's script; the unlock texts read "A Grade on Race Level 1" to
  "Race Level 4". In 901's shipped source, finishing under 2,900 ticks (145 s at 20 ticks a second) sets the next
  race's Goodie. Script Goodie numbers are 1-based:
  `IScript::SetGoodieState` (00533a70) subtracts 1, so the source's `SetGoodieState(68, …)` sets save index 67.

## Folders that cannot load (29)

None of these has a `NNN_res_PC.aya`. "Header" means a record in `WorldHeaders.dat`.

| Folders | Header | Contents |
| --- | --- | --- |
| 000, 001, 002, 005, 007, 008, 009, 011, 012, 013, 018, 023, 025, 026, 030, 105, 301, 900 | yes | an empty `text.stf` only |
| 520 | yes | a `text.stf` holding only the text converter's banner comment |
| 003 | yes | a base defence: three zones west, east and south of the base warn when Muspell ground forces enter, with counters for Forseti and Muspell buildings and turrets. Its English text is in `english.dat` |
| 004 | yes | tank traps and a vital building and emplacement |
| 010 | yes | a target range with close, medium and long-range targets; declares its variables in an `attributes … end_attributes` block, which no other level script uses (the rest use `vars … end_vars`) |
| 020 | yes | destroy the Muspell advance base and motorised units, and keep four ambulances alive; objectives printed to the console. The same `attributes` block as 010 |
| 021 | yes | destroy three hangars; losing the control tower loses the level |
| 022 | no | a HUD walkthrough using the object scripts of 100 Training Level (airborne drones, target tanks, four target zones); it reads as an earlier cut of that level |
| 530 | yes | an unfinished level with the Hive and Gill-M boss scripts of 521–524 (arachnid, gnat, hive, `GillM*`, sub, lander) and a stub level script whose boss start is commented out. It has no name, briefing or text |
| 888 | yes | a flagship duel test: the Fenrir's loss prints "FORSETI WIN" and the Venturer's "MUSPELL WIN". The script includes one developer's text header (`data\text\extra2\jim\text.stf`) |
| 956, 958 | no | byte-identical copies of 856's and 858's scripts |

## WorldHeaders.dat

`CFEPBEConfig::Init` (0044fa90) and `CFEPWingmen` read it when the frontend starts: a version and a count, then one record per
world (`CFEPBEConfig::Load` 0044fe70). A record holds the world number, the Battle Engine configurations offered
(counted strings such as `Standard`, `Laser`, `Blaster`, `Sniper`, `Aquila Prototype`, `Racer`), the three wingman
flags and the world type (`SBEConfigLevel`, `FEPBEConfig.h`). All 97 records are version 3. Each record has the
shape of the header at the front of that world's own file, which `CWorld::LoadHeader` (0050d4c0) reads when the
level loads: the frontend takes its choices from this collected copy, and the level takes its type from its own.

- The 97 worlds are the 92 folders with headers (every folder except 022, 956 and 958) plus five worlds that exist
  nowhere else: 950, 951, 952, 960 and 961.
- The world type is `CWorld::EWorldType` (`world.h`: 0 single player, 1 co-operative, 2 versus). It is 1 for every
  Co-Op level and for 856 and 858, 2 for every Skirmish and Versus level and for 888, and 0 for every other world.
  In a level, `CWorld::IsMultiplayer` (0050d7d0) tests the world file's copy; no reader of this file's copy
  (`mUnknown10`) is known.

## Open questions

- Do the shipped `.msl` sources match the compiled scripts in the archives? Cheapest falsifier: decode one archive's
  script object code (the `CMissionScriptObjectCode` stream) and compare its event names and constants with the
  folder's source. 901's race-time thresholds are a good first probe.
- What were 856 and 858 meant to be? They play (2026-08 traces) but no menu lists them. Cheapest falsifier: a
  capture of `-level 856` on the Linux harness, once David has released the desktop, compared with 850's opening.
- Does anything read the world type in the frontend's copy? Search the unmatched frontend functions for
  `SBEConfigLevel` offset `+0x10` loads.
