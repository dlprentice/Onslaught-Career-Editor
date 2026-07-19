# Current Capabilities

Onslaught Toolkit has one player-facing product: the WinUI 3 Windows app.
AppCore owns its file and copied-target correctness. Reverse engineering, the
unshipped CLI, focused tools, and the early GPL rebuild support that product and
the longer reconstruction effort; they are not parallel app lanes.

## WinUI toolkit

The primary navigation is Home, Save Lab, Media, Asset Library, Lore, Windowed
& Mods, Settings, and About.

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

- Treat the installed game and original `BEA.exe` as read-only sources.
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
back the retail minimum `0.1`. This proves the copied option and live global,
not subjective mouse feel or physical-controller behavior.

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
walker-to-jet state to 16 ticks at 30 Hz. Jet-to-walker timing, animation,
camera, resources, weapons, and flight dynamics remain unproven.

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

- Media reads supported audio/video from a selected local game path.
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

The Godot Level 100 Opening Slice now uses the released 65×65 coarse Level 100
heightfield plus Federation walker/jet, Control Tower, and Tank Factory
geometry. Core starts at the released player-one heading and owns the authored
player ground elevation plus the Target Zone 1 → Firing Range trigger sequence,
including each script's
0.5-second event delay. The prior synthetic arena boundary, flat plane, and
placeholder structures are gone. Terrain, retained meshes, facilities, sky,
light, camera, and Core-relative positions now share the released
`(X, Y, Z-down)` → Godot `(X, -Z, -Y)` mapping. The opening view follows the
released four-point Level 100 pan around the exterior Aquila, switches to the
retained first-person cockpit and HUD after 5.95 seconds, and enables player
input after the full six-second retail interval. Core rejects movement, look,
fire, and transform input during those first 180 deterministic ticks. Two fresh
uninterrupted safe-copy runs repeated the same camera endpoints, six-second
length, handoff, and playing-state boundary. A clean Level 100 control and two
fresh repeated safe-copy runs also establish the walker's acceleration,
equal forward/strafe cap, frictional
coast, and inertial body turning. The client renders Core's continuous yaw
rather than an eight-direction visual snap. Walker-to-jet initiation also exposes Core's
retail-timed 16-tick transition instead of switching to Jet immediately. The
walker now loads directly from its exact released AYA as a 63-part hierarchy
with 54 base-material surfaces. Its twenty leg-chain parts begin in a stable
machine-observed Level 100 standing pose and follow the released 101-frame
`LegMotion` cycle from Core velocity. The jet and two facilities remain bounded
static conversions. The exterior meshes and exact frame-25 first-person
cockpit render from eight retained AYA-wrapped textures. Twelve exact released
HUD textures, including Font13PS, replace the prototype overlay for the bounded
crosshair, radar/radio frames, and current objective line. The released macro
terrain blend, exact Level 100 repeating detail texture, cube-25 sky, fog, and
environment lighting replace their earlier placeholders. The detail texture
uses both released coordinate scales and observed modulation modes; the moving
cloud-shadow stage remains absent. Walker acceleration now follows Core's
continuous body yaw; jet translation and projectile heading retain the older
eight-way approximation. The slice does not
yet reproduce steep-slope or actor collision response or the retail controller's procedural foot
placement, the rest of the mission, AI, weapon roster, secondary/reflection and
cloud-shadow passes, facility destruction, transform animation, complete HUD
state/contacts/radio behavior, audio, campaign, networking, or the rest of the
transform model. The camera slice does not yet reproduce cockpit pitch response,
terrain occlusion, camera shake, or later scripted cameras.
Tutorial dialogue and flight/weapon eligibility gates are not implemented; the
remaining synthetic combat targets are Core handling fixtures and are no longer
drawn as Level 100 scenery. Synthetic objective beacons are also absent.
Core embeds the exact Level 100 HFLD, applies Steam's released fixed-point
height sampler, and hashes the resulting walker ground elevation. Godot adapts
that value for the player; static facilities and synthetic projectiles remain
presentation-grounded. The observed route did not exercise a steep-slope flag,
body tilt, or nonzero vertical velocity, so those behaviors remain outside the
demonstrated slice.

The project has full permission to use, modify, and distribute the original
game assets. The remaining asset gap is technical integration and format
fidelity, not a requirement that every user supply an unshipped private pack.
Read [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md) before changing this lane.

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

The published `v1.0.9` app is an unsigned portable Windows x64 ZIP. It does not
currently include the retail executable, original asset set, saves, full Ghidra
database, raw captures, installer/MSIX identity, signing, or rebuild client.
Asset permission does not change that current package shape; any future bundled
asset slice requires deliberate provenance, attribution, and third-party notice
review.

Use `npm run` for the current focused command surface. `npm test` checks the
WinUI/AppCore product lane; rebuild, native-client, runtime, and release checks
are selected only when their owning contract changes.
