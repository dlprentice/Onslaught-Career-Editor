# Execution Program

Status: durable backlog under David's 2026-10-15 direction
Last updated: 2026-10-23 (companion CE phase D)
Summary: the open work, its acceptance gates, and what was closed or paused, without an execution diary.

The [goal](GOAL.md) sets the direction. Capability claims belong in
[CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md) and checks in [VALIDATION.md](VALIDATION.md). The queue that
ran the Ghidra campaign, the decompilation plan and the rebuild's work items until 2026-10-15 is in Git history;
the campaign's records are in the private `dlprentice/onslaught-re-archive`.

## Open work

### Godot rebuild

The rebuild's work queue, milestones and measured parity are kept in
[onslaught-godot](https://github.com/dlprentice/onslaught-godot), where it is developed; `rebuild/` here is a frozen
copy.

### Companion — CE integration

The companion is a C# application built in code on Godot 4.8 beta1 .NET and .NET 10, and organised around players: careers
with a campaign map, Goodies, career editing, cheats, game settings, automatic backups that can be put back, music
and voices, and lore (see its [README](companion/OnslaughtToolkit.Godot/README.md)). Every write into the game is a
choice made after a verified backup, never while the game runs.
[CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md#godot-companion--careers-settings-backups-music-and-lore) records
what is proven. David resumed companion development for phase D: CE as a separate target alongside the original game.

Remaining acceptance and release work:

- A human click-through, listening to the music and voices, and running the Windows package. The portable write
  path has run only on Linux; Windows cross-export and package checks do not establish Windows execution.
- Phase D adds CE discovery, launcher-only start, signed public update status, CE careers and the two documented
  launcher switches. The launcher retains update installation. See the companion README for the pinned contract,
  backup scope and Windows limitations. Branch `codex/companion-ce-20261023` awaits the lead's review and merge.
  Any media replacement would be a CE option (for example a CE user-data override folder), not a file swap in an
  install. Then, at David's direction, a public release.

Keep the companion's application code, the rebuild and private retail data separate. Beyond launching and managing
Onslaught CE, no store, account or community features are planned.

### Game documentation — ongoing

Write what the decompilation establishes as prose and specs under [`reverse-engineering/`](reverse-engineering/RE-INDEX.md),
citing functions rather than quoting code. The companion's CE work (careers, settings, launch) is the next
consumer. Sections whose decompiler listings moved to the private archive on 2026-10-15 keep a pointer and,
where needed, a short summary; a fuller prose description is welcome wherever a reader needs one.

### Decompilation and native port

The byte-matching decompilation is complete (5,482 of 5,482 functions) and published as
[onslaught-decomp](https://github.com/dlprentice/onslaught-decomp), whose README holds its score and divergences. Its
native source port (Windows and Linux) is published as [Onslaught CE](https://github.com/dlprentice/onslaught-ce)
(GPL-3.0-only source and binaries, no game files). Nothing from either is copied into this repository.

### Repository

- The public history was flattened to a single new root (approved by David); the full earlier history is a
  verified bundle and `refs/old/*` in the private RE archive. The third-party fork and GitHub's pull-request refs
  still hold the old history; whether to ask GitHub Support to purge the PR refs is David's decision.
- The split: the Godot rebuild is developed in [onslaught-godot](https://github.com/dlprentice/onslaught-godot) (the `rebuild/` copy here is frozen), and
  the game documentation is published as [onslaught-preservation](https://github.com/dlprentice/onslaught-preservation). Still to come: this repository's
  full history is bundled into the private RE archive and flattened again, and the repository is renamed
  onslaught-companion. The companion CE integration is a separate feature branch for lead review. Each step is a separate, coordinated task.

## Paused

- **The earlier fixed-point rebuild's queue** (Core/Client/Godot, paused 2026-10-15 when the rebuild restarted around
  the parity core): World 110 generalization (former P7) and player-input replay tapes (former P8). Its final state is
  described in [rebuild/README.md](rebuild/README.md#the-earlier-rebuild-history). The rebuild's scope is level
  100 only.
- **The companion** (above), until David sets new requirements.

## Closed

| Item | Outcome |
| --- | --- |
| Retail RE by Ghidra campaign (generations, contracts, promotion cohorts, record audit) | Superseded by the byte-matching decompilation; records in the private RE archive. |
| Byte-matching decompilation | Complete (5,482/5,482), published as [onslaught-decomp](https://github.com/dlprentice/onslaught-decomp). |
| WinUI toolkit, its UI tests and CLI (former P11) | Removed 2026-10-15; the companion replaced them. |
| Campaign bookkeeping relief (former P6) | Retired with the campaign. |
| Repository preparation (former P12) | The checkout lives on Archive B behind the Projects bind; `local-lab/` and `local-data/` are real ignored children. The 2026-10-15 cleanup moved the Ghidra checkpoint and RE machinery to the private archive and removed the WinUI surfaces. |
