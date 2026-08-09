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
> **Revised 2026-08-02** by the maintainer: full retail reverse engineering, the
> Godot rebuild, and the WinUI 3 app are coequal outcomes. A current goal chooses
> focus, not standing rank. See [Revision history](#revision-history).
>
> Last updated: 2026-08-09. Current measured status belongs in
> [`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md) and
> [`developer_state.json`](developer_state.json) (routing key
> `current_re_authority`). Generation 73 is retained only as the exact
> projection oracle named by the post-loss claim-closure receipt; it is not a
> campaign parent or authority.
> Summary: what "done" means here — the objectives, the rebuild acceptance test that
> stands in for it, the evidence partition, the evidence rule, and the standing
> constraints.

This is **the maintainer's statement of what is wanted**. It is not a finding and
it is not superseded by measurement. Everything else in this repository is in
service of it.

---

## The objectives

This is one full-scope project with three coequal, mutually reinforcing outcomes:

1. **Fully reverse Battle Engine Aquila's retail release**—its functions,
   contracts, data, systems, patch points, and dormant capabilities—so the game
   can be understood, preserved, patched, and modded with evidence rather than
   folklore.
2. **Rebuild Battle Engine Aquila in Godot at 1:1 behavioral and experiential
   parity**, beginning with the complete released path from startup through
   Level 100 completed—splash, intro FMV, click-to-start, main menu, level
   select, loading, and the full tutorial—such that it feels like the original
   game, not a resemblance of it.
3. **Ship a polished WinUI 3 preservation toolkit** for careers, saves, safe
   copies, patching, media, and the other user-facing capabilities the project
   proves, with no known data-loss path.

Retail RE feeds reconstruction, and reconstruction exposes the next retail
questions; RE and shared tooling also make safe app features possible. None is a
side lane or lower priority. Limited attention follows the current goal without
changing their standing rank. A recovered name or one observed call is not a
completed function contract, and a reconstruction approximation does not become
retail truth because it looks plausible.

### The rebuild property, and the test that stands in for it

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

## Preserved recursive RE campaign objective

The maintainer set the following campaign objective on 2026-08-02 and asked on
2026-08-04 that it remain durable even when a shorter thread goal is used to
reach a safe handoff boundary. It is preserved verbatim below. A handoff goal
may define where one agent stops safely; it does not supersede, narrow, or mark
this standing campaign complete.

> Build, validate, and operate a recursive Battle Engine Aquila function-discovery, proof, and reconstruction campaign. Refresh exact specimen-bound Ghidra function/range accounting and publish atomic, hash-bound READY snapshots. Account for every current Ghidra function and every mapped or unmapped .text range—including never-executed residuals—until each has an evidence-graded terminal classification or an explicit open question, cheapest falsifier, and next instrument.
>
> Run coupled discovery, contract, and rebuild lanes. The discovery lane must find and classify missing functions and recover exact boundaries, callers/callees, class ownership, signatures, globals, structure fields, algorithms, constants, units, ordering, and failure behavior. The contract lane must establish what enters, what leaves, what changes, and under which conditions. A function is not complete merely because one observed call has a contract: progress it toward REBUILD_READY, with enough bounded evidence to implement its relevant behavior in rebuild/, create focused parity tests, and state remaining uncertainty. Prioritize unknown functions by their impact on blocked rebuild systems, call chains, and vertical slices. Maintain explicit mappings from specimen-bound retail function/entity keys to reconstruction owners, implementations, and tests.
>
> Implement a durable select → author → run → refute → advance loop that addresses questions individually, preserves unanswered fields and unresolved questions, records superseded entities, and never treats UNSCORED evidence as success. Parse and validate actual receipts, manifests, debugger observations, identities, controls, and refuter outputs instead of trusting metadata labels. Every nonterminal function or residual must remain reachable through the frontier; successful work must advance campaign state rather than causing the same question to recur indefinitely.
>
> Mine the existing 60+ level-start traces, combat takes, static evidence, Stuart source, and Ghidra evidence before creating new captures. Treat natural gameplay traces as broad discovery evidence and authored scenarios as sparse causal probes. When existing evidence cannot answer a preregistered question, use fresh safe-copy derivatives to construct the smallest controlled experiment necessary: isolate relevant actors and systems, suppress presentation or briefing state when appropriate, position actors deterministically, remove unrelated activity, select exact inputs, define competing outcomes, and stop capture immediately after the answer window.
>
> Prove the complete loop with the observed missing-handler cohort and the bounded Level 100 Turret 01 damage-chain pilot, then recursively expand across the remaining function and .text residual frontier. Carry sufficiently proven findings into focused reconstruction code and parity tests rather than allowing the campaign to become a documentation-only exercise. Separate released-behavior evidence, source-informed architecture, reconstruction decisions, and remaining hypotheses.
>
> Promotion to the maintainer Ghidra project is authorized for evidence-adjudicated function boundaries, names, signatures, types, comments, and references only after exact program/specimen identity verification, a verified recoverable project backup, isolated scratch-project validation, explicit dry-run/apply/readback receipts, and successful independent refutation gates. Never promote UNSCORED, aliased, identity-mismatched, partially applied, or refuter-pending claims. Record candidate-to-final entity supersession so later snapshots and campaign generations inherit completed work.
>
> Preserve the pristine 74154bfa… specimen absolutely, use fresh scratch derivatives for runtime experiments, and defer elevation-dependent operations until elevation is available. “100%” means honest terminal-state accounting—proved code, proved data or padding, bounded ambiguity with a falsifier, or rebuild-ready behavior—not invented names, assumed semantics, or a requirement that every byte execute.
>
> Do not mark this goal complete while any current function, .text residual, contract, rebuild mapping, or newly proven high-throughput discovery instrument retains an actionable unresolved frontier; a milestone, successful pilot, or live Ghidra promotion is progress, not completion.

---

## Current replay authority (do not restate volatile counts here)

Standing complete-RE progress is **not** the Gen10 handoff below and is no
longer selected from the damaged Generation-73 candidate chain. Read
`developer_state.json` → `current_re_authority`. As of 2026-08-09 the exact
authority is canonical Generation 17 at
`local-lab/re-campaign-incident-recovery-20260808-v1/generation-17-lockhit-bounded-contract-v1/`:
READY SHA-256 `6d794905d6fc5daea11f99b781cf8eb7740765e749c784d02507d43436b801a2`,
frozen reducer ID
`fbb343d629fa12a641aced04db88b59e5270e1f45990d9d203284302f8761621`,
and external authority receipt SHA-256
`c37aae056dc2f04d946db69d4e13d276dbc11d1a52976c97657af0a5549b00cb`.
Its independent replica is reproduction-only. Generation 73 supplied a
field-level projection oracle; Generations 12 through 17 then admitted bounded
Damage/Hit field-write contracts, one replicated zero-shield ApplyDamage
contract, the exact consumer-bound TokenArchive dispatch-table partition, and
the exact Mission-native SetPos boundary plus its replicated script-visible
position-copy contract and partial rebuild mapping, plus LockHit's retained
single-node removal path, without broadening them beyond their evidence. The
campaign remains incomplete and the next valid campaign generation is 18. Ghidra mutation still requires
its separate promotion gate and authority.

## Historical atomic handoff boundary (2026-08-04 / Generation 10)

The temporary 2026-08-04 handoff objective stopped at campaign Generation 10,
`local-lab/ttd-call-context-level521-impact-generation10-20260804-v1/generation-10-ttd-call-context-observation-v2/`.
Its `campaign.ready.json` SHA-256 is
`b349f0b2895849ba320b0b0b783c60a98794d01f375d57d9a04bbe4a5aebabb2`
and its frozen reducer ID is
`7dfa4015aad676bfeb22977adf3aadcddac49ba31fa8203a63a32f76d941f5d9`.
Generation 10 advanced exactly three bounded Level 521 call-context contracts;
it changed no Ghidra range or name, proved no memory write or rebuild parity,
and left `StartDie` open and opaque. Generation 9 remained its exact live
Ghidra parent. That boundary is **historical**, not the current post-loss
Generation-11 replay authority.

The immutable boundary, rejected candidates, verification command, ranked next
three frontiers, and successor operating brief are recorded under
`_RECURSIVE_RE_CAMPAIGN_2026_08_02.handoff_2026_08_04` in
[`developer_state.json`](developer_state.json). A successor must replay that
boundary rather than trusting this summary. Completing the temporary handoff
does **not** complete the preserved recursive campaign above.

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

### 2026-08-04 — recursive campaign directive preserved for handoff

The full recursive function-discovery, proof, contract, Ghidra-promotion, and
reconstruction directive is now recorded verbatim in this file. A temporary
thread goal may end at an atomic, verified, externally resumable handoff
boundary, but that administrative stopping condition does not redefine the
standing project objective or turn an unfinished frontier into completion.

### 2026-08-02 — RE, rebuild, and the WinUI app are coequal

The objective previously made the Godot rebuild primary and listed the Ghidra
reconstruction and WinUI app as supporting aims. The maintainer corrected that
hierarchy: full retail RE, the 1:1 Godot rebuild, and the polished WinUI 3 app
are equal standing outcomes. A current goal can focus almost entirely on one of
them because attention is finite; that focus is not a permanent priority rank.

The rebuild's cold-career Level 100 acceptance test remains unchanged. It tests
the rebuild objective; it is not a completion test for full retail function and
range accounting or the WinUI product.

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
