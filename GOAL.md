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
> Last updated: 2026-08-15. Current measured status belongs in
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
canonical Generation 29 through successive mechanically verified generations,
maximizing defensible progress toward complete retail understanding, durable
function and behavior contracts, a materially improved live Ghidra
reconstruction, and Godot parity. This is a long-horizon execution mandate, not
permission to manufacture certainty, and not an instruction to produce process
theater in place of reverse engineering.

### Ground yourself before acting

Confirm HEAD is at or beyond `e7aa7548`. Confirm the pristine specimen SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`. Confirm the
Generation 29 READY
`fe61f69646c644a880134474869f1c577403e6aa5675730cd1f0c467660c9ac9` and frozen
reducer `8b86f5b568067aa4cdb438b658cd95a2c118ce8f8ef2541899eaa67815832587`
through the literal pinned verify command in
[`developer_state.json`](developer_state.json) → `current_re_authority`.
Generation 29 is the sole campaign parent, the next valid generation is 30, and
Generation 73 is a projection oracle that is never a parent or authority.

### Never collapse the evidence layers

Static-envelope closure covers the dated 8,136-function census against which it
was sealed. A later 34-row Mission-registry addendum bounds the resulting
8,170-row state at C1 static and a separate metadata ceremony records only its
Tier-2 registry vocabulary. Later ceremonies admitted 31 text-gap, 79
external-table, 24 JPEG/IJG callback, and 23 CRT P0 runtime boundaries, so the
saved structural census reached 8,327. The later D3DX ceremony adds two more
DEFAULT-source rows, so the rolling census is now 8,329. The 31 have bounded
provider-compatible classifications; the 79, JPEG/IJG 24, CRT 23, and two
D3DX rows remain default-metadata structural rows. Generation 29 represents
all 203 current post-Generation-23 rows as OPAQUE where no stronger semantic
grade exists.
All remain outside the frozen static-grade projection. None of
these counts is a final ceiling,
semantic recovery, or reversal. The PC demo
partition and the instruction-local Xbox source-line anchors are oracles, never
denominators for retail completion. Generation 29 carries Generation 28's
admitted campaign state onto exact db.18618 geometry without changing a
semantic grade and remains sparse.
Live Ghidra structural navigation may lead the
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

Updated 2026-08-14 after the external-table boundary promotion and current
`.text` ownership refresh, including the earlier 75-row MissionScript vocabulary
and one-row explosion-factory promotions. Recording what closed is not narrowing
the mandate; the completion test and every clause above are unchanged.

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
  snapshot. That structural census was 8,170; the new functions remain outside
  the dated static-closure and demo-map tables. A
  separate reviewed addendum now gives all 34 bounded static C1 contracts and
  falsifiers, extending static-envelope coverage to every saved row without
  changing Generation 23. A later separate backed-up metadata ceremony gave
  those 34 functions bounded Tier-2 registry names/comments/tags without
  changing bodies, ABI/storage, parameters, or campaign grades.
- Thirty-one exact text-gap bodies were later promoted through the same backed-
  up structural gate, advancing that census to 8,201 while preserving
  every 8,170-row PRE record exactly. They remain default-named structural rows
  with separate CRT/AMD/IJG-compatible static classifications, not campaign or
  runtime grades.
- Seventy-nine exact external-table targets were then promoted once through
  fresh PRE/POST backups, replicas, separate readback, tracked-still-PRE proof,
  tracked refresh, and restore probes. They advance the structural census to
  8,280 while preserving every 8,201 PRE row, but add no semantic grade,
  original linker identity, runtime contract, or rebuild mapping.
- Current saved-body `.text` ownership is independently closed at 1,811,691 /
  1,929,117 bytes = 93.912966399% across 8,329 functions / 8,459 exact ranges,
  with zero overlap. The five reviewed current-function jump fragments are now
  repaired existing bodies; the 24 reviewed JPEG/IJG callbacks are now exact
  default-metadata functions; and the 23 reviewed CRT P0 entries are now exact
  default-metadata functions. The later 25-byte CRT EH repair joins one split
  existing parent without adding an entry. The subsequent D3DX promotion adds
  two exact DEFAULT-source functions and removes 248 fully decoded bytes from
  the gap. The remaining 117,426 bytes are listing-
  partitioned high-yield code/data/padding queues. This is structural
  accounting, not a final function census or semantic score.
- The 75-row existing-entry MissionScript normalization passed its complete
  scratch/live/backup/readback gate and is synchronized to tracked Ghidra: 54
  former defaults, five message-name corrections, and 16 Tier-3-to-Tier-2
  supersessions. These are script-facing registry names, not recovered original
  C++ symbols, and no ABI or semantic grade changed.
- `0x0050FF10` is no longer the stale pickup factory. A separately backed-up,
  scratch-rehearsed, live-applied, read-back, and tracked-synchronized ceremony
  now records `CWorldPhysicsManager__CreateExplosion` with its proved one-dword
  caller-cleaned signature and bounded static comment. No body, instruction,
  executable byte, function boundary, or non-target function row changed.
- Documentation coverage for the 170 previously uncovered coordinate-instrument
  functions is closed: 29 unique functions across five per-file documents and
  141 unique functions represented by 148 rows in
  `functions/coordinate-long-tail.md`. This closes measured coverage, not
  behavior contracts. The instrument is factory-biased and its 827 functions
  are not a random sample of the then-current 8,136; `monitor.h`/`Monitor.h` are
  one file the image spells two ways; and the per-file ranking counts coordinate
  rows rather than functions.

  Superseded history of this item is retained because it corrected itself
  twice. The first audit read one `Address:` per document and missed table rows.
  Recounting every address across 1,056 `reverse-engineering/` documents found
  318 of 323 real-named coordinate-covered functions mentioned and five not
  mentioned, but a mention was not a contract. Under the final stated
  definition—dedicated function note or table row with a purpose cell—the
  pre-remediation split was 26 contracted, 127 tabled, 153 documented, and 170
  undocumented. The corrected leading gaps were `MeshPart.cpp` 32,
  `BattleEngineDataManager.cpp` 31, `WorldPhysicsManager.cpp` 21, `oids.cpp` 20,
  and `mesh.cpp` 19.

- **The Mission `Damage` native's rebuild blocker (2026-08-15).**
  `C-8c445f1e27de9913` (`IScript__Damage @ 0x005348C0`) was the campaign's only
  `CONTRACT_ONLY` row: `C2_BOUNDED_RUNTIME` evidence with no rebuild
  implementation and `parityTests: UNMAPPED`. It now has both, plus three
  evidence advances that did not exist before. A decode of all 25 hash-pinned
  Level 100 script objects proves the shipped Level 100 content issues **366
  native calls across 40 commands and never native 69**, so reaching it there is
  a property of the released VM, not of released content. A shipped-source
  census then found the **first evidence that shipped authored content calls
  this native at all**: six authored call sites in four levels, which the pilot
  had explicitly recorded as unestablished. That is authored source, not proved
  execution — no `SetScript` attaches those scripts, so attachment comes from
  level data and is unverified. A pristine-specimen read of vtable slot
  `+0xA0` resolves `CBattleEngine 0x005D89C4` to `CBattleEngine::Damage
  @ 0x0040A890` and the measured receiver `0x005E24DC` to `CUnit__ApplyDamage
  @ 0x004F9A90`, joining three existing contracts under one proven
  receiver-selection rule. Generation 29 stays frozen and the campaign still
  reports `CONTRACT_ONLY 1`; only the rebuild and evidence layers moved.
- **A natural Mission `Damage` call is measured (2026-08-15).** Two earlier
  claims in this entry were wrong and are corrected: a retained trace *does*
  reach a shipped call site, and `hive.msl` *is* proved attached. Querying the
  level-720 trace — no elevation, no gameplay, 240 s — returned two gap-free
  `CALL_ENTRY_RETURN` envelopes. On shipped content the Mission VM dispatcher
  at `0x0052EB54` enters the wrapper, which forwards
  `amount = 122.61930847167969`, `source`, `applyShields = 1`,
  `meshPart = -1` — the forced pilot's tuple, confirmed naturally. The
  two-arm `+0xA0` reading is superseded: the prison receiver's slot 40 is
  `CBuilding__VFunc_40_004179a0`, a **forwarder** to `CUnit__ApplyDamage`, so
  `+0xA0` is a per-class virtual that some classes implement and others
  forward. Receipt `call-context.jsonl` SHA-256 `5cd0f261…92e4b0`.

**Active frontier, in priority order:**

1. **Recover the highest-confidence callable units and body repairs in the
   current 117,426-byte `.text` gap.** Continue re-grounding the remaining
   code-shaped cohorts against current `db.18618` geometry, then use cross-build
   shape, current listing state, incoming control flow, alignment, and library
   classification to prove exact boundaries; do not infer entries from linear
   decode alone.
2. **Preserve Generation 29 as the exact db.18618 authority.** Advance
   Generation 30 only after a mechanically complete structural, semantic, or
   runtime change; keep frozen reducers immutable and do not pin HUD route order
   as C2.
3. **Deepen coherent semantic/runtime/rebuild slices.** Prefer existing traces,
   Xbox sparse-symbol joins, shipped data, and current static contracts before
   recording new runtime evidence; carry only proved 5-to-10-contract slices
   into existing reconstruction owners.
4. **Four HUD names describing the wrong subsystem** — targets 0, 3, 4, 5. The
   binary names none of them, so this needs a naming-convention decision before
   any promotion.
5. **Reach the battle-engine arm of `Damage`.** The level-720 natural call is
   now **measured** (see the closure above), which leaves one arm untested.
   `CBattleEngine::Damage @ 0x0040A890` is covered at `level731`, `level732`,
   and `level854`; query those three for whether it is reached *through*
   `0x005348C0` rather than by weapon or collision code. Same instrument, no
   elevation, no gameplay. Level 720 also passed `source` equal to the receiver
   pointer, so a different receiver/source pair is still needed to separate
   "source" from "self".
6. **Only then, the hive contact.** It stays open but is now the harder of two
   natural paths rather than the only one.
   [`tools/RUNBOOK-level521-native-capture.md`](tools/RUNBOOK-level521-native-capture.md)
   already targets this native and names the act: fly the battle engine into
   the Hive boss. The level-521 index proves `hive.msl` is attached and live
   (its uniquely-authored `Teleport` executed) while leaving `0x005348C0`
   uncovered, so the gap is the player collision, not attachment. Cost is the
   blocker: TTD runs this game **~62× slow** (301 s recorded = 4.85 s of game
   time). `tools/Test-Level521NativeCoverage.ps1` scores such a take, and
   unattended recording needs `TTD.exe -installservice` once — the missing
   `TTDService` is why every recording prompts today.

Rank from current evidence; a reproduced contradiction outranks this list.

#### `F:\DS DEEP Review` integration — recorded 2026-08-16

The standing goal points here for specifics so they can be revised without
re-setting it. Counts marked (est) come from reviewer sampling and are replaced
by byte-derived manifests as those land.

**Verified grounding.** The pristine specimen and the Gen-29 READY pin
`fe61f696…c9ac9` are byte-identical to ours, as are all eight baseline campaign
TSVs, and the 14,438 contract IDs join 1:1 with zero orphans. An independent
pass re-checked all 8,737 declared body ranges and 1,143 residual heads against
the specimen: zero missing files, zero length mismatches, zero byte mismatches.
The bundle layer is trustworthy and re-derivation from it is cheap.

**What the drop is not.** Its adjudication layer decided 1,179 of 1,539
conflicts by regex over agent prose without opening an artifact, while emitting
rationales asserting byte evidence. 923 rows carry a false
`AGREEMENT primary==adversarial` label because `build_ledger.py` collapses
issue classes, and 905 terminal `FLAGGED` rows carry no class at all. Its
validators accepted 11 of 16 deliberately fabricated shards, and five of six
gates cannot fail anything. Both passes ran one model, so lane agreement is
correlated error rather than corroboration.

**Cohort order.** Each cohort promotes only after every row in it is re-derived
from pristine bytes, and only through the full Ghidra gate.

| # | Cohort | Size | Disposition |
| ---: | --- | ---: | --- |
| 1 | BOUNDARY, restricted | **41 of 77 (byte-derived)** | Manifest complete; ready for ceremony once preconditions clear |
| 2 | ABI, byte-provable | ~548 of 1,001 (est) | Promote after per-row `RET n` / `ADD ESP,n` check |
| 3 | NAME, Tier 1 only | **33 (anchor-verified)** | Promote; each re-proved twice, zero re-proof failures |
| 4 | NAME, demotions | **116** | 90 neutral `_T3_<addr>` placeholders + 26 descriptive relabels |
| 5 | XREF | 73 | Byte-check each; 59 are single-lane |
| 6 | COMMENT / OTHER | 254 | Defer; documentation grade |

**BOUNDARY, re-derived 2026-08-16.** The 77 is not a ledger count — only 55
rows carry a terminal `FLAGGED(BOUNDARY)`; 77 comes from the report's
categoriser (terminal suffix, else `primary_issue`, else `adv_issue`), a rule
that reproduces the whole 2,383 distribution exactly. Subtypes: FILL_HOLE 23,
CREATE_NEW_FUNCTION 17, CORPUS_ROW 12, EXTEND_TAIL 10, RET_IMM_SPLIT 5,
JUMP/SEH table 3, UNCLEAR 3, EXPORT_BUG 2, FALSE 2. **41 rows are promotable,
recovering 3,293 bytes**, each re-derived by linear sweep from the entry with a
branch high-water mark and each byte-proof re-read from the specimen; zero
invariant violations and zero overlaps. Eleven further rows carry wrong
addresses in their notes but a correct extent, so they promote on the derived
range, never the quoted one.

**Excluded — do not promote.** 28 unique rows, having removed a double count:
`0x00455d9b` and `0x005d6b71` are RES-lane and already inside the corpus-12.

- All 469 `DECOMPILE` rows. Decompiler output is regenerated on demand, so
  there is no stored artifact to mutate.
- The 17 BOUNDARY rows whose correct action is **create a function**, not
  extend one. `0x0055d988 __global_unwind2` ends correctly at `0x0055D9A7`;
  extending it would swallow the separate routine at `0x0055D9A8`–`0x0055D9C9`.
- Four demonstrably false rows: `0x00455d9b` and `0x005d6b71` assert a
  recorded-versus-pristine byte mismatch that reproduces as byte-identical;
  `0x00466ba0` argues from a declared end the metadata does not carry, putting
  its "25 bytes past the end" inside the declared range; `0x0052d3d0` is
  contiguous to its `ret` and is a `disasm.tsv` mis-decode misfiled as a
  boundary.
- Two `ExportBundles.java` export-bug rows, and two UNCLEAR rows whose naive
  fill would swallow `CRT__UnlockByIndex9_005621b9`, `…_00562307`, and
  `CRT__UnlockHeap9_SbHeapMsizePath` — caught by the overlap detector.
- **Verify exclusions too.** `0x0056defa` was carried on the export-bug list
  and is in fact a genuine 30-byte fill: both gaps are that function's own SEH
  filter and handler funclets, dword-referenced from scope tables `0x005e69e4`
  and `0x005e69f0`, matching nine promoted CRT rows in shape. An exclusion list
  inherited from a report is a hypothesis like any other.
- The 22 `CBattleEngineJetPart` / `CBattleEngineWalkerPart` NAME proposals. The
  image contains no `JetPart`, no `WalkerPart`, and neither `.cpp` path, so they
  are SOURCE grade and have no rung in the naming convention.
- The 73 soft calling-convention ABI rows — `__fastcall` versus `__thiscall` on
  a receiver-only function is byte-indistinguishable, as the campaign itself
  states at `0x004013d0` — and the 81 `calling_conv=unknown` rows, which record
  honest database state rather than a defect.
- The 53 FLAGGED rows on RES/UMT/SYM/PAD lanes, twelve of them BOUNDARY. These
  are Gen-29 corpus records, not Ghidra objects; correcting them is a campaign
  edit, and two of the ones checked are already known false.

**Preconditions — both CLEAR as of 2026-08-16.**

*Re-pin.* The drop's `inputs/readback/functions.tsv` is byte-identical to our
own **pre-demotion** readback, so the drop sits exactly one ceremony behind
`5c82208f`. Across 8,329 rows each side there are zero only-in-drop rows, zero
only-in-ours, **zero body-extent differences**, and exactly four name
divergences — the four HUD routes we demoted (`0x00483530`, `0x004858d0`,
`0x00485d50`, `0x00486940`). The drop is internally split: all 8,813 bundle
`meta.tsv` files are **current** with zero name mismatches, while the index,
manifest, shard rows, and ledger `entity_key` are stale. **A ceremony therefore
reads current state from bundle `meta.tsv`, never from the ledger key.** All
four stale addresses carry FLAGGED NAME rows whose finding simply *is* the
demotion we already landed.

*Duplicate addresses.* 309 confirmed (308 with two rows, one with three). The
111 splits as 43 base-verdict differences — exactly the reconciled set — plus
68 class-only and 198 identical. The 68 are not 68 conflicts: 47 are an
annotation artifact of `build_final_ledger.py`'s
`terminal = pv if pv == av else (av or pv)`, which overwrites a class when one
lane wrote a bare `FLAGGED`; the remaining 21 are 18 ROLE_DIFFERENT and 3
GENUINE_CONFLICT, with zero unresolved. That same merge rule silently discarded
two real DECOMPILE defects, at `0x00577de8` and `0x0057828b`, which no ledger
row now carries.

*Two further BOUNDARY refutations.* `0x005abb00` and `0x005abdb0` claim
"ranges 2-3 not exported"; the bundles ship every range (655 and 549 bytes,
matching declared `bodyBytes` exactly) and the inter-range gaps are alignment
NOPs. The boundary lane reached the same verdict independently. Both are absent
from the 41-row manifest, as are all six refuted rows and all four
stale-named addresses; the cohort is 23 FILL_HOLE, 10 EXTEND_TAIL, 5
RET_IMM_SPLIT, and 3 JUMP/SEH-table rows.

**NAME, re-derived 2026-08-16.** The 509 is composite, like the 77: only 368
rows carry a terminal `FLAGGED(NAME)`, the rest are plain `FLAGGED` with
`primary_issue == NAME`, over 504 unique addresses. Of 70 real proposals, **33
survive anchor verification** and were re-proved from scratch in a second pass
with zero failures; 116 become demotions; 8 are rejected. The strongest
promotion closes a falsifier left open by review: `0x0053f010` binds to
`CDXEngine` because all four call sites carry `MOV ECX,0x0089c9a0`, that global
is initialised to vtable `0x005e4fc4`, and its COL resolves to
`.?AVCDXEngine@@`. 347 rows stay UNRESOLVED — non-virtual members whose
declaring class no vtable can settle; they need body or call-site work, not
another naming pass.

**Two naming waves, and one is systematically wrong.** A mechanical audit of
all 439 refutations found that `Class__VFunc_N_addr` names measure exact (9 of
9) while `Class__VFuncNN_Description` names are off by one (6 of 6 —
`CInfantryUnit__VFunc65` is slot 66). The two waves used different base
conventions. **This affects existing database names well beyond this cohort and
should be swept separately.** The same audit found 38 refutations that do not
survive, because the recorded class genuinely owns the vtable slot, and 49
"invented" names that are drift from shipped source paths
(`CSpawnerThng` ← `SpawnerThng.cpp`) — misspellings rather than fabrications.
Rejections include two rows whose recorded name was already correct and only
the slot ordinal wrong, and one, `0x005503b0`, where the drop's own refutation
is false: it claims a full-image scan found no `CDXPatchManager` evidence, but
`C:\dev\ONSLAUGHT2\DXPatchManager.cpp` ships at file offset `0x25211c`.

**Campaign-layer corrections.** Discard the single `CONTRACT_REFUTED` row. It
claims `0x005d85d8` sits in bss with no file bytes, but that VA maps to file
offset `0x1D85D8`, which holds `00 00 a0 40` — exactly the 5.0f the Gen-29
contract recorded. Void the 1,013 zero-evidence residual verdicts: 153
`OPEN_CLASSIFICATION` plus 860 `TERMINAL_BOUNDED_AMBIGUITY` rows stamped
`CONTRACT_VERIFIED` with empty evidence and notes.

**Semantic pass.** The 8,102 fills read accurately — roughly 99% citation
accuracy under byte-level attack, with randomly sampled and least-informative
rows alike reproducing exactly — and they fill the semantic axis that
`function-c1-closure-2026-08-11` explicitly left open. But the pass has no
adversarial lane, its gate accepts C1 on three non-`UNKNOWN` fields, and zero
C0 across 8,102 functions is a completion-pressure signature rather than a
finding. No grade moves on it. Supply the missing lane in three tranches:
mechanically verify the 966 `STATIC_FORMAL_PROOF` rows, adversarially review
the 6,094 `SUPPORTED_BY_PE_STATIC_SPINE` rows, and route the 1,042
`SOURCE_CORRELATED_STATIC` rows into rebuild parity, where a focused test is
the cheapest falsifier available.

**Tranche 1 closed 2026-08-16.** A capstone-based verifier extracted 4,434
machine-checkable assertions from the 966 `STATIC_FORMAL_PROOF` rows and
checked each against the specimen: **948 CONFIRMED, 1 with warnings, 3 REFUTED,
14 uncheckable.** All three refutations are address-citation defects rather
than semantic ones — `0x004011b0` cites the `JS` one byte early, `0x00569c60`
cites the `JZ` two bytes early, and `0x00439af0` is systematically `-0x20`,
with one cited VA falling inside another instruction. The described behavior is
correct in each; only the addresses are wrong, which is still the class of
error that corrupts a comment or label pass. The verifier fails when it should:
five named corruptions all flipped to REFUTED, and a bulk sweep detects 100% of
RET-immediate and returned-constant mutations, 98% of mnemonics, and 86% of
global-store targets.

Carry its caveat rather than rounding it away. Its own tuning loop found 27 of
30 first-pass failures were verifier bugs, which biases toward CONFIRMED, and
~4.6 assertions per row cannot cover seven prose fields; frame-relative
displacement checks are WARN-only by design because prologue pushes shift ESP.
**"No machine-checkable contradiction" is a weaker statement than "tier-1
byte-provable," and this tranche closes only the former.** Semantic claims —
role names, "computes the adjugate", "lazy-inits the deletion set" — remain
unchecked and still need a falsifier each.

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
- **2026-08-13 — existing registry vocabulary normalized.** The separate
  75-row metadata cohort passed scratch and live gates with verified PRE/POST
  recovery, exact readback, and tracked-snapshot synchronization. The frontier
  now starts with the 34 newly created default-metadata handlers, while the
  one-row explosion-factory repair remains a distinct corruption correction.
- **2026-08-13 — explosion-factory corruption repair.** The distinct one-row
  correction passed its own scratch, backup, live-apply, separate-readback, and
  tracked-snapshot gates. It is now closed without changing the campaign
  generation; the 34 new registry handlers remain the first active frontier.
- **2026-08-13 — new-function registry vocabulary normalized.** The distinct
  34-row metadata cohort passed scratch, PRE/POST recovery, one live apply,
  separate readback, exact non-target collateral, and tracked-snapshot gates.
  The frontier now moves to `.text` boundary/body recovery, the Generation-24
  carry refusal, and coherent semantic/runtime/rebuild depth; no campaign grade
  or completion condition changed.
- **2026-08-14 — current geometry reseeded as Generation 24.** The literal-
  pinned canonical and reproduction-only replica replays account for all 8,280
  current functions and all 27,780 eligible Generation-23 carry rows. The 154
  structural additions enter the campaign as OPAQUE; no semantic, runtime,
  Ghidra, executable, rebuild, or completion claim was added. The next valid
  campaign generation is 25.
- **2026-08-14 — five body fragments promoted.** A separately backed-up live
  ceremony repaired five existing bodies without changing the 8,280-function
  count. Exact body ownership advances by 1,258 bytes to 93.072115377%, the
  live/tracked project advances to `db.18614`, and all 8,275 non-target rows
  remain byte-identical. Generation 24 stays frozen on its `db.18613` input;
  the next campaign must re-ground the current geometry rather than repinning
  that reducer.
- **2026-08-14 — then-current db.18614 geometry reseeded as Generation 25.** Two
  independent snapshots and canonical/replica full replays agree at 8,280
  functions. All 27,089 eligible Generation-24 carry rows are accounted for;
  16 changed structural lineages are retired explicitly and one new 12-byte
  residual remains open. The five repaired functions stay OPAQUE, no semantic
  grade or runtime contract moves, and Generation 26 is the next valid parent.
- **2026-08-14 — 24 JPEG/IJG callbacks promoted.** A separately backed-up
  one-save ceremony advanced live and tracked Ghidra from 8,280/db.18614 to
  8,304/db.18615 while preserving every PRE row. It added 38 exact body ranges
  and 14,817 owned `.text` bytes, reaching 93.840186987%. Generation 25 remains
  frozen and a successor campaign must re-ground the new structural geometry.
- **2026-08-14 — current db.18615 geometry reseeded as Generation 26.** Two
  independent snapshots and canonical/replica full replays agree at 8,304
  functions. All 27,025 eligible Generation-25 carry rows are accounted for;
  eight changed structural lineages are retired explicitly and the 24 new
  JPEG/IJG rows enter as DARK/FUN/OPAQUE. No semantic grade, runtime contract,
  Ghidra project, executable, or rebuild owner changes. Generation 27 is the
  next valid parent.
- **2026-08-14 — 23 CRT P0 runtime boundaries promoted.** A separately backed-
  up one-save ceremony advanced live and tracked Ghidra from 8,304/db.18615 to
  8,327/db.18616 while preserving every PRE row. It added 24 exact body ranges
  and 1,131 owned `.text` bytes, reaching 93.898814846%. Generation 26 remains
  frozen.
- **2026-08-14 — then-current db.18616 geometry reseeded as Generation 27.** Two
  independent snapshots and canonical/replica full replays agree at 8,327
  functions. All 26,993 eligible Generation-26 carry rows are accounted for;
  37 changed structural lineages are retired explicitly and the 23 new CRT rows
  enter as OPAQUE with nine covered, ten partial, and four dark retained-trace
  states. No semantic grade, runtime contract, Ghidra project, executable, or
  rebuild owner changes. Generation 28 is the next valid parent.
- **2026-08-14 — CRT EH parent body repaired and db.18617 reseeded as Generation
  28.** A separately backed one-save ceremony joined the existing
  `CRT__LongJmpProbe_NoOp` parent across its proven 25-byte filter/handler gap
  without adding a function. Two independent snapshots and full campaign
  replays then account for all 26,845 eligible Generation-27 carry rows, retire
  the one changed structural lineage, and preserve all 72 scenarios. No
  semantic grade, runtime contract, executable, or rebuild owner changes.
  Generation 29 is the next valid parent.
- **2026-08-14 — two D3DX-compatible boundaries promoted to db.18618.** A
  separately backed one-save ceremony adds exact DEFAULT-source functions at
  `0x00595FC9` and `0x00596028`, preserves every 8,327 PRE row, advances the
  rolling census to 8,329 functions / 8,459 ranges, and raises saved-body
  ownership by 248 bytes to 93.912966399%. Generation 28 remains frozen on its
  prior db.18617 geometry; the two new rows receive no semantic or runtime grade
  here.
- **2026-08-16 — DS DEEP Review integration frontier recorded.** The maintainer
  set a long-horizon goal covering integration of the external
  `F:\DS DEEP Review` drop alongside coequal rebuild advancement. That goal is a
  short proxy that points at this section for revisable specifics, so the
  cohort order, exclusion lists, preconditions, and campaign-layer corrections
  are recorded above rather than in the goal string. Nothing in the mandate was
  narrowed or retargeted: the drop adds an annotation layer over Generation 29
  and changes no grade on its own authority. Five independent reviews graded the
  drop before any of it was accepted; the exclusions exist because that review
  found rows whose application would have damaged the database.
- **2026-08-15 — Mission `Damage` slice carried into the rebuild.** The
  frontier records one closure and one new open question. No Ghidra, executable,
  campaign generation, or semantic grade changed, and no frontier was removed:
  the completion test and every clause above stand. The new item 5 is added
  because closing the rebuild blocker exposed a runtime gap that no retained
  trace can fill, which is the kind of open question this directive asks to be
  preserved rather than papered over.
- **2026-08-14 — db.18618 reseeded as Generation 29.** Two independent
  snapshots and canonical/replica full replays agree at 8,329 functions. All
  26,841 eligible Generation-28 carry rows are accounted for; the D3DX pair
  enters as OPAQUE/DARK, one changed residual/contract/question/adjudication
  lineage is retired explicitly, and all 72 scenarios remain. No semantic
  grade, runtime contract, Ghidra project, executable, or rebuild owner changes.
  Generation 30 is the next valid parent.

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
`developer_state.json` → `current_re_authority`. As of 2026-08-14 the exact
authority is canonical Generation 29 at
`local-lab/re-campaign-incident-recovery-20260808-v1/generation-29-current-8329-db18618-v2/`:
READY SHA-256 `fe61f69646c644a880134474869f1c577403e6aa5675730cd1f0c467660c9ac9`,
frozen reducer ID
`8b86f5b568067aa4cdb438b658cd95a2c118ce8f8ef2541899eaa67815832587`,
and external authority receipt SHA-256
`1156ee18875a2892e3fb580716acc0867fd318bc3d4b403813b83e381331e93e`.
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
Generation 24 then reseeded those exact Generation-23 claims onto the
then-current 8,280-function/db.18613 geometry: all 27,780 eligible carry rows are accounted
for, the 154 added structural identities enter as OPAQUE, and no new semantic,
runtime, Ghidra, executable, or rebuild claim is made. Its 105 open residuals
(101 dark and four executed) reflect that sealed geometry rather than loss of the
6,019 exact terminal carries. The campaign remains incomplete and the next
valid campaign generation was 25. Generation 25 re-grounds the five repaired
body identities on exact db.18614 geometry, accounts for all 27,089 eligible
Generation-24 carry rows, explicitly retires 16 changed structural lineages,
and leaves one new 12-byte residual open. It changes no semantic grade,
runtime contract, Ghidra project, executable, or rebuild owner. Generation 26
then re-grounds the 24 JPEG/IJG structural functions on exact db.18615 geometry,
accounts for all 27,025 eligible Generation-25 carry rows, explicitly retires
eight changed residual/contract/question/adjudication identities, and represents
the new functions as DARK/FUN/OPAQUE without inventing semantics. Generation 27
then re-grounds the newer 23 CRT P0 structural rows on exact db.18616 geometry,
accounts for all 26,993 eligible Generation-26 carry rows, explicitly retires
37 changed structural identities, and preserves all 23 rows as OPAQUE without
inventing semantics. Generation 28 re-grounds the later CRT EH parent repair on
exact db.18617 geometry, accounts for all 26,845 eligible Generation-27 carry
rows, retires the one changed structural lineage, and preserves all 72
scenarios without changing a semantic grade. Generation 29 then re-grounds the
two D3DX-compatible functions on exact db.18618 geometry, accounts for all
26,841 eligible Generation-28 carry rows, retires one changed lineage, and
carries both new rows as OPAQUE/DARK without changing a semantic grade. The next
valid campaign generation is 30.
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
