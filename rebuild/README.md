# Onslaught Rebuild

Status: early GPL reconstruction lane
Last updated: 2026-07-29. Current startup/frontend, pine-detail, and
mouse-sensitivity claims were re-reviewed. Other sections retain
their narrower dated evidence boundaries.
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
career-name page, a Level 100-only level selector, the mission-briefing and
select-configuration pages, and loading. Loading constructs the Level 100
world; the first-time intro then plays before gameplay activation.
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
separate fast-tree owner adds one camera-facing standing card at every range
and its height-gated horizontal card above the released 20-unit camera/ground
delta. The converted meshes render with
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
Vulcan firing, and most mission behavior remain provisional. The bounded
ground-vehicle owner does retain the released Target Tank and Target Truck
command intents and advances their canonical actor poses from the materialized
waypoint and physics definitions.

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
(retail's `CHOOSE GAME NAME` page, implemented visually and sequentially only —
no save and no career persistence), Options, the Level 100-only selector,
Mission Briefing, Select Configuration, Loading, and the Level 100 intro
cutscene. The
`RetailFrontendScreen` enum in
`rebuild/OnslaughtRebuild.Client/RetailFrontendSession.cs` is authoritative for
that list; read it rather than this sentence when the two disagree.
(*Corrected 2026-07-28: this read "The frontend owns **only** click-to-start,
Main Menu, the Level 100-only selector, and Loading." The word "only" made it a
completeness claim and it was false — five further screens were already declared
and shipping. Nothing was removed; the list was understated.*)
Each launch request makes the host construct a fresh canonical
`InteractiveSession` from the materialized Level 100 actor definitions before
gameplay activation. The frontend does not inspect
`WorldSnapshot.Level100Mission` or own gameplay, save, result, or later
campaign-selection state. `RestartLevel100` returns through the same Loading
edge; `LeaveLevel100ForMainMenu` disposes the active world and returns to the
same frontend shell.
The gameplay pause owner freezes that same deterministic session with zero Core
steps, discards pending gameplay input, pauses the existing Level 100 audio
owner, and routes its cursor through the frontend's sole mouse-mode writer.
Continue resumes after a neutral input sample; Retry and Quit call those
existing lifecycle seams after the audio owner completes its kill-then-Select
exit boundary once. Message Log, Briefing, and the three settings rows remain
visible but disabled until canonical integrated owners exist. The current
opening slice does not synthesize terminal events, rank, kill summary, unlock,
save, or campaign progression. `FrontendAudioCueRequested` is an observation
seam; the existing Level 100 audio owner remains the sole playback owner.

Core currently provides integer positions, opening tutorial/objective state,
reset behavior, ordered snapshots, and versioned SHA-256 state and trace hashes.
Resource and cooldown behavior remains provisional. The bounded three-training-
tank path uses the observed Pulse Cannon gate, continuous-yaw projectile heading,
retail speed, direct-hit damage, and objective removal. Continuous body yaw and
Level 100 objective state are part of the snapshot/hash, and every input axis—including
look—is part of the trace. Walker acceleration is projected through the body's
continuous deterministic yaw; only jet movement retains the older eight-way
approximation.

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
on Level 100's authored start slope. Pulse Cannon rounds use the same yaw/pitch
direction as the crosshair camera and begin at the measured cockpit `Gun`
emitter. Terrain-relative pitch limiting, vertical target collision, auto-aim,
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
contact/destruction, Vulcan ballistics, and the remainder of the mission remain
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
