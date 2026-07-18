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
- Edit supported startup, audio, controller, and binding values in a copied
  `defaultoptions.bea`.
- Compare files and inspect bounded structural details.

AppCore starts from an existing retail-generated baseline, preserves file size
and unknown bytes outside selected regions, stages output beside the
destination, and verifies the committed bytes. It does not synthesize saves.

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

The Godot Aquila Handling Lab is currently an input/rendering harness with a
procedural arena, synthetic craft/targets, simplified movement, projectiles,
energy, shield, and hull. It does not yet reproduce retail camera feel, terrain,
missions, AI, weapon roster, animation, audio, campaign, or networking. Its
purpose is to replace those placeholders with the smallest source-derived and
retail-checked Aquila handling slice, then run a recognizable portion of Level
100 from authorized original assets.

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
