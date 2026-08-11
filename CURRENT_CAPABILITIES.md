# Current Capabilities

Status: active — what is demonstrated today, and what is not
Last updated: 2026-08-09. RE authority block refreshed to canonical Gen19
(`current_re_authority`; candidate Gen73 is projection-oracle only). Primary WinUI
navigation was rechecked 2026-08-03 against the live shell (includes Cheats).
The 2026-08-01 shell, appearance, Lore, Media, and four-run Level 100 reviews
retain their stated boundaries. Other rebuild and save/patch claims not
re-reviewed by this pass retain their prior boundaries.
Summary: the demonstrated capability of each lane with the measured gap stated
beside it. Every figure here is the value at the commit that wrote it;
re-measure before relying on one.

Onslaught Toolkit has one player-facing preservation app: the WinUI 3 Windows
app. AppCore owns its file and copied-target correctness. Full retail reverse
engineering and the 1:1 Godot rebuild are coequal project outcomes, not
subordinate app lanes; the unshipped CLI and focused tools are support surfaces.

## WinUI toolkit

The primary navigation is Home, Windowed & Mods, Save Lab, Cheats, Media, Lore,
Asset Library, Settings, and About.

> **Updated 2026-08-01.** The order previously read Home, Save Lab, Media, Asset
> Library, Lore, Windowed & Mods, Settings, About — which put the step the Home
> page calls first in sixth position, behind three browse-only pages. Only the
> order changed; no page was added or removed by that pass.

### Shell and appearance

The app carries its own icon (project-authored; see
[`tools/generate_app_icon.py`](tools/generate_app_icon.py)) on the window,
taskbar, and alt-tab.

Appearance follows Windows by default and can be set to Light or Dark in
Settings; the change applies immediately rather than at next launch. Both
palettes are gated for contrast by `ThemeContrastAuditTests`, and a companion
audit fails the build if a theme brush is bound with `StaticResource`, which
resolves once at page load and silently freezes a surface in the theme that was
active when it first appeared.

Home reports what the app has found on the machine — the configured install, the
number of detected save/options files, and whether media is ready to browse —
rather than describing those capabilities in the abstract.

Game-install detection reads Steam's own recorded location from the registry
(`HKCU\Software\Valve\Steam` `SteamPath`, and the `Valve\Steam` `InstallPath`
values under `HKLM`) before falling back to the previously hardcoded
`C:`/`D:`/`E:` candidate list, then scans `libraryfolders.vdf` as before. The
test-only `ONSLAUGHT_GAME_DIR_CANDIDATES` and `ONSLAUGHT_STEAM_ROOT_CANDIDATES`
overrides still short-circuit every built-in candidate, including the registry.

### Lore

The Lore reader renders documents as native WinUI content parsed from Markdig's
AST, not in an embedded browser. Text is selectable and exposed to assistive
technology, headings carry their semantic level, tables render as real tables,
and the reader follows the app theme.

> **Superseded 2026-08-01 — a defect, not a capability change.** The reader
> previously hosted a `WebView2`. It displayed **nothing** for any document: the
> HTML was written correctly, navigation reported success, and a live renderer
> process held the page, but no pixels reached the WinUI surface and a full
> window resize did not recover it. The native reader replaced it. `WebView2`
> remains an indirect dependency of the Windows App SDK; the app no longer
> references or uses it.

Packaged lore documents have the repository's maintainer header block
(`Status` / `Last updated` / `Summary`) removed at pack-build time, so a reader
opens on the article rather than on repository bookkeeping. The tracked source
files keep the block.

### Save Lab and Game Options

- Analyze existing `.bes` career saves and `.bea` options files.
- Write a separate save copy with supported mission, link, Goodie, rank, and
  kill-count changes.
- Write one selected displayable Goodie state directly to one `.bes` file in a
  verified app-owned Safe Game Copy; in-place and installed-tree output remain
  blocked.
- Edit supported startup, audio, controller, and binding values in a copied
  `defaultoptions.bea`.
- Compare files and inspect bounded structural details.

AppCore starts from an existing retail-generated baseline, preserves file size
and unknown bytes outside selected regions, stages output beside the
destination, and verifies the committed bytes. It does not synthesize saves.

One bounded Steam-retail A/B proved Goodie `2` only. Starting from a real
`10004`-byte save with state `0`, the focused WinUI/AppCore path wrote state `2`
at dword `0x1F4E`; only byte `0x1F4E` changed and every other byte, including
reserved Goodie slots `233..299`, remained identical. The source hash was
unchanged. Identical verified copied executables loaded Goodies `1..3` as
runtime states `1,0,0` in the control and `1,2,0` in the edit. At wall
coordinate `(2,0)`, the retail mapper selected ID `2`; the edited cell was gold,
exposed `Unlocked! Col. Chuck Kramer`, and transitioned from live state `2` to
`3` when opened. The tested `Maladim` name enables the unrelated retail
cheat-index-3 God-menu gate, but the Goodies process consults only cheat indices
`0` and `5`. The retail load path also mirrored each selected save buffer to
that copy's `defaultoptions.bea`. This proves one load, wall-display, and live
state-transition path on the tested Steam specimen, not a generic no-cheat
environment, other Goodie IDs, unlock rules, releases, or disk persistence
after opening the item. Save staging continues to verify the app-owned profile
and executable, but does not treat retail's mutable `defaultoptions.bea` mirror
as immutable staging evidence; guarded launch validation remains strict.

### Windowed & Mods

- Treat the installed game and original `BEA.exe` as read-only sources by
  default; patching them is opt-in and takes a verified backup first.
- Create an app-owned playable safe game copy.
- Plan, apply, restore, and verify expected-byte catalog patches on that copy.
- Launch and stop only the copied-game process started by the app.
- Keep BEA.exe-only technical copies separate from playable profiles.

Enhanced Copy applies the complete 28-region widescreen correction, selects
the retail 16:9 option, uses the supported `-res 1600 900` windowed baseline,
and writes mouse sensitivity `0.1` in the copy. A controlled Level 100 launch
reported live dimensions `1600x900` and aspect terms `0.5625`, `1.333333`, and
`1.777778`. This demonstrates the supported Steam specimen on the tested
machine; other resolutions, drivers, wrappers, menus, cutscenes, and
split-screen layouts are not implied.

The modern-input defect reproduced here was an internal preset disagreement:
WinUI instructed Steam Input users to lower retail mouse sensitivity to its
minimum while Enhanced Copy wrote `2.25`. Enhanced Copy now writes and reads
back `0.1`, **which is AppCore's own lowest preset, not a retail minimum**
(`GameProfileControlOptionsService.MinimumMouseLookSensitivity`). This proves
the copied option and live global, not subjective mouse feel or
physical-controller behavior.

> **Superseded 2026-07-27 — over-claim withdrawn.** This previously read
> "Enhanced Copy now writes and reads back **the retail minimum `0.1`**". `0.1`
> is not a retail minimum and not a retail value. Retail's own selectable
> minimum is **`3.0`** — the slider is `(index + 1) * 3.0f`, giving `3, 6, … 63`
> — and its compiled default is **`7.0`**. `0.1` is one of AppCore's four
> presets (`0.1`, `1.5`, `2.25`, `3.0`). The demonstrated capability is
> unchanged: AppCore writes the value into a safe copy and reads it back. Only
> the attribution of `0.1` to retail was wrong. This exact line was named as an
> unactioned over-claim by the project's own adversarial pass
> (`local-lab/agent-notes-2026-07-27/adverse-settings.md`, F7).

The bounded retail-content go/no-go also passed for one English mission line.
WinUI can opt a safe copy into a fixed-size replacement of Level 100 text ID
`4422830` (`TUTORIAL_01`) in `data/language/english.dat`. AppCore requires the
supported Steam table hash and exact original UTF-16 bytes, preserves file
length, writes an original backup, records both hashes, and revalidates them
before launch. A controlled copied Level 100 run rendered the unique
`TOOLKIT MOD ACTIVE`
objective line. This proves one direct localization-table edit, not arbitrary
language import, loose mission-script loading, texture replacement, AYA
repacking, or a general mod format.

The bounded gameplay-modding go/no-go also passed for one compiled Level 100
mission command. WinUI can opt a safe copy into rebuilding the supported
`data/resources/100_res_PC.aya` so the initial `DisableFlightMode` call becomes
`EnableFlightMode`. AppCore requires the exact original archive and payload,
changes one byte in the verified `LevelScript` instruction stream, preserves an
original backup, round-trips the four-member archive, and revalidates both
payloads before launch. With the same transform input, the original archive hit
the retail rejection return while the modified archive reached the walker-to-jet
state write; a WinUI-created copy reproduced the accepted result with
`flight=1`. This proves one exact compiled-command substitution, not loose
`.msl` loading, normal tutorial progression, a mission compiler/editor, or a
general AYA repacker.

That controlled setup now also owns one rebuild behavior. One clean and two
modified fresh copies bound Transform through copied `defaultoptions.bea` and
delivered retail action `0x21` to player one's BattleEngine. The control stayed
in raw walker state `2`; both modified runs repeated `2 → 1 → 3`, with the
raw transition lasting 535.359–537.249 ms. Deterministic Core maps only that
walker-to-jet state to 16 ticks at 30 Hz. A later clean control and two fresh
modified repetitions established the separate released presentation: the
renderer swaps to the 54-part jet hierarchy at transition entry, external
`walktofly` runs for about 1.24 seconds, and the 21-part cockpit completes its
independent transition after about 1.14 seconds while the first-person camera
remains attached. Godot now consumes those exact hierarchies, authored frames,
and takeoff/in-flight PCM records without extending Core's state duration.
Jet-to-walker presentation, exact sound mixing, resources, weapons, and flight
dynamics remain unproven.

The patch catalog's original/replacement bytes and copied-target rules are
automatically checked. A byte-correct patch is not automatically proof of its
visible or gameplay effect. Windowed startup, expanded mode enumeration, card-ID
handling, graphics defaults, colors, Goodies display, pause binding, version
text, and free-camera experiments therefore retain their individual stability
labels and evidence notes.

The local split-screen action currently supplies the game's existing launch
arguments to a safe copy. It is not proof of active P2 input and does not add
online play. Host/Join, matchmaking, and new networking are unavailable.

### Media, assets, and Lore

- Media reads supported audio/video from a selected local game path. A load
  failure now states its cause where the user can see it; the reason previously
  went only into a permanently collapsed panel.
- Cutscenes are listed by number (`Cutscene 01`..`Cutscene 33`). The game ships
  no titles for them.

> **Withdrawn 2026-08-01 — fabricated content removed.** The catalog carried 33
> invented story titles ("Tatiana Introduction", "Boss Battle", "Plot Twist", …)
> and presented them to users as fact. They appear nowhere in the game, the lore
> library, or the evidence store; they existed only in `MediaCatalogService` and
> its own test. A regression test now refuses any cutscene label other than the
> numbered form until a real title is demonstrated. The five retained
> main-video names each expand an abbreviation the file itself carries
> (`LT` = Lost Toys, `FE` = front end, `TWIMTBP` = NVIDIA's campaign). The sixth,
> `UsTheMovie` → "Credits Video", asserts a role rather than expanding a name and
> is retained only because it is wired into receipt-bound evidence acceptance;
> it is recorded as unconfirmed.
- Asset Library opens an existing generated catalog and previews supported
  PNG/FBX metadata, linked textures, and bounded wireframes. It has no asset
  importer, repacker, animation/bone pipeline, or material-package workflow.
- Lore searches and renders the canonical articles under [`lore/`](lore/_index.md)
  with tree navigation and Back/Forward/Home history. Portable builds generate
  a reader pack from that single source rather than tracking a mirror.

`tools/aya_archive_inventory.py` is a working read-only AYA structure scanner.
The legacy AYA export bridge still depends on untracked local upstream binaries,
so a clean checkout does not prove end-to-end PNG/FBX export.

## AppCore and CLI

`OnslaughtCareerEditor.AppCore` owns save/options parsing, unknown-byte
preservation, guarded publication, copied-target enforcement, patch plans,
media discovery, asset-catalog reading, and Lore loading.

`OnslaughtCareerEditor.Cli` is a small, source-only maintainer adapter for
AppCore save, options, patch, and catalog operations. It is built with the
solution but is not shipped beside WinUI and is not a gamer-facing product or a
generic automation workbench.

## Reconstruction

[`rebuild/`](rebuild/README.md) is a GPL-3.0-or-later, source- and RE-informed
reconstruction lane. `OnslaughtRebuild.Core` owns fixed-step simulation,
snapshots, state hashing, and command-tape replay without presentation,
filesystem, clock, process, network, or GPU dependencies.

The Godot Level 100 Opening Slice now uses all 513×513 unit-lattice positions
decoded from the released tiled Level 100 HFLD, plus the Federation walker/jet,
all 33 visible static objects in the
released Level 100 base-world records, all 1,481 Steam-instantiated pines, the
released active-path water grid and authored shoreline, three training tanks,
and target Warehouse
geometry. Core starts at the released
player-one heading and owns the authored player ground elevation plus the
machine-observed objective and player gates through the first Firing Range
exercise. The prior synthetic arena boundary, flat plane, and
placeholder structures are gone. Terrain, retained meshes, facilities, sky,
light, camera, and Core-relative positions now share the released
`(X, Y, Z-down)` → Godot `(X, -Z, -Y)` mapping. The opening view follows the
released four-point Level 100 pan around the exterior Aquila, switches to the
retained first-person cockpit and HUD after 5.95 seconds, and reaches the retail
playing-camera state after six seconds. Level 100's script keeps the player
deactivated beyond that camera handoff: Core enables movement/look only when the
released power flag changes at tick 1000 relative to the pan start. The Firing
Range later deactivates the player, then re-enables it with only the Pulse
Cannon; flight remains disabled. Two fresh
uninterrupted safe-copy runs repeated the same camera endpoints, six-second
length, handoff, and playing-state boundary. A clean Level 100 control and two
fresh repeated safe-copy runs also establish the walker's acceleration,
equal forward/strafe cap, frictional
coast, and inertial body turning. The client renders Core's continuous yaw
rather than an eight-direction visual snap. Two further repeated runs establish
BattleEngine-owned vertical aim at the authored start: exact first input and
`0.8` coast response, stable pitch endpoints `+0.532123` and about `-1.0912`,
and a Pulse Cannon direction matching the crosshair-derived yaw/pitch vector
within `0.00119` per component. Godot now pitches the retained retail cockpit
and camera and renders the resulting three-dimensional Core projectile path.
It also follows the released input ownership: `WASD` and arrow keys move the
Battle Engine, while mouse or trackpad motion owns look and aim. At retail's
compiled default sensitivity `7.0`, the Godot adapter preserves pointer
magnitude, applies
the released centered-offset mapping and recentering rate, and feeds Core's
released walker yaw/pitch response. Other sensitivity settings,
inversion, and jet mouse response are not yet claimed.

> **Superseded 2026-07-27.** This previously read "At copied Steam sensitivity
> `1.5`". **`1.5` is not a retail value at all.** Retail's slider law is
> `g_MouseSensitivity = (index + 1) * 3.0f` with max index `0x14`, so the
> selectable values are `3, 6, … 63` and **`1.5` is below the floor a player can
> reach**. The compiled image default, before the slider is ever touched, is
> `7.0` — itself not reachable from the slider either. All three constants were
> read from the **pristine** specimen (sha256 `74154bfa…`), not the installed
> executable: `0x006254f4 = 7.0`, `0x005d8cc0 = 3.0`,
> `0x005d97c8 = 0.004333333`. The old pointer scalar `13/2000` is exactly
> `1.5 × 13/3000`; it is now `91/3000 = 7.0 × 13/3000`, so aiming had been
> 4.67× too slow at equal hand motion (`fed5829b`).
Core retains the previously measured 16-tick walker-to-jet transition, but the
clean opening's flight gate keeps it unavailable until later tutorial
progression is implemented. The walker, jet, and first-person cockpit now load
directly from their exact released AYA files as 63-, 54-, and 21-part
hierarchies with 54, 58, and 10 material surfaces. The external jet and cockpit
advance through their separately timed authored `walktofly` frames after the
released transition-entry mesh swap, then select looping `fly` frame 0. The
exact takeoff effect and in-flight loop begin at that same boundary. The
walker's twenty leg-chain parts consume four
deterministic Core foot contacts. Core reproduces the released diagonal step
scheduling, 400-phase-unit-per-second swing, 0.4-unit lift, and exact Level 100
heightfield contact; Godot selects each leg's `LegMotion` frame by required
root-to-foot extension rather than replaying one synthetic gait cycle. The 24
non-tree static-world mesh types, four `pinesnow` variants, and two target types
remain bounded static conversions. The 1,481 pine placements use exact released
meshes inside retail's **authored 30-unit** horizontal mesh-quality boundary —
the image's own static initialiser, which is the Geometry detail = Medium arm —
and exact six-view atlas geometry beyond it. A separate fast-tree owner adds its always-on
camera-facing standing card and its camera-height-gated horizontal card. Its
standing view uses a manifest-pinned phase-0 ordinal cycle only as a
deterministic reconstruction; all 1,481 assignments and their four counts are
checked. Steam's exact owner allocation/view sequence and address-selector
phase remain unresolved. The
converted static-world and target OBJ front faces are adapted to
Godot's clockwise winding instead of exposing
interior/back faces. Aquila and exterior meshes render from exact locally
materialized AYA-wrapped textures. Static object
shading uses the released PC ambient plus opposing sun/anti-sun lights and
stage-zero `MODULATE2X`, not invented Godot metallic/roughness values. One no-input control and two
fixed-yaw retail repetitions per facility establish circular walker contact only
for the Control Tower and Tank Factory: inward motion is removed, while tangent
motion slides around the tower. Core consumes those two observed envelopes; it
does not claim general mesh collision.

> **Superseded 2026-07-27, recorded here 2026-07-28 — the pine mesh-quality
> boundary.** The paragraph above previously read "The 1,481 pine placements use
> exact released meshes through the **selected high-quality 70-unit** horizontal
> boundary and exact six-view atlas geometry beyond it." **`70.0` was this
> workstation's `defaultoptions.bea`, which is persisted run state, not an
> authored default** — precisely the lab artefact `GOAL.md`'s defaults rule
> exists to keep out of shipped behaviour. The released out-of-box arm is
> **Medium, not High**. `0x004DD6B0` dispatches Geometry detail to three arms
> writing `10.0` / `30.0` / `70.0`, and the image's own static initialisers are
> uniquely the middle arm: file `0x2321A0` = `00 00 f0 41` = `30.0f`, with
> `0x231E88` and `0x230E0C` both `1.0f`. Read this pass from
> `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
> `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`,
> 2,506,752 bytes — the **pristine** specimen, not the deliberately patched
> installed `BEA.exe`. Corrected in code on 2026-07-27 (task #137); the offset
> table and the proof that `defaultoptions.bea` is run state are in
> [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md). **Unchanged:** everything
> else in that sentence — the placement count, the exact meshes inside the
> boundary, and the six-view atlas geometry beyond it.

Twenty-nine exact released HUD textures — **the count the client loads and
composes**, not the count the asset materializer retains, which is larger and is
stated in `rebuild/PROVENANCE.md` — including Font13PS and the three v3
crosshair layers, replace the prototype overlay for the bounded threat circle,
lower-left scanner/weapon instrument, lower-right battleline/portrait,
active-objective markers, and conditional message panel. All fifty-one
English tutorial messages now use
exact released strings, shipped Ogg/Vorbis voices, proportional font metrics,
the native 120-pixel message composition, and four released
Tatiana/technician portrait poses. Repeated retail runs matched every retained opening boundary
within 50 ms, then repeated Target Zone 1's 5.4-unit overlap, delayed objective
swap, and `TUTORIAL_02` dispatch. One control and three accepted Firing Range
runs then repeated the same five-message sequence, current-weapon highlight,
four objective pointers, temporary player deactivation, and Pulse Cannon-only
activation. A no-fire control and fresh isolated copied-runtime runs then
established the same bounded lifecycle for each of the three training tanks:
first active charge bucket `10`, round speed `35`, movement `1.75` per released
20 Hz update, starting life `6`, direct-hit damage `1.8`, and
destruction/objective removal on shot four; one separate glancing hit removed
`1.0`. Two further isolated repetitions then removed the Warehouse objective
after exactly twelve normal hits along one fixed center-aim attack line and
repeated the released player-off,
Vulcan-message, Pulse-off/Vulcan-on handoff. That observation remains a bounded
runtime comparison; Core now uses the released object's 28-segment controller
rules rather than encoding twelve hits as generic Warehouse health. Godot
removes each completed objective and radar marker,
uses the measured cockpit `Gun` emitter, and consumes exact released round,
impact, tank-destruction, sound, text, and voice assets for the bounded
presentation. The exact initial root terrain now includes the released macro
blend, structure shadows, and pine-shadow rules over all 1,481 placements. Its repeating Level
100 detail texture, cube-25 sky, fixed-function
ambient/sun/anti-sun lighting, exponential fog, and renderer-correct final color
transfer replace their earlier placeholders. Copied-runtime state confirms the
released Level 100 terrain path; static analysis fixes its stage order to plain
macro/detail modulation followed by `MODULATE2X` cloud/rotated-detail stages. The
one Level 100 base texture whose released `CTexture` record selects
texture-alpha blending now preserves its lit exterior under transparent texels
instead of exposing the facility interior. Water now uses the
released camera-following 25×25 grid, exact Level 100 height and color, two
animated caustic stages, authored `reflection00` imagery, sun-reflection stages,
and both exact `SURF` shoreline bands. Its active reflection stage uses the
released absolute-world `1/256` transform rather than the inactive advanced
path's animated half-scale transform. Steam disables the wave stage before the
main grid draw; the client applies its measured animation only to the authored
shoreline passes, alongside the camera-height-scaled alpha-tested sun patch,
late additive shore pass, released pass order, and measured animation rates. This reconstructs
the bounded active fixed-function path observed on the supported Steam specimen;
it does not claim the inactive advanced path, dynamic scene reflection/refraction,
or general renderer pixel identity. The detail texture uses the released
identity and rotated quarter-scale transforms and observed modulation modes; the exact
moving cloud-shadow texture now uses the released scale, scroll, and modulation.
Core's projectile path now consumes canonical-registry actor identity,
hash-verified mesh binding, active state, full three-dimensional pose/basis and
velocity. The released medium-pulse swept sphere uses BBOX only for broadphase
and deterministically millimetre-quantized projected mesh
topology for contact. Target Tanks retain their four-hit direct
path; Warehouse contacts now drive the evidenced extent-weighted 28-segment
state, `5.0` core multiplier, core-child/strict-30% terminal tests, and
`Hit`/dying/died facts consumed by the released mission scripts. Segment and
typed effect state is deterministic and hashed. Godot consumes the ordered
Pulse-impact and terminal effect events, including their existing audio and
target-destruction presentation. It still removes the complete target at
terminal; detached Warehouse parts, rubble, and retail-random secondary debris
are not yet presented.
Walker acceleration now follows Core's
continuous body yaw; the bounded projectile path shares its yaw and vertical
pitch while jet
translation retains the older eight-way approximation. The slice does not
yet reproduce Steam's dynamic 1/2/4-step terrain patch topology, steep-slope or
wire the available actor contact path into walker movement beyond those two
observed facility envelopes, exact toe-normal alignment or CMC body sway,
resolved Warehouse rubble trajectories,
mesh-part damage variation, retail-random secondary particles/debris, the
three moving truck targets, Vulcan firing, the rest of
the mission, AI, the
remaining weapon roster, facility destruction,
the inactive optional advanced-water path and dynamic scene reflection/refraction,
jet-to-walker presentation, Steam's dynamic
HUD ring and full multi-stage mask/influence-map implementation, general
contacts, other portraits/video, and exact portrait RNG phase,
later mission audio, campaign,
networking, or the rest of the transform model. The camera slice does not yet
reproduce terrain-relative pitch limits, terrain occlusion, camera shake, or later
scripted cameras. The old seeded synthetic targets are gone; Core and Godot
share the four observed retail targets. HUD markers use the shipped radar asset,
not world-space synthetic beacons.
Core embeds the exact Level 100 HFLD, applies Steam's released fixed-point
height sampler, and hashes the resulting walker ground elevation. Godot adapts
that value for the player; static-world objects and projectile effects remain
presentation-grounded. The observed route did not exercise a steep-slope flag,
body tilt, or nonzero vertical velocity, so those behaviors remain outside the
demonstrated slice.

**None of the above is a parity claim, and the measured gap is large.** As of
2026-07-27 the best Level 100 gameplay frame scores **22.55% of pixels
materially different from retail, mean channel distance 7.6**, against a
retail reference at t0+25065 ms.

The startup and frontend path is further off. FEP_MAIN's settled window measures
**15.14%** full-frame, its reveal window **19.49%**, and its **entry frame
7.53%**. Only the per-region **measured** values are recorded in
`rebuild/tools/frontend-parity-plan.json`; the regression ceiling is **derived**
from each by `tools/score_frontend_capture.py` as `min(measured + marginPp, 100)`
using the plan's single `_measurementProvenance.marginPp` of `2.0`, and is
deliberately **not stored**. Several regions are tens of percent off retail: at
the settled window `title-logo` measures 29.48% and `bg-emblem-topright` 19.92%,
and at the reveal window 31.83% and 22.97%. Those ceilings say "do not get
worse"; they are not parity numbers, and quoting one as a parity number is a
misreading. **Five** frontend pages are deliberately ungated and reported
`UNSCORED`, **for two different reasons**: `FEP_DEVSELECT` and
`FEP_LEVEL_SELECT` because retail's own two runs disagree (by 5.8–44.2% and
9.6–62.5% material respectively), so no improvement below that is measurable;
`FEP_MISSION_BRIEFING`, `FEP_SELECT_CONFIGURATION` and `FEP_LOADING` because
there is **no second retail run at all** in the no-skipfmv set to form a noise
floor from.

> **Superseded 2026-07-27.** The paragraphs above previously read: "the best
> Level 100 gameplay frame scores **23.06% of pixels materially different from
> retail, mean channel distance 7.85**" and "FEP_MAIN's settled window measures
> **15.14%** full-frame, its reveal window 22.35%, and its **entry frame 71.47%**
> — retail staggers the page's build-up and **we draw it all on frame 0
> (tracked)**" and "**Three** frontend pages are deliberately ungated **because
> retail's own two runs disagree**".
>
> Four corrections, all landing the same afternoon the original was written:
>
> 1. **Gameplay full frame is 22.55% / meanD 7.6.** Trajectory 23.47 → 23.99 →
>    23.32 → 22.55.
> 2. **FEP_MAIN entry is 7.53%, not 71.47%; reveal is 19.49%, not 22.35%.**
>    Settled (15.14%) and `title-logo` (29.48%) are unchanged.
> 3. **"We draw it all on frame 0" describes a defect that was fixed**, by
>    `8618e773` — the main menu now builds up over the released 50-frame
>    transition recovered from the shipped bytes, which is what produced the
>    entry-frame drop in (2). The sentence is deleted rather than amended,
>    because there is no longer a stagger gap to describe.
> 4. **It is five ungated pages, not three, and the single stated reason covered
>    only two of them.** This one was wrong when written, not merely stale —
>    `frontend-parity-plan.json`'s `unscored[]` has carried five entries with two
>    distinct `reason` strings throughout.
>
> **Caveat on (2) — CLOSED 2026-07-28.** It read: "`frontend-parity-plan.json`
> still stores the pre-`8618e773` `measured` values of 71.47 @entry and 22.35
> @reveal, because `8618e773` states 'Ceilings are NOT re-derived here.' The JSON
> and the figures above will therefore disagree until the ceilings are
> re-derived." They no longer disagree. The plan was re-derived at `432c53f7`
> from a production capture off a clean worktree; **17 of its 30 stored numbers
> were stale**, the worst by 99.72 points. The `@entry` ceiling had been 73.47
> against a real 7.53 — nine times loose, incapable of failing. See
> `local-lab/PARITY-GATE-REPAIR-2026-07-28.md`.

> **Superseded 2026-07-28 — where the ceilings live.** The paragraph above
> previously read: "Its regression ceilings are recorded in
> `rebuild/tools/frontend-parity-plan.json` beside the measured value each was
> derived from, and several are tens of percent wrong — `title-logo` alone
> measures 29.48%." **The plan no longer stores ceilings at all.** It holds
> `measured` per region plus one global `_measurementProvenance.marginPp`, and
> the ceiling is derived at load time by `tools/score_frontend_capture.py`, whose
> own docstring is the canonical statement of the reasoning: "The ceiling is
> derived rather than stored because it was briefly both" — the plan had carried
> 30 `regressionCeiling` values, every one exactly `measured + 2.0`, and two
> copies of one fact drift. Verified 2026-07-28 by parsing the plan at HEAD and
> in the working tree: no `ceiling` key in either, `marginPp` `2.0` in both.
> **Unchanged:** the four figures themselves, and the fact that several regions
> are tens of percent off retail.

These numbers move, and they moved several times on 2026-07-27 alone. Treat any
figure here as the value at the commit that wrote it, and re-measure before
relying on one — `tools/score_frontend_capture.py` and
`tools/pair_gameplay_capture.py` are the instruments, and the frontend gate will
now FAIL on a regression rather than reporting a healthy capture as a pass.

**The current outcome comes from four distinct deterministic runs; combining
them would claim a client or human path that does not exist.**

The cold-start client/Core harness visits startup, logo, montage, splash,
click-to-start, main menu, New Game, level select, briefing, configuration
select, loading, and gameplay in released order. Driven through the client input
adapter, that same cold first career **reaches `Won`**, through
`event("Reached Target Zone 4")` and with failure reason `None`. It gets there
on the released **sub-40% hull abort branch**: it destroys **18 of the 22**
targets — three Target Trucks, six Moving Targets, three Airborne Targets 1, two
of six Airborne Targets 2, plus `Target Tank 2`, `Target Tank 3`,
`Target Warehouse` and `Target Tank #23` — trips `Abort Airborne Drones` at
t6732 with 5,700 of 20,000 hull, and leaves primary objective 4 `Failed`.

A second, direct-Core cold run applies the same pointer/integer-pixel
quantisation as the client path. It has the same terminal outcome and tick,
state hash, and pose trace as the client/input-adapter run, so nothing in that
result is evidence of an additional frontend or `InteractiveSession` defect. A
third, **unquantised** direct-Core cold-career control also reaches **`Won`**
and does the whole job: **all 22 destroyed**, all six wave-2 drones, the abort
poll never fired, objective 4 `Complete`. The four targets the client arm loses
are therefore lost to the whole-retail-pixel look quantum, on a beat that is
chaotic at finer than that quantum. All three results are asserted by
[`rebuild/OnslaughtRebuild.Core.Tests/Level100ColdStartTests.cs`](rebuild/OnslaughtRebuild.Core.Tests/Level100ColdStartTests.cs).

A fourth, returning-player direct-Core run reaches `Won` with the four
`SLOT_TUTORIAL_*` values already saved; it does not traverse the frontend or
client adapter. It also wins on the abort branch, with three of the six wave-2
drones down. That evidence is
[`rebuild/OnslaughtRebuild.Core.Tests/Level100FullChainTests.cs`](rebuild/OnslaughtRebuild.Core.Tests/Level100FullChainTests.cs).
None of these is a human or automated native-Godot end-to-end proof.

**Beat 9's kill count is chaotic and these figures are the 2026-08-01 values.**
The `WaterLoss` that used to end the cold runs was fixed by the ferry
hand-off clearance term; the wave-2 counts then moved again when the vertical
datum (#154) and the look-response table (#161) landed, each of which flipped
one career and not the other. `Level100ChainAutopilot.ErrorPole` carries the
measurement showing single-term changes moving this count between 0 and 6. Read
the counts as the value at the commit that wrote them, and the `Won` outcomes
and the Target Zone 4 dispatch as the stable claims.

**There is no remaining ferry loss.** `NavigateToZone` used to leave jet mode
within 20 m of the target volume regardless of what was underneath, and on the
ferry to Target Zone 4 that point is open water, so the run ditched. An altitude
term on the hand-off — `Level100ChainAutopilot.ZoneHandoffClearanceMillimeters` —
fixed it, and [`Level100FerryLandingTests`](rebuild/OnslaughtRebuild.Core.Tests/Level100FerryLandingTests.cs)
now asserts zero `WaterLoss` across a twenty-run one-permille sweep and carries
an adverse control that reinstates the defect and drowns. **The water rule
itself was not touched**: it is a byte-faithful port of `BattleEngine.cpp`
:1259-1262, pinned at water + 200 mm two independent ways in the same file. A
naive water-landing *guard* remains **tried and measured worse** and is
deliberately not restored.

The terminal **tick and hull are recorded but not gated**. The test writes them
to its log rather than asserting them. Treat both as re-measurable, not as
pinned facts. The test summary states the same four-run boundary as its
assertions.

> **Superseded 2026-08-01.** The two paragraphs above previously said the cold
> runs still ended `Lost` / `WaterLoss` on the flight home at `t17699` with
> roughly 10,700 of 20,000 hull, and that the client arm destroyed all 22
> targets with objective 4 `Complete` and the abort poll never firing. The
> ferry loss was fixed on 2026-07-31 by the hand-off clearance term; the
> wave-2 counts moved on 2026-08-01 with the vertical datum and the
> look-response table. Both are asserted at their current values in the two
> test files named above.

> **Superseded 2026-07-28 — every load-bearing clause of the paragraph these
> three replaced is now false.** It read: "on a cold career the same sequence ends **`Lost` /
> `TutorialBroken` at tick 5051**, at full hull 20000/20000, with objective 4
> never reached. The cause is the career premise rather than the join: a
> cold-career control with no client involved loses identically. The tutorial
> lectures shift `Activate Static Targets` by +1338 ticks while the trucks drive
> their authored routes regardless, so `TargetTruck1.msl`'s `died()` case FALSE
> posts `Broke Tutorial`. The returning-player run cleared that margin by 36
> ticks — 1.2 released seconds."
>
> **It was accurate when written.** `t5051` was the joined client run and
> `t4978` the no-client control — two different runs, both correctly recorded at
> the time (`local-lab/agent-notes-2026-07-27/end-to-end-run.md`, lines 14, 18
> and 43). Three of the changes are **asserted** in
> `Level100ColdStartTests.cs`: the failure reason is `WaterLoss`, not
> `TutorialBroken`; objective 4 **is** reached and `Complete`; and the control
> does **not** lose identically — it reaches `Won`, which inverts the old
> sentence's conclusion about the career premise. The fourth, that hull is no
> longer full, is **recorded but not asserted** — it appears in the test's own
> comment and in its log output, not in a gate.
>
> **Unchanged:** the two-halves framing above. `Won` as a returning player and
> `Lost` on a cold first career are both still current, under different career
> preconditions. The 36-tick margin figure is dropped rather than restated —
> it described the returning-player run against a guard the cold run no longer
> trips, and it lives in a test comment rather than an assertion.

> **Superseded 2026-07-27.** This section previously read: "`Won` is likewise not
> a full clear. The observed route to the level's `Won` state runs through the
> **released ABORT branch**: the LevelScript's sub-40% hull poll posts `Abort
> Airborne Drones`, which retires the airborne phase with its own dialogue and
> score penalty. That is the released script doing what it was written to do, not
> the tutorial completed on its intended path."
>
> That was accurate when written and was superseded twice the same day. First by
> `a923d157`, which cleared beat 9 on the intended path — the unlock was not the
> mid-beat ground recharge that had been named as the blocker, but the discovery
> that a stick position is a **rate** demand behind a five-tick lag, not an angle
> demand. Then by `b9e1ae50`, which joined the frontend and the beat chain for
> the first time and established the cold-first-career result above.
>
> **Do not compress this to "it reaches `Won`", and do not compress it to "it
> does not reach `Won`".** Both are current, under different career preconditions.
> `GOAL.md` and `developer_state.json` carry the same two-halves phrasing.

The current source tree and release packages do not include retail game assets
or their conversions, other than two registered screenshots used for the app's
own Home and About surfaces — pictures of the game running rather than files
copied out of it. They are listed in
[`reverse-engineering/project-meta/attribution.md`](reverse-engineering/project-meta/attribution.md)
and the allowance is stated in [`AGENTS.md`](AGENTS.md).
The rebuild materializes the exact currently consumed slice
from a user-provided supported retail installation into ignored local paths.
The remaining asset gap is technical integration and format fidelity.
Read [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md) before changing this lane.

## Reverse engineering and proof campaign

**Current replay authority (2026-08-09):** read `developer_state.json` →
`current_re_authority` before quoting generation or grade counts. Do not select
the historical Gen10 or candidate Gen73 roots by generation number, ledger
equality, or self-derived pins.

| Metric | Canonical Gen19 |
| --- | ---: |
| Authority generation | **19** (lineage `incident-20260806-recovery-v1`) |
| Functions | **8126** |
| C1_CANDIDATE_PARTIAL | **217** |
| C2_BOUNDED_RUNTIME | **7** |
| function_semantic OPAQUE | **7902** |
| contract_C0_OPAQUE | **14021** (second opacity axis) |
| OPEN residual | **17** |
| REBUILD_READY | **0** |
| complete_RE | **false** |
| READY / reducer | `f83dbb6e…ab9a` / `151acbe5…f3e2` |
| Next valid generation | **20** |

Generation 11's post-loss closure accounts for every Generation-73 candidate delta without
making that candidate a parent. It readmits 935 names, 216 bounded C1 claims,
and 6,082 residual terminalizations; preserved 20 police-open residuals, seven
name-only wrappers, and the unsupported NearClone quarantine. Generation 12
then admitted bounded Damage/Hit field-write contracts; Generation 13 advanced
ApplyDamage from C1 to C2 only for its replicated 1,000-damage zero-shield path
and mapped the exact overkill vector to one focused rebuild test. Generation 14
then closed one of those residuals as the exact consumer-bound dispatch-data
partition adjacent to `CTokenArchive::ReadNextToken`. Generation 15 closes a
second residual by proving the exact Mission-native `IScript__SetPos` function
between two NOP ranges, leaving 18 open. Its separate live Ghidra promotion
added one name/signature/comment with a distinct readback while preserving the
executable bytes, instructions, data units, and references. Generation 16
advances that same SetPos entity to bounded C2 after two independently staged
GetPos → SetPos → GetPos treatments and three controls, and carries the observed
position-copy behavior into a focused partial rebuild implementation/test. The
complete internal write set, other receivers/vectors, side effects, persistence,
and failure paths remain open. Generation 17 then admits only one non-null,
sole-matching-node `CBattleEngine::LockHit` removal path from retained evidence;
null, absent, multi-node, free-head, destructor, return, identity, and rebuild
questions remain open. Positive
shields, return pairing, death/effect ordering, and alternate paths remain open.
Generation 18 adds an exact static `CTokenArchive::ReadNextToken`
parser/corpus/factory/direct-writer contract at C1. Its runtime and refuter
verdicts remain `UNSCORED`, runtime replays are zero, malformed/allocation/
overflow and named-token-32 paths remain open, and the rebuild is still partial.
Generation 19 adds the exact UnsetObjective 3-byte NOP / 13-byte wrapper /
3-byte NOP partition and a C1 static conditional-call/bit-clear contract.
Retail runtime, opaque callee `0x004E5BD0`, HUD/lifetime behavior, and complete
rebuild parity remain open; live Ghidra is unchanged.
Further reviewer use is situational under `reverse-engineering/REVIEW-PROTOCOL.md`,
not a fixed model matrix.

**Historical Gen10 instruments (still true as capabilities, not tip census):**

The copied-runtime lab can use generated Mission bytecode as a typed text
oracle through the one-byte logger gate, expose the realized console command and
variable registries through a bounded disposable bridge, collect exact executed
instruction-byte ranges from existing TTD traces, collect selected raw
call/entry/return boundaries with x86 registers and bounded stack bytes, and
collect exact-window field-write chains. Schema-v3 call-context replay clears
associations across conservative global barriers: the replicated calibration has
four call-entry pairs, four raw returns, three validated returns, one orphan,
and three gap-free envelopes. Raw registers and stack bytes remain untyped.

Generation 10 admitted three bounded Level 521 call-context contracts (collision
slot-39 → player `Damage` → player `Hit` raw carriers/order with limited return
linkage) and carried Generation 9's five same-range target-lock metadata
corrections. `StartDie` remained open/opaque at that handoff. The independent
data-write lane has one refuter-survived semantic result: a Level 521 `LockHit`
invocation removed the supplied target's sole fired-lock node through five exact
ordered field transitions. These are instrument capabilities and historical
admissions. Canonical Gen19 retains those four C2 rows, separately re-proves a
narrower fifth ApplyDamage C2 from intact TTD wrappers, and adds the bounded
SetPos roundtrip as a sixth and LockHit's single-node removal path as a seventh;
it does not revive the rejected historical package,
claim positive-shield behavior, or broaden SetPos beyond the observed path.

A 2026-08-10 recursive static/source join now identifies the former raw
slot-39 function `0x004D8AE0` as `CRound::Hit`, recovers its ABI and direct
writes, and connects named `CRoundDamage` to the observed target-Damage call.
The same pass recovers `CExplosion::Hit`'s named radial-damage formula and
`CExplosion::Move`'s radius progression, and corrects the misnamed explosion
factory at `0x0050FF10`. The recovered mode-3 impact switch now proves that
`CRound::Hit` resolves `CRoundExplosion`, creates the object, and calls
`CExplosion::Init`; later same-receiver collision/addition, one contrasting
gate outcome, and rebuild parity remain open. This advances semantic understanding without retroactively
claiming that the Gen10 runtime instrument inferred the name or types.

The direct factory census now removes the same stale pickup interpretation from
all 22 containing functions. Three exact profile adapters identify unit,
small-unit, and stomp explosion fields; strict RTTI supplies virtual owners and
slots. The corrected family includes building/infantry/tentacle death
explosions, boat/dropship/boss/sentinel/simple-building small explosions,
mech/Warspite/ThunderHead stomp explosions, feature and rocket explosions, and
the Gill-M claw activation explosion. Static creation/initialization is proved;
mission reachability, later damage/effects, and rebuild parity remain open.

These instruments do not infer function boundaries, C++ receivers, argument or
return types, semantics, or parity. Static/source/RTTI evidence supplied joins
for early data-write plates. Focused player-damage / Level 521 successor work
remains an open runtime front alongside the next impact-ranked Generation-20
contract/rebuild advance. There is
not yet a normalized corpus-wide semantic ledger, and no new trace is justified
until existing evidence plus these instruments cannot answer a preregistered
question. The next campaign generation is 20.

## Evidence boundary

[`reverse-engineering/RE-INDEX.md`](reverse-engineering/RE-INDEX.md) is the
technical front door. The Ghidra database and retail executable own static
released-binary facts. Controlled copied-runtime observations own measured
behavior. Stuart's GPL source owns architecture and implementation evidence;
retail static/runtime differences decide where the Steam release diverged.

Generated inventories and proof-plan chains are not capabilities. Query the
canonical binary, source, or local corpus for the subsystem being implemented,
retain only the smallest durable conclusion, and validate the resulting product
behavior directly.

## Distribution

The `v1.0.11` app is an unsigned portable Windows x64 ZIP. It does not
currently include the retail executable, original asset set, saves, full Ghidra
database, raw captures, installer/MSIX identity, signing, or rebuild client.
Repository licenses do not cover retail game data. Future releases must keep
that user-supplied boundary unless a separately documented distribution basis
and all applicable attribution and third-party terms are established.

Use `npm run` for the current focused command surface. `npm test` checks the
WinUI/AppCore product lane; rebuild, native-client, runtime, and release checks
are selected only when their owning contract changes.
