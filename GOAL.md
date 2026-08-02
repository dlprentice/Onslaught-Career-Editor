# The goal

> Status: the standing objective for this project, set by the maintainer.
> Recorded here 2026-07-27 because it previously existed only outside the
> repository, which meant a fresh clone — and any session resuming after a
> context compaction — could not read it.
>
> **Revised 2026-07-27** after a day of measurement. Three clauses were added
> and one was demoted; see [Revision history](#revision-history) at the bottom
> for what changed and what each change is a reaction to.
>
> **Revised 2026-08-01** by the maintainer: the standing constraint forbidding
> mutation of the Steam install was replaced. See
> [Revision history](#revision-history).
>
> Last updated: 2026-08-01. The objective and acceptance test are unchanged;
> measured status belongs in
> [`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md) and
> [`developer_state.json`](developer_state.json).
> Summary: what "done" means here — the objective, the acceptance test that
> stands in for it, the evidence partition, the evidence rule, and the standing
> constraints.

This is **the maintainer's statement of what is wanted**. It is not a finding and
it is not superseded by measurement. Everything else in this repository is in
service of it.

---

## The objective

Rebuild Battle Engine Aquila **in Godot** so its released experience runs again,
faithfully, from startup through Level 100 completed — splash, intro FMV,
click-to-start, main menu, level select, loading, and the full Level 100 tutorial
— such that **it feels like the original game, not a resemblance of it**.

### The property, and the test that stands in for it

The **property wanted** is that a human starting a **cold first career** — the
only career the shipping client can start — gets the released experience.

The **acceptance test** is that an agent drives Level 100 to outcome **Won**
using only player input and posting no mission event.

That test is a **proxy, not the goal**. An autopilot that reaches `Won` by means
no player could reproduce has proved nothing.

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

## The method rule

**Build the instrument before doing by hand what it could do wholesale.** Prefer
a measurement that answers many questions at once — a draw-call log, a
time-travel trace, a table read straight from the shipped data — over fitting one
value at a time.

Fitting produces confident wrong answers that cost more to withdraw than to make.

## The defaults rule

**The reconstruction's defaults are retail's defaults.** A value traceable to
this machine's settings, or to a convenience patch in the capture rig, is a lab
artefact and must never ship as authored behaviour.

## Supporting aims

- A Ghidra reconstruction in which every function that can carry a developer name
  has one, **graded by its evidence**, with compiler-generated funclets and
  import thunks excluded **by measurement rather than assumption**.
- A WinUI 3 save/career editor with **no known data-loss path**.

## Standing constraints

- **The pristine `BEA.exe` (`74154bfa…`) is never mutated.** It is the
  measurement baseline for every byte finding in the RE lane. Absolute.
- **The user's game is theirs.** The app may change an installed game when the
  person who owns it asks for that — and only with an explicit, informed choice
  and a verified backup made *before* the write, with no opt-out. Refuse rather
  than manufacture: a backup taken from an already-modified file and named
  "original" destroys the only route back.
- **The user's saves are theirs.** Nothing may destroy save data as a side
  effect of doing something else.
- Keep `OnslaughtRebuild.Core` deterministic and free of presentation,
  filesystem, clock, process, network, and GPU dependencies.

---

## Where the goal currently stands

**Not met.** For the honest, current status — which changes as work lands and
must not be restated from memory — see
[`developer_state.json`](developer_state.json) under `goal_status`, and
[`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md).

"**Feels like** the original" is a higher bar than any percentage. A frame can
score well and still feel wrong—a silent menu, an unskippable pan, or a dead
world. Pixel scores can expose defects; they are not the goal.

---

## Revision history

### 2026-08-01 — the installed game belongs to the person who installed it

The standing constraint read **"Never mutate the Steam install or the pristine
`BEA.exe`."** It was written when those two were the same risk. They are not.

The pristine specimen is a *measurement* concern: every byte finding in the RE
lane is quoted against it, so mutating it would silently invalidate evidence
nobody would think to re-check. That half is now stated on its own and is
absolute.

The installed game is a *user* concern, and forbidding it outright was the wrong
answer. It forced a multi-gigabyte copy of the whole game on anyone who just
wanted to play theirs patched, and the maintainer had to work around his own rule
to test anything. A rule that forbids the thing people want produces workarounds,
not safety.

What replaced it is narrower where it matters and wider where the prohibition
cost something: the app may change an installed game when its owner asks, and
only behind an explicit informed choice and a verified backup taken first, with
no opt-out. Expressed as a precondition the calling code cannot skip rather than
a step it must remember — `BinaryPatchEngine.AuthorizeInstalledGameWrite` will
not hand back permission until a verified original sits beside the target.

A third clause was added at the same time, because the work that prompted this
found something worse than the thing it set out to fix: deleting a safe copy was
destroying the careers played inside it, silently. Saves are the one thing in
that folder the game cannot regenerate, so they get their own line.

This paragraph exists because `CLAUDE.md` says this document is not superseded by
measurement. A file with that status, left contradicting the code, is not a stale
comment — it is an instruction to a future session to revert working features.
`CLAUDE.md` and `AGENTS.md` were rewritten to these principles in `65afc257`;
this file lagged them by a day.

### 2026-07-27 — the Godot naming, the proxy demotion, and two method rules

The objective previously read "make ... run again" without naming an engine, and
stated the agent-driven `Won` run as though it were the goal itself. Three
changes, each a reaction to something that actually happened:

- **Godot is now named.** The deliverable surface was implicit and the goal read
  engine-agnostic.
- **The `Won` run was demoted from goal to acceptance test**, with the underlying
  property stated separately. As written before, an autopilot that reached `Won`
  counted as fidelity progress, which let effort drift toward the harness instead
  of the game.
- **The method rule was added.** The D3D9 draw-call proxy was built late in a
  day and used once; time-travel tracing sat installed and unused across roughly
  33 game launches. Before the proxy existed, every HUD coordinate was recovered
  by fitting pixels, which produced at least one conclusion — a claimed "1.49
  energy surplus" — that had to be withdrawn because it was a fit to an artefact
  rather than a measurement.
- **The defaults rule was added.** Two lab artefacts had already reached, or come
  close to reaching, authored behaviour: a pine LOD distance pinned to this
  machine's graphics setting rather than retail's default, and the capture rig's
  four-byte force-windowed patch.

Nothing was removed. The evidence partition, the evidence rule, the supporting
aims and the standing constraints are unchanged.
