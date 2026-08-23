# The Worlds of the Campaign

- **Status:** live preservation record. Graph links and world identities are
  measured; runtime notes are bounded observations from retained TTD openings;
  story names remain in [world-lore.md](world-lore.md). Where this page and a
  measurement under [`reverse-engineering/`](../reverse-engineering/RE-INDEX.md)
  disagree, the measurement wins.
- **Last updated:** 2026-08-22
- **Summary:** all 43 career nodes and all 23 additional numeric worlds shipped
  in the pristine PC resource shelf, with one section per world and an honest
  boundary between graph fact, observed mechanics, and unknown purpose.

## What a world is

The game calls a mission a **world**. The integer is used by the career graph,
save nodes, world headers, numeric resource archives, mission scripts, and
frontend selection. World `100` is hard-coded as always unlocked; otherwise the
retail unlock gate resolves the world to a career node and accepts a completed
incoming link ([career-graph.md](../reverse-engineering/save-file/career-graph.md)).

The pristine PC shelf has exactly **66 numeric resource archives**. Their IDs
are:

`100 110 200 201 211 212 221 222 231 232 300 311 312 321 322 331 332 400 411 412 421 422 431 432 500 511 512 521 522 523 524 600 611 612 621 622 700 710 720 731 732 741 742 800 850 851 852 853 854 855 856 857 858 859 860 861 862 863 864 865 866 901 902 903 904 905`.

A strict read-only basename census finds this exact same 66-ID set in Xbox
Europe, Korea, and USA. PS2 differs: its exact `DATA0.NYO` index has 67 numeric
resource names, sharing 65 IDs with PC/Xbox, adding `000` and `888`, and omitting
a numeric `201_res_PS2.aya` row. These are presence facts, not career-node or
byte-parity claims; the purpose and reach of `000`/`888` remain unknown. Xbox
Europe also has different resource bytes for 612, 856, and 863. See [The Same
War on Different Platforms](platform-content-variants.md).

Only 43 of those IDs occur in the compiled `level_structure` career graph. The
other 23 are real shipped worlds but are not career nodes. Presence is not an
unlock claim.

## How to read the runtime notes

The 2026-08-22 TTD mine retained one roughly three-minute opening capture for
each of the 66 worlds. Its cleanest result is a **range-level fingerprint**, not
a proof that every member of the range instantiates every named system:

| Range | Mechanic-shaped functions distinctive in retained openings |
|---|---|
| 1xx | `IScript` spawn/objective family; world 100 has no observed combat path, while `CUnit__ApplyDamage` first appears in 110 |
| 2xx | `Attack` / `GetEnergy` script family |
| 3xx | Thunderhead family, including its dedicated leg-motion path |
| 4xx | WarspiteDome family |
| 5xx | Submarine and HiveBoss families |
| 6xx | Carver family |
| 7xx | `IScript__Damage`, `IScript__GameTime`, and `OP_DIVIDE` VM work |
| 8xx | MCTentacle and Sentinel variants |
| 9xx | SphereTrigger plus `Rand`/`CMP`/`JMPNE` script work |

“Distinctive” means observed in that range and in no other retained opening set
under the mine's threshold. It does not mean impossible elsewhere. All opening
captures stop before normal level-end flow.

## Career worlds — 43 measured nodes

### World 100 — career node 0

Graph: campaign root; child `110`. Retail treats it as always unlocked. Its
opening covered 540,411 executable bytes and did not execute the retained
weapon-fire or `CUnit__ApplyDamage` paths. Four tutorial slots (63-66) preserve
teaching progress, and the released world header selects `Aquila Prototype`.

### World 110 — career node 1

Graph: parent `100`; child `200`. Its opening covered 618,821 executable bytes.
This is the first retained opening where round-hit, explosion-hit, weapon burst,
and `CUnit__ApplyDamage` all execute, so it is the observed transition from the
non-combat tutorial into live combat.

### World 200 — career node 2

Graph: parent `110`; children `211` and `212`. Its opening covered 590,893
executable bytes. It begins the 2xx branch and belongs to the range whose
bounded runtime fingerprint is the `Attack`/`GetEnergy` script family.

### World 211 — career node 3

Graph: parent `200`; children `221` and `222`; primary/secondary base snapshots
target `231`/`232`. Its opening covered 590,851 executable bytes. It is one side
of the first paired route, not a separate episode.

### World 212 — career node 4

Graph: parent `200`; children `221` and `222`; base snapshots also target
`231`/`232`. Its opening covered 589,502 executable bytes. The shared children
are measured graph structure, not an inferred reconvergence.

### World 221 — career node 5

Graph: parents `211` and `212`; children `231` and `232`. Its opening covered
541,061 executable bytes. It remains inside the 2xx `Attack`/`GetEnergy`
fingerprint.

### World 222 — career node 6

Graph: parents `211` and `212`; children `231` and `232`. Its opening covered
544,227 executable bytes. It is the sibling route to 221.

### World 231 — career node 7

Graph: parents `221` and `222`; child `300`. Its opening covered 610,780
executable bytes and executed the measured round-plus-explosion damage path.
It is one of the two exits from episode 2.

### World 232 — career node 8

Graph: parents `221` and `222`; child `300`. Its opening covered 613,586
executable bytes and executed the same measured damage path as 231. Both routes
reconverge at the single world-300 node.

### World 300 — career node 9

Graph: parents `231` and `232`; children `311` and `312`. Its opening covered
574,193 executable bytes. It begins the 3xx range whose bounded fingerprint is
the Thunderhead subsystem.

### World 311 — career node 10

Graph: parent `300`; children `321` and `322`; base snapshots target
`321`/`322`. Its opening covered 608,178 executable bytes. Mission-script
evidence also uses a friendly-building count and failure threshold here.

### World 312 — career node 11

Graph: parent `300`; children `321` and `322`; base snapshots target
`321`/`322`. Its opening covered 608,696 executable bytes. It is the sibling
route to 311 under the same 3xx fingerprint.

### World 321 — career node 12

Graph: parents `311` and `312`; children `331` and `332`. Its opening covered
608,357 executable bytes. The range-level Thunderhead fingerprint applies as a
comparison contract, not proof that this exact opening spawned the boss.

### World 322 — career node 13

Graph: parents `311` and `312`; children `331` and `332`. Its opening covered
614,242 executable bytes and executed both round-hit and explosion-hit paths.

### World 331 — career node 14

Graph: parents `321` and `322`; child `400`. Its opening covered 562,021
executable bytes. It is one of two 3xx exits into the carrier-war branch.

### World 332 — career node 15

Graph: parents `321` and `322`; child `400`. Its opening covered 580,603
executable bytes. It is the sibling exit to 331.

### World 400 — career node 16

Graph: parents `331` and `332`; children `411` and `412`. Its opening covered
600,095 executable bytes. It begins the 4xx set, where the WarspiteDome family
is distinctive in retained openings.

### World 411 — career node 17

Graph: parent `400`; children `421` and `422`; base snapshots target
`431`/`432`. Its opening covered 620,928 executable bytes.

### World 412 — career node 18

Graph: parent `400`; children `421` and `422`; base snapshots target
`431`/`432`. Its opening covered 623,000 executable bytes. It is the sibling
route to 411.

### World 421 — career node 19

Graph: parents `411` and `412`; children `431` and `432`. Its opening covered
548,958 executable bytes and executed the ordinary projectile/damage pipeline.

### World 422 — career node 20

Graph: parents `411` and `412`; children `431` and `432`. Its opening covered
548,217 executable bytes. It is the sibling route to 421.

### World 431 — career node 21

Graph: parents `421` and `422`; child `500`. Its opening covered 603,600
executable bytes. It is one exit from the 4xx WarspiteDome range.

### World 432 — career node 22

Graph: parents `421` and `422`; child `500`. Its opening covered 605,695
executable bytes. It is the sibling exit to 431.

### World 500 — career node 23

Graph: parents `431` and `432`; children `511` and `512`. Its opening covered
559,204 executable bytes. This is the graph's special branch gate: mission
slots 61 and 62 record the rocket and submarine outcomes used by
`CCareer__ReCalcLinks`. The level's scripts name both rocket and submarine
paths; the 5xx range is where Submarine/HiveBoss functions are distinctive.

### World 511 — career node 24

Graph: parent `500`; children `521` and `522`. Its opening covered 627,548
executable bytes. It is the first half of the rocket/submarine branch fan.

### World 512 — career node 25

Graph: parent `500`; children `523` and `524`. Its opening covered 595,172
executable bytes and reached unit destruction/cleanup in the retained window.
It is the sibling half of the fan.

### World 521 — career node 26

Graph: parent `511`; child `600`. Its opening covered 594,893 executable bytes.
Separate retained combat takes identify the Muspell Research Station, eight
turrets, the FSV Marshall, Gnats, and the Hive Boss as named mission actors;
those takes, not the passive opening, exercise the deep HiveBoss damage path.

### World 522 — career node 27

Graph: parent `511`; child `600`. Its opening covered 513,981 executable bytes.
It is one of four parallel 5xx routes that all reconverge at 600.

### World 523 — career node 28

Graph: parent `512`; child `600`. Its opening covered 589,512 executable bytes.
It is the third of the four parallel routes.

### World 524 — career node 29

Graph: parent `512`; child `600`. Its opening covered 591,647 executable bytes.
It completes the four-route fan and reconverges at 600.

### World 600 — career node 30

Graph: parents `521`, `522`, `523`, and `524`; children `611` and `612`. Its
opening covered 523,745 executable bytes. It begins the 6xx range, whose bounded
runtime fingerprint is the Carver subsystem.

### World 611 — career node 31

Graph: parent `600`; children `621` and `622`; base snapshots target
`621`/`622`. Its opening covered 564,667 executable bytes.

### World 612 — career node 32

Graph: parent `600`; children `621` and `622`; base snapshots target
`621`/`622`. Its opening covered 572,448 executable bytes. Retained call-context
also enters `CCarver__Init`, directly corroborating the range attribution.

### World 621 — career node 33

Graph: parents `611` and `612`; child `700`. Its opening covered 565,492
executable bytes. It is one exit from the Carver range.

### World 622 — career node 34

Graph: parents `611` and `612`; child `700`. Its opening covered 572,133
executable bytes. It is the sibling exit to 621.

### World 700 — career node 35

Graph: parents `621` and `622`; child `710`. Its opening covered 551,245
executable bytes. It starts the straight 7xx approach to the final fork.

### World 710 — career node 36

Graph: parent `700`; child `720`; the base snapshot target is `720`. Its opening
covered 547,299 executable bytes. The shipped world-header/configuration census
makes `Sniper` the only base-world configuration here, and the level script
gates cloak tutorial text on that configuration.

### World 720 — career node 37

Graph: parent `710`; children `731` and `732`; base snapshots target those same
children. Its opening covered 578,188 executable bytes and directly executed
`IScript__Damage`, one of the 7xx-distinctive script operations.

### World 731 — career node 38

Graph: parent `720`; child `741`. Its opening covered 600,826 executable bytes
and is one of the retained openings where the player's damage function executes.
Career slots 1-30 are named for route-731 Fenrir component state.

### World 732 — career node 39

Graph: parent `720`; child `742`. Its opening covered 597,153 executable bytes
and also executed the player's damage function. Career slots 31-60 are named for
route-732 Fenrir component state.

### World 741 — career node 40

Graph: parent `731`; no child. Its opening covered 547,947 executable bytes.
The shipped level-741 script directory owns `Fenrir.msl`, engine, turret, and
cutscene scripts; the Fenrir component vocabulary covers turrets, main gun,
plane launchers, bomb bays, engines, and doors.

### World 742 — career node 41

Graph: parent `732`; child `800`. Its opening covered 552,196 executable bytes.
The paired Fenrir script handles component persistence; its loss path spawns an
escape pod, performs a three-point pan around Fenrir, and reports the player as
still inside. The graph's asymmetry is literal: 741 is terminal while 742 leads
to 800.

### World 800 — career node 42

Graph: parent `742`; no child. Its opening covered 504,618 executable bytes and
terminates the 43-node career table. It is also the first member of the broader
8xx runtime comparison set, where MCTentacle/Sentinel variants are distinctive.
No graph evidence connects 800 to 850.

## Shipped non-career worlds — 23 numeric archives

### World 201 — non-career 2xx world

Not present in `level_structure`; a shipped numeric resource and retained
opening nevertheless exist. The opening covered 605,880 executable bytes,
including the round/explosion damage path, and belongs to the 2xx
`Attack`/`GetEnergy` comparison range. Its normal unlock route is unknown.

### World 850 — non-career 8xx world

Not in the career graph. Its opening covered 585,103 executable bytes. It is one
of seventeen contiguous 850-866 archives in the 8xx MCTentacle/Sentinel
comparison set; that family-level result does not prove both systems appear in
this individual world.

### World 851 — non-career 8xx world

Not in the career graph. Its opening covered 571,295 executable bytes. A retained
call-context bundle also exercised the HUD target-indicator path.

### World 852 — non-career 8xx world

Not in the career graph. Its opening covered 498,939 executable bytes. No unique
story or unlock claim is established.

### World 853 — non-career 8xx world

Not in the career graph. Its opening covered 513,883 executable bytes. Its exact
purpose outside the career table remains open.

### World 854 — non-career 8xx world

Not in the career graph. Its opening covered 536,222 executable bytes and
reached `CBattleEngine__Damage` through the explosion path.

### World 855 — non-career 8xx world

Not in the career graph. Its opening covered 564,625 executable bytes and
executed the measured round-hit path.

### World 856 — non-career 8xx world

Not in the career graph. Its opening covered 564,116 executable bytes. The Xbox
Europe resource for 856 differs from the Korea/USA pair, but all regions still
carry world 856; that is a regional asset variant, not an exclusive map.

### World 857 — non-career 8xx world

Not in the career graph. Its opening covered 472,270 executable bytes, the
smallest observed 8xx opening footprint in the retained set.

### World 858 — non-career 8xx world

Not in the career graph. Its opening covered 563,327 executable bytes.

### World 859 — non-career 8xx world

Not in the career graph. Its opening covered 525,296 executable bytes and
reached projectile targeting support.

### World 860 — non-career 8xx world

Not in the career graph. Its opening covered 576,320 executable bytes.

### World 861 — non-career 8xx world

Not in the career graph. Its opening covered 577,411 executable bytes.

### World 862 — non-career 8xx world

Not in the career graph. Its opening covered 594,660 executable bytes, the
largest footprint among 856-866, and reached round hit, explosion hit, unit
damage, and destruction cleanup in the retained window.

### World 863 — non-career 8xx world

Not in the career graph. Its opening covered 574,335 executable bytes. As with
856, Xbox Europe carries a region-specific resource variant while Korea/USA
match; the world ID itself is common.

### World 864 — non-career 8xx world

Not in the career graph. Its opening covered 585,020 executable bytes.

### World 865 — non-career 8xx world

Not in the career graph. Its opening covered 491,159 executable bytes.

### World 866 — non-career 8xx world

Not in the career graph. Its opening covered 525,190 executable bytes and closes
the contiguous shipped 850-866 run. No measured career link reaches any member
of that run.

### World 901 — non-career 9xx world

Not in the career graph. Its opening covered 498,609 executable bytes. Shipped
mission-script evidence identifies this as the loader race: lap monitors,
checkpoints, timers, a qualifying threshold, and victory after four laps. The
9xx range's bounded runtime fingerprint is SphereTrigger plus
`Rand`/`CMP`/`JMPNE` script work.

### World 902 — non-career 9xx world

Not in the career graph. Its opening covered 515,472 executable bytes. It is a
shipped 9xx multiplayer/race-era world; no more specific purpose is claimed
without a cited script.

### World 903 — non-career 9xx world

Not in the career graph. Its opening covered 533,960 executable bytes. It shares
the 9xx script-family comparison boundary, not a proven identical mode.

### World 904 — non-career 9xx world

Not in the career graph. Its opening covered 550,567 executable bytes and
reached additional unit-AI support in the retained window.

### World 905 — non-career 9xx world

Not in the career graph. Its opening covered 486,236 executable bytes and is the
last numeric world shipped in the PC resource shelf.

## Honest unknowns

- A numeric resource and a successful forced opening do not establish normal
  frontend reachability. That remains open for 201 and 850-866.
- The 8xx and 9xx family fingerprints are range-level observations. They must
  not be rewritten as “every world contains this boss/mode.”
- Mission titles are intentionally read from the user's own language data by
  the app rather than copied into this repository; see
  [the-campaign.md](the-campaign.md).
- The retail shelf measured here contains no numeric worlds below 100, no 888,
  and no 956/958. Older directory-census prose that mentions such numbers is
  not evidence that corresponding pristine PC resource archives ship.

## Sources

- Career nodes, links, and real-save validation:
  [career-graph.md](../reverse-engineering/save-file/career-graph.md).
- Numeric resource count and world-header corpus:
  [installed-corpus-census.md](../reverse-engineering/installed-corpus-census.md).
- Per-world opening byte counts and range fingerprints:
  `local-lab/hermes-kanban-campaign-2026-08-22/ttd-deep-mine/REPORT.md` and
  batches 1-7 (runtime observation, bounded to retained captures).
- Mission slots, level-500 branching, level-901 race, and Fenrir scripts:
  [msl-scripting.md](../reverse-engineering/game-assets/msl-scripting.md).
- Level-710 configuration evidence:
  [battleengine-config-values.md](../reverse-engineering/quick-reference/battleengine-config-values.md).
- Cross-region Xbox level-resource differences:
  [BUILD_AND_DUMP_MATRIX.md](../reverse-engineering/BUILD_AND_DUMP_MATRIX.md).
- Place names and story framing: [world-lore.md](world-lore.md) and
  [characters.md](characters.md); those are lore/prose sources, not executable
  evidence.
