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
> Last updated: 2026-08-13. Current measured status belongs in
> [`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md) and
> [`developer_state.json`](developer_state.json) (routing key
> `current_re_authority`). Generation 73 is retained only as the exact
> projection oracle named by the post-loss claim-closure receipt; it is not a
> campaign parent or authority.
>
> **The one mutable section is `## Current directive`.** An agent's standing
> goal is a short proxy that points at it, so the directive can be revised as
> evidence lands without re-setting the goal. Everything above and below that
> section is the stable statement of what is wanted.
>
> Summary: what "done" means here — the objectives, the rebuild acceptance test that
> stands in for it, the evidence partition, the evidence rule, the standing
> constraints, and the current directive an agent executes.

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

## Current directive

> **This is the mutable section.** An agent's standing goal is a short proxy
> that points here, so this directive can be revised as evidence lands without
> re-setting the goal. It is **maintainer-owned**: an agent may propose changes
> and must not narrow, weaken, retarget, or complete it on its own authority.
> Revise it by superseding in place with a dated note in *Directive revisions*
> below; never keep a parallel copy.
>
> Set 2026-08-12. Status: **active**.

### Mandate

Drive the primary Battle Engine Aquila reverse-engineering lane forward from
canonical Generation 23 through successive mechanically verified generations,
maximizing defensible progress toward complete retail understanding, durable
function and behavior contracts, a materially improved live Ghidra
reconstruction, and Godot parity. This is a long-horizon execution mandate, not
permission to manufacture certainty, and not an instruction to produce process
theater in place of reverse engineering.

### Ground yourself before acting

Confirm HEAD is at or beyond `25fba71a`. Confirm the pristine specimen SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`. Confirm the
Generation 23 READY
`4471fdfe105340ad06c2ad28d945eb05e9bc94f002110888b164581ccf1a93fc` and frozen
reducer `a757bc51cd8302cf0e889c7db72ca58f9d865597b250371444d8c2285537db09`
through the literal pinned verify command in
[`developer_state.json`](developer_state.json) → `current_re_authority`.
Generation 23 is the sole campaign parent, the next valid generation is 24, and
Generation 73 is a projection oracle that is never a parent or authority.

### Never collapse the evidence layers

Static-envelope closure covers the dated 8,136-function census against which it
was sealed. The current saved structural census is 8,170 after 34 additional
Mission-registry boundaries were independently proved and promoted; those 34
are not yet in the closure table. Neither count is a final ceiling, semantic
recovery, or reversal. The PC demo
partition and the instruction-local Xbox source-line anchors are oracles, never
denominators for retail completion. Generation 23 owns admitted runtime
semantics and remains sparse. Live Ghidra structural navigation may lead the
campaign without silently upgrading any semantic grade. Report the layer, the
exact denominator, the specimen, and the date with every published number, and
refuse any single percentage that spans layers.

### The loop

Run a bounded select → preregister → measure → refute → advance loop. Rank
questions by blocked contracts, call-chain leverage, Ghidra structure, patch and
mod value, and rebuild parity — never by address order. Mine existing evidence
first: retained traces, pristine bytes, shipped data and compiled scripts,
registries, RTTI, strings, dormant loggers, the pinned GPL source, current and
backed-up Ghidra, and prior campaign ledgers. Record a new capture only when a
preregistered question survives that mining, and then build the smallest
controlled probe carrying explicit positive, negative, adverse, and replication
controls.

### Evidence discipline

Recover what enters, what leaves, what changes, and under which conditions. A
recovered name, a plausible decompile, one observed call, a model report, or a
passing document gate is a lead with an evidence pointer — never
self-authenticating truth. Reproduce every load-bearing conclusion locally
before admitting it. Preserve open questions and the cheapest falsifier rather
than filling gaps with confident labels. Re-check prior arithmetic, hashes, body
ranges, multi-range bodies, aliases, and whether a test exercises the production
path.

### Ghidra promotion gate

Promote to live Ghidra only through the full gate: exact program and specimen
identity; a verified off-volume backup with a proven restore and open path;
isolated persistent scratch replicas; rollback probes; separate-process dry run,
apply, and readback; full non-target and program-metric comparison; thunk and
alias refutation; a verified POST backup; and tracked-snapshot refresh only on
byte equality. Never mutate Ghidra to show activity, and never let a report or
model recommendation stand in for that gate. The owning procedure is
[`reverse-engineering/ghidra/README.md`](reverse-engineering/ghidra/README.md).

### Carry into the rebuild

Carry sufficiently proven behavior into focused rebuild owners and parity tests,
keeping `OnslaughtRebuild.Core` deterministic and free of presentation,
filesystem, clock, process, network, and GPU dependencies. Maintain exact retail
entity → reconstruction owner → implementation → test mappings, and keep
released behavior, source-informed architecture, reconstruction choice, and
remaining uncertainty visibly separate.

### Preserve what you did not create

Read the pristine specimen and never write it. Treat the installed executable as
deliberately patched and never as byte authority. Keep `G:\BEA ROMS` read-only.
Never destroy save or career data. Never hard-delete lab evidence; stage it
through `tools/lab_quarantine.py` instead. Leave the uncommitted Godot toolchain
work, the two protected UnsetObjective files, the stale lane worktrees, and every
unrelated dirty change untouched unless explicitly directed.

### Delegation

Choose single-agent or coordinated execution situationally. Delegation and
external consultation are optional, bounded, and read-only by default; you
remain the sole integration owner and final authority.
[`reverse-engineering/REVIEW-PROTOCOL.md`](reverse-engineering/REVIEW-PROTOCOL.md)
owns the detail.

### Countable outcomes

End every work unit in one countable outcome: campaign or evidence advancement;
an authorized Ghidra promotion; a reconstruction or parity advance; or an
explicit open question with its cheapest falsifier and exact next command. After
two attempts at the same noise floor, change instrument or rotate frontier. Keep
durable owners aligned with verified reality, and supersede proven drift in
place.

### Completion test

This directive is not complete while any actionable function, residual,
contract, rebuild mapping, evidence join, or proven instrument retains an open
frontier. Milestones, closures, successful consults, and overnight progress are
progress, not completion.

### Current frontier

Updated 2026-08-13 after the 34-boundary live promotion. Recording what closed is not
narrowing the mandate; the completion test and every clause above are unchanged.

**Closed this session — do not re-derive:**

- The HUD `RenderBlur` question, against six instruments (PostRender scan, demo
  PostRender, `CHud__*` orphan census, shipped ASCII, Xbox `dxengine.cpp`
  anchors, PC-native coordinates). Only the Xbox/PS2 disassembly proper remains.
- Whether `CDXEngine+0x4CC`/`+0x4D0` are named anywhere — they are not.
- Target 7's two arguments: a per-viewpoint object pointer from `0x0089CE08`
  indexed by a zero-based viewpoint index, which explains both retained stack
  words.
- The observed trace route order is **static**, predicted exactly by the call
  tree, so it belongs at C1 and a Generation 24 must not pin it as C2.
- All seven descriptive HUD route names are tested: 0 and 5 refuted, 3 half
  refuted, 4 suspect, 1/2/6 consistent.
- The 34 MissionScript registry pointers missing from the saved 8,136-function
  project were proved as callable boundaries, admitted by one backed-up live
  Ghidra ceremony, separately read back, and synchronized to the tracked
  snapshot. The current structural census is 8,170; the new default-metadata
  functions remain outside the dated static-closure and demo-map tables. A
  separate reviewed addendum now gives all 34 bounded static C1 contracts and
  falsifiers, extending static-envelope coverage to every saved row without
  changing Generation 23 or Ghidra metadata.

**Active frontier, in priority order:**

1. **The 75-row MissionScript registry normalization.** This is one
   evidence-coherent metadata cohort: 54 default `FUN_*` handlers, the five
   message-name corrections at `0x00537410`, `0x00537500`, `0x005375F0`,
   `0x005377E0`, and `0x005378E0`, and 16 descriptive Tier-3 names that lose to
   shipped Tier-2 command vocabulary. Registry names are script-facing slot
   names, not recovered original C++ symbols. Preserve every ABI/signature and
   bounded mechanism fact; add no behavior claim merely from the registry.
   Keep the frozen 2026-08-12 name table for its pinned consumers and advance
   only the new 2026-08-13 projection and current checker.
2. **Name the 34 newly admitted registry handlers in a separate cohort.** Their
   boundaries and bounded static contracts are now tracked, but their default
   names/comments remain unchanged and they are not part of the exact 75-row
   existing-entry manifest. Use the registry only as Tier-2 script vocabulary;
   preserve each row's explicit unknowns and do not imply C++ symbols,
   signatures, runtime reachability, or reconstruction parity.
3. **Repair `0x0050FF10` separately.** Replace the stale pickup identity with
   `CWorldPhysicsManager__CreateExplosion` and the proved caller-cleaned
   one-index signature/comment. This is a one-row corruption repair with
   different evidence and must not be folded into the registry ceremony.
4. **Four HUD names describing the wrong subsystem** — targets 0, 3, 4, 5. The
   binary names none of them, so this needs a naming-convention decision before
   any promotion.
5. **CLOSED 2026-08-12 — documentation coverage.** All 170 functions the
   coordinate instrument covers that lacked documentation now carry at least a
   measured row: 29 unique functions across five per-file documents (`MeshPart.cpp`,
   `BattleEngineDataManager.cpp`, `WorldPhysicsManager.cpp`, `mesh.cpp`,
   `ParticleSet.cpp`) and 141 unique functions represented by 148 function/file
   rows in the mechanically generated `functions/coordinate-long-tail.md`,
   spanning 93 files.
   **Coverage is what closed, not understanding** — those rows are tabled
   measured facts, not behaviour contracts, and the documents say so. Three
   caveats are recorded with them: the instrument is factory-biased and its 827
   functions are not a random sample of the then-current 8,136;
   `monitor.h`/`Monitor.h` are
   one file the image spells two ways; and the per-file ranking counts
   coordinate rows rather than functions.

   Superseded history of this item, kept because it corrected itself twice:
   That audit read one `Address:` per document and missed every table row.
   Recounted across all addresses in all 1,056 `reverse-engineering/` documents:
   of 323 real-named coordinate-covered functions, **318 are mentioned somewhere
   and 5 are not**. Neither bound is useful on its own — "mentioned" is not
   "contracted", and the original measurement never defined which it tested.
   Now re-measured against a stated definition — documented means a dedicated
   function note or a table row carrying a purpose cell, not a bare mention.
   Of 323: 26 contracted, 127 tabled, **153 documented, 170 undocumented**.
   Corrected ranking: `MeshPart.cpp` 32, `BattleEngineDataManager.cpp` 31,
   `WorldPhysicsManager.cpp` 21, `oids.cpp` 20, `mesh.cpp` 19. The broken figure
   pointed at the mission-script VM; the real gap is mesh, particle and
   data-manager code.
6. **Generation 24**, if still wanted, parented strictly on Generation 23 and
   respecting the route-order correction above.

Rank from current evidence; a reproduced contradiction outranks this list.

### Directive revisions

- **2026-08-12 — directive established.** The prior longform goal was cleared by
  the maintainer. This section replaces the practice of encoding the whole
  mandate in the goal string, which could not be revised without re-setting the
  goal. No frontier was selected at establishment.
- **2026-08-12 — first frontier update, and a clarification of the ownership
  clause.** `Current frontier` was rewritten from "None selected" to record five
  closures and a ranked active list. The agent had initially read
  *"maintainer-owned … never narrow or complete it yourself"* as forbidding any
  edit to this section, and therefore left it stale while the evidence moved —
  which stalled the loop. The maintainer corrected that reading. **The clause
  forbids narrowing, weakening, retargeting, or completing the mandate; it does
  not forbid recording progress**, and leaving the frontier stale contradicts
  this directive's own instruction to keep durable owners aligned with verified
  reality. Recording closures and re-ranking open work is expected. Removing the
  completion test, deleting frontiers to make the goal satisfiable, or retargeting
  the mandate still requires the maintainer.
- **2026-08-13 — structural census advanced.** The 34 registry-proved callable
  gaps passed the full scratch/live/backup/readback gate and advanced saved
  Ghidra from 8,136 to 8,170 functions. The frontier now separates the 75-row
  registry vocabulary normalization from the one-row explosion-factory repair;
  neither structural admission nor re-ranking changes the standing completion
  test.

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
`developer_state.json` → `current_re_authority`. As of 2026-08-12 the exact
authority is canonical Generation 23 at
`local-lab/re-campaign-incident-recovery-20260808-v1/generation-23-cround-handle-event-arm-effects-v1/`:
READY SHA-256 `4471fdfe105340ad06c2ad28d945eb05e9bc94f002110888b164581ccf1a93fc`,
frozen reducer ID
`a757bc51cd8302cf0e889c7db72ca58f9d865597b250371444d8c2285537db09`,
and external authority receipt SHA-256
`12509207913b0116a94c923da7fe163c47de226b7733538baea54eb31df73ba8`.
Its independent replica is reproduction-only. Generation 73 supplied a
field-level projection oracle; Generations 12 through 23 then admitted bounded
Damage/Hit field-write contracts, one replicated zero-shield ApplyDamage
contract, the exact consumer-bound TokenArchive dispatch-table partition, and
the exact Mission-native SetPos boundary plus its replicated script-visible
position-copy contract and partial rebuild mapping, LockHit's retained
single-node removal path, and an exact static TokenArchive parser/corpus/factory
contract at C1, then the exact Mission-native UnsetObjective 3/13/3 partition
and C1 static wrapper contract without broadening them beyond their evidence,
then ten bounded retained-trace `CExplosion` internal slot-40 carrier calls.
The explosion entry, writes, returns, full dispatch envelope, and segmented
mesh-part behavior remain open. Generation 21 additionally admits only 7,513
strict-`CRound` slot-66 call-entry envelopes across two retained traces, with
7,204 gap-free returns and 309 raw orphan returns. No `CMissile`-style receiver
was observed; receiver writes, branch ordering, complete Move behavior,
original source spelling, and full rebuild parity remain open. Generation 22
additionally admits only 2,555 strict-`CRound` slot-0 call-entry-arm paths across
retained Level 521 and independent Level 512 recordings, with receiver/event-
pointer continuity and exactly one selected arm per invocation. Event 4002 and
`CMissile`-style placement were not observed. Generation 23 deepens that same
bounded slot-0 contract with 84 exact receiver-write pairs across five selected
invocations, retaining per-window continuity gaps and rejecting a universal
event-4000 sequence because the two sessions differ in writers, values, and
order. External effects, event 2000, event 4002, field meanings, broader
populations, original source spelling, and direct rebuild parity remain open.
The campaign remains incomplete and the next valid campaign generation is 24.
The saved `VFuncSlot_00_004d9910` name and grade remain unchanged. The bounded
addenda were appended to twelve exact live/tracked Ghidra comments only after
backup, replica, rollback, adverse-control, readback, and restore gates; no
name, signature, boundary, executable-byte, instruction, data, symbol, or
reference mutation occurred.

A separate Xbox sparse-symbol lane is also now safely promoted: isolated
Issue-11 and US-retail Ghidra projects contain 1,166 independently decoded
instruction-local source mappings apiece, with 425 exact PC/Xbox seeds over 93
presently known PC functions. Ninety-five Ghidra instruction sites were repaired
through scratch/apply/readback and fresh PRE/POST recovery gates without changing
either Xbox function inventory. The two Xbox projects and their backups remain
machine-local retail-derived evidence; the tracked PC-retail Ghidra snapshot is
still the single repository database owner. A read-only successor now places
1,065 anchors into 379 one-to-one current Xbox function pairs with zero
ambiguous components and leaves 101 symmetrically uncontained. Complete section
censuses isolate 14 named SDK/middleware sections but retain all 6,723 functions
in `.text` as a mixed-ownership frontier. A second read-only successor resolves
the 101 sites into the same 88 loose-instruction anchor partitions in both Xbox
builds and independently verifies 2,803 decoded instructions. The 12 PC-linked
sites touch 11 compiler unwind funclets and one ordinary `CMapTex` function;
the latter has only a 10-byte non-terminal Xbox fragment. This changes zero PC
function boundaries, semantic contracts, or reconstruction mappings. Original
source boundaries, complete `.text` ownership separation, whole-body or
semantic transfer, runtime parity, and final platform function counts remain
open.

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

### 2026-08-12 — the goal string became a proxy, and the directive became mutable

`## Current directive` was added, and it is the only mutable section in this
file. An agent's standing goal is now a short proxy that points at it rather
than a longform mandate encoded in the goal string itself.

The reason is mechanical: a goal string is set once and length-capped, so every
revision — a new frontier, a superseded pin, a corrected count — required
re-setting the whole goal, and in practice meant the live mandate drifted from
the evidence. A tracked section can be superseded in place, which is what the
rest of this repository already does instead of keeping parallel truth.

Two guards travel with the proxy, because the indirection is otherwise
self-defeating: the directive is maintainer-owned, so an agent may propose
changes but must not narrow, weaken, retarget, or complete it on its own
authority; and the goal is not complete while the directive still names an open
frontier. Without those, the process bound by the directive could edit the
directive that binds it.

Nothing above `## Current directive` changed in substance. The objectives, the
acceptance test, the evidence partition, and the standing constraints remain the
stable statement of what is wanted.

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
