# Onslaught Rebuild

Status: early GPL reconstruction lane
Last updated: 2026-08-24. The bounded world-110 authored-definition projection,
native-88 Core session, career read/load frontend slice, and world-admission
claims below are the newly re-reviewed surface.
Other sections retain their narrower dated evidence boundaries.
Summary: what the `rebuild/` lane is, who owns which assembly, and what the
Level 100 Opening Slice does and does not currently do.
[`PROVENANCE.md`](PROVENANCE.md) is the authority for its evidence boundary.
[`DETERMINISM.md`](DETERMINISM.md) is the determinism contract (the first
thing a contributor to Core breaks). [`PARITY.md`](PARITY.md) defines what
"1:1 parity" means operationally and what is currently graded.

This subtree is the replacement-engine effort for *Battle Engine Aquila*. It is
source- and RE-informed, not clean-room. The immediate target is a bounded
released-style startup/menu path into a recognizable Aquila handling slice and
the opening portion of Level 100—not a larger synthetic arena or another layer
of readiness tooling.

## Ownership

- `OnslaughtRebuild.Core` owns deterministic simulation state and fixed 20 Hz
  stepping - retail's own rate, `GAME_FR 20.0` / `CLOCK_TICK 0.05`. It has no presentation, filesystem, clock, process, network, or GPU
  dependency.
- `OnslaughtRebuild.Client` adapts real-time input to exact Core steps and owns
  the presentation-only frontend lifecycle state.
- `OnslaughtRebuild.Headless` replays command tapes and verifies versioned final
  state and rolling trace hashes.
- `OnslaughtRebuild.Godot` renders Core snapshots and supplies player input.

The current Godot app is the **Level 100 Opening Slice**. With locally
materialized media, a plain launch plays the released Lost Toys logo, opening
montage, and splash before click-to-start, v3 main-menu language, retail's
career-name/load page, the bounded Godot level selector, the mission-briefing
and select-configuration pages, and loading. Loading constructs the Level 100
world; the first-time intro then plays before gameplay activation. Repeating
`--career-save=<path>` opts in exact named career files for the Load Game list;
the host performs no directory or installed-save discovery and never writes
those files.
`--skipfmv`, smoke, and capture modes suppress those video sequences. Their
Bink audio streams are not decoded, so video playback is currently silent.
(*Extended 2026-07-28: this read "click-to-start page, v3 main-menu language, a
Level 100-only level selector, and the released loading-screen language". The
three pages added had already shipped; see* `## Current truth` *below for the
full list and its authority.*) It renders the locally
materialized released Federation Aquila; all 33 visible static objects
serialized by Level 100; exact close meshes for the 1,481 pine placements
instantiated by the Steam world loader; the released active-path water grid and
authored shoreline; three training tanks; and the target Warehouse at their
authored positions over the exact Level 100 heightfield lattice. Core owns the
released player start heading, exact
Level 100 player-ground sampling, and the machine-observed objective and player
gates through the first Firing Range exercise. The walker is loaded directly
from its exact released AYA as a 63-part
hierarchy; its twenty animated leg-chain parts consume four deterministic Core
foot contacts. The released controller's diagonal swing scheduling and Level 100
height contacts select independent `LegMotion` extension poses for each leg.
The exact 54-part jet and 21-part cockpit hierarchies own the bounded
walker-to-jet presentation. The 24 non-tree static-world mesh types, four pine
variants, and two target types retain bounded static conversions. The 1,481
pine placements use their exact meshes inside the released out-of-box
**Medium-detail 30-unit**
mesh-quality boundary and their six-face imposters outside it.
(*Corrected 2026-07-27, recorded here 2026-07-28: this read "inside the selected
released high-quality 70-unit boundary".* `70.0` *is the released High-detail
arm, but it was not the released out-of-box/current default; this workstation's
saved* `defaultoptions.bea` *selected it.
The image's own static initialiser is* `30.0f` *at file* `0x2321A0` *of the
pristine specimen* `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`*,
SHA-256* `74154bfa…`*, read again during this pass; the released out-of-box
Geometry detail arm is Medium. Offset table and the proof that*
`defaultoptions.bea` *is run state:* [`PROVENANCE.md`](PROVENANCE.md)*.*) The
reconstruction draws no third fast-tree path: no always-on camera-facing
standing card and no height-gated horizontal card is rendered — the only pine
representations are the gated close meshes and the six-face far imposters
(`rebuild/OnslaughtRebuild.Client.Tests/Level100PineRepresentationTests.cs`
forbids any third batch, `AddFastPineImposters`, and `camera_facing`). Retail's
own separate fast-tree static findings stay an unresolved retail path, not
drawn by the reconstruction. The converted meshes render with
their active retained retail material passes and
follow the released PC ambient, opposing sun/anti-sun, and `MODULATE2X` path
rather than approximate Godot PBR values. The
released macro terrain blend, repeating detail and moving cloud-shadow textures,
cube-25 sky, and exponential `CHFD` fog now replace the procedural ground/sky.
The shared fixed-function shader also owns the renderer-aware final color
transfer, so the Compatibility renderer does not apply the old double transfer.
The opening view uses the released Level
100 four-point exterior fly-in, then hands off to the released first-person
projection and exact walker cockpit at its runtime-selected `walk` pose. The HUD
remains hidden with the pan camera and appears at the control-camera handoff.
Twenty-nine exact HUD textures and the released Font13PS atlas now compose the
bounded v3 crosshair, threat compass, lower-left scanner/weapon instrument,
lower-right battleline/portrait, active-objective markers, and conditional
message panel. The first seventeen released English tutorial messages through
the first exercise's Vulcan handoff now use their exact text, shipped voice
clips, proportional font metrics, and four released Tatiana/technician portrait
poses. Core follows the observed
power, objective, weapon-highlight, four-target, and Pulse Cannon activation
boundaries while keeping flight disabled. Independently repeated lowest-charge
Pulse Cannon runs now give all three training tanks their retail speed,
direct-hit damage, and four-hit deactivation. Two isolated Warehouse runs also
repeat one fixed center-aim twelve-hit path and the released Vulcan handoff.
Godot consumes the exact released round, impact, tank-destruction, sound, text,
and voice assets required by that path.
The path-specific Godot audio owner also retains all 51 accepted English Level
100 character messages, the released tutorial music selection, and the exact
menu, Aquila, weapon, warning, actor, repair, hit, destruction, and debris PCM
records required through mission return. It centralizes pause/resume/stop and
loop ownership. Playback consumes ordered mission-message, Aquila-flight, and
destruction envelopes from the client frame result. The Aquila source binds to
the native `Player 1` ActorId and follows its full three-dimensional registry
pose; pause, frontend, and level-exit state remain supplied by their existing
owners. Audio does not own mission waits, objectives, actor mechanics, frontend
pages, or pause actions. Retained cues without canonical events remain silent.
The wired mission still reproduces only the observed circular walker contact
and tangent slide for the Control Tower and Tank Factory. Pulse projectiles
consume identity, active state, full pose/basis, velocity, health and lifecycle
from the canonical actor registry. Their dependency-inverted contact owner uses
BBOX only for broadphase and a hash-verified, millimetre-quantized mesh
projection for narrowphase. The Warehouse path applies
the evidenced extent-weighted segment health, `5.0` core multiplier,
core-child/strict-`30%` terminal rules, and reports ordered hit/dying/died facts
without owning objectives or mission progression. The client consumes the
ordered typed impact/terminal effects across every Core step in a rendered
frame. Secondary material passes, steep-slope and broader actor/structure
collision, unmeasured mesh-part damage variation, retail debris RNG/bounce,
occupancy/path-grid route adjustment, Target Truck contact/destruction,
Vulcan contact/damage parity, and most mission behavior remain provisional.
The bounded ground-vehicle owner does retain the released Target Tank and
Target Truck command intents and advances their canonical actor poses from the
materialized waypoint and physics definitions.

Retail asset payloads and converted copies are not repository source. The
bounded materializer verifies a supported user-provided installation and writes
the exact current slice to ignored paths. Expected source hashes and limitations
live with the [`Frontend`](OnslaughtRebuild.Godot/Assets/Frontend/README.md),
[`Aquila`](OnslaughtRebuild.Godot/Assets/Aquila/README.md), and
[`Level 100`](OnslaughtRebuild.Godot/Assets/Level100/README.md) recipes.

## Run

Install .NET 8, then from the repository root run:

```powershell
npm run run:rebuild-godot
```

The command first detects a lawfully obtained retail installation and
materializes the exact current source/runtime files to ignored paths. For a custom
location, run
`pwsh rebuild/tools/Run-FirstFlight.ps1 -GameRoot "<game folder>"`. The first
run uses the pinned official Godot 4.7.1 .NET Windows toolchain described by
`toolchains/godot-4.7-stable-win-x64.json`. When the process—or, on Windows,
the current user—has `GODOT_DOTNET_ROOT` pointing to that exact verified tree,
the system installation is reused; otherwise the archive is downloaded to a
per-user cache and verified before every execution.
Use `pwsh rebuild/tools/Run-FirstFlight.ps1 -Offline` to forbid downloads.

`npm run prepare:rebuild-assets` performs the same exact local materialization
without building or launching. Core, client, headless, and native smoke commands
use that same owner; no separate manual extraction path is required.

Controls:

| Input | Action |
| --- | --- |
| Mouse, `Up`, `Down` | Navigate the frontend |
| Click, `Space`, `Enter` | Leave click-to-start or select the highlighted frontend item |
| `Esc` | Return from frontend level selection; open/close the gameplay pause root |
| Mouse, wheel, `Up`, `Down`, `Enter`, controller D-pad/A/B/Start | Navigate or close the gameplay pause root |
| `W`, `A`, `S`, `D` or arrow keys | Move forward/back and strafe after the tutorial powers the Aquila |
| Mouse or trackpad | Turn the body and aim the attached first-person view |
| Mouse wheel down/up during walker gameplay | Zoom in/out with the released `1.0` to `0.4` Battle Engine law |
| Middle mouse or `;` during gameplay | Cycle to the next active weapon; the released heat/store eligibility extension and Missile Pod firing remain incomplete |
| `Space` | Fire the selected implemented weapon after the tutorial enables it |
| `R` | Reset the slice |

## Current truth

The frontend owns click-to-start, Main Menu, the Quit confirmation, DevSelect
(retail's `CHOOSE GAME NAME` surface for a new name or an injected read-only
career selection), Options, Client's career-law selection state, the bounded
Godot level-selector page, Mission Briefing, Select Configuration, Loading, and
the Level 100 intro cutscene. The
`RetailFrontendScreen` enum in
`rebuild/OnslaughtRebuild.Client/RetailFrontendSession.cs` is authoritative for
that list; read it rather than this sentence when the two disagree.
(*Corrected 2026-07-28: this read "The frontend owns **only** click-to-start,
Main Menu, the Level 100-only selector, and Loading." The word "only" made it a
completeness claim and it was false — five further screens were already declared
and shipping. Nothing was removed; the list was understated.*)
`RetailCareerSaveCodec` is a deterministic Core reader over a caller-supplied
byte span. It accepts only the measured 10,004-byte / `0x4BD1` PC container,
validates the 43 campaign nodes and 86 structural link rows, retains a private
copy of every byte (including reserved/options/tail bytes), and exposes the
current completion/grade, Goodie-count, selectable-world, and latest-selectable
summary. It has no load-by-path, serializer, or write API. Tests use only
`tests_shared/fixtures/gold_career_save.bin` (10,004 bytes, SHA-256
`0c17e47db9d666e9b26ef88d43d0a25e7cbfbf4f88c8005cc748965050e506fb`).
The Godot adapter reads only repeated explicit `--career-save=<path>` arguments
and injects slot/name descriptors into Client in argument order. Load Game then
owns bounded selection, accept/back, and a one-shot selected-career handoff;
there is still no implicit save scan, save creation, overwrite, autosave,
debrief persistence, or options-tail application. A loaded model remains
immutable; merging a later Won update back into that model is also still open.
Core/Client can carry any loaded career's `SuggestedWorldNumber`, and
`SelectWorld` applies the released career unlock law. The current Godot page
does not project that general state: it does not read `SelectedWorldNumber` for
rendering or implement LevelSelect keyboard traversal, its pointer path exposes
only world 100 and unlocked world 110, and the host constructs only world 100.
(*Updated 2026-08-22: the selector is no longer Level-100-only by law. The
session carries the released 43-node career graph
(`OnslaughtRebuild.Core/RetailWorldCatalog.cs`, Stuart's pinned
`Career.cpp:24-70`) and `SelectWorld` admits a world exactly when retail's
measured ReCalcLinks unlock admits it — the root always, any other world once a
completed incoming link points at it. The launch edge was renamed
`LevelLaunchRequested` and carries `ConsumeLaunchWorldNumber`. What a launch
*constructs* is still Level 100 only: world-110's compiled scripts, heightfield,
and identity-only authored-definition projection are admitted by Core (below),
and a bounded Core-only session now steps its LevelScript against a
world-stamped copy of the Level 100 test fixture. A complete world-110 actor
definition set and Godot lifecycle still do not exist, so the host cannot build
that world. After a Level 100 Won reaches `FrontEndHandoffReady`, Client applies
the pinned FillOut/Career update, consumes the two Career Goodie latches in
retail order, and opens `FEP_DEBRIEFING`. The settled page projects the measured
mission status, objective-group summaries, and win-only grade and draws the
exact locally materialized rank/ring surfaces. Confirm or Back then enters
SELECT LEVEL, where world 110 is already selectable. The Episode-1 child node
is clickable, but launching it returns to SELECT LEVEL rather than constructing
Level 100 in its place. `SetCurrentLevelToHighestAvailable` is not in the source
drop and is not invented — the highlight stays on the root until the player
picks the child.*
Each launch request makes the host construct a fresh canonical
`InteractiveSession` from the materialized Level 100 actor definitions before
gameplay activation. The frontend does not inspect
`WorldSnapshot.Level100Mission` or own gameplay or save writes; it does own the
explicit debriefing projection and result-page presentation/navigation.
`RestartLevel100` returns through the same Loading edge;
`LeaveLevel100ForMainMenu` disposes the active world and returns to the same
frontend shell.
The gameplay pause owner freezes that same deterministic session with zero Core
steps, discards pending gameplay input, pauses the existing Level 100 audio
owner, and routes its cursor through the frontend's sole mouse-mode writer.
Continue resumes after a neutral input sample; Retry and Quit call those
existing lifecycle seams after the audio owner completes its kill-then-Select
exit boundary once. Message Log, Briefing, and the three settings rows remain
visible but disabled until canonical integrated owners exist. The current
opening slice does not synthesize terminal events, a kill summary, or save
writes. Its post-Won debrief is a bounded static-to-rebuild projection, not
complete post-Won parity: the canned Level-100 ranking remains an unmeasured
live score/time shortcut; outro FMV, entry/exit interpolation, Goodie effects
and first-Goodie message, grade glint, persistence, and retail-frame pixel
validation remain open. The page does not claim a kill summary or visible
Goodie list because retail Render contains neither. `FrontendAudioCueRequested`
is an observation seam; the existing Level 100 audio owner remains the sole
playback owner.

Core currently provides integer positions, opening tutorial/objective state,
reset behavior, ordered snapshots, and versioned SHA-256 state and trace hashes.
Resource and cooldown behavior remains provisional. The bounded three-training-
tank path uses the observed Pulse Cannon gate, continuous-yaw projectile heading,
retail speed, direct-hit damage, and objective removal. Continuous body yaw and
Level 100 objective state are part of the snapshot/hash, and every input axis—including
look—is part of the trace. Walker acceleration is projected through the body's
continuous deterministic yaw; only jet movement retains the older eight-way
approximation.

Core also carries the released-family `CUnitAI` close-target scoring kernel as
`RetailUnitAITargetSelection`. Its upstream adapter selects one of three
caller-captured world-list views by owner allegiance, applies the released
squad-or-unit transform, preserves list order, and deliberately measures
distance from the raw payload while reading scoring fields from the resolved
unit. The scorer then computes the exact `TF_DYING`/mode and
allegiance/`CUnitIndiscriminate` gates before applying the measured range gate,
source-backed `IsAThreat()`/`CUnitIgnoreThreats` zero-score law,
`CUnitAttackPriority` ladder, stable primary/secondary tie law, and shared-stream
random arm. This is not autonomous AI wiring: population and
lifecycle of the three world indexes, the ordered weapon/capability gate,
reader mutation, attack-provider selection, and fire-feasibility helper
population remain outside Core until their owning actor paths are reconstructed.

Core separately carries the ordered all-squads probe from the enclosing UnitAI
update as `RetailUnitAISquadSupportProbe`. It consumes caller-captured
`CWorld::GetSquadNB()` order, preserves the current-squad/null/side/capability
filters and strict squad-position range test, and emits every downstream helper
call in order. The caller executes that call before reading the live successor,
because spawning can tail-append a squad that retail visits in the same scan.
The step deliberately retains duplicate squads and the separately resolved
second representative, including null; retail neither chooses a winner nor
stops after one passing squad. Squad lifecycle, virtual calls, spawner
readiness/masks/ranges, and actual spawning remain actor-runtime work.

`RetailUnitAITargetTransaction` now joins that probe and the target scorer at
the next exact boundary. It emits the ordered calls and raw field writes for
slot 4's caller-retained refresh, slot 11's fast reuse, or slot 11's full
selection commit. The full path preserves result pre-clear order, the SetReader
call, two support updates around the first runtime-gate clear, conditional B/A
evaluation, the second gate clear, and the released no-rollback behavior. It
also preserves PC's C3-only NaN fast-reuse quirk separately from Xbox/PS2's
ordered-zero rule. The Godot actor adapter still must execute deletion-aware
reader mutation and concrete support/weapon helpers; Core does not pretend an
integer identity is a retail monitor pointer.

The earlier slot-4 direct/current-target arm is carried separately by
`RetailUnitAIDirectTargetArm`. It clears a dying entry reader before the raw
membership virtual, falls through without touching results when that gate is
absent/nonzero, otherwise pre-clears A then B, clears the reader on active-state
failure, and runs support/B/conditional-A in released order. Its request keeps
the reader identity observed at each call site, so a lifecycle change between
stages is not flattened into one stale target. The membership virtual's
authored name and all pointer/monitor/helper execution remain adapter-owned.

`RetailUnitAIUpdateTransaction` now closes the next PC retail/demo cadence
boundary: shared virtual slot 3 always refreshes target/support state, then
chooses jittered aim, direct aim, fire support, or one of two idle delays. Core
preserves its exact zero/one/four random-draw law, strict jitter sign threshold,
stage-local target rereads, target-clear tail, idle owner writes, and returned
delay. The enclosing event-3000 handler reuses its incoming event and rounds
manager time plus that delay to float only once; Core preserves that x87 order,
including a measured one-bit discriminator against ordinary chained float
addition. Matrix/aim helpers, virtual execution, monitor lifetime, event
delivery, and autonomous actor scheduling remain adapter work.

`RetailActiveReaderGraph` now supplies that deletion-aware boundary. It gives
each non-owning reader a stable cell identity, preserves exact same-target
no-op and detach-old/publish-new/attach-new rebind order, and tracks each
target's reverse memberships newest-first. Target shutdown nulls only those
registered cells before clearing the reverse set; for the UnitAI retained
target this leaves the adjacent gate and fire-result fields untouched. The PC
UnitAI owner path also detaches outbound cells `+0x28`, `+0x24`, then `+0x0C`
before invalidating readers aimed at the dying AI. Runtime objects and pointers
remain adapter-owned; Core models the deterministic relationship, not retail's
allocation-failure crash.

`RetailSpawnerCycleTransaction` closes the nested spawner boundary that the
live UnitAI probe can invoke. It preserves strict admission time, finite amount
versus infinite mode, empty-squad publication before cycle commit, amount-slot
consumption even when the squad factory returns null, and the synchronous first
member wave. Subsequent member success attaches only when a squad exists;
clearance/allocation failure retains the busy cycle and schedules event 3000,
while final success clears the squad flag/reader/busy latch and writes the next
squad time in released order. Disabling does not cancel a busy wave. Core emits
the deterministic transaction transcript; allocation, virtual initialization,
live world-list mutation, reader lifetime, clearance, attachment, and event
delivery remain runtime-adapter work.

World admission is no longer Level-100-only in Core (2026-08-22): the released
43-node career graph lives in `RetailWorldCatalog` with its selectability law,
world 110 — the second career node — is admitted from its own measured
payloads, world 200 — the third node — joins it, and the separately measured
world-300 main-episode payload is admitted without pretending its enclosing
level-world header shares the earlier shape.
`materialize_retail_assets.py` pins `data/resources/110_res_PC.aya`
(SHA-256 `4e041c75…3c2b`) and walks out its 13 version-50 script objects plus
the HFLD envelope into `Assets/Level110/`; `Level100MissionProgram.LoadEmbedded`
admits them per-world under the same hash law as Level 100 (world 110's
LevelScript: 181 instructions, 92 symbols, five named events), and
`Level100Terrain.World110` carries the heightfield under the same envelope law.
An explicit Core-only session now consumes the world-110 LevelScript through its
first `Pause` and one idle step. Native 88 writes the measured failed secondary
slot, and StateHasher schema 43 binds the non-root world and all ten secondary
records while default world 100 stays byte-identical on schema 42. This session
deliberately stamps the existing Level 100 test definitions: no product/Godot
simulation consumes world-110 terrain or authored actors, and no world-110
FillOut or full mission run exists. The level-world actor table is measured
(40 RLWD initial actors, header `(2, 0, 40)`; types 19 and 28 are trailers
Level 100 does not use) and the BSWD island is byte-identical to Level 100
(`04c5a383…10f4`). `RetailWorldActorDefinitionAdmission` now admits the exact
archive identity plus 49 ordered definition-bearing object identities under the
existing `wres:bswd:NNNN` / `wres:rlwd:NNNN` law: 33 shared-BSWD actor rows,
15 world-110 RLWD actor rows, and one type-19 spawner row. Wrong world, archive,
object, definition, count, or row shape fails closed. This is an identity/shape
projection only: it carries no authored pose, mesh, health, runtime class,
player binding, actor registry, or session construction. RLWD ordinal 0 is the
LevelScript object, and the type-15 start carries no Battle Engine definition;
there is still no authored `Player 1` definition to construct.

World 200 (2026-08-22) generalizes that pattern and measures three places the
shared law needed refining: `data/resources/200_res_PC.aya` (SHA-256
`99dbd433…b77`) yields fourteen script objects into `Assets/Level200/`
(LevelScript: 413 instructions, 169 symbols, sixteen named events), the HFLD
envelope — found inside ERES by the same whole-image tag/size/hash scan as
worlds 100 and 110 — lands in
`Level100Terrain.World200`, and `RetailWorld200LevelActors` pins the census:
actor header `(3, 0, 54)`, post-zeros word **2** (earlier worlds carry 1),
and an own 80,232-byte BSWD (`9c0575ea…adba`) instead of the shared island.
The named-event identifier source is now value-text-first with symbol-name
fallback in `Level100MissionProgram.Parse`, which worlds 100/110 satisfy
unchanged. No world-200 actor-table record walk has been completed yet; no
simulation consumes any of these payloads, and the only product/Godot session
owner remains Level 100.

World 300 (2026-08-22) is the explicit falsifier for treating "version 50" as
one RLWD preamble. `data/resources/300_res_PC.aya` (SHA-256
`7293bcbe…9efe4`, 1,927,844 bytes) carries header words `(3, 47, 300)`, then
three names — `Standard`, `Laser`, `Blaster` — and trailing words
`(1, 1, 1, 0, 3)`, where worlds 100/110/200 carry `(3, 41, world)`, one
`Aquila Prototype` name, and zeroes before the final variant word. The
materializer therefore models an exact `_WorldLevelHeader` per variant and
drives all later-world extraction from `LATER_WORLD_ADMISSIONS`; it does not
copy a third extraction block or weaken the header check. Its eight hash-pinned
compiled objects land in `Assets/Level300/`; the main object is released as
`Level300script`, not `LevelScript` (448 instructions, 197 symbols, ten named
events). The 668,660-byte framed HFLD remains inside ERES
(`68a181f9…acb1a`), while WRES owns world 300's distinct 77,113-byte BSWD
payload (`3c153d55…0dfc`). The actor header after the script region is
`(10, 0, 36)`. `RetailWorldCatalog.FindPayloadCensus(300)` pins those measured
facts without naming the unknown header words. No complete per-type walk of
the 36 actor records is promoted: the partial probe reaches a type-38 trailer
whose wider record law is unresolved. No world-300 VM run, actor projection,
or session owner exists, and the only constructed product world remains Level
100.

The walker now consumes the shipped Aquila configuration's exact `1.0/75`
yaw-input gain instead of the older fitted `1.7/75` value. Terrain touchdown
also consumes the pinned-source and pristine-PC-static Battle Engine contract:
retail `CBattleEngine::DeclareOnGround` at `0x0040C750` has the same strict
walker/non-walker speed thresholds, dash self-damage immunity, incidence-squared
shield-bypassing damage and whole-velocity retention, plus the low-speed jet's
`0.90` retention. Core evaluates that contact against its deterministic Level
100 HFLD normal. Runtime outcome/quantization parity, object-supported contact,
and the separate generic vertical bounce remain open; see
[`PROVENANCE.md`](PROVENANCE.md) and delta D20 rather than treating the source
port or static identity as runtime proof.

Repeated Level 100 retail observations now inform walker acceleration, equal
forward/strafe speed, frictional coast, and inertial body turning. Walker-to-jet
remains an explicit transition for 10 Core ticks before Jet mode commits;
repeated transform input, movement, turning, and fire are blocked during that
state, but clean Level 100 keeps the flight gate closed throughout the current
slice. A separate clean control and two early-flight copied-runtime repetitions
establish that Steam swaps to its 54-part jet hierarchy at transition entry,
runs the external `walktofly` animation for about 1.24 seconds, and independently
changes the 21-part cockpit over about 1.14 seconds without replacing the
attached camera. Godot consumes those exact authored hierarchies and the exact
takeoff/in-flight PCM records while leaving Core's shorter state transition
unchanged. The presentation camera now uses clean Level 100's released opening
lifecycle: four orientation-relative spline points around the exterior Aquila,
a six-second Steam pan, control-view handoff at 5.95 seconds, and then the
attached first-person view at the Aquila center of gravity with its horizontal
orientation and BattleEngine-owned vertical pitch, 58.7155-degree vertical
field of view, 0.1 near plane, and authored frame-25 walker cockpit. Core
mirrors the released playing-state
camera boundary at 180 fixed ticks, then keeps movement/look gated until the
mission powers the Aquila at tick 1000. Reaching the Firing Range temporarily
deactivates the player, then re-enables it with the Pulse Cannon; flight remains
disabled. Walker pitch uses the released `1/117`-radian input and `0.8`
retention verbatim, with the two repeated absolute limits measured
on Level 100's authored start slope. Pulse Cannon and both player Vulcans now
apply each mode's shipped inaccuracy through the exact shared-gameplay-stream
two-draw order, while rounds still begin at the measured cockpit `Gun` emitter.
The base aim remains the crosshair camera's yaw/pitch; exact absolute retail RNG
phase, predictive aiming, and authored per-round muzzle sequences remain open.
Terrain-relative pitch limiting, vertical target collision, auto-aim,
terrain clipping, mouse inversion,
jet movement,
jet-to-walker simulation, exact backend attenuation, resource semantics,
the rest of the weapon
model, target mesh-part damage,
secondary hit/destruction effects and debris, terrain collision
beyond grounded height following, AI, the mission
beyond the first four-target exercise and its weapon handoff,
campaign, and networking
remain provisional or absent.

Mouse sensitivity is **not** in that list. The slider exists — `RetailOptionsMenu`,
Controller Options row 0 — and `InteractiveSession.SetMouseSensitivity` is its
only consumer, scaling the pointer axis by `sensitivity * 13/3000`. The
untouched default is retail's **compiled `7.0`**, the image's own static
initialiser. What remains unproven is the *runtime mapping at any value other
than the single one that was actually measured*; no run has been captured at a
second sensitivity.

> **Superseded 2026-07-27, recorded here 2026-07-28.** The list above previously
> read "mouse inversion and sensitivity settings other than the copied Steam
> `1.5` baseline". **`1.5` is not a released default or UI-selectable value.**
> It was a copied-options test setting consumed by the retail executable.
> Retail's slider law is `g_MouseSensitivity = (index + 1) * 3.0f` with max
> index `0x14`, so the reachable set is `{3, 6, … 63}` and `1.5` is below the
> floor; it reached the reconstruction from the copied `defaultoptions.bea` those
> runs were configured through, which is persisted run state rather than an
> authored value. Read this pass from the pristine specimen
> `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
> `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`: file
> `0x2254F4` (VA `0x006254F4`) = `00 00 e0 40` = `7.0f`, `0x1D8CC0`
> (VA `0x005D8CC0`) = `3.0f`, `0x1D97C8` (VA `0x005D97C8`) = `0.004333333f`.
> The pointer scalar moved from `13/2000` to `91/3000` in `fed5829b` — aiming
> had been 4.67× too slow at equal hand motion. See
> [`../CURRENT_CAPABILITIES.md`](../CURRENT_CAPABILITIES.md) for the withdrawal
> in full. **Unchanged:** mouse inversion really is still absent, and it stays in
> the list above.

The client switches between the released walker's and jet's exact part
hierarchies and independently animates the exact first-person cockpit. It
decodes Level 100's
version-50 base-world records into 33 visible static instances, 24 mesh types,
and 1,481 pines across four authored mesh variants, while retaining the
separate Target Tank and Warehouse meshes. The
retired synthetic arena boundary, flat plane, and placeholder structures are
gone. Godot uses the released 65×65 eight-step lattice for coarse selections and
camera-selected 4/2/1-step tile grids from the exact tiled HFLD. Selection uses
the recovered height-error score and distance thresholds; topology uses the
released triangle diagonal, all 16 edge-stitch variants, and absolute landscape
coordinates. The local materializer retains the exact sources for Steam's five
logical 512×512 RGB565 caches and independently verifies the initial root texture
from Level 100's `MAPT`/`MMAP`, lighting, structure shadows, and the released
shadow rules over all 1,481 pine placements. Godot updates one cyclic cache per
logical level through that compositor and applies the exact Level 100 detail
texture at both released coordinate transforms, including the rotated
quarter-scale pass, inserts the exact moving cloud-shadow stage with its released
scroll and modulation, and renders the five exact cube-25 sky
faces with `CHFD` fog and lighting values. Terrain, static objects, cockpit,
targets, and water share the released exponential fog color/density path. Static
objects use the released ambient plus opposing sun/anti-sun fixed-function
equation and stage-zero `MODULATE2X`; final color transfer follows Godot's active
renderer contract rather than converting Compatibility output twice. The one
Level 100 base texture flagged for fixed-function texture-alpha blending retains
its lit exterior below transparent texels instead of becoming a cutout; ordinary
alpha-tested foliage remains unchanged.
Deterministic Core embeds the same
hash-verified HFLD, applies Steam's 24.8 fixed-point signed interpolation, and
hashes the player's ground elevation. Godot adapts that Core value for the
player rather than running an independent sampler. The client preserves each
active mesh group's six ordered retail texture slots and decodes the exact
AYA-wrapped textures selected by the Aquila, cockpit, static world, close pine
meshes, and range targets plus the four exact 64×64
textures named by the medium Pulse Bolt descriptor. It also uses twenty-nine
exact HUD textures, including the three released v3 crosshair layers,
uncompressed proportional font atlas, scanner/north sprites, battleline,
four-pose Tatiana/technician portrait/noise treatment, and objective marker. The
observed player route uses Steam's
5.4-unit overlap and delayed dispatch to replace Target Zone 1 with the Firing
Range on that radar. A control and three repeated retail runs then establish the
Firing Range's five-message sequence, current-weapon highlight, four objective
targets, temporary player deactivation, and Pulse Cannon-only activation. The
client uses the exact seventeen retained English lines and voices through its
Vulcan handoff. A no-fire control and fresh isolated copied-runtime runs then
established the first charge bucket, definition speed `35`, `1.75`-unit released
update, life `6`, total direct-contact damage `1.8`, and four-shot objective
removal for each of the three training tanks; one separate glancing hit removed
`1.0`. Pristine control flow and exact physics records split that `1.8` into
ordered `CRoundDamage 0.8` and immediate `CExplosionDamage 1.0` calls. Core
retains both whole-body stores for Target Tank/Drone instead of collapsing them
into one subtraction.
Two isolated Warehouse repetitions then required twelve normal hits along one
fixed center-aim attack line before terminal objective removal and the same
Pulse-to-Vulcan gate. The explosion call's segmented mesh part remains unknown,
so Warehouse deliberately retains that observed aggregate rather than assuming
both calls select the direct-hit segment. Core implements only those bounded
paths. Godot removes each completed model and radar marker and presents retained
shot, hit, tank-destruction, text, voice, and primary particle layers.
Water reproduces the fixed-function path active on the supported Steam specimen:
its camera-following grid, Level 100 color, two caustic stages, authored
reflection image with the released absolute-world `1/256` transform, sun stages,
the camera-height-scaled alpha-tested sun patch, and both exact shoreline passes
in released order. Steam disables the wave stage for the main grid; the measured
wave animation belongs only to the authored shoreline passes. Its measured caustic phase
and wave scroll advance at `1` radian and `0.06` texture cycles per second. This
does not claim Steam's exact stateful gamut/frustum clipping or bounded terrain
pool exhaustion/reuse order, the inactive optional advanced-water path, dynamic
scene reflection/refraction, or pixel identity outside this bounded pass. The visible-sun
particle, facility destruction,
steep-slope sliding,
actor/structure collision beyond the observed Control Tower and Tank Factory
contact envelopes, exact toe-normal alignment and CMC body sway,
jet-to-walker presentation, general HUD contacts and later state logic, Steam's
dynamic ring texture, full multi-stage mask state and Level 100 influence map,
other radio portraits/video and exact portrait RNG phase, Warehouse
segment-specific health and breakup,
mesh-part damage variation, secondary particles/debris, Target Truck
contact/destruction, Vulcan muzzle sequences and predictive aiming, and the
remainder of the mission remain
unimplemented. The old seeded synthetic targets are gone;
Core and Godot now share the observed retail targets by canonical actor ID and
definition/mesh binding, including dynamically spawned training trucks, plus
the shipped objective marker without adding world-space beacons.

## Verify

Choose the smallest relevant command:

```powershell
npm run test:rebuild-core
npm run test:rebuild-client
npm run run:rebuild-headless
npm run test:rebuild-godot-smoke
```

The headless host loads the checked-in `first-flight.v1.json`, repeats it, and
fails if identical inputs diverge. It reports versioned state and trace hashes;
callers may supply `--expect <trace-hash>` when they own an external expected
result. Files are limited to 8 MiB and one invocation to 100,000 total steps.

The native smoke builds with the pinned engine, enters through cold
click-to-start → Main Menu → level select → Loading → gameplay, runs the bounded
scripted input sequence, and checks the final deterministic state. It then
checks focus/cursor policy, a fresh retry, and return to the same Main Menu with
the Level 100 world released. It writes structured report and log evidence
only; it has no screenshot or visual-parity machinery.

Visual regression is a separate gate. `rebuild/tools/Capture-Frontend.ps1`
captures a plan and scores it against the retail reference through
`tools/score_frontend_capture.py`, folding that verdict into `Status`: a
frontend regression returns `FAIL`, and a run with nothing to score against
returns `UNSCORED` rather than `PASS`. Its thresholds live in
`rebuild/tools/frontend-parity-plan.json` and are regression ceilings, not
parity claims. Reference frames are retail-derived and live under ignored local
paths, so a fresh clone scores nothing.

Read [PROVENANCE.md](PROVENANCE.md) before implementation work. Retail behavior
claims must point to the smallest relevant binary/source/runtime evidence; Core
agreement never re-proves retail.
