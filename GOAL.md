# The goal

> Status: the standing objective for this project, set by the maintainer.
> Recorded here 2026-07-27 because it previously existed only outside the
> repository, which meant a fresh clone — and any session resuming after a
> context compaction — could not read it.

This is **the maintainer's statement of what is wanted**. It is not a finding and
it is not superseded by measurement. Everything else in this repository is in
service of it.

---

## The objective

Make Battle Engine Aquila's released experience run again, faithfully, from
startup through Level 100 completed — splash, intro FMV, click-to-start, main
menu, level select, loading, and the full Level 100 tutorial driven to outcome
**Won** by an agent using only player input and posting no mission event — such
that **it feels like the original game, not a resemblance of it**.

## The evidence partition

Use the cheapest sufficient evidence for each part. The pinned GPL source is a
**PARTIAL drop**, so "read the source" is not a blanket method.

- **Port from source** (present in the drop): player-vehicle physics and flight
  (`BattleEngine`, walker part, jet part), frontend page flow, career, camera,
  sound. **Cite file and line.**
- **Read from the retail `data/` folder** (authored content, no RE needed):
  `MissionScripts/level***`, `battle engine configurations.dat`,
  `worldheaders.dat`, `default physics.dat`, textures, video, language.
- **Recover from shipped bytes** (absent from the drop): the HUD, cockpit,
  battleline instrument, message system, unit AI, weapons, the mission-script VM,
  and the `FVector`/`FMatrix` math conventions.

Override ported source from bytes **only where a measurement proves divergence**,
and record each divergence as a tracked exception.

**Where our implementation diverges from available source without an
explanation — byte-proven, or architectural and stated — treat that divergence as
a defect.**

## The evidence rule

Every behaviour claim must cite a capture, a byte comparison, a test, or the
pinned source with file and line — **never decompiler output alone, and never a
model's opinion.**

Prefer a test that asserts a recovered law over a pixel comparison, which can
only detect that something is wrong, not what.

## Supporting aims

- A Ghidra reconstruction in which every function that can carry a developer name
  has one, **graded by its evidence**, with compiler-generated funclets and
  import thunks excluded **by measurement rather than assumption**.
- A WinUI 3 save/career editor with **no known data-loss path**.

## Standing constraints

- **Never mutate the Steam install or the pristine `BEA.exe`.**
- Keep `OnslaughtRebuild.Core` deterministic and free of presentation,
  filesystem, clock, process, network, and GPU dependencies.

---

## Where the goal currently stands

**Not met.** For the honest, current status — which changes as work lands and
must not be restated from memory — see
[`developer_state.json`](developer_state.json) under `goal_status`, and
[`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md).

Two things about that status are worth stating here because they have been
mis-said before:

1. "Driven to **Won** by player input" is the wording. Measured 2026-07-27: the
   full sequence runs as one thing and reaches `Won` **as a returning player**,
   but the shipping client can only start a **cold first career**, and on that it
   ends `Lost`. Do not report the first without the second.
2. "**Feels like** the original" is a higher bar than any percentage. A frame can
   score well and still feel wrong — a silent menu, an unskippable pan, a dead
   world. Pixel scores are necessary and are not the goal.
