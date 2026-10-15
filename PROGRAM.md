# Execution Program

Status: durable backlog under David's 2026-10-15 direction
Last updated: 2026-10-15 (decompilation done and private; native port in progress; companion active; Godot rebuild parked; repository cleaned)
Summary: the open work, its acceptance gates, and what was closed or parked, without an execution diary.

The [goal](GOAL.md) sets the direction. Capability claims belong in
[CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md) and checks in [VALIDATION.md](VALIDATION.md). The queue that
ran the Ghidra campaign, the decompilation plan and the rebuild's work items until 2026-10-15 is in Git history;
the campaign's records are in the private `dlprentice/onslaught-re-archive`.

## Open work

### Companion — active

The companion is a C# application built in code on Godot 4.8 dev6 .NET and organised around players: careers
with a campaign map, Goodies, career editing, cheats, game settings, automatic backups that can be put back, music
and voices, and lore (see its [README](companion/OnslaughtToolkit.Godot/README.md)). Every write into the game is a
choice made after a verified backup, never while the game runs.
[CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md#godot-companion--careers-settings-backups-music-and-lore) records
what is proven.

Open:

- A human click-through, listening to the music and voices, and running the Windows package. The portable write
  path has run only on Linux; Windows cross-export and package checks do not establish Windows execution.
- The mod manager, built on the AppCore patching core: patching the installed `BEA.exe` with a preview, a verified
  backup and restore, through `BinaryPatchEngine.AuthorizeInstalledGameWrite`. Then, at David's direction, showing
  the Goodies' own contents, media replacement and a public release.

Keep MIT application code, the GPL rebuild and private retail data separate. No unrelated launcher, store or
community features are planned.

### Game documentation — ongoing

Write what the decompilation establishes as prose and specs under [`reverse-engineering/`](reverse-engineering/RE-INDEX.md),
citing functions rather than quoting code. The companion's next features (patches, Goodie contents, media) are the
first consumers. Sections whose decompiler listings moved to the private archive on 2026-10-15 keep a pointer and,
where needed, a short summary; a fuller prose description is welcome wherever a reader needs one.

### Decompilation and native port — private

The byte-matching decompilation is complete (5,482 of 5,482 functions) in the private `bea-decomp`, which owns its
plan, score and divergences. Its native source port (Windows and Linux) is in progress there. Publication as
"Onslaught CE" (GPL-3.0 source and binaries, no game files) follows once the port plays like retail. Nothing from
it is copied into this repository.

### Repository

- The public history is to be flattened to a single new root after this cleanup lands, with a hash-verified
  private bundle of the full history kept first (approved by David; the lead runs it).
- A later rename of the repository toward the "Onslaught CE" name is a separate, coordinated task.

## Parked

- **The Godot rebuild** (parked 2026-10-15 at tag `archive/godot-rebuild-20260926`): World 110 generalization
  (former P7) and player-input replay tapes (former P8) are parked with it. At the tag the cold-start route wins
  Level 100 through player input and its tape replays deterministically; World 110 is built in Core from retail
  data but is not playable in the Godot host. See [rebuild/README.md](rebuild/README.md).

## Closed

| Item | Outcome |
| --- | --- |
| Retail RE by Ghidra campaign (generations, contracts, promotion cohorts, record audit) | Superseded by the byte-matching decompilation; records in the private RE archive. |
| Byte-matching decompilation | Complete (5,482/5,482) in private `bea-decomp`. |
| WinUI toolkit, its UI tests and CLI (former P11) | Removed 2026-10-15; the companion replaced them. |
| Campaign bookkeeping relief (former P6) | Retired with the campaign. |
| Repository preparation (former P12) | The checkout lives on Archive B behind the Projects bind; `local-lab/` and `local-data/` are real ignored children. The 2026-10-15 cleanup moved the Ghidra checkpoint and RE machinery to the private archive and removed the WinUI surfaces. |
