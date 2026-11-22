# The goal

Status: standing maintainer objective; not complete
Last updated: 2026-11-21 (repurposed repository as the Onslaught Modding & Content Toolkit; standalone Companion GUI retired into Onslaught CE)
Summary: what David wants from the Onslaught preservation ecosystem now, where each part is owned, and the evidence and safety rules that still apply.

This is the maintainer's statement of what is wanted across the project. Measurements can correct implementation claims; they cannot narrow or mark this objective complete. Earlier Ghidra-campaign records remain in Git history and the private historical archive.

## The direction

- **Reverse engineering is grounded in decompilation.** All 5,482 of 5,482 mapped game functions match purely from source in the maintainer tree, with 0 object-byte concessions and 0 link aliases. Its public export, [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp), reproduces 5,449 of 5,482 purely from source (0 concessions, 0 aliases; the other 33 are in excluded DirectX SDK sample files). Clear records of labelled source and layout stand-ins remain required; function matching alone does not prove complete behavioural equivalence.
- **Onslaught CE is the unified native source port** for Windows and Linux, published separately as [Onslaught CE](https://github.com/dlprentice/onslaught-ce) (GPL-3.0-only, no game files). It preserves a faithful baseline while adding reliability fixes, modern display/input/controller support, high-resolution UI readability, optional visual/LOD controls, developer tools and privacy-conscious diagnostics. Ordinary campaign play remains preserved; new modes stay optional.
- **Player career, backup, lore, media, modding and authoring workflows live inside native CE.** The standalone Godot/.NET Companion GUI was retired from this repository on 2026-11-21 in favour of CE's built-in Service Record, Career/Backup, Goodies, Music/Lore, Mods and 3D Map/Mission Editor screens. Integrated career editing inside CE retains verified backups, stale-write refusal, read-back checks and coordination with loaded profile state.
- **This repository is the Onslaught Modding & Content Toolkit.** It owns the evidence-based JSON Content Catalogue (`tools/content_catalog.py`), byte-level Content Inventory (`tools/content_inventory.py`), format decoders/encoders, mod-staging utilities, MSL compiler/inspector and canonical lore library—supporting CE modding, content inspection and future HD asset pipelines without distributing proprietary game files.
- **Online play, RTS Commander, direct unit control and an explorable 3D museum** remain required native CE outcomes on the road to CE 0.2.0:
  - Approachable online co-op and opposing-team versus/skirmish play across Linux and Windows with lobby browsing, invitations and team/squad/proximity voice and text chat.
  - Continuous real-time 3D RTS Commander inside CE, distinct from directly piloting any controllable unit (infantry, vehicles, mounted guns, eligible structures) with safe AI hand-back.
  - Usable in-game 3D map and mission editors with modern `.ceproject` authoring and save/reopen/playtest loops, plus an actual explorable 3D museum reached through CE's menus.
  - Everything CE adds must look and feel like part of the original game.
- **The Godot rebuild** continues separately in [onslaught-godot](https://github.com/dlprentice/onslaught-godot), with `OnslaughtRebuild.Parity` owning deterministic simulation and `OnslaughtRebuild.Host` owning presentation, measured Present by Present against recorded references.
- **Game documentation** lives in [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation) (prose, format specs, mechanics, saves, levels and engine, CC BY-SA 4.0). New findings go there; this repository carries no frozen duplicate of `reverse-engineering/`.
- **Recovery** preserves unique project work, evidence, saves and signing/recovery material off-site with verified restoration while keeping sensitive paths and keys private.

## How progress is measured

Progress changes an outcome: a player or modder can do something useful that was previously unavailable; a demonstrated defect is fixed and verified; a specific unknown is resolved; or a preservation/documentation gap is closed. Report ideas, experiments, reviewed source, integrated source, validated releases and physical-device acceptance separately, without invented percentages.

[PROGRAM.md](PROGRAM.md) owns the dated cross-project chart and work queue. Product repositories own their detailed release, design and evidence records; [CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md) owns this repository's demonstrated Toolkit capabilities.

**CE release cadence.** CE follows an incremental release cadence (`0.1.14` through `0.1.19`) leading to `0.2.0` for the full milestone. Each release requires passing its Linux and native Windows gates plus maintainer go-ahead.

## Evidence and safeguards

- Every behaviour or format claim cites a capture, byte comparison, focused test or pinned function in [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp) (cited by function, never quoted). `references/Onslaught` is a source reference, not proof of retail behaviour. Unknowns are written as open questions with a falsifier.
- Never write the pristine measurement specimen or mutate an installed game without explicit informed user choice and a verified backup. Toolkit scripts never modify an installed game.
- Never synthesize `.bes` saves from scratch; preserve length, reserved fields and unknown bytes.
- Keep retail material, generated catalogues/inventories, Ghidra databases and decompiler output out of Git (`npm run test:safety`).
- No hosted CI/CD or telemetry unless explicitly directed; run the local validation gates instead.

## Where the goal stands

Not met. All 5,482 mapped game functions match purely from source (0 concessions, 0 aliases); Onslaught CE is public with current downloads in its [release list](https://github.com/dlprentice/onslaught-ce/releases/latest); the Godot rebuild continues in [onslaught-godot](https://github.com/dlprentice/onslaught-godot); and this repository delivers the verified Modding & Content Toolkit (JSON Content Catalogue, Content Inventory, format decoders, mod-staging tools and lore). [CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md) owns what is demonstrated here, [PROGRAM.md](PROGRAM.md) the work queue and [VALIDATION.md](VALIDATION.md) the checks.
