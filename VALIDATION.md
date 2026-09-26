# Validation

Status: active — the gate-selection table
Last updated: 2026-09-26 (World 110's static world from retail data; audit corrections: the Mech Bullet's round-only damage and comments; the terrain detail texture's one-radian stage-3 matrix; waypoint walks from the nearest node; scripts start on their INIT_SCRIPT events; the level's three-second pre-run; rounds on their own MOVE and life events; influence-map and warm-up draws in Level 100's load; cockpit Gun emitters for player rounds; Level 100's retail construction order and unit callbacks; every round's retail launch basis; the jet Missile Pod, its locks and seeking rounds; weapon stores, recoil shake and round Init draws; the Battle Engine's crosshair and auto-aim refresh; September 25 three-lane baseline, reconciliation, the AYA malformed-input contract and the return to all-code C#; earlier dated validation retained).
Summary: choosing the smallest evidence that proves the contract you changed.
[`package.json`](package.json) owns the commands.

Validation is proportional to the contract changed. Root
[`package.json`](package.json) is the command authority; the commands below are
options, not a required sequence.

Linux is the active development and native Godot host. `npm test` runs the companion's
C# contract suite (career codec, media inventory, protected adapter, publication races
and the code-built interface) and its launcher tests without opening a window. `npm run build` and
`npm run dev` build/run the Godot .NET companion. The latter opens a window.
The rebuild has native Linux build/run/smoke/capture commands; live input checks
need an available desktop. Source and headless tests alone do not establish native
input, audio, focus or full tutorial behavior.

The retained WinUI default is `npm run test:winui`. The full legacy AppCore suite,
WinUI, Windows-targeted CLI and ZIP procedures remain Windows-gated. The unused
evaluation VM was retired; no Windows host is provisioned here. The Windows entries
below require a separately provided Windows validation host, not a Linux prerequisite
or an instruction to recreate the VM. Historical rebuild launchers use explicit `:windows` aliases
and pin the matching 4.8 dev6 engine manifest and managed SDK. Archive/manifest
verification on Linux does not establish Windows runtime behavior.
No Linux result is Windows runtime acceptance. The dated August 30 full AppCore
run was **1,575 passed / 26 failed / 1,601 total**; its Windows-dependent failures
are not replaced by the focused portable results below.

| Change | Focused evidence |
| --- | --- |
| Documentation or deletion only | `git diff --check`, `npm run test:docs`, and the affected generator/reference check |
| A new or edited tracked `.md` header | `npm run test:doc-headers`, which is also inside `test:docs`. The contract is [`DOCUMENTATION.md`](DOCUMENTATION.md); the backlog of pre-standard documents is `tools/doc_header_backlog.txt` and may only shrink |
| AppCore behavior | `npm run test:save-lab` covers the supported Linux workflow on .NET 8; select an affected portable fixture and framework for other source changes. `test:appcore` retains the full Windows-dependent suite. |
| WinUI behavior or copy | On Windows, `npm run test:ui` or the affected test fixture, then one real-app workflow smoke |
| Companion (C# built in code) and its file safety | `npm run test:companion-godot` runs `Tests/CompanionTestRunner.cs` on owned real-save copies: codec contracts, independent byte diffs, protected round trips, changed/conflicting sources and links, publication races and the code-built interface's real controls. `test:companion-tools` checks pins, the code-only policy, staging and exports. |
| Retained save, options, copied-target, or patch safety | `test:save-lab` retains the C# service oracle and existing safety tests. Other services need their own affected fixture. The retained Windows `test:safe-copy` includes UI regressions. |
| CLI | On Windows, `npm run test:cli` and the relevant AppCore test |
| Lore inputs/reader | `npm run test:lore-pack` is portable; run the LoreBrowserService/AppCore fixture on Windows unless that exact fixture has been demonstrated platform-neutral |
| Public payload/provenance boundary | `npm run test:safety` |
| Rebuild Godot checks | `python rebuild/tools/first_flight.py run --no-build --no-prepare --timeout 600 --engine-arg=--headless --engine-arg=--audio-driver --engine-arg=Dummy --engine-arg=res://Scenes/Pause/Tests/PauseSceneChecks.tscn`, and the same with `res://Scenes/Shared/Tests/AyaTextureChecks.tscn` (add `-- --aya-expect=REPORT` to compare with a prior report). Smoke is the launcher's `smoke` mode with `-- --record-tape=PATH`, then `npm run run:rebuild-headless -- --tape PATH --repeat 2`. Pixel or audio claims need a godot-offscreen Movie Maker capture compared with the dated baseline. |
| Rebuild Core | `npm run test:rebuild-core` is the focused cross-host command and excludes only `Level100FerryLandingTests`; use `npm run test:rebuild-ferry-sweep` for that complete explicit oracle. The larger `npm run test:rebuild` aggregate additionally includes Windows-only Godot/capture gates and therefore requires a separately provided Windows host. **Current broad default receipt, 2026-08-31, at combined tip `c0e994ef` over causal Blaster commit `b8fca9ea`:** `dotnet test rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj --nologo --no-restore --filter 'FullyQualifiedName!~Level100FerryLandingTests' --logger 'console;verbosity=minimal'` measured **1,130 passed / 3 known failed / 1,133 total / 0 skipped**, **34 m 23 s**. The only failures in that dated run were the Linux-host Windows-message assertions `TapeFileWriteNew_RejectsExtendedNamespaceAliasInsideSuppliedKnownRoot`, `TapeFileWriteNew_RefusesUnsupportedDeviceNamespaceDestinations`, and `TapeFileWriteNew_EvaluatesResolvedIdentityOfExtendedAliasWithDotSegments`; the September 6 focused correction and result below close those failures without claiming a new broad run. The former `BlasterMissLaw_SeparatesTheRunsOwnHitsFromItsMisses` population mismatch now passes through exact internal round identity, and no assignment/start failure appeared. The 2026-08-30 **1,118/4/1,122** receipt remains historical. **PROGRAM P9 historical receipt, 2026-08-23, pre-change HEAD `221d7811`:** the actual runner first discovered 939 tests, including exactly the six ferry facts. After the split and three gate-composition facts, runner discovery proved **942 = 936 default + 6 sweep**, intersection zero, with the all-minus-default and explicit-sweep sets both exactly those six facts. The gate guard was RED 0/3 before script registration and GREEN 3/3 after. The explicit command passed **6/6** over the unchanged **20 perturbations × 2 arms = 40 runs**; VSTest reported **6 m 38 s**, while fleet-loaded wall time was **67 m 39 s**. Its pre-change 112.6 m overloaded run and the 2026-08-21 **862 passed / 1 failed / 863 total** run remain dated history, not current counts |
| Rebuild client/adapters | `npm run test:rebuild-client` |
| Godot toolchain or native behavior | `test:godot-host` checks launcher routing/process cleanup with fake tools. `build:companion-godot` refuses GDScript, saved resources and multi-node scenes, then builds the C# companion; `export:companion-godot` produces normal Godot .NET Linux/Windows exports. `build:rebuild-godot` follows its separate owner. Builds are headless. On an available desktop, `test:rebuild-godot-smoke` is a native synthetic smoke; actual input/audio and the Save Lab UI need a separate live workflow. |
| Frontend page drawing | Linux `capture:rebuild-godot -- -- --capture-plan=mainmenu` produces native captures. Compare them with the existing `tools/compare_capture.py` scorer and appropriate retail reference; capture success alone is not parity. The historical Windows `Capture-Frontend.ps1` combines capture and scoring. |
| Portable ZIP inputs or layout | On Windows, `npm run release:winui-zip` |
| Tip census claim in docs | Re-read `developer_state.json` → `current_re_authority`, require its literal READY/reducer/authority-receipt pins, and run the named full replay. Historical Gen10 and candidate Gen73 blocks are not current routing |
| Campaign ledger / generation TSVs | The externally pinned frozen bootstrap in `current_re_authority.verify`; a generation number, matching ledgers, self-derived pins, integrity-only success, or candidate reducer is not authority |
| Tracked evidence register or current authority pointer | `python ./tools/re_evidence_register_export.py --state developer_state.json --check-header-only` for the portable header gate; on the maintainer host, omit `--check-header-only` and use `--check` for literal-pinned full replay plus byte equality |
| C1 PE plate apply | Exact current pack path/bytes/SHA, entity/body identity, pristine-byte validation, and a field-scoped reducer. Independent normal/adversarial review is strongly advised for consequential changes but is not a fixed model matrix; see `reverse-engineering/REVIEW-PROTOCOL.md` |
| C2_BOUNDED_RUNTIME claim | Entity-scoped controlled runtime + can-fail refuter; refuse PE-only bulk C2 |
| Ghidra mutation | A declared cohort within the authorized task and the preservation/rehearsal/readback gate in `reverse-engineering/ghidra/README.md`; no writable opening of the tracked or cold owner. |

Rebuild commands materialize their exact retail inputs to ignored paths. Linux
selects canonical `local-lab/rebuild-godot` and discovers Steam library roots;
`-- --game-root "/absolute/game/root"` overrides discovery. A fresh checkout needs
its private canonical lab owner; worktrees verify and link its current materialized
files read-only, with imports and new output owned by the worktree. `prepare:rebuild-assets`
is sufficient when only that boundary changed.

September 19 engine migration: both installed 4.8 dev6 editions and matching
template payloads passed the shared toolchain's pinned hash verification. The
rebuild's supported Linux build passed locked restore/build with
`Godot.NET.Sdk/4.8.0-dev.6`, zero warnings/errors and unchanged `net8.0`. The
launcher suites passed 12 shared-host and 18 rebuild cases; canonical input
reuse/routing passed 17 cases, including stale-input, conflicting-file and
directory-link refusal. The matching Windows archive/manifest was checked on
Linux; Windows execution was not run. Evidence belongs to this branch's
`local-data/engine48/` and task transcript. These checks do not establish visual,
input, audio, GPU-performance or complete combat acceptance.

### World 110's static world from retail data — September 26

The materializer now writes World 110's level for the Simulation:
`rebuild/OnslaughtRebuild.Core/Assets/Level110/level110-static-world.json`
(schema `onslaught.world110-static-world.v1`, SHA-256 `7b201943…`, ignored like
the other Level110 outputs). It is built from the pristine specimen's
`110_res_PC.aya` and `default physics.dat` and follows the RE lane's
construction contract
(`reverse-engineering/game-mechanics/world-110-construction-order.md`):
- the shared base world's 33 objects and 1,481 pines, identical to Level 100's
  manifest, with each building's life from its unit record;
- the level rows in file order: Player 1 at the Start (row 1), the inactive
  spawner (row 5), the four landing craft each followed by its "Dropship Gun
  Turret" child, the volume (row 9), the 22 members of the five type-28 squads
  and the six fighters, each with its authored allegiance;
- the five squads (members, script, allegiance, mode, authored transform) and
  the four turret children;
- the four named paths, with the rows the loader drops (8, 25 and 5) and each
  waypoint's own target (`waypoint-paths.md`);
- each unit type's motion class and the settings words (pan 2.0).

`Level100ActorDefinitionManifest.DecodeWorld110` decodes it into a world-110
definition set, and Core's set now carries squads, components and each actor's
allegiance; identity format 14 hashes them, and Level 100's identities do not
move. Until the canonical checkout publishes the file, a worktree keeps an
exact local copy: the asset preparation accepts a missing canonical output only
when the local file has the pinned bytes.

Tests: `materialize_retail_assets_tests` (95, including the builder against the
pristine inputs and the missing-canonical rule), `World110StaticWorldManifestTests`
(4), Core 1,551 and Client 916 with the two known skips, and the safety gate
(4,085 files).

Open: the turret child's life (its component record's field map is not
established); member formation slots, which the squad sets at runtime
(`0x004e9600`, `0x004e8730`); dropship motion (the RE lane's contract is in
progress).

### Audit corrections: Mech Bullet damage and comments — September 26

The RE lane's record audit found these in rebuild code; each was re-read here
from the pristine specimen (`74154bfa…`).
- **Mech Bullet damage is 0.08, not 0.081.** `CExplosion::Init` compares an
  explosion's damage with the double 0.0015 (`0x0044b9e8-0x0044ba02`, `0x5db298`).
  At or below it, the explosion's collision mask becomes −1, and the filter at
  `0x00426900` then never collides. "Mech Bullet Hit" deals 0.001
  (`0x3a83126f`, `default physics.dat`), so a Mech Bullet does only its round's
  0.08 (`0x3DA3D70A`). The old value added the explosion. A Target Tank now takes
  76 rounds (was 75); a truck still takes 38 and a drone 13. No pinned run lands
  a Mech Bullet, so no pin moved. The cold-start run fires the Vulcan: it still
  wins at tick 8,540 with hull 3,350 on the abort branch, and its won tape now
  ends at state `c6017343…` (trace `b44844e6…`), replayed twice.
- **Comments only:** `CGame::SetSlot` and `CCareer::SetSlot` set a slot bit only
  for 1 (`0x0046d3c5`, `0x00421505`); the image has 146 `mov ecx, 0x008a9a98`
  (149 operand references); Enter is binding row 19 and Numpad Enter row 21;
  the installed Steam executable hashes pristine today; `+0x2494` is
  `mIsGod[2]`; the stop flag's readers and writers in `Run`, `CopyState` and
  Pause; the terrain scroll advances per `RenderTerrain` call for view 0 and
  wraps only above 1.0 (`0x005455f5`). Whether a second mission in the same
  process restarts the scroll phase is open.

### Terrain detail rotation — September 26

The terrain shader's second detail layer used an axis-aligned quarter scale. The
RE lane's audit found that stage 3's angle is the double at `0x005d87e0`,
re-read here from the pristine specimen (`74154bfa…`, `0x005459a4-0x005459fd`).
`fld qword` loads 1.0, one radian; read as a float32, its low dword is the 0.0
the old comment cited. `fcos` and `fsin` of it are scaled by `0x005d858c`
(0.25), with sin stored as a float32 first. That gives _11 = _22 = `0x3e0a5140`
(0.13507557), _12 = −_21 = `0x3e576aa4` (0.21036774) and offset (0.3, 0.3).
Stage 3 is COUNT2 (`0x0054599f`). The shader now applies that matrix to
(u, v, 1), and `Level100TerrainCompositorTests` pins both words and the shader
lines. Only a GPU render compiles the shader; the final capture is its check.

### Waypoint walks from the nearest node — September 26

Core started every waypoint walk at the head of its path's target chain and
steered at waypoints' authored heights. The RE lane's contract
(`reverse-engineering/game-mechanics/waypoint-paths.md`, commits `1e7bc137` and
`d0709d36`) was re-read here from the pristine specimen (`74154bfa…`):
- The loader keeps a path's `CWaypoint` rows (flag bit `0x1000`,
  `0x00505a29-0x00505a35`) and prepends each one (`0x004e5a80` links the new
  node ahead of the head). A path's list therefore runs in reverse file order.
- `0x00505c30` returns the listed node nearest the unit. It takes dx, dy and dz
  as waypoint minus unit (`+0x1c/+0x20/+0x24`) and sums (dx² + dz²) + dy² on the
  x87 stack. The sum is compared with `fcom` (C0, a strict `<`) against a
  float32 minimum that starts at 9999999.0 (`0x4b18967f`); a new minimum is
  stored with `fstp`.
- On arrival the next node is the current waypoint's `+0x3c` (`0x005384dc`). A
  waypoint that targets itself logs `0x0064fe50` and ends the walk.
- `CThing::Init` raises a waypoint below the heightfield sample (`0x0047eb80`,
  `0x004f34fb-0x004f3534`) to it, then one below the water level (`0x006fbdfc`,
  `0x004f3549-0x004f3559`) to that. `InitAndLink`'s second sample
  (`0x005057db-0x005057f6`) cannot move it again.
- When a walk ends, `CDropship`'s slot 64 is a bare `ret` (`0x00459990`).
  `CPlane`'s (`0x00422750`) resets its guide: slot 8 (`0x0047e3d0`) clears the
  mode word, sets the goal to the position and zeroes `+0x14c`'s xyz. A ground
  vehicle takes the Unit default (`0x004fcf00`).

Core now loads each path as retail's list, with each node's own target
(`Level100WaypointPathDefinition.FromFileOrder`), and seats the waypoints at
their load-time heights (`Level100ActorMechanics.SeatWaypoints`). A walk starts
at `NearestPoint` from the unit's position and follows the targets. A dropship
keeps its velocity at the end of a walk. The definition identity carries each
node's target (formats 10-13). What moved in Level 100:
- The Air Trainer is authored nearer node 42 than 41, so it flies 42 → 43
  instead of 41 → 42 → 43.
- Flyby node 42 lies 3.1 m inside the hillside and rises to the ground
  (z −18.10). The nodes over the sea rise to the water level (z −8.84): Flyby
  43, Transporter 44 and all four drone nodes. The truck and tank nodes rise to
  the ground.
- Spawned targets start from the node nearest their spawn. Target Tank #23
  still drives 6 → 7 → 18.

Six mutations were killed and restored byte-identical
(`local-data/test-runs/waypoint-routes-20260926/mutation-kills/`): a start at
the list head; no load-time lift; a dropship that stops at the walk's end; a
self-target that keeps walking; the file order kept; and a tie that keeps the
later node.

Tests that moved read the retail list and node targets instead of the chain.
The Transporter test now places the craft at its authored position, since the
fixture's origin is nearer node 23.

Core passes 1,553, the ferry sweep 6/6, and Client 912 with the two known
skips. The pause checks (56) and AYA checks (447) pass. Re-pinned:
- `first-flight.v1.json` replays to trace `fe219cb2…` and state `5e51c9a6…`;
- the in-process smoke and its validator: state `8649ff2b…`;
- the canonical-hash fingerprints;
- the chain autopilot, now on the six-kill branch: Won at tick 6,502 with hull
  9,554.

The headless Godot smoke records tape `ed3b77b5…` (trace `97cf1e7c…`, state
`8649ff2b…`). The C# replayer reproduces it twice, and the smoke validator
module accepts the report. The cold-start won tape is 8,540 ticks (trace
`d6df9a59…`, state `fdf132e6…`), on the abort branch after two second-wave kills
with hull 3,350, and it replays twice.

Open: Core has no dropship motion, so the U-17 and World 110's landing craft do
not fly their paths yet. The RE lane's runtime check of the start nodes is still
open.

### Scripts start on their INIT_SCRIPT events — September 26

Core used to run every script's `init()` during the load: Setup first, the
authored scripts in actor-id order, then LevelScript. Retail starts each script
on an event (the RE lane's construction contract, "Level-world rows" and
"Scripts in the first frames", with its answers on the carriers and on World
110's Setup):
- `SetScript` binds the VM and files INIT_SCRIPT 2001 at −1 for the thing itself
  (`0x004f42b1-0x004f42da`).
- A constructed thing's script is bound first in its construction sequence.
- A script carrier (`CLevelScriptThing`: Level 100's LevelScript and Setup at
  rows 5 and 17, World 110's rows 0, 2 and 39) files only that event, at its
  row position.
- A scripted unit's AI constructor also files the 2003 for its `ready()`
  before its AI.
- So the first flush runs the inits in row order. Setup's own `SetScript`
  bindings file for frame 2, which is when the Tank Factory runs its init and
  builds its first Target Tank. World 110 depends on this: Setup activates
  five inactive base units after their first AI events.

Core now files these events during the load and lets the flush run them:
- a scripted row's 2001 first in its sequence, and its 2003 before its AI;
- each carrier's 2001 at its row, placed by the definitions' level-row
  identities;
- `SetScript` and spawned units' 2001 for the next frame.

The Simulation owns the handlers: a thing's init or `ready()`, LevelScript's
`init()` (the mission now takes it on its event), and Setup's. An authored
plane's `ready()` now runs on its 2003; a spawned plane's still comes from its
exit handoff. Standalone script and mission tests keep the immediate path.

Tests:
- `SimulationTests.Construction_StartsEveryScriptOnItsInitScriptEvent` pins
  the load's 2001 order: row 5, rows 9-16, row 17, then rows 19, 21 and 40. It
  also pins the Tank Factory's first spawn to frame 2 and every script
  initialized after the pre-run.
- `Level100UnitCallbackTests` now expect the Warehouse's 2001 and 2003 in its
  sequence, and set the world's carriers aside.
- The load-draw count no longer includes the Tank Factory's spawn, which
  closes the open difference recorded with the construction order.

Five mutations were killed and restored byte-identical
(`local-data/test-runs/script-inits-20260926/mutation-kills/`): no INIT_SCRIPT
for a scripted row, carriers after every row, `SetScript` running at once, no
`ready()` event, and a spawned script starting at once.

Other tests that moved:
- A Client test read the Target Tank's guide phase as if at its construction.
  It is now read 58 frames later, since the tank is built on frame 2.
- The truck-spawn test stopped as soon as the trucks settled. It now waits for
  their scripts, a frame later, to send them down their paths.

Core passes 1,555, the ferry sweep 6/6, and Client 912 with the two known
skips. Re-pinned:
- `first-flight.v1.json` replays to trace `7d4a41a7…` and state `ab0c274b…`;
- the in-process smoke and its validator: state `629076b4…`;
- the canonical-hash fingerprints;
- the chain autopilot, still on the abort branch after two kills, at tick 5,793
  with hull 4,750.

The headless Godot smoke records inputs equal to the previous tape's (tape
`ec218626…`, trace `cb556aa4…`), and the C# replayer reproduces it twice. The
cold-start won tape is 7,750 ticks (trace `45c72494…`, state `00616ef4…`), on
the abort branch with no second-wave kills and hull 1,293, and it replays
twice.

Open: World 110's Weather carrier has no Core owner yet, and its handler
refuses it.

### The level's three-second pre-run — September 26

Core started Level 100's six-second pan at its first tick, so its world had
run 60 frames less than retail's when the player first saw it.
- `CGame::InitRestartLoop` files FINISHED_PRE_RUN at now + 3.0 before the world
  loads (`game.cpp:371-373`).
- `CGame::PreRun` then runs whole updates, unrendered, until it arrives
  (`game.cpp:2063-2071`).
- The RE lane confirmed the frames (`reverse-engineering/game-mechanics/level100-construction-order.md`,
  "Pre-run, pan and the first rendered frame", commit `2035942b`):
  - frames 1-60 run in the pre-run, and frame 60's flush starts the pan;
  - FINISHED_PANNING lands on frame 180 for Level 100 and frame 100 for World 110;
  - no state-1 check changes a draw. Script events run as usual; only
    presentation, sounds and input differ.
- The Steam measurements of the pan (installed at event time 3.0, playing at
  9.0) and of the message boundaries already count from the pan's start.

Level construction now runs those 60 frames with no input, so tick 0 is frame
60 and the first tick is frame 61:
- The pan starts after them, and the event and mission clocks both read 60 at
  tick 0.
- The message box's gate is 181 mission ticks, the same instant as before on
  the session's clock.
- The load's and the pre-run's mission events and script commands reach the
  first tick, as retail shows them once the visuals start.
- An internal receipt keeps the state at the end of the load for construction
  tests.

Tests that compared the session's tick with a script or mission clock now use
one clock:
- the trigger helpers and the reference-frame text gate;
- the skip-panning gates;
- the Godot audio's mission-start guard. It rejected a mission clock ahead of
  the session's, which the first headless smoke caught before the guard was
  changed.

Construction and at-rest tests read the load receipt. The Vulcan-ready clock
test now finds the first frame after the pre-run that shows its rounding
pattern.

`SimulationTests.Construction_RunsTheThreeSecondPreRunBeforeThePan` pins:
- both clocks at 60 and the draws the pre-run took;
- the pan's full 120 ticks, ending on frame 180, and the gate at 181;
- the cold career's deactivation reaching the first tick.

Five mutations were killed and restored byte-identical
(`local-data/test-runs/pre-run-20260926/mutation-kills/`): no pre-run, 59
frames, no pan after it, the pre-run's mission events dropped, and a message
gate without it. A sixth, the pan also set at the load, is equivalent, since
the pre-run's end resets it.

The pre-run moved the chain autopilot and the cold-start route:
- **Cold start.** It first lost to water at Target Zone 4. After the drone
  abort it dropped out of jet mode 2.75 m from the zone, 12 m up at 5.7 m/s,
  and drifted 13 m into the sea. The autopilot's cruise hand-off now also
  requires a dry-land ballistic touchdown, which its committed hand-off
  already did.
- **Chain autopilot.** It wins on the abort branch after two kills, at tick
  5,618 with hull 6,050. The test calls the branch a fixture reading, and it
  still checks the result is a released branch.

Core passes 1,554 (the ferry sweep 6/6 among them) and Client 912 with the two
known skips. Re-pinned:
- `first-flight.v1.json` replays to trace `d956053b…` and state `6b49e986…`;
- the in-process smoke and its validator: state `3582db72…`, with a mission
  tick of 2,208;
- the canonical-hash fingerprints.

The headless Godot smoke records inputs equal to the previous tape's (tape
`633e782f…`, trace `a1be972b…`), and the C# replayer reproduces it twice. The
cold-start won tape is 7,557 ticks (trace `9aa196fc…`, state `15a4c22f…`), on
the abort branch with one second-wave kill and hull 5,700, and it replays
twice.

Open:
- **First rendered frame.** Retail's shows frame 61's update with its render
  fraction; the Godot host draws tick 0 first.
- **Script inits.** Core still runs them at the load, not in frame 1's flush.
  The Tank Factory's spawn draws therefore still come before frame 1 rather
  than in frame 2.

### Rounds on their own MOVE and life events — September 26

Core used to move player rounds at the end of every update, starting on the
launch frame, newest first. Drone rounds moved after the flush, also newest
first. Every round lived a fixed tick count. The RE lane's round contract
(`reverse-engineering/game-mechanics/level100-final-drone-wave.md`, "Frames"
and "No hit while dying", commits `0827d186` and `6c966df3`, with its message
on insertion order) says:
- `CRound::Init` files the Actor MOVE at −1 and the life event 4000 at now +
  the life span. A round built in frame N first moves in frame N+1's flush,
  then every frame.
- Each delivered MOVE re-files itself as it is delivered, so rounds move in the
  manager's insertion order. A round made by a controller Fire goes in before
  the MOVEs its flush re-files, so it moves ahead of older rounds. One made by
  a 5001 burst goes in at that point of the flush.
- The life event lands k = floor((life − 0.001) × 20) buckets out and comes
  before that frame's MOVE. A `CRoundExplode` round (the Micro Missile) bursts
  in the air where it is, then every round starts dying. The MOVE still takes
  one last step and is not re-filed: k + 1 Moves, 160 for 8.0 s.
- A dying round's last step still meets things, but its own Hit returns before
  damage, its impact explosion and its death. Only the struck thing's script
  hit notification remains.

Core now files both events for every round, player and drone, on the level's
event manager under round listeners, and moves each round when its MOVE is
delivered. A life of 9.9 s or more is past the ring and waits in the overflow
list, which is delivered after the lanes. So the Forseti Missile (10 s) takes
that frame's MOVE, then its last step in the next frame. The dying state is the
absence of a filed life event, so snapshots gain no fields. Not modelled:
- the Forseti's own air burst;
- the next frame's SHUTDOWN. Core removes a round on its last step or its
  impact, so a hit round's `LockHit` comes one frame early, and a round that
  impacts one frame before its life ends does not burst a second time, as the
  contract says retail does.

Tests:
- `SimulationTests`:
  - `PitchedPulseRound_FollowsViewPitchWithoutInventingVerticalTargetHits`
    pins a round at its emitter on the launch frame and gone after L Moves;
  - `ControllerRounds_MoveAheadOfRoundsAlreadyInFlight` reads the next
    bucket's MOVE order;
  - `DyingRound_LastStepCrossesATargetWithoutDamagingIt` checks the dying step
    against a live control;
  - the pod launcher test now pins each air burst exactly at the missile's
    previous-frame position.
- `Level100ActorWeaponTests`:
  - `ActorRounds_MoveOnTheirOwnEventsUntilTheirLifeEnds`: the Blaster's 60
    Moves, and the Forseti's overflow count computed from its filed due time;
  - `ActorRound_LastStepMeetsThePlayerWithoutDamage`: a contact-only receipt
    on the dying step, a damaging one a step earlier.
- `Level100DestructionContactTests.DyingRoundContact_ReportsTheHitButLeavesTheTargetUnharmed`.

Eight mutations were killed and restored byte-identical
(`local-data/test-runs/round-frames-20260926/mutation-kills/`): a first Move
two frames late; a new round queued behind the re-filed MOVEs; player and
drone rounds that outlive their life event; the air burst where the last step
ends; dying player and drone steps that damage; and a dying contact the
target's script never hears.

Core passes 1,547, the ferry sweep 6/6, and Client 912 with the two known
skips. First-flight fires nothing and keeps its pins. Re-pinned:
- the in-process smoke and its validator: state `7191f986…`;
- the chain autopilot, which still wins on the six-kill branch, at tick 6,286
  with hull 12,450.

The headless Godot smoke records inputs equal to the previous tape's (tape
`167b17b0…`, trace `274aecdf…`), and the C# replayer reproduces it twice. The
cold-start won tape is 8,188 ticks (trace `cc34aaec…`, state `fa0ea6ce…`), on
the abort branch with one second-wave kill and hull 7,377, and it replays
twice.

### Influence map and warm-up draws in Level 100's load — September 26

The RE lane corrected its construction-order contract
(`reverse-engineering/game-mechanics/level100-construction-order.md`, commit
`ec29ffa4`). Retail's load takes six draws that Core did not:
- After the base world's pines, `CInfluenceMapManager::Load` (`0x0048b010`)
  ends in `0x0048b8e0`. It takes one draw (`0x0048bf0f`, on every path) and
  files an influence 1000 at now + 1.0 + (r mod 65536) × 2⁻¹⁶.
- After the last level row, `SpawnInitialThings` (`0x0050dcb0`) builds one unit
  of each script-spawned type that no row built, then destroys it at once; only
  its construction draws remain. Level 100's scripts spawn Target Truck, Target
  Tank, Air Trainer and Target Drone. The rows already built the tanks and the
  Air Trainer, so two warm-ups are left: the Target Truck (Actor and hover
  draws) and the Target Drone (Actor draw and `CPlane::Init`'s last draw).
- The load's tail calls `0x0048b8e0(0)` again: one draw and a second 1000.

Each 1000 delivery takes one draw and files that chain's next 1000, so the two
chains draw every one to two seconds for the whole level. Core now takes these
draws and runs both chains on the level's event manager under a reserved
listener. The influence map's 1001 and 1002 and the Battle Engine's new
motion-controller 3000, cockpit 2001 and receiver 4000 draw nothing, so Core
still does not file them. The base-world pass exists only for a definition set
that carries the base world's pines, which the materialized retail set does and
the small test fixture does not.

Tests:
- `Level100UnitCallbackTests.BaseWorldPass_StartsTwoInfluenceChainsAroundTheWarmUps`
  pins both 1000s' due times against the draw sequence (pines, first draw, rows,
  four warm-up draws, tail draw) and one delivery's draw and re-file.
- `Level100BattleEngineRefreshTests` and the construction draw count
  (`Level100ActorWeaponTests.ConstructionDraws`) take the six new draws.
- A Client test pinned the first Target Tank's move phase at 0. That value
  came from where its Actor draw fell, so the test now derives the phase from
  the tank's construction and first-Move frames.

Six mutations were killed and restored byte-identical
(`local-data/test-runs/influence-warmup-20260926/mutation-kills/`): no draw
after the pines, no warm-ups, warm-ups of types the rows built, no tail draw, a
2⁻¹⁵ delay scale, and a chain that stops after one delivery.

Core passes 1,540 and Client 912 with the two known skips. Re-pinned:
- `first-flight.v1.json` replays to trace `79a4db1b…` and state `77a71d70…`.
- The in-process smoke and its validator: state `0df3dd5c…`.

The headless Godot smoke records inputs equal to the previous tape's (tape
`7136d58b…`, trace `c44be61a…`), and the C# replayer reproduces it twice. The
chain autopilot runs on the fixture and keeps six kills at tick 6,254 with hull
11,564. The cold-start won tape is 8,220 ticks (trace `de6af83a…`, state
`2bce3c9c…`), on the abort branch with no second-wave kills and hull 9,450, and
it replays twice.

Open: whether both 1000 chains persist all level, and the receiver's 0.03 s
delay; the contract names a draw-count log in a copied runtime as the check.

### Cockpit Gun emitters for player rounds — September 26

Core launched every player round from one point: a live capture of the Pulse's
emitter relative to the Battle Engine (right −6 mm, forward 80 mm, up 259 mm),
turned by yaw and pitch only. The RE lane's aiming contract
(`reverse-engineering/game-mechanics/battle-engine-aiming.md`, "Gun emitters",
commits `0827d186` and `0aa1ceac`) gives each weapon its own emitters on the
cockpit mesh `cockpit2.msh`. Their model positions are x right, y forward and z
down, and the world pose is the body orientation `+0x3c`, roll included, times
that position plus the Battle Engine's position.

The weapon modes' launch sequences name the emitters: Pulse, Gun 1; Twin
Vulcan, Guns 9-12 (walk pose); Mech Vulcan, Guns 13-14; pod, Guns 4, 3, 5, 2,
6. Gun 1 comes out at (0.09, 84, 258 above) mm. The captured (−6, 80, 259)
differs by the cockpit tilt and render-fraction terms that the contract leaves
open, so the model value is used.

Tests:
- `Level100CockpitEmitterTests` (9 cases) pins the Gun table against the
  contract's composed poses and each weapon's sequence.
- `SimulationTests.MechVulcanRounds_LeaveGunsThirteenAndFourteenInSequence`
  checks the jet Vulcan's two rounds leave Guns 13 and 14 in order, through the
  full body basis.
- The Pulse emitter tests now expect Gun 1.

Four mutations were killed and restored byte-identical
(`local-data/test-runs/emitters-20260926/mutation-kills/`).

Core passes 1,539 and Client 912 with the two known skips. First-flight fires
nothing and keeps its pins. The in-process smoke and validator now read state
`cb9281fc…`. The headless Godot smoke records inputs equal to the previous tape's
(tape `add3de61…`, trace `06af5907…`), and the C# replayer reproduces it twice.
The chain autopilot wins through six kills at tick 6,254 with hull 11,564. The
cold-start won tape is 8,139 ticks (trace `c430525d…`, state `6e1f75a0…`), on
the abort branch with no second-wave kills, and it replays twice.

Open:
- The cockpit tilt S and the render-fraction lerp of the pose.
- The cockpit's own offsets `+0x1c` and `+0xc`, taken as zero.
- The body shake term of `+0x3c`, not yet applied.

Correction to the previous change's commit message: retail takes 1,535 draws
before its first frame, not 1,540. Core's other five are the Tank Factory
spawn, which retail takes on frame 2.

### Level 100 construction order and unit callbacks — September 26

Core used to take three draws while building Level 100 (the Air Trainer's Actor
draw, then the Battle Engine's 6002 and 6003) and no unit callbacks at all. The RE
lane's construction-order contract
(`reverse-engineering/game-mechanics/level100-construction-order.md`, commits
`b8a19b68`, `c3fff6c4` and `0aa1ceac`) gives the retail load: the base world's
1,481 pines, one draw each; base rows 0-34 in file order; then the level world's
rows. Row 0's Start builds the Battle Engine inline, so its draws follow base row
34.

Per class, in load order:
- **Buildings:** one Actor draw, then a 4003 and an AI.
- **Cannons:** the Actor draw, which also phases their four-frame Move, and the
  fire-control refresh's draw with its 4001; then a 4003 and an AI.
- **Features and city buildings:** one Actor draw; city buildings also get a 4003.
- **Battle Engine:** its Actor draw and a 4003, then 6002's and 6003's draws.
- **Target Tanks:** the Actor draw, which phases the squad member's Move; a
  4003; the hover draw; an AI; then three squad draws for 4000, 4001 and 4002.
- **Warehouse:** one draw; its AI starts on 3001 because its authored target is a
  waypoint.
- **U-17:** one Actor draw, a 4003 and an AI.
- **Air Trainer:** the Actor draw, a 4003, the guide callbacks, an AI and
  `CPlane::Init`'s last draw.

Core files the callbacks that draw, on the level's one event manager, and delivers
them with the contract's draws and requeues:
- **4003** takes one draw and re-files at now + 3 + r/65536. It sets
  `+0x110` when the camera is strictly within 50 units.
- **A polling AI** (inactive or switched off) draws and files 3003 two to four
  seconds out; the 3003 files 3000 for the next frame.
- **An active AI with no target** takes Update's idle arm: one draw, then 1.5 to
  2.5 s when `+0x110` is set, else 3 to 5 s. With a target the delay is 0.5 to
  1.5 s.
- **The Warehouse's 3001** draws and re-files one to two seconds out.
- **Turret fire control** draws and re-files within 0.1 s, and stops once the
  turret is dying.
- **The tank squads** re-file 4000, 4001 and 4002 with one draw each. While the
  member follows a waypoint, 4002 re-files for the next frame without a draw.

Ground vehicles' mechanics state now exists from construction, with the full-guide
phase set by the Actor draw. It advances every frame, active or not. A unit moves
first on the frame after its construction, so a spawned tank no longer moves on
its spawn frame. A spawned drone keeps its exit controller, and its AI loop after
the exit is not filed yet.

Schema 52 carries the callbacks' state. The definition identity gains format 9,
the pine count, which the manifest decoder now validates (1,481).

Tests:
- `Level100UnitCallbackTests` (7 cases) builds one-row worlds from the
  materialized definitions and pins every draw and due time: a building, the
  inactive Tank Factory's poll, a turret, the Warehouse, a Target Tank's squad
  draws and Move phase, the camera rule and the snapshot restore.
- `Level100BattleEngineRefreshTests` pins the whole load draw sequence around
  the Battle Engine's refreshes.

Eleven mutations were killed and restored byte-identical
(`local-data/test-runs/construction-order-20260926/mutation-kills/`).

The new draws moved the test autopilot's timing enough to expose a gap in it,
not in Core. In the first drone wave the third drone was still unflagged as an
objective when the second died over the sea, so the autopilot had nothing to
shoot. Its `Hold` then morphed to walker and lost the level to water. `Hold` now
follows the sorties' existing rule: never come down over water, and head for the
last dry ground.

Core passes 1,529 and the Client suite 912 with the two known skips. The explicit
ferry sweep passes 6/6 over its twenty perturbations; no run drowns. One of its
assertions was too strong and is weakened: it claimed the two hand-off arms
separate only when the adverse ferry hands off above the 20 m tier. On this route
both arms hand off at 19.3 m, and they still separate twelve ticks later through
the driver's re-launch, which the same clearance term governs. Re-pinned:
- `first-flight.v1.json` replays to trace `2564e760…` and state `66cab706…`.
- The in-process smoke and its validator: state `afc552db…`.
- The canonical-hash fingerprints.

The headless Godot smoke records inputs equal to the previous tape's (tape
`85338db6…`, trace `3971f7fe…`), and the C# replayer reproduces it twice.

The chain autopilot now wins through the six-kill branch at tick 5,901 with hull
10,650. The cold-start route's won tape is 7,759 ticks (trace `a65fb9ec…`, state
`40493662…`), on the abort branch after three kills, and it replays twice.

Open, each also listed in PARITY.md:
- Core runs every script's init at construction, so the Tank Factory's first
  `SpawnThing` takes its squad's five draws before frame 1; retail runs that init
  on frame 2.
- Core has no pan camera, so `+0x110` uses the Battle Engine's position, which
  is only exact for the first-person camera.
- The drones' AI loop after their exit is not filed.
- The squads' target branch is not modelled.
- The Air Trainer's `+0x284` draw is taken but the value is unused.

Logs: `.worktrees/godot-editor-48-20260919/local-data/test-runs/construction-order-20260926/`.

### Launch basis for every round — September 26

The burst spawner builds each round's basis as orientation × launch angle ×
scatter, every factor an `FMatrix(yaw, pitch, 0)` (the RE lane's burst-spawner
contract, steps 5-7, and its 36-case Euler-constructor control, commit
`84193799`). Before this change Core added the scatter to the aim as angles, which
matches the product only when the aim is level, and gave modes without launch-angle
entries no launch angle at all. Three corrections:
- **Default launch angle.** A mode without `CWeaponLaunchAngle` entries uses
  `0x004f8140(0, 1, 0)`: a pitch of float(2π/4096). Retail's z axis points down,
  so every Pulse, Vulcan and drone round now leaves 1,534 µrad nose-down of its aim.
- **Matrix composition.** Player rounds and the drones' rounds now compose aim,
  angle and scatter through the one function the Missile Pod already uses. The
  drones' rounds keep pitch nose-up internally, so their aim and wiggle pitch
  convert to retail's nose-down pitch at the boundary. Before, the drones'
  scatter and wiggle pitch had the opposite sign to retail's.
- **Pulse scatter.** The Pulse Cannon Pod's level-0 mode, `Mech Pulse Cannon
  Charged` @`0x134e3` in `data/default physics.dat` (`e1fb3ded…`), has
  `CWeaponInaccuracy` 0; its first node's payload is `00000000`. Core scattered
  its bolts by 0.5° (`0x3c0efa35`), which belongs to `Mech Pulse Cannon`
  @`0x13473`, the Small bolt's mode, and the pod never selects that mode. The two
  scatter draws are still taken and now scale to nothing.

`SimulationTests.PlayerProjectilesConsumeReleasedScatterInRetailDrawOrder` now
checks every Pulse and Vulcan heading against a double-precision matrix
product. Four mutations were killed and restored byte-identical
(`local-data/test-runs/launch-basis-20260926/mutation-kills/`): no default
pitch, the Small bolt's scatter restored, and the drones' pitch sign flipped at
either end of the composition.

Core passes 1,522 and the Client suite 912 with the two known skips.
`first-flight.v1.json` and the canonical fingerprints do not move, because they
fire nothing. The smoke fires the Pulse four times, so its pins move: the
in-process fingerprints and the smoke validator now read state `aaf7bba9…`. The
headless Godot smoke records a tape whose inputs equal the previous tape's;
only its expected hashes differ (tape `0923ca41…`, trace `e3ed327f…`). The C#
replayer reproduces it twice.

The chain autopilot still wins on the final wave's abort branch, now after one
kill at tick 5,543 with hull 7,950. The cold-start route records a won tape of
7,347 ticks (trace `25332a14…`, state `6dd3c819…`), also on the abort branch
with two kills, and it replays twice. Logs:
`.worktrees/godot-editor-48-20260919/local-data/test-runs/launch-basis-20260926/`.

### Jet Missile Pod, locks and seeking rounds — September 26

The jet's second weapon did nothing in the rebuild: Core refused to invent a
shot. It now fires as retail's records and the RE lane's contracts describe.
The records are `data/default physics.dat` (SHA-256 `e1fb3ded…`): `Weapon
"Missile Pod"` @`0x17746`, its modes `Mech Micro Missile Launcher` @`0x13e49`
and `… Salvo` @`0x14093`, `Round "Micro Missile"` @`0x8e74` and `Explosion
"Micro Missile Hit"` @`0x3a59`. The contracts, on the RE branch, are the weapon
stores and charge law (`05d5ed86`), the burst spawner's launch sequence, launch
angle and Euler matrices (`d5ad5c9a`, `056c56d7`, `84193799`) and the final-wave
contract's lock, seeking-round and round-lifetime sections (`35056883`,
`c477f220`). The lock code follows `BattleEngine.cpp:586-1010`.

- **Charge and Fire.** Holding charge adds 8 per call from 0, so the 13th call
  reaches 104: level 1, the salvo, and full. Fire takes the level and mode before
  its reload check, so a press during a salvo's 0.8 s reload switches the rest of
  that burst to the launcher's five. The reload runs from the burst's start.
- **Burst.** The first missile leaves at once and event 5001 is filed at now +
  `CWeaponBurstDelay` on the level event manager; each delivery launches one more
  until the mode's burst size (5 × 0.1 s, or 10 × 0.05 s).
- **Each missile, in retail order.** Store 3 pays 1 (`WeaponFired`); one launch
  sound per event; the launch-sequence and launch-angle counters advance (both
  start at −1); two scatter draws; `GetCurrentTarget`; `FireLock`; the round's
  Init draw; the recoil's three shake draws (power 0.01).
- **Launch direction.** It is the launch orientation × `FMatrix(angle yaw, angle
  pitch, 0)` × the scatter matrix, composed as retail's matrices. Retail's z axis
  points down, so Core's nose-down player pitch is retail's own; the shared
  seeking law measures pitch nose-up, and the Battle Engine's rounds convert.
- **Locks.** `HandleLocks` runs every Move before movement. It returns while the
  jet's pod is mid-burst. It prunes by the current mode's deflection cone,
  acquires the crosshair unit (or the outer-sphere probe's) inside 100 m and the
  cone, and starts a lock that finishes after 0.2 s. The pod's lock unit
  `0x000e8400` takes planes, ground vehicles and cannons, never buildings or
  features.
- **Flight.** Each Move takes two wiggle draws. After the 0.05 s seek delay the
  missile steers toward its bound target's centre, 0.0349 rad per step, inside a
  0.785 rad cone. Leaving the cone, the target dying, a hit and the end of life
  each release the target, and every release calls `LockHit`.
- **Life's end.** At the end of its 8 s span the missile bursts in the air, as
  `CRoundExplode` rounds do at event 4000. A contact makes the same `Micro
  Missile Hit` effect and sound; direct damage is 1.5 plus the explosion's 0.5.

Presentation follows the records.
- **The missile** is `Micro Missile Effect`'s sprite layer (`Blue Spark 2.tga`,
  radius 0.1). Its `Pulsate` modifier, its `f_micromissile` mesh layer and its
  `Blue Trail` (`Blue Beam.tga`, not retained) are not drawn.
- **The impact** is `Blue Explosion`'s `Flash Small` (`sun2.tga`, radius 0.7 to
  0 over four turns) and `Blast Anim Sprite Medium` (`alparticle5.tga`, cells
  0-8 played once at 0.8 cells a turn, radius 0.5 to 1, cyan to black). The
  ten-particle `Blue Debris Emitter Medium` is not drawn.
- **Sound.** `BE Micro Missile Fire` (sounds.sfx record 34) plays once per burst
  event, and `Explosion Medium` (record 104) plays per impact or air burst.

No Godot run fires the pod yet, so nobody has seen or heard these effects.

Tests:
- `Level100MissilePodTests` (6 cases) pins the charge steps and the salvo, the
  Fire quirk and reload, the counters, the lock parameters, the lock-unit
  classes and the charge losses.
- `SimulationTests.MissilePodLauncher_SpawnsFiveMissilesOnTheBurstEventsAlongTheirSlots`
  pins the filed 5001 time, five missiles two frames apart, store 3 at 195, the
  pod state, every heading against a double-precision matrix product, and five
  air bursts.
- `SimulationTests.MissilePod_LocksAStaticTargetAndItsMissilesSeekItThenReleaseTheLock`
  locks a script-enemy static target at the firing range. The lock finishes
  0.2 s after it starts, all five missiles bind and strike the target, and the
  fired set empties again.

Eleven mutations were each killed and restored byte-identical
(`local-data/test-runs/missile-pod-20260926/mutation-kills/`).

Core passes 1,522; the Client suite passes 912 with the two known skips, once
the two new impact sprites are registered with their shipped records. Schema 51
is selected only when the pod or a seeking round differs from construction, so
no route that leaves the pod alone changes its bytes. The headless Godot smoke
records the same tape as the previous change (`7c7ca639…`), and the C# replayer
reproduces it twice (trace `248b326a…`, state `89b9ada6…`). The cold-start won
tape is byte-identical too (`c5050fa0…`, 7,813 ticks, trace `613489cc…`, state
`278af3f3…`). No pin moved. Logs:
`.worktrees/godot-editor-48-20260919/local-data/test-runs/missile-pod-20260926/`.

### Weapon stores, recoil shake and the round's Init draw — September 26

The rebuild charged every walker Pulse shot 30 milli-units of walker energy
(and the Twin Vulcan 15), a placeholder the code itself called unaccepted. Retail
spends no energy on weapons. The RE lane's contract
(`reverse-engineering/game-mechanics/battle-engine-weapon-stores.md` on the RE
branch, commit `05d5ed86`, with the GPL part bodies) gives the Aquila's six stores from
`data/battle engine configurations.dat` offset `0x35f`: ammo 2000 (both Vulcans),
ammo 100, heat 150 (Pulse Cannon Pod), ammo 200 (Missile Pod), heat 100, heat
100. Ammo starts full and heat empty; a burst event's `WeaponFired` spends once,
before its volley (jet ammo −consumption, walker heat +consumption, jet heat
+consumption − 1); every Move cools each heat store by the integer
`kWeaponCoolRate` 1 and clears overheat strictly below three quarters of capacity;
a charged heat shot costs nothing; charging a heat weapon adds its consumption
per call and, at capacity, overheats and forces a Fire; `ChangeWeapon` skips an
ammo weapon that cannot pay. A walker heat shot or charge clears
`mShieldsRecharging`, which halves that update's ground recharge — the arm the
rebuild had left out only because stores were unmodelled.

The burst spawner's order (the RE lane's Q12 answer and correction, commits
`d5ad5c9a` and `35056883`) adds four things per round of a Battle Engine weapon:
`GetCurrentTarget` (its cursor zeroed by each successful `Fire`), `FireLock` for
the current weapon, the round's `CRound::Init` → `CActor::Init` draw, and
`RecoilWeapon`'s `AddShockShake(CWeaponPower)`, three draws when the power is at
least 0.001 (Pulse Charged 0.03, Charged 2 0.05; both Vulcans 0).
`CBattleEngine::Damage` ends with `AddShockShake` of the life lost times 0.125,
halved while shields remain, capped at 0.25. The drones' rounds take their
Actor Init draw too, so every spawned round costs three launch draws. The shake
offsets, phase and decay are kept exactly; applying them to the Battle Engine's
orientation (`UpdateRotation`) is not done yet.

`Level100PlayerStoresTests` (12 cases) pins the stores, spend, refusal and cue
stamps, cooling and the overheat clear, the charged shot, the charge overheat,
the store-gated weapon change, the shake draws and decay, and the damage amount.
Six mutations were each killed and restored byte-identical
(`local-data/test-runs/stores-shake-20260926/mutation-kills/`). The scatter-order
test now counts six draws per Pulse release and three per bullet.

With these draws the re-rolled final wave now ends on retail's abort branch in
both driven routes. The chain autopilot wins at tick 5,982 after two kills; the
cold-start route wins after none, taking the abort at the first sub-40 % poll.
The RE contract classes the six-kill, no-abort result both tests demanded as a
driver expectation, so they now assert the released final-wave contract
(`Level100FinalWaveContract`: six kills with objective 4 complete, or the abort
with objective 4 failed and every surviving drone switched to AI off and
friendly). `ColdStart_PlaysLevel100ThroughThePlayerInputSurface`, failing since
September 12, passes on that contract. Core passes all 1,508; the Client suite
passes 912 with the two known skips. First-flight and the canonical-hash
fingerprints do not move (no shot or hit). The in-process smoke and validator
re-pin to state `89b9ada6…`; the headless Godot smoke records a tape whose inputs
equal the September 25 tape's (tape `7c7ca639…`, trace `248b326a…`), and the C#
replayer reproduces it twice. The cold-start won tape is 7,813 ticks, trace
`613489cc…`, state `278af3f3…`, replayed twice. Logs:
`.worktrees/godot-editor-48-20260919/local-data/test-runs/stores-shake-20260926/`.

### Battle Engine crosshair and auto-aim refresh — September 26

Retail's player Battle Engine files two refresh events for itself that the
rebuild never had, and both draw from the one gameplay stream: event 6002
(`CALC_UNIT_OVER_CROSSHAIR`) and event 6003 (`HANDLE_AUTO_AIM`). The RE lane's
static contract ([level100-final-drone-wave.md](reverse-engineering/game-mechanics/level100-final-drone-wave.md),
"Crosshair and auto-aim refresh", commit `f23dcc28`, and its due-time answer
from the pristine `74154bfa…` bytes) gives: `CBattleEngine::Init` takes one draw
and files 6002, then `HandleAutoAim(NULL)` takes one draw and files 6003; each
delivery re-files the same way with one draw; 6002's due time is
`(sample × 0x364ccccd + mTime) + 0.1f` and 6003's `(sample × 0x35cccccd + mTime) + 0.2f`.
Core now files both on the level's one event manager (the scheduler the
aircraft already used, now created with the Battle Engine), under a reserved
listener identity, so insertion order between them and the aircraft callbacks
is the delivery order.

Each 6002 delivery runs `CalcUnitOverCrossHair`'s event path: it clears both
crosshair readers, casts the 1,000-unit view line through the shared contact
query (terrain first, a thing only when not farther, dying non-buildings
skipped), retains the line report and returns the struck unit when the current
weapon's `GetActualMaxRange` exceeds the hit distance (Pulse 210 or 140,
Vulcans 60, Missile Pod 100, from the RE lane's Q14 answer). The launch
correction (`GetLaunchPosition`) now reads that retained distance along the
current view line, as retail does, instead of the rebuild's former per-shot
fresh trace. The auto-aim candidate search is not implemented yet, so its
offsets stay zero; its draw and requeue are exact. The Battle Engine's Init
draws follow the Air Trainer's Actor Init draw until the RE lane's first-flush
order places them. Core has no camera, so the view line starts at the Battle
Engine's position along its facing, as the launch correction always assumed.

`Level100BattleEngineRefreshTests` (22 cases) pins the due-time arithmetic bit
for bit, the range and side-gate tables, the construction order and draws, the
one-of-each queue invariant over 200 frames, the crosshair unit and report
against the Control Tower, features occluding without becoming units, and the
launch correction's use of the retained distance (a fresh trace would keep the
facing). Core passes except the known cold-start six-kill expectation; the
Client suite passes 912 with the two known skips.

The new draws move every Level 100 hash. Re-pinned with this change:
`first-flight.v1.json` now replays to trace `a59321dc…` / state `63b241d6…`;
the in-process 2,148-step smoke and the smoke validator to state `a8c2209d…`;
the canonical-hash and older-definition fingerprints in `SimulationTests`,
`HeadlessApplicationTests` and `InteractiveSessionTests`; schema 49 where
targeting state exists. The headless Godot smoke records a tape whose seed,
duration and every input span equal the September 25 tape's (`89ca7b4b…`); only
its embedded expected hashes differ (tape `43d63bd0…`, trace `33ebdaee…`, state
`a8c2209d…`), and the C# replayer reproduces it twice with no divergence. The
chain autopilot still wins with six kills, now at tick 5,803 with hull 12,500.
The cold-start run records a won tape of 7,374 ticks (trace `ca2209e7…`, state
`0a8e7972…`), still through the abort branch, which replays twice. The ferry
sweep's twenty runs all still win without water loss, but the re-rolled final
wave now brings every ferry in 13.9 m up, below the 20 m tier where the two
hand-off rules differ. The route-level adverse control therefore compares
identical runs, so the rule itself is now pinned directly
(`Level100ZoneHandoffTests`, in the default Core gate). The divergence
check asserts that the arms separate exactly when an adverse hand-off exceeds
the tier. Logs: `.worktrees/godot-editor-48-20260919/local-data/test-runs/be-refresh-20260926/`.

### Terrain contact sweep pruning — September 25

The recorded launch hitch came from the terrain half of
`Level100ContactMechanics.TrySweepRoundWithTerrain`: a scratch benchmark at the
smoke tape's four firing ticks timed the whole crosshair sweep at 78–82 ms, the
terrain search alone at the same, and the 34 actors' mesh sweep at 0.01 ms. The
terrain search bisects the ray down to one part per million and prunes only
spans whose ends share a terrain cell, so a 1,000-unit ray toward the horizon
walks every cell.

It now also skips any span whose lowest point, plus the contact radius, clears
the highest ground its box can sample. Each sample interpolates between the four
samples of its own tile's cell, the elevation conversion is monotonic and
interpolation along the ray is monotonic, so every test inside such a span would
report no contact; `Level100Terrain` keeps a min/max pyramid over the 512 x 512
cells to bound them. `Level100TerrainSweepPruningTests` compares 400
deterministic random rays (radii 0–2.5 m, lengths to 1,000 units, 247
contacts, some starting past the map edge) with and without the pruning: every
contact record is identical, in 17 ms against 36,339 ms.

At the four firing ticks the crosshair sweep now takes **0.06 ms**. The 2,148-tick
smoke replay (Release, warm) has **no tick over 1 ms**: median 0.0745 ms, p99
0.36 ms, maximum 0.48 ms, and about 28 µs per live projectile per tick. The
smoke tape and `first-flight.v1.json` still replay to trace `a4e6673b…` / state
`53c1cc64…` and `0872e009…` / `69bd64ac…`; the Core suite (1,471 of 1,472, the
known cold-start route) now runs in 1 m 32 s instead of 7 m 55 s and the Client
suite (912 passed) in 16 s. Logs:
`.worktrees/godot-editor-48-20260919/local-data/test-runs/reticle-sweep-profile-20260925/`,
`sim-benchmark-20260925/after-terrain-prune.log` and
`terrain-prune-suites-20260925-231708/`.

### Level 100 won tape — September 25

The cold-start Level 100 run (frontend by clicks, then the chain autopilot on
the client's own `InteractiveSession`) now records its command tape from tick 0,
as the Godot host's `--record-tape` does. `Level100ColdStartTests.
ColdStart_RecordsATapeThatReplaysDeterministicallyToAWin` builds that tape and
replays it twice through `ReplayRunner`; both replays reproduce the live trace
and final-state hashes and end with the mission **Won**. The tape covers
**8,141 ticks**, trace `885ae25b…`, final state `0a656b1c…`; the C# headless CLI
(`--repeat 2`) reproduces both with no divergence
(`.worktrees/godot-editor-48-20260919/local-data/test-runs/level100-won-tape-20260925-225339/`).

The win goes through retail's designed abort branch: the final drone wave aborts
after one kill once the player's life falls below 40 %, and `LevelWon()` still
follows. The RE lane's contract
([level100-final-drone-wave.md](reverse-engineering/game-mechanics/level100-final-drone-wave.md))
shows the rebuild lacks two retail helps in that wave, the four friendly turrets
that Help Player activates and the jet Missile Pod, and that every base-world
Building and Cannon draws shared RNG from level start. Until those land, this
tape is a deterministic, won run of the current rebuild, not a retail-parity
playthrough. `ColdStart_PlaysLevel100ThroughThePlayerInputSurface` still fails
on its six-kill expectation, which the contract classes as a driver
expectation, not a retail invariant.

### Return to all-code C# — September 25

David directed that the project be 100% C# and built in code. The rebuild's
code, tests, tools, C# headless replayer and docs were restored to `b0b9c5e7`,
the last commit before GDScript entered the rebuild (its child `29727e2b`
began the editor-scene conversion). Separate commits then rebuilt the pause
menu's tree in code, carried the stricter AYA admission into the C# decoder,
refused two impossible inputs (an Int32.MaxValue emitter lifetime and an
invalid compositor level) and restored the smoke validator's `53c1cc64` pin.
The 244 GDScript files, their parity runners and oracles, the simulation
bridge, the editor scenes and `tools/godot_compat` are deleted; Git keeps
them. A read-only review of every commit in `b0b9c5e7..37cf89b3` found the
simulation unchanged and no other evidenced behavior to carry.

Executed at the restored state:
- The solution and Godot project build with 0 warnings and 0 errors.
- `npm run test:rebuild-client`: **912 passed**, 2 existing skips.
- `npm run test:rebuild-core`: **1,469 of 1,470**. The one failure is
  `Level100ColdStartTests.ColdStart_PlaysLevel100ThroughThePlayerInputSurface`,
  failing since the September 12 aircraft work (see below); the RE lane's
  contract identifies two missing retail helps in its final wave.
- The C# headless replayer reproduces the baseline smoke tape (`89ca7b4b…`,
  2,148 ticks, trace `a4e6673b…`, state `53c1cc64…`) and `first-flight.v1.json`
  (838 ticks, trace `0872e009…`, state `69bd64ac…`), twice each.
- The headless smoke records the identical tape (`89ca7b4b…`).
- `PauseSceneChecks` **56 passed** headless; offscreen, the code-built root
  and confirmation renders are pixel-identical to the `b0b9c5e7` scene's.
- `AyaTextureChecks` **801 checks**, 0 failures, 0 unexpected diagnostics; all
  142 cases match the September 25 production decoder's report, including the
  decoded bytes of all 51 actual textures.

Capture. godot-offscreen Movie Maker at 60 fps and 1280x720 recorded startup,
menus, Level 100, a retry and the return to the main menu, exactly as the
September 25 baseline (`migration-baseline-20260925/run-2`, from `d5e002d0`).
The restored build recorded the identical tape and state, and its WAV is
byte-identical to the baseline's (`932b25a9…`). All 15,334 frames are identical
to a capture of `b0b9c5e7` itself. Against the baseline, frames 0–13,179
(startup, menus and the whole first Level 100 session) are identical; the
2,154 frames from 13,180 differ for two evidenced reasons:
- **Pines after the retry (frames 13,180–15,330).** The baseline shows no pine
  trees in the retry session, although the first session draws them and a
  retry builds a fresh world. A capture of `29b40721` (September 19 C# with the
  `29727e2b` scene-imported world) reproduces the loss and matches the
  baseline on 15,330 frames, so the scene import introduced it; the all-code
  world builds its pines on every construction. This restores the earlier
  behavior rather than inventing one.
- **The last three frames (15,331–15,333).** They are drawn after the smoke
  completes: `RequestQuit` freezes every child node and the root keeps
  rendering only while real audio retires, which is why headless runs (dummy
  audio) end at frame 15,330. Instrumented runs, headless and offscreen with
  real audio, show the frontend's last update in both builds is on the
  Loading screen with identical clocks and the title-logo reflection hidden.
  A capture of `b0b9c5e7` changed only to add its frontend ahead of the audio
  node, as the scene host orders them (`order-experiment-20260925-223458`),
  differs from the unmodified capture in exactly these three frames, so they
  depend on scene composition. It still does not show the baseline's logo
  sheen, and the scene-based `29b40721` does, so the scene host's exact render
  path for these frames is not isolated. **Open question:** which frontend state
  does each build hold when Movie Maker draws them? Cheapest falsifier: log the
  screen and reflection visibility per Movie Maker frame in both builds.
  Normal play never quits here, so the frames are a capture-harness artifact.

Other differences: none. Logs: `local-data/test-runs/csharp-allcode-lane-20260925-221042/`,
`csharp-pre-b0b9c5e7/`, `csharp-scenes-29b40721/`, `order-experiment-20260925-223458/`,
`feback-trace-20260925-222356/`
and the worktree's `local-data/test-runs/csharp-allcode-20260925-215316/`.

### Lane baseline — September 25

Each lane was built and checked in its own checkout on Linux: Godot 4.8 dev6 .NET
(`godot48-mono`), with the standard edition for the GDScript-only gates. Every Godot
run was headless with Dummy audio; no window opened. Logs are in canonical
`local-data/test-runs/lane-baseline-20260925-H8dhmW/`; rebuild-owned runs are under
`.worktrees/godot-editor-48-20260919/local-data/test-runs/lane-baseline-*`.

- **Companion (`main` `996d6109`).** `npm run build` had zero warnings/errors.
  `npm test` ran the native Save Lab with **0 failures**, **6/6** publication races and
  **12/12** launcher tests. `test:save-lab` passed **24/24**, `test:godot-host` **12 + 20**,
  plus `test:docs` and `test:safety`. Main's rebuild also built with its Level 100 import verified.
- **Reverse engineering.** Before its merge, the lane passed `test:docs`, `test:safety`,
  the cohort framework (**93/93**, `python -m unittest tools.ghidra_cohort_framework_tests`),
  `test:save-lab` and its 4.7.2 .NET companion build. Its own commits never touched Godot
  code; the 4.7.2 selection came from its merge base. After merging `main` (`eeb4d1f6`),
  the same checks plus `npm run build` and `npm test` passed on 4.8 dev6 .NET, and the
  lane merged into `main` (`ed7f5332`).
- **Rebuild.** Checkpoint `9559f1f4` built with zero warnings/errors and passed
  **24,177** world checks, the headless smoke (tape SHA-256 `89ca7b4b…`, state
  `53c1cc64…`) and two replays with trace `a4e6673b…` verified. Two gates failed for
  known causes, fixed in `94223492` and `172d6ad7`. The `particle-effects` parity group
  failed 2 cases because the C# oracle formatted ±∞ with the host culture (`∞` under
  `en_US.UTF-8`) while the GDScript port writes invariant `Infinity`; every earlier
  receipt recorded an invariant oracle culture, which the oracle now pins. The Client
  suite failed 1 of 912 because `Level100HudBlendEvidenceTests` still read
  `FirstFlightHud.cs` for the flash lifetime that `4b519d6f` moved to
  `first_flight_hud.gd`; the guard now reads the native owner.
- **Rebuild after merging `main` (`23c8f8c8`).** Build zero warnings/errors; **24,190**
  world checks (main adds 13 import-ownership checks); smoke tape and state hashes and
  both replays unchanged; parity **29/29** groups; Client **910** passed with the two
  known skips; companion `npm test`, `test:docs` and `test:safety` passed. A headless
  sweep of **77** component scene checks, run in their documented `.NET`-reference and
  standard-engine forms, had **73** clean passes. `PauseSceneChecks` and
  `WorldPresentationChecks` logged their documented engine errors (deliberate zlib
  fixtures, extreme-coordinate `look_at`). `CareerNameSceneChecks` logged one
  "resources still in use at exit" line in 1 of 7 runs.
  `AyaTextureChecks`, added unvalidated in `5c8276ce`, fails **15 of 1,206**
  checks, all synthetic malformed inputs: 12 undeclared `file_access_memory.cpp`
  short-read diagnostics; 2 short-pixel cases whose image bytes differ between the
  retained C# decoder and `retail_aya_texture.gd`, both reading past a 129-byte DDS;
  and an empty second AYA record that the harness's own oracle refuses. All 47 real
  import uses, the cursor and fonts decode identically. Settling that malformed-input
  contract is the lane's unfinished step, so the rebuild lane is not merged.

Not run: the broad Core suite, because no lane or merge changed `OnslaughtRebuild.Core`,
its tests or their shared inputs since `25db5b23`. Also not run: rendered or pixel
captures, editor-mode harnesses, live input or audio, and Windows.

### AYA malformed-input contract — September 25

`AyaTextureChecks` now passes **1,289 checks over 142 cases** with **0 unexpected
diagnostics**; all 47 import uses, the cursor and both fonts still decode byte-identically
in the reference, native and facade paths. The pinned loader
(`modules/dds/texture_loader_dds.cpp` at `8898c2b3d`) fills a short DDS surface from
uninitialized memory, which is why the two short-pixel images differed from run to run.
`retail_aya_texture.gd` now refuses any payload shorter than that loader's read,
computed for the admitted layouts including its width-remainder padding, mip chains,
cubemap faces and volume slices. Every such refusal must coincide with an actual
`file_access_memory.cpp` short read in the unchanged reference, and complete
odd-width, mip-chain, six-face and two-slice counterparts must decode identically.
The empty-second-record control now contains a real empty zlib member: the pinned
.NET compressor wrote nothing for an empty payload, so the old fixture tested a
zero-length record, now its own refused case. The truncated-width case moved from
`decode-before-dimension`, which again tests decode-then-dimension order with a
complete payload. Short-read diagnostics are admitted only in the reference phase.
The rebuild then built with zero warnings/errors and a verified Level 100 import,
passed 77/77 headless scene checks, **24,190** world checks, **910** Client tests
(2 known skips), and kept the smoke tape (`89ca7b4b…`) and replayed state
(`53c1cc64…`). Logs: `.worktrees/godot-editor-48-20260919/local-data/test-runs/aya-contract-afwwC2/`.

### Simulation language measurement — September 25

The language rule of the time required a recorded measurement before any subsystem
stayed in C#. A scratch Release benchmark (`net8.0`, tiered PGO) replayed the 2,148-tick
Level 100 smoke tape through `Simulation.Step`, reproduced final state `53c1cc64…`,
and timed the warm last of six replays. The typical tick is cheap (median **0.08 ms**,
p95 **0.11 ms**), but p99 is **4.1–7.8 ms** and the maximum **98–226 ms**. Canonical
serialization plus SHA-256 adds **0.11 ms** per tick for 50,536 bytes. An instrumented
scratch copy of `Simulation.Step` attributes **380–414 ms** of the ~0.7 s run to
`TryFire`: four launches of about **95–100 ms**, all inside `ReticleAdjustedLaunchAngles`,
whose `TrySweepRoundWithTerrain` sweeps a 1,000-unit ray against terrain and every
active actor's contact geometry. `UpdateProjectiles` costs **146–153 ms**, about 1 ms
per live projectile per tick. Every other phase totals at most 26 ms for the run; the
typical tick is mostly snapshot creation.

Matched kernels on identical inputs produced identical results in both languages.
The terrain fixed-point lookup costs **6.0 ns** in C# and **410 ns** in GDScript (68x).
PC24 multiply-and-add costs **12.1 ns** in C#, **403 ns** in the current GDScript port
(33x), **122 ns** with an allocation-free helper (10x) and **24 ns** fully inlined; the
last form is not maintainable across the Core. Applying the measured 10–68x to the
measured C# phases gives a GDScript Level 100 tick of roughly 1–5 ms when idle,
3–7 s per launch and 10–70 ms per live projectile per tick. RE could not quickly
establish the largest retail battle's unit count, so the stress case is 10x Level 100's
45–48 actors. The Level 100 Core cannot construct it without mission-level changes;
scaling the measured per-actor work puts even the idle GDScript tick at 10–56 ms.

**Decision:** superseded the same evening. David directed C# only for the whole
repository (`AGENTS.md`), so no subsystem needs a measured exception. The launch and
flight costs above were the terrain contact sweep; the pruning recorded in "Terrain
contact sweep pruning — September 25" removed them without changing any result. Sources and logs:
`.worktrees/godot-editor-48-20260919/local-data/test-runs/sim-benchmark-20260925/`.

### September 19 production scene migration

The supported Linux build passed with zero warnings/errors and explicitly
imported the private Level 100 scene. No Core simulation, snapshot format,
gameplay constant or input tape changed in this presentation migration.
Executed focused selections passed **112 Core replay/camera/headless/recorder/
scheduler tests**, **101 world Client tests** (one existing captured-water skip),
**114 HUD tests**, **319 frontend tests** (one existing font-capture skip),
**53 startup tests**, **8 pause tests**, and **24 Save Lab/backend gate tests**.
These selections overlap; they are not a broad-suite census or new retail parity
receipt. The rebuild launcher suite now passes **20** cases, including explicit
world import and stripping diagnostic terrain probes only from the import process.

Actual Godot scene checks passed for frontend, startup, HUD and pause, including
authored layout round-trips, frozen editor state, production asset binding and
preventing private pixels from being serialized into public UI scenes. The world
check passed **23,864 assertions**: saved geometry and texture bytes before
runtime binding, no second world construction, selected snapshot poses, separate
retry materials/terrain, pointer preservation and unchanged simulation hashes.
The import receipt was verified after those checks. Logs live in this branch's
`local-data/editor-48/checks/`, `local-data/hud-editor/`, `local-data/pause-*`
and `local-data/frontend-render-20260919/`; source checks live beside their
production scenes under `rebuild/OnslaughtRebuild.Godot/Scenes/`.

For the world check, after the supported build:

```bash
python rebuild/tools/first_flight.py run --no-build --no-prepare --timeout 90 \
  --engine-arg=--headless --engine-arg=--audio-driver --engine-arg=Dummy \
  --engine-arg=res://Scenes/World/WorldSceneChecks.tscn
```

The same launch form accepts `res://Scenes/Hud/Tests/HudSceneChecks.tscn` or
`res://Scenes/Pause/Tests/PauseSceneChecks.tscn`. For the frontend and startup,
use `--engine-arg=--script` followed by
`--engine-arg=res://Scenes/Frontend/Tests/frontend_scene_checks.gd` or
`--engine-arg=res://Scenes/Frontend/Tests/startup_scene_checks.gd`.
Those two scripts also accept `--engine-arg=--editor` for tool-mode checks;
the HUD has a separate `res://Scenes/Hud/Tests/hud_editor_checks.gd` editor script.
Each launcher invocation owns fresh local output and a separate user profile.
Use an available desktop or a properly isolated display for rendered checks;
never reuse the user's desktop implicitly.

Isolated software-rendered checks inspected main menu, career, level selection,
briefing, configuration, loading, options, startup splash, HUD at two sizes and
pause/confirmation. An actual isolated editor opened the private Level 100 scene,
passed eight hierarchy/safety assertions and captured its native 3D viewport.
Runtime scene-check logs are clean. The `--editor --script` harness reports
progress-dialog/current-window warnings and teardown RID/ObjectDB diagnostics;
the HUD harness's teardown counts also occur with an empty editor-script control.
These are recorded limitations, not a claim of clean interactive editor shutdown.
No software capture proves normal GPU performance, physical input or audible audio.

The subsequent GDScript pause conversion passed **1,047 model transitions** against
the retained C# model, **115 standard-engine scene checks**, **91 editor-mode
checks**, and **94 checks through the temporary managed host adapter**. The
seven selected Client checks passed, including unchanged pause/resume tape,
trace and final-hash equality and neutral-input handling after resume. The
scene script is `res://Scenes/Pause/Tests/pause_scene_checks.gd`; run it with the
standard pinned engine's `--headless --audio-driver Dummy --script` options and
the rebuild project path, adding `--editor` for the frozen preview checks.
The isolated software render passed **120 checks**; its root and confirmation
captures each differed from the previous C# scene capture by **zero pixels**.
Checks cover authored rows/hit regions, input gating, private texture packing,
asset bytes and bitmap-font measurements, including raw UTF-16 code units where
embedded NUL cannot cross the ordinary Godot string bridge intact. Deliberately
corrupt compressed fixtures produce two expected native zlib errors. The editor
harness also reports scan-abort and teardown RID/ObjectDB diagnostics; this is
not a clean interactive-editor shutdown claim. Evidence is in the owned
`local-data/test-runs/gdscript-pause-94vdiqq3/` directory. Whole-game simulation
and the remaining frontend/HUD/world host still use C# during conversion. The
supported headless smoke also passed after reimporting the worktree's private
world scene: `local-data/first-flight/smoke-izxr9__1/` retains the same 2,148-step
`53c1cc64…` hash, retry and return-to-menu behavior, with mission **Running**.

The next GDScript foundation gate passed **970 JSON cases**, **7,134 startup
schedule samples**, **269 chunk-reader operations across 52 scenarios**, and
**370 scheduler operations across 31 scenarios**, including **362 snapshots**.
The numerical/native-Euler and pause comparisons also passed in that run.
JSON comparisons include exact int64 limits, escaped duplicates, Unicode/NUL,
depth and malformed syntax, varied decimal doubles and exact halfway cases;
they measure full string admission as well as explicit parse-stage boundaries,
not merely lazy `JsonDocument.Parse` acceptance. Scheduler checks include
callback interruption, reset/restore, pool exhaustion, wrap and mutation before
failure. The parser modules and scheduler remain foundations for future live
consumer ports; this receipt does not replace whole-game replay acceptance.
Logs, unchanged C# expected words and reports are in the owned
`local-data/test-runs/gdscript-parity-pfhk60nx/` directory. All six standard-engine
check logs completed without errors; seven launcher checks passed.
The existing C# scheduler/chunk selection also passed **51 tests**; its log is
`local-data/test-runs/gdscript-pause-94vdiqq3/foundation-csharp.log`.

The production startup playback is now GDScript. Actual-scene checks passed
**244 .NET-host checks**, including the temporary bridge and audio-retirement
observer, and **233 standard-engine checks**. The frozen editor view passed
**79 checks** in the .NET editor. The whole project still needs that edition
while world/frontend/HUD controllers remain C#: a standard-editor run can
report missing C# loaders when restoring those scenes. The scripted editor
exit also reports editor-owned RID/ObjectDB shutdown allocations; this is not
evidence of a clean interactive editor shutdown.

Four isolated llvmpipe startup captures passed **256 rendered checks** for
the real logo, montage and two splash fade points. The full-brightness splash
matches the previous C# scene capture pixel for pixel. HUD native texture
recipes and screen fitting now use GDScript, with **44 headless checks** and
**46 rendered checks**; both the 640×480 and 1280×720 captures match the prior
C# output pixel for pixel. The affected existing startup/frontend source and
behavior tests passed **57 tests**. Logs and private captures are retained in
`local-data/test-runs/gdscript-startup-a8xurdqe/`. Rendered runs used fresh
private X-server credentials and cleaned up their own display processes.
These observations establish the converted components and their host boundary,
not audible playback, physical input, GPU performance or full combat parity.

Replay-hash foundations passed **286 synthetic SHA-256 streams**, including
**873 chunk appends/current-hash reads**, and **96 exact schema-4 trace entries**.
The checks compare current/final digests with the existing .NET implementation
and native Godot SHA-256; repeated reads, source/result mutation, stream copies,
padding boundaries, signed field widths, refusal and disposal are covered.
Evidence is in `local-data/test-runs/gdscript-parity-yl94z6c5/`. This preserves
the trace format without replacing the live complete state serializer or runner.

The invariant filename formatter also passed **10,155 output comparisons**
and **611 failure comparisons** against the current .NET library. Its raw
UTF-16 API adds **868 output** and **37 failure** comparisons for embedded
NUL, lone surrogates, numeric-format termination and exact alignment.
Source-checkout loading from the separately licensed root-tools utility passed
**9 dependency checks**; package/export loading is not established. These
reports are in `local-data/test-runs/gdscript-parity-qpd6ptf8/`.
Use `python rebuild/tools/gdscript_parity.py --check NAME` to rerun an affected
group; omit `--check` for the complete bounded migration gate.

Command-tape comparison passed all six sections: JSON admission, validation,
input records, canonical strings/identities, reader/cursor behavior and explicit
boundary refusals. It includes the tracked first-flight tape, without changing
its input or expected hashes. The message-panel port passed **315 wraps**,
**20,201 window samples** and **1,036 reveal-time samples**, including raw
UTF-16, leading U+FEFF, NUL, malformed surrogate and Int32-overflow cases.
The shared strict JSON group also passed after repairing leading-U+FEFF native
String conversion. These reports are in
`local-data/test-runs/gdscript-parity-aertulih/`; they do not establish a ported
full simulation, full HUD runtime or rendered-text equivalence.

All **12 migration groups** subsequently passed together in
`local-data/test-runs/gdscript-parity-wjzad094/`. This added **135 media-load
comparisons**, exact file-inventory checks (including literal-backslash decoys),
**146 BinaryWriter string cases**, **597 direct float-trig cases** and **2,089
scanner placements** compared by raw float32 words. HUD message timing and state
projection also passed. The C# oracle now runs from the same process directory
as Godot, so relative-path fixtures exercise the same filesystem contract.
Eight launcher checks passed, including that directory and desktop isolation.
The exact-byte media accessor then passed **12 additional read comparisons**
alongside that complete media group in
`local-data/test-runs/gdscript-parity-l7rxkeyg/`.

A bounded headless SHA-stream sample appended 41,057-byte synthetic states
twelve times. Inlining fixed rotations reduced its observed median from
33.78 ms to 12.53 ms while preserving the native digest; receipts are in
`local-data/test-runs/gdscript-hash-profile-dyls6119/` and
`local-data/test-runs/gdscript-hash-profile-dd20on6h/`. These shared-machine
microbenchmarks do not establish full-game throughput, input latency or GPU
performance. Live simulation and full replay have not yet migrated.

The production HUD then moved its model, message schedule, text reveal and all
three drawing layers to GDScript. The actual standard-engine scene passed
**174 headless checks** and **182 isolated rendered checks**; the temporary
C# Core/catalog bridge passed **1,487 headless checks** and **1,489 rendered
checks**. This includes all 51 catalog message IDs and signed extremes for
portrait/noise phases. The two real initial-session captures, at 640×480 and
1280×720, match `local-data/hud-editor/capture-01/` pixel for pixel. Synthetic
optional-branch captures exercise rendering but are not retail fidelity
references. Receipts are under
`local-data/test-runs/gdscript-hud-render-n3spgf53/` and
`local-data/test-runs/gdscript-hud-scene-v19y_5xj/`.

The frozen HUD editor scene passed **170 checks** and startup passed **80**;
both refuse live initialization and retain pointer ownership. The startup
host passed **250 checks** after using the production GDScript cache provider.
Its audio-retirement check now observes the actual weak handle against the
same monotonic five-second deadline as the game shutdown path. The old fixed
SceneTreeTimer could expire immediately using the long cache-loading frame's
delta; the measured handle retired after **88 ms** with no remaining playback.
These receipts are in
`local-data/test-runs/gdscript-hud-startup-integration-ftp_v4m7/`. Scripted editor
exit still reports the same editor-owned shutdown allocations described above;
this does not establish a clean interactive editor shutdown.

The affected existing HUD, message, startup and skip checks passed **127/127**
in `local-data/test-runs/gdscript-hud-client-wxgh0rgy/client-verified.log`.
The HUD evidence test now locates prepared links from an owned artifacts
directory and stops at its worktree boundary when they are missing.

The startup batch provider also passed **294 explicit-directory** and **294
process-directory** path comparisons. Its actual playback helpers selected the
correct decoded pixels and bytes from synthetic literal-backslash, normalized
alias and ordinary PNG paths, preserving every fixture hash; evidence is in
`local-data/test-runs/gdscript-parity-n1072_a7/`. The real admitted cache batch
matched the earlier C# provider, including **5,378 ordered frame paths**, in
`local-data/test-runs/gdscript-startup-provider-ew38cn7q/`. The standard-engine
startup scene passed **239 checks** against that retained C# fixture in
`local-data/test-runs/gdscript-startup-scene-ugcfv1yr/`.

The supported headless application smoke then passed **2,148 simulation steps**,
retry and return to the main menu with the unchanged state hash
`53c1cc64ace55542f48534d0554d6ffed57dda0eae48c9f2a55a928fea096e5e`.
The native HUD was ready and delivered the same 13 message IDs and one help
event. Its owned receipt is
`local-data/test-runs/gdscript-hud-smoke-iu5agxg_/smoke/first-flight-smoke.json`.
Outcome was still `Running`, terminal state `None`; this is not a complete
combat victory. World import wrote only this worktree's private generated scenes.

The complete GDScript state serializer passed **55 C# snapshot envelopes**:
**31 exact canonical payloads/hashes** across schemas **42–48**, with the
remaining envelopes refusing invalid state. Checks retain equal-key sort order,
Int64 limits, raw UTF-16, all mission-event arms, raw Plane words and detached
source/output buffers. The existing 40-step `SimulationTests` fingerprint
`0a0b24633f25bb96ac2e8b98443524de47e065b3744b9a15871c09595127a19d`
is unchanged. This is `--check state-hash`, with evidence in
`local-data/test-runs/gdscript-parity-n1072_a7/`; it establishes canonical
serialization, not GDScript simulation stepping or restore behavior.

The native HUD catalog passed both the retained .NET reader comparison and the
standard-engine reader in
`local-data/test-runs/gdscript-hud-catalog-yqylpkir/`. It retains the exact file
SHA and source pins, all 51 messages, six help rows, eight terminal strings,
raw UTF-16 text, refusals and detached lookups. Production now calls that native
reader at boot. After integration, the actual HUD host again passed **1,487
checks**, and the standard catalog check passed with no engine errors in
`local-data/test-runs/gdscript-hud-catalog-integration-hbu89l1i/`.

Career progression, host input and camera value checks passed in
`local-data/test-runs/gdscript-parity-9mt08bqg/`. They cover objective/ranking/
goodie/link mutations, the 43-row world table, input records and edge sequences,
movie-zoom caching and copied viewpoint/hash state. The complete pure frontend
session passed its transitions, constructor admission, detached getters and
all 65,536 UTF-16 glyph inputs in
`local-data/test-runs/gdscript-parity-tlbmrjke/`. These are comparisons against
existing behavior, not new retail discoveries or full-game completion.

The native read-only career reader passed **456 containers derived in memory
from the real tracked gold fixture**: **139 accepted projections** and **317
refusals**, including exact error precedence. Every accepted read preserved
the supplied bytes; source and returned data do not alias, and the fixture
remained unchanged. Evidence is in
`local-data/test-runs/gdscript-parity-ejtvaa12/` (`--check career-save`). No save
writer or AppCore replacement is part of this reader.

The current attached-pan camera and Level 100 viewpoint adapter passed native
state, interpolation, lifecycle, error-order and hash comparisons in
`local-data/test-runs/gdscript-parity-3mxhl595/` (`--check attached-camera`). The
fixtures include every opening tick, varied raw poses and live simulation
snapshot pairs. This preserves the committed camera contract; the separately
preserved camera draft remains unfinished and was not integrated by this port.

The actual frontend then switched to the native session/path owners and passed
**967 scene checks** covering original career-selection identity, transitions,
loading/retry, cached display transport and disposal. The actual world camera
passed **849 bridge/scene checks**, including exact pose words and hashes,
frozen entry, reparenting and final disposal. The private world round-trip passed
**23,864 assertions** over saved geometry, textures, placements and runtime
bindings. Its importer now explicitly disposes four temporary PackedScene
wrappers: the first reimport reported unsafe retained references and aborted at
shutdown; the corrected reimport and world checks exited cleanly. Logs are in
`local-data/test-runs/gdscript-native-front-camera-5clstjzh/`.

That same invocation passed **93 existing Client tests**, **1,487 actual HUD
host checks**, **174 standard-engine HUD scene checks** and the frontend's ten
authored-page checks. The frozen editor checks passed for frontend and HUD
(**170 HUD checks**); their scripted shutdown still reports the same previously
measured editor-owned allocations, including 205 objects. Runtime checks are
clean. The supported headless smoke again completed **2,148 steps**, retry and
return to the main menu with unchanged `53c1cc64…` state identity and 13 delivered
message IDs. Its `smoke/first-flight-smoke.json` still says `Running` / `None`,
not full combat completion. No physical input or audible playback was exercised.

Native control response and all **200 numeric simulation constants**, eight
positions and foot phases passed exact comparisons in
`local-data/test-runs/gdscript-parity-dhfq_7q2/control-response-fixed.json`.
The control probes include 6,174 raw axes across four normalizers, the complete
look table and signed-boundary admission. Native mission timing passed the
existing fade, pause, terminal, message and trigger laws in
`local-data/test-runs/gdscript-parity-9j8h7yxm/`. Native audio recipes, arithmetic,
music actions and queue ordering passed in
`local-data/test-runs/gdscript-parity-jfd_jga6/audio-policy-fixed.json`.
These are `control-response`, `mission-timing` and `audio-policy` migration groups;
the audio laws alone do not establish native scene playback or audible parity.

The `render-interpolation` group passed in
`local-data/test-runs/gdscript-parity-ron2r1pn/`: admission, exact basis and
entity transforms, target projections, trail vertices and vector operations.
Its three extreme retained-tail checks are explicitly source-derived; the
original Int32-maximum loop was not run. The `options` and
`invariant-number` groups passed together with the affected `strict-json`
regression group in `local-data/test-runs/gdscript-parity-oll093em/`.
The options check covers all four pages, controller side-effect ordering,
binding input and detached settings. Number checks cover exact binary32
midpoints and shortest round-trip output, plus parsing failures and whitespace.
These are pure production-model comparisons; native options scene acceptance
is separate.

The `particle-set` and `particle-effects` groups passed together in
`local-data/test-runs/gdscript-parity-9apnf0np/`. The reader compares all
**1,479 descriptors** and numeric getter results, exact byte re-emission and
unchanged input hashes for the three existing prepared files. Synthetic cases
cover duplicate/raw names, field order and error precedence. Encoding checks
compare every UTF-16 unit; effect checks compare every valid Unicode scalar
for invariant casing, authored plans, ordered omissions, cycles, caps and
detached results. The Int32-maximum lifetime refusal is source-derived, not
an executed infinite-loop comparison; all **338 shipped emitter lifetimes**
were checked and exclude that input. No corpus copy or original write occurs.

Native audio integration passed **4,034 .NET reference checks** and **4,031
standard-engine checks** in `gdscript-audio-scene-20260919-f/` and
`gdscript-audio-scene-20260919-g/` under `local-data/test-runs/`.
They compare 135 RNG observations, all 128 music-gain words, ordered frame
interleavings and callback aborts, persistent/transient players and cleanup.
The focused catalog/ownership suite passed **90 tests** in
`audio-client-20260919-a/`; the two affected pause/particle source guards
passed separately in `gdscript-audio-guards-bj_mov24/`.
The supported build and refreshed private scene import passed, followed by
`audio-smoke-20260919-a/first-flight-smoke.json`: unchanged
`53c1cc64…096e5e` state hash, 13 ordered message IDs, retry and main-menu
release, with no runtime errors or shutdown leaks. The .NET editor harness
passed **67 safety assertions** but retained the known 205-object/RID shutdown
diagnostics; its strict console gate remains red. These Dummy-audio checks
establish control/state compatibility, not audible parity or full combat.

The `terrain` group passed **45,681 checks** in
`local-data/test-runs/gdscript-parity-7uz9cc9v/` on the pinned standard engine.
Each of the four existing world resources was compared with its already-linked
input without copying the corpus. Exact metadata, complete 513×513 lattice,
512×512 subcell interpolation and 64×64 LOD-word hashes pass, together with
edge/mask probes, 2,048 scale words, signed-64 division cases, byte admission
failures and detachment. This validates the native owner; the subsequent Sun
consumer integration is covered below. Other live terrain consumers remain managed.

The resumed Options integration passed **1,282 standard-engine scene checks**,
**1,292 isolated rendered checks** across four actual pages, and **1,284 editor
assertions**. Its actual C#/GDScript frontend boundary passed **5,988 headless
checks** and **6,005 rendered checks**, including nine exact RGBA font comparisons
at varied scales/shadows. The same host checks cover all font widths, FEBack byte
tables/phase boundaries, shared frame identity, settings/audio/Back handoffs,
callback failures, partial mutation and reentrant action order. The focused
Client selection passed **144/144**. Pure Options comparisons also passed after
the synchronous callback change. Final receipts are
`local-data/test-runs/options-host-tlovxf1e/`, `options-fonts-rxyrhscr/` and
`options-client-mi9cy457/`; native page/editor receipts are `options-action-7l25qk90/`,
`options-render-4s4gdbbu/` and `options-editor-mszwwwnv/` under that same test-runs
owner. The actual Godot process reports `.NET 10.0.12` with unchanged `net8.0`
targets. Explicit native casts preserve its observed FEBack overflow/NaN result.

Explicit Variant-carrier disposal removed 574 retained texture allocations at
the temporary frontend boundary. The final rendered host exits cleanly, but the
headless Options harness still reports **one Image and one Dummy texture RID**
at exit; its strict console gate remains red. Disposing the retained DDS loader's
temporary Image did not resolve that final allocation. Its owner is unresolved;
no forced GC, diagnostic suppression or weakened assertion was used. The native
editor harness also retains scripted-editor scan/shutdown diagnostics. These
limits are separate from the passing behavior and pixel comparisons.

The entity owner passed **89 native runtime checks**, **64 editor assertions**
and **23,038 actual managed-boundary checks**. Every actor/foot/projectile word,
trail vertex/UV and muzzle frame retains its reference behavior; all six authored
texture pages match the previous loader byte-for-byte, including format and
mipmap flags. Public template saves contain recipes without decoded pixels.
The authored albedo/emission slots share a page; the checks preserve the pinned
engine's omission of inactive unshaded emission properties during scene-local
duplication, while still refusing an active mismatched page. Runtime logs are
clean; the editor has the previously recorded scripted shutdown diagnostics.
Receipts are `entity-art-native-fixed-cthkzvbj/`, `entity-art-editor-46875jwv/`
and `entity-art-bridge-final-oxutw64r/` under `local-data/test-runs/`.
The particle/quad/Sun Client selection passed **25/25** in
`entity-art-client-ofvtnlgq/results/focused.trx` under that same owner.

The production Sun passed **8,081 standard-engine checks**, including 848 height
samples and 2,348 camera cases against the unchanged, renamed C# reference, plus
exact texture/material/mesh/colour comparisons. **104 editor assertions** cover
inactive sampler/input, unchanged sources, public saves without pixels and
repeated private saves retaining external resources. Runtime is clean; scripted
editor teardown diagnostics remain. Receipts are `gdscript-sun-reference-5jfln59c/`,
`gdscript-sun-native-final-znutlbka/` and `gdscript-sun-editor-final-du_moph1/` under
`local-data/test-runs/`. The explicit NaN coordinate shim matches the actual
host's current heightfield reader; it does not establish retail NaN behavior or
resolve the existing terrain-only/VisibleSun omissions.

The combined supported build and private import passed with zero warnings/errors
in `local-data/test-runs/gdscript-resume-build-g/`. The final world check passed
**24,132 assertions** in `gdscript-resume-world-c/`, with clean runtime shutdown.
It covers geometry/material/texture round-trips, initial bindings, selected poses,
retry isolation, unchanged pointer/hash state and native source/resource import
invalidation. Exactly two authored trail slots remain empty before movement;
their generated history is checked by the entity comparison. The unchanged
camera bridge also passed **849 checks** in `gdscript-resume-camera-a/`.
The supported headless smoke in `gdscript-resume-smoke-a/` again retained
**2,148 steps**, the unchanged `53c1cc64…096e5e` hash, 13 ordered message IDs,
fresh retry and world release at the main menu, with a clean runtime log.
Its actual 2,148-step recording passed two Headless replays in
`gdscript-resume-replay-a/replay.log`: both embedded live trace
(`a4e6673b…43c58f2`) and final-state hashes verified, with no first divergence.
Mission outcome remains **Running**, terminal state **None**; this is not full
combat completion. All these directories are under this worktree's
`local-data/test-runs/`, using the canonical lab read-only. Rendered checks used
isolated credentials/displays and establish no physical-input, audible-playback
or normal GPU-performance claim.

The native terrain renderer passed **801 assertions** across **3,183,306 exact
mesh words**, 464 height samples, all 49 stitch-index patterns and twelve full
camera/mesh updates. The retained C# exporter passed **49,206 assertions**.
The first comparison found a transposed complexity-grid lookup; the production
admission now converts x-major samples to the renderer's y/x order, with no
expected-data change. Smoothing words, ordered tile batches, FNV64 signatures,
material retention, supplied mesh identity and resource release all match.
The unchanged reference is in `height-field-oracle-y2kb9hoj/`; the final cached
implementation report is `heightfield-cache-1pvzrig6/native.json` under
`local-data/test-runs/`. Both logs are clean.

The immutable actor-definition and pinned manifest ports passed **3,856 native
assertions** and **139,848 exact canonical bytes**. The unchanged C# exporter
passed **194 checks**, providing 275 constructor cases (160 accepted, 115
refused), 164 lookup cases and eighteen manifest refusals. Identity formats
6/7/8, raw UTF-16/NUL/unpaired-surrogate keys, detached inputs/snapshots/lookups,
and ordered failure types/parameters agree. World number remains admitted but
absent from the existing identity bytes. The actual definition identity remains
`2fc2219881a66a4662688d69b1ab5d2b7b9e02cb6fdc63ce5a34019974fa69b2`.
Receipts are `actor-definition-reference-tyv7nvwk/` and
`actor-definitions-native-lo2crjol/` under `local-data/test-runs/`; both engine
logs are clean. Run .NET `Scenes/World/Tests/ActorDefinitionReferenceChecks.tscn`
with fresh fixture/report user paths, then standard
`Scenes/World/Tests/actor_definition_checks.gd` with that fixture and a fresh
report. This validates immutable definitions; the live registry is still C#.

The native click-page expressions passed **68,630 exact checks** against the
retained C# helpers: 5,703 expression rows, 144 binary64 clock rows and fifty
Int32-width glyph rows. The initial thirty-six failures came from using
double-precision `cos` followed by a float32 cast. The pinned Arm adaptation,
with exact fused-operation emulation, passed **69,113 assertions** against the
actual Godot-hosted .NET 10.0.12 `MathF.Cos` and `Math.FusedMultiplyAdd`: 21,078
cosine words, 4,112 finite FMA inputs, and the existing click samples. No expected
word changed. This is bounded compatibility evidence for Linux x86-64/glibc 2.44,
not proof of every float input or of Windows/retail trigonometry. Receipts are
`click-laws-reference-n1z2lgpw/`, `click-adopted-hl1txc21/`,
`cosf-reference-ya7q4rwv/` and `cosf-native-0iuj4dyh/` under
`local-data/test-runs/`.

The actual native Click scene passed **136 headless assertions** and **329
rendered assertions**, including **128 exact full-page RGBA comparisons**:
sixteen pulse/page-time pairs at 640×480, 1280×720, 801×601 and 320×240, each
against the retained drawing and the integrated frontend. The same comparisons
against the pre-integration host also passed. A first parent-scale/translation
implementation changed a few filtered color bytes by one at fractional viewport
scales. The final small image/text controls form the original float32 rectangles
before canvas transforms and pass the unchanged zero-difference assertion.
Source passes, coordinates, gates, colors, private texture/font bytes and clock
facts are retained. Captures used an isolated authenticated Xvfb display with
llvmpipe and dummy audio, not the physical desktop. Clean headless logs and final
render logs (only XIM/VSync warnings) are in `click-integrated-2z_igtkj/`; the
pre-integration comparison is `click-render-surfaces-cljldf49/`. The affected
22-class Client run passed **113/113**, with no skips or changed numerical
expectations (`click-source-client-mtbgbjke/results/click-client.trx`).
Loading's existing handoff/asset checks also passed **234 assertions** after the
shared bitmap-label extension (`click-integrated-2z_igtkj/loading.log`).

To reproduce the Click checks, run .NET
`Scenes/Frontend/Tests/ClickLawReferenceChecks.tscn` with one fresh fixture
user path, then standard `Scenes/Frontend/Tests/click_law_checks.gd` with that
fixture and a fresh report. The cosine exporter is
`Scenes/Shared/Tests/CosfReferenceChecks.tscn`; its two fresh fixture/report
arguments produce the cosine fixture. Standard
`Scenes/Shared/Tests/retail_cosf_checks.gd` takes, in order, that cosine fixture,
the click fixture and a fresh report path. Run .NET
`Scenes/Frontend/Tests/ClickSceneChecks.tscn -- --skipfmv` for the integrated
component. With a caller-owned isolated display, add
`--click-render-dir=/absolute/owned/capture-directory` for exact RGBA comparisons.
All output paths belong under the invoking worktree's `local-data/`.

The standalone native Click harness passed **658 checks** in both standard
runtime and editor, covering actual assets, source-order drawing rectangles,
preserved authored geometry/centers, frozen inspector facts, detached inputs,
round-trip serialization without private pixels, and pointer/input ownership.
The `.NET --editor` frontend check passed all ten pages plus native Click,
frozen-time and shared-title assertions. An initial editor-only dependency
refusal was resolved by marking the pure cosine utility `@tool`; its numerical
implementation is unchanged. Final receipts are `click-scene-native-iemqeo_e/`,
`click-scene-editor-t3gzsieg/` and `frontend-click-editor-ia7i3pg1/`.
Runtime is clean. The editors retain 166 (standard) / 205 (.NET) ObjectDB
instances and associated Canvas/viewport/texture/text RID shutdown diagnostics;
these are not clean editor exits. Run standard
`Scenes/Frontend/Tests/click_scene_checks.gd` with one fresh owned output directory,
adding `--editor` for inspector/serialization checks. The integrated editor entry
is `Scenes/Frontend/Tests/frontend_scene_checks.gd` under the .NET engine.

The shared fixed-function material factory passed **1,732 native assertions**
against 88 original factory/admission cases and 1,044 alpha words. Texture and
shader identity, ordered failures, all parameters, public/private serialization
and release match. Both old and native text saves reload fog density as decimal
double `0.0084`, while preserving shader float32 word `0x3c09a027`; the checks
compare actual old/new reloads and separately preserve original shader words.
The external shader differs only by its SPDX line and end-of-file newline.
Reference/native runtime logs are clean in `gdscript-fixed-material-reference-q9qpn_id/`
and `gdscript-fixed-material-native-35t_bdpw/`. The three affected Client classes
passed **53/53** in `gdscript-fixed-material-client-hg72ai4f/results/material.trx`.
The .NET editor gate passed **42 functional checks**, retaining the previously
observed 205 ObjectDB/associated RID shutdown diagnostics
(`gdscript-fixed-material-editor-mono-hh0tc01l/`); that editor exit is not clean.
Use .NET `Scenes/Shared/FixedFunctionMaterialChecks.tscn` with fresh fixture/report
user arguments, then standard `Scenes/Shared/fixed_function_material_checks.gd`
with that fixture and a fresh report; `--editor` selects its inactive-resource gate.

After Click/material integration, the supported pinned build and private Level
100 import passed with zero build warnings/errors. `WorldSceneChecks.tscn`
passed **24,144 checks**, including the added external-dependency route/content
and missing-input checks (`click-material-full-build-e.log` and
`click-material-world-e.log`). The **2,148-step** smoke retained thirteen ordered
message deliveries/queues, a fresh retry, return to Main Menu and world release.
Its complete recorded tape is byte-identical to the prior milestone, SHA-256
`89ca7b4ba0642c7fa1e68bbaf1875c724762a5d3ef6902182110da84706db14a`.
Two replays verified unchanged trace hash
`a4e6673b92e651c05fcd2ddc2c10932d325db0f7d8db1d774e9c60ede43c58f2`
and state hash `53c1cc64ace55542f48534d0554d6ffed57dda0eae48c9f2a55a928fea096e5e`,
with no first divergence. Receipts are `click-material-smoke-3ywj6mz6/` and
`click-material-replay-7s41lvmd/`; runtime logs are clean. Eight voices began
before teardown versus nine in the prior host-timed run; the ordered queue and
simulation delivery sequence remain identical. The mission is still
`Running`/`None` with zero targets destroyed: this is not full-combat acceptance.

The native Aquila component passed **1,121 checks** against the original three
profiles: complete decoded definitions, mesh arrays/format flags, shared
materials, componentwise matrix interpolation, contact poses, saved resources
and retry binding. The expanded set includes **546 pose checks**, nonfinite
contacts and the original partial-mutation/error order. The initial Godot-native
arc constructor sanitized some nonfinite inputs; the final explicit IEEE path
preserves the original raw words and parameterless zero-vector error instead.
Reference/native receipts are `gdscript-aquila-reference-56_ecpii/` and
`gdscript-aquila-native-qu0dw_db/`, with clean runtime logs. All **19** affected
Client material/provenance tests passed (`aquila-client-c8cd03nv/results/aquila.trx`).

All **111** synthetic public source-admission comparisons also match. A separate
uncommitted diagnostic found **21/36** differences between the old private
`ZLibStream` helper's incomplete/trailing-record acceptance and the shared
native strict decoder. Every affected input is rejected by both production
entrances' length/SHA-256 pins before decompression; all three admitted streams
decode byte-for-byte identically. The diagnostic vectors/results remain in the
reference fixture and earlier `gdscript-aquila-reference-cnkzi_zu/` comparison
receipts. No committed expectations were relaxed and no general unpinned
inflater equivalence is claimed. Admitting another source requires a new review.

The final .NET editor gate passed **33 functional checks**
(`gdscript-aquila-editor-mono-5ab1tqit/`), retaining the known 205 ObjectDB/RID
shutdown diagnostics. An isolated Xvfb/llvmpipe editor run rendered the actual
walker, jet and cockpit as **54/58/10 surfaces** without an animation owner or
input capture; images and source hashes are in `aquila-editor-visual-0gqofenh/`.
These were inspected as bounded component views. That custom editor run also
reported two progress-dialog `current_window` errors and 163 ObjectDB/associated
RID shutdown diagnostics; it is not a clean editor exit or a normal-GPU claim.
Run .NET `Scenes/Aquila/AquilaSceneChecks.tscn` with fresh absolute fixture/report
paths, then standard `Scenes/Aquila/aquila_scene_checks.gd` with that fixture and
a fresh report. Add `--editor` for the inactive preview/serialization gate.
Both use the owned worktree's `local-data/`; comparison scenes remain private.

The supported pinned build and private Level 100 import passed with zero
warnings/errors after live Aquila adoption (`aquila-full-build-g.log`).
`WorldSceneChecks.tscn` passed **24,169 checks** (`aquila-world-g.log`), including
native profile/script binding before initialization, inactive animation owners,
Aquila template edits invalidating the bake, the existing geometry/material
round-trip, selected snapshot poses, retry isolation and unchanged state hashes.
The receipt now also admits the five actual private texture inputs used by the
saved Aquila recipes. Focused synthetic files exercise same-size byte changes,
missing inputs, malformed/duplicate/empty receipt entries and normalized path
refusals, plus read-only linked input preservation. Research inputs are untouched.

The live Aquila smoke (`aquila-smoke-t56qsw2y/`) kept the **2,148-step** tape
byte-identical to the preceding Click/material milestone
(`89ca7b4ba0642c7fa1e68bbaf1875c724762a5d3ef6902182110da84706db14a`).
Two actual-tape replay runs (`aquila-replay-eqg57euc/`) matched trace
`a4e6673b92e651c05fcd2ddc2c10932d325db0f7d8db1d774e9c60ede43c58f2`
and final state `53c1cc64ace55542f48534d0554d6ffed57dda0eae48c9f2a55a928fea096e5e`
with no behavioral event or state divergence. All 13 ordered message IDs, queues
and speakers remained the same; host-timed playback had seven voice starts
before teardown versus eight previously. Retry/return released the world, and
the 112 exterior/10 cockpit surfaces retained their existing counts. The route
still ends `Running`/`None` with zero targets destroyed; this does not establish
full combat completion or audible playback.

#### Interrupted conversion checkpoint — September 20

At this checkpoint the native Main Menu was integrated but still under validation. The following
receipts are retained in the conversion worktree's `local-data/test-runs/`:

- `main-menu-law-fixed-njfykcp9/report.json`: **205,452** comparisons passed
  against `main-menu-laws-1u34suyk/`, covering 5,188 expression cases and 1,040
  packed-color cases. Ten initial overflow/negative-NaN word differences were
  corrected in the native implementation against the unchanged fixture.
  Subsequent harness output guards/completion metadata still need a re-run.
- `main-menu-frontend-b.log`: the actual frontend scene checks passed after
  enabling editable Main Menu children; the initial round-trip failure is
  retained in `main-menu-frontend-a.log`. The checks cover all ten authored
  pages, seven menu rows, shared resources, edits and unchanged pointer mode.
- `main-menu-frontend-editor-a.log`: functional editor checks passed, with
  the known 205 ObjectDB/associated RID shutdown diagnostics. This is not a
  clean editor-exit claim.
- `main-menu-session-a.log`: **967** session/path/admission assertions passed;
  `main-menu-click-sharing-a.log`: **136** shared Click/title checks passed.
  These are headless checks, not rendered Main Menu comparisons.
- `main-menu-client-j2kczeef/results/main-menu-b.trx`: **177/177** affected
  Client tests passed, with no skips. Existing numerical expectations remain
  unchanged; production-source guards now inspect the native owners.
- `safe-resume-checkpoint-build-20260920-a.log`: the supported pinned
  `first_flight.py build --no-prepare` passed with **zero warnings/errors**,
  including the new `MainMenuSceneChecks` and `RetailWeaponReferenceChecks`.
  Neither new scene harness has been executed at this checkpoint.

The standalone editor/publication checks, rendered comparison and integration
review were unfinished at that checkpoint. The September 22 results below
supersede those gaps; the earlier Aquila receipts above retain their original
scope.

The three weapon foundations had only parsed at the September 20 checkpoint;
their subsequent comparison results are recorded below. They have no live
consumers yet.
Current component guidance is in [`rebuild/README.md`](rebuild/README.md#native-main-menu).

#### Native Main Menu — September 22

The production native page and its live frontend adapter preserve the existing
renderer in the following executed checks. All receipts below belong to this
worktree's ignored `local-data/test-runs/`; canonical research inputs were read
through the existing asset routes.

- `main-menu-resume-laws-zw542v2k/`: **205,454 checks**, all expression and
  packed-color groups complete, against 5,188 expression rows and 1,040 color
  rows from the unchanged C# comparison. Eight output-path refusals preserved
  their sentinels and fixture hash (`main-menu-law-guards-5z2qnidd/`).
- `main-menu-render-decor-o5hlffl3/report.json`: **2,282 checks**, all five
  groups and **92 samples** complete. All **178 native/live-host image
  comparisons have zero RGBA-byte differences** against the retained original
  renderer: 640×480, 1280×720, 801×601 and 320×240 transitions, language flags,
  raw UTF-16, reflection suppression and authored row text/geometry. The
  isolated Xvfb display used separate credentials/profiles, Dummy audio and
  llvmpipe (Mesa 26.2.2, LLVM 22.1.8), then stopped its owned processes.
  Two representative captures were inspected. The log contains only the
  expected virtual-display input-method/V-Sync warnings, with no runtime
  errors or teardown leaks. This is software-rendered regression evidence,
  not normal-GPU performance, physical input or audible playback.
- `main-menu-native-pass-edit-pwuz8krr/result/report.json`: **576 checks**,
  all ten groups complete in standard headless Godot, with a clean log.
  It uses the actual production scene/assets, checks inactive input/clocks,
  detached admitted facts, frozen Inspector redraws, independent decoration
  edits and actual pack/reopen. Public serialization excludes private decoded
  images and byte buffers. Standard headless editor also passed all **576**
  checks (`main-menu-native-editor-shared-frame-v2tlygzz/`) but reported
  **166 ObjectDB/associated RID teardown leaks**; this is not a clean
  editor-exit claim. Eight native output-path refusals preserved their
  sentinels (`main-menu-native-output-guards-be33uep4/`).
- The actual .NET frontend scene passed its ten-page/seven-row, asset sharing,
  edit/round-trip and pointer checks in runtime and editor modes
  (`main-menu-frontend-runtime-final-myenqszi/` and
  `main-menu-frontend-editor-final-ivccwh8b/`). The runtime log is clean; the
  editor retained **205 ObjectDB/associated RID shutdown leaks**.
- `main-menu-client-complete-mnjeui0b/results/main-menu.trx`: **177/177** affected
  Client tests passed with zero skips. Numerical expectations remain unchanged.
- `main-menu-full-build-f1uqiost/`: the supported pinned .NET build and private
  Level 100 production import passed with zero warnings/errors.
  `main-menu-world-3n78x08g/`: **24,169 world checks** passed, including saved
  geometry/materials, native bindings, selected poses, retry isolation and
  unchanged simulation hashes.
- `main-menu-smoke-eaehifkc/`: the live headless frontend/world smoke completed
  **2,148 steps**, thirteen ordered message deliveries/queues, a fresh retry
  and return to Main Menu with world release. Its recorded tape remains
  byte-identical to the preceding Aquila milestone, SHA-256
  `89ca7b4ba0642c7fa1e68bbaf1875c724762a5d3ef6902182110da84706db14a`.
  `main-menu-replay-cq_in8zz/`: two actual-tape replays verified unchanged
  trace `a4e6673b92e651c05fcd2ddc2c10932d325db0f7d8db1d774e9c60ede43c58f2`
  and state `53c1cc64ace55542f48534d0554d6ffed57dda0eae48c9f2a55a928fea096e5e`,
  with no first divergence. Runtime logs are clean. The mission still ends
  `Running`/`None` with zero targets destroyed; this is not full-combat acceptance.

The rendered check exposed two canvas-structure differences at fractional
scales. The reflection now retains the original canvas-root shader submission,
follows frozen authored title/ancestor transforms and keeps derived pose/Z out
of saved defaults. Decoration passes now share the original decoration canvas
frame instead of regrouping floating-point transforms around tighter individual
bounds. Their named Controls remain independently editable. The assertions
still require exact pixels. Review also exposed an unknown Resource leaking
through frame snapshots and an anchor edit requiring another frame batch;
both are fixed and covered by the native checks.

Run .NET `Scenes/Frontend/Tests/MainMenuSceneChecks.tscn` with `--skipfmv` for
actual scene/host checks; a caller-owned isolated display plus
`--main-menu-render-dir=ABS_FRESH_EMPTY_DIR` enables the exact image comparisons.
Run standard `--headless --script
res://Scenes/Frontend/Tests/main_menu_scene_checks.gd -- ABS_FRESH_EMPTY_DIR`
for native editor/publication checks; `--editor` selects tool mode. Output must
stay in this worktree's `local-data/`. The scene comparison reference preserves
the reconstruction's existing retail evidence gaps; matching it does not close
unmeasured retail behavior or complete Level 100 combat.

#### Native Quit confirmation — September 22

The actual `QuitConfirm.tscn` replaces the single C# dialog draw pass in the
production frontend. Receipts below are in the conversion worktree's ignored
`local-data/test-runs/`; prepared research inputs retain their recorded hashes.

- `quit-confirm-native-roundtrip-m3ydb0s3/result/report.json`: **314 checks**,
  all seven sections complete in standard headless Godot. Actual Controls,
  font sharing, rejected input batches, detached snapshots, frozen edits,
  half-open hit boundaries at five Stage scales and pack/reopen passed.
  Private image storage is absent from public serialization. Two output
  refusal probes preserved their sentinels (`quit-confirm-output-guards-9733aoml/`).
- `quit-comparison-headless-ozjwqf6l/report.json`: **1,457 checks**, all five
  groups and twelve states complete against the retained `5390cb11` drawing.
  The live host preserves default No selection, keyboard/pointer behavior,
  ordered audio/cursor/exit callbacks and unchanged input hashes. Headless
  results make no pixel claim.
- `quit-comparison-render-faf9mqkz/report.json`: **1,517 checks**, twelve states
  and **24 exact native/live-host image comparisons with zero differing
  RGBA bytes**. Coverage includes 640×480, 1280×720, 801×601 and 320×240 plus
  authored translation, size, rotation and scale. The caller-owned Xvfb
  display used separate credentials/profiles, software rendering and Dummy
  audio, then stopped its own processes. The 1280×720 live-host capture was
  inspected. Only expected virtual-display input-method/V-Sync warnings
  appeared; there were no runtime errors or teardown leaks.
- `quit-frontend-runtime-kiwe9kaw/` and `quit-frontend-editor-xfgx0f3p/`:
  actual frontend asset sharing, frozen page selection, authored edits,
  pack/reopen and unchanged pointer passed. Runtime shutdown is clean.
  Editor shutdown still reports **205 ObjectDB/associated RID leaks**, as
  before this conversion; this is not a clean editor-exit claim.
- `quit-client-fixed-voidd1_c/results/quit.trx`: **256/256** affected Client
  tests passed, zero skips. Existing numerical expectations are unchanged;
  source-ownership guards now inspect the native production scene/scripts.
- `quit-full-build-g0xxaoue/`: supported pinned .NET build and private Level 100
  import passed with zero build warnings/errors. `quit-world-e6ffz5x5/` passed
  **24,169** production world checks. `quit-smoke-vudd6qza/` completed **2,148**
  steps, thirteen ordered message deliveries/queues, focus-loss handling,
  fresh retry and return to Main Menu with world release. Its recorded tape
  retains SHA-256 `89ca7b4ba0642c7fa1e68bbaf1875c724762a5d3ef6902182110da84706db14a`.
  Two replays (`quit-replay-n6o623ra/`) retained trace
  `a4e6673b92e651c05fcd2ddc2c10932d325db0f7d8db1d774e9c60ede43c58f2`
  and state `53c1cc64ace55542f48534d0554d6ffed57dda0eae48c9f2a55a928fea096e5e`,
  with no first divergence. Runtime logs are clean; mission outcome remains
  `Running`/`None`, zero targets destroyed, so full combat remains unproven.

A direct hit probe exposed a real conversion error: at 1024×768, pointer
`(832,400)` maps to excluded design point `(520,250)`, but an extra
design→canvas→design round-trip selected No. The adapter now passes the original
design point directly; the native row composes only its authored transforms.
The original half-open limits, including adjacent float values, pass in both
standalone and actual-host checks. Before/after receipts are
`quit-hit-before-d08piubz/` and `quit-hit-after-67821ncj/`.

Run standard `--headless --script
res://Scenes/Frontend/Tests/quit_confirm_scene_checks.gd -- ABS_FRESH_EMPTY_DIR`
for native checks. The .NET `Scenes/Frontend/Tests/QuitConfirmSceneChecks.tscn`
requires `--skipfmv`; supply `--quit-render-dir=ABS_FRESH_EMPTY_DIR` only with a
caller-owned isolated display for pixel comparisons. Both output directories
must be inside this worktree's `local-data/`. The actual frontend editor check
is `--editor --headless --script
res://Scenes/Frontend/Tests/frontend_scene_checks.gd -- --skipfmv`.
These comparisons preserve the previous reconstruction. Retail Quit rendering,
localization and the reconstructed dialog height remain unmeasured; software
captures establish neither normal GPU performance nor physical input/audio.

#### Native career-name page — September 22

`CareerName.tscn` now owns the production New/Load page's header, bracket pair,
eleven row slots, list/scrollbar, name field/highlight and chevrons. Gameplay
and the editor use the same typed GDScript controls and shared font/texture
recipes. The narrow host adapter supplies detached display facts, queries hit
regions/name extent, and retains the existing session/navigation/audio/save
handoff. The original renderer and its measurement provenance are retained
under `Scenes/Frontend/Tests/CareerNameReference*`, pinned to `14f6f72b`.

Executed receipts under the conversion worktree's `local-data/test-runs/`:

- `career-name-native-66aas6ow/result/report.json`: **495 checks**, all eight
  sections, zero failures in standard headless Godot. Authored nodes exist
  before Ready; frozen previews, UTF-16/width laws, overflow/refusals, transformed
  half-open hit regions, edits and pack/reopen passed. Fourteen public sources
  and five private production inputs retained their hashes; public scene
  serialization contains no private image pixels. Runtime diagnostics are clean.
  `career-output-guards-t61kzkdq/` adds two executed existing-report/symlink
  refusal probes; the sentinel bytes and symlink target remained unchanged.
- `career-headless-fixed-wur6ftj9/report.json`: **6,338 checks**, sixteen states
  and all five comparison groups passed. This includes the live host, all BMP
  input units, source-frame geometry, name editing, keyboard/pointer navigation,
  exact selected descriptor identity and ordered callbacks. The tracked gold
  save fixture was read through its verified parser and remained byte-identical;
  no save was discovered, synthesized or written. No pixel claim is made here.
- `career-comparison-render-3ryerm7e/report.json`: **6,418 checks** and **32
  exact native/live-host image comparisons with zero differing RGBA bytes**.
  Coverage includes 640×480, 1280×720, 801×601 and 320×240, New/Load, overflow
  selection, raw UTF-16, edited names and authored header/list/name transforms.
  The 1280×720 New and 801×601 Load host images were inspected. Rendering used
  task-owned Xvfb credentials/profiles, llvmpipe and Dummy audio with process
  cleanup. Only the expected input-method/V-Sync warnings appeared; no runtime
  errors or teardown leaks occurred.
- `career-frontend-runtime-zcyj78m7/` and `career-frontend-editor-wz7yhlm5/`:
  actual frontend sharing, all ten frozen editor pages, native CareerName edits,
  pack/reopen and unchanged pointer passed. Runtime shutdown is clean. Editor
  shutdown retains the existing **205 ObjectDB/associated RID leaks**; it is
  not a clean-exit claim. The separate import
  `career-frontend-editor-import-gwf0lkdg/` completed cleanly.
- `career-startup-capture-rijwodsj/run/capture-manifest.json`: all **13/13**
  scheduled startup shots captured at 640×480 with the expected screen at every
  boundary. `career-client-final-ikbjrsw9/results/career.trx` then executed
  **127 affected Client tests: 126 passed, one failed, zero skipped**. The
  failing retail title gate is described below; its expected values are unchanged.
- `career-integration-final-0puv5c6w/`: supported pinned .NET build and private
  Level 100 import passed with zero build warnings/errors. The **2,148-step**
  smoke preserved thirteen ordered message deliveries/queues, focus-loss/rearm,
  a fresh retry and return to Main Menu with world release. The recorded tape
  retains SHA-256 `89ca7b4ba0642c7fa1e68bbaf1875c724762a5d3ef6902182110da84706db14a`.
  Both replay runs verified trace
  `a4e6673b92e651c05fcd2ddc2c10932d325db0f7d8db1d774e9c60ede43c58f2`
  and state `53c1cc64ace55542f48534d0554d6ffed57dda0eae48c9f2a55a928fea096e5e`,
  with no divergence. Logs are clean; mission outcome remains `Running`, zero
  targets destroyed. A prior smoke correctly refused stale generated scenes
  after the comparison harness was recompiled; the supported build refreshed
  this worktree's private scene import before the successful final run.

The fresh retail header gate is **not green**. Both CareerName and the unchanged
LevelSelect draw title ink at **y71..87**, while the pinned retail expectation is
**y72..88**. All glyph-run widths match. Current horizontal extents match retail
(CareerName x263..513, LevelSelect x304..471), so the old one-pixel-right note is
historical. `career-header-diagnosis-ovow_8tj/report.json` records the same y71..87
result from the retained pre-conversion CareerName renderer on the same engine,
with byte-identical native/reference comparison images. It also remeasures the
pristine retail `local-lab/retail-reference-pristine/choose-game-name/choose-game-name-640x480.png`
(SHA-256 `45bd325ad9112af8323755a8aadb210f856ba3f5d1206b4293b32d4c126ea1d5`)
at y72..88. This is an unresolved reconstruction/raster discrepancy, not evidence
that this conversion moved the title. Its cause is still unknown. A bounded
comparison of the same retained draw under the previous pinned engine and dev6,
followed by the actual retail glyph submissions, can distinguish engine raster
change from the retained drawing origin. No source constant, expected row or
image threshold was adjusted to pass. Automatic capture selection now considers
native frontend sources/resources as well as the C# host, preventing stale
pre-conversion captures from satisfying this gate.

An offscreen-null regression was found and corrected: the old renderer stops
before row eleven, so the bridge must preserve a null twelfth name without
reading or normalizing it. That case now renders exactly. Malformed *visible*
null rows are explicitly refused at native `set_frame` admission with
`InvalidDataException`; the retained renderer threw `NullReferenceException`
during glyph iteration. Both session owners retain the original partial mutation
and failure when selecting a null name. The native API rejects that resulting
null name, while the temporary host's raw-text projection still throws
`ArgumentNullException`, the same type as the prior draw's name-width sum.
The comparison report records these different refusal stages; it does not claim
identical malformed-input exception timing.

Run standard `--headless --script
res://Scenes/Frontend/Tests/career_name_scene_checks.gd -- ABS_FRESH_OWNED_DIR`
for the native component. Run .NET
`res://Scenes/Frontend/Tests/CareerNameSceneChecks.tscn -- --skipfmv` headlessly
for the comparison, or add `--career-render-dir=ABS_FRESH_EMPTY_DIR` only on a
caller-owned isolated display. Output belongs under this worktree's `local-data/`.
The missing header endcaps/Forseti art, unmeasured page transition and retail
header discrepancy remain open. These checks establish neither full combat nor
normal GPU, physical-device, audible playback or cross-platform parity.

#### Native Select Configuration — September 22

`SelectConfiguration.tscn` owns the production background passes, translucent
header, unit name, Walker/Jet weapon rows and chevrons. Its six sections expose
real editable controls before Ready. The shared atlas fonts and private texture
recipes serve both gameplay and frozen editor examples. The C# host forwards
five raw UTF-16 display fields and queries the native hit regions, retaining the
existing session, audio and launch ordering. The original draw methods and
their measurement provenance remain in `Tests/ConfigurationReference*`, pinned
to `7474445c`.

Executed receipts under the conversion worktree's `local-data/test-runs/`:

- `configuration-native-68nn5ltn/result/report.json`: **385 checks**, all eight
  sections and zero failures in standard headless Godot. Coverage includes
  actual asset admission, detached UTF-16, refusal atomicity, half-open arrow
  edges, authored transforms, frozen text overrides and pack/reopen. Thirteen
  public sources and five private production inputs retained their hashes.
  Saved scenes contain public recipes and layout, not decoded private pixels.
  Runtime diagnostics are clean. The same receipt's two output-refusal probes
  preserve an existing report-directory sentinel and a dangling scene symlink.
- `configuration-headless-_e3rsl5k/report.json`: **1,997 checks**, eleven states
  and all five comparison groups passed against the retained C# renderer and
  actual frontend host. Coverage includes exact asset/glyph bytes and widths,
  detached facts, authored source transforms, half-open targets at five window
  sizes, the one-configuration restriction and keyboard/pointer callback order
  through two loading handoffs. No gameplay world is constructed. Logs are clean.
- `configuration-render-6o0d44b6/report.json`: **2,044 checks** and **18 exact
  native/live-host image comparisons with zero differing RGBA bytes**. This
  covers production defaults at 640×480, 1280×720, 801×601 and 320×240, raw
  UTF-16/empty text, edited background/header/weapon sections and explicit
  unit-name overrides. The 1280×720 production and edited Walker host images
  were inspected. Task-owned Xvfb used separate credentials/profiles, software
  rendering and Dummy audio; processes were cleaned up and credentials removed.
  Only the expected input-method/V-Sync warnings appeared; runtime and shutdown
  were otherwise clean. Six private inputs retained their hashes.
- `configuration-editor-b84mrgvl/`: headless .NET editor import and actual
  frontend runtime/edit/pack/reopen checks passed. All ten frozen editor-page
  selections passed; selecting Configuration starts neither processing nor
  loading. Pointer state remains unchanged. Import and runtime
  exit cleanly. Editor shutdown retains the existing **205 ObjectDB/associated
  RID leaks**, so the editor result is a functional pass, not a clean-exit claim.
- `configuration-startup-ozo7di_i/run/capture-manifest.json`: all **13/13**
  scheduled 640×480 startup shots matched their expected screens, including
  entry/settled Configuration and the Loading boundary, on an isolated display.
- `configuration-client-j0d50v19/results/configuration.trx`: **127 affected
  Client tests executed: 126 passed, one failed, zero skipped**. The fresh
  captures reproduce the same CareerName/LevelSelect retail header discrepancy
  described above: y71..87 versus the unchanged y72..88 expectation. No new
  configuration failure appeared, and no assertion or expected image was weakened.
- `configuration-build-iskvkwcx/`: supported pinned .NET build and this
  worktree's private Level 100 import passed with zero build warnings/errors.
  `configuration-smoke-0s9difyy/` then passed the **2,148-step** lifecycle smoke,
  thirteen ordered message deliveries/queues, synthetic focus-loss/rearm,
  fresh retry and Main Menu return with world release. Its tape SHA-256 is
  unchanged at `89ca7b4ba0642c7fa1e68bbaf1875c724762a5d3ef6902182110da84706db14a`.
  Both replay runs verified trace
  `a4e6673b92e651c05fcd2ddc2c10932d325db0f7d8db1d774e9c60ede43c58f2`
  and state `53c1cc64ace55542f48534d0554d6ffed57dda0eae48c9f2a55a928fea096e5e`
  without divergence. Logs are clean. Outcome remains `Running`, with zero
  targets destroyed; this is not full-combat acceptance.

The half-transparent header, ring red gain above 1.0, fractional unit-name
origin and mirrored arrow preserve the retained rendering contract. Explicit
label overrides are a new editor feature: the old C# configuration sections'
text override did not affect these draw methods. The missing live unit model,
mode icons, rating stars, Forseti emblem and header endcaps remain unresolved.
The separate CareerName/LevelSelect retail header gate above does not measure
this configuration page.

Run standard `--headless --script
res://Scenes/Frontend/Tests/configuration_scene_checks.gd -- ABS_FRESH_OWNED_DIR`
for the native scene. Run .NET
`res://Scenes/Frontend/Tests/ConfigurationSceneChecks.tscn -- --skipfmv`
headlessly for the comparison, or add
`--configuration-render-dir=ABS_FRESH_EMPTY_DIR` on a caller-owned isolated
display. Outputs belong below this worktree's `local-data/`. These checks make
no full-combat, physical-input, audible-playback, GPU-performance or Windows claim.

#### Native Mission Briefing — September 23

`MissionBriefing.tscn` replaces the remaining briefing draw callback with
editable Background, Header, LevelName, Body and Navigation sections. It reuses
the Configuration background resources and controls, atlas labels/fonts and
signed arrow component. `Body/Text` owns raw UTF-16 paragraph layout with the
original source rectangle, float32 width/y arithmetic and 286-pixel ceiling.
The narrow host forwards the selected world's name and paragraphs in one batch
and retains session/input/audio/navigation ownership. Frozen editor facts reuse
the native world-100 text table. The former methods and measurement provenance
remain in `Tests/BriefingReference*` from `51477f62`.

The retained executable behavior splits only on ASCII space, keeps empty tokens,
wraps when the current line is nonempty and its candidate exceeds 286, and leaves oversized words whole.
Explicit empty paragraphs advance by 10; nonempty lines advance by 16.
Nonempty paragraph boundaries insert no extra gap. An empty *list* chooses the
nine-element world-100 fallback, including its explicit blank element. This
contradicts the old renderer's comment promising to draw nothing for an empty
session body. The normal two-paragraph Level 100 text therefore has different
vertical spacing from that fallback. Conversion preserves both behaviors;
neither is newly asserted as faithful retail policy. The cheapest falsifier is
a controlled retail observation of paragraph/line submissions for the normal
world-100 pair and a missing selected-world body, rather than another comparison
against the C# reconstruction. The missing video inset, header endcaps and
Forseti emblem remain open; no black video placeholder was introduced.

The existing selected-world wiring test now reads the live bridge/native body
owner. Its table-pair assertion remains unchanged, but its comment no longer
claims to execute the separately wrapped fallback. The old renderer cited
`RetailFrontendFlowWrapTests`; no such test exists in this tree. The new native
and retained-reference layout harnesses directly compare those wrapping paths.

Executed receipts under this worktree's `local-data/test-runs/`:

- `briefing-native-n8nuftpf/result/report.json`: **317 checks**, nine groups,
  zero failures in standard headless Godot. Includes the 286/287 width boundary,
  explicit blanks, repeated spaces, oversized words, raw UTF-16, frozen editor
  facts, authored edits and pack/reopen without private pixel serialization.
  Fifteen public sources and five private inputs retained their hashes; both
  existing-output/symlink refusal probes passed. Runtime diagnostics are clean.
- `briefing-integrated-4pwpv8yi/`: the supported .NET build and private Level 100
  import passed with zero build warnings/errors. `report.json` then passed
  **2,656 checks**, sixteen states and five groups against the retained renderer
  and actual host. Both new-career World 100 and read-only gold-fixture World 110
  navigation preserve callback ordering and the exact career/save handoff.
  An earlier harness attempt omitted Load's required row selection and correctly
  stopped at the Level Select assertion; the setup now selects that row through
  the existing input path. Production navigation was not changed to pass it.
- `briefing-render-hafevgwd/report.json`: **2,726 checks**, **27 exact native/
  live-host image comparisons**, zero differing RGBA bytes. Coverage includes
  both worlds at 640×480, 1280×720, 801×601 and 320×240, empty-body fallback,
  explicit blank paragraphs, spacing/long-word/raw-unit cases, authored body/
  header/name edits and explicit text overrides. The World 100, World 110 and
  edited-body host images were inspected. Isolated Xvfb used task-owned
  credentials/profiles, software rendering and Dummy audio; credentials and
  processes were cleaned up. Only the expected XIM/V-Sync warnings appeared.
  The tracked save fixture and seven private inputs retained their hashes.
- `briefing-editor-dxzv_m5b/`: import and runtime scene checks exited cleanly;
  all ten frozen editor pages and edit/pack/reopen checks passed. Briefing
  neither acquires input nor starts a world, and resizing its section does not
  replace the measured wrap ceiling. The editor check still reports the same
  **205 ObjectDB/associated RID shutdown leaks**; this is a functional pass.
- `briefing-startup-_xalh0md/run/capture-manifest.json`: **13/13** scheduled
  startup shots matched their expected screens through Loading, without save
  errors, at 640×480 on the isolated display.
- `briefing-client-tw27nast/results/briefing.trx`: **127 affected Client tests**,
  **126 passed, one failed, zero skipped**. The fresh CareerName/LevelSelect
  retail header gate retains the same y71..87 versus y72..88 discrepancy above.
  It does not measure Briefing. No assertion or expected hash was weakened.
- `briefing-smoke-s5gy8vs8/`: **2,148-step** lifecycle smoke and both recorded
  tape replays passed. The tape, trace and final-state hashes match the
  Configuration receipt above. Thirteen ordered message deliveries/queues,
  synthetic focus-loss/rearm, fresh retry and Main Menu return/world release
  passed with clean logs. Outcome remains `Running`, zero targets destroyed;
  this is not full-combat acceptance.

Run standard `--headless --script
res://Scenes/Frontend/Tests/briefing_scene_checks.gd -- ABS_FRESH_OWNED_DIR` for
the native scene. Run .NET
`res://Scenes/Frontend/Tests/BriefingSceneChecks.tscn -- --skipfmv` headlessly,
or add `--briefing-render-dir=ABS_FRESH_EMPTY_DIR` on an isolated owned display.
Outputs belong below this worktree's `local-data/`. Conversion equivalence is
not full retail, full-combat, physical-input, audible-playback, GPU-performance
or Windows acceptance.

#### Native Level Select — September 23

`LevelSelect.tscn` replaces the final legacy frontend page draw callback with
authored background/guides, three arcs, sixteen links, twelve node groups and
thirteen ring passes, bracket/shadow, labels and navigation. Narrow typed
controls retain the original `draw_arc`/`draw_line` operations, float32 inputs,
draw order and full-stage source coordinates. Ring sprites share the existing
production component; font, underlay and texture resources are shared with
other pages. Authored node changes update connected link endpoints and targets.
The original renderer and measurement provenance are retained in
`Tests/LevelSelectReference*` from `51477f62`.

The host supplies only the selected name and FEBack time, and retains the
session's selection/input/audio/loading order. The settled graph still
highlights node zero even when World 110 supplies the name. Its node hit regions
remain above the ring centers. Clicking World 100 confirms even when unchanged;
World 110 confirms only when `SelectWorld` accepts the change. The other
discarded `RetailLevelSelect*` evidence-helper results do not become newly
invented positions, fades or animation. Missing emblem, header endcaps, amber
node-center art and faint writing remain undrawn. The arcs retain their current
alpha blend; the retail additive appearance is a separate unresolved gap.

With no remaining consumer, the production `RetailFrontendPart` proxy, draw
dispatch, C# glyph renderer and duplicated texture/font handles are removed.
The root still owns frontend orchestration in C#. Existing numerical/evidence
tests remain intact; their old source-consumption checks explicitly target the
retained reference. Production page-fill guards now read the live native
clear/darkener/composite owner. Options and Debriefing comparison harnesses
use the retained, unchanged C# glyph/FEBack methods and inspect shared native
font resources instead of removed live C# fields.

Executed receipts under this worktree's `local-data/test-runs/`:

- `level-select-native-y68doiup/`: **813 checks**, nine groups, zero failures
  and clean shutdown in standard headless Godot. Covers authored content,
  production assets, exact geometry, detached facts, half-open hit bounds,
  node/link/target edits, frozen preview and pack/reopen without private pixels.
  Twenty-four source hashes and eight private-input hashes stayed unchanged.
  Both existing-output/dangling-symlink refusal probes passed. The initial
  detached-node test incorrectly expected resolved fullrect sizes before tree
  entry; it now checks stored anchors/offsets, then actual sizes after Ready.
- `level-select-integrated-1ao4c4xq/`: supported .NET build/private Level 100
  import passed with zero build warnings/errors. **7,669 headless comparisons**,
  fourteen states and five groups passed against the retained renderer and
  actual host. Exact arc/link/ring submissions, decoded fonts/textures, FEBack
  phase boundaries, five-size hit bounds, actual new/load navigation, callback
  order and original gold-fixture identity are checked. Updated Options host
  checks passed **6,048**, including observer failure/reentry; Loading passed
  **234**. All runtime logs are clean.
- `level-select-render-6cmfdlzs/report.json`: **7,733 checks**, **25 exact native/
  live-host image comparisons**, zero differing RGBA bytes. Includes World 100
  and 110 at four viewport sizes, fractional scaling, empty/raw UTF-16 names,
  whole-page position/size/scale/rotation edits and explicit text overrides.
  World 100, World 110 and edited-size host images were inspected. Task-owned
  Xvfb, separate credentials/profiles, software rendering and Dummy audio were
  cleaned up; only expected XIM/V-Sync warnings appeared. Fixture/input hashes
  remain unchanged. This measures equivalence to the reconstruction, not retail.
- `level-select-editor-ca4vdy7v/`: updated Debriefing checks passed **212**,
  and editor import exited cleanly. `level-select-editor-final-mld1ihef/` then
  passed all ten frozen page selections and runtime/editor edit/pack/reopen.
  The integration test initially set Position before Size on a fullrect node;
  Godot's centered grow direction shifted that position by half the size delta.
  It now sets Size before the final Position and still requires the exact
  requested rectangle to persist. No production change or assertion relaxation
  was needed. Runtime is clean; editor teardown retains the same **205 ObjectDB/
  associated RID leaks**.
- `level-select-startup-ltpjeizc/`: all **13/13** fresh startup shots match their
  expected screens through Loading with no save errors. The affected Client
  gate executed **164 tests: 163 passed, one failed, zero skipped**. The unchanged
  CareerName/LevelSelect retail header assertion still finds y71..87 versus
  y72..88. No expected hash, retail glyph bound or numerical assertion changed.
- `level-select-smoke-rw3g4ll9/`: the **2,148-step** lifecycle smoke and two
  replay runs passed with the same tape, trace and final-state hashes recorded
  above. Thirteen ordered message deliveries/queues, synthetic focus-loss/rearm,
  fresh retry and Main Menu return/world release passed with clean diagnostics.
  Outcome remains `Running`, zero targets destroyed; full combat remains open.

Run standard `--headless --script
res://Scenes/Frontend/Tests/level_select_scene_checks.gd -- ABS_FRESH_OWNED_DIR`
for the native scene. Run .NET
`res://Scenes/Frontend/Tests/LevelSelectSceneChecks.tscn -- --skipfmv` headlessly,
or add `--level-select-render-dir=ABS_FRESH_EMPTY_DIR` on an isolated owned
display. Use this worktree's `local-data/` for outputs. These checks establish
neither full-combat completion nor physical input, audible playback, normal
GPU performance or Windows behavior.

#### Native Pulse impact — September 23

`Scenes/World/PulseImpact.tscn` now supplies the production blob, flash and
shockwave sphere. The native controller receives the existing float32
presentation clock at explicit start. The C# host retains event dispatch and
scene instantiation; its remaining effect construction/animation helpers are
removed. This preserves the reconstruction's `1.07f` blob scale endpoint,
callback-only random initial atlas cell and separate 1.05-second lifetime.

Executed headless checks use fresh owned profiles under `local-data/test-runs/`:

- `pulse-impact-verified-8m0p7zn8/`: supported build/private import passed with
  zero compiler warnings/errors; all **22** affected Client tests passed with
  zero skips. The entity harness passed **78,830 assertions**, including **4,306
  exact shockwave arithmetic cases** for scale, UV, RGBA and initial scroll.
  Dense float32 ages, boundary neighbours, signed zero and large/nonfinite clock
  values match the retained `b8c1a220` operations without tolerances. Nonfinite
  clocks are tested through the same pure production helper without assigning
  invalid transforms to nodes.
- The same harness compares nineteen actual native/retained tween steps,
  initial callback timing, captured materials, parent/child lifetime ownership,
  independent instances, one RNG draw and its unchanged suffix. All three
  decoded texture pages match the old loader, and prepared input hashes remain
  unchanged. The public event route preserves actor/tick naming, coordinate
  conversion and a nonzero host clock.
- `pulse-impact-client-final-f4qn38jb/`: all **22** affected Client tests passed
  again after retaining the size guard's rejection of unregistered effect meshes.
- `pulse-impact-native-ctsr0w79/`: standard-engine parsing and **195 runtime
  assertions** passed with clean logs. **171 editor assertions** passed for
  authored geometry/artwork, inactive timers/tweens/input and scene packing
  without private pixels. The scripted editor still reports the same **166
  ObjectDB instances** and RID shutdown diagnostics; its strict clean-log gate
  remains failed.
- `pulse-impact-smoke-aonolece/`: the normal startup/menu/Level 100/retry/
  Main Menu smoke passed **2,148 ticks**, followed by two verified replay
  repetitions. Recording, trace and final-state hashes match the destruction
  milestone below; runtime logs are clean. The mission remains **Running /
  None** with **zero targets destroyed**, so this does not establish full combat.

Use the existing `EntityBridgeChecks.tscn` and `entity_scene_checks.gd` commands
below. These comparisons preserve the current implementation; they do not prove
complete retail combat, normal GPU performance, physical input, audible audio
or Windows execution.

#### Native destruction scenes — September 23

Tank, drone and facility destruction now instantiate authored scenes driven by
`Scenes/World/destruction_effect.gd`. Their retained layers share four native
texture recipes, including the blob and flash objects also used by Pulse impact.
The original six texture-admission slots remain ordered. Existing representative
emitter limitations are unchanged; no debris, placement, velocity or colour law
was inferred to fill them.

Headless checks used fresh owned profiles under `local-data/test-runs/`:

- `destruction-scenes-final-1c6ey79n/`: supported build/private import passed
  with zero compiler warnings/errors. The entity harness passed **29,444
  assertions**, including paired native/retained schedules for all three
  families, raw UV/scale/colour/elapsed words, visibility, captured materials,
  independent siblings, lifetime timers and actual public event routing.
  Texture bytes match the retained loader and source hashes remain unchanged.
  RNG checks preserve exactly **1 / 1 / 2** start draws for tank/drone/facility,
  with facility fireball before smoke and no further animation draws.
- `destruction-scenes-client-hdrlknux/`: all **21** affected Client tests passed,
  with zero skips. Descriptor and numerical assertions are unchanged. The size
  guard now follows each named scene layer to its own QuadMesh resource.
- `destruction-scenes-native-71rcgquf/`: standard-engine parsing and **172
  runtime assertions** passed with clean logs. **148 editor assertions** passed
  for real artwork, scene round-trips, private-pixel exclusion and inactive
  timer/tween/input state. The same **166 ObjectDB instances** and associated
  RID shutdown diagnostics remain; the editor's strict clean-log gate failed.
- `destruction-scenes-smoke-epp65z9f/`: the normal startup/menu/Level 100/retry/
  Main Menu route passed **2,148 ticks**, followed by two successful replays.
  Runtime logs are clean; recording, trace and final-state hashes are unchanged
  from the world milestone below. This also exercises admission of the shared
  recipes by the remaining managed host. The mission remains **Running / None**
  with **zero targets destroyed**, so this is not combat-completion evidence.

Run the existing `EntityBridgeChecks.tscn` and `entity_scene_checks.gd` forms
below. These are comparisons against the retained `673b630a` reconstruction,
not new retail-completeness or GPU-performance claims.

#### Native Vulcan impact — September 23

`Scenes/World/VulcanImpact.tscn` now supplies the production direct spark's
billboard, material and stopped lifetime timer. Its GDScript controller retains
cells 11–15, four binary64 intervals, the Single-rounded scale target, separate
timer/tween ownership and zero RNG draws. The two unresolved sibling emitter
branches are still absent. The existing muzzle controller also now retains its
original animated material in callbacks, matching the former C# closure when a
mesh is removed or its material override changes.

All execution was headless with owned profiles under `local-data/test-runs/`:

- `vulcan-impact-complete-uv1uho4u/`: supported build/private import passed with
  zero compiler warnings/errors. The entity harness passed **23,362 assertions**,
  including exact decoded texture bytes, boundary-step UV/scale/completion,
  independent instance materials, captured-material behavior, child/root
  lifetime comparisons, unchanged source bytes and seeded RNG state. The actual
  public destruction-event path uses the native scene with the original name,
  coordinate conversion and timer. All **21** affected Client tests passed,
  with zero skips and unchanged descriptor/hash/radius expectations.
- `impact-callback-native-1a_dhx8e/`: the final standard-engine runtime check
  passed **105 assertions** with clean logs. The preceding
  `vulcan-impact-native-2i0j1bnv/` editor check passed **81 functional assertions**,
  including frozen artwork, inactive time/input and scene packing without private
  pixels. It retains the same **166 ObjectDB instances** and RID diagnostics as
  the world check below; its strict clean-log gate remains failed.

Earlier harness failures assumed that reaching the final atlas cell immediately
reported tween completion, and that freeing a bound node immediately invalidated
its tween. The final checks compare the actual retained C# behavior through one
additional observation step and identical frees. Production timing, numerical
tolerances and expected hashes were not changed to satisfy those assumptions.
Use the existing `EntityBridgeChecks.tscn` and `entity_scene_checks.gd` launch
forms below. These checks establish component migration, not complete combat,
physical input, audible playback, normal GPU performance or Windows behavior.

#### Native world presentation — September 23

The actual private Level 100 scene now embeds `WorldPresentation.tscn`.
`world_presentation.gd` owns player interpolation, foot conversion, Aquila
transitions, camera/projection application and environment update order.
`static_world_animation.gd` owns scenery's double clock and discrete rigid-part
frames. The temporary C# facade submits one immutable snapshot pair and caches
detached display facts. Its former camera adapter is test-only. Import
construction, full simulation and replay entry still need
conversion; the full game still requires .NET.

Executed checks use owned profiles and outputs under this worktree's ignored
`local-data/test-runs/`, with the canonical lab read in place:

- `world-presentation-final-r19du5l7/`: standard-engine parsing and the supported
  .NET build/private import passed with zero compiler warnings/errors. Scenery
  animation passed **84,395 assertions**, including raw transform words, pinned
  private tracks, discrete frame selection, wrapping, alias order and partial
  failures. Camera **852**, entities **23,038**, and the actual imported world
  **24,177** checks passed. The world check covers authored geometry/materials,
  round-trip, shared production nodes, retry isolation and unchanged snapshots.
- `world-frame-verified-umx3qe6v/`: the final supported build/import passed.
  The combined controller passed **112,833 assertions** against retained
  `1bb29345` arithmetic on identical authored node state. Six completed groups
  cover initialization, player/Aquila/camera, partial writes, deferred target
  and projectile failures, nonfinite transition math and disposed scenery.
  The extreme Int32-coordinate case produces the same engine `look_at` refusal
  in both implementations. Those two diagnostics remain in the receipt; this
  is an exact comparison pass, not a clean-log claim for that adversarial case.
- `world-frame-client-havrl4nl/`: **72/72** affected Client tests passed, with
  zero skips. Camera/viewpoint, interpolation, scenery, particle and measured
  Aquila material expectations remain unchanged. Only source-wiring checks
  moved to the actual native controller.
- `world-frame-native-yyh3b6fb/`: standard Godot passed **95 runtime** and
  **71 editor** assertions. Native templates retain their production artwork;
  the world controller starts no processing, camera, clock, gameplay or input
  owner. Editor configuration is refused before admission. The scripted editor
  shutdown still reports the existing **166 ObjectDB instances** and associated
  RID allocations, so its strict clean-log gate remains failed.
- `world-frame-smoke-jkomlsmt/`: the normal headless startup→menus→Level 100→retry→
  Main Menu smoke completed **2,148 ticks**, followed by two successful replay
  repetitions. Runtime logs are clean. The recording, trace and final-state
  hashes are unchanged from the frontend milestone below. Thirteen ordered
  deliveries/queues and world release remain verified. The mission still ends
  **Running / None**, with **zero targets destroyed**; this is not combat
  completion.

The first combined comparison exposed a fixture error: its fresh identity
player node did not share the saved world's decomposed scale. The bounded probe
in `world-yaw-probe-5tc9_gy3/` reproduces the one-ULP difference with the same
yaw word and no renderer call. The final oracle captures the authored transforms
and flags before initialization. No production arithmetic, tolerance or expected
hash changed to resolve that fixture issue.

Run .NET `res://Scenes/World/StaticAnimationChecks.tscn` and
`res://Scenes/World/Tests/WorldPresentationChecks.tscn` with the supported
headless launch form and Dummy audio. The existing camera, entity and world
scene harnesses use the same form. Standard
`--script res://Scenes/World/entity_scene_checks.gd` checks the native templates
and inactive controller; add `--editor` for the editor guard. These comparisons
do not establish normal GPU performance, physical input, audible playback,
Windows behavior or full-combat completion.

#### Native frontend orchestration — September 23

`Frontend.tscn` now uses `frontend_flow.gd` as its actual Control script. It owns
its one native Session, clocks, input, page binding, loading and intro completion.
`frontend_pages.gd` configures the same ten production pages in their original
order. `RetailFrontendFlow` is now a non-Node managed facade for coarse commands,
verified save identities and synchronous typed host callbacks. No managed frame
loop or per-page frame batch remains. C# scene comparison helpers live under
`Scenes/Frontend/Tests/`; their retained numerical/pixel expectations are unchanged.

The conversion preserves failure points as well as successful navigation. In
particular, an initialization observer can replace `AssetPaths` before later page
reads; failed localization retains the preceding Add/field writes; and a host
observer can throw or reenter after a loading mutation. Native checked results
stop the interrupted operation. Explicit facade calls rethrow the same managed
observer exception and retire their temporary exception tokens. JSON reader
failures cross that temporary facade as public `JsonException` (the original
.NET `JsonReaderException` subtype is internal); native admission and its failure
ordering remain checked separately.

Receipts are under this worktree's ignored `local-data/test-runs/`:

- `frontend-native-parse-qvcqjlll/`: standard-engine parser check and **177
  localization assertions** across five groups passed. Partial writes, all ten
  field boundaries, duplicate Add/retry order, last JSON property, raw UTF-16 and
  the unchanged atomic loader APIs are covered.
- `frontend-native-scene-kwtjx7c_/`: the complete frontend passed the existing
  standard-engine runtime scene inspection, shared production assets, layout
  editing, pack/reopen and private-pixel exclusion checks.
- `frontend-flow-editor-gnibq925/`: the complete standard-engine headless editor
  passed all ten frozen page selections, authored edits and pack/reopen, without
  pointer, gameplay or audio ownership. The known scripted editor exit still
  reported **166 ObjectDB instances** and associated RID allocations; this was
  a functional pass, not a clean editor shutdown.
- `frontend-flow-final-nl0k8ksd/`: supported .NET build and private Level 100
  import passed with no compiler warnings or errors. All twelve managed
  frontend harnesses passed: Session **1,025**, Options **6,048**, Loading
  **234**, Debriefing **212**, Cursor **20**, Click **136**, Main Menu **1,832**,
  Quit **1,457**, Career Name **6,338**, Configuration **1,997**, Briefing
  **2,656** and Level Select **7,669** assertions. Session includes **57**
  focused synchronous callback failure/reentry assertions, exact original
  exception identity, partial mutations and exception-token retirement. Settled
  native frames make no facade calls or redundant host-state notifications.
- `frontend-flow-client-oy654utz/`: affected Client checks passed **436**, with
  **one existing capture-dependent HeaderFont skip**, no failures and a clean
  compile. Numerical fixtures remained unchanged; source-wiring checks now
  inspect the actual native owners.
- `frontend-flow-native-verified-chad7xnz/`: standard Godot passed **35** focused
  controller assertions across route precedence, initialization failure/retry
  and native timing/input. Its report separately exposes **one environment
  parity gap**, described below. The runtime and editor scene checks again
  passed all ten editable pages, shared assets and private-pixel exclusion;
  the editor retained the same **166-instance** shutdown allocation warning.
- `frontend-flow-render-51phmvq_/`: isolated authenticated Xvfb and llvmpipe
  comparisons passed **2,282** Main Menu and **33** cursor assertions. All
  **178 Main Menu** and **six cursor** image pairs matched their retained
  C# rendering references exactly. Private captures stayed in the owned output
  directory; the display, credentials and child processes were cleaned up.
- `frontend-flow-smoke-19wub5xx/`: final supported build/private import passed,
  followed by the headless startup→menus→Level 100→retry→main-menu smoke and
  two replay repetitions. The **2,148-tick** run retained trace hash
  `a4e6673b92e651c05fcd2ddc2c10932d325db0f7d8db1d774e9c60ede43c58f2`
  and state hash
  `53c1cc64ace55542f48534d0554d6ffed57dda0eae48c9f2a55a928fea096e5e`.
  Its mission remained **Running / None**, with **zero targets destroyed**;
  this is lifecycle/replay evidence, not combat completion.

The route check initially failed **one of 34** assertions in
`frontend-flow-native-final-3w5um7z2/`. The isolated probe
`frontend-env-probe-igpwftri/` establishes that pinned Linux Godot's
`OS.get_environment` removes a leading U+FEFF, including a BOM-only value.
The .NET probe in `frontend-flow-smoke-19wub5xx/` preserves both cases and
does not classify them as whitespace. A BOM-only native environment value can
therefore fall through to another media owner. The final native report keeps
the original expected bytes and actual route under `parity_gaps`; it does not
claim equivalent environment routing. The actual prefixed command-line probe
in `frontend-flow-native-verified-chad7xnz/` preserves U+FEFF through
`--startup-media=`. Open question: can a later pinned engine expose environment
values without this loss? Re-run this focused probe when reviewing that engine;
do not change the whitespace law or infer that retail paths contain this edge.

The standalone frontend has no world-construction callback; reaching Loading
there does not establish a standard-engine game. Full combat completion remains
unresolved. Software rendering, headless input events and synthetic handoff
fixtures do not establish physical input, audible playback, normal GPU performance
or Windows behavior. Existing retail header/art and editor shutdown gaps remain.

Run standard `godot48 --headless --audio-driver Dummy --path
rebuild/OnslaughtRebuild.Godot --script res://Tests/frontend_localization_checks.gd`
for the pure admission checks. The production scene harness remains
`res://Scenes/Frontend/Tests/frontend_scene_checks.gd`; add `--editor` for its
frozen editor path. Run the standard engine with
`--script res://Tests/frontend_flow_checks.gd -- --skipfmv` for controller checks;
inspect its `parity_gaps` as well as `failure_count`. Run .NET
`FrontendSessionSceneChecks.tscn` with `--skipfmv`
and an explicit absolute `--gold-career-fixture=.../tests_shared/fixtures/gold_career_save.bin`
for its managed host, exact verified object identity and read-only fixture checks.

#### Native cursor and asset routing — September 23

`MouseCursor.tscn` now owns the production final frontend draw; `Frontend.tscn`
embeds that scene and an actual black `Letterbox` control. The cursor preserves
the measured 32×32 quad, 124×124 UV region, literal white, exclusion of Loading /
IntroCutscene / Gameplay, unclamped top-left placement and late draw order.
Only an explicitly configured runtime source permits live pointer sampling,
after lazy texture admission in `_draw`. Editor previews remain frozen and the
full frontend leaves the game cursor hidden. The managed host no longer draws
page content, the cursor or the letterbox; navigation and clocks remain there.
The old cursor predicate and renderer remain test-only references from
`92c1775b` with their existing provenance.

`RetailFrontendAssets.tres` now uses a typed GDScript routing Resource with the
same exported field names. Override lookup still precedes folder validation;
nonblank override text is returned exactly and only trailing ASCII slashes are
trimmed from a default directory. The temporary C# wrapper transports raw UTF-16
and maps checked failures; it does not contain a second path resolver.

Executed receipts under this worktree's `local-data/test-runs/`:

- `cursor-native-final-xz5w3ro_/`: **104 standard-headless checks**, all eight
  groups, clean shutdown. Covered live-source lifetime, deterministic capture
  override, missing-file retry, actual curated DXT2→RGBA8/eight-mip admission,
  frozen geometry edits, scene reopening and the explicit fractional draw fit.
  Both output-refusal probes passed in the initial `mouse-cursor-native-xioyz1cs/`
  run; all ten source hashes and the measured mouse texture hash were unchanged
  within each native run.
- `frontend-asset-paths-final-4rxabo62/`: **126 standard-headless checks**, all
  six groups, clean shutdown. Exact routing, Unicode whitespace, raw UTF-16,
  null/error order, exported metadata, resource duplication and ordinary
  edited-resource save/reload passed. No texture or save was opened by this gate.
  The pinned engine's `.tres` reload strips a leading U+FEFF from both built-in
  `Resource.resource_name` and the native directory field. The receipt records
  both carriers' before/reloaded units; direct routing keeps the same character.
  Earlier failing resource receipts are retained. No custom serialization or
  altered retail assertion was introduced to hide this engine limitation.
- `cursor-final-49t3lwxo/`: the supported pinned .NET build/private Level 100
  import passed with zero build warnings/errors. **967 frontend session checks**,
  **20 cursor host checks**, the runtime ten-page edit/pack/reopen check and
  **33 affected Client tests** passed with clean diagnostics. The initial
  `cursor-host-0l6yfzk5/` integration also passed **6,048 Options checks** including
  synchronous observer failures/reentry, and **234 Loading checks**.
- `cursor-render-final-c2nr_vn5/`: **33 checks**, **six exact composed-image
  comparisons**, zero differing RGBA bytes. Four viewport sizes cover the actual
  menu reflection, fractional cursor coordinates and unclamped off-screen draws.
  Inspection included the 801×601 image. The first rendered attempt exposed
  Control pixel snapping of Stage's y=0.125 offset: 1,061 cursor RGBA bytes differed.
  Keeping the native cursor beside Stage and submitting the original explicit
  fit inside the draw callback removed that rounding, without changing expected
  pixels or globally disabling GUI snapping. The isolated X server/client and
  credentials were cleaned up; only the expected XIM/VSync warnings remain.
- `cursor-editor-3xqc8m9g/`: headless editor import was clean. All ten actual
  pages, the letterbox, inactive cursor, shared resources and authored edit /
  pack / reopen checks passed without changing pointer mode. Scripted editor
  teardown still reports the previously recorded **205 ObjectDB instances**
  and associated RID allocations; runtime checks remain clean.
- `cursor-smoke-36w1xotj/`: the supported **2,148-step** lifecycle smoke and
  two replay runs passed with unchanged tape, trace and state hashes recorded
  above. Thirteen ordered message/audio queues, synthetic focus-loss/rearm,
  fresh retry, Main Menu return, world release and cursor policy all passed.
  Outcome remains `Running`, zero targets destroyed; this is not full combat.

Run standard `--headless --script
res://Scenes/Frontend/Tests/mouse_cursor_scene_checks.gd -- ABS_FRESH_OWNED_DIR`
or `frontend_asset_paths_checks.gd` with the same arguments. Run .NET
`res://Scenes/Frontend/Tests/MouseCursorSceneChecks.tscn -- --skipfmv` for host
integration; `--cursor-render-dir=ABS_FRESH_EMPTY_DIR` additionally compares
rendered output on an isolated owned display. Outputs belong under this
worktree's `local-data/`. These checks do not establish physical input,
audible playback, normal GPU performance, Windows behavior or combat completion.

#### Live native input edges — September 22

`FirstFlightGame` now injects the existing `Client/platform_input_edges.gd`
owner into its actual `InteractiveSession`. The temporary managed bridge has
no mirrored key/joystick maps. Its native resource is released on retry, world
release and shutdown, including partial-load failure paths. The standalone
C# state remains the comparison/default for managed consumers; simulation and
the rest of the session have not been converted by this change.

The earlier standard-engine input foundation receipt remains
`gdscript-parity-9mt08bqg/client-input.json` (**3,855 checks**). The adoption
adds these executed checks under the same worktree's `local-data/test-runs/`:

- `input-bridge-client-ewvs9xkq/`: **58** affected platform/session tests plus
  **5** pause integration tests passed, zero skips. The new injection test
  proves the borrowed owner receives the original frame/reset lifecycle.
- `input-bridge-headless-b5v2o4sr/report.json`: **3,891 checks**, **526**
  reference operations and **11** explicit session-frame calls; all five
  groups completed with zero failures and a clean runtime log. Coverage
  includes Echo, release-latched presses, byte values through 255, signed
  Int32 IDs, signed Int64 counters beyond binary64 precision and overflow,
  detached captures, refusals, disposal, actual host create/release/retry,
  focus/pause resets and exact paired-session event/state/tape bytes.
  The admitted manifest and source inputs retained their recorded hashes.
  The paired-session final state was
  `04c5aaaa7dd5de5712f4c08c343b782efb47277e28afea1118a8a0785b20543a`,
  trace `a36d1d4e7084976e4919b51a132949f69b3c9468e62bfcffc33df630171facf6`.
- `input-bridge-build-fixed-8h7_09jw/`: supported pinned .NET build and private
  Level 100 import passed with zero build warnings/errors.
- `input-bridge-smoke-25y8sm09/`: live native-input gameplay completed the
  existing **2,148-step** smoke with focus-loss/rearm, fresh retry and world
  release at Main Menu. Its tape remains byte-identical to the Quit milestone,
  SHA-256 `89ca7b4ba0642c7fa1e68bbaf1875c724762a5d3ef6902182110da84706db14a`.
  Two replays (`input-bridge-replay-b4cfw8j5/`) verified the same full-smoke
  trace/state hashes recorded above with no first divergence. Runtime logs
  are clean. The mission remains `Running`/`None`, zero targets destroyed;
  this is regression evidence, not full-combat acceptance.

Run .NET `--headless --audio-driver Dummy --path GODOT_PROJECT
res://Tests/PlatformInputBridgeChecks.tscn` with an isolated owned profile.
The harness reports to stdout and writes no files; the caller owns its log.
It never samples physical devices or enters the game tree. Explicit paused
session API calls advance input history once; the actual host still returns
before making those calls while paused. This conversion preserves that
distinction. Retail repeat policy and joystick polling cadence remain open;
these checks do not establish physical-device behavior or full combat parity.

#### Native weapon foundations — September 22

The standard-engine comparison passed **89,663 assertions** over all nine
required groups: 1,299 charge sequences/14,331 steps, 1,521 readiness cases,
1,788 store cases, 787 cycles and 1,106 Unit scorer/selection cases. It checks
raw float words, aliasing, failure ordering, detached values and public input
admission against the unchanged C# owners. The first run exposed 90 NaN-payload
differences; explicit current-charge-first payload selection and quieting fixed
them against the same fixture. This is managed regression evidence, not proof
of retail behavior for synthetic NaNs.

The final receipt is `retail-weapon-final-xp45flg1/native.json` under the
conversion worktree's `local-data/test-runs/`; it records all four source
identities and fixture SHA-256
`9f5faddbd2d074057c252d606b9103240107f3d5cd55544ab854e84ab9573b9d`.
The incomplete-fixture/missing-source controls and eight output refusal checks
preserved their inputs and sentinel bytes. All **149** existing affected Core
tests also passed, with no skips (`retail-weapon-core-ug8izsg6/core.log`).
Runtime logs are clean. Run the .NET `Scenes/World/Tests/RetailWeaponReferenceChecks.tscn`
with fresh absolute fixture/report paths, then standard
`Scenes/World/Tests/retail_weapon_checks.gd` with the fixture and a fresh report;
both outputs belong below this worktree's `local-data/`. Live weapon scheduling,
effects, event order and full combat remain with their existing owners.

#### Completed actor foundations

The mutable native actor registry passed **2,756 assertions** against the
unchanged C# owner: **190** construction/restoration cases and **333** operations
over **12** definition sets. Checks compare full ordered snapshots after both
successful and refused operations, authored/spawned identities, raw Plane
creation/exit poses, lifecycle/fact ordering, UTF-16 lookups, immutable restore
admission, signed fact-sequence wrap, detached inputs and owner lifetime.
The fixtures include the actual 44-actor/10-spawn Level 100 definitions; no live
consumer or simulation hash expectation changed. The guarded getters preserve
the shared Thing/Actor allocation rather than restoring another mutable owner.
Reference/native receipts are `actor-registry-reference-fd7qq2nu/` and
`actor-registry-native-3k47ow66/`; both logs are clean. The source-only check is
`actor-registry-parse-v2rb1xvb/`. Run .NET
`Scenes/World/Tests/ActorRegistryReferenceChecks.tscn` with a fresh absolute
`.variant` fixture and report, then standard
`Scenes/World/Tests/actor_registry_checks.gd` with that fixture and a fresh report.
Outputs stay under the owned worktree's `local-data/`. Live mission scheduling,
collision handling and complete registry adoption remain unconverted.

The pure Thing/Actor base-state port passed **18,548 native assertions** against
the unchanged Core implementation on Godot-hosted .NET 10.0.12: 818 factory/restore
cases, 993 mutation/getter operations, 2,884 projection/angular-law cases and
349 derived-property cases. Checks retain signed float words (including signed
zero), checked overflow, wrapped movement subtraction, flags/type words,
current/old pose order, failure atomicity and detached snapshot ownership.
The existing distinction between allowing a negative motion countdown at runtime
and refusing it on restore is preserved. There is no Godot physics or live
registry integration in this foundation.
Run .NET `Scenes/World/Tests/ThingActorStateReferenceChecks.tscn` with two fresh
absolute fixture/report paths under this worktree's `local-data/`, then standard
`Tests/thing_actor_state_checks.gd` with the fixture and a fresh report path.
Receipts `thing-actor-state-8_v6hbwr/`, `thing-actor-final-g2de2np9/` and
`thing-actor-export-final-a1n8p3qa/` under `local-data/test-runs/` have clean runtime
logs. Both harnesses also refused dangling output links without creating the
target; the final exporter produced unchanged fixture SHA-256
`efc4403db2d972cf6d02b020cbae16c82d86ec80d81d66466e67f5324a859da1`.

The pure mesh-part pose port passed **53,592 native assertions**, including
**14,058 exact raw float words**, against **2,058 unchanged-C# cases**: 1,299
accepted results and 759 expected refusals. The four operations retain their
PC24 evaluation order, signed zeros, intermediate overflow refusals, permitted
final infinity stores and detached outputs. This does not select frames/caches,
port the separate PC53 attachment operations or replace the live registry.
Both runtime logs are clean in `mesh-part-pose-reference-xhdyoaq9/` and
`mesh-part-pose-native-ow95mdhg/` under `local-data/test-runs/`.
Run .NET `Scenes/World/Tests/MeshPartPoseReferenceChecks.tscn` with two fresh
absolute fixture/report paths under the owned worktree's `local-data/`, then
standard `Scenes/World/Tests/mesh_part_pose_checks.gd` with that fixture and a
fresh report path. Both run headlessly with Dummy audio; no retail inputs are
needed. The exporter preserves target framework `net8.0`.

The pure Plane motion port passed **14,741 native checks** against **3,015
direct cases**, 21 sequences with **567 steps**, and **26 restores** from the
unchanged C# owner on Godot-hosted .NET 10.0.12. These cover raw words, PC24
operation order, ignored fields, unusual-basis retention, checked-overflow
failures and atomic Actor commits. Terrain clearance uses the existing sampler;
the canonical heightfield remains unchanged. Reference and native logs are
clean in `plane-motion-reference-ja9aqb18/` and `plane-motion-native-a0njrw3t/`;
both include exact `command.json` invocations. Four final/ancestor output-link
refusals also passed without creating targets (`plane-motion-output-guards-qajfvylq/`).
Run .NET `Scenes/World/Tests/RetailPlaneMotionReferenceChecks.tscn` with two fresh
absolute fixture/report paths, then standard `Tests/retail_plane_motion_checks.gd`
with that fixture and a fresh report, using headless/Dummy audio and owned
`local-data/` outputs. This foundation does not replace the live registry,
collision/lifecycle owners or establish general cross-platform transcendental parity.

The native terrain compositor passed **5,789 assertions** and **17,434,773 exact
compared bytes** against the unchanged C# exporter, which passed **43 checks**.
All 4,096 level-zero tiles reproduce the existing 524,288-byte root and its
unchanged hash. Thirty-two higher-level blocks, five pine-order fixtures,
902 blends, 162 lighting cases, admission and partial-write boundaries also
match. Empty input initially exposed Godot's refusal of `HashingContext.update`
with zero bytes; finishing a started empty hash preserves the original identity
refusal without that engine error. The owner releases after the suspended
comparison coroutine unwinds one process frame later; no forced collection or
weakened release assertion is used. Final logs are clean in
`terrain-compositor-native-fixed-1jn1mha8/`, against
`terrain-compositor-reference-lix2e76b/reference.variant`, under
`local-data/test-runs/`. The reference scene is
`Scenes/World/TerrainCompositorSceneChecks.tscn`; its two user arguments are fresh
owned fixture and JSON report paths. Standard Godot runs
`Scenes/World/terrain_compositor_checks.gd` with that fixture and a fresh report.
These compositor checks alone do not establish cache/material integration or performance.

The native terrain appearance owner passed **397 checks** against **39 exact
ordered snapshots** from eight unchanged C# scenarios. The exporter passed
**13 checks**. Phase words, CPU/GPU cache bytes, slot ownership, alias failures,
retry states, both complete 4,096-record APIs, supplied material/shader identity
and public/private resource round-trips agree. The shader comparison removes
only the added license line and final newline. Receipts are
`gdscript-appearance-reference-wv6mqhsr/` and
`gdscript-appearance-native-fxgx3mvc/` under `local-data/test-runs/`; both console
logs are clean. The original compositor moved into `Scenes/World/Tests/` without
logic changes, and the original appearance owner remains beside it.

The appearance editor harness passed **53 checks** in each engine edition.
It preserves recipe-only public materials and refuses live cache initialization
in the editor. The standard editor scan still encounters retained C# frontend
resources and reports 166 ObjectDB instances at shutdown; the .NET run has the
previously observed custom-harness shutdown diagnostics (205 ObjectDB instances,
viewport/texture/text RIDs and Canvas items). These are not clean editor exits.
Receipts are `gdscript-appearance-editor-6rqstmyf/` and
`gdscript-appearance-editor-mono-7tfxxan6/`. Run
`Scenes/World/TerrainAppearanceSceneChecks.tscn` in .NET with fresh fixture/report
user arguments, then standard `Scenes/World/terrain_appearance_checks.gd` with
that fixture and a fresh report; adding `--editor` selects the inactive-resource
checks. All output belongs to the invoking worktree's private `local-data/`.

The allocation-free presentation float store passed **299,263 raw-word
comparisons** against the former packed-array store, including ties, signed zero,
subnormals, overflow and NaN payloads (`heightfield-fast-float-2szsnnpi/float.log`).
The same bounded twelve-update headless probe measured about 36–40 ms per moving
update before lazy geometry caching and 10–11 ms afterwards. This is a local CPU
observation, not a normal GPU or whole-game performance result. After the shared
store change, Options passed 1,282 scene assertions and its 5,204 pure comparisons,
HUD passed 174 scene assertions, and Sun passed 8,081 comparisons. Pause passed
115 assertions; its deliberate malformed gzip cases still emit engine diagnostics.
Receipts are `float-scene-regressions-em7nufka/`, `gdscript-float-options-a/` and
`sun-fast-float-yvhqwcse/` under `local-data/test-runs/`.

The native Water scene passed **2,702 checks** against the retained C# component,
including exact mesh arrays, decoded bytes from all five textures and **1,173
ordered phase/placement/rebind operations**. The oracle reads surface-format bits
through the native Int64 method; the typed C# enum had discarded bit 35 and is
not an adequate reference for that field. Public-save/private-resource round trips
and failed-input retries also pass. The isolated llvmpipe check passed **2,631
assertions** with **zero differing RGBA pixels** in a 640×360 component image.
It establishes preservation of the current water renderer, not retail pixel parity.
The editor check passed **353 assertions** with the existing 166-object/RID
shutdown diagnostics; automatic preview creates the real three meshes without a
live animation/input owner. Receipts are `gdscript-water-reference-x7culyur/`,
`gdscript-water-native-n62n9z5g/`, `gdscript-water-capture-2k3b287p/` and
`gdscript-water-editor-0lllj7_s/`. The first integrated world check exposed missing
child overrides when Water was nested inside StaticWorld. Water now marks its
private instance editable in the owning parent; two-level save tests compare exact
stored transforms, meshes and materials before binding. The production instance
stays shared with its public template. Fresh import and the unchanged world gate
then passed **24,134 assertions**, including the new shader identity checks,
before-play geometry/materials, selected poses, retry isolation and unchanged
simulation hashes (`gdscript-terrain-water-world-b/`), with clean logs.
The related Client terrain/water selection passed
**6 tests**, with the existing full-gameplay retail-water pixel test **skipped**
without a qualifying capture; its thresholds are unchanged
(`terrain-water-client-q1zscu55/results/terrain-water.trx`).

The native Debriefing scene passed **2,059 runtime assertions** and **2,060 editor
assertions**; the frontend editor selector exercises all ten pages, including
Debriefing's frozen resource without manufacturing a Won session. The actual
host/render comparison passed **274 checks**, with ten complete 640×480 pages
byte-identical to the retained C# renderer. Cases include all outcome labels,
objective-row combinations, grades A–E/S, raw UTF-16 fallback and FEBack times.
The ring uses an authored Node2D origin to preserve the former fractional draw
rectangle without changing GUI snapping for other pages. Client debriefing and
frontend-path tests passed **23/23**, with zero skips. Receipts are
`debriefing-native-1tdcg2z7/`, `debriefing-editor-u_g_ebv4/`,
`debriefing-frontend-editor-zeeht8o1/`, `debriefing-render-8f3zk4v1/` and
`debriefing-client-h1wgdut_/` under `local-data/test-runs/`. Runtime logs are clean;
both editor harnesses finish their checks and filesystem scans, then report 205
ObjectDB instances and Canvas/viewport/text RID diagnostics during teardown.
This does not claim a clean editor-harness shutdown, retail pixels, completed
combat or resolution of the earlier Options Image/RID gap.

The integrated presentation passed the supported .NET build with zero warnings
or errors (`gdscript-terrain-water-build-d.log`) and the headless application
smoke (`gdscript-terrain-water-smoke-a/`). The smoke retains **2,148 steps**, all
13 ordered message deliveries/queues, fresh retry, world release and MainMenu.
Its state hash remains `53c1cc64ace55542f48534d0554d6ffed57dda0eae48c9f2a55a928fea096e5e`;
the recorded tape is byte-identical to the preceding milestone. The two actual
headless replays in `terrain-water-replay-99w1vqgo/replay.log` verify both embedded
expectations and retain trace hash
`a4e6673b92e651c05fcd2ddc2c10932d325db0f7d8db1d774e9c60ede43c58f2`, with no divergence.
Only the smoke's wall-clock audio observation advanced further: seven queued
voices had started instead of four. Both remain the required ordered prefix;
`FirstFlightGame.SampleSmokeVoiceProgress` and its report explicitly distinguish
audio-mixer progress from fixed-fps simulation. Mission state remains **Running /
None**, so this is not full-combat acceptance or an audible-playback result.

The native Loading page passed **165 standard-engine checks**, followed by
**234 integrated host checks** and **316 isolated rendered checks**. All twenty
complete RGBA pages match the retained `DrawLoading` renderer: five loading/raw
UTF-16 cases at 640×480, 1280×720, 801×601 and 320×240. The old composed frontend
had snapped away the source caption's `393.5` vertical anchor. Loading now uses
an authored Node2D origin to preserve that existing value; comparison with the
old composition finds text-only pixel differences, explicitly recorded in
`loading-baseline-3m4xxuni/render.log`. This corrects the scene wrapper, not the
unresolved retail progress-bar behavior. The fixed black bar, two-frame request,
ready handoff and root-hide ordering remain unchanged. Final runtime receipts
are `loading-native-917fgaad/` and `loading-integrated-gp6txn4l/` under
`local-data/test-runs/`; logs are clean apart from the isolated Xvfb driver's
input-method/VSync warnings. These software-rendered comparisons establish no
normal GPU, physical-input or audible-playback result.

Loading passed **166 editor checks** in standard Godot. The full frontend's
.NET editor selector also passed all ten pages, checking Loading's frozen facts,
authored layout, pointer safety and public serialization. Both retain the
custom editor-harness shutdown diagnostics: 166 ObjectDB instances in the
standard run, 205 in .NET, plus Canvas, viewport, texture and text RIDs. No clean
editor exit is claimed. Receipts are in `loading-editor-final-w3epra0x/` under
`local-data/test-runs/`. The related Client selection passed **39/39**, with zero
failures or skips: thirty Loading/source guards and nine terrain compositor,
ambient and macro-cache checks (`loading-client-34tteit_/results/loading-client.trx`).

The combined terrain appearance/Loading integration passed the supported .NET
build and private scene import with zero warnings/errors
(`gdscript-terrain-loading-build-e.log`). The regenerated Level 100 passed
**24,134 world checks** with a clean log
(`gdscript-terrain-loading-world-check-a.log`). The application smoke passed
**2,148 steps**, thirteen unchanged ordered deliveries/queues, fresh retry and
world release at MainMenu (`terrain-loading-smoke-o1oxik06/run/`). Its actual
recording is byte-identical to the preceding milestone: SHA-256
`89ca7b4ba0642c7fa1e68bbaf1875c724762a5d3ef6902182110da84706db14a`.
Two Headless replays verify the embedded trace and final-state expectations
unchanged, with no divergence (`terrain-loading-replay-yafz8_rw/replay.log`).
The audio-mixer observation reached nine voices, still the same ordered prefix;
it is not fixed-step simulation or an audible-playback check. Runtime logs are
clean. Mission state remains **Running / None**, with zero destroyed targets;
full combat acceptance is still open. These receipts are worktree-owned beneath
`local-data/test-runs/` and consume the canonical lab read-only.

Run standard `Scenes/Frontend/Tests/loading_scene_checks.gd` with
`--headless --script`, adding `--editor` for its frozen-resource checks. The .NET
`Scenes/Frontend/Tests/LoadingSceneChecks.tscn -- --skipfmv` checks the live host;
`--loading-render-dir=/absolute/owned/local-data/path` enables rendered comparisons
only when the caller provides an isolated display. The historical baseline used
`--loading-measure-existing-composition` before integration; that mode requires
the old production `DrawLoading` implementation. No test chooses the physical display.

Run `res://Scenes/Shared/retail_float32_checks.gd` with the standard engine's
`--headless --script` options for the focused binary32 store check. The .NET
`Scenes/World/HeightFieldSceneChecks.tscn` exports an object-free fixture and JSON
report to two distinct fresh absolute paths under this worktree's `local-data/`,
passed after `--`. The standard `height_field_checks.gd` consumes that fixture and
a fresh report path. `WaterSceneChecks.tscn` and `water_scene_checks.gd` use the
same explicit fixture/report convention. These checks never choose a display.
Debriefing's standard `Scenes/Frontend/Tests/debriefing_scene_checks.gd` also runs
under `--editor`. The .NET `DebriefingSceneChecks.tscn -- --skipfmv` checks the
actual frontend boundary; rendered comparisons require a caller-owned isolated
display and `--debriefing-render-dir=/absolute/owned/local-data/path`.

Run `res://Scenes/Frontend/Tests/OptionsBridgeChecks.tscn` and
`res://Scenes/World/EntityBridgeChecks.tscn` using the same supported headless
launch form as the world check above. Standard Godot accepts
`--script res://Scenes/Frontend/Tests/options_scene_checks.gd` and
`--script res://Scenes/World/entity_scene_checks.gd`, with `--editor` for their
frozen editor checks. Sun's headless .NET `SunSceneChecks.tscn` requires two fresh
absolute owned output paths after `--` (reference Variant and report JSON);
the standard `sun_scene_checks.gd` accepts that reference and a new owned report
path. These entry points reuse production scenes and existing comparison owners.

The scheduler group additionally passed **454 checks** derived from the committed
September 19 queue/precision contracts described in [PARITY.md](rebuild/PARITY.md),
alongside its existing differential transcripts. The HUD model comparison also
passed after adopting native default constants. Both reports are in
`local-data/test-runs/gdscript-native-front-camera-5clstjzh/`. The scheduler checks
cover delivery only, not the native component flag write, monitored allocation,
or a measured live precision mode.

The headless and isolated 640×480 software-rendered Godot smokes completed
startup/menu/gameplay/retry/return and passed the existing full
`Test-FirstFlightSmokeEvidence` validator. Their 2,148-step state
matches the current Client oracle, which also passed separately. The validator's
old `bc5d99c7…` pin predated already-committed simulation/definition changes. It now
uses the existing `53c1cc64…` oracle in
`InteractiveSessionTests.FirstFlightSmokeScenario_ReachesFiringRangeAndCompletesWaypoint`.
That test retains gameplay assertions, compares definition-format 7 every tick
after an identity-only substitution and recovers both format-6 and format-7
fingerprints. The earlier causal receipt below remains the explanation of those
changes; the scene migration introduces no new simulation hash. No assertion or
driver constant was relaxed. The smoke ends with mission **Running**, not Won.
The rendered host recorded its actual 2,148-step command tape; two Headless
replays verified both embedded live trace and final-state hashes with no
divergence (`rendered-smoke-tape.json`, `rendered-smoke-replay.log` under the
check directory). The isolated X server reported unavailable input-method and
V-Sync support; no Godot runtime error was reported. An earlier 1280×720 software
attempt hit its 180-second bound and was cleaned up; reducing capture resolution
changed no driver inputs or simulation budget.
Full startup-to-combat-completion and Windows execution remain unresolved.

September 19 main integration independently rebuilt the combined companion and
rebuild changes with zero warnings/errors. Launcher checks passed 12 shared-host
and 20 rebuild cases; canonical asset reuse/routing passed 17 cases. The routing fixtures
initially failed two expected-message assertions because their supposedly external
scratch paths were inside the checkout; all 17 passed with private `/var/tmp`
scratch, without changing the routing implementation or assertions.
Headless production checks passed for world (23,877 assertions, including 13 new
import ownership checks), HUD (44), pause (70), frontend and startup. The combined
native companion gate also passed its scene/domain workflow, 17 file-bridge
protocol cases and 12 launcher cases. The affected Client selection passed 24
HUD-layout, pause and existing First Flight fingerprint tests. Documentation and
public-payload checks passed with the pinned reference submodules present.
These are execution checks on the merged sources, not a new retail or
human-interaction acceptance claim.

The merge review found and corrected a scene-import preservation defect: a valid
older receipt did not prevent newly generated names from overwriting unlisted
private files. The importer now plans and checks all destinations before saving
and repeats ownership/hash checks at each save. Actual stale-receipt runs rejected
both a late numbered-resource collision and an Aquila component-scene collision,
leaving all 320 existing files byte-identical in each case. A successful
regeneration preserved an unrelated noncolliding file. Commands, logs, before/after
hashes and the bounded reproducer are retained under
`.worktrees/main-integration-20260919/local-data/merge-checks/rebuild-11whx7zg/`;
the reusable ownership checks live in `WorldSceneChecks.cs`. This protects the
observed collisions; it is not a claim of an atomic multi-file import transaction.

The retained Windows `test:winui` builds one WinUI solution, then runs selected
AppCore contracts, UI tests excluding `WinUIRuntime`/`LegacyWpf`, and CLI tests.
It is not the Linux default or a replacement for native acceptance.

September 6 Linux phase results are in
`local-data/test-runs/linux-route-20260906-af1sa_l9/`: the default gate passed
**24/24** Save Lab/composition tests and **14/14** fake-tool launcher tests;
startup cache/audio tests passed **16/16**. Focused recorder/headless tests passed
**59/59**, and client launch/career tests **12/12**. The native First Flight smoke
completed, and the separately recorded **9,367-tick** session replayed twice with
both live expected hashes verified. That session was mostly idle and did not
complete the tutorial. The companion's native shell/file dialog opened, but its
UI write/reopen flow remains pending. Startup logo/montage audio decoded with
format/length readback; native playback of those new tracks remains pending.
These are bounded results, not a new broad Core, Windows or full parity receipt.

September 7 first-training corrections passed **43/43** Client tests selected by
`RetailFrontendSessionTests|RetailCareerLoadFlowTests`, then **68/68** focused
weapon Core tests and **5/5** Client input/smoke tests. The latter include held
Twin Vulcan input, Pulse hold/release/tap, release latching, destruction-event
aggregation and `FirstFlightSmokeScenario_ReachesFiringRangeAndCompletesWaypoint`.
The Jet check composes actual Client button samples with the existing isolated
flight fixture; it is not a complete flight playthrough. Two materialized smoke
input runs reproduced the new weapon-state hash before its focused and retained
Windows-launcher pins changed. Test output is retained in this task's transcript,
not a newly claimed log file. Native Godot built without warnings/errors; no
visible launch or Windows execution followed these changes. The shared Ghidra
cohort framework passed **88** focused tests; its actual isolated rehearsal,
stale-comment refusal, live apply, separate readback and PRE/POST restore probes
are recorded by the [Ghidra owner](reverse-engineering/ghidra/README.md).

September 8 focused checks passed **46/46 Core and 8/8 Client** for the shared
retail clock, reset/pause behavior, readiness boundaries and canonical state;
**73/73 materializer and 22/22 contact tests** for raw serialized geometry; and
**38/38 Core and 4/4 Client** for Large Pulse launch/contact and affected weapons.
These selections overlap and are not a new total-suite census. The existing
forty-step and FirstFlight fingerprints held without repinning. Logs share the
Linux run directory above: `retail-clock-{core,client}-20260908.log`,
`contact-float-geometry-materializer.log`, and `large-pulse-{core,client}-20260908.log`.
That contact change introduced schema v5; conditional canonical schema 45 retains an event frame
count when pause makes it differ from the already-hashed mission tick. The
checks do not establish a complete spatial blast, exact motion/expiry, event
dispatch ordering or a live playthrough.

The charged Pulse zero-spread correction first failed its direction regression
with 2,124 microradians of unwanted yaw, then passed **8/8 Core and 1/1 Client**
checks. Both scatter random draws remain, and no fingerprint changed. The
`large-pulse-zero-scatter-{red,green,client}-20260908.log` files retain the runs.

Contact schema v6 additionally preserves all 362 original part records,
including hierarchy inputs, opaque words and absent CPOS/CORI caches. Stripping
only those additions and restoring the old schema reproduces the exact v5
payload hash. The full materializer suite passed **74/74** and contact tests
**23/23**; the former log is `contact-v6-materializer-full-20260908.log` in the
Linux run directory above. Runtime sweeps remain unchanged. These inputs do
not establish the selected collision pose or runtime explosion report.
The subsequent mesh-pose arithmetic passed **7/7** focused tests, covering raw
Warehouse hierarchy inputs, signed zero and distinct matrix/store ordering.
Those results were captured in the task transcript. They do not establish
runtime cache/controller execution or the live FPU state.

The subsequent passive-bounds and geometry precision correction passed **43/43**
focused contact/pose tests. Eight new expectations first failed under the old
53-bit model. The corrected model rounds each operation to 24 significand bits,
retains intermediate exponent range and preserves the shipped three-axis bounds
quirk. A separate native x87 PC24/RN probe passed **9/9** synthetic arithmetic
checks, including a tangency decision and cancellation outside float32's
exponent range; it restored its process control word and did not run the game.
Logs are `geometry-pc24-{red,green}-20260908.log` and
`geometry-pc24-x87-probe.log` in the Linux run directory above. These establish
the bounded arithmetic model, not live gameplay precision or an integrated
spatial explosion scan. The preceding 33-test bounds run used the now-superseded
53-bit assumption and is retained as a dated result only.

Warehouse report construction and local sphere conversion then passed **49/49**
focused contact/pose tests; the materializer passed **74/74**. Tests exercise
the cached transpose, Z/Y/X accumulation, stored centre subtraction, signed zero,
reference geometry with a separate pose/identity, and the first-six cap before
a closer seventh contact. Initial test assumptions about root preview eligibility
and empty BBOX padding were corrected from the actual retained words.
Contact schema v7 adds only original `NumNmic/IsNmic` words; removing those fields
and restoring the schema reproduces the complete v6 payload exactly. Logs are
`warehouse-bounds-report-final-20260908.log` and
`contact-v7-materializer-20260908.log` in the same directory. Caller-supplied
poses/eligibility remain explicit; this does not validate the segment lifecycle
or connect the report to Simulation's explosion path.

The Warehouse immediate core2 cascade passed **40/40** contact tests and
**4/4** cold-start/pointer-route checks. Four causal expectations first failed
against the old single-part break. The correction preserves reverse child-list
order, leaves queued chimney parts unchanged, rejects a short event buffer before
mutation, and preserves component health/eligibility through snapshots and hashes.
Logs are `warehouse-cascade-red-behavior-20260908.log`,
`warehouse-cascade-final-20260908.log` and `warehouse-cascade-routes-20260908.log`
in the Linux run directory above. The snapshot test uses a component serialization
envelope, not a complete matching-registry runtime restore. Queued lifecycle,
debris rendering and native controller notification order remain open.

The subsequent subtree-sum and threshold correction passed **55/55** focused
contact/pose tests and **5/5** cold-start/pointer/handoff checks. Both new behavioral discriminators first failed: an actual
part-data leaf sequence emitted the wrong sum word, and a synthetic equality
state terminated early. A native x87 PC24/RN probe separately passed **2/2**
coefficient checks without executing game code. Logs are
`warehouse-sums-{red,green,routes}-20260908.log` and `warehouse-threshold-x87-probe.log`
in the same Linux directory. The leaf calls use supplied lethal amounts; the
boundary state is artificial. Neither is native player acceptance.

The Tank/Truck shutdown correction passed **123/123** focused Core checks:
contact/lifetime, Thing/Actor state, existing event scheduler, actor scripts,
tutorial progression and the established loss/pause-clock scenario. Four
behavioral expectations first failed against immediate removal/terminal damage
discard. Tests cover the frame-13 due-word discriminator (delivery at frame 23
even though the clock is below due), ring wrap, repeat damage without renewed
death/timer, immediate script teardown/objective clearing, pending restore/hash,
equal-time insertion order and visible zero-health target projection. The pause
timer test directly repeats BeginTick without advancing the manager; the loss
scenario separately exercises Simulation's paused clock. The input-only static
target run now measures four impacts **at death**, separately from accepted
post-death impacts, and stops after its three target objectives instead of
continuing through unrelated exercises. No driving commands were retuned.
Logs are `ground-shutdown-{red,green-initial,green,integration,final}-20260908.log`
in the same Linux directory. The subsequent cold-start/pointer/handoff selection
passed **5/5** (`ground-shutdown-routes-20260908.log`), with the same input drivers
and full-client/direct-control equality requirements. The Client first-flight
smoke passed **1/1** (`ground-shutdown-client-20260908.log`). The intermediate failures preserve obsolete
immediate-removal expectations and their corrections. These are deterministic
tests and static-byte contracts, not a native retail/Godot death playthrough.

Pending ground movement passed **83/83** focused mechanics, base-state,
contact and tutorial-progression tests (`ground-dying-motion-final-20260908.log`
in the same directory). All four cadence positions first failed against the
immediate-stop implementation (`ground-dying-motion-red-behavior-20260908.log`).
The final selection covers retained lite velocity, full-update stop, distinct
old position/orientation, mid-phase restore, deactivated pending actors and
Tank/Truck terrain clamping without a velocity rewrite. The earlier `red` log
records a corrected test literal compilation error, not a behavioral result.
Native float motion, initial cadence alignment and full surface behavior remain
open. The subsequent cold-start/pointer/handoff selection passed **5/5**
(`ground-dying-motion-routes-20260908.log`) without driver or fingerprint changes.
These results do not establish live play parity.

The retail-to-Core basis correction passed **112/112** focused Core checks
(Thing/Actor projection, mechanics, contacts, registry and existing World 110
construction) and **76/76** materializer checks. Both exact quarter-turn offset
cases and signed-zero preservation first failed against the old unsigned
permutation. The Core cases also check the resulting rendered point without
launching Godot. Real materialization reproduced **389 exact files**. The two
changed manifests contain only projected-basis signed-zero changes: 237 words
across Level 100's 44 actors/10 spawns, and 189 across World 110's 43 actors.
Raw retail words, positions and non-pose fields are unchanged. Logs are
`actor-basis-{core,python}-red-20260908.log`,
`actor-basis-{core,python}-final-20260908.log` and
`actor-basis-materialize-20260908.log` in the same Linux directory.
The materialized Client selection passed **7/7** after updating the manifest
identity and reproducing the new first-flight fingerprint twice; the earlier
`client-initial` and `client-pin` logs preserve the stale-pin failures.
The five existing cold-start/handoff tests also pass (`actor-basis-routes-20260908.log`),
but use reduced hand-built definitions and do not validate the new manifest.
The coupled waypoint/flyby checks passed **10/10** after preserving the four
negative-zero words in their authored Trainer basis; the prior mismatch and
the correction are retained in `actor-basis-waypoints-20260908.log` and
`actor-basis-waypoints-final-20260908.log`.

The subsequent cold-start harness correction passed **4/4**
(`cold-shipping-definitions-initial-20260908.log` in the same directory).
Both client and direct pointer control now use the production manifest decoder
and assert its definition identity and 44 authored actors. The unchanged driver
clears 22 targets, keeps abort false, completes primary objective 4 and reaches
Won; complete state and pose-trace equality remain required. Spawned Tank 1 is
selected by target group/ordinal and verified definition/script/owner, replacing
the reduced fixture's allocation-dependent name. The separate returning and
negative controls remain synthetic. This is a deterministic regression, not
player-observable live acceptance.

The Air Trainer initial-life correction passed **22/22** focused Core checks,
**6/6** materialized Client checks and **76/76** materializer checks. Both
authored and spawned creation first failed with zero life, then supplied the
physics profile's 3000 milli-life and retained it through snapshot restoration.
The ambient Trainer remains outside mission targets despite its positive life.
Materialization reproduced **389 exact files**; exactly two manifest leaves
change, both `initialHealth`. Logs are `trainer-life-red-20260908.log`,
`trainer-life-{core,client-final,python,materialize}-20260908.log` in the same
directory. Initial health does not close aircraft damage or death behavior.
The shipping-data cold-start selection then passed **4/4**
(`trainer-life-cold-start-20260908.log`). Both input adapters still reach Won
at tick 9191 with hull 8545 and identical full state/pose traces; their new state
hash is `7ddb32258aff65782bd232ba49c9d33a0b3c6c806f766c81f4271e48311c1ea8`.
No driver changes or live player acceptance are involved.

The finite Unit Euler update passed **19/19** native-output cases, then
**32/32** with adjacent PC24 mesh-pose arithmetic checks
(`unit-euler-core-final-20260908.log` in the same directory). Expected words
come from isolated execution of the unchanged retail routine under controlled
PC24; its PC53 comparison is also retained in `unit-euler-native-final-20260908.log`.
Coverage includes strict angle boundaries, pitch without wrapping, one-pass
normalization, multiplier four, signed zero, the float coefficient and a
subnormal step retained until the final store. Review replaced one initial
coefficient example that did not distinguish multiplication from division.
The subsequent matrix implementation passed **50/50** focused Core cases:
nineteen angle updates and thirty-one matrix outputs
(`unit-euler-live-matrix-20260908.log`). Twelve additional inputs came from
actual Plane calls in the private copied-game WineD3D run; the unchanged native
oracle also matched eleven consecutive live Euler/basis transitions. Its
constructor/cache/Euler samples all read PC24/RN. The exact private route and
receipts are in the [Unit evidence](reverse-engineering/binary-analysis/functions/CComplexThing.cpp.md).
Managed trig remains provisional outside those finite cases. The subsequent
`observe-plane-motion-a` run supplied 32 complete Move transactions (128 boundary
samples); `managed-plane-comparison.log` records 352 matching grouped compiled-Core
comparisons. The live mover now uses the ordered raw free-flight transaction.
Guide/controller observations supplied to that comparison do not validate the
whole production event, avoidance, contact or effect graph.

The living-Plane turn-rate correction passed **34/34** mechanics/Euler checks
and **1/1** repeated Client FirstFlight check. Both aircraft first failed at
14,544 rather than 43,633 microradians. Logs are
`living-plane-turn-{red,final-core,client-final}-20260908.log` in the same
Linux directory. The Godot build also passed with zero warnings/errors.
The native Godot smoke then completed at 2,148 ticks with the same fingerprint
on a private authenticated Xvfb display, at both 60 and 20 recording frames/s.
Only 20 frames/s matches this synthetic runner's one 20 Hz tick per frame.
The two `first-flight-smoke.json` reports are under `movie/` and
`movie-realtime/` in `local-data/first-flight/progress-video-20260908-a/`.
They establish the smoke route, including retry/return, without desktop access;
they do not establish live player acceptance. The recording's four ObjectDB leaks
were subsequently reproduced and corrected as described below.

The audio shutdown correction passed **174/174** focused Client audio, music,
startup, frontend and pause checks (`audio-retirement-client-20260908.log` in
the same Linux test directory), and the Godot build passed with zero warnings/errors.
Under the same private display/Dummy-audio route, `lifecycle-smoke-red-command.log`
reported four leaked objects. Stream-identity instrumentation in
`lifecycle-stream-identity-command.log` mapped eight leaked objects to the final
frontend and just-retired tutorial Ogg playback graphs. The instrumentation was
removed. `lifecycle-retirement-green-b-command.log` then completed the full smoke
without leaked objects or shutdown timeout. Its report retains tick 2,148, the
same state hash, fresh retry session and released world on return. Wall-clock
voice progress differs between runs and is not a deterministic/audio-parity claim.
The window-close check (`lifecycle-window-close-d-command.log`) and main-menu
capture (`lifecycle-capture-close-command.log`, 161/161 saved, screen-matched
frames) also exited cleanly. All five logs and the reports are under
`local-data/first-flight/progress-video-20260908-a/`. Earlier close-test attempts
failed in the private display setup; the accepted run pre-created the close
protocol atom that Godot expects a window manager to provide. No host desktop
input was used. The private driver's V-Sync warning remains; Windows and audible
output were not tested by these runs.

The shutdown mechanism follows the pinned engine's deferred playback deletion
in [AudioServer](https://github.com/godotengine/godot/blob/ed1daf0bf/servers/audio/audio_server.cpp).
The adapter polls native weak references through disposed Variants, avoiding a
new managed reference while waiting for retirement. It reports a failed drain
and nonzero exit after five seconds instead of treating a fixed delay as success.

The broader cold/returning selection passed **6/9**
(`living-plane-turn-routes-20260908.log`). Two failures remain real full-combat
gaps: the unchanged cold driver aborts with one final-wave kill, and the
returning driver aborts with five. Both cold input adapters still match exactly
at Won/tick 7260/hull 2750, hash
`72defa3e803b75a263687945a34f30c1b64afaa6c432fba7a4752b64a32c3d4f`.
Their full-combat assertions remain intact; the earlier successful routes below
predate this corrected flight behavior.

The third failure was an unsupported statistical hit-rate requirement. A
focused old-cap control passed its former limits, showing route sensitivity;
the source was restored to the measured full cap afterward. The test now checks
causal hit/miss receipts, unique round identities, damage and disappearance,
without treating an earlier sortie's percentages as a retail invariant.
That check passed separately: each control's 67 damage events matched 67 named
round hits (`living-plane-turn-{old-cap-control,causal-receipts}-20260908.log`).
Existing finite-cylinder contact tests and both full-combat requirements remain.

The test pilot's reticle-origin correction then passed **2/2** focused cases
that had both failed with its fictitious muzzle-height offset
(`reticle-fire-gate-{red,focused}-20260908.log`). The affected route selection
passed **6/8** (`reticle-fire-gate-routes-20260908.log`): returning combat still
aborts after five final-wave kills; cold combat now aborts with none. Both cold
adapters match at Won/tick 7194/hull 7050, hash
`53a682fd6693ccee442655189df25c7ff524cb646e1fe88d2e2be0b60b146b76`.
This fixes the driver's stated geometry, not the unfinished combat route.
Simulation code, steering gains and full-combat assertions were unchanged.

The direct-controller phase correction passed **23/23** focused Core checks,
then **1/1** Client FirstFlight smoke and **5/5** final cold/returning-route
tests. Causal regressions first reproduced firing on the unlock update, losing
a shot before the disable callback and using the moved emitter. The corrected
cold pointer route clears all targets without abort and exactly matches its
same-input direct-Core control's state hash and pose trace. The former
unquantized cold fixture issued different commands and lost to water; it was
retired as an invalid adapter-comparison requirement. The separate returning,
naive and trigger-disabled controls remain.

After the living-Plane rate correction, the repeated FirstFlight
fingerprint is `bc5d99c7f1fbd5e2bf86363e5309e5aa77f0ad132241ef08a9e61b15d75b3dfd`
(`living-plane-turn-client-final-20260908.log`). Its retained Windows-launcher
expectation was updated for the same tape, without Windows execution. The
earlier controller-phase logs are `controller-phase-final-focused-20260908.log`,
`controller-phase-final-smoke-20260908.log` and
`controller-phase-final-consolidated-routes-20260908.log` in the Linux directory
above. These are in-process regression results, not desktop tutorial acceptance
or a new broad-suite/ferry sweep. Full axis and event-priority parity remain open.

The World 110 integration review exposed a setter/restore mismatch: script
assignment still used the World 100 list. The new focused regression failed
before repair, then **24/24** affected construction/registry tests passed.
The existing Level 100 fingerprint passed separately without repinning.
Both Godot projects then built through the shared Linux launcher with zero
warnings/errors. This remains partial construction, not second-world runtime.

September 7 targeted RE reproduced a Core scheduler overflow-count mismatch:
the new callback regression failed before the fix, then the complete affected
`RetailEventSchedulerTests` fixture passed **32/32, zero skipped**. The
[event-system owner](reverse-engineering/source-code/io/event-system.md) records
the pristine instruction sites, body hashes and test's artificial callback
boundary. Its `scheduler-overflow-{red,green}.log` files share the Linux run
directory above. Actor/base and Unit initialization extensions are static
evidence, independently checked against selected complete pristine bodies;
no new runtime, full-campaign or broad Core result is claimed.

The subsequent World110 attachment change passed **20/20 Core facts, zero
skipped**: attachment arithmetic, real initial construction, detached player
construction and the existing World100 forty-step fingerprint. The unchanged
fingerprint was not repinned. The materializer's affected fixtures passed
**12/12**; the existing synthetic mesh parser/re-emitter fixtures plus new
emitter framing cases passed **65/65**, without running a corpus census.
The two real factory meshes produced the same four spawner transforms before
and after the parser change. The existing materializer published only the
changed 38,751-byte World110 actor/input asset.

An original native x87 probe under explicit `0x027f` checked all four attachment
positions, nine-component bases and child Euler outputs; it executed no retail
code. Exact source/log hashes and static body evidence are in the
[Unit transform owner](reverse-engineering/binary-analysis/functions/Unit.cpp/CUnit__UpdateTransform.md).
The `world110-attachment-{core,materializer,docs,safety}.log` and
`mesh-emitter-tests.log` files use the existing Linux run directory above.
Read-only reviews found no remaining parser or arithmetic defects after the
misplaced test assertions were corrected. These results do not establish
complete child initialization, second-world play or general animated/x87 parity.

The World110 tree-input and Simulation-boundary change passed **71/71 Core
facts, zero skipped**, plus **14/14 focused materializer checks**. The initial
adjacent hash check exposed the old test-only World110 Simulation running
Level100 Setup; that unsupported route now fails before initialization. Direct
native-88/native-84 mission coverage, definition/world mismatch checks, actual
construction/player tests and the unchanged World100 forty-step hash passed.
Logs are `world110-trees-core.log` (initial failure),
`world110-trees-core-fixed.log` and `world110-trees-materializer.log` in the
existing Linux run directory.

An in-memory counterexample at Level100 RLWD offset 52,498 changed a variant
to 4: the previous committed parser accepted it; the shared reader rejected it.
The exact archive pin already protected ordinary source selection. Independent
old/new parser comparison preserved the complete actual100/110 base actor/pine
outputs in both name modes and all actual100 level actors/waypoint paths.
Only the new 155,972-byte World110 input asset was published locally. Both tree
tables' raw record digests also reproduced after Core decoding. That step did
not initialize trees or integrate live listeners; the following step extends it.

The connected base-tree prefix passed **69/69 Core facts, zero skipped**, and
**10/10 World110 materializer checks**. The Core selection covers actual pine
construction, float terrain/mesh fields, one shared draw per tree, 1,481 real
readiness callbacks, world/player/reader identity separation, live sector-list
ordering and mutation, shared Actor state, existing scheduler laws and the
unchanged World100 forty-step hash. An initial radius-boundary test expected
the next float to cross a layer; direct arithmetic showed its product still
stores as 8.0f. The corrected test preserves that additional equality case and
checks the following float crosses. Logs are `tree-prefix-core.log`,
`tree-prefix-core-fixed.log` and `tree-prefix-materializer.log` in the same
existing Linux run directory. The ignored World110 asset is now 157,121 bytes;
only that derived input was regenerated. Read-only review also exposed and
closed mutable collection/index escape routes from the world owner.

These checks execute the reconstruction under explicit nearest/53-bit numerical
assumptions and a supplied incoming seed. They do not measure the retail load's
control word/seed, final tree orientation, full collision responses, transition
reset or World110 play. No desktop, Ghidra or broad runtime campaign was used.

The subsequent PostLoad sort change passed **73/73 selected Core facts, zero
skipped**, including the unchanged World100 forty-step hash. Four additional
MapWho facts cover original-tail rotation, mixed entries and repaired links,
the four finer layers, the preserved shared cursor and unchanged empty/single/
ordinary sectors. Intentionally including layer 0 failed its exact order check
(expected `[2,1]`, actual `[1,2]`); source restoration returned that fact to green.
Logs are `mapwho-postload-core.log`, `mapwho-postload-mutation.log` and
`mapwho-postload-restored.log` in the same existing Linux run directory.
Sort remains separate from the incomplete world-load sequence. Building,
Feature and startup findings in this pass are static evidence, not live checks.

The first Control Tower Core construction passed **96/96 focused Core facts**
and **11/11 World110 materializer checks**, zero skipped. Checks cover the
existing Actor/raw-pose owner, real 15-pine collision rejection, 29 segment
allocations/eight cores, exact graph/scale words, five undelivered shared events,
AI reader cells, world memberships and rejection of unsupported lifecycle,
restore and hashing. The existing World100 forty-step hash remains unchanged.
A deliberate child-tail mutation failed the independent sibling-order oracle
(expected `[33,32,31,30,2]`, actual `[2,30,31,32,33]`); original bytes were restored
and the expanded 96-fact selection passed,
including the existing World100 registry suite.
Logs are `control-tower-core.log`, `control-tower-materializer.log` and
`control-tower-mutation.log` in the same Linux run directory. Only the ignored
164,510-byte v5 World110 actor input was regenerated. These are headless
reconstruction checks under explicit fresh resource-route and numerical
assumptions. No renderer-cache, frame-delivery, damage, reset, retail runtime
or full parity acceptance is claimed.

The extension through the factory and repair pad passed **174/174 focused Core
facts** and **13/13 World110 materializer checks**, zero skipped. The selection
includes existing charge/selection laws and the World100 forty-step hash check.
It checks 64 segment owners, repair aliases and exact health words, factory
big-list/active-state behavior, copied spawner inputs, repair mode/charge state,
the shared effect chain, and 15 events with three Actor draws. Reversing the
weapon's two effect-node constructors deliberately failed its instance/order
assertion (expected weapon `+0x1c`, actual `+0x14`); source was restored byte for
byte before rerunning the selection. Logs are `initial-buildings-core.log`,
`initial-buildings-materializer.log` and `initial-buildings-mutation.log` in the
same Linux run directory. Only the ignored 175,671-byte v6 actor input was
regenerated. These are construction checks; they establish neither tank
spawning, repair firing, rendered World110 nor runtime parity.

The extension through SAT and all six icebergs passed **183/183 focused Core
facts** and **14/14 World110 materializer checks**, zero skipped. This adds six
connected-construction facts and the three existing attachment-pose checks to
the prior selection. It covers authored order, mixed world memberships, SAT's
mode-ID/index distinction and shared weapon state, Feature current/old poses,
collision spheres and distinct rounding stores, 1,513 pending events and the
1,491-draw stream. The World100 forty-step hash remains unchanged.
Two controlled mutations failed their exact facts: water Teleport overwrote
authored old Z; an inverted centre branch lost Building BBOX transformations.
Source was restored byte-for-byte before the full focused selection passed again.
Logs are `initial-icebergs-core.log`, `initial-icebergs-restored.log`,
`initial-icebergs-materializer.log`, `initial-icebergs-water-mutation.log` and
`initial-icebergs-centre-mutation.log` in the same Linux run directory.
Only the ignored 234,999-byte v7 actor input was published. This remains
headless construction evidence under explicit numerical/resource assumptions;
no retail/Godot runtime, Ghidra database or desktop was opened.

### Aircraft integration follow-up — September 12

`npm run test:rebuild-core` built successfully and finished with **1,354 passed,
8 failed, zero skipped**. Six failures exposed outdated component fixtures or
fingerprints after raw aircraft construction; the other two are the still-failing
cold and returning full-combat routes. This is not a passing broad-suite receipt.
The follow-up filter covering `Level100DestructionContactTests`, the weapon-state
hash variants, both direct-spawn drone cases, `HeadlessApplicationTests`, the
Hangar restore regression and the forty-step hash passed **78/78**. Logs are
`plane-integration-core-20260912.log` and
`plane-integration-focused-20260912.log` under
`local-data/test-runs/linux-route-20260906-af1sa_l9/`.

Actor-script restore now retains spawn admission and event-clock callbacks;
`RestoreDuringHangarPausePreservesNativeSpawnAdmissionAndCurrentClock` passed
through the native Hangar Pause/SpawnThing continuation. Standalone spawn
fixtures now invoke the same creation owner as production. Component-only
ground-death snapshots use the existing legacy hash envelope instead of claiming
an aircraft event clock they never advanced. Their lifetime, ordering and restore
assertions remain; full raw-aircraft restore has its own tests.

The forty-step golden-hash diagnosis is byte-exact, not a repeatability inference.
The current 41,057-byte canonical state hashes to `f121a469…f55b8`.
Flipping only `PlaneEvents.Float24Arithmetic` changes byte 40,798; removing that
one mode byte exactly reproduces the former `5e642166…caa54` fingerprint.
The ignored `hash-cause-20260912/` probe and `hash-cause-20260912.log` preserve
the command source and both full hashes. The mode is future-affecting state:
aircraft now use measured PC24 scheduling, while legacy scheduler callers retain
their default arithmetic. This diagnoses the missed pin update in the raw-plane
commit without treating the former state as a restorable current snapshot.

The compiled Headless first-flight tape replayed twice for 838 ticks with no
divergence: trace `0d835c29…591518`, final state `5edc8900…c9239`.
This is a revision fingerprint after accumulated changes since schema 42,
including raw aircraft motion and scheduler state. The test checks the bounded
startup state: the player has activated and moved in Walker mode, has no flight
permission, projectiles or kills, and the running mission retains raw Trainer
state and its PC24 scheduler. Direct replay measured activation at tick 665;
an older test comment's 996-tick value was not current. Despite its historical
name this tape does not exercise player flight. The forty-step byte-isolation proof above does
not explain every intervening change to this separate tape. The JSON and stderr log are
`plane-first-flight-replay-20260912.*` in the same directory. No assertion on
combat completion, native input, audio or rendering is weakened by these updates.
The cold and returning full-combat runs still reach Won through the low-health
abort, with objective 4 failed and no final-wave kills; they remain failures.

New general check output belongs under ignored `local-data/test-runs/` or a
descriptive child of `local-data/`. Preserve existing coupled `.artifacts/` and
specimen-bound `local-lab/` evidence paths. Validation output is not release content
or proof of unrelated runtime behavior.

The dated live-window attempt produced blank captures and established neither
input delivery nor a walkthrough; PrintWindow success alone is not pixel evidence.
Its historical correction is recoverable through `developer_state.json` → `_history`.

September 6 repository preparation used the existing focused checks: packet exporter
**21/21**, probe refuter **46/46**, probe author **43 checks with 17 falsifiable guards**,
and host-attestor unit tests **13/13**. The exporter tests use fake headless launchers;
no Ghidra project was opened. The probe author retained the three protected input hashes.
The attestor's help/diagnostic correction did not rerun full campaign verification.
Documentation and public-payload gates passed.

The independent follow-up reproduced two unsafe unregistered-packet cases and the
bind-alias output-admission defect before repair. The completed exporter suite passed
**24/24** with fake headless launchers. The tool runner passed **4/4** self-tests,
including Linux skip accounting and simulated Windows dispatch for the four identified
Windows suites; the full tools aggregate was not rerun. Evidence-register unit tests
passed **6/6**, the installed-write claim guard passed **14/14** classifier cases and
its tracked scan, and the docs/public-payload gates passed. State reduction compared
all protected values with the exact pre-cleanup Git blob; this is not full campaign
replay or native runtime evidence. The only Core source edit in this follow-up corrects
a historical replay comment; it changes no executable behavior.

The three Linux namespace-message failures in the August 31 Core receipt were
reproduced on September 6. The tests now expect Linux's earlier absolute-path refusal
and retain their Windows-specific assertions; production `TapeFile` behavior is unchanged.
The complete affected class passed **22/22, zero skipped** using
`dotnet test rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj --no-restore --nologo --filter FullyQualifiedName~HeadlessApplicationTests`.
Before/after TRX files are in `local-data/test-runs/preparation-20260906/`.
This focused result closes those three failures; it does not replace the dated broad
receipt or establish Windows/Godot runtime acceptance.

Do not add a new test during cleanup unless implementation behavior changed,
the regression is consequential, and no focused existing check covers it. Do
not fix unrelated failures discovered outside the changed contract.

## Remote source review — 2026-09-09 (execution pending)

The following is the September 9 remote handoff record; its host execution is
recorded below. At remote closeout it was pending verification. Source changes
are on `codex/onslaught-remote-integration-20260908`, following `82af1a41`.
Native-command and Python probes returned `TransportTimeoutError` without program
output; no compiler, test suite, Godot, Ghidra or retail program ran in this pass.
GitHub commit diffs were inspected and branch updates were read back separately.
Those checks establish source/publication state, not executable correctness.

| Source change | Added cases declared in source | Required verification |
| --- | ---: | --- |
| `f9d2e6dd`: FirstFlight launch admission | 14 | Existing `FirstFlightLaunchOptionsTests`, including legal repeated careers and capture with recording; reject smoke/capture conflicts and duplicate output arguments before file-opening adapters. |
| `752f913e`: command-tape JSON admission | 30 | `CommandTapeJsonAdmissionTests`, then existing replay/recorder/headless checks. Test duplicate decoded names, hidden schema/command/hash replacements, escaped keys, strict v4 migration, invalid roots and unchanged canonical identities for valid v4/v5 inputs. |
| `e8178614`: scheduler Update guard | 8 | `RetailEventSchedulerUpdateGuardTests` and existing `RetailEventSchedulerTests`. Test caught/uncaught nesting, interrupted retries, ring wrap, PC24/default arithmetic, retained rearm state, subsequent delivery/recycling and Init recovery. |

The 52 additional cases are an authored count, not runner discovery or passes.
Existing tests were retained. No tape schema, serializer output, scenario fixture,
golden fingerprint, normal scheduling arithmetic or gameplay constant was changed.
The scheduler guard is a reconstruction API correction; it adds no retail contract
grade or Ghidra correction. Microsoft's documented last-definition behavior for
[JsonElement.TryGetProperty](https://learn.microsoft.com/en-us/dotnet/api/system.text.json.jsonelement.trygetproperty?view=net-8.0)
supports the JSON ambiguity analysis; the fix uses .NET 8 enumeration APIs rather
than adding a newer-framework duplicate-property option.

On a functioning host, first prepare the existing admitted retail inputs and
perform the pinned project restore without changing locks, targets or engine.
The test projects reference Core's materialized resources even when an individual
fixture only checks parsing. With that setup already successful, run from the
repository root (these commands were NOT executed remotely):

```bash
dotnet test rebuild/OnslaughtRebuild.Client.Tests/OnslaughtRebuild.Client.Tests.csproj --no-restore --nologo --filter 'FullyQualifiedName~FirstFlightLaunchOptionsTests'
dotnet test rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj --no-restore --nologo --filter 'FullyQualifiedName~CommandTapeJsonAdmissionTests|FullyQualifiedName~RetailEventSchedulerUpdateGuardTests'
dotnet test rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj --no-restore --nologo --filter 'FullyQualifiedName~RetailEventSchedulerTests|FullyQualifiedName~ReplayTests|FullyQualifiedName~HeadlessApplicationTests'
npm run test:docs
npm run test:safety
```

Require nonempty runner discovery and preserve failures. Inspect the new negative
cases against the pre-fix implementations in an isolated review worktree when
establishing regression evidence; source reasoning alone is not a red/green run.
Broaden to affected Client/recording integration as results warrant. A native
Godot launch/capture check is still separate from argument-parser unit tests.

Review the full remote branch from the `13577577` feature baseline, not just these
three commits. Earlier `3654eb73` fixed actor-script restoration but still needs
`RestoreDuringHangarPausePreservesNativeSpawnAdmissionAndCurrentClock` executed.
`CanonicalHash_BindsRawPlaneStateAndWorld110SecondaryState` remains an unresolved
baseline diagnosis, not permission to replace its expected hash. Earlier remote
launcher/exporter commits contain dated test reports; this pass did not rerun them.
The proposed Python smoke report/log gate remains unpublished and unverified.
Record actual commands, outcomes and output locations here before integration;
do not transform these pending entries or historical receipts into claimed passes.

### Linux execution of the remote checkpoint — September 12

Reviewed the complete `13577577..f6ad243f` difference in
`.worktrees/remote-review-20260912`, preserving `031c975d` Windows retirement
and `31e9b437` local aircraft follow-up. Locked Core/Client restore succeeded
without target or dependency-lock changes. The integrated Core filter passed
**150/150**: new JSON/scheduler fixtures, existing scheduler/replay/recorder,
Headless, Hangar restore, forty-step canonical hash and raw Plane creation.
The new source's initial bounded Core selection passed **118/118**. The full
Client suite initially passed 905 with two failures and two existing skips;
after fixing the old spawn-pose expectation and the pre-raw-aircraft smoke
fingerprint, it passed **907, zero failed, two skipped**. Both failures preceded
the remote fixes. Emitter height remains above its seated Airfield; the
2,148-step smoke's gameplay assertions and independent input repeat still pass.
No flight/combat assertion or gameplay constant was relaxed.

All 52 new remote cases executed successfully. With the original four C#
implementations temporarily substituted in the isolated worktree, the selected
Core controls failed **29/39** and Client launch controls failed **13/23**.
Incoming source was restored byte-for-byte before the final passing runs.
Commands and results are in `remote-core-*.log` and `remote-client-*.log` under
`local-data/test-runs/linux-route-20260906-af1sa_l9/`. Core filters select
`CommandTapeJsonAdmissionTests`, `RetailEventSchedulerUpdateGuardTests`,
`RetailEventSchedulerTests`, `ReplayTests`, `CommandTapeRecorderTests`,
`HeadlessApplicationTests`, the named Hangar/canonical-hash regressions, and
`Level100RawPlaneCreationTests`; no empty selection is counted as a pass.

`python tools/godot_host_tests.py` passed **10/10**;
`python tools/export_packets_tests.py` passed **32/32**. First Flight initially
passed its 11 existing tests, but a new fake-engine control reproduced exit zero
with no report. `python rebuild/tools/first_flight_tests.py` now passes **14/14**,
including missing/malformed/incomplete completion reports, normal completion,
retained nonzero exit and captured timeout diagnostics. These are fake-tool
results. The new gate checks the completed smoke lifecycle; it does not port
or claim the entire retained Windows report/log validator. Logs are
`remote-godot-host-20260912.log`, `remote-export-packets-20260912.log`, and
`remote-smoke-completion-{red,green}-20260912.log` in the same owner.

Ghidra 12.1.3 compiled the changed packet exporter and exported 14 selected
functions from a verified read-only replica. The full 8,330-row function export
and program metrics matched the retained working POST exactly; the designated
working payload remained unchanged. Private outputs are in
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260912/`.
This verifies exporter execution and preserved structural state, not a complete
semantic audit, retail run, or native Godot acceptance.

### Plane-controller prototype and structural audit — September 12

The selected pristine executable was freshly hashed to the identity in the
[Ghidra owner](reverse-engineering/ghidra/README.md#plane-controller-event-argument-2026-09-12).
The reviewed checkpoint was inspected by file hashes only. The existing
Archive A working PRE was freshly copied, compared and reopened read-only.
The one-function manifest then passed isolated census/dry/apply and a separate
readback, independent raw-byte review, a sealed dry/apply/readback, and the
same live dry/apply/separate-readback sequence. Every headless invocation used
`-process BEA.exe -noanalysis`; only the declared isolated/live apply steps
omitted `-readOnly`. Exact live command arrays and receipts are retained in
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260912/plane-event-argument/`.

Full live function/program/variable/type/bookmark exports equal the sealed
rehearsal. Exactly one of 8,330 function rows changed. All other function and
variable rows, all program metrics and the complete saved stack-purge export
stayed identical. The POST recovery copy on Archive A passed a separate
restore/reopen with no missing, extra, size-different or hash-different file.
The function/variable exports cover internal functions; external/import
semantics are not certified by these comparisons. This does not certify every
decompiled expression: the spurious return-address
and vector-local artifacts persist and are documented in the controller owner.

`python -m unittest tools.ghidra_cohort_framework_tests` discovered **91 tests:
85 passed, six existing skips**. The new test executes the production Java
column-policy method. Five actual Ghidra refusal cases exercise stale, empty
and absent current-convention bindings, an undeclared prototype verb and
readback against PRE; a sixth runs the stale binding in actual apply mode.
All refuse without writes. Logs are `plane-argument-framework-*-20260912.log`
under `local-data/test-runs/linux-route-20260906-af1sa_l9/` and
`negative-controls/*.json` under the cohort owner. Initial incomplete census
bindings and a missing packet output directory were refused; corrected
invocations and their outputs are retained separately. No failed invocation
is counted as a successful export or mutation.

### Two native script callback signatures — September 12

`SetSpawnScript` and `IScript__SetAIState` passed exact raw dispatcher/body
review, isolated and sealed apply/separate-readback, independent full metadata
comparison, live dry/apply/separate-readback, and independently restored POST
recovery. A stale signature in the second manifest row was rejected in actual
apply mode before either row was written. All 8,328 non-target function rows,
all program metrics/types/bookmarks, and the entire saved stack-purge export
remained identical. Exactly eight parameter rows were added; the unknown
return rows stayed byte-identical. Native `RET 0ch`, declared parameter size
12 and saved UNKNOWN purge are recorded as separate facts.

`python -m unittest tools.ghidra_cohort_framework_tests` again discovered 91:
**85 passed, six existing skips**, including the production Java column probe.
Its tiny temporary source file now uses the platform temporary directory,
removing a Linux-only test-path assumption. The applier's only further change
is the independently reviewed two-row live grant. No C# code changed in this
cohort and no engine build/playthrough was needed. Command arrays, full exports,
negative control and recovery receipts are under
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260912/script-callback-arguments/`;
`script-callback-framework-20260912.log` is in the existing Linux test owner.

### Bounded Unit weapon selector — September 12

`python local-data/test-runs/linux-route-20260906-af1sa_l9/provider-selection-20260912.py`
passed **37** isolated original-code selection/reader cases. It executes ten
unchanged routine bodies plus three constants from the verified pristine
specimen at their original addresses. Its `.inputs.bin`, `.outputs.bin` and
`.results.json` stay private beside the script. Empty spawner lists, current
modes and nonnull nonballistic projectiles are admitted; terrain sampling and
reader clearing are stubs. This is not a retail playthrough or complete firing
acceptance. The script asserts 21 winning-score words and the new PC24
distance discriminator; other retained distances are observations. Independent
read-only review checked the initial 35-case artifact's actual ELF load mappings,
retained inputs/outputs and instruction-derived arithmetic; it did not rerun it.

The new `RetailUnitWeaponSelectionTests` passed **44/44**. With existing
`RetailWeaponSelectionTests` and `RetailWeaponChargeTests`, the final Core
filter passed **117/117**, zero skips:

```bash
dotnet test rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj --no-restore --nologo --filter 'FullyQualifiedName~RetailUnitWeaponSelectionTests|FullyQualifiedName~RetailWeaponSelectionTests|FullyQualifiedName~RetailWeaponChargeTests'
```

Negative controls used the same project and `--filter` with the exact owning
method. Last-wins selection failed **2/2** `EqualScoresRetainAttachmentOrder`
cases. Widened distance arithmetic initially survived **3/3**
`RawDistanceMatchesOriginalPc24Observations` cases. The original routine then
confirmed `(0.1f,0.1f,1.1f)` distance `3f8df578`, where the widened norm gives
`3f8df579`; adding this case made the mutation fail **1/4**. Source bytes were
restored exactly and the final 117-case run rebuilt the correct implementation.
The initial survivor is retained, not counted as a successful negative control.
Commands, TRX files, logs and restoration hash are under the same owner in
`provider-{last-wins,wide-distance,wide-distance-discriminator,final}-20260912.*`
and `provider-mutations-20260912.results.json`.

This additive selector does not yet change the actor firing loop. No gameplay
hash, scheduler behavior or combat assertion changed; no broad combat rerun,
desktop control or new Ghidra mutation was needed for this step.
`git diff --check`, `npm run test:docs` and `npm run test:safety` passed;
the public-payload check examined 3,978 candidates. The npm logs use the
`provider-{docs,safety}-20260912.log` names in the same private owner.

### Weapon provider Ghidra correction — September 12

The five-row `weapon-provider-semantics` manifest passed pristine-body and
independent semantic review, isolated dry/apply/separate-readback, full metadata
comparison, final-spec review, sealed rehearsal, live dry/apply/separate-readback
and independent POST recovery. All 8,325 non-target function rows and target
ABI/bodies/repeatable comments remained unchanged. All variables, types,
bookmarks, saved stack metadata and Plane-depth exports held. The only changed
program metric is `commentsSha256`; all eight live exports equal sealed POST.

A deliberately stale tag set in the fifth row was rejected in actual apply
mode before any row was written. Its separate function/program export matches
PRE byte-for-byte. PRE and POST recovery were restored to new local paths and
opened read-only; the tracked checkpoint was freshly hash-compared and preserved.
Exact command arrays, manifests, exports, control and recovery receipts are in
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260912/weapon-provider-semantics/`.

`python -m unittest tools.ghidra_cohort_framework_tests` passed **91/91**,
with no skips on this invocation. Its production-Java and exact live-twin
derivation checks passed; no framework gate changed. The live twin adds only
this reviewed cohort to its allowlist. Output is
`local-data/test-runs/linux-route-20260906-af1sa_l9/weapon-provider-framework-20260912.log`.

The documentation gate, name-checker self-test and `git diff --check` passed;
all 8,330 projected current names also match the live export. The first payload
check refused the encoded comment manifest. Its ten decoded analytic comments
(8,032 bytes) passed the existing content/secret guards and independent review;
the existing exact-path/hash register now admits only that reviewed file.
The final safety check passed for **3,980 candidates**. The initial refusal and
final pass remain separate `weapon-provider-safety-20260912.log` and
`weapon-provider-safety-final-20260912.log` files in the same test owner;
docs and name self-test logs use the matching `weapon-provider-` prefix.

### Aircraft weapon model inputs and model-time fraction — September 12

`npm run prepare:rebuild-assets` materialized **389 exact files**. The new
166,705-byte static-world manifest has SHA-256
`17d6112a96d548fb546999b79d3980d173ce5bb0a6f0da4573eae28fc5b62c09`.
It equals the independently projected update byte-for-byte. Removing only
the two aircraft profiles' `weaponMounts` and the corresponding provenance
entry recovers every previous JSON field. The prior 165,541-byte manifest and
expected update are retained as `aircraft-mount-input-pre-20260912.json` and
`aircraft-mount-input-expected-20260912.json` in
`local-data/test-runs/linux-route-20260906-af1sa_l9/` (the owner below).
The aircraft mesh remains separately hash-pinned; the static-mesh aggregate
and animation manifest were not widened to imply different source coverage.

`python rebuild/tools/materialize_retail_assets_tests.py` passed **90/90**;
the initial selected aircraft/Airfield/physics gate passed **17/17**. Tests
retain the legitimate earlier GunA/2, exact selector1, ordered uses/raw flags,
CPOS/CORI words, padding exclusion, cache ownership and constant ancestors.
Malformed tuples and ambiguous/missing bindings are rejected.

`TMPDIR=/var/tmp dotnet test rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj --no-restore --nologo`
passed **135/135** with the exact filter
`FullyQualifiedName~Level100ActorRegistryTests|FullyQualifiedName~Level100WaypointFixtureTests|FullyQualifiedName~SimulationTests|FullyQualifiedName~HeadlessApplicationTests|FullyQualifiedName~RetailWorld110InitialObjectSeedAdmissionTests|FullyQualifiedName~RetailWorld110LevelActorsTests`.
The final log/TRX stem is `aircraft-mount-core-final-20260912`; all logs and
TRX files use the owner above. New cases cover both immutable lookup views,
raw-word/use/order identity, nonfinite rejection and cross-definition restore.

`TMPDIR=/var/tmp dotnet test rebuild/OnslaughtRebuild.Client.Tests/OnslaughtRebuild.Client.Tests.csproj --no-restore --nologo`
passed **907 tests**, with the same two existing capture skips (header-font
retail glyph runs and the captured-water envelope). The final log/TRX stem
is `aircraft-mount-client-final-20260912`. Both final dotnet invocations used
`--results-directory local-data/test-runs/linux-route-20260906-af1sa_l9`, a
named TRX logger and `console;verbosity=minimal`. No engine or visible launch
was part of these checks.
`npm run test:docs`, `git diff --check` and `npm run test:safety` passed;
the safety gate checked 3,986 candidates. Their logs use the same owner and
`aircraft-mount-docs-20260912` / `aircraft-mount-safety-20260912` stems.

Definition format 8 adds model input; these runs retain world-state schema 47.
The 838-step Headless route compares **complete canonical bytes each tick**
against an independently stepped format-7 run after replacing only the new
definition identity. Both format-7 and older format-6 state/trace fingerprints
are recovered; the final `--expect` and two-repeat application checks pass.
The Client 2,148-step route uses the public canonical hash each step for the
same counterfactual, retaining both historical fingerprints and its existing
gameplay assertions. This proves input-identity causation on those routes,
not retail parity or full combat. Current fingerprints are owned by the tests:

| Route | State SHA-256 | Trace SHA-256 |
| --- | --- | --- |
| Core 40 steps | `0a0b24633f25bb96ac2e8b98443524de47e065b3744b9a15871c09595127a19d` | — |
| Headless 838 steps | `69bd64ac4b2f344c1300d64e6619931f57dc06d768dbd70a5f1b816aedb1f59a` | `0872e009a2fb254927a3014d539ae1039332ad5eb8bd8af38a6e77cc86575ec9` |
| Client 2,148 steps | `53c1cc64ace55542f48534d0554d6ffed57dda0eae48c9f2a55a928fea096e5e` | — |

Initial Core execution passed 131/135: two current pins required this causal
check, and two World110 isolation tests carried an already-old duplicate
fingerprint. Those isolation tests now compare complete before/after-admission
bytes; `SimulationTests` retains the golden owner. Initial Client compilation
rejected an internal canonical-byte helper; the existing public hash API now
checks each step without widening Core's public surface. Subsequent focused
Client execution reached only its expected old-pin failure after all causal
checks passed. These initial logs remain separate from final results. The
retained Windows smoke validator's older `bc5d…` pin was not repinned from a
Linux in-process result; its native route still requires separate validation.

`python local-data/test-runs/linux-route-20260906-af1sa_l9/plane-model-fraction-20260912.py`
passed **8/8 synthetic cases**. The selected pristine executable was freshly
hash-checked against `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The actual ELF load mapping contains unchanged `[0046ef40,0046efd5)`:
149 bytes, SHA-256 `72fba6a65a6d45e0104ea275f634c1cbb5e3beca98aefd36f489a0bd33b3e356`.
The appended return is outside this range. Supplied base times 0, 256, 65,536
and 1,048,576 use frame-length word `3d4ccccd`, each under PC24/RN and PC53/RN.
At 256 the respective fraction words are `3f7ff000` and `3f800000`, despite
identical stored frame time. Source, ELF, input/output, log and result JSON
share the script stem. The 2,099-byte result JSON has SHA-256
`07dca8819e7ecb20e01c8f1bb19b60cbe45d334ce6088f79b835564d0fa9aa28`.
Both 8,192-byte I/O files and all receiver writes were independently reconciled
against the saved cases. Stack/register checks, x87 TOP/invalid checks and
control-word readback pass; precision status flags are expected. No complete
MainLoop, CGame update, attachment query, renderer or desktop ran. This is a
counterexample to simplifying the supplied fraction calculation, not an
observation of ambient precision/time across retail play. The separate bounded
attachment composition below extends this evidence; production firing remains
open. Ghidra is unchanged.

### Aircraft attachment composition — September 12

`python local-data/test-runs/linux-route-20260906-af1sa_l9/plane-attachment-paths-20260912.py`
passed **27 synthetic cases / 33 calls**, including the follow-up assertions
over saved direct-cache keys and all meaningful cached pose words. It executes
unchanged Unit `004fc4e0` with native tag routing, list/mesh lookup, renderer
dispatch/refresh entry, direct evaluator, Actor getters and math. The ELF's
actual load mappings contain **21 unchanged routine bodies**, the jump table,
GunA/GunB strings, constants and selected Plane vtables; each is compared with
PE-mapped pristine bytes. The executable was freshly verified as 2,506,752 bytes,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The exact aircraft mesh is freshly checked against the separate pin in the
model-input section above. The synthetic emitter table retains the three
relevant records from the eleven-emitter mesh: GunA/2 before GunA/1, with
GunB/1 following; renderer-cache entries use actual part ordinals.

All source, ELF, assembly/object, I/O, log and result artifacts share that
private script stem. The script is 18,183 bytes, SHA-256
`8515aef582c6027c3720dd30b26a26dd3468aae49d9ecd5ae08cb3355da8cff5`.
The 26,556-byte result JSON has SHA-256
`badc59208887ea105562992486736c3945ab0c7b53ef3c6ae98ff621b1f057dc`.
Both I/O files are 552,960 bytes: input SHA-256
`732b7454bb3c5ef8e07ba6cff400e93560e96fd39a7611deb369654597d4d83f`,
output SHA-256 `49af51a963700de475ec46d3b2ebbc8b3c9b5693baaf739f2e8008ad9c9e8323`.
The stronger cache assertions leave these observed I/O/result bytes unchanged.
Independent read-only review reconciled all 25 mapped ranges, all 27 input
graphs, 33 output records and exact cache transitions against the saved artifacts;
it did not rerun the experiment. The ELF SHA-256 is
`1a49e3830627e92980a0a2c4a05f7a0ef3bd77ebe4cdd932af7617c03ec947d0`.

Predictions cover all twelve meaningful position/basis words. Tests preserve
the stack and nonvolatile registers, read back explicit PC24/PC53 control words,
reject x87 stack/invalid faults and check every arena byte outside the declared
output/current-X/profile-cursor writes. Fourth-word padding is not a meaningful
pose claim. The direct-cache snapshots bind the actual receiver/part, model
frame zero and supplied render stamp; other paths leave that cache zero.
The frozen probe's generic `frame` labels mean CGame's render-frame number,
as clarified by the later MainLoop readback; it is not the event-manager tick.

The [Unit evidence owner](reverse-engineering/binary-analysis/functions/Unit.cpp/CUnit__UpdateTransform.md#isolated-aircraft-attachment-composition)
records the causal comparisons: supplied fraction below one changes fallback
pose; a synthetic basis distinguishes accumulation order; same-frame direct
reuse survives current-pose changes but not a frame advance or selected-part
change. This experiment prepopulates the two warm caches and supplies native
one-pose records through synthetic objects. It does not execute the loader,
cache population, animated/recursive hierarchy, nonnull motion, camera state,
complete game or weapon/round delivery. Unexpected selected-boundary calls
are rejection sentinels, never replacement pose implementations. No desktop
control or Ghidra opening occurred; the firing approximation is unchanged.
Actor translation varies only along X; these fixtures do not claim arbitrary
3D arithmetic or independently establish every Y/Z interpolation spill.
`npm run test:docs` and `git diff --check` passed for the existing evidence-owner
updates; the docs log is `plane-attachment-docs-20260912.log` in the same owner.

### Aircraft renderer-cache population — September 12

`python local-data/test-runs/linux-route-20260906-af1sa_l9/plane-attachment-population-20260912.py`
passed **11 cases / 17 calls**, including strengthened per-call cache-guard
assertions. The previous warm-cache artifacts stay unchanged. This experiment
reuses their hash-pinned assembly and pure finite arithmetic helpers, adds the
original recursive cache population and hierarchy evaluation, and verifies all
**27 unchanged routine bodies plus five data ranges** in the actual ELF mappings
against the freshly checked pristine specimen `74154bfa…e7750` above.
The native finite-zero floor path includes its real FPU-control dependencies.

The supplied cache header/arrays follow the initialized shape, with stamp
`-9999`, model time `-99999.0f`, and 12 parts. The full relocated transform
graph and all eleven emitter bindings are derived from the hash-checked training
mesh `48876552…f4e6ec5`; its ELF mapping is read-only. With no CAMD, mode `-1`
and null motion, all twelve parts select hierarchy frame zero. Every meaningful
cached XYZ/basis word agrees with the instruction-ordered oracle and stored
CPOS/CORI under both PC24/RN and PC53/RN: **24/24 part/precision comparisons**.
All twelve resolved-index and inherited-value slots are also checked.

Stamps 0/1 leave the supplied renderer cache untouched and use the direct path;
2/3 populate it. A declared control changes cached GunA/1 X to `-33` between
queries. The same stamp reuses it; the next stamp regenerates the original
hierarchy value. This tests refresh admission, not a retail corruption scenario.
Stack/nonvolatile-register, x87 control/TOP/invalid, per-call cache guards,
direct-cache keys and all other arena-byte checks pass. Padding is excluded
from numerical pose claims. The stronger guards leave observed I/O unchanged.

All artifacts share the private script stem. The final script is 18,112 bytes,
SHA-256 `c923f036dea93911404c2a0c88aa3bf02b4059b7e3c137691332532da7540c51`.
The ELF is 156,816 bytes,
SHA-256 `e4170ddf4a57c8ab987f4edff4d9a1e0700edcf318bd2fdc9b3f6b80d05d5d3b`.
The 22,192-byte graph has SHA-256
`2cb59710502b5ada9efffb9125b457100bd69a881d748c8e3b9f743faad44d1c`.
Both I/O files are 315,392 bytes: input SHA-256
`aae0d77c4794a5615c93173612337a28762b5d291af7893f74a7f0b602f53e73`,
output SHA-256 `68bae66d50afceaa35a5fab531db165d0b0aab44bf9dc6c372ec13e52a1f402a`.
The 23,067-byte result JSON has SHA-256
`0d77a4b243d9257f196698e7169a8a34df9f6ec02d77cad5a37aaf3e47e9ea04`.
An independent read-only review checked the 32 mappings, graph relocation,
retained I/O and arithmetic; it did not rerun the experiment. Its comment-only
correction records that unused zero-filled scalar fields need not fault.

The [Unit owner](reverse-engineering/binary-analysis/functions/Unit.cpp/CUnit__UpdateTransform.md#renderer-cache-population-and-render-stamp)
records the result and limits. Fresh static
[MainLoop readback](reverse-engineering/binary-analysis/functions/game.cpp/CGame__MainLoop.md#render-stamp-and-gameplay-ordering)
identifies the stamp as **render count**, distinct from Update and event frames.
The probes supply this context; they do not execute its real cadence. Allocation,
loading, active motion/animation, camera-latch delivery, integrated firing and
player acceptance remain outside the experiment. No complete game, graphics
renderer, Ghidra or desktop ran. Production simulation behavior is unchanged.
`npm run test:docs`, `git diff --check` and `npm run test:safety` passed
(3,986 public candidates). The same private owner retains
`plane-population-docs-pass-20260912.log` and
`plane-population-safety-20260912.log`. Earlier docs logs retain the corrected
MainLoop header/provenance findings; its one header-backlog entry was removed.

### Common controller and Unit weapon composition — September 12

`python local-data/test-runs/linux-route-20260906-af1sa_l9/plane-common-weapon-phases-20260912.py`
passed **21/21 synthetic cases, 27 calls**, including the rerun with complete
four-word retained/forwarded-vector assertions. It executes ten unchanged
retail routines, including common update, slot-4 refresh and the earlier Unit
phase bodies. The selected specimen remains 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
New raw-body identities are:

| Range | Bytes | SHA-256 |
| --- | ---: | --- |
| `004fef40..004ff322` | 994 | `7aca029cc9b576958d86a01282e847e6b624d29dcbc23b4ae2b89cbf8193fffe` |
| `004ff4f0..004ff70b` | 539 | `4bf6a880bceb0db303c5adab07deb05430df97d61a8bdbe34b99cb608958f60d` |
| `004fbc90..004fbcae` | 30 | `b5a96a9c821defad155def39a7ff2e12ac40d82fc9b1cda0aeeb0ed2f2fbee6d` |

The private source, ELF, exact input/output and result JSON share that stem.
The result JSON is 16,670 bytes, SHA-256
`29205cbcad5ce400f9d0732fee7a16a1bc392aa5db27589561eec70e96899120`.
The 86,016-byte inputs and 107,520-byte outputs were independently reconciled
against all cases, call traces and final receiver snapshots. The harness also
checks unchanged original bytes in ELF load mappings, preserved registers and
stack, x87 stack/error conditions and PC24/RN control word `007f`.

Counterexamples distinguish ready firing from the newly failed preparation
gate, preserve the earlier aim through phase 1, expose two selection calls,
and retain post-fire behavior when WeaponFire returns zero or negative.
Target aim capture/application, A/B feasibility, selection, acquisition,
reader registration, RNG, WeaponFire and waiting animation are explicit stubs;
support/spawner membership is absent. Positive delays and clear-after-fire are
synthetic branch cases. Phase completion is invoked directly. No real projectile,
Plane/Move scheduling, burst delivery, automatic acquisition or geometry is tested.
`plane-normal-static-boundaries-20260912.log` in the same owner binds the
attachment and line-query findings to exact bytes and the freshly hashed physics
records. [The Unit owner](reverse-engineering/binary-analysis/functions/CComplexThing.cpp.md#remaining-selected-provider-integration)
records the consequences and remaining production work.

### Weapon line-query arbitration — September 19

`python local-data/test-runs/weapon-query-20260919-4al_wt70/query_arbitration.py`
passed **53 scenarios / 106 original-code calls**, each scenario under PC24/RN
(`007f`) and PC53/RN (`027f`). The selected pristine executable was freshly
verified as 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The unchanged 1,256-byte query `[0050b030,0050b518)` hashes to
`bca08a3dabe410117feccb3538fbce08599f791794f6654555b685781b39ac2d`.
The array constructor `[004011b0,004011da)`, vector constructor
`[00402d20,00402d23)` and iterator-node conversion `[00492c90,00492c94)`
also execute unchanged at their retail addresses. All four bodies were compared
against pristine bytes through the ELF's actual load mappings.

The script creates a fresh private output directory on each invocation. The
recorded successful stem is
`local-data/test-runs/weapon-query-20260919-4al_wt70/run-njtb3uk6/query_arbitration`;
the ELF, assembly, `.inputs.bin`, `.outputs.bin`, `.stderr.txt` and `.results.json`
share it. The earlier 44- and 51-scenario outputs are preserved in sibling run
directories. The first assembler attempt rejected macro operands before any
original-code execution; its assembly remains in the parent directory.

Independent read-only review reconciled all 106 saved binary records with the
JSON, complete result words, input immutability and exact cross-kind traces,
including stub values and retail return addresses. It separately parsed the PE
and ELF load mappings; it did not rerun the experiment. The final result JSON is
104,683 bytes, SHA-256
`62f8ce270675ab79114ff7359d64e5afc9be57e95cd7039adbbdcb1f2ff3c9d1`.
The same private parent owns `docs-final.log` and `safety-final.log` for the
documentation and public-payload gates.

Every call checks four output words, returned status, unchanged synthetic
receiver/input bytes outside the output record, preserved nonvolatile registers
and stack, restored SEH chain, retained control word, empty x87 stack and absence
of invalid-operation/stack faults. FS checks cover normal return only, without
exceptions or unwinding. Stub checks cover the passed line, terrain flag,
iterator endpoints, translated broad centre and refined translation, plus ordered
candidate visits and geometry/radius/refinement calls. Reversed order and paired
boundary cases distinguish strict proxy admission from inclusive refined ties;
other controls cover masks, exact collision low-bit equality, missing collision/
child, negative proxy, the initial 99999 distance limit, refined-to-broad subhit
replacement, and output-field retention on miss/terrain/early stop. A filtered
candidate followed by an early-stop hit also checks iterator progress. The
initial fixture's next-call expectation did not cover that combination; it was
replaced with complete expected call sequences before adding the case.

Terrain, candidate enumeration, collision/bounds lookup, radius, broad geometry
and refined geometry are **supplied stubs**. The result establishes arbitration
over those inputs. It does not validate the geometry, actual world enumeration,
Weapon B's complete caller, nonfinite behavior, gameplay, Ghidra metadata or the
rebuild implementation. The supplied integer-distance cases do not establish
general PC24/PC53 equivalence. No desktop or production source was used.
The [existing Unit/weapon owner](reverse-engineering/binary-analysis/functions/CComplexThing.cpp.md#weapon-line-query-arbitration-and-retained-result-fields)
records the resulting contract and remaining questions.

### Weapon aim point and native motion provider — September 19

`python local-data/test-runs/weapon-aim-20260919-evgb1qwd/aim_endpoint.py`
passed **21 scenarios / 42 endpoint calls**, covering PC24/RN and PC53/RN.
The original Actor getter executes **38 times**; four prediction-disabled calls
never request it. The pristine specimen was freshly rechecked against the
2,506,752-byte / SHA-256 identity in the preceding query receipt.

| Original range or constant | Bytes | SHA-256 |
| --- | ---: | --- |
| `[0050a0e0,0050a286)` | 422 | `5b0316361a8f4c83df55ed3a827e6aed871a1876a23db88d8d00865c94d8da7f` |
| `[00404120,00404144)` | 36 | `34f806584d1baf2f03b3711999a46c4afc77dfab5a8a4cb760f60bb0387cb1e5` |
| Float 20 at `005d857c` | 4 | `8502957747a29907927566be940a9b39fee0a15dd471ba428eb9eedd15aa80e7` |

Final saved stem:
`local-data/test-runs/weapon-aim-20260919-evgb1qwd/run-gpiwaker/aim_endpoint`.
The ELF, assembly, `.inputs.bin`, `.outputs.bin`, `.stderr.txt` and `.results.json`
share it. The prior run using a motion-copy stub remains in `run-1t02_gvq`.
Each invocation creates a fresh output directory.

The harness verifies original bytes in ELF load mappings, complete endpoint
output, untouched input bytes, return pointer, nonvolatile registers, stack
balance, control word, x87 stack and the specified exception flags. The motion
shim invokes the unchanged getter and separately verifies its return pointer
and copied fourth word. Recorded calls establish the supplied provider order
and receivers. Independent read-only review parsed the PE and ELF separately,
reconciled every saved record and used exact-rational PC24/PC53 rounding to
check the arithmetic. It also reviewed the original-getter extension; endpoint
outputs and statuses match the earlier supplied-motion experiment.

The cancellation control gives output words `34000000/34000000/34000000`
under PC24, versus `34000000/34000000/34200000` under PC53. Zero-speed controls
deliberately test original masked exceptional arithmetic: nonzero distance
divided by zero gives positive infinity with status `04`; subsequent zero
motion gives indefinite NaN with status `05`; zero distance and zero speed
give indefinite NaN with status `01`. Precision flag `20` is recorded but
excluded from the lower-five-bit exception assertion.

Attachment position/orientation and target point remain explicit stubs.
The Actor receiver is synthetic. No real lifecycle, complete target/attachment
provider, collision, Weapon B caller or gameplay runs. Other precision modes,
rounding modes, denormals and unmasked faults remain untested. The
[weapon owner](reverse-engineering/binary-analysis/functions/CComplexThing.cpp.md#target-point-providers-and-weapon-prediction)
separates these observations from the static dispatch and source-unit evidence.

### Weapon B nonballistic caller composition — September 19

`python local-data/test-runs/weapon-feasibility-20260919-v_2sqaqx/weapon_feasibility.py`
passed **22 scenarios / 44 original Weapon B calls** under masked PC24/RN
(`007f`) and PC53/RN (`027f`). The selected pristine executable was freshly
verified against its 2,506,752-byte size and SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The endpoint and Actor-getter bodies retain the hashes in the preceding receipt.
Additional unchanged bodies, verified in the ELF's actual load mappings:

| Original range | Bytes | SHA-256 |
| --- | ---: | --- |
| Weapon B `[005088b0,00509135)` | 2,181 | `3624bd4fc4565f5faa6e6b7e503a0ef5de93157a8f03574b527f597566d3fe99` |
| Magnitude `[004026b0,004026d1)` | 33 | `7de765c91bae23f3bf44eb837806928b78cc76637b667101421546f141c3c4d4` |
| Line copy `[004098e0,0040994f)` | 111 | `8196b18dc22fd421a8d9c2c426b44dba7c0d2d663d79075df73f78f1f35a4496` |

The recorded successful stem is
`local-data/test-runs/weapon-feasibility-20260919-v_2sqaqx/run-laerx66n/weapon_feasibility`.
The ELF, assembly, `.driver.py`, `.cases.json`, `.input.bin`, `.output.bin`,
`.stderr` and `.json` share it; each invocation owns a fresh run directory.
The result JSON is 66,432 bytes, SHA-256
`dd06c651772dcca7961e57467a4fb2a6ed49a369de165fe1d917f6e453a46627`.
Initial disassembly used the existing system disassembler after the default
Python environment lacked Capstone; no package or environment was changed.

The original endpoint executes 42 times and the original Actor getter 40 times;
two height-gate refusals stop before both, and two prediction-disabled controls
skip the getter. A recording world-query stub receives 30 complete by-value
lines and all eight subsequent arguments. Checks cover exact endpoint words,
query arguments and initial result storage, Boolean return, call order and exact
receiver/return-site tuples,
unchanged 4-KiB synthetic object/input arenas, nonvolatile registers, stack,
normal-return FS/SEH chain, retained control word and empty x87 stack.
The displaced zero-speed/zero-motion cases retain invalid/divide-by-zero flags
`05`; zero-distance prediction retains `01`, and direct-copy/height controls
retain zero exception flags. No approximation substitutes for an executed
trigonometric helper: unexpected math or skipped-branch calls exit with failure.
The retained endpoint fourth word `51515151` is harness stack fill, not a retail
constant or recovered value.

Independent read-only review reconciled all 40 saved calls in the preceding
20-case run (`run-sxbtfl7v`) with its inputs, JSON, assembled stubs and actual
ELF load mappings. The final extension adds upper/lower bound refusals with seek
enabled and makes the exact receiver/return-site oracle executable. Its ELF is
byte-identical and the original 40 outcomes, exception words, endpoints and
normalized traces are unchanged; `extension-comparison.json` records that check.
The review did not rerun native code. All four added calls passed the same ABI,
input-preservation and output checks.

Paired controls establish inclusive zero-angle bounds, nonzero seek bypass,
distinct same-allegiance Unit admission, null/non-Unit/wrong-allegiance refusal,
target-type-dependent child mode and the difference between direct copying and
prediction. The full original caller does not sanitize the predicted NaNs before
the query stub. This does **not** execute the real query against those NaNs or
show that ordinary authored gameplay supplies these inputs. Attachment/point
providers, query results and all object state are controlled substitutes;
finite-angle trig, ballistics, real collision, lifecycle and live combat remain
outside this result. No Ghidra or rebuild implementation changed.
The [weapon owner](reverse-engineering/binary-analysis/functions/CComplexThing.cpp.md#weapon-b-nonballistic-caller-composition)
records the reconstruction implications.

### Weapon B finite-angle composition — September 19

The extended `weapon_feasibility.py` command above passed **49 scenarios / 152
original caller executions**: the prior 22 scenarios under two precision modes,
plus 27 finite scenarios under PC24/RN and PC53/RN with supplied CRT mode 0/1.
The pristine specimen was rehashed to the same `74154bfa…7750` identity above.
Original caller/endpoint/getter/magnitude/line-copy bytes retain their preceding
pins. Added unmodified code, checked against actual ELF load mappings:

| Original range | Bytes | SHA-256 |
| --- | --- | --- |
| Angle wrapper, alternate entry and core `[0055dcb0,0055dd7b)` | 203 | `750a2a1cfe8f3f3c052cdffe828c46fc37fcc3c6b52a4abc6f2b1caa7d65ba41` |
| Error-record helper `[00561547,00561583)` | 60 | `e635df29a77e340ab58f4d27a5be9770760e0020bf076ccfc95172775a4c1eaf` |
| Classifiers/control support `[005615a5,00561665)` | 192 | `0e63ae2de4858df9110b8f3e70a81987ad0bc29813de37dcb96d5abf0af98344` |
| Masked-error helper `[005627ea,00562a01)` | 535 | `0036539cb836792003645031c3b392d943c9f26da34627ad0d453431ca8e1349` |
| Error-kind dispatch `[00562a89,00562ab1)` | 40 | `f9b415ecff2961414c5c0888a3e02788d809f3678f2c7e5801911f8edb76f952` |
| Control/status helpers `[00562c76,00562cef)` | 121 | `0b22f26a2c310176d25ac53de9dd73b4c892516c2676ef93c984dd7fce783ae2` |
| CRT dispatcher `[00569cc1,00569d91)` | 208 | `c4475177497be476cdf6ecd75caa3a18fc35761c0abcc93513ec6e2391a2e268` |

The original `asin` name literal at `00653310` and 80-bit pi/2 constant at
`0065373a` are also mapped and pinned in the receipt. Original code handles
finite interior and exact +/-1 inputs; selected exceptional/OS dependencies
trap rather than supplying approximations. The global `009d08b4` is explicitly
supplied and checked unchanged. Neither its runtime value nor the game's current
floating-point mode is inferred from this experiment.

Final stem:
`local-data/test-runs/weapon-feasibility-20260919-v_2sqaqx/run-y3mf5pmc/weapon_feasibility`.
Saved `.driver.py`, assembly, ELF, cases, input/output bytes, stderr and JSON
remain together. JSON: **202,329 bytes**, SHA-256
`d98a3ed85d68687a7948eebaa81cace30491888f93210f8259274fccb22101f5`.
The earlier 124- and 136-call extensions remain separate receipts.

Checks cover all input bytes, original body identities, exact provider call
order/receivers, endpoints, query arguments/result initialization, return values,
nonvolatile registers, stack, normal-return FS/SEH chain, x87 control/exception
state and empty x87 stack. The final deflection is observed after return without
patching the body; all 96 query calls agree with a second observation made before
the query stub modifies its result. There are 150 endpoint and 48 Actor-getter
executions. The prior 44 outcomes/status/endpoint/normalized call traces remain
unchanged, and all 54 finite CRT-mode pairs agree; `extension-comparison.json`
records that comparison.

Independent arithmetic predictions were supplied before reviewing native output:
signed/asymmetric bounds, horizontal reversal, nonunit normalization, identical-
direction residuals, displacement stores and a precision-dependent tiny-angle
boundary. The harness includes the separate arithmetic comparator for the
selected final words. Original `FPATAN` still executes; the comparator is not a
replacement or an assertion of general modern-library equivalence. The
[weapon owner](reverse-engineering/binary-analysis/functions/CComplexThing.cpp.md#weapon-b-finite-elevation-and-arithmetic-boundaries)
records the derived implementation contract and measured discriminating cases.

Subsequent read-only review independently reconciled all 152 saved binary
records, all 17 original code/constant pins through ELF load mappings, and all
14 stub/trap destinations. It checked the stack-relative angle observers and
all 44 prior records, normalizing only the documented new observation/input
fields and relocated harness/stack addresses. It also compared the finite
results with its preceding arithmetic predictions. The reviewer did not rerun
native code; this is an audit of retained execution evidence.

This is finite nonballistic caller composition with controlled providers and
query results. No production reconstruction code or Ghidra database changes in
this experiment; real collision, special mount handling, ballistics, unmasked
faults, other rounding modes and live combat remain unvalidated.

### Shared math-error ABI — September 19

`python local-data/test-runs/math-error-abi-20260919/math_error_abi.py`
passed **eight isolated original-code calls**. The runner rehashed the pristine
specimen and verified the unchanged 60-byte `[00561547,00561583)` body against
its actual ELF load mapping and the pin in the finite-angle table above.
Only its dispatcher at `00569cc1` is replaced with a declared recording/
mutation stub, whose jump destination is also checked. No real CRT dispatcher
or retail process executes in this experiment.

Saved stem:
`local-data/test-runs/math-error-abi-20260919/run-6h_ig7kz/math_error_abi`.
The exact driver, assembly, ELF, command arguments, input/output bytes, cases,
stderr and JSON are retained. JSON SHA-256:
`193c33a2acdbd25be284239d87e0f047c453577fa31d341e01f146c7700d1cf2`;
ELF SHA-256:
`226be50179ae880688d34abe03d28895da1c4928586c540bcf0f038c376562f6`.

The controls distinguish binary64 midpoint rounding, upward rounding, PC24
storage behavior, post-dispatch result replacement, EAX-independent ST0 return,
and the saved-`027f` restoration bypass. Assertions also cover all synthetic
input bytes, every record field including untouched second-argument fill,
the call's return address and pointer offsets, stack canaries, zero argument
cleanup, nonvolatile registers and x87 stack depth. Independent read-only
review reconciled all eight binary records and checked the ELF/stub mappings;
it did not rerun native code. Numerical scope is positive inputs near this
single boundary with supplied masked control words. The
[function owner](reverse-engineering/binary-analysis/functions/CComplexThing.cpp.md#shared-unary-math-error-bridge)
records the contract and its remaining limits.

Three disposable Ghidra model projects and their scopes, commands, logs,
exports and comparisons are retained under
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260919/math-error-abi/`.
The two return-model experiments each change only `00561547`'s prototype and
return/parameter records: all 8,329 other function rows, target locals, existing
types, bookmarks, stack-depth exports and program metrics remain identical.
The seven saved parameters become six explicit inputs, removing the hidden
pointer. Separate read-only processes reproduce each model and all six C
exports byte-for-byte; database files remain unchanged by those readbacks.

The record experiment compares the untyped pointer, typed pointer and explicit
local-record variants. The typed pointer alone already gives a complete record
and visible result field in the C view. The helper's high P-code is identical
across all three stages, including its call-dependent result and later reload.
The reopened final variant changes only the dispatcher's record-parameter type,
the declared helper locals and three added record/pointer types; all existing
types and unrelated rows are unchanged. Its explicit-width `char *32` is an
extra model type, not a required live addition. An explicit local rewrite is
also unnecessary for the demonstrated improvement.

No live Ghidra project, tracked checkpoint or production implementation changed
for these experiments. The subsequent ABI-only promotion below adopts the
physical carrier model; the record-type experiment remains unpromoted.
Initial exploratory export/comparison failures
were missing function ownership and comparison-format assumptions, not native
execution failures; the retained successful readbacks and explicit comparisons
own the results above.

### Round renderer registry — September 19

`python local-data/test-runs/round-render-registry-20260919/round_render_registry.py`
passed **22 isolated original-code cases**. Six unchanged bodies, twelve
file-backed strings, one PE zero-tail empty string and the controlled
dependency trampolines were verified in the resulting ELF load mappings.
The original constructors/default initializer produce the selected table;
the harness supplies zeroed globals and the 47-record construction loop.
Renderer allocation/Init are controlled stubs. No game, desktop, graphics
context, actual renderer or Actor initializer runs.

Default OID 4 yields no factory/Init calls, directly and through the common
Round wrapper. OID 0 and a deliberately admitted OID 4 yield one of each;
the latter's out-of-count control yields neither. Allocation failure yields
one factory and zero Init calls. Controls also cover disabled entries,
negative/zero global count, last-entry bounds, duplicate first-match, unused
Init arguments and the malformed per-record counts 0/-1. Every case checks
complete registry/receiver bytes, stack/nonvolatile preservation and owner
forwarding; initialized objects link to the null prior head. The
[Actor owner](reverse-engineering/binary-analysis/functions/Actor.cpp.md#selected-round-renderer-admission)
records the interpretation and `DEC`/`JS` edge limitation.

Saved stem:
`local-data/test-runs/round-render-registry-20260919/run-ewi5pgxl/round_render_registry`.
Its `.json` receipt SHA-256 is
`e9efa780d57b2a60c6b8e7a475c23c9f7734f26e337ae88d1063186faae11e2a`;
ELF SHA-256 is
`1982c0ec40c09eff81c9de4d8c4cd46e6828ca138aae6ae2322ea47c2fff41f8`.
The saved driver, assembly, exact build commands, input cases and raw output
remain beside them. Independent read-only review parsed the PE/ELF mappings
and all 22 saved outputs; it did not rerun the experiment.

The separate command
`python -B local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260919/round-render-registry/static_receipt.py`
binds selected physics records, weapon-to-round references and all 166 shared
return-4 pointer slots through RTTI. Its `static-receipt.json` SHA-256 is
`44f11693cf446a54bd4a4ba4aadedd059894e4b3c82606efb703f49ca9df662c`.
This establishes one renderer-admission boundary, not retail startup execution,
an exhaustive projectile RNG count, full-combat acceptance or a campaign grade.

The subsequent [two Ghidra cohorts](reverse-engineering/ghidra/README.md#renderer-arguments-and-shared-return-4-correction-2026-09-19)
corrected the wrapper/registry arguments and the shared return-4 leaf's name.
Each passed restored PRE, isolated dry/apply/separate readback, independent
full comparison, live dry/apply/separate readback and independent POST restore.
All nine live exports match the corresponding rehearsals byte-for-byte;
the tracked checkpoint is unchanged. Exact commands, final sealed specs and
recovery receipts are under the same private `round-render-registry/` owner.
`python tools/ghidra_cohort_framework_tests.py` passed **92 tests** after the
two live allowlist entries were generated; the base framework did not change.
`python tools/re_function_doc_names_check.py --self-test` passed with the new
one-row current-name overlay. Its intentional missing-table control emits
`UNAVAILABLE`; that expected refusal is not an untested name projection.
Documentation checks passed. The first public-payload check rejected the new
encoded comments; all six were decoded and reviewed as analytic prose, then
admitted by exact manifest hashes using the existing mechanism. Its unchanged
mutation/path/secret refusal controls and the public-payload check passed.

### Round collision initialization — September 19

`python local-data/test-runs/round-collision-init-20260919/round_collision_init.py`
passed **20 isolated original-code cases**. Six unchanged bodies cover Round
collision Init, base/persistent Init, response, readiness event and the persistent
mask filter. Every body and the original `0.05f` constant were checked against
their executable ELF load mappings. The harness controls allocation, centre,
radius, maximum speed, movement delta, shape selection, scan, geometry, event
request and owner-Hit dependencies. It does not launch a game or open Ghidra.

Selected delayed configuration reaches the controlled scan with flags `0x56`;
its response is called but stops before geometry/Hits. Ready positive controls
reach geometry and both ordered Hits. Event 2999 stays blocked; event 3000 and
`0x12340bb8` restore readiness. Negative geometry, each ignore-pointer direction
and each owner's dead flag distinguish their gates. The native persistent
predicate admits peer type `02000000` for the selected Forseti mask and rejects
it for Blaster; zero-type and Round-bit controls cover both masks. Radius is
`1.75` during scan and `4.0` afterward, or `6.5` with controlled length `2.5`.
These numeric inputs are synthetic controls, not retail observations.

Saved stem:
`local-data/test-runs/round-collision-init-20260919/run-_podygs2/round_collision_init`.
The `.json` receipt SHA-256 is
`dd3585729618177452d7e46c67cf634abd633a8aab24c3de8ca9113144c0e8d7`;
ELF SHA-256 is
`1dcd8bf138d8a0cd7c27333c5112b8edff5ea0f57bd80a74c505d251d5c88a43`.
The driver, assembly, exact build commands, input cases and raw output remain
beside it. Independent read-only review checked PE/ELF binding, all 20 saved
outputs, callback ABI/order and protected storage; it did not rerun the code.
Native helper padding at `+10/+20/+30` remains unconstrained.

`python -B local-data/test-runs/round-collision-init-20260919/selected_static.py`
separately rechecked the authored records and byte-bound factory/vtable chain.
Its `selected-static-receipt.json` SHA-256 is
`df835d4e0a7a96771c6f825bec2ba11da3132d6d7428cdf3deec3b4fdbf0fb79`.
Blaster's nested type ID 3 reaches a getter returning 2; the Round prefix uses
that result to add its extra exclusion bit. Both selected ordinary zero-radius
Round definitions retain the default collision-readiness delay. The
[collision owner](reverse-engineering/binary-analysis/functions/collisionseekingthing.cpp.md#selected-round-initialization--2026-09-19)
records the full contract and distinction between the native persistent
predicate and concrete Round trajectory filter. The same static receipt and
full bodies bind all five collision-component vtables and three distinct
candidate-side filters; their paths for ordinary Round arguments reach no
RNG or unresolved virtual call. This is static closure, separate from the
20 native cases. Five compatible renderer tables additionally close the centre
getters through four pointer-reading bodies, under the valid-object/resource
preconditions recorded by the owner. The next section records the subsequent
speed/queue investigation; it is not part of these 20 controls. Actual scanning, scheduler
cadence, geometry/damage, full Round/Actor execution and total RNG consumption
remain outside these controls; no campaign grade or parity assertion changes.

### Projectile readiness queue and speed dependencies — September 19

`python -B local-data/test-runs/round-collision-dependencies-20260919/readiness_queue.py`
passed **23 isolated original-code cases**, using 18 unchanged scheduler,
monitor/list, finite CRT floor/control-word and readiness-handler bodies.
The executable's load mappings contain the exact pristine bytes and constants.
Inputs are authored initialized manager/component/event/node storage. Only the
16-byte monitor-list allocator and selected diagnostics have recording
replacements; other allocation, resize and floating-point exception paths
are guarded. Private Linux TLS supports the tested FS chain; this does not
execute Windows exception handling or take desktop control.

The controls cover delayed readiness, wrong/high-word IDs, priority 2, existing
monitor storage, already-ready state, null/invalid/empty/over-limit refusals,
relative-clock crossings, ring wrap, computed buckets and strict overflow time.
They also expose a one-update admission difference between controlled x87
PC24/PC64 at one exact float boundary, with neighboring-float controls, and a
growth-disabled overflow failure that increments the count without publishing
the event. The [scheduler owner](reverse-engineering/binary-analysis/functions/CEventManager.cpp.md#projectile-readiness-queue--september-19)
records inputs, ordering, ownership and limits. Live scheduler precision was
not measured and no reconstruction implementation changed.

Accepted stem:
`local-data/test-runs/round-collision-dependencies-20260919/queue-run-nmtsnc4k/readiness_queue`.
Receipt SHA-256:
`5cfaf280ce4b94aa8f8b04a0d6ded98dec61bc6e00bbb017f9171f70ba72704a`;
ELF SHA-256:
`54ee0feceb022b22335d0bf9edd22724661556ca759ff60371eae7179a4c40c8`.
Saved driver/assembly/build commands and per-case inputs, outputs and stderr
sit beside the combined receipt. The earlier 17-case run remains preserved
under `queue-run-zyh47lht/`. Compiled guards check arguments/receiver, stack,
nonvolatile registers, x87 state and private FS-chain restoration. The driver
asserts the snapshot observations and complete component storage; independent
read-only review additionally checks the saved full memory regions.

`python -B local-data/test-runs/round-collision-dependencies-20260919/selected_dependencies.py`
separately binds 62 compatible primary speed-provider tables, 14 targets, 43
complete exported bodies and the constructor candidate absent from the
function export. Its `selected-dependencies.json` SHA-256 is
`a3accd11b68cba11959a68406149403a1152ed8eb95f34781afaa05258afc658`.
The [collision owner](reverse-engineering/binary-analysis/functions/collisionseekingthing.cpp.md#static-maximum-speed-providers-and-linked-parents)
records the normal parent-assignment/type closure and unresolved global
acyclicity. The same receipt binds scheduler allocation arguments, the explicit
20,000-event count, allocator bodies and mutex imports. No Ghidra database was
opened or changed for these findings; no full-shot RNG, retail session,
campaign-grade or parity completion is claimed.

### Debug-log ownership and initialization — September 19

The [logger contract](reverse-engineering/binary-analysis/functions/string-helpers.md#debug-log-ownership-and-history--september-19)
separates static control flow, isolated initialization/reset, and unresolved
live file/heap state. All byte findings select pristine SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Private owner: `local-data/test-runs/round-logging-boundary-20260919/`.

- `python -B <owner>/inspect.py`: pins nine complete contiguous bodies and
  the explicitly identified three-range heap-body envelope. The envelope is
  not a recovered complete contiguous function.
- `python -B <owner>/literal_paths.py`: all **111** bytes of the two fixed
  pool messages remain on the pristine formatter's literal path. Receipt
  `literal-paths.json`, SHA-256
  `392a9a557cca37800ce288e813d1cef9b1726f7e9b9b3752b6acf932ba854e92`.
  This is static table/instruction analysis, not a retail execution.
- `python -B <owner>/initializer_reset.py`: **24/24** original-code controls
  passed. Accepted stem `initializer-run-ar33gbxm/initializer_reset`; receipt
  `.json` SHA-256
  `e2541be24011d1e9d03226d0e0246a0f4f8a535398b64d9b19083f518319f830`;
  executable SHA-256
  `59bc2ddb14c4086f5ce82e0f209841d5ba9aad38bc414885bb2ec21ceb323af1`.
  The saved driver, assembly/link commands, actual load-byte comparison and
  each input/output are retained beside it.

The three complete bodies are `[004415b0,0044161a)`,
`[00441630,0044169a)` and `[004416e0,0044172c)`. Authored adjacent logger
objects and selector values exercise initial output-off/output-on, selectors
0/1/2/`FFFFFFFF`, and initialized/1/7 flag states. A recording exit-registration
hook is the only substituted dependency. Four full 5,120-byte snapshots per
case distinguish each initialization, the authored pre-reset state and the
reset result. The reset preserves the other logger, filename, vptr,
first-attempt flag, text interiors and guards; nonvolatile registers and stack
sentinels also pass. Independent read-only review reconstructed those exact
writes from the saved bytes and outputs; it did not rerun the experiment.

The function names and corrected comments belong to the separate
[five-row Ghidra cohort](reverse-engineering/ghidra/README.md#debug-log-metadata--september-19).
The warning-specific disabled route does not establish arbitrary-format
safety. Enabled file logging may reach a CRT allocation-failure handler before
a successful retry. Actual enable, locale, heap mode, retry/handler state,
startup/parser execution, file I/O, rendering and complete-shot RNG remain
outside these results. No desktop or game session was used.

### CLI initialization and parser ownership — September 19

`python local-data/test-runs/cli-startup-20260919/inspect.py` pinned the complete
initializer, startup wrapper, parser and WinMain bodies against pristine
`74154bfa…7750`. The complete parser review identified 25 comparisons and their
direct actions; `parser-static.json` binds the literals and five complete
helper bodies. This was static review, not execution of all options.

`python local-data/test-runs/cli-startup-20260919/initializer_control.py`
passed **4/4** original-code cases: zeroed/poisoned receiver memory crossed
with the external `0066e94e` byte at `0/1`. Accepted stem:
`local-data/test-runs/cli-startup-20260919/initializer-run-48y5v5ma/cli_defaults`.
Its receipt SHA-256 is
`917010a27b097282015b3b71821cebece4099fe47d091f2b41f5fea4655422a6`;
the actual ELF SHA-256 is
`8fde3fcd2aa5ccf3dd177c1ade38bcccce622edf068f50faa847c12a624a7cfc`.
All 459 original body bytes and 26 literal-range bytes remain unchanged at
their original addresses. Each case compares a full 864-byte guarded
postimage, returned receiver, stack/nonvolatile registers and external-byte
preservation. No dependency stubs are needed: this body makes no calls.
An independent reviewer reconstructed all outputs from the saved instructions;
that review did not rerun them. Static disassembly commands are retained in the
private body receipts.

The [one-row Ghidra correction](reverse-engineering/ghidra/README.md#cli-initializer-ownership--september-19)
passed fresh PRE equality/restore-open, isolated dry/apply/separate readback,
independent exact-cohort review, live dry/apply/separate readback and independent
Archive A POST restore-open. Exactly one name, nonrepeatable comment and tag
set changes; all 8,330 other functions, every ABI/variable/type/stack record
and program structure stay unchanged. Only the comment digest moves among
program metrics; all nine live exports equal rehearsal. The initial unsupported
`dry-run` mode refused before writes and the replica stayed unchanged; corrected
`dry` passed. Stale-comment and name-collision controls both refused before
writes. The final spec seals the measured rehearsal; no second sealed rehearsal
is claimed.

`python -m tools.ghidra_cohort_framework_tests` passed **92 tests**;
`python tools/re_function_doc_names_check.py --self-test` passed.
Commands, logs, comparisons, refusals and recovery receipts are in
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260919/cli-initializer-ownership/`.
`compare_exports.py rehearsal-post` and `compare_exports.py live-post` compare
the complete exports. The [parser owner](reverse-engineering/binary-analysis/functions/CLIParams.cpp/CLIParams__ParseCommandLine.md)
records the source/retail distinctions and unresolved consumers. No full parser,
retail startup, later selector values, file I/O, desktop or gameplay acceptance
was exercised.

### Original parser and startup selectors — September 19

`python local-data/test-runs/cli-startup-20260919/parser_control.py` passed
**47 isolated original-code cases**, retaining the complete parser, initializer,
native ASCII scanner and helper bodies at original addresses. Accepted stem:
`local-data/test-runs/cli-startup-20260919/parser-run-m20ei0zy/cli_parser`.
Receipt SHA-256 `e6dca9f618862716ac0c129f151335938b3d81e8e72e441146a4a499173a1296`;
ELF SHA-256 `9d785de30b3e49cb1a24ad7b38b2fa5f40474a9d894ae23336a151497f5104cf`.
Each case compares 8,400 bytes of selected state, including input immutability,
both guarded receivers and both complete logger extents. Forty-six verify
normal-return ABI preservation; the version case takes an intercepted
nonreturning exit. A forbidden syscall control terminates with SIGSYS.

The [CLI contract](reverse-engineering/binary-analysis/functions/CLIParams.cpp/CLIParams__ParseCommandLine.md#isolated-parser-execution--september-19)
records argument ordering, conversion failure, windowed guard, timeout,
resolution, directory-prefix and version-exit controls. Independent read-only
review checked all saved bytes, inputs, outputs and the compiled syscall filter;
it did not rerun them. Initial setup refused an incorrect single-range assumption
for `strchr`; the next harness returned 99 with a malformed filter descriptor.
Both were corrected before accepted execution. The intermediate 45-case run
and all failed attempts are retained separately; they are not added to the
47-case pass count.

`trace_consumers.py` then reproduced ten absolute developer-selector reads,
the startup call chain and the bounded absence of identified trace-field
consumers. `trace-consumers.json` and `selector-neighbors.json` retain body
pins and disassembly commands. These corrections change documentation only;
the Ghidra working project and tracked checkpoint were not opened or modified.
Native review records are retained under the existing audit owner in
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260919/cli-parser-review.json`.

OS/printf boundaries are authored hooks. The false directory result uses last
error zero and does not cover normal nonzero Win32 error handling. Original-code
checks use authored startup memory/default locale and are not a retail launch,
whole-process write audit, console rendering, full startup or gameplay acceptance.

### Original save and startup controls — September 19

`python -P local-data/test-runs/save-startup-20260919/startup_control.py`
passed **17 isolated original-code scenarios**, retaining 38 code envelopes
(10,828 bytes; 10,817 body bytes plus the already identified 11-byte `strchr`
alignment envelope). Accepted stem:
`local-data/test-runs/save-startup-20260919/startup-run-o3zcj6ov/startup`.
Receipt SHA-256 `9639d263d59a96532c7f182d1e0b209f20b4faa90bc9e4acc519c8dd938a45f7`;
ELF SHA-256 `1a3ea8c014e2e7f9e8fe16b4dd8bbe0a2b6b0223d6a843aadcdc85ed04b7694a`.
`startup-controls-v5.log` retains the command result; the immutable driver,
assembler/linker commands, inputs, output buffers and stderr live beside the receipt.

The original WinMain, parser, career initializer/load/Blank, binding-table
initializer and options-tail reader execute. The driver supplies Windows
version/system-query, file and allocation boundaries, plus a controlled
adapter/device/mode context. WinMain returns through its ordinary failure
return after an intercepted graphics-create call. No window, actual game-file
operation or desktop control occurs.

Cases cover missing/empty/short/wrong-version inputs, successful settings load,
the CLI read-name override, changed/unchanged audio settings, noncanonical
boolean bytes, integer/float conversion loss, conditional graphics-reset
request, and matching-second/unavailable/empty display-mode lists. Three
snapshots compare the selected career/binding/settings state, complete input
immutability and read-buffer guards. Conversion uses `fninit`'s default x87
state. The preset hook's copied tail is taken from an authored address; it does
not independently measure the reader's cursor or returned end pointer.

**After WinMain returns**, the driver separately calls original Save,
SaveWithFlag and the default-options writer. It compares both complete
10,004-byte serializer outputs and guards in every scenario, and observes the
packed-mode refresh and live progress word. Full state snapshots precede those
serializer calls; only the explicitly captured fields establish their observed
live-state effects. The file writer receives the original fixture-derived
buffer, not either serializer output. This is neither a serialize→file→reload
round trip nor evidence that startup automatically writes settings. Writer
success/open-failure/short-write/close-error results are supplied by hooks;
actual publication durability is untested.

Audio, preset/language actions, diagnostics and final Goodie recomputation stay
intercepted. The raw original Goodie dependency and complete normal menu-load
transaction were not executed. A Linux seccomp negative control attempts
`getpid`, terminates with SIGSYS (`-31`), and produces no output. The admitted
syscalls are only read/write/exit. The pristine executable and real tracked save
fixture are rehashed unchanged after execution.

The first 10-case experiment intercepted the whole tail reader. The following
attempt retained that reader but failed an expectation that the real fixture's
audio choices equaled CLI defaults; they differ. That failure remains in
`startup-controls-v2.log` and `startup-run-drggwcgp/`. Subsequent 14- and 17-case
intermediate results remain separate, not added to the final pass count.
Independent read-only reviews checked saved code/input/output identities,
compiled sandbox instructions and the serializer extension; they did not rerun
the experiment. Records use the existing ignored aircraft-audit owner.

The [subsystem contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md)
separates executed findings, fresh static checks, inherited receipts and pending
cross-runtime acceptance. This tranche changes RE documentation; it does not
modify Ghidra or either implementation lane.

### Original menu load and next startup — September 19

`python -P local-data/test-runs/save-startup-20260919/menu_control.py`
passed **20 isolated composed menu-load cases**, retaining 18 unchanged original
bodies (2,974 bytes). Accepted stem:
`local-data/test-runs/save-startup-20260919/menu-run-47t_hlhy/menu`.
Receipt SHA-256 `720608d9374496a1341259191136537c6a903c725a468e1eafb60c8092159211`;
ELF SHA-256 `bc6212a7849c6fa9c6880de80c0e95f92e194e371c635b3058a49f1669985ee9`.
`menu-controls-v1.log`, saved driver, assembler/linker commands, inputs, full
outputs and stderr retain the invocation. No failed experiment preceded this
accepted set.

The complete original menu body calls the real PC card-info/read/name-conversion
code, career Load(flag 1) and conditional default-options writer. Cases cover no
selection, missing/empty/short/version-failing reads, successful load, supplied
writer open/write/close failures, reader close errors, low-byte publication
gating, changed device/slot and low-byte filename alias/truncation. Two explicit
dependency controls make the intercepted page callback set/clear the gate;
these prove the test occurs after the callback, not that an actual page callback
has those effects.

Complete selected career/binding state, input and read-buffer immutability,
guards, attempted publication payload, call order and preserved calling
convention are compared. Font lookup pops one argument; the remaining pushed
values belong to the subsequent eleven-argument dialog call. The original PC
card-info stub reports present/formatted, so unavailable-card branches are not
claimed executed. Latest-world selection, text/font/dialog/page behavior and
file/allocation services are intercepted. Only read/write/exit syscalls remain
admitted; forbidden `getpid` again terminates with SIGSYS and no output.

`python -P local-data/test-runs/save-startup-20260919/menu_to_startup.py`
then passed the successful menu case's exact captured payload to the earlier
original WinMain executable. Accepted stem `menu-boot-qssmorvv/chain` in the same
owner; receipt SHA-256
`533c72da0958207b18b1eb5ea20ec378598226a3c0ca5065451d71906f2f3639`;
command result `menu-to-startup-v1.log`. It checks the preserved menu-live volume
bits, changed next-startup volume bits and audio-action arguments, binding copy,
sensitivity, progress reset and immutable input. A comparison with the earlier
checked startup case is a continuity check, not an independent semantic oracle.
The startup driver's separately invoked post-WinMain serializers/writer are
outside this chain claim.

The storage handoff is supplied and assumes successful publication. These
experiments establish neither durable writes nor actual CRT double-close
effects, desktop startup, input/audio acceptance or complete save compatibility.
Pristine executable and real tracked fixture identities are checked unchanged
after execution. No Ghidra or implementation-lane code was changed.

### Original control preset behavior — September 19

`python -P local-data/test-runs/save-startup-20260919/preset_control.py`
passed **20 direct original-code cases**, retaining nine unchanged bodies
(2,499 bytes) with no intercepted callees. Accepted stem
`local-data/test-runs/save-startup-20260919/preset-run-viieck2x/preset`;
receipt SHA-256 `e69513d9c0cec731d786cd2ca8933a63b12ec7c28bc9af6f03da45b2a1ee2c70`;
ELF SHA-256 `c9a28da4f3120e00a7f76e99a3473da41d9947bfb54957b5c473040c38eea51d`.
`preset-controls-v2.log`, immutable driver, commands, inputs, outputs and stderr
retain the invocation. No failed execution preceded the accepted cases. An
earlier inspection tried to read the fallback table directly from the PE and
was correctly refused because the addresses are BSS; the experiment instead
executes its actual initializer.

The original single/dual/fallback initializers, three entry helpers, FindById,
ApplyPreset and GetSaveSize execute. The driver copies real fixture binding
rows into the initialized runtime table; it does not call Load. BSS retains
ordinary zero initialization, with explicit surrounding guards. Authored
detected counts stay within `0..4`; flags include enabled, disabled,
out-of-count and noncanonical-nonzero examples. Schemes cover 0, 1, 2, 3, 4,
65535 and a negative direct-call value that cannot arise from the saved u16.

Comparisons cover complete runtime and preset tables, guards, immutable input,
size before/after and the calling convention. One/two/three-device cases
distinguish actual selected indices and the clearing of secondary-slot field0
across inactive rows. The initial 19-case artifact remains at
`preset-run-8ook0_le/preset`; its inactive rows already had field0 `-1`, so
unchanged output alone did not demonstrate those writes. Read-only review
identified that limitation. The final added control seeds all 31 inactive
secondary slots to `(3, 0x44556677, 0x12345678)` and verifies exactly
`(-1, 0x44556677, 0x12345678)` afterward. It also asserts nonzero-scheme
preset-cursor destinations. Missing/duplicate/inactive/early-sentinel runtime IDs
exercise lookup and size effects. A deliberately changed preset with absent
secondary slots exercises the general fallback branch; it is explicitly not
the untouched shipped group. The read/write/exit-only syscall filter again
rejects a forbidden `getpid` with SIGSYS and no output. Fixture and specimen
identities remain unchanged.

This establishes the selected helper behavior, not device enumeration, key
delivery, selector/remap UI execution, full loader/preset composition or
arbitrary malformed-save safety. The [binding contract](reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md)
separates these executions from fresh UI instruction checks and inherited
historical mappings. No Ghidra or implementation code changed.

### Original loader, preset and serialization composition — September 20

`python -P local-data/test-runs/save-startup-20260919/load_preset_control.py`
passed **19 composed original-code cases**, retaining 19 unchanged bodies
(4,976 bytes). Accepted stem
`local-data/test-runs/save-startup-20260919/load-preset-run-k8m1uqgd/load`;
receipt SHA-256 `2235a9b50f4d537e1ec45c5fabc2c491ca6c73450d59d0608496e2c2fcab8610`;
ELF SHA-256 `e8a67606bbf1c716b2509442682e681a1415a34b567b5732de6059161a0f727e`.
`load-preset-controls-v1.log`, immutable driver, assembler/linker commands and
complete input/output/stderr files retain the invocation.

Original table initializers, Load, TailRead, ApplyPreset and helpers execute;
original Save/TailWrite run after the final Load. Cases cover ordinary custom
and preset settings, authored enabled-device inputs, low-byte flags, version
rejection, incoming inactive/sentinel/duplicate metadata, preset restoration,
preexisting inactive/sentinel rows and an alternate career receiver. Both
direct repeated loads use the same input in the same process. Actual ESI at
the intercepted language call measures the tail-end cursor; Load's return
does not expose TailRead's return value.

The selected before/after snapshots, complete source, table guards and entire
serializer capacity are compared. Incoming inactive metadata changes sizes
`10004 → 9972 → 9940` over two direct loads; incoming first ID `-1` makes the
next size 9492. The preset-one case restores the tested active row. These
results do not establish drift across fresh startups, which initialize the
tables again. Audio actions read canonical career globals even with an
alternate receiver. The serialized result is not reloaded, and post-Save
whole-memory state is not claimed measured.

Language/audio/latest-world services and diagnostics remain intercepted here.
No Blank, file caller, real input or process restart occurs. A read/write/exit
seccomp filter rejects forbidden `getpid` with SIGSYS and empty output; fixture
and pristine executable are rehashed unchanged. A read-only review separately
checked the bodies, instruction-shaped table oracle and saved results without
rerunning original code.

### Original language copy and save composition — September 20

`python -P local-data/test-runs/save-startup-20260919/language_control.py`
passed **16 composed original-code cases**, retaining 22 unchanged bodies
(5,207 bytes). Accepted stem
`local-data/test-runs/save-startup-20260919/language-run-n__ph8sw/language`;
receipt SHA-256 `016b415f9846f13e02fc2c290e5c96c52e01f1af9cc245d30d119cf507fde5dd`;
ELF SHA-256 `f2db062ad045c30ae35d067cc986bb6b30d8888856bbfba470e3477890949ebf`.
`language-controls-v1.log`, immutable driver, commands and saved inputs/outputs
retain the invocation under the same private owner.

This extends the actual Load/TailRead/preset/Save chain with original language
selection `00466ab0`, cleanup `0051f8e0` and text copy `004f2660`. Cleanup takes
its real null-object path. Five cache slots, an adjacent-state negative header,
source byte buffers and allocation destinations are explicitly authored;
allocator/free calls are intercepted and recorded. Their preserved argument
cleanup is checked along with the caller's stack/register guards.

Cases distinguish copied header language from requested selector, low-WORD
serialization of a full language DWORD, repeat selection, null/existing prior
buffers, sizes 0/1/3/4/7/17, original preset composition and flag/version skips.
Index 5 and out-of-buffer source-pointer controls exercise unchecked selection
and pointer rebasing without calling those supported configurations. Complete
selected headers, buffers, guards, input and serialization capacity are compared.
Events capture active-header and mirror values before freeing, during allocation
and after copy; actual ESI at the audio-service boundary measures the tail end.
The last 16 header bytes survive, and Save consumes the copied language field,
not the input mirror. The repeated case frees the first returned buffer before
receiving a distinct second allocation.

The same syscall restriction/forbidden-call negative and original-input hash
checks pass. These controls establish neither actual language-file parsing nor
allocation failure, nonnull object destruction, audio output, durable save
publication or localized presentation. The complete loader/preset and language
review records use the existing ignored aircraft-audit owner. No Ghidra or
implementation-lane source changes accompany this documentation tranche.

The subsequent static dependency inspection reads complete `CText__Init`
`[004f21f0,004f2497)`, SHA-256
`f208b0fcea5393790160ea84b43bd07d441566d7f264b2ea77251b3badb499ca`,
and the actual fatal chain `0042c750 → 0042cfa0 → ExitProcess` plus cached-read,
size, ctor/dtor and close helpers. Selected disassembly is retained as
`language-<address>.asm` in this same owner. That static phase did not execute
the initializer or fatal chain. `language-file-inputs.json` pins six bounded
preserved-file reads and their version-3/count-2571 headers. The following
experiments supply the later executed evidence.

### Original language file parsing — September 20

`python -P local-data/test-runs/save-startup-20260919/language_file_control.py`
passed **19 original-code cases**, retaining ten unchanged function bodies
(1,982 bytes) plus Init's one alignment byte and 20-byte switch table.
Accepted stem `local-data/test-runs/save-startup-20260919/language-file-run-8clnw9rt/file`;
receipt SHA-256 `a3bebcc872a6df436cbbdd01351ea4ab0599c55fa48954ef8d48f1ba46d3aaec`;
ELF SHA-256 `50afc2b7a9a9d7ec9755dfd2b2c88f3b8bb73e99622e016f73b06a359626a57e`.
`language-file-controls-v2.log` records the passing invocation. The first
build failed because output overlapped TLS/arena; no original code ran.
`language-file-run-s2cqn14x/` and `language-file-controls-v1.log` retain
that failure. The accepted output base is `0x0a000000`.

Original Init, ctor/dtor, file-size/cached Read/Close and SetLanguage/null
cleanup/CopyFrom execute against the six admitted files and owned derivatives.
Open supplies the byte-backed final-prefetch object shape; formatting,
allocation/free and GetFileSize/CloseHandle are explicit hooks. No refill,
decompression, real file access or heap failure is exercised.

The 19 cases cover six language files, American override of a French selector,
invalid Init selector/English fallback, 16-byte and empty cache reads,
unknown versions with/without the high bit, v1/v2/legacy header derivatives,
two header guard skips, Open failure and a CloseHandle error. Full selected
state, allocations/guards and complete input are compared. Copied bytes and
the logical count at Close measure the short reads; Read's EAX is not separately
captured. Short/empty cases use declared zero allocation fill, so loaded state
does not establish usable text. Version derivatives establish arithmetic only;
high-bit v2/v3 auxiliary parsing remains outside this cohort.

The Open-failure child stops at the fatal call with exit 17; it does not
manufacture cleanup/unwind. Normal Init restores the valid `FS:[0]` sentinel
provided through i386 TLS; stack and callee-saved registers are checked.
The invalid Init selector is 65535 but the later SetLanguage cache slot is zero.
Actual SetLanguage bounds safety is not established. A forbidden-call negative
ends with SIGSYS; original specimen/resources remain unchanged.
Independent read-only review reproduced embedded bytes and saved state
without rerunning the experiment.

### Original language lookups from parser output — September 20

`python -P local-data/test-runs/save-startup-20260919/language_lookup_control.py`
passed **17 cases**, with three unchanged lookup bodies (420 bytes).
Accepted stem `local-data/test-runs/save-startup-20260919/language-lookup-run-ekd5wuja/lookup`;
receipt SHA-256 `13dff5555778153c3971046d8771c99ddd66c6114332df6dcc9c8c83e102db7b`;
ELF SHA-256 `208d8bef42c1c8ba62c70e716c714690aaff9784579d4cd67c7dea53b396a079`.
`language-lookup-controls-v1.log`, immutable driver/assembly, commands and
all inputs/outputs preserve the accepted run.

The experiment imports exact active headers and allocation snapshots from the
previous parser/copy outputs, with producer receipt/output hashes checked.
For each of six resources, all 2,571 record IDs and one absent ID pass through
original text, audio and After lookup. After uses +1 for each nonfinal record,
zero for the final/missing controls. Eleven owned derivatives test duplicate-first
selection, negative/excess/wrapped displacement, cleared loaded state,
v1/unknown/negative versions, nonpositive counts and unchecked pool offsets.
There are 46,338 native calls; this is a call count, not extra independent
acceptance cases or a parity percentage.

The entire imported header/arena/input remains unchanged. Results match ordered
pointer selection; real-file pointers are also checked offline against declared
pools, termination, UTF-16LE and ASCII decoding. All six files have unique IDs.
Adverse returned pointers are compared without dereferencing. The ordinary
logger is intercepted; legacy MultiByteToWideChar is not exercised.
Stack/register guards and forbidden-syscall negative pass. The logger records
its first three arguments; After's fourth diagnostic argument (requested offset)
is not captured. Independent read-only review checked all returned pointers,
saved memory, embedded bytes and decoded rows without rerunning native code.

This establishes bounded parser-output/lookup compatibility, not continuous
startup, actual audio assets/playback, glyph rendering or save publication.
The separate four-probe decoder check reproduces missing offline bounds and
termination validation using only in-memory derivatives; private receipt
`language-lookup-consumer-probe.json` SHA-256
`39b6ba91c73b1b164efafa3cb31733074361ea8a0a7b86c122b32241a3c02bf3`.
No production decoder/rebuild/companion source is changed by these contracts.

### Original audio volume controls — September 20

`python -P local-data/test-runs/save-startup-20260919/audio_volume_control.py`
passed **50 cases**: 25 scenario/rounding combinations, each at PC53 and PC64.
Accepted stem `local-data/test-runs/save-startup-20260919/audio-volume-run-vra1oais/volume`;
receipt SHA-256 `80a944c49b0e54c3ee76cd128d7f314dcd440a935a14dbd1874a4775e85f29a0`;
ELF SHA-256 `7cc622a08f0df338ca075fd585e40983cce52eb0d8247d152af8426333ce10b9`.
`audio-volume-controls-v2.log` records the invocation. Earlier 25 PC64-only
cases passed at `audio-volume-run-jcl2i1js/volume`; v2 expands precision
coverage, rather than repairing a failed case.

Four unchanged bodies (917 bytes) execute with original constants: music and
sound setters, GetCamera and PC UpdateSound. Authored lists include both
categories, playing-byte/channel variants, tracked positions, null buffer slots
and an owned 2D COM object. Intercepted methods record SetVolume, SetFrequency
and GetStatus; the sole failed HRESULT case is SetVolume. GetStatus supplies
a playing status. The stopped-buffer and 3D COM routes are excluded.

Complete before/after-music/after-sound selected snapshots, guards and input
copies match an exact-rational oracle. Chosen intermediates fit both precisions
and distances have exact integral square roots; agreement does not prove
precision equivalence for arbitrary inputs. Four rounding modes produce distinct
integer results. Manager fields change before the logger, career globals after
it; event fields and 28 COM observations across the 50 cases match.
The saved fixture supplies raw music/sound words from offsets `0x2492/0x248e`.

Native integer ABI guards and Python x87 control/TOP checks pass; no full x87
tag audit is claimed. A forbidden getpid ends with SIGSYS, and specimen/fixture
bytes remain unchanged. Independent read-only review checked all saved results
without rerunning the executable. There is no audio-device creation, playback,
Load/TailRead, Save, reset/bank execution or full-process preservation claim.

Fresh static inspection follows entry `00560181` through
`0055dd7b → [006532e8]=0055da76 → 00560cb1` to the control-word helpers
`0056947e/00569449/00569494/00569526`. The configured mask changes precision
to 53 bits while preserving rounding-direction bits. This does not establish
the initial rounding direction or FPU state after device calls. Complete selected
disassembly is retained as `audio-<address>.asm` in the same private owner.

### Original Load, audio and Save composition — September 20

`python -P local-data/test-runs/save-startup-20260919/load_audio_control.py`
passed **16 composed cases**, retaining 26 unchanged bodies (6,124 bytes).
Accepted stem `local-data/test-runs/save-startup-20260919/load-audio-run-ehbe0h_d/load`;
receipt SHA-256 `3f92794e90da6d0728787ecfe6be39f3e8cd441ab43a1baec5352a962b74a972`;
ELF SHA-256 `347f511146830f5a9ec25996958234a6e0d5e9dd345a43a30e76706de6bab1e5`.
`load-audio-controls-v1.log` and immutable driver/assembly/input/output files
retain the command and result. The unchanged parent language driver is pinned
in the receipt.

The original music/sound setters replace the former hooks inside the accepted
Load/TailRead/preset/language-copy chain, followed by original Save. One authored
playing event reaches original PC UpdateSound's null-buffer return; a second,
nonplaying tracked event still receives both volume-field updates. Manager/event
state is compared in full alongside existing career, binding, language, guards,
input and entire serialization capacity. Real setter logs are observed as
double arguments; the old intercepted-call argument layout is not reused.
This logger layout omits music's additional integer argument; the direct controls
capture it separately. The 16 cases vary composition/language conditions using
one volume pair. Every active case reaches the bank hook, so the reset branch
is not covered by this run.

The fixture gives configured music 51 and sound master bits `0x3f19999a`;
the tracked event's fields become `(-3600,-4000)` in this declared state.
Repeated loads, low-byte flag modes, version rejection and the existing
language-copy controls retain expected results. The preservation mode and
wrong-version cases leave sound-event state unchanged. PC53 nearest is supplied
and checked after execution. These are not measurements of a real detected
audio device or initialized game scene.

Reset/language-bank, allocator/free, diagnostics and latest-world remain
explicit hooks. No real language-file parsing is added here, and the output
is not fed back through a durable file round trip. Input/specimen preservation
and forbidden-syscall controls pass. Independent read-only review checked the
complete saved composition without rerunning it. No Ghidra or implementation-lane
source changes accompany this tranche.

### Original audio reset and music restoration — September 20

`python -P local-data/test-runs/save-startup-20260919/audio_reset_control.py`
passed **26 cases**, with nine unchanged original bodies (985 bytes) and the
20-byte original selection table. Accepted stem
`local-data/test-runs/save-startup-20260919/audio-reset-run-qi8cblpe/reset`;
receipt SHA-256 `1261c203280b093848bec7f080419e941a9e6e1558b3e84458d7d9b98a71a74e`;
ELF SHA-256 `981c2131385de9664167f629664994cd8931a5cf5415310dc5dd78be016b90f5`.
`audio-reset-controls-v1.log` retains the command result.

Complete selected snapshots, guards, input copies and **625 ordered hook
observations** match. The original wrapper/reinitializer, sample deletion,
music shutdown/Init/selection, level selection, device shutdown and message
voice helper execute. Supplied Init returns distinguish AL from higher bits;
wrapper/playing flags use low bytes, while music-enable and refresh-suppression
use full words. Cases include failed initialization, empty/short/new playlists,
Level 100/110/frontend selection, repeated reset, cutscene admission and an
alternate receiver's canonical sample refresh.

The preserved fixture supplies music volume bits, producing configured integer
51 under the supplied PC53-nearest mode. Music's current-song pointer can remain
after the recorded playlist frees. Shared authored pointers in the alternate
case and hooks that preserve their memory do not establish valid lifetime after
real destruction. Integer ABI and x87 control/TOP checks pass; full x87 tag words
and whole-process preservation are not asserted. A forbidden syscall ends in
SIGSYS, and original specimen/fixture bytes remain unchanged.

Device Init, music-platform/playlist construction, sample-bank publication,
allocation/free/destructors, sample lookup, voice stopping, virtual playback,
RNG and formatting remain declared hooks. These exercise caller behavior under
supplied results, not real API failures, devices or playback. Trace hooks observe
calls to `0040c640`, whose original body is RET; they do not recover retail logs.
Selection categories 1/3, active-track transitions, negative RNG and the separate
byte music override are not covered. Load/TailRead and Save remain separate.
Independent read-only review reproduced saved results without rerunning them.

### Original language-bank admission and retry — September 20

`python -P local-data/test-runs/save-startup-20260919/language_bank_control.py`
passed **22 cases**, retaining seven complete bodies (1,166 bytes) and the
20-byte language-name switch table. Final stem
`local-data/test-runs/save-startup-20260919/language-bank-run-7p1_0_ep/bank`;
receipt SHA-256 `c121f8a7da97a19c327eda2966db9d7d8db300a0b8867284177718d9b678d8fb`;
ELF SHA-256 `9ca10744f39c7cfd80cc245b91245d68140f4f4b2a1f1e5820c5381215805270`.
`language-bank-controls-v3.log` records this final run.

Original Reload, GetLanguageName, ASCII stricmp, 64-slot buffer Stop,
compressed-bank admission and file ctor/dtor execute. Open always returns zero
at an explicit boundary. All selected snapshots and **223 ordered observations**
match: early cache writes, full list relinking, Stop without pointer clearing,
sample-destructor calls, failed-open cleanup and preserved input/guards.
Same-path retries skip after failure or admission changes; a different language
retries. Case-only path changes also skip. All five names, unknown/negative-ID
fallback and the American-text distinction are checked.

The alternate receiver has distinct buffer objects and cache text: Stop and
Open use the canonical manager, while the selected manager owns event/sample/cache
updates. Event/sample nodes remain shared authored objects, not independent
healthy managers. The formatter supplies only the verified two-string bank path;
original sprintf and non-C locale behavior are excluded. Normal FS registration
restoration, integer ABI and forbidden-syscall controls pass. Original specimen
bytes remain unchanged. There is no actual file-open error, allocation/free,
COM Stop/destruction, successful bank parsing, codec, playback, Windows exception
dispatch, Load/TailRead or Save execution in this cohort.

The initial `language-bank-controls-v1.log` preserves one oracle failure at
`language-bank-run-ydd_0rts`: the second destructor free-return site was written
as `00547db0`. Fresh inspection of the five-byte CALL at `00547daa` establishes
`00547daf`; v2 fixes only that expected address and passes at
`language-bank-run-18wy3l8i`. V3 adds distinct alternate buffer objects to make
Stop ownership discriminating, with no original-byte change. Independent
read-only review reproduced the final saved results and this correction history.
Exact prompts and full reports remain in the existing private review owner.

### Original Load, Save and reload controls — September 20

`python -P local-data/test-runs/save-startup-20260919/load_roundtrip_control.py`
passed **15 cases** with 27 unchanged original bodies (6,236 bytes). Accepted stem
`local-data/test-runs/save-startup-20260919/load-roundtrip-run-a29vv1kx/load`;
receipt SHA-256 `5a89bc7561ebcb69baeac9f684311d139d79c39ce0f9bf8a003be4d2451a9c20`;
ELF SHA-256 `c3bdb6b3ba35bb1cce7b891c47b4b955c0c7c8b6f36e005cfae61c13faac6169`.
`load-roundtrip-controls-v2.log` records the accepted run.

The second native Load reads the first original serializer buffer directly.
Six selected snapshots, all supplied input bytes, both complete serializer
capacities/guards, integer ABI, x87 CW/TOP and **126 ordered observations** pass.
Both gold controls compare each native 10,004-byte output directly with the real
fixture, with/without career reinitialization. Named private derivatives cover
counter normalization, binding reinitialization/preset application, low-byte
Load flags and discriminating zero-to-one progress-flag writes. Setting only
the second SaveWithFlag changes exactly file byte `0x248a`.

The original career static initializer restores career volume words to `.8/.9`;
it is not Blank or a complete audio reset. Preserve-mode Load retains those
words and skips volume setters, leaving the prior audio-manager state. Original
reset/bank, allocation/free, diagnostics and latest-world remain hooks. Language
cache headers and audio objects are authored. Binding reinitialization is
compared with captured original-initializer output; this review did not rederive
every initial binding constant. These are not whole-memory, general malformed
input, real-device or full process-startup guarantees.

Each generated output is created privately, flushed/fsynced and reread with
Python. No original save is overwritten. This is Linux private-copy readback,
not retail-writer, Windows or crash-durability acceptance. The forbidden syscall
control terminates with SIGSYS; selected specimen and fixture remain unchanged.
Independent review reconstructed saved results without rerunning them.

The retained first run (`load-roundtrip-controls-v1.log`,
`load-roundtrip-run-6q_xyqop/load`) passed 12 cases. Its SaveWithFlag inputs already
had the progress flag set, so they did not discriminate the mutation; its full
save payload was checked but its preceding control header was not snapshotted.
V2 adds those checks, three zero-scalar cases and the corrected low-byte label.
No original body bytes changed. Both iterations remain private evidence.

### Original startup reset with Goodies — September 20

`python -P local-data/test-runs/save-startup-20260919/startup_goodies_control.py`
passed **17 cases**, with 53 unchanged original functions and the 36-byte episode
jump table. Their copied extents total 37,597 bytes: 37,586 inventoried body bytes
plus 11 preserved inter-range bytes around the existing `0055e2d0` CRT extent.
Accepted stem
`local-data/test-runs/save-startup-20260919/startup-goodies-run-0e30s139/startup`;
receipt SHA-256 `97bc4eb4bb6544e04735878cbb56d85623b9f74d44c109b3ef4a0e0fecea0f97`;
ELF SHA-256 `41e4493e7894a5807d8ba67e885989ed7ef661cdf18f74e7099f8ecab6dea57b`.
`startup-goodies-controls-v1.log` records the run. The retained original
`startup_control.py` remains unchanged, SHA-256
`557915d737c6b7e3ba55823d30960e7d7976f7e0f56ac416ad851b5bdc7a56a1`.

WinMain calls original Load/Blank; the final Goodie call now executes with
original descriptor initialization, grade/episode/index helpers and text scratch
conversion. Complete career comparisons include every Goodie: precisely slots
`0, 1, 8, 14, 33, 36, 41, 42, 43` finish at state one; all others and both badge
bookkeeping globals are zero. The valid, missing, short and invalid-version
cases retain their expected settings and untouched record storage. Original
Save/SaveWithFlag and default-options writer are separately invoked afterward;
that is not a claim that startup automatically saves settings. This separately
invoked writer receives the original input buffer, not the reset serialization.

Three selected snapshots include the full input, guarded descriptor table and
text scratch. Descriptor preservation and threshold 40 are checked; the original
initializer, rather than guessed zero BSS, supplies other descriptor values.
Scratch contents and guards match, except its final rotating index is checked
only within `0..3` (observed 3), not independently derived from a call count.
Positive-ranking CRT conversion traps unexpected entry; its absence is expected
for the reset graph. ABI, PC53-nearest CW/TOP, buffer capacities and the SIGSYS
negative control pass. Original inputs remain unchanged.

File/allocator/version/system services, graphics, audio and preset/language
actions remain intercepted. The experiment returns through the declared
graphics-create failure. It does not cover general unlock rules, malformed
graphs, alternate receivers, retail storage, real devices, visible startup or UI.
The byte-backed static dependency review and final instrument review are retained
with exact prompts and full reports in the existing private review owner.

### Original nonnull language cleanup — September 22

`python -P local-data/test-runs/save-startup-20260919/language_cleanup_control.py`
passed **26 cases**, retaining 16 complete single-range original bodies
(1,081 bytes). Accepted stem
`local-data/test-runs/save-startup-20260919/language-cleanup-run-f_nhvrni/cleanup`;
receipt SHA-256 `a971620046afeb991e507b2d43a4ffce4b033d3c3e4254323b06c16186a64b5a`;
ELF SHA-256 `90a56a903bea39990c8c20d743019a191f8832dc83ee6962f34a9b3cbd1a712b`.
`language-cleanup-controls-v3.log` records the run. The saved driver, assembler/
linker commands and complete input/output/stderr files retain the instrument.
The selected pristine executable remains SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Original Cleanup/SetLanguage, outer and nested menu/base/controller-item
destruction, pooled-list clear, resource decrement, monitored-base invalidation,
key-sink adapter/store and CText copy execute. The real constructor is excluded;
objects, references, resources, cache headers and buffers are authored. The
constructor/vtable ownership link is separately instruction-backed, not executed.

Cases cover null/empty/populated owners, optional child dispatch, repeated
cleanup, aliased/absent/zero-count resources, absent monitors, embedded-null
payloads/cells, a zero list count with live nodes, controller flag states,
deleting-wrapper bit admission and repeated/changed language selection. These
adverse states are explicit controls, not evidence that retail creates them.
Complete selected state is compared before/after calls and at **185 ordered
hook observations**, including the old active text throughout destruction and
the owner clearing before text-buffer free. Repeated language calls allocate
distinct buffers; their second cleanup sees null rather than recreating menus.

The key-sink word at `00889008`, its guards, the untouched `00888008` word,
complete input, unused output capacity and normal FS-chain restoration are
checked. Integer stack/register guards and PC53-nearest x87 CW/TOP pass. The
read/write/exit restriction rejects forbidden `getpid` with SIGSYS and no output.
Original specimen bytes are rechecked unchanged. No Windows exception dispatch,
whole-process memory preservation or actual input-device behavior is claimed.

The saved v1 failure at `language-cleanup-run-7x9im6kj/cleanup` watched the wrong
word: a private static review and oracle had misadded `00855bb0 + 33458` as
`00888008`. Fresh selected instructions establish `00889008`. V2 reran the
unchanged failing driver after an inspection helper used a string instead of
the Path required by PeImage. V3 corrects the captured/expected address, seeds
it nonzero and retains the previous word as an unchanged control. No original
instructions or expected final hash were substituted to force agreement.

Heap allocation/free and optional child virtual calls remain recording hooks
with their checked argument cleanup. The large constructor, other derived item
and actual optional child destructors, real memory reclamation, exception
unwinding, reentrancy, language-format admission, Load/Save composition and live
menu recreation/rendering remain outside this cohort. Exact reviewer prompts
and reports are retained in the existing private review owner.

### Original sample decode and quality conversion — September 22

`python -P local-data/test-runs/save-startup-20260919/audio_sample_control.py`
passed **44 cases**, retaining five complete single-range original bodies
(2,002 bytes). Accepted stem
`local-data/test-runs/save-startup-20260919/audio-sample-run-czk0ur1j/sample`;
receipt SHA-256 `1edefa0d58727cc6b9f4631ee1f8a233d0d9cbc1fefeb661a296e141e4116bd4`;
ELF SHA-256 `7755ab7a4c603414a20b071dbc2b389cd6982ad63fc43729aede410e7a0b377d`.
`audio-sample-controls-v2.log` records the invocation. The saved driver,
assembly/link commands, complete input/output/stderr and selected body/table
hashes preserve the instrument. The selected pristine executable remains
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Original sample loading, cached Read, buffer creation, ADPCM decoding and
quality conversion execute. Two complete real English-bank size/payload records
run at qualities 0, 1 and 2. Authored size residues, quality 3/negative quality,
fresh/reused objects, supplied Create/Lock/Unlock failures, zero/short reads,
short returned lock span and descriptor flag/GUID selection cover adverse paths.
The [contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#original-sample-decoding-and-saved-quality)
identifies the bank and separates its 164 framed records from the two decoded.

Complete selected state, the entire guarded allocation arena and unchanged input
are compared, with **310 ordered hook snapshots**. Device descriptor/format and
meaningful method arguments are checked; incidental stack-pointer values are
captured rather than modeled. Unused event capacity, integer ABI guards and
PC53-nearest x87 CW/TOP pass. The syscall restriction rejects `getpid` with
SIGSYS and no output. Executable and bank are rechecked unchanged.

The preserved v1 failure expected zero after the 16-byte PCM format prefix.
Original stack instructions place the 36-byte buffer descriptor immediately
after that prefix, so an 18-byte capture includes its size's low word `0x24`.
V2 corrects that observation boundary; it does not claim an initialized
`WAVEFORMATEX.cbSize` or alter retail instructions to obtain agreement.

One real 29,490-byte record requests/writes 14,745/14,746 bytes at quality 1
and 3,687/3,686 at quality 2. The full arena comparisons include the excess byte
and unchanged trailing byte. Heap/COM hooks retain oversized owned memory;
supplied failures and span lengths do not establish actual driver behavior,
real overflow/crashes, lifetime safety or audible results. Open/refill, complete
bank traversal, outer CreateSample/reuse lookup, allocation failure, malformed
huge lengths, exceptions, Load/Save composition and full startup remain outside
this experiment.

A separate `python -P -` read-only AST comparison selected only the current
materializer's two literal tables and pure decoder. The private
`audio-sample-materializer-comparison.json` records exact source hash
`710c3843f533af18e9b634ed40051da2ab1f1a6cb71fab0db716e13081566081`, selected lines
and output hashes. Both complete real quality-0 outputs match; an authored odd
size differs only at its final byte. The full materializer was not invoked or
edited. Review prompts, full reports and root dispositions remain in the existing
private save-loader/language review record. No Ghidra database was opened.

### Original sample admission and registration — September 22

`python -P local-data/test-runs/save-startup-20260919/audio_sample_control.py --outer`
passed **25 cases / 172 ordered hook snapshots**. Accepted stem
`local-data/test-runs/save-startup-20260919/audio-sample-outer-run-rmgj4y_q/sample`;
receipt SHA-256 `487ca48200e953807f5527b4bb9dc6e48679d2c3d99cded176c75b0748f722ae`;
ELF SHA-256 `b9ee0618c1cdc74b5283190b8d3d7ed79e9a48cf262b404326283900cec8fc86`.
`audio-sample-outer-controls-v2.log` retains the result. Nine complete original
bodies total 2,827 bytes; the new four are CreateSample, two CRT string helpers
and the null-stream stub. Specimen identity is unchanged from the preceding
sample cohort. The original 44-case receipt and saved driver remain immutable.

This mode executes only English-bank record 3. Cases cover fresh insertion,
case-insensitive head/second/duplicate selection, byte versus word reuse flags,
music-word preservation, null streams, name truncation, stored-name suffix
boundaries, create/lock failures, zero payload reads and composed quality-1
conversion. Complete selected state, arena, guards and input plus all ordered
snapshots are checked. Integer ABI, PC53-nearest CW/TOP, unused output capacity,
specimen/bank identity and the forbidden-syscall negative control pass.

Formatter/logger calls only record arguments and return; no formatted path
bytes are produced. The destination is unused by the tested compressed route
and original null-stream stub. The original ASCII-locale comparison/copy does
execute; other locales do not. Heap/COM/destruction hooks retain memory, so
sample reuse and insertion are not proof of actual device or object lifetime.
No bank traversal, real file access, audible behavior, Load/Save composition or
startup acceptance is claimed. The [contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#outer-sample-admission-and-registration)
distinguishes caller evidence from the separate Ghidra correction below.

The preserved v1 outer run passed but inherited two-record receipt wording
from direct mode and duplicated one case. V2 narrows the executed-record metadata
to record 3 and replaces that duplicate with reuse preserving music word 256.
The ELF is unchanged. Exact prompts and full independent reports stay in the
existing private review owner; these original-code experiments did not open or
modify a Ghidra project.

### Sample-loading Ghidra metadata — September 22

The [two-stage correction](reverse-engineering/ghidra/README.md#sample-loading-metadata--september-22)
passed fresh PRE equality against independent Archive A recovery, restored
read-only opening, isolated dry/apply/separate readbacks, sealed-spec readbacks,
independent exact comparison, live dry/apply/separate readbacks and independent
POST copy/restore/opening. Scope: two function names, four explicit parameter
names, four nonrepeatable comments and four tag sets. Every return/parameter
type, storage location, local, type definition, stack record and instruction is
preserved, along with all 8,327 non-target functions. Exactly four of 32,698
variable rows change their names. All nine live exports equal the reopened
rehearsal; only `commentsSha256` changes among program metrics.

The framework's former `arity * 4` rule could not represent the bank's existing
one-byte `char` parameter extent. A narrow exception requires the existing
dynamic types, convention, shape and extent to match; it does not widen the
parameter or change its four-byte stack purge. A focused API-proxy positive
and 16 negative variations execute this admission predicate. Actual saved
database comparisons establish storage preservation separately. Wrong-comment
and wrong-extent read-only controls also refuse with no attempted writes and
byte-identical project inventories.

Private owner:
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260919/audio-sample-loading/`.
The executed entry points were `prepare_preservation.py`, `prepare.py`,
`rehearse.py loading`, `rehearse.py parameters`, `negative_controls.py`,
`apply_live.py`, `compare_exports.py live-post` and `finish.py`, each invoked
with `python -P`. Exact headless commands and receipts are retained there.
`PYTHONPATH=. python -P tools/ghidra_cohort_framework_tests.py` passed **93 tests
without skips**, including after the reviewed live allowance. The name oracle,
documentation and public-payload checks passed. Review corrected the draft
stub coverage count to two cases and clarified name-copy padding before their
respective rehearsal applies. Final specs add only the derived live-applier
hash to the measured rehearsal pins. The tracked checkpoint is unchanged.

These metadata changes preserve the preceding 44 direct and 25 outer controls;
they do not execute successful whole-bank traversal, actual sample destruction,
real audio-device operations or a complete startup.

### Original sample destruction and failed loads — September 22

`python -P local-data/test-runs/save-startup-20260919/sample_destruction_control.py`
passed **23 cases / 112 ordered hook snapshots**. Accepted stem
`local-data/test-runs/save-startup-20260919/sample-destruction-run-1waarils/destruction`;
receipt SHA-256 `6105827101f7cba36147e6b60f75fb63c498ac4cb6644ac5bcfdd392f63e95fc`;
ELF SHA-256 `6c056ab660b46afbd538f23c43992f9b24dd917861cf692edaa1330f46620c01`.
`sample-destruction-controls-v2.log` records the result. Seven complete original
bodies total 615 bytes. The saved driver preserves the exact source used; the current
driver subsequently gained the composition mode below.

Cases cover deletion flags, all canonical list positions, matching/nonmatching
events, zero playing state, negative channels, strict notification flags,
null primary/secondary slots, owner-list removal and deliberately inconsistent
ownership. Independent review recomputed all final captured bytes and hook
snapshots from actual saved inputs. It caught four fixtures labeled singleton
that actually inherited a middle position. V2 explicitly supplies singleton
ownership: all four now clear the canonical head. The ELF/assembly are unchanged;
the other 19 inputs are identical, and their outputs differ only in captured
per-process FS addresses. V1 remains preserved, not counted as singleton evidence.

`python -P local-data/test-runs/save-startup-20260919/sample_destruction_control.py --load-failure`
then passed **11 cases / 84 ordered hook snapshots**. Accepted stem
`local-data/test-runs/save-startup-20260919/sample-load-failure-run-0gj_94uh/destruction`;
receipt SHA-256 `77bbc859158828ba198e2a8c3bbc09bedc8db99e96a52b27998835c059d61bc3`;
ELF SHA-256 `d4188bf8a6adb55a854aef8c17e9a0f9bfd32cb147e38282949731b972e9bdca`.
`sample-load-failure-controls-v3.log` records the result. Four additional complete
bodies retain 2,278 original bytes in total: CreateSample, ASCII name comparison,
the buffer loader and cached Read now reach the original destructor. Authored
headers declare 32 or zero decoded bytes, with no following payload. This is
failure-path composition, not successful bank loading or a decoded retail record.

The selected pristine specimen remains SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Both instruments check original bodies/data/BSS, nonoverlapping ELF segments,
full selected guarded state, unchanged input, ordered snapshots, unused output
storage, integer ABI, PC53-nearest CW/TOP and normal FS-chain restoration.
The forbidden-syscall control terminates with SIGSYS and empty output. Root
separately decoded failure outputs to check exact release counts, canonical
unlinking, fresh-case preservation and zero-size versus EOF error state.

The composed instrument's preserved v1 syntax failure executed no experiment.
V2 exposed an incorrect expected incidental ECX value at the loader's Release:
`005172da` loads its vtable into EDX, leaving the supplied heap hook's ECX intact.
V3 corrects that expectation from the instructions, without changing original
bytes. Formatter/logger hooks validate stable arguments; the formatter writes
no path bytes because this route does not consume them. Heap and COM storage
is retained, and owner callbacks only record. These checks do not establish
actual reclamation, device lifetime, callback side effects, exception dispatch,
successful bank traversal, file publication, playback or complete startup.
The [contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#original-sample-destruction-and-failed-loads)
records observed ordering and adverse-fixture limits. Exact review prompts,
reports and primary dispositions remain in the existing private review owner.
No Ghidra project was opened for these experiments.

### Original complete bank loading and reloads — September 22

`python -P local-data/test-runs/save-startup-20260919/audio_bank_control.py --all`
passed **11 cases / 184 sample attempts / 2,009 ordered hook snapshots**.
Accepted stem `local-data/test-runs/save-startup-20260919/audio-bank-run-6yqv9knl/bank`;
receipt SHA-256 `bfb45043109560269cca4385d05fd181ed05d1c92e06938be59563a412f3d71a`;
ELF SHA-256 `7e72a16b3d946ed632f7f5b14bb939201a84807e67836f1675be08c830cce533`.
The frozen driver, exact inputs/outputs and `audio-bank-controls-v5.log` retain
the executed work. Thirteen complete bodies total 4,709 unchanged original bytes
from pristine SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

The full English bank at quality zero exercises all 164 records and six actual
original-code refill requests. Ten bounded variants use private two-record
derivatives or complete empty headers: reuse on/off across two loads, qualities
one/two, altered tags with trailer, counts zero/negative, first-sample Create/Lock
failure and CloseHandle false. Full PCM destinations/guards, final object/global/
cache/scratch regions, complete samples at every progress event, file state,
resource ordering and all nine per-event cursor/counter/liveness words are checked.
The stack is owned initialized storage; integer ABI, normal SEH restoration and
x87 control/stack state pass. Raw final status `0x220` for the full bank is a
this-host observation, not a portable whole-status-register guarantee. The
forbidden-syscall control terminates with SIGSYS and empty output.

Independent read-only review parsed saved bytes without running/importing the
driver. Root separately checked admitted bodies, source and output identities,
every progress name/size/buffer/link/head, refill indices and consumed versus
prefetched lengths. A separate read-only AST extraction of the materializer's
two tables and pure decoder matches **all 164 PCM outputs / 21,537,072 bytes**;
source SHA-256 `710c3843f533af18e9b634ed40051da2ab1f1a6cb71fab0db716e13081566081`.
`audio-bank-materializer-comparison.json` records each comparison; it is not a
full materializer run or a lower-quality/playback validation.

Earlier attempts remain preserved. V1 failed assembly because `GS` collided
with a register name; no original code ran. V2 passed the first whole-bank
control but omitted the intended per-event I/O cursor capture. V3 corrected
that capture and strengthened checks, then exposed an incorrect x87 expectation:
the final `FSTP` rounds `163/164` upward to float32, setting C1 as well as precision.
V4 corrected the oracle from that instruction sequence. V5 replaces the skipped
intermediate reload comparison and checks exact release/publication order.
Its ELF and all 33 case input/output/stderr files equal V4 byte-for-byte.

Heap, filesystem imports, COM/device behavior, formatting and frontend progress
remain explicit supplied boundaries. The trailer is prefetched but not parsed;
CloseHandle false tests ignored return behavior, not actual closure. No Ghidra
project, original save or production implementation was changed. The
[contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#complete-original-bank-loading-and-reloads)
records reconstruction implications and remaining composition/playback limits.
Exact review prompts and reports remain in the existing private review owner.

### Original coupled settings and audio routing — September 23

`python -P local-data/test-runs/save-startup-20260919/load_audio_routing_control.py`
passed **nine cases / 105 ordered boundary snapshots**. Accepted stem
`local-data/test-runs/save-startup-20260919/load-audio-routing-run-k7s4slkl/load`;
receipt SHA-256 `cf4e5f977337b48c6708092c16f3bd1f70b6d0a554b25090155f917656f9ef3c`;
ELF SHA-256 `32f3706cf90767612102048337a6e8cc07c2eb407353488d44e772cc737dc859`.
The frozen driver and `load-audio-routing-controls-v2.log` retain this run.
Thirty-seven complete original bodies total 7,257 bytes; the language-name
getter also uses its original 20-byte jump table. Pristine and unchanged gold
identities remain those recorded above.

Cases vary prior language/path, each of four audio comparison words, both
preservation flags and supplied Init success/failure. All use the same real
fixture. Eight full-settings cases preserve all 10,004 bytes in both original
serializer outputs. The ninth preserves live settings and checks their complete
expected serialization. Six complete selected-state snapshots, source/serializer
guards, all recorded paths, bank arguments/return sites, integer ABI, owned stack
and x87 control/TOP pass. The forbidden-syscall control terminates with SIGSYS.

Root independently compares original bodies/data/zero BSS, nonoverlapping ELF
regions and the read-only jump table against the pristine file. Saved-output
readback checks all source/control bytes, complete serializers and guards,
immutable music vtable and all 44 CLI-tail bytes at every observation phase.
Full review and root readback remain private. The retained v1 failure caught
Python/assembler escaping removing the authored path separators; v2 uses numeric
string bytes and verifies their exact loaded representation. Retail bytes are
unchanged.

This composition executes reset/shutdown and language-path construction, with
actual bank loading at a **recording boundary**; it is not the preceding full-bank
experiment embedded into Load. Device Init supplies status without state effects;
its failure leaves the authored initialized flag set, admitting the later refresh.
That case does not establish real device failure recovery.
The formatter produces only the admitted bank-path template; heap, music-platform
shutdown, diagnostics and latest-world remain supplied boundaries. No actual file
Open, device normalization, playback or cold-start reachability is established.
The [contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#coupled-language-and-audio-settings-routing)
records the stale-path result, second-load correction and serialization limits.

### Original audio-device initialization — September 23

`python -P local-data/test-runs/save-startup-20260919/audio_device_init_control.py`
passed **29 cases / 3,213 ordered observations** in
`local-data/test-runs/save-startup-20260919/audio-device-init-run-6_s044v6/init`.
Receipt SHA-256 `5730c451811c14b1d7e5ac18f4de80435d0751328088dea1cdd9d669f2a720f9`;
ELF SHA-256 `2d7e3083761c5a856cc0d4ce49221a030fd4cbdae63726e9463e83f329ac2d56`.
The frozen driver SHA-256 is
`dd8a21137262a162074829051063f21b798e21afe04d1904b723507740a7ccec`;
`audio-device-init-controls-v1.log` retains the command outcome.

Nine complete original bodies total 2,412 bytes, including Init, actual callback,
wrapper construction/destruction and description conversion/copy. The loaded
bodies/data/zero BSS match the pinned pristine specimen. Each case compares two
complete 39,300-byte selected-state snapshots, intact input, immutable vtables,
ordered consequential boundary calls, manager/CLI/wrapper state, GUID/capability/
descriptor/format payloads and exact stack-relative output locations. The owned
initialized stack, integer ABI, FS-chain restoration and x87 control/status pass.
The forbidden-syscall negative control terminates with SIGSYS and empty output.

Cases include every main failure stage, positive HRESULTs, null allocation,
existing-wrapper early return, filtered enumeration, eleven callbacks versus ten
records, returned enumeration failure, index boundaries, all format branches,
automatic/explicit method/count values, high-bit count arithmetic, and bounded
high-byte/49/50-byte descriptions. Supplied failures normally write null output;
the second QueryInterface failure deliberately leaves its prior output unchanged.
The existing-wrapper case retains an authored table-count sentinel; the receipt's
`admittedDevices` field there is **not an enumeration count**.

Root independently reads the saved bytes without importing/running the driver;
`root-output-review.json` records original-byte identity, index/GUID selection,
unchanged settings and manager regions, exact format requests and selected failure
results. Independent read-only reviews also reconstructed every selected-state
byte and all 3,213 event positions; full prompts/reports remain in the existing
private review owner. Acquisition counters describe this invocation's resources,
excluding pre-existing authored pointers. These are isolated original-code controls with supplied heap, API, COM,
logger and narrow hex formatter behavior. No real device, playback, save Load/Save
composition, empty-description localization or complete startup acceptance is
established. The [contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#original-audio-device-initialization)
records the reconstruction implications and remaining boundaries.

### Original outer sound-manager initialization — September 23

`python -P local-data/test-runs/save-startup-20260919/audio_manager_init_control.py`
passed **10 cases / 3,595 observations**; the accepted frozen owner is
`local-data/test-runs/save-startup-20260919/audio-manager-init-run-3gzsvdhh/init`.
Receipt SHA-256 `b076063fe41d4d232f1a5e2faa732eeabbc68ba464c36801c12cb51fe421cfa0`;
ELF SHA-256 `fb9b1d9edf9cf75fcece6ebc5a7cac954c6efa9190acb535afd22a467fd38f34`;
driver SHA-256 `d836eabc774d830862342da5d2001ae8d064229dd0a7b047f998bd055f507a73`.
The command log is `audio-manager-init-controls-v2.log` in the parent owner.

Seventeen complete bodies total **4,148 original bytes**. Two 84,804-byte selected
snapshots per case cover the guarded pool/menu/console objects, manager/device
state, master volume, timer/baseline, registry, locale and excluded effect-list
region. Ordered events check original receiver/stack conventions, all 256 pool
allocations, before-call manager state and timer output-pointer locations.
The fixture verifies normal-return integer ABI, stack guards, FS restoration,
the x87 control word and permitted status bits. The forbidden-syscall control
terminates with SIGSYS and empty output. Actual APIs are intercepted.

Cases cover successful setup, failed device creation, empty device enumeration,
existing and null wrappers, pre-existing registry/uppercase console entries,
first and established performance-counter baselines, zero API return status
with supplied counter output, and unsigned millisecond fallback. Pool/menu/
console allocations succeed by construction. The SFX parser is excluded at its
exact call boundary; effect-list state is unchanged, not populated successfully.

Root readback independently checks body/data identity, all outer object bytes
and guards, registration links/fields, initialized high bytes, sampled values,
event ordering and snapshot pins without running/importing the driver.
`init.root-readback.json` records it. All 30 input/output/stderr artifacts equal
the preserved first run; the second version replaces unused excluded-locale
traps with their verified targets and adds pointer/logger assertions. Neither
version alters original instructions. Full read-only review reports remain in
the existing private review owner. No real clock/device, SFX parser, Load/Save
composition, full WinMain/shell execution or player acceptance is established.
See the [contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#original-outer-sound-manager-initialization).

### Original device effects during Load and Save — September 23

`python -P local-data/test-runs/save-startup-20260919/load_device_composition_control.py`
passed **8 cases / 89 routing and 358 device observations** under
`local-data/test-runs/save-startup-20260919/load-device-composition-run-klssepgg/load`.
Receipt SHA-256 `9de4fbccc9c0f879bf7ab843b74a416264de922fccfa021ba55b665ff00e65de`;
ELF SHA-256 `537b86bf6ac0d40d6399020f62e2f73c6648aa6888a9055fcf369a02789eb3f6`;
frozen driver SHA-256 `ebad6f2bf11401e94d3e3c9e38feb8a2978524df018af70e9028faac3bf079af`.
The parent owner retains `load-device-composition-controls-v2.log`.

The ELF combines **46 complete original bodies / 9,669 bytes** and the original
20-byte language table. Six complete 80,392-byte selected snapshots per case,
both 10,004-byte serializer outputs and their full capacities/guards are checked.
The second Load reads the first native serializer buffer directly. Five inputs
are unchanged gold; three alter only the declared device-index field. Every
case preserves its original input and supplied platform data. ABI/stack/FS and
x87 checks pass, as does the SIGSYS forbidden-syscall control. Generated output
copies are created exclusively, fsynced and reread; this is Linux evidence for
those files, not retail save-file durability.

The first preserved prototype returned normally and matched its predicted full
state, then failed an overly broad cached-path assertion. Its 64-byte capture
contains the 52-byte path plus method/device/first-slot fields changed by Init.
The accepted assertion predicts those adjacent fields separately and still
checks all 64 bytes. ELF, first input and first output are unchanged. Root's
separate `load.root-readback.json` checks source identities, all serializers,
unknown-byte preservation, device pointers, flags and stage-specific requests
without importing or executing the candidate. Independent read-only reviews
remain in the existing review owner.

Original outer startup and final bank parsing are excluded. Initialized state
is authored; platform, heap, diagnostics and the final bank request are supplied
boundaries. A failed device's later bank request does not establish usable audio
or safe recovery. The [contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#original-device-effects-during-load-and-save)
separates saved preferences, live device state and pending downstream behavior.

### Original bank null-device controls — September 23

Four local GDB variants reuse the byte-identical original bank ELF
`local-data/test-runs/save-startup-20260919/audio-bank-run-6yqv9knl/bank`
(SHA-256 `7e72a16b3d946ed632f7f5b14bb939201a84807e67836f1675be08c830cce533`).
Their commands, scripts, logs and native outputs are under
`local-data/test-runs/save-startup-20260919/audio-bank-null-device-run-pkoygbwh/`;
`result.json` SHA-256 is
`937adf970408fb171119c8c3de991acde07c5608b61d3fcefe928abc81ef14fe`.
Each recorded command is `gdb -q -nx -nh -batch -x <owned-case.gdb>`; automatic
loading, debuginfod and history writes are disabled. Core dumps remain disabled
and the original fixture's syscall filter remains installed.

The breakpoint is in owned wrapper code immediately before the bank call,
after its initial snapshot. GDB changes only four declared process-state fields:
main device, initialized byte, listener and wrapper. With two real retained bank
records and a supplied valid device, execution completes two samples/buffers.
With a null device, initialized bytes one and zero both stop at original
`00517595` with EAX zero/SIGSEGV, before COM dispatch. A valid zero-count input
with a null device completes without samples. Debugger exit terminates its own
stopped inferior; the recorded stopped PIDs were subsequently absent.

Root compares **6,675,024 bytes** of the two successful outputs with retained
parent outputs: only the nine/twelve declared final-snapshot bytes differ. All
PCM, event and guard bytes match. The initial snapshot predates debugger writes
and remains identical. `result.root-readback.json` records that comparison;
independent read-only inspection checks all thirteen original body pins and
the four debugger captures. The ELF and original inputs remain unchanged.

These are isolated original-instruction observations with supplied file/heap/COM
dependencies. They are separate from the composed Load experiment, and establish
neither real Windows/Proton failure nor full startup reachability. The
[contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#bank-loading-with-a-missing-device)
distinguishes null-interface dereference from a returned method failure.

### Level 100 turret targeting control — September 25

`python -P local-data/test-runs/level100-final-wave-20260925/turret_targeting_control.py`
passed **16 cases** under `local-data/test-runs/level100-final-wave-20260925/turret-run-1s9s58nr/`.
Receipt SHA-256 `6ff66c70ab7b0886163d5038e6e8cfd55eca4b0e574c43bea400195311b1602a`;
ELF SHA-256 `7a6117d690170766e17e82dac1088ecd94871222c5abceadb0ace22743ebada3`;
driver copy SHA-256 `133230c6914bc33d91115db29a9c3d409ee4f64ab2cd86cecf17941f5a47a1bc`.

The ELF places ten unchanged pristine bodies and seven `.rdata` scalars at their
retail addresses: script `SetAllegiance`, `SetFactionForHierarchy`, CSPtrSet
add-to-head/add-to-tail/remove, the close-target scan `0x004ff710`, its state and
side gates, `SetReader` and monitor registration. Feasibility A/B, capability,
support and support-band helpers are recording stubs; objects, the node free list
and the three world lists are synthetic. Every case checks callee-saved registers,
stack, FS:0 and the x87 control word, and the full list contents, counts and tails.

A squad-less unit switched from 0 to 1 moves from `0x008550b0` to `0x008550c0`; a
squad member is not relisted; allegiance 6 joins both lists and 2 neither; a
non-unit receiver is ignored; a child component follows its parent. An
allegiance-0 owner selects an allegiance-1 drone from `0x008550c0`, cannot see one
left in `0x008550b0`, rejects a stale allegiance-0 entry at the side gate, and
applies the strict range and dying gates; the nearer of two drones wins; a false
B keeps the reader and zeroes A. The composed Level 100 order (spawned friendly,
script ENEMY, then turret scan) selects the drone; a squad-wrapped drone stays
invisible. The first run failed on a harness defect, not a retail result: its
`fnstenv` overwrote the first trace slot and its predicted call list omitted the
capability stub. Both were corrected before the passing run.

This measures the list, allegiance and selection transaction with supplied
helper results. It establishes no turret aim, weapon, geometry, spawner or retail
gameplay behavior; the [contract](reverse-engineering/game-mechanics/level100-final-drone-wave.md)
keeps those open.

### Level 100 turret fire-control control — September 25

`python -P local-data/test-runs/level100-final-wave-20260925/turret_fire_control_control.py`
passed **21 cases** under `local-data/test-runs/level100-final-wave-20260925/fire-control-run-ob8ydblf/`.
Receipt SHA-256 `4efecff6d05e6a33a408fff564688ab96b21d245d58fc09e3596bc104245efe2`;
ELF SHA-256 `0a6ff38de4811e088cd116327ea89b9174c0582b4e3f441cf43592f2a2178683`;
driver copy SHA-256 `6382a81107b62a7fa890a190650f651cd88179a72380207db1f88000346bad95`.

The ELF places the unchanged `CUnit::Init` inspection range `[0x004f889a,0x004f89fb)`
and its nine-entry jump table, the emitter lookup `0x004aa820`, CRT `stricmp`,
`_strnicmp` and `_strncmp`, the fire-control refresh `0x004fb280`,
`Random__NextLCGAbs`, the shipped name strings and seven constants at their retail
addresses. Part and emitter structures come from the three shipped turret meshes
(hashes in the [contract](reverse-engineering/game-mechanics/level100-final-drone-wave.md#fire-control-control))
through the repository CMSH parser. The C-locale fast path is supplied and the
locale-lock path is trapped; the Euler constructor and `AddEvent_AtTime` are
recording stubs and the ballistic solver is a trap. Every case checks stack,
FS:0 and the x87 control word; refresh cases also check callee-saved registers.

All three meshes set `+0x224`, the barrel pointer and the rest angle; Blaster and
Pulse also set the weapon turret flag, SAT does not. Zero turn rate, a missing
emitter or selector, the Pulse `GunB` chain, a capitalised `Barrel`, and a
capitalised `Turret` behave as the byte reading predicts; an `x1 barrel` prefix and
a linked second mesh are found. Each enabled refresh takes one draw and queues
4001 at time + low16 × 0.1/65536 whether the owner is active or not; disabled and
dying owners do neither; both angle clamps hold; two refreshes match an exact int32
model of the generator. The first run (`fire-control-run-5gchgdb9/`) failed only in
that model, which lacked 32-bit wraparound for a deliberately out-of-range seed.

This corrects the World 110 owner's Turret 03 statement. It establishes the
inspection and refresh transactions only, not turret aiming, firing, rendering or
retail gameplay.

### Launch-angle Euler constructors control — September 25

`python -P local-data/test-runs/player-launch-20260925/euler_constructors_control.py`
ran **36 cases** under `local-data/test-runs/player-launch-20260925/euler-run-9ks6dz5x/`.
Receipt SHA-256 `39dbcff3f0f68ac810e39b66df3c5cee86ac78b4585cd1fa741d1e63f7dfbe59`;
ELF SHA-256 `be7485fd4de1f9f7286061afbee26e0ea38feffe0c09501e8118525a693ea328`;
driver copy SHA-256 `bc9f9b98520a397286bb3610a37d8b92a628fed786558ff2073285b1c68fa75a`.

The ELF places the unchanged integer-angle constructor `0x004f8140` with its callees
`0x00401ec0`, `0x00401f10` and `0x0040d320`, the float constructor `0x004062d0`, and
the constant at `0x005dfb6c` at their retail addresses. Each case checks stack and
callee-saved registers. Under control words `0x027f` and `0x007f`, every tested
`0x004f8140(a, b, c)` equals `0x004062d0(a·t, b·t, c·t)` with t = float(2π/4096)
except for signed zero words, and the integer version leaves each row's fourth
word unwritten. So the burst spawner's default launch matrix `0x004f8140(0, 1, 0)`
is a 2π/4096 pitch; see the
[burst contract](reverse-engineering/contracts/render-platform/ProjectileBurst__SpawnFromCurrentPreset__005069f0.md).
This measures the two constructors only, not the spawner or a retail run.

### Scheduled-event constructor boundary — September 19

The [one-function boundary correction](reverse-engineering/ghidra/README.md#scheduled-event-constructor-boundary-2026-09-19)
passed fresh PRE equality/restore-open, isolated dry/apply, separate readback,
independent comparison, live dry/apply/separate readback, and independent
Archive A POST restore-open. Both actual-database negative controls rejected
their inputs before writes: wrong body hash and a clipped final return.
The replica remained byte-identical after both refusals. All nine live
exports equal rehearsal; all 8,330 prior functions, 32,697 prior variables,
types, bookmarks and prior stack records are unchanged. The sole addition is
the default 64-byte, 15-instruction function at `0044b190`, with its default
return and unknown-purge stack records. Only the function-count metric moves.

`python -m tools.ghidra_cohort_framework_tests` passed **92 tests**.
The initial direct-file invocation could not import the repository package;
the module invocation is the executed passing command. The base applier is
unchanged; the derived live applier admits only the additional declared cohort.
`python tools/re_function_doc_names_check.py --self-test` passed after the
current-name projection gained the new default function. Frozen tables stay
unchanged. These checks establish the bounded correction, not a recovered
semantic prototype or retail runtime behavior.

Private owner:
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260919/event-constructor-boundary/`.
`*.command.json` records the actual headless arguments; corresponding logs
and receipts preserve outcomes. `compare_exports.py rehearsal-post` and
`compare_exports.py live-post` independently check the full exported records.
The first comparison stopped at the added default return record; inspection
confirmed its meaning and the final comparison admits exactly that new
record while preserving all existing variables. `live-readback.json` and
`post-restore.json` identities are recorded in the Ghidra owner above.

### Shared math-error Ghidra correction — September 19

The [one-function correction](reverse-engineering/ghidra/README.md#shared-math-error-abi-correction-2026-09-19)
replaces `00561547`'s fabricated hidden-pointer/fastcall description with six
explicit register/x87/stack inputs and a `float10` ST0 return. It changes only
the prototype, nonrepeatable comment and tags. The binary64 spill/reload and
conditional control-word restore remain explicit in the comment; this is a
physical ABI model, not a recovered C declaration.

`python -m unittest tools.ghidra_cohort_framework_tests -v` passed **92 tests**.
The optional custom-storage route adds exact PRE/POST ABI pins, parameter
name/storage conflict checks with `force=false`, and a protected census of
program bytes, all locals, unrelated internal/external ABIs and datatype
definitions/settings. The historical dynamic-storage census is unchanged.
Independent opens exposed the built-in `ImageBaseOffset32` type's process-local
ID; pinned Ghidra source and a complete field comparison justified excluding
built-in IDs, while persistent type and source-archive identities remain bound.

Ten actual-Ghidra negative controls refused before writes: conflicting local
names/storage, target/unrelated local comments, same-rendered input-register,
stack-offset and return-register changes, incomplete bindings, width mismatch,
and overlapping inputs. Three additional database-backed controls detect enum,
function-definition and argument comments that the rendered definitions omit.
All control projects were opened read-only and retained identical project bytes.

Fresh isolated dry/apply/separate readback and the sealed repetition passed;
the live dry/apply/separate readback produced identical full exports. Only
one of 8,330 function rows changed; all 8,329 other rows and every local
variable remain identical. Removing the invented parameter reduces variable
records from 32,697 to 32,696. Types, bookmarks, saved stack details, Plane-depth
and all target instructions are unchanged; only `commentsSha256` moves among
29 program metrics. Independent review also reconciled all 8,965 protected
census entries. The scoped source correction does not validate the real CRT
dispatcher, exceptional inputs, Windows behavior or gameplay.

Commands, exact manifests, logs, full comparisons and PRE/POST recovery receipts
belong to
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260919/math-error-abi/promotion/`.
The Ghidra correction record above owns the live-readback and recovery identities;
no tracked-checkpoint refresh is included.

### Asin-helper Ghidra correction — September 19

The two-function [correction record](reverse-engineering/ghidra/README.md#asin-helper-metadata-correction-2026-09-19)
owns the exact manifest/spec and working/recovery identities. Fresh exports
matched 194 pristine bytes across 54 instructions. The final rehearsal and
independent full comparison changed only names, nonrepeatable comments and tag
sets at two entries; all prototypes, 32,697 variable records, 8,328 non-target
function rows and program structure remain unchanged. Only the program comment
digest moves. All nine live exports match the separately reopened rehearsal.

The existing framework passed isolated dry/apply, stale-second-comment refusal
before writes, sealed readback, live dry/apply/separate readback, and independent
Archive A POST restore/read-only reopen. The refusal control used the initial
draft with the same PRE guards; final wording was rehearsed on a fresh PRE copy.
`python -m tools.ghidra_cohort_framework_tests` passed **91 tests**. Direct script
invocation first failed to resolve the existing `tools` package; module invocation
passed without a framework behavior change. The only live-applier change is the
exact new cohort grant. Private commands, logs and comparison records are under
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260919/asin-helper-semantics/`.

The tracked checkpoint is unchanged. Implicit x87 inputs, the shared error helper's
signature and alternate-entry ownership remain separate open work; the corrected
names do not certify those prototypes or live gameplay.

### Aim-provider Ghidra correction — September 19

The four-function [correction record](reverse-engineering/ghidra/README.md#aim-provider-metadata-correction-2026-09-19)
owns the immutable manifest/spec and measured working/recovery identities.
Fresh body exports matched all 731 pristine bytes, covering 239 instructions.
Independent read-only review checked the semantic corrections and compared all
8,330 internal function rows and 32,697 variable records. Exactly four function
metadata rows and two return-type/storage records changed; every formal
parameter/local and all non-target rows stayed unchanged. The only program
metric change was `commentsSha256`; types/bookmarks/stack/Plane-depth held.

The existing framework ran read-only dry, isolated apply, separate readback,
stale-PRE refusal, sealed readback, live dry/apply/separate readback and independent
POST restore/reopen. All nine live exports equal the reviewed rehearsal. The
stale-PRE control reports failure with `writesAttempted=false`; headless exit zero
alone was not treated as success. Framework checks passed **91 tests** with
`python -m tools.ghidra_cohort_framework_tests`; the live twin differs only by the
new exact cohort grant. Current-name projection and public-safety self-tests
also passed. Raw commands, logs, manifests, comparisons and restore receipts are
under `local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260919/aim-provider-semantics/`.

The tracked checkpoint payload remains byte-identical. Neither the metadata
correction nor the isolated endpoint experiment above establishes actual segment
poses, live combat or reconstruction acceptance.

### UnitAI exit comment correction — September 12

The exact one-comment manifest passed the preserved rehearsal/live/readback/
independent-recovery route in [Ghidra's owner](reverse-engineering/ghidra/README.md#unitai-exit-contract-comment-2026-09-12).
Only `004ffbb0`'s nonrepeatable comment changes; all eight live exports equal
the isolated rehearsal. The tracked checkpoint remains unchanged.
`python -m tools.ghidra_cohort_framework_tests` passed **91/91**.
The direct script invocation first failed to import `tools`; module invocation
uses the existing package without changing the framework's behavior.
The cohort receipts and exact commands are under
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260912/unit-ai-exit-contract/`.
No engine/runtime acceptance was inferred from these metadata and RE checks.
The first payload gate refused the new encoded-comment manifest. Its two
decoded analytic comments (3,509 bytes) passed control/secret/payload inspection;
only that exact manifest path and SHA-256 were registered through the existing
reviewed-comment mechanism. Other payload guards remain active. Final docs and
safety receipts are `plane-common-exit-docs-final-20260912.log` and
`plane-common-exit-safety-final-20260912.log` in the test-run owner above.

### Unit weapon preparation and fire phases — September 12

`python local-data/test-runs/linux-route-20260906-af1sa_l9/weapon-phases-20260912.py`
passed **26 synthetic cases / 32 calls**. Seven unchanged routine bodies and
one constant execute at their original addresses, checked through actual ELF
load mappings against the pristine specimen. The `.inputs.bin`, `.outputs.bin`
and `.results.json` remain private beside the script. Every case checks return
values where meaningful, phase/deadline/request/prepared words, call counts,
balanced x87 stack/control word, and that no other input bytes changed.

Cases distinguish strict reload readiness, zero/positive/negative preparation
delay, phase-1 completion at equality versus phase-2 completion after equality,
fire refusal clearing flags, and accepted Unit fire despite zero/negative
Weapon Fire returns. A canceled phase-1 case confirms that the outer completion
clears the phase after the real post callback set phase 2, retaining its deadline.
Independent read-only review checked all retained cases, ELF mappings, stubs
and instruction ordering; the reviewer did not rerun the executable.

Inputs use a current-mode weapon, empty spawner list, no deploy prerequisite
and no preparation/post effects. Weapon Fire and waiting animation are stubs;
the post callback and its empty-effect helper execute original code. These
checks establish no projectile, effects, phase-3 pose restoration, player route
or combat acceptance. No desktop control or C# runtime change was involved.

### Aircraft spawner exit inputs — September 12

All output below uses the existing private owner
`local-data/test-runs/linux-route-20260906-af1sa_l9/`.
The unchanged-code scripts `plane-controller-init-20260912.py` and
`plane-controller-exit-20260912.py` passed **18** and **26** synthetic cases.
Their original bodies/constants were checked in ELF load mappings; the first
executes the native SEH chain push/pop against private FS memory, and the
second executes the real state-1 transition helper. Full synthetic receiver
bytes, ABI, call order and event arguments are checked. The separate
`plane-controller-scheduling-20260912.py` passed **18** cases, extending the
retained eleven-case probe with supplied common-return, dying-owner,
missing-target and event-reuse controls. Inputs, outputs and JSON results remain
beside each script. Read-only reviewers checked the code and retained records;
they did not rerun them. Scene/reader/terrain/RNG/AddEvent stubs do not establish
actual event delivery, total transitive randomness or a completed exit.

Actual static-world materialization regenerated **66 outputs** in
`local-lab/rebuild-godot/airfield-exit-20260912-y8_etv9r/`.
Only `level100-static-world.json` changed: four Airfield spawn rows gained
`spawnerExitWaypoints`. Its 165,541 bytes exactly match a separately composed
expected document; deleting just those four added fields recovers the old
document. The other 65 outputs are byte-identical. PRE, expected, regeneration
log and publication receipt are `airfield-exit-manifest-{pre,expected}-20260912.json`
and `airfield-exit-materialize-20260912.{log,results.json}`. The new manifest hash
is `52a17547c8a91a8bae9abe3df291c02ba1a106bbf39e10c71642a0f32fd34879`.
The first extraction attempt refused missing CORI on the waypoint parts;
native cache-owner inspection then established their declared root inheritance.
No default orientation or launch transform was substituted.

`npm run prepare:rebuild-assets` accepted **389 exact files** after publication
(`airfield-exit-assets-ready-20260912.log`).
`python -m unittest materialize_retail_assets_tests`, from `rebuild/tools`,
passed **82/82**, with no skips (`airfield-exit-materializer-final-20260912.log`).
The selected Core run uses `dotnet test` with `--no-restore --nologo`, the Core
test project and filter
`FullyQualifiedName~Level100RawPlaneCreationTests|FullyQualifiedName~Level100ActorRegistryTests|FullyQualifiedName~Level100ActorPlaneRuntimeTests|FullyQualifiedName~SimulationTests|FullyQualifiedName~RetailMeshPartPoseTests|FullyQualifiedName~Level100ActorScriptRuntimeTests`.
It passed **113/113**, no skips; exact results and logs are
`airfield-exit-core-final-20260912.{trx,log}`. Coverage includes exit selectors,
independently calculated A/B pose words, input ownership, restore rejection,
legacy missing-input distinction, raw Plane creation and existing script flow.
The calculated pose cases are not retail observations.

The initial Core run passed 27 cases and failed its old canonical-hash pin.
The cause check then restored only the old definition identity and compared
**every canonical byte** with a forty-step run lacking the new exit inputs;
that comparison and the old `f121a469…` fingerprint passed before the deliberately
unchanged final pin failed. The final test retains those assertions and pins
`5a71982008e1a30f1684030e562fd45580cde149a3bcd3c3a4649201d4bb2750`.
Initial/cause results remain `airfield-exit-core-20260912.{trx,log}` and
`airfield-exit-hash-cause-20260912.{trx,log}`. Definition format 7 binds exit
selectors/model words; sets with no recovered exit inputs retain format 6.
No gameplay constant, scheduled aircraft behavior or combat assertion changed.

The complete Client suite then passed **907**, with its two existing capture
skips and no failures (`airfield-exit-client-complete-20260912.{trx,log}`).
It used `dotnet test rebuild/OnslaughtRebuild.Client.Tests/OnslaughtRebuild.Client.Tests.csproj`
with `--no-restore --nologo`, the same results directory and no filter.
The first run had 906 passes and one old First Flight hash failure
(`airfield-exit-client-20260912.{trx,log}`). The corrected test runs the complete
2,148-step input route with and without the exit definitions and recovers the
old `107e827d…` hash by changing only the definition identity. All route
assertions remain required; the new pin is
`2f5f634f8b785a304508fc39bba8f373148fc1292ec67271a1a21888a60d65de`.
A test-only intermediate compile failure attempted to call Core's internal
canonical-byte helper from Client tests; the final comparison uses the public
state hash, without widening that API (`airfield-exit-client-final-20260912.log`).
The Core test above retains its direct complete-byte comparison.

`git diff --check`, `npm run test:docs` and `npm run test:safety` passed;
the safety gate checked **3,980 candidates**. Their logs use
`airfield-exit-docs-20260912.log` and `airfield-exit-safety-20260912.log`.
These are in-process reconstruction checks, not native Godot, retail runtime,
full-combat or desktop acceptance.

### UnitAI initializer and event arguments — September 12

The `unit-ai-initializer` and `unit-ai-event-arguments` cohorts passed exact
pristine body/RTTI/comment review, isolated dry/apply, separate full readback,
sealed POST checks, live dry/apply and separate live readback. Commands and
results are in their respective children under
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260912/`.
Each `*.command.json` records the actual argv; `rehearsal-comparison.json`
records the independent full comparison, and `live-comparison.json` confirms
all eight live exports equal rehearsal. The first initializer dry run refused
unprefixed addresses before any writes; its corrected run passed. No guard
was weakened to admit that input.

The initializer changes one name/display signature, nonrepeatable comment and
tag membership; 8,329 other rows and all ABI/variable/stack metadata remain
unchanged. The event cohort changes two function signatures/comments and only
two explicit parameter rows: dispatcher name/type and exit parameter name.
Its other 8,328 function rows, parameter storage/source, automatic receivers,
provisional returns, saved stack/frame fields, types and bookmarks are preserved.
Program metrics change only the comment digest in each cohort.

The exact source project was byte-matched to the preceding independent POST
before each apply. Both new Archive A POST copies were copied, hash-compared,
restored elsewhere and opened read-only successfully. Each owner retains
`source-{pre,post}.json`, `tracked-pre.json` and `post-working-restore.json`.
The initializer's fresh PRE restore is `pre-working-restore.json`; its restored
POST then supplies the second cohort's PRE. The reviewed tracked checkpoint
was freshly compared and remained unchanged.

`python -m unittest tools.ghidra_cohort_framework_tests` passed **91/91**, no
skips (`local-data/test-runs/linux-route-20260906-af1sa_l9/unit-ai-framework-final-20260912.log`).
An intermediate run found two derivation failures because direct-script module
resolution had prevented emitting the live twin; module invocation corrected
the invocation, and the final diff adds only the two cohort IDs to that twin.
The initial result remains `unit-ai-framework-20260912.log`. The new comment
manifests contain six reviewed analytic comments, **5,762 decoded bytes**;
all pass the existing content/secret guards, and only their exact file hashes
are registered. No retail payload or database copy was added to Git.

The name-checker self-test, documentation gate and `git diff --check` passed.
All **8,330** current projected names also match the final live function export
(`unit-ai-event-arguments/current-name-comparison.json`). The initial docs gate
found a missing source-provenance header in the edited ThunderHead note; the
note now has its complete header, a fresh bounded caller inspection and no
unsupported Warspite-specific pseudocode. The header backlog shrank by one.
The public safety check passed for **3,984 candidates**. Gate logs in the same
test owner are `unit-ai-name-selftest-20260912.log`,
`unit-ai-docs-{,final-}20260912.log` and `unit-ai-safety-20260912.log`.
These checks establish the declared metadata corrections and preservation,
not full semantic audit or runtime acceptance.

### Aircraft exit lifecycle integration — September 12

Outputs below remain in `local-data/test-runs/linux-route-20260906-af1sa_l9/`.
`python local-data/test-runs/linux-route-20260906-af1sa_l9/plane-controller-exit-goto-20260912.py`
passed **26/26** synthetic cases with unchanged exit, transition, AirUnit GoTo
and Guide GoTo bodies at their retail addresses. The input executable was
verified as 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The script, native ELF, inputs, outputs and `.results.json` retain body/constant
load-map checks, all controller words, ABI and x87 state. Separate CST/guide
receivers distinguish collision-ignore clearing from unchanged guide state;
the real GoTo adds its second altitude clamp after the exit arrival comparison.
Terrain, scene queries, vulnerability, StartDying, RNG and event admission are
stubs. The reviewer inspected the code and recorded results without rerunning
them. This is original-code experiment evidence, not a live game observation.

`plane-exit-static-boundaries-20260912.log` records bounded pristine disassembly
of the death path, vulnerability getter, collision-ignore write and MinAltitude
default/field setter. It also records the freshly verified physics input and
all 25 hash-pinned Level100 script objects: 1,925 instructions, no native-32
SetVulnerable call. The [Unit evidence](reverse-engineering/binary-analysis/functions/CComplexThing.cpp.md#aircraft-spawner-exit-and-script-readiness--september-12)
owns the interpretation. No Ghidra database was opened or changed for this step.

The final affected Core run passed **317/317**, no skips
(`plane-exit-core-final-20260912.{log,trx}`). It uses
`dotnet test rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj`
with `--no-restore --nologo --filter` selecting `Level100ActorPlaneRuntimeTests`,
`Level100ActorMechanicsTests`, `Level100ActorWeaponTests`,
`Level100DestructionContactTests`, `Level100RawPlaneCreationTests`,
`Level100ActorRegistryTests`, `Level100ActorScriptRuntimeTests`, `SimulationTests`,
`ReplayTests`, `HeadlessApplicationTests`, `RetailEventSchedulerTests` and
`RetailEventSchedulerUpdateGuardTests` by `FullyQualifiedName~` joined with `|`.
The log preserves the exact argv. The complete Client suite passed **907**, with
the same two capture-dependent skips and no failures
(`plane-exit-client-final-20260912.{log,trx}`); it uses the Client test project
with `--no-restore --nologo` and no filter. The existing forty-step and 2,148-step
fingerprints still pass unchanged.

The narrower **22/22** lifecycle selection is retained as
`plane-exit-lifecycle-focused-v3-20260912.{log,trx}`. It covers both restore
boundaries, targeted Ready while Init is paused, strict arrival/deadline edges,
both altitude clamps, distinct owner lifetimes, deleted listeners, hash/admission
guards, burst suppression/continuation and next-tick round movement. Before the
repair, both spawner-loss variants failed because generic StartDieProcess also
set DeclaredShutdown (`plane-exit-unit-death-red-20260912.{log,trx}`). The narrow
Unit transition now retains Dying, StartedDying notification, health/parts and
Move recurrence without manufacturing Died/Shutdown. Initial compilation and
the earlier 16/19-case results remain under `plane-exit-lifecycle-*`; the first
compile failure was nullable attachment access and was corrected with `.Value`.

The first adjacent selection passed 314 and failed three cases
(`plane-exit-core-affected-20260912.{log,trx}`). Two rate-cap fixtures supplied
Attack immediately after spawn; they now supply controlled normal-guide input
directly to the same production mover, retaining all original expected values.
The remaining Headless pin had missed the preceding exit-input materialization.
`plane-exit-legacy-fixtures-cause-20260912.{log,trx}` passes the two rate checks
and fails only the deliberately unchanged pin after proving that substituting
only the previous definition identity recovers every prior canonical byte across
all 838 ticks, including the previous complete trace. The final test retains
that proof. Its current trace is
`2da46d641e2187ead860869dd25b5abdf54f59aa5bac8830f7e661babe000309`,
final state `6ec3dfbbfd2351f824e4bab7685503e8e014a57f9e6990ad2c13a78dfc44ad4d`.
The direct `dotnet rebuild/OnslaughtRebuild.Headless/bin/Debug/net8.0/OnslaughtRebuild.Headless.dll --repeat 2`
result is `plane-exit-headless-observed-20260912.json` with no replay divergence.

The two full-combat drivers ran with their existing completion requirements
(`plane-exit-combat-boundary-20260912.{log,trx}`). The returning-career driver,
using its reduced fixture definitions, destroyed all 22 targets, damaged and
killed all six final drones for 6000 damage, completed objective 4 and reached
Won without abort at tick 5588/hull 11450. Its first run passed those assertions
and failed only the old exact tick 7621 pin. Those reconstruction endpoint
readings were updated; no driver commands, steering/damage constants or semantic
completion requirement changed. Exit scheduling, its RNG consumption and delayed
Ready all changed, so this result does not isolate one contributor to each shot.
The repeated returning run and existing causal-damage, abort-silencing and
weapon-event checks then passed **4/4**, no skips
(`plane-exit-returning-combat-final-20260912.{log,trx}`). This uses the same Core
command with a four-method `FullyQualifiedName~` filter recorded in that log.

The cold shipping-manifest route **still fails** the original six-kill assertion:
one final-wave kill, objective 4 Failed, abort at tick 7805 and Won at tick 8141
with hull 4400. Its client and pointer-quantized Core control have no divergent
tick and the same final hash
`b163d10bbd55bf1f183cad36c146f41c5cfa8016ff4a1480a05ab3b5faf6dc30`.
That failure remains visible; it was not repinned or weakened. Both drivers
read internal state and are in-process reconstruction instruments, not player
or retail acceptance. The earlier broad Core run remains a dated failing receipt.

`git diff --check`, the docs gate and public safety gate passed; the latter
checked 3984 candidates. Logs are `plane-exit-docs-20260912.log` and
`plane-exit-safety-20260912.log`; the final documentation refresh uses
`plane-exit-docs-final-20260912.log`.

This closes the selected exit prefix through scheduled Ready and handoff to the
existing approximate normal-control bridge. It does not close provider/common-AI
execution, complete dying flight, contacts, avoidance, full event/RNG order,
or the player-input tutorial and Save Lab UI acceptance routes. No desktop
control, visible launch, asset regeneration or gameplay-constant adjustment was
used. Schema 48 binds spawned exit ownership; unspawned schema 47 stays intact.

## Native companion migration — September 19

This section records the standard-engine/standalone-helper predecessor at
`9764e585`. The active architecture and subsequent checks are in the
[.NET integration section](#companion-net-integration--september-19).

`npm test` runs the standard-engine native scene/domain and media tests, followed
by the explicit file bridge's **17** protocol cases (including six Linux
transaction race/failure cases) and **12** focused launcher/package tests.
The completed run is canonical `local-data/companion/gdscript-test-xc1i0e2n/`.
The fixture was copied before use. Tests independently compare all 10,004 bytes,
selected low-24-bit counts and packed/unselected bytes; source content and physical
identity replacement, aliases, destination conflicts, failed staging and invalid
receipts are meaningful negative cases. Test-only race hooks are absent from the
production protocol. Shared AppCore source remains unchanged.

The isolated Xvfb/llvmpipe render run at
`local-data/companion/gdscript-render-p5wuchkj/` exercised the actual scene and
protected publication before capturing its own viewport. It confirms rendering
and programmatic controls; it does not claim human click-through, audio or Windows
execution. No physical desktop was used. Engine and template identities are pinned
in the companion's `toolchain.json`, verified against the shared installation.

Use `npm run export:companion-godot -- --platform both` for standard Linux/Windows
x86_64 packages with separate self-contained file-bridge directories and licenses.
The September 19 packages are in canonical
`local-data/companion/gdscript-export-pdsz2xf4/packages/`. The final scene suite
also passed against that staged source and its packaged helper after the result
scroll/column-label changes: `local-data/companion/gdscript-final-scene-lfre5ykz/`.

The exported Linux application passed a separate actual-input workflow on isolated
Xvfb with software OpenGL. XTest events reached only that virtual display. The
real file dialog opened an owned golden-fixture copy; controls selected Aircraft
3221 → 123456, displayed the byte preview, explicitly published and reopened the
result, refused an existing destination, created an unchanged recovery copy, and
opened that verified copy as the next source. An independent byte comparison found
exactly offsets `0x23F6`–`0x23F8` changed; all 10,004 bytes of the original and
recovery matched, and all unselected/packed bytes in the edited copy were preserved.
The source SHA-256 is `0c17e47db9d666e9b26ef88d43d0a25e7cbfbf4f88c8005cc748965050e506fb`;
the edited SHA-256 is `84fee8d5db1967b38788e363e314be5dce2c1ef276cbc11fd5fa12eb2f43a51e`.
`ONSLAUGHT_FILE_BRIDGE` was unset, `PATH` was `/usr/bin:/bin`, and `DOTNET_ROOT`
pointed to a nonexistent directory, exercising the sibling self-contained helper.
Receipts and own-display captures are in
`local-data/companion/export-acceptance-nx_j5ynz/`. The app and virtual server were
stopped after the check. Only virtual input-method/V-Sync warnings occurred.

Both package hash inventories verified all 194 listed files. The Linux inventory
covers 152,222,368 bytes and Windows 185,773,971 bytes, excluding the inventory
file itself. ELF/PE x86_64 identities, runtime 8.0.30 and licenses were inspected.
Mounted package resource views contained no legacy C# project, tests, saves,
retail or GPL rebuild payloads. This is Windows cross-export/package evidence;
Windows execution, its retained guarded staging handoff, human usability and
audio acceptance remain open. No physical desktop, VM, release or hosted CI was
used.

The original worktree project also passed a headless standard-editor import,
including its retained C# reference files. Its ten GDScript UID files are tracked
so opening the source preserves stable editor identities. Import receipt:
`local-data/companion/gdscript-source-editor-o1jyr6ug/logs/source-import.log`.

## Companion .NET integration — September 19

David clarified that any necessary C# belongs inside Godot's .NET edition, while
GDScript should own as much application behavior as possible. The companion now
uses the existing shared **4.8.dev6.mono.official.8898c2b3d** editor and matching
templates. The standard `godot48` install was not changed. The active C# assembly
contains a thin RefCounted adapter, compatibility stubs and the two unchanged MIT
file-safety sources. Scenes, save interpretation, edit plans, comparison, media
inventory and workflow remain GDScript. The subprocess protocol, base64 transport,
helper-path environment hook and sibling production helper are gone.

`npm test` passed in canonical `local-data/companion/godot-dotnet-test-1rg3gl2k/`:
the actual scene workflow, byte-domain and media cases, direct adapter tests, six
publication races and twelve launcher tests. Adapter cases include exact owned
round trips, independently prepared byte edits, malformed lengths/hashes/paths,
same-byte source identity replacement, changed content, hard/symbolic links,
existing/dangling destinations and game-tree refusal. The scene verifies raw
managed byte-array results and independently reopens successful publications.
No legacy JSON protocol test is counted as current application acceptance.

The subsequent main integration independently reran `npm test` against the
combined tree: the Godot .NET build had zero warnings/errors, headless import and
all GDScript checks passed, the actual scene/domain/adapter workflow reported zero
failures, and all six publication race cases and twelve launcher tests passed.
Runtime output is canonical `local-data/companion/godot-dotnet-test-fa1cjhbm/`;
the integration command/log owner is
`.worktrees/main-integration-20260919/local-data/merge-checks/companion-dotnet-ym7xiwqf/`.
The integration did not rerun the exported-app interaction or Windows acceptance
described below. Rebuild production files and the separate RE checkout were not
changed by this companion merge.

The UI awaits one worker thread without falsely treating a timeout as cancellation.
Normal closing while busy is deferred until the transaction returns; shutdown
joins an outstanding worker. A read-only integration review found no actionable
ownership, thread-lifetime, uncertainty or unchecked-write issue. The unchanged
filesystem code's Windows staging-handoff and power-loss limitations remain as
documented in the [API/safety record](https://github.com/dlprentice/Onslaught-Career-Editor/blob/d5e002d00aa8b7d2fb6d745aa1775285d957f2fd/companion/OnslaughtToolkit.FileBridge/README.md), retired with the prototype on September 25.

The actual worktree source built with zero warnings/errors and imported headlessly
with the .NET editor: `local-data/companion/mono-source-editor-ps1m7phv/`.
The same source also passed the editor's `--build-solutions` command, recorded in
`editor-build.log`. This validates the source project a user opens, as well as the
isolated snapshots.

Normal Godot .NET Linux and Windows x86_64 exports completed in canonical
`local-data/companion/godot-dotnet-export-ph2r7cmk/packages/`. Both hash inventories
verified all 194 entries, covering 158,347,590 Linux bytes and 191,890,481 Windows
bytes, excluding the inventories themselves. Package inspection confirmed ELF/PE
x86_64 executables, the integrated assembly, runtime 8.0.30 and notices. No helper,
AppCore assembly, WinUI assembly or test harness is shipped. The mounted resource
views omit retained SaveLab/test resources; the two active C# script resources are
Godot's one-newline managed-script placeholders, not source text.

The exported Linux .NET application passed real file-dialog and button input on
isolated Xvfb/software OpenGL. XTest reached only that private display. The flow
opened an owned real-fixture copy, selected Aircraft 3221 → 123456, previewed the
three changed bytes, explicitly published and verified/reopened the edited copy,
refused an existing destination without changing it, created an unchanged recovery
copy and opened that verified result. Independent full-byte checks found only
`0x23F6`–`0x23F8` changed. The original and recovery matched all 10,004 fixture bytes
(SHA-256 `0c17e47db9d666e9b26ef88d43d0a25e7cbfbf4f88c8005cc748965050e506fb`);
the edited copy hashed to
`84fee8d5db1967b38788e363e314be5dce2c1ef276cbc11fd5fa12eb2f43a51e`.
`PATH` was an empty directory, both `DOTNET_ROOT` variables pointed to nonexistent
directories and the old helper environment hook was unset. `/proc` mappings
confirmed `libcoreclr`, `libhostfxr` and `libhostpolicy` loaded from the exported
package's own runtime directory. Receipt, package inspection and own-display
captures: `local-data/companion/dotnet-export-acceptance-d394_btv/`.

Normal exported-app closing through `WM_DELETE_WINDOW` on a separate private
display exited with code 0 and no error lines:
`local-data/companion/dotnet-close-wm-atoms-_gnw9ww7/receipt.json`.
The bare virtual display needed the standard window-manager atoms initialized
before launch. The earlier forced-SIGTERM cleanup emitted engine teardown
diagnostics and is retained separately, not counted as clean closing. Both runs'
owned app/server processes, display sockets and private cookies were cleaned up.

This is executed Linux workflow evidence and Windows cross-export/package
inspection. Windows execution, human usability and audio acceptance remain pending.
No physical desktop, VM, release or hosted CI was used.

## Companion C# migration — September 25

Branch `claude/companion-csharp-20260925` replaced the companion's GDScript domain,
interface and tests with one C# application built in code. `Main.tscn` is a one-node
wrapper attaching `Ui/CompanionApp.cs`; the build now refuses `.gd`, saved resources and
any scene with more than that node. Each former GDScript contract moved to a C# suite
run inside headless Godot by `Tests/CompanionTestRunner.cs`: the codec checks to
`CareerSaveTests`, the media checks to `MediaCatalogTests`, the direct adapter checks to
`ProtectedFilesTests`, the scene workflow to `CompanionUiTests`, and the retired
FileBridge harness's six Linux publication races to `TransactionRaceTests`, which calls
the linked transaction's internal hook in-process. GDScript's string-key, float and
boolean selection refusals have no C# equivalent because selections are typed; every
representable invalid selection is still refused. New checks cover plan immutability,
the preview's byte count, one listed row per differing byte, a receipt whose bytes
differ from the plan, a worker with no protected access, scan-limit and relative-path
refusal, and explicitly reopening a verified result. `Tests/` and `Development/`
compile only into development builds; the export launcher refuses a release assembly
that contains either namespace.

`npm test` passed in canonical `local-data/companion/godot-dotnet-test-6r33pbap/`:
**302 checks, 0 failures**, then all **15** launcher cases, in 9.3 s. The C# build
reported zero warnings and errors with warnings treated as errors. Two deliberate
defects — authoring the packed fourth kill byte and accepting a receipt without
original verification — turned the same suite red with exit code 1 and ten named
failures: `local-data/companion/godot-dotnet-test-6862alcj/`. The standalone FileBridge
prototype and its Python protocol test were removed; their Windows staging-handoff and
power-loss limits now live in the [companion README](companion/OnslaughtToolkit.Godot/README.md#file-safety-boundary).

## Companion approved workflows — September 26

David approved four feature groups and the Flight-deck look on 2026-09-25 (careers and
Goodies; copies and options; install and backups; music, voices and lore), with patching
the installed `BEA.exe` left for a later phase. Branch `claude/companion-csharp-20260925`
built all four in C# and in code; the [companion README](companion/OnslaughtToolkit.Godot/README.md)
describes them and [CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md#godot-companion--careers-options-install-music-and-lore)
states their limits.

**Suite.** `npm test` passed in canonical `local-data/companion/godot-dotnet-test-mzmgwefv/`:
**596 checks, 0 failures**, then all **16** launcher cases, in 13 s, with zero build warnings
under warnings-as-errors. New suites cover Steam discovery on a fake library, the game's
text decoded from a synthetic v3 language table, backup sets and installs (a new career, a
replaced career and options file, refusals for unsafe target names, a running game, an
unsupported source and a backup folder inside the game, a career that changes after its
backup, and a file that takes the target's name just before the exchange), the options
block and key table, music and voice grouping and the Vorbis header check, and the lore
library: reading order, header removal, balanced markup and every link in every article.

**Falsifiers.** Disabling the check that the file displaced by `RENAME_EXCHANGE` is the one
backed up turned the suite red with the named swap-back failure, exit 1:
`local-data/companion/godot-dotnet-test-3_qidnty/`. The lore link check failed on a real
anchor, `lore/units-and-mechs.md:173` → `worlds.md#world-500-career-node-23`, which GitHub
never resolved either (the em dash leaves `world-500--career-node-23`); the link was
corrected in `a0246a39`.

**Screens.** `npm run capture:companion-godot` rendered 76 screens through `godot-offscreen`
at 1280×800 and 1920×1080 against a fake install —
`local-data/companion/godot-dotnet-capture-y9reye8p/captures/` — and 74 against the real
Steam library with `--capture-arg=--steam-root=$HOME/.local/share/Steam` —
`local-data/companion/godot-dotnet-capture-l1d7rpel/captures/`. The real install's
`BEA.exe`, `defaultoptions.bea` and its one career hashed identically before and after
that run, and `savegames/` gained no file. Every page and state was reviewed first-hand at
both sizes: each page empty, the career pages with the fixture open, cheat names with and
without a backup folder, options from open to a captured key and a verified copy, backup
sets, an install into the fake game, each confirmation dialog, a loaded voice line, and
the lore reader's front door, memo, section link, tables, mission list and search. The
review led to the fixes in `da660c0a`. The real install showed the Steam `BEA.exe`
recognised, the game's mission names and Goodie titles, voice transcripts, and the
campaign page's mission table read from the game's text.

**Packages.** `npm run export:companion-godot -- --platform both` built
`local-data/companion/godot-dotnet-export-qnwi9ous/packages/linux` (152 MB) and `windows`
(184 MB). Each release `OnslaughtToolkit.Godot.dll` (635,392 bytes) carries the embedded
lore and neither the `Tests` nor the `Development` namespace. The Linux package ran
`--headless --quit-after 240` with isolated XDG directories and exited 0 with no error
output; no core dump from the companion appeared.

**Not verified.** Windows execution, including the Windows file path for copies and
backups; a human click-through with a mouse and keyboard; listening to the music and voice
playback (the audio was decoded, never heard); and anything the game does with a copy
beyond the options, Goodie and cheat behaviour the RE lane has already watched.
