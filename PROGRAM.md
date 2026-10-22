# Execution Program

Status: durable backlog under David's 2026-10-15 direction
Last updated: 2026-10-22 (the companion's next step is the CE launcher and manager; exe patching and safe launch retired; relicensing: code GPL-3.0-only, docs and lore CC BY-SA 4.0)
Summary: the open work, its acceptance gates, and what was closed or paused, without an execution diary.

The [goal](GOAL.md) sets the direction. Capability claims belong in
[CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md) and checks in [VALIDATION.md](VALIDATION.md). The queue that
ran the Ghidra campaign, the decompilation plan and the rebuild's work items until 2026-10-15 is in Git history;
the campaign's records are in the private `dlprentice/onslaught-re-archive`.

## Open work

### Godot rebuild — active (scoped proof of concept)

David reactivated the rebuild on 2026-10-15: startup to exit 1:1 with retail, with level 100 playable to completion
(win, loss and retry) and the career written after a win identical to retail's. `OnslaughtRebuild.Parity` owns the
simulation and `OnslaughtRebuild.Host` the presentation (experimental live mode `HOST_LIVE=1`); the earlier
Core/Client/Godot projects are reference material. Parity is measured Present by Present against retail and
native-port recordings; [rebuild/PARITY.md](rebuild/PARITY.md) records the milestones and what is measured, and
[rebuild/README.md](rebuild/README.md#working-lane) the working branch, clone and reference environment.

Open, in priority order:

- The tutorial win: a level 100 route driven by ordinary player inputs through every target group, zone and the
  genuine win, then end-level data, the save and the debrief, compared across retail, the native port and the
  rebuild.
- The level-start pan camera: the parity core rounds its orientation's angles as the earlier port did, where retail
  keeps them unrounded through its inline block (port patch 0036). Port retail's block with its oracle cases, then
  re-compare the trainer (to P17300) and c17 (to P22150) routes, which match the native port at every Present today.
- The controls and display Apply paths (display reset, joystick, the remaining options) that still stop a run.
- The remaining motion controllers and the incomplete BattleEngine coverage.
- The Host's remaining drawing and output: the HUD's text (weapon name, warnings, objective panel), the lock-on pieces
  and warning-receiver threats (not ported), the front end's particles and battle-engine model, P2800's dome, then
  actual audio output, display reset and live input, with moving-footage review. The front end, the level's 2D and the
  HUD's target passes are drawn and compared with the port ([PARITY.md](rebuild/PARITY.md), M7 slices 1 to 4).

### Companion — paused

The companion is a C# application built in code on Godot 4.8 dev6 .NET and organised around players: careers
with a campaign map, Goodies, career editing, cheats, game settings, automatic backups that can be put back, music
and voices, and lore (see its [README](companion/OnslaughtToolkit.Godot/README.md)). Every write into the game is a
choice made after a verified backup, never while the game runs.
[CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md#godot-companion--careers-settings-backups-music-and-lore) records
what is proven. Development paused after the Goodies and mip work (branch `claude/companion-20261015`); it resumes
when David sets new requirements.

Open when it resumes:

- A human click-through, listening to the music and voices, and running the Windows package. The portable write
  path has run only on Linux; Windows cross-export and package checks do not establish Windows execution.
- The Onslaught CE launcher and manager: find, launch and update Onslaught CE; show and edit CE's careers and
  settings in CE's own folder, with the same protected writes and per-game backups; say which game is running. The
  original game's save and settings editing stays, with protected writes. Executable patching and the WinUI app's
  copied-install safe launch are retired; AppCore goes once its test facts are ported into the companion's tests.
  Any media replacement would be a CE option (for example a CE user-data override folder), not a file swap in an
  install. Then, at David's direction, a public release.

Keep the companion's application code, the rebuild and private retail data separate. Beyond launching and managing
Onslaught CE, no store, account or community features are planned.

### Game documentation — ongoing

Write what the decompilation establishes as prose and specs under [`reverse-engineering/`](reverse-engineering/RE-INDEX.md),
citing functions rather than quoting code. The companion's CE work (careers, settings, launch) is the next
consumer. Sections whose decompiler listings moved to the private archive on 2026-10-15 keep a pointer and,
where needed, a short summary; a fuller prose description is welcome wherever a reader needs one.

### Decompilation and native port — private

The byte-matching decompilation is complete (5,482 of 5,482 functions) in the private `bea-decomp`, which owns its
plan, score and divergences. Its native source port (Windows and Linux) is developed there and published
separately as Onslaught CE (GPL-3.0-only source and binaries, no game files; link added at release). Nothing from
it is copied into this repository.

### Repository

- The public history was flattened to a single new root (approved by David); the full earlier history is a
  verified bundle and `refs/old/*` in the private RE archive. The third-party fork and GitHub's pull-request refs
  still hold the old history; whether to ask GitHub Support to purge the PR refs is David's decision.
- The decided plan, in order: after the Onslaught CE release, the Godot rebuild (`rebuild/`) moves to its own
  repository, `onslaught-godot`; this repository's full history is then bundled into the private RE archive and
  flattened again; and finally this repository is renamed to the companion's name, which David has yet to choose.
  The companion later becomes the CE launcher. Each step is a separate, coordinated task.

## Paused

- **The earlier fixed-point rebuild's queue** (Core/Client/Godot, paused 2026-10-15 when the rebuild restarted around
  the parity core): World 110 generalization (former P7) and player-input replay tapes (former P8). Its final state is
  described in [rebuild/README.md](rebuild/README.md#the-earlier-rebuild-history). The active rebuild's scope is level
  100 only.
- **The companion** (above), until David sets new requirements.

## Closed

| Item | Outcome |
| --- | --- |
| Retail RE by Ghidra campaign (generations, contracts, promotion cohorts, record audit) | Superseded by the byte-matching decompilation; records in the private RE archive. |
| Byte-matching decompilation | Complete (5,482/5,482) in private `bea-decomp`. |
| WinUI toolkit, its UI tests and CLI (former P11) | Removed 2026-10-15; the companion replaced them. |
| Campaign bookkeeping relief (former P6) | Retired with the campaign. |
| Repository preparation (former P12) | The checkout lives on Archive B behind the Projects bind; `local-lab/` and `local-data/` are real ignored children. The 2026-10-15 cleanup moved the Ghidra checkpoint and RE machinery to the private archive and removed the WinUI surfaces. |
