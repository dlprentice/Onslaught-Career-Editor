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
> Last updated: 2026-08-23. Current measured status belongs in
> [`CURRENT_CAPABILITIES.md`](CURRENT_CAPABILITIES.md) and
> [`developer_state.json`](developer_state.json) (routing key
> `current_re_authority`). That object alone owns the campaign generation,
> READY/reducer pins, grades, verify command, and next-valid generation; do not
> copy those volatile values into this standing goal. Generation 73 is retained
> only as the projection oracle named by the post-loss claim-closure receipt;
> it is not a campaign parent or authority. Dated full-suite counts remain
> historical measurements, not a live inventory.
> `F:\DS DEEP *` paths are historical origins; the corpus is
> `local-lab\ds-deep-review*`.
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
> Set 2026-08-12; revised 2026-08-17 (full-RE mandate, Generation 30/31
> grounding, corpus relocation). Status: **active**.

### Mandate

Reverse the retail binary to completion as the prime directive. Drive every
function admitted by the rolling Ghidra authority — and every later-admitted
boundary — toward a defensible terminal state: a C2/REBUILD_READY contract, or
an explicit open question with its cheapest falsifier and next instrument.
Every claim is
byte-proven and two-witness gated; the Godot rebuild and the WinUI toolkit
consume this work as coequal outcomes. Advance through successive mechanically
verified generations and framework-gated Ghidra promotions, maximizing
defensible progress and landing promotions rather than accumulating tooling.
This is a long-horizon execution mandate, not permission to manufacture
certainty, and not an instruction to produce process theater in place of
reverse engineering.

### Ground yourself before acting

Confirm HEAD and the pristine specimen SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`. Then read
and run the literal verify command in
[`developer_state.json`](developer_state.json) → `current_re_authority`; that
single object owns the campaign parent, exact geometry, READY/reducer pins,
grades, rebuild states, and next-valid generation. Read
[`reverse-engineering/ghidra/README.md`](reverse-engineering/ghidra/README.md)
and inspect the databases for rolling tracked/live Ghidra state. Never quote a
database version or infer live/tracked equality from this goal.
Generation 73 is a projection oracle and the DeepSeek drop's verdict layer is
an index, never a campaign parent or authority.

### Never collapse the evidence layers

Static-envelope closure covers the dated census against which it was sealed.
Later Mission-registry, text-gap, external-table, JPEG/IJG, CRT, and D3DX
ceremonies are retained as exact dated evidence in *Directive revisions* below;
their then-current population and body counts are not a live selector. Read
[`reverse-engineering/ghidra/README.md`](reverse-engineering/ghidra/README.md)
plus a fresh inspection for the rolling structural census and body ownership.
Those structural admissions remain distinct from semantic grades, and the
frozen Generation-29 projection records its then-admitted rows as OPAQUE where
no stronger semantic grade existed. None of those historical counts is a final
ceiling, semantic recovery, or reversal. The PC demo
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

Updated 2026-08-18 (pin hygiene). Recording what closed is not narrowing
the mandate; the completion test and every clause above are unchanged.

**2026-08-18 — stale pins superseded (do not revive).** At that cut, Generation
31 **v2** superseded the v1 directories (`generation-31-current-8329-db18624-v2`,
READY `2e77c62d…4219`); every `generation-31-*-v1*` directory is renamed
`*-superseded-by-v2-20260817`. The full Core suite was RE-MEASURED 2026-08-19:
This is a frozen receipt, not a live campaign selector; use
`developer_state.json` → `current_re_authority`. **854 passed / 2 failed / 856
total** (34 m). 730/730 on `a65826fa` (23 m 45 s)
and 729/729 on `fd5ab355` are retired history, not a live count, and the suite
is **not green** — both failures are `Level100FullChainTests` trajectory pins.
Neither is a live inventory: later L100 owners raised the static
`[Fact]`+`[InlineData]` count to **856**. Do not re-run the 25-minute
suite unless a Core owner changed; use the focused filter named by the
owner. Dated "lanes still running" / eight-lane / data34+trace-mine
in-flight sentences are not a liveness oracle; read the Kanban board and
`local-lab/hermes-kanban-campaign-2026-08-18/CHECKPOINT-2026-08-19-90pct.md`.
`F:\DS DEEP Review`, `F:\DS DEEP Review Extended`, and `F:\rows.tsv` no
longer exist; use `local-lab\ds-deep-review\` and
`local-lab\ds-deep-review-extended\`.

**2026-08-17 — maintainer directive, goal reset, and corpus relocation.** The
maintainer returned 2026-08-17 (~13:05 EDT) and directed: target the complete,
proof-gated reverse engineering of the retail binary so a proper rebuild can
proceed; relocate the DeepSeek corpus off F:; and work autonomously through a
~5-hour window with delegated decisions. The harness goal was set to this
directive. The corpus relocation is COMPLETE and verified: `local-lab\ds-deep-review\`
(frozen drop; 155,622 files, 532,623,995 bytes) is byte-exact against F: by
equal tree SHA-256 `9291c7ee…dfbf`; `local-lab\ds-deep-review-extended\` is
per-file byte-exact (95/95); `rows.tsv` is byte-exact; and the H: twin matched
the verified C: copy by equal tree SHA before removal. The F: and H: copies
were removed via `tools\lab_quarantine.py` staging into `D:\lab-quarantine\20260817`
(recoverable; manifest sha256s equal the verified copies), leaving
`F:\GhidraBackups` as the only retained F: content. Priority order is the carry
bridge → Generation 31 on db.18624 (the 16 mutation-killed contracts become the
first REBUILD_READY rows) → slot-instrument reproducibility → arity-36 promotion
→ pointer/vftable cohort → runtime-witnessed name corrections → Level100 crash
characterisation → falsifier close-out. Full-RE completion remains the standing
mandate; this 2026-08-17 list is **not** the current frontier
(SUPERSEDED 2026-08-19: carry bridge / Gen 31 v2 / arity-36 /
name-cohort5 / vftable65 are closed). Named-system RE + playable
startup→menu→L100 is the diet.

**2026-08-17 (autonomous shift) — SUPERSEDED 2026-08-18.** This paragraph
said Generation 31 was "in cut", F:/H: copies were "being staged", and
arity-36 still needed re-derivation. All three are closed: Gen 31 **v2**
is the authority, the F:/H: sources were staged then removed the same
day, and arity-36 / name-cohort5 / vftable65 promoted to live. Keep the
dated measurements below as history; do not resume from this paragraph.

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
- The exact 2026-08-14 saved-body `.text` ownership receipt remains independently
  closed and reproducible, but is historical rather than a live count. Read
  `reverse-engineering/ghidra/README.md` plus a fresh inspection before quoting
  the rolling population, range, byte, or gap totals. At that cut, the five
  reviewed current-function jump fragments were
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

1. **Carry bridge — DONE.** `_verify_generation30_campaign_carry` landed
   (`a0a3987b`) with literal pins from `77d6ae26…`, reproduced independently.
2. **Generation 31 — CUT AND INDEPENDENTLY VERIFIED 2026-08-17; v2 is
   the authority.** The first 16 `REBUILD_READY` rows land on db.18624
   (`6bd1f54a`): 14 rows raise C0_OPAQUE → C1_CANDIDATE_PARTIAL, row 13
   unchanged, the second GetFriction row `C-2b931aa6…` enters C1. The
   integration owner re-ran the frozen bootstrap with the measured
   on-disk pins: CAMPAIGN_VERIFIED, exit 0
   (`local-lab\gen31-verify-measuredpins-2026-08-17.log`). The leftover
   v1 ceremony steps named here (replica, cut-time inspect receipts,
   POST backup/tracked refresh, authority receipt) **completed the same
   day as v2** — item 3. Do not treat v1 READY `b99b6e4f…` or a
   "remaining ceremony" sentence as current.
3. **Gen-31 ceremony — COMPLETE (v2 re-cut).** Canonical + replica rebuilt on
   the current tree after the Godot smoke repair moved the rebuild-source
   fingerprint, both frozen-verified CAMPAIGN_VERIFIED, all eight ledgers
   byte-identical, cut-time live/backup/tracked Ghidra inspect receipts agree
   at 19 files / 187,403,141 bytes (tracked == live, no refresh needed), POST
   backup verified, and the external authority receipt is emitted and pinned
   (`current_re_authority` → v2; `0bf94104`).
4. **abi-two-witness-arity36 — PROMOTED TO LIVE 2026-08-17.** The slot
   instrument visit-order question is settled 2026-08-17 (no flip) and all 36
   rows are byte-adjudicated (36/36 witness + RET anchors re-verify against
   the pristine specimen; `local-lab\arity36-readjudication-2026-08-17\REPORT.md`),
   and the spec pins the honest `LOWER_BOUND` exactness (`72bf182b`). The full
   gate then ran on live: census/dry/apply/readback all PASS, 36 rows changed /
   8,293 untouched / only the three signature columns moved, PRE and POST
   backups restore-proven, and the tracked snapshot refreshed on byte equality
   (live rolled db.18624 → db.18625; `local-lab\arity36-ceremony-2026-08-17\`).
5. **Pointer/vftable cohort — PROMOTED TO LIVE 2026-08-17.** The typed
   `SET_DATA_POINTER` verb landed in the framework (75-test suite green) and
   the 65-slot cohort ran the full gate: rehearsal and live identity/dry/apply/
   readback all PASS (db.18626 → db.18627); each pointer is typed with its
   recovered class identity, zero function rows moved, PRE/POST backups
   restore-proven, tracked refreshed on byte equality. The 34 `.data` rows of
   the original 99 were correctly excluded (their COL anchors fail — a
   different table shape); 65 is exactly the objective's RTTI-vftable count.
6. **Runtime-witnessed name corrections — PROMOTED TO LIVE 2026-08-17.** The
   five-row `name-cohort5` landed through the framework (db.18625 → db.18626):
   `0x0048c3b0` → `CInfluenceNode__CalculateInfluence`, `0x0052ff20` →
   `ScriptCommandRegistry__InitBuiltins_thunk_0052ff20` (jump thunk to the real
   InitBuiltins), `0x005363e0` → `IScript__GetPlayer`, `0x0043a860` →
   `CExplosionStatement__VFunc_3_0043a860`, `0x004398f0` →
   `SharedVFunc_T3_004398f0` (owner refuted; neutral placeholder). Rehearsal and
   live receipts in `local-lab\name-cohort5-{rehearsal,ceremony}-2026-08-17\`.
7. **Falsifier frontier — CLOSED 2026-08-17.** `0x004e2b30` terminal (no
   vftable store; class unrecoverable from specimen), `[obj+0x260]` polarity
   settled (2 = walker, 3 = flight), `0x0043a860`/`0x0052db60` statically
   settled, `0x005363e0` terminal carrying its slot-21 GetPlayer witness
   (`local-lab\falsifier-closeout-2026-08-17\CLOSEOUT.md`). The remaining name
   corrections join the name-cohort item.
8. **Continuous function-level RE.** Mine the retained 66-trace corpus and the
   relocated DeepSeek index to raise the 8,088 OPAQUE rows through bounded,
   byte-cited C1/C2 slices and rebuild owners. Reasoned "this consumes X and
   decides Y" hypotheses with explicit confidence labels are progress; the
   cheapest falsifier travels with every row.
9. **Core gate — RED as of 2026-08-19 (854/2/856), re-confirmed 2026-08-21.**
   Both failures are `Level100FullChainTests`: the chain tick pin (expected
   8404, actual 6572; the run still reaches Won at higher hull) and the
   Blaster observable count (153 vs the 154-162 range). See
   [`VALIDATION.md`](VALIDATION.md) and `developer_state.json` →
   `_CORE_SUITE_20260819`. The retired 729/729 and 730/730 passes
   (`fd5ab355`, `a65826fa`) are history. Historical host deaths stay
   attributed to environmental contention until reproduced.
10. **Organization and truth routing.** Consolidate the top-level, RE, and
    local-lab documents toward one current-truth path; retire directly into
    manifested `H:\graveyard\lab-quarantine\` with
    `tools/lab_quarantine.py stage` after confirming H: is mounted and
    writable; do not use D: or G: as intermediate staging or backup volumes
    (see the retirement rule in [`AGENTS.md`](AGENTS.md)); keep
    `developer_state.json`, `RE-INDEX.md`, and `CURRENT_CAPABILITIES.md`
    aligned as each promotion lands.

Rank from current evidence; a reproduced contradiction outranks this list.
Backlog (the 117,426-byte `.text` gap, the HUD naming-convention decision, the
battle-engine `Damage` arm, the hive contact, spine-tier field coverage) stays
recorded in the history above and does not gate the current frontier.

#### DeepSeek drop integration — recorded 2026-08-16; corpus now at `local-lab\ds-deep-review`

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
| 1 | BOUNDARY, restricted | **41 of 77 (byte-derived)** | **PROMOTED TO LIVE 2026-08-17** — tracked refresh still pending |
| 2 | ABI, byte-derived | **294 of 1,001** — *not* the ~548 estimate | Rehearsed; the 548 plan would have fabricated ABI state |
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

**Slot-ordinal naming — swept, and the two-wave reading is refuted.** The NAME
audit proposed that `Class__VFunc_N_addr` names are exact while
`Class__VFuncNN_Description` names are systematically off by one. A full sweep
of all **919** slot-encoding names across six spellings disproves it: **891
exact, 9 off-by-one, 7 gross, 4 aliased-but-matching, 8 not errors.** The
`VFuncNN_Description` spelling is 21 exact against 9 wrong — mixed, not a
convention. The earlier 6-of-6 sample came entirely from `CInfantryUnit`, where
6 of the 9 bad names live, and correctly-numbered names of the same spelling
sit interleaved in that same vtable. The defect is per-name, never per-wave.

*Proven cause, and it is neither candidate we proposed.* The delta is **+1** —
encoded one lower than truth — and delta −1 occurs **zero times** in 919 names,
so nothing in this database counts the RTTI pointer as slot 0. The namer took
slot 0 as `head+4`: all 9 satisfy both `encoded == index-from-head+4` and
`head+4` being that class's scalar deleting destructor. That is the "MSVC
vtable[0] is the destructor" assumption, false in this hierarchy, where slot 0
is `CUnit__HandleEvent` at `0x004f9820` and the destructor is slot 1.
**16 names need correction**, zero unresolved, no collisions; two `CTree` names
have the ordinal written in hex (`VFunc_27` is slot 39), and three carry a wrong
class label as well. The 8 `Destructor_VFunc01` names are correct as written —
each names its calling thunk's slot, not a vtable entry.

The NAME audit also found 38 refutations that do not
survive, because the recorded class genuinely owns the vtable slot, and 49
"invented" names that are drift from shipped source paths
(`CSpawnerThng` ← `SpawnerThng.cpp`) — misspellings rather than fabrications.
Rejections include two rows whose recorded name was already correct and only
the slot ordinal wrong, and one, `0x005503b0`, where the drop's own refutation
is false: it claims a full-image scan found no `CDXPatchManager` evidence, but
`C:\dev\ONSLAUGHT2\DXPatchManager.cpp` ships at file offset `0x25211c`.

**Semantic tranche 3 closed 2026-08-16 — and it is the rebuild feedstock.** All
1,042 `SOURCE_CORRELATED_STATIC` rows were checked against pinned source
`5352a81`: **885 SOURCE_CONFIRMED, 51 partial, 20 refuted, 86 uncitable**, over
1,857 GPL-tree citations. All 337 cross-checked disassembly bundles are
byte-exact against the specimen, so the evidence chain validates end to end.
Read `SOURCE_CONFIRMED` as "not contradicted" rather than "verified": only
**61% of confirmations land on the row's own subject**, the rest on a collateral
identifier the row merely mentions. The strict primary-identifier rate is 94.7%.

**Seventeen retail-versus-source divergences — tracked exceptions.** The
evidence partition requires recording each one:

- `0x004e0890 CSoundManager::CreateSample` — source takes three arguments (12
  bytes); retail `RET 0x10` pops **16**, and the body reads `[ESP+0x10c]` and
  `[ESP+0x114]`. The PC build carries a fourth parameter the Xbox source lacks.
- `0x005145f0 CController::CController` — source takes four arguments; retail
  `RET 0xc` pops 12. The PC constructor drops one.
- `0x0052af00` and `0x0052ba50` — source declares `()`; both retail bodies
  `RET 0x4`, so each takes one argument.
- `0x0042e610` — the binary's own `__FILE__`/`__LINE__` pair cites
  `Controller.cpp:967`, but the GPL file has **553 lines**. The retail
  translation unit is at least 1.75× longer than the drop, which quantifies the
  partiality rather than assuming it.
- Eleven string-constant divergences: the `!EVAH!` cheat literal, the
  `sysmem.csv` / `memstats.txt` / `memmap.txt` dump paths, several D3D error
  and leak strings, and `meshtex\basicpanel.tga` are all absent from retail
  though `meshtex` is present. Five of the seventeen are low-confidence,
  aligned on method name only.

**Two rows where the citation is right and our name is wrong.**
`0x0041c330 CCareer__GetGradeForWorld` is the free function
`CGrade GRADE(int world_num)` at `Career.cpp:640` — retail agrees with the
source, being `__cdecl` with no receiver and loading global `0x00624184`.
`0x0042f220 CSPtrSet__Clear` is `GenericSPtrSet::RemoveAll()`, wrong in both
halves.

**Rebuild feedstock: 188 prime rows.** 510 of the 1,042 sit in portable
subsystems (ActiveReaderSPtr 112, FrontendPageFlow 73, Sound 63, BattleEngine
46, EventScheduler 46, Camera 45, JetPart 30, Controller 30, WalkerPart 28,
Career 22, SaveStorage 15); 532 are recover-from-bytes. The 188 that are
confirmed *on their own subject*, portable, and agree with the binary are the
first real parity-test queue this project has had, led by the Camera,
EventScheduler, Controller, SaveStorage `CChunkReader__*`, and Music/Sound
clusters.

**Semantic tranche 2 closed 2026-08-16 — and it is the calibration result.**
All 6,094 `SUPPORTED_BY_PE_STATIC_SPINE` rows were run through the tier-1
verifier: 33,158 assertions, **5,405 CONFIRMED, 38 with warnings, 591
uncheckable, 60 REFUTED.** The raw pass produced 250 refutations and **190 were
checker defects**, found by adjudicating all 297 failures individually —
function-extent citations whose high endpoint can never be an instruction
boundary, traversal stopping at jump tables (some bodies only 4–35% covered),
idiom-start citations, and notation collisions such as `RET 0xc3` where `0xC3`
is the opcode. The fixes are targeted rather than lenient: the corrected
checker reproduces tranche 1 exactly at 948/3/14/1 with none of its three
refutations dissolving.

*The 60.* Twelve are semantic contradictions, all ABI: six wrong arities or
terminators and six with the cleanup direction inverted. `0x0050f600` and
`0x005387a0` are the priority pair — both assert a `RET` on a function that has
none, being vtable tail-dispatches, and both contradict their own `returns`
field. Thirteen are address-citation defects. The remaining 35 are checker
artifacts carrying no ledger defect.

*Coverage is the real finding.* Only one row is fully checked; 5,434 are
partial and 659 have no machine contact. Across 39,939 load-bearing fields only
**27.3% carry any assertion**: `inputs` 79.2%, `returns` 27.1%, `writes` 26.0%,
`receiver` 26.0%, `sideEffects` 15.0%, `failureModes` 10.8%, `preconditions`
**3.0%**. **1,230 CONFIRMED rows — 22.8% — rest on exactly one passing
assertion**, usually the RET immediate. The control quantifies the ceiling:
RET-immediate mutations are caught 99.6% of the time, but GWRITE and DISP
manage 86% and 93% only on call-free fully-covered bodies, and just **11% of
the tier is call-free and fully covered**. So roughly 95% of global-store and
displacement claims are not machine-falsifiable at all, and 5,914 passing DISP
assertions mostly mean the displacement appears somewhere in the body.

**Read `CONFIRMED` in this tier as "the argument-cleanup convention checks out
and little else does."** The `inputs` field and the body extents are settled;
nothing else is. The 659 no-contact rows are a smaller risk than the label
suggests — median body two instructions, 81% at three or fewer, and 25 sampled
by hand were all plausible with the inferred part explicitly hedged — but the
**21 with 40 or more instructions are checkable content lost to notation gaps**
and should be re-extracted first. Follow-ups the evidence supports: fix the 12
ABI contradictions and 13 address citations, and sweep the corpus for
`retn <param-bytes>` written on cdecl functions, since that house notation habit
was only caught where the extractor happened to see it.

**BOUNDARY scratch rehearsal 2026-08-16 — technical PASS, procedural NO-GO.**
Identity was verified from inside the database, not from a filename: specimen
`74154bfa…7750`, 8,329 internal plus 224 external functions, 551,143
instructions, 234,478 references. Dry run 41/41 with zero gate failures; apply
then **separate-process** readback 41/41, confirmed again by a second tool
recomputing body digests independently. Collateral proof: 0 functions created,
0 destroyed, **8,288 non-target rows compared and 0 changed**, non-target
raw-text digest identical PRE and POST, and every program-scope metric
unchanged including `memorySha256`, `referencesSha256`, and `commentsSha256`.
The project's own `ghidra_inventory_diff.py` independently reports
`created=0 destroyed=0 boundsChanged=41 namesChanged=0`.

*Seven adverse probes, seven refused* — overlap with a neighbour, end
mid-instruction, missing entry, current-state drift, dropping owned bytes, a
tampered manifest, and a live-looking project path. All were run **writable**,
so a broken gate could have persisted damage; afterwards the probe replica was
byte-identical to its baseline. The live project was hashed before and after
and is unchanged in sha256, size, and mtime.

*Why NO-GO, and none of it is a defect in the cohort.* No off-volume PRE
backup, restore probe, or read-only reopen has been done — a hard gate. No
existing applier could take this cohort, since each hard-pins `TARGET_COUNT`,
manifest sha, and PRE/POST counts from its own completed ceremony and the
README forbids repinning a one-shot owner; the necessary new applier therefore
has no mutator tests and no independent refutation, which `AGENTS.md` forbids
promoting. Only one replica was used where the precedent lane used two plus
staged mid-apply probes. Refused probes still printed `Save succeeded` and
rolled the checkpoint db, so a live run must do its gate pass `-readOnly` and
open writable only after the cohort reports OK.

*Two substantive items to adjudicate first.* **19 of 41 targets add 233 bytes
containing no defined instructions** — all five RET_IMM_SPLIT rows, all three
jump/SEH-table rows, `entry`, `__amsg_exit`, and nine fills. Earlier CRT-P0,
JPEG, and external-table lanes authorized bounded in-body disassembly, so if
the live promotion should disassemble those bytes it is a different mutation
shape needing its own rehearsal, and if not, the POST state must not be read as
complete. Separately the manifest's `endValidation` is False for `0x00472d50`,
`0x0047d750`, `0x0048a570`, and `0x00560181` while Ghidra's own
ends-mid-instruction gate passes all four: the linear sweep and Ghidra's
code-unit view disagree on those tails, which is expected for jump-table tails
but must be adjudicated rather than left as two answers.

**First rebuild slice landed 2026-08-16 — eight contracts, 77 parity tests.**
`RetailEventScheduler`, `RetailChunkReader`, `RetailAnalogueControls`, and
`RetailCameraLaws` own the released event-scheduler ring, in-memory chunk
framing, PC analogue-axis normalisation, and the aspect/zoom laws. All four are
dependency-free — no `using` statements at all — and nothing is wired into
`Simulation.Step`, so no existing Core trace hash moves. A 14-mutant sweep
killed 12 and proved 2 behaviourally equivalent; the lane also caught and
corrected one of its own false claims, having documented a mutant as fatal that
turned out to be a pure optimisation.

**Six more divergences, all on rows the manifest marks `AGREES`.** These raise
the tracked-exception count to 23 and show what `AGREES` does and does not
scope to:

- **A whole source stage is absent from retail.** `Controller.cpp:226-233`
  specifies four analogue reads and the `ANALOGUE_X_DEAD`/`ANALOGUE_Y_DEAD`
  `0.36f` clamps. The retail body at `0x0042DB40` goes from inlined
  `CalcNumMappings` straight to the `mPlaying` test with no axis read, and
  `0.36f` (`0x3EB851EC`) occurs **zero times** in the whole image. `AGREES` is
  scoped to bytes, args, ret, and strings — it does not mean the cited source
  range is implemented.
- **Compiler reciprocals, twice.** `PCController.cpp` says `/1000.0f` but
  `0x00514640` does `fmul 0.001f`, differing by one ulp at **81,462 of 140,001**
  raw axis values. `Camera.cpp:650` says `(fov/90)/2.0f` but `0x0041A681`
  multiplies by the rounded `1/90`, diverging on **41 of 180** integer FOVs.
- **Event numbers are `int16`**, not the `const int` the signature advertises:
  `CScheduledEvent::Set` writes a WORD and `0x0044B32E` re-reads with `movsx`,
  so 40000 round-trips as −25536.
- `CChunkReader__Read` is *understated* as `NOT_CROSS_CHECKED`; its bytes match
  `chunker.cpp:180-187` exactly, and its release build has the
  `ASSERT(ReadSinceChunk<=Size)` compiled out, which is what makes the silent
  over-read real.
- **There is no separate `CEventManager::AdvanceTime`** — it is inlined into
  `Update` at `0x0044B5C3`.

**NO-GO clearance 2026-08-16 — four of five blockers cleared, the fifth is the
mutation shape.** An off-volume PRE backup of the live project exists at
`D:\BEA-Ghidra-Backups\2026-08-16-boundary-cohort41-pre-live`, restore-proved
byte-exact and reopened read-only, giving four-way per-file equality across
LIVE, BACKUP, RESTORED, and TRACKED. The applier is hardened: **29 gates were
each provoked with a single-difference probe run writable and every one
refused**, with no probe ever producing an APPLIED verdict. Eight rows were
re-derived by recursive-descent traversal rather than the builder's linear
sweep — five reproduce exactly and three were traversal blind spots closed with
direct byte evidence, including an MSVC SEH filter/handler pair whose addresses
appear verbatim in the `_EH4` scope table at `0x005e5b60`. **No refutation
survived; the manifest needed no correction.** A second replica built from the
backup reproduces the first digest-for-digest, and a genuine mid-batch halt
leaves coherent state that restores byte-exact.

*The remaining blocker, and the premise needed correcting first.* "19 rows /
233 bytes with no defined instructions" actually means no instruction *starts*
in the added range. Those 233 bytes are 11 operand-tail bytes of instructions
beginning outside the range, 72 already typed as DATA, and only 150 genuinely
undefined; the true figure is **274 undefined bytes across 34 rows**. Precedent
is unambiguous — `setBody(` appears in exactly two shipped appliers and both
follow it with bounded disassembly, while the one non-disassembling boundary
applier refuses any target that is not already fully defined. **No completed
ceremony has ever left admitted bytes undefined.**

*But porting that precedent verbatim is measurably destructive here.* Measured
on a throwaway replica, the clear-then-disassemble shape clears 800
instructions, drives references **−48**, fails exact coverage on 11 of 41 rows,
and at `0x00450010` turns 58 defined instruction bytes into 65 undefined. The
minimal shape — bounded disassembly seeded only at the undefined runs — instead
yields **+90 instructions and +12 references with no escape beyond the proposed
bodies**. The fix is a V3 applier built on the correct generalisation of the
shared invariant: **every admitted byte must end fully *classified*, instruction
or defined data**, not "fully instruction-covered". The six operand-tail rows
and three table rows satisfy that by precondition and must not be disassembled;
disassembling the tables would be wrong. The measurement also exposed a real
database defect — in six rows Ghidra's existing decode inside the added range is
desynchronised by 2–3 bytes from the true stream.

*Adjudicated and not blocking.* The four `endValidation=False` rows are a false
alarm: three are jump/SEH data tables already typed as DATA with `endIsCUmax`
true and zero gap to the next function, and `entry` decodes 264 of 264 bytes,
its only irregularity being a `call exit` tail rather than ret/jmp. All 41 rows
have `endIsCUmax` true. Tighten `validate_end` to report those subtypes
distinctly rather than as a bare `False` that reads like a defect.

**Second rebuild slice 2026-08-16 — nine contracts, and a defect in our own
code.** `RetailCareerNodes`, `RetailCareerProgress`, `RetailWeaponStores`, and
`RetailJetFriction` bring the parity suite to **185 tests**, all passing, with
36 mutants swept and 31 killed; the five survivors were each *proved*
equivalent, notably float-versus-double division being innocuous by Figueroa's
condition with a 2×10⁸ operand sweep finding zero disagreements.

*The most valuable finding is a rebuild defect, not a drop defect.*
`Simulation.JetFrictionNumerator` gates its interpolated arm at
`speed >= 1_000`; retail's gate is **1.5** (`BattleEngineJetPart.cpp:628`,
constant `0x3FC00000` at `0x005D8BD8`, loaded at `0x00411B39`), and the
1000× scale is confirmed by that function's own `1_000`/`3_000` altitude bounds
standing for retail's 1 and 3. Jets at altitude ∈ [1,3) and speed ∈ [1.0,1.5)
get a flat 0.99 where retail interpolates to 0.98. **Five review passes over
these rows found nothing here — implementing them did.**

**Fixed 2026-08-17, and the reason it was deferred turned out to be false.** This
was left standing on the belief that it moves cold-start trace hashes and so
required a `DETERMINISM.md` re-pin. It moves **no** hashes — measured by
instrumenting the ladder directly: over a full cold start it is called **2,623**
times, the maximum speed ever passed is **602**, and the number of calls whose
altitude even enters the `[1_000, 3_000)` window is **zero**. The jet throttle
targets at most `JetMaximumSpeedPerTick = 900` (shipped `mMaxAirVelocity` 0.9),
which is *below* the band floor, so **no replay in this repository can reach the
gate** and the re-pin clause was never engaged. A green suite here would have been
**vacuous**, which is the trap worth remembering: a passing test that cannot see
the constant it guards is not evidence.

Because replay cannot supply a falsifier, the proof is a direct one — a test that
drives the integer ladder through the boundary, asserts the band is non-empty,
cross-checks every probe against the float-exact model bit for bit, and pins the
`>=` boundary at 1_499/1_500. Its **mutation kill is measured**: restoring the
gate to `1_000` fails that test while the other 21 rows still pass, which proves
both that the new test bites and that the pre-existing suite was blind to this
constant.

*SUPERSEDED 2026-08-18 — this "never completed" claim is false.* The
full unfiltered Core suite later passed 729/729 on `fd5ab355` and
730/730 on `a65826fa`. The 582/~729 aborted run and the host-crash
attribution below are a 2026-08-17 environmental observation, not the
current gate. Do not treat them as a reason to re-run the 25-minute
suite or to report the Core gate unmet.

*One gate was unmet on the morning of 2026-08-17 and is recorded rather than glossed.* The full
unfiltered Core suite had not then completed — with or without the change. The test
host crashes (never an assertion) at wildly varying points, and it **reproduces
on the pristine baseline with the change reverted**, so it is not a regression
signal. Attribution is inference, not measurement: machine commit charge was
36.6 GB of a 44.2 GB limit with two Ghidra JVMs, `cdb`, and several agent lanes
resident, and no dump or stack could be captured. The honest consequence is that
**the concurrency that speeds this work up is what prevents its own acceptance
gate from running**.

*Best run so far, 2026-08-17 on `a0469ffc` — still not a pass.* On a quieter
machine (8.2 GB physical free rather than 6.8) the suite reached **582 passed, 0
failed, 0 skipped in 28m01s** — and then a parallel test host crashed, the run
reported `Test Run Aborted`, and the process exit code was **1**. The project
declares 368 `[Fact]` plus 85 `[Theory]` carrying 361 data rows, so on the order
of **150 cases never executed**. Read it precisely: *everything that ran was
green, and the blocker is environmental rather than behavioural* — but 582 of ~729
is **not** a met gate, and must not be reported as one. Note also that a tee'd
pipeline's exit status is not `dotnet test`'s; take the code from
`PIPESTATUS`/`$LASTEXITCODE` or the run will look clean when it aborted.

*Three more divergences, again on rows marked `AGREES`, bringing tracked
exceptions to 26.* `GetGradeFromRanking` grades **NaN as `'S'`**, because
`if (f == 1.f)` compiles to `fcomp`/`fnstsw`/`test ah,0x40` — C3 alone — and an
unordered compare sets `C3|C2|C0 = 0x45`, so the mask hits and NaN takes the top
grade. `GetWeaponAmmoCount` **rounds rather than truncates**: the source casts
`(SINT)` but `0x0041449D` is a bare `fistp qword` under `/QIfist`, so 3.5 → 4
where the source says 3. And `GetWeaponAmmoPercentage`'s `mStoreHeat` branch is
**dead** — `test edx,edx` at `0x0041443F` sets flags nothing consumes, because
both source arms denote the same division and the compiler folded them.

*Two shipped defects recorded, not repaired.* The slot guard is `cmp eax,0x100`
against an `int[32]` store, so slots 256–1023 exist in the save and are
unreachable; and `IsEpisodeAvailable` dereferences the NULL its own
`GetNodeFromWorldNo` just returned, where the sibling `DoesBaseThingExist`
checks first.

**LIVE PROMOTION COMPLETE 2026-08-17 — the 41-row boundary cohort is in the
maintainer database.** Every gate held on the first attempt; nothing was
restored or repaired. The applier is `tools/GhidraApplyBoundaryCohort41V4.java`,
derived from V3 by an allowlisted edit of **9 lines removed and 11 added**, the
only substantive change being the containment gate — which now requires the
live project path by `equals` rather than `contains`, so no replica, restored
backup, or clone can satisfy it. Both repository-path refusals carry verbatim
and still run first. V3 remains unmodified and `LIVE_FORBIDDEN`. Its 37 tests
prove the derivation two independent ways — replaying the allowlist onto V3
reproduces V4's exact bytes, and every differing line must be claimed by an
allowlist entry — with negative controls confirming a weakened pin and a
deleted table check are both caught.

*Results.* PRE and POST backups both taken off-volume to `D:` and both
restore-proven by byte comparison and a read-only reopen. Live's tree digest
was byte-identical to the rehearsal base, so nothing had drifted. Dry
(`-readOnly`) 41× WOULD_APPLY, apply 41× APPLIED with 25 units cleared and zero
admitted bytes left undefined, separate-JVM readback 41/41 PASS. **POST pins
match V3's re-measurement with zero deviation**: 8,329 functions, 551,232
instructions (+89), 234,493 references (+15), 48,583 defined data, 3,907,629
undefined, 2,301 bookmarks. Collateral proof passes with the non-target digest
`96a0d2d0…641b5` identical on both sides and **8,288 non-target rows
unchanged**; the 41 target rows moved only in their geometry columns.

*The strongest single receipt:* the live `dry.tsv`, `apply.tsv`, `readback.tsv`,
and both inventory files are **byte-identical to the rehearsal's replica-a
receipts**. The live apply reproduced the rehearsed one exactly, which is what a
rehearsal is supposed to buy and rarely proves this cleanly.

*State.* Live is now 187,026,309 bytes and holds the promotion. **The tracked
snapshot at `reverse-engineering/ghidra` was deliberately left untouched at
187,009,925 bytes** and still holds the pre-cohort state — refreshing it is a
separate promotion requiring its own authorization, and live and tracked are no
longer twins until then. The pristine specimen still hashes `74154bfa…7750`.
Generation 30, all semantic grades, and the NAME, slot-ordinal, and ABI cohorts
were untouched.

**Third rebuild slice 2026-08-17 — and a systemic divergence class.** Eight
contracts across six new owners bring the parity suite to **327 tests** (later
measured at **501** across the 21 `Retail*` owners, in 2.4 s). The
mutation sweep ran 47 and killed 43; four survivors were each proved equivalent,
and a fifth apparent survivor turned out to be a **missing test** — the
`GoingIntoWater` arm selector coincides only over a sea-level water line, and
lifting the water to 4.0 makes the narrowing bite, so the test was added and the
mutant killed rather than the equivalence assumed.

**The systemic finding: `nDivergence=0` is a statement about identity, not
semantics.** Six of these eight contracts diverge from their source *text* on
unordered inputs, because the shipped compares read `C0` alone or `C0|C3` where
C's operators do neither. **Refined 2026-08-17 — the earlier statement was too
broad.** MSVC's `>=` and `>` idioms *are* NaN-correct: they emit `test ah,0x41`
(C0|C3), so an unordered compare fails as C requires. The offenders are the
**equality and truthiness** idioms, which emit `test ah,0x40` (C3 alone) or
`test ah,1` (C0 alone) and therefore mis-handle unordered inputs. Reading the
mask is what distinguishes them, so "check every float compare" stands while
"every compare diverges" does not. Jet `Gravity` returns `0.005f` when
`mEnergy == 0` — `test ah,0x40` then `je` yields `0.0f` only when *not* equal,
matching `BattleEngineJetPart.cpp:509` — and a NaN energy *also* returns
`0.005f`, so the divergence is that C semantics would give `0.0f`. (An earlier
draft of this sentence had that clause inverted, reading "where `mEnergy == 0`
returns `0.0f`"; the substance held but the polarity was wrong.) NaN speed and
NaN energy both fail
`AutoLevel`'s gates; a NaN store value counts as *below* capacity in
`CanWeaponFire` and opens the gate; and `ChangeWeapon`'s unordered compare
*accepts* where `value >= consumption` rejects. Combined with slice 2's
`GetGradeFromRanking` grading NaN as `'S'`, this is now a recurring class rather
than a curiosity: **MSVC's comparison idioms are not NaN-correct, and the
Xbox-era source cannot show it.** Any contract ported from source text without
reading the compare's condition-code mask is unverified on that axis.

*Two manifest defects.* `CBattleEngineWalkerPart::CanWeaponFire` at
`0x00414630` **has no manifest row at all** — a 128-byte gap between
`GetWeaponIconName` and `ResetConfiguration`. And the walker and jet
`CanWeaponFire` are **not twins**, though both sit at line 936 of their own file
and the jet's row is `AGREES` with `nDivergence=0`:
`BattleEngineWalkerPart.cpp:940` wraps the whole body in
`if (weapon->IsActive())` and the jet's does not, with the shipped code matching
each — `mov ecx,[eax+0x9C] / test ecx,ecx / je` at `0x0041463C` in the walker
and no such load anywhere in `0x00412570`. **A rebuild sharing one
implementation across both chassis would be wrong for one of them.**

*Constants read from the image, not headers.* Both `Gravity` jump tables were
walked out of the binary — `EBattleEngineState` declares `MORPHING_INTO_WALKER`
first, so reading the header as "walker first" inverts the law. `SUPERTYPE::
Gravity()` inlines as `0.01f` and `*0.2f` folds bit-exactly to `0.002f`
(`0x3B03126F`). `CWeapon` is absent from the drop entirely, so its five charge
levels, `-1` sentinel, `index*100` scale, and live charge at `weapon+0x60` were
recovered from bytes alone.

**ABI cohort re-derived 2026-08-17 — and the recorded plan was wrong.** The
~548-row promotion set written into this frontier came from reviewer sampling.
Re-deriving all 1,001 rows from bytes cuts it to **294**, and the difference is
not conservatism: the 548 plan would have **fabricated ABI state**. It would
have relabelled calling conventions the bytes cannot discriminate (144
targets), written signatures onto 103 functions whose live state is Ghidra's
DEFAULT *absence* rather than a defect, fabricated an EDX register argument on
30 `__fastcall` functions, and fabricated a hidden `__return_storage_ptr__`
stack parameter on 2 x87 returns — the last two hazard classes unidentified by
review. **165 targets are affirmatively refuted**: every byte-decidable axis
agrees with the live signature, so there is nothing to fix. Note also that the
1,001 rows are only 936 distinct targets, 924 of them in-image.

The manifest **never relabels a calling convention** (thiscall 238, stdcall 40,
fastcall 11, cdecl 5, all unchanged). It changes arity on 279, return on 8, both
on 7 — removing 190 phantom stack parameters and adding 96 proven ones. Arity is
cross-checked by an independent measure, the highest incoming-arg frame slot the
body actually reads, giving 157 EXACT, 71 CONSISTENT_LOWER, **0 CONTRADICTS**,
and disqualifying 13 rows outright. Re-pin found **zero drift**, correcting the
brief rather than confirming it: today's 199 changed functions have an empty
intersection with the cohort, and the comparator was proved non-vacuous by
feeding it those 199 and seeing exactly 158 signature and 1 geometry flags.

**Material safety finding — no headless rollback.** In this Ghidra 12.1.2 build
`endTransaction(id, false)` does **not** revert `Function.updateFunction`: 296
rehearsal targets survived an abort, because a headless postScript already runs
inside an outer transaction and the nested abort is a no-op. `Program.canUndo()`
is false, and headless writes a new db version even when the script throws.
**Reversibility must therefore be proven at the ceremony level — a replica
restored from backup being byte-identical — never at the transaction level**, and
the name-cohort applier's atomic-abort claim cannot be substantiated for
signatures. Required practice from here: evaluate every non-mutating gate for
every row *before* the first write, with data-type resolution done lookup-only
so no new type is ever defined, so no gate can fail mid-cohort. A fresh
pre-apply backup with verified restore is mandatory, not advisory. This is also
the root cause of the earlier observation that refused writable probes still
printed `Save succeeded` and advanced the checkpoint database.

**Ungated sandbox experiment 2026-08-17 — verdict: triage instrument, not a
mutation harness.** All 2,383 ledger rows were applied ungated in a
`NONCANONICAL_SANDBOX_NEVER_SYNC_TO_LIVE` project built from a restore-proven
backup; live and tracked were byte-identical to their PRE state at both the
start and end of the run. 508 applied, 2 refused.

*What the sandbox caught:* both `OverlappingFunctionException` refusals, exactly
the two rows a static pre-pass had predicted — and `0x0056080d`'s proposed end
`0x00560a49` **is another function's entry** (`CRT__DestroyCatchObject`), so the
extraction had grabbed the next function's start. Also the absence-to-assertion
conversion, quantified: `sigSource` moved DEFAULT→USER_DEFINED on 158 functions,
219 of 423 arity rows overwrote a Ghidra DEFAULT, and 363 landed on functions
whose calling convention is `unknown`.

*What it missed, and this is the point:* **all 165 refuted ABI signatures apply
cleanly**, as do the anchorless names and the `0x0044ca30` slot-108-of-a-68-entry
vtable attribution — which the run renamed to the literal string `recorded`,
with Ghidra's full cooperation and no warning. 70 distinct verified names
collapsed into that one word silently. The ~18-of-708 estimate held.

*The lane's own headline, worth keeping:* **the dominant damage was its
prose-to-mutation extraction, not the ledger's proposals.** 79 of 81 name
extractions were English words lifted out of evidence prose; the honest
expressible count is ~431, not the regex's 510. Extraction is the riskiest link
and it fails silently, which is why the drop carrying no structured target field
is the expensive part of integrating it.

**NEW PROMOTABLE COHORT — the XREF class is a defect in our own reference
graph.** Of 742 stored references to the 66 flagged addresses, 505 verify
byte-exactly as `E8` CALL+rel32, but **39 are typed `UNCONDITIONAL_CALL` where
the source byte is `E9`** — a tail JMP mistyped as a call — and a whole-image
pointer scan found a further **27 DATA references present in the bytes and
absent from the database**. 18 of 66 addresses carry a type contradiction and 24
of 66 a DATA discrepancy, with two cited claims reproducing exactly
(`0x004059c0` 18 raw versus 14 stored, `0x00405ee0` 15 versus 13).

Those counts are a **66-address sample, not the population** — the corpus
measurement below supersedes them at 1,399 and 122 — and the 2 "bogus"
PE-header references counted here are **withdrawn**: they are legitimate
`ImageBaseOffset32` RVA fields. Read this paragraph as the discovery, not as the
size or the verdict.

**Also decided from the populated database:** 131 of 234 COMMENT rows are stale
(129 name a symbol existing nowhere in the database), 9 of 20 OTHER rows resolve
— 5 confirmed frame-size defects, 4 confirmed mistyped thunks, and **6 that are
latent uninitialised-memory bugs in the retail binary itself** — and 31 of the
347 unresolved names are disambiguated structurally: 26 are `TEXT_RESIDUAL`
range labels that are not function entries, and 5 cite an address 16–112 bytes
*inside* a function whose entry lies elsewhere. The remaining 316 are blocked by
anchor absence in the image, which no database state can settle.

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

**The XREF class, sized and attributed 2026-08-17.** The class is real and it is
a **database** defect, not an exporter one — and that is now direct evidence
rather than inference. The exporter iterates `getReferencesTo` and writes every
reference with `ref_type` from Ghidra's own `RefType.toString()`, with no filter
and no type mapping anywhere in the write loop. So a reference absent from
`xrefs_to.tsv` was never created by Ghidra at all, and the mistyped edges carry
that type in the database itself.

The population is far larger than the flagged rows. Of 27,836
`UNCONDITIONAL_CALL` rows, **1,399 sit on an `E9` byte across 170 entities, and
all 1,399 resolve to the correct target** — the edge is right, only its kind is
wrong. The error is strictly one-directional: all 32 `UNCONDITIONAL_JUMP` rows
sit on `E9` and none on `E8`, so the correct label demonstrably exists and is
used. Separately, **122 of 14,110** four-byte-aligned `.rdata`/`.data` slots
holding a `.text` VA are missing, across 90 entities, structurally rather than
uniformly — in the window `0x005daaf8`–`0x005dab40` every third dword is absent
while its neighbour is listed, an RTTI vftable typing artifact. Adjudication of
the 73 flagged rows: 148 byte assertions at 134 holds, 5 refuted, 9
semantic-undecidable; zero rows fully refuted; every count the review gave
reproduced exactly.

**That 1,399 is not a cohort at all — the suspicion was correct and it is now
settled.** All 1,400 candidates (1,399 `E9` plus one `EB`) carry an explicit
**`FlowOverride.CALL_RETURN`** on a `JMP`: 1,400 of 1,400, none without. That is
Ghidra's deliberate and correct model for a **tail call**, so the label is a
faithful report of an intentional decision and the "wrong kind" reading was
wrong too. Proven by experiment, not argued: clearing the override on 12 sites
grew decompilation **181 → 378 lines**, made the decompiler inline callee bodies
so the named call vanished, and raised unreachable-block warnings. Retyping would
**destroy 1,400 correct call edges** — 4.91% of 28,502, touching 1,012 of 8,329
functions, and leaving **89 callees with no inbound call edge**, reading as dead
code. The below/above-`0x5d0000` split is not two populations: both are tail
calls, differing only in provenance. **The deliverable here is documentation** —
read `UNCONDITIONAL_CALL` on an `E9`/`EB` byte as "tail jump under
`FlowOverride.CALL_RETURN`" — and the lesson is that a large mechanical
population is not automatically a large mechanical win.

**What survives is class (b): 99 promotable rows**, the untyped pointer slots,
reproducing 14,110/13,988/122 exactly. Safety is measured, not assumed: all 99
target slots with no data defined and not inside any defined data, so nothing
Ghidra laid down is overwritten, and only **29** are read directly by code, so
only those can move any decompilation. Controls are the reason to trust it —
8,000 non-boundary VAs and 8,000 corrupted `E8` immediates all rejected with zero
leaks, 26,447 of 26,447 genuine edges accepted, and the control caught *itself*
false-rejecting three real pointer slots that read as printable UTF-16. Residual
risk to name: pre-typing individual dwords could block a later RTTI structure
application over the same bytes.

Most of the drop's own XREF numbers do not reproduce — 742 stored refs measures
1,170, 505 measures 996, 39 measures 10 in-cohort, 18-of-66 measures 8-of-65, and
the 27 missing DATA refs measures 21, with 27 being the count of the *mirror* set,
which looks like a sign flip. Only the two cited claims reproduce byte-exactly.
Three withdrawals stand: the `0x00401000` row is a false positive, the
`0x004013d0` count is 11 not 12, and the "2 bogus PE-header refs" are 11
header-sourced references, **all legitimate** `ImageBaseOffset32` fields. One
exporter-side defect sits outside the 73 — `index.tsv`'s `callers` counts every
inbound reference including vtable slots, so `SharedVFunc__Return2` reports 14 and
has **zero** real callers. Never rank or call a function unreferenced by it.

**The retained coverage indexes have a domain, and it bounds every reachability
claim.** The instrument installs a single whole-module watchpoint with
`AccessMask::Execute`, so data reads and writes are invisible **by access type**,
not by address range; `re_coverage_ledger.py` then clips to `[text_lo, text_hi)`.
So for an address in `.rdata`, `.data`, BSS or `.rsrc`, "0 traces" is a
**category error, not a measurement**, and a join reporting data symbols as
unreached describes the instrument rather than the program. Conversely a 0-trace
result for a `.text` address *is* load-bearing, and three such addresses are
genuinely never executed.

**Do not convert that into an address threshold.** `.text` runs to `0x005D7F9D`;
the highest *covered* VA is `0x005D050F`, an empirical high-water mark and not a
domain edge. Every miss below `0x005D8000` is a valid measured negative — a
mechanical `>= 0x005D1000` rule would wrongly flag **1,198 legitimate
`OPEN_DARK` rows**, the unwind funclets and cold tails. And quote denominators
with their root: `G:\bea-ttd` holds 72 `coverage.jsonl` files, of which **66**
are the level-opening campaign and the rest are 3 level-521 takes plus 3 pilots.
So 69 and 72 are reconstructible as wider-root joins; what is wrong is reading
either as the level-opening denominator, against which a per-address "69 of 72"
does not reproduce — three such addresses measure **66/66**, every trace. State
the roots a join walked rather than a bare count. An audit for tracked claims
resting on the category error found **none**: it is recorded as refuted, never
asserted, and the offending join lives only in the untracked drop.

**The open falsifiers closed 32 of 34 on free instruments** — shipped strings,
RTTI census, static derivation from pristine bytes, and the retained coverage
indexes. No TTD query, no debugger breakpoint, nothing above tier 1. That is the
directive's instrument ladder working as intended, and it is worth noticing that
*six of the falsifiers were themselves defective*: nine of ten contract rows have
an **empty** falsifier column, one demanded a runtime experiment for a string
sitting in `.data`, one named a `DSOUND.dll` that does not ship, two deferred to
sources or a PDB nobody has when the image's own RTTI answers outright, and one
proposed breakpointing the parameters of a function that takes none. A falsifier
that cannot be executed is not a plan.

Two results carry beyond their rows. **`0x0043a860` is wrong in both halves of
its name**: a run of one-per-type factory stubs stores each type code at
`[eax+4]`, recovering the enum — 6 is `CExplosionStatement` and **7 is
`CComponentStatement`** — so the owner is wrong *and* the number is wrong. And
the **cheat/debug gate is a live shipped affordance, not dead code**: `0x00662DF4`
is written via `[ebx+0x3c]` off the same `ebx = 0x00662DB8` base as
`m_bWindowed`, gated by the shipped switch **`-autoconfigtest`**. That correction
came from the lane withdrawing its own "dormant unless patched" claim after being
pointed at the documented trap that an absolute-address scan cannot see an
object-relative store — the same trap that once refuted a "this flag is dead"
caveat. Its accompanying switch-table "discovery" is *not* new; see
[`CLIParams__ParseCommandLine.md`](reverse-engineering/binary-analysis/functions/CLIParams.cpp/CLIParams__ParseCommandLine.md).

One row is now **terminal rather than open**, which is the right disposition and
under-used: `0x004e2b30`'s class name is *not recoverable from the specimen* — no
`CSoundEvent` among 667 RTTI type descriptors, in no vtable, named by no string.
Recording that as the answer beats parking it forever against a PDB nobody has.
Its honest loose thread is preserved: the function calls through `[esi]`, so the
receiver *is* polymorphic and a vftable must be installed outside the censused
window.

**A name-correction cohort is assembling from byte evidence**, independent of the
drop's NAME class: `0x0043a860`, `g_D3DDeviceIndex` at `0x0066061c` (refuted — a
packed display-mode selector, bits 0–15 / 16–30 / flag at 31, not an index),
`0x004398f0`, `0x005363e0`, `0x0052ff20`, and `0x004f0860`. Equally worth
recording are the names that **survived** so nobody re-opens them: `CActor` at
`0x00401b50` holds because `CActor` carries two Complete Object Locators, at
offset 8 and offset 0; `CWaypoint` holds on an ICF-folded body owned by three
classes; `g_Cheat_MALLOY` and `g_Cheat_LATETE` hold, the missing plaintext being
XOR obfuscation under the key `"HELP ME!!"`; and all four
`CAREER_mInvertY{Walker,Flight}_{P1,P2}` hold — the UTF-16LE UI labels at string
ids `0x38`/`0x39` settle the walker-versus-flight assignment that
[`CCareer__StaticInitDefaults.md`](reverse-engineering/binary-analysis/functions/Career.cpp/CCareer__StaticInitDefaults.md)
had recorded as *verification pending*. Neither cohort gets a bespoke applier:
both wait for the framework, which exists precisely to stop a fourth one being
written.

**The ABI contradiction class has a mechanical root cause, found 2026-08-17.**
Ghidra's `param_size` was transcribed into review prose as the RET immediate, and
that single confusion explains every inverted-cleanup row examined. *Refined:*
`param_size` is **the sum of the declared parameter *type* sizes**, not the
aligned stack-argument area — a `char` or `bool` parameter yields `psz=1` against
a `RET 0x4`, which is why three apparent self-ABI gaps (`0x0042b120`,
`0x00517d00`, `0x0052af00`) are not gaps at all. 12 confirmed became **17** once a
checker rule that passes `retn N (cdecl)` was dropped; it was defensible about
author intent but it hid text the bytes refute. A harder class sits underneath:
functions that **contain no RET at all**, tail-dispatching via JMP, where the
cited RET address is the last byte of the dispatch instruction and the byte is
`0x00` — `0x0050f600`, `0x005387a0`, `0x00453460`, `0x00453630` so far. A defect
in the review's prose is **not** evidence our database is wrong; only rows
implying a wrong convention, parameter count, or stack delta are mutation
candidates.

**The bulk lever does not generalise — swept, and the hypothesis is refuted.**
`param_size` confusion explains **5 of the 1,001** FLAGGED(ABI) rows, and the
histogram is `NOT_A_DEFECT` 989, `NO_RET_AT_ALL` 7, `PARAM_SIZE_CONFUSION` 5,
**`GENUINE` 0**. The reason is a **population conflation**, and it is worth
naming: the reviewers' shard prose overwhelmingly *does* distinguish the two —
the canonical finding in this drop is literally "declared `param_size 8` but
terminator is `RET 0xc`" — and where the confusion occurs it is in the *semantic
contract* text, not the shard note. The 17-in-a-sample rate came from a checker
over contract text, a **different population**, and none of the four exemplars
that motivated the sweep is even among the 1,001. So one class's root cause is
not transferable to a class that merely shares its name.

Staleness explains **zero** of it, measured rather than assumed: across all 924
in-image cohort addresses the drop's readback and today's live readback diverge in
**no** field — `paramSize`, `paramCount`, `callingConv`, `returnType`, `varArgs`,
body geometry, signature, name, `sigSource` — with the comparator proved
non-vacuous by flagging 41 `bodyBytes`, 23 `bodyRanges`, 18 `bodyMax` and 4
name+signature changes whole-image.

Corpus-wide, **990 of 8,329 declared bodies contain no RET** (976 tail-dispatch
JMP, 7 noreturn CALL, 4 ending mid-flow, and 3 truncated with the real RET just
past `bodyMax` — a *boundary* class, not ABI). Of the 983 genuinely RET-less, 63
still carry a RET assertion and only 6 are in the 1,001, so this is a ~6%
notation leak rather than a systemic failure. Dropping the lenient `retn N
(cdecl)` rule exposes 16 claims over 14 functions; ten are the clean shape and
all ten were byte-verified, but **nine sit outside the 1,001**. Three name their
own source in the text — "RET 4 (param_size 4)", "retn 0x30 (param_size 0x30)",
"retn 8 per meta" — which is direct evidence of the transcription mechanism even
though it does not generalise.

**Candidate supply is not the constraint; independent corroboration is.** 498
addresses imply a database correction (268 pop more than declared, 194 less), but
only **82 carry an independent witness** — the frame corroborator is sound only on
EBP frames, 252 of 924. So 416 of the 498 rest on the RET immediate *alone*, the
same single-assertion weakness the tier-2 calibration already flagged. Do **not**
promote at 498, and do not treat it as corroborating the earlier 294: they are two
different measurements under different tests, not one confirmed by the other. The
right next move is an instrument, not an adjudication queue — a path-correct
argument-slot measure (per-basic-block ESP abstract interpretation, or
caller-push-count corroboration from `xrefs_to.tsv`) lifts coverage from 27% to
near 100% and is cheaper than hand-checking 416 rows. Meanwhile the **23
prose-only corrections can land now**, since they need no Ghidra gate at all, and
the 141 `cc=unknown` rows should have their **arity** corrected while the
convention stays recorded as genuinely UNDETERMINED.

One scope limit, stated rather than buried: `GENUINE = 0` is scoped to the **RET
axis**. The receiver, phantom-parameter, return-value and varargs axes are
**unmeasured** — the ECX-receiver attempt was abandoned because the prose does not
distinguish "the convention passes `this` in ECX" from "the body reads ECX", and a
first pass produced 85 contradictions that were all regex artifacts. One
byte-refuted claim of a third kind did surface outside the population:
`0x004bfbb0`'s "RET 0x24 matches disasm" reads a six-byte body
`b8 24 00 00 00 c3`, where `0x24` is the **return value**, not a cleanup immediate.

**DECOMPILE has a mechanical root cause too, and it is not what the class name
suggests: the flagged rows are collateral, and the defects live at the CALLEE.**
The flag is "decompile sanity — phantom params, missing inputs, absurd
prototypes", and attribution is direct evidence rather than inference: the exporter
opens a `DecompInterface` and writes `getDecompiledFunction().getC()` **verbatim**,
so `decompile.c` is a pure function of pristine bytes × our database × decompiler
version. There is no stored artifact to mutate — but a *faithful* rendering can
still report a wrong database **field**, and it almost always belongs to a callee
rather than the address that got flagged. **Zero rows are defects in the drop's own
artifacts**, which is the opposite of the XREF result.

Three clean mechanisms account for the bulk. **266 rows reduce to a handful of
callee signature fields**, and **210 of them come from a single address**:
`OID__FreeObject_Callback` at `0x00449d40` is declared with one parameter while 657
call sites push four (`line, path, memtype, obj`) with `ADD ESP,0x10`, so the
decompiler drops the `__FILE__`/`__LINE__` plate everywhere. **SEH funclets are
inherent, not defective** — every `Unwind@` row carrying an `unaff_` uses exactly
`unaff_EBP`, because a funclet is entered with its *parent's* EBP and no C
prototype can express that. And **decompiler ESP desync** explains 29 of 41
non-funclet `unaff_` rows, each containing an indirect callee-pop call. Four rows
are simply arithmetically false prose: "decompile says `+0xd`, disasm proves
`+0x34`" describes pointer arithmetic on an `int*`, and 0xd × 4 = 0x34 — the same
address.

**The structural half of DECOMPILE is a shadow of the ABI cohort.** Of 29 genuine
database-defect addresses, **19 are already in the 294-row ABI set** with
`retImmediate` and `arityBytes` matching an independent measurement exactly — so
promoting ABI clears them for free, and no DECOMPILE cohort should be created. Ten
are new and byte-verified, including `sprintf` and `CConsole__AddString` declared
`varargs=false`, `CDXMemBuffer__dtor_base` declared `__fastcall(void)` when
`MOV ESI,ECX` is its second instruction, and three functions declared `__cdecl`
that pop their own stack — which a `__cdecl` function cannot do. **Three were
already documented in our own plate comments**: earlier campaign prose recorded the
defect and nobody converted it into a signature change.

*A tool defect worth fixing before it becomes live — now closed, and the
"latent" half of the claim was wrong:*
`tools/GhidraApplyAbiSignaturesV2.java` **unconditionally clears `varargs` and
asserts `false`** in both POST and readback, so it cannot carry a varargs row at
all. It was latent for that cohort — none of its 294 targets had `varargs=true` —
but **10 of the 8,329 functions in the database do** (measured 2026-08-17 on
db.18622), so a single added row would have stripped a real variadic function with
the applier's own POST gate certifying the strip. Fixed 2026-08-17 in the shared
framework rather than in V2, whose source digest its receipts pin: `varargs` is
now a manifest field of `SET_PROTOTYPE` in
`tools/GhidraApplyCohortManifest.java`, defaulting to **preserve**, with the
column left frozen for any cohort that does not bind it, POST/readback compared
against the manifest value, and both directions plus the preserve case provoked by
execution. `sprintf` (`0x0055de9b`) and `CConsole__AddString` (`0x0042b840`) are
expressed as the two-row `varargs-cohort2` spec, **rehearsed, not promoted**.

Two accounting notes. **469 is composite**: only 397 rows carry a terminal
`FLAGGED(DECOMPILE)`, the DECOMPILE-*touching* population is 490, and 21 land in
other classes because a terminal ABI suffix wins. And the lane drew its own
inference boundary rather than rounding it away: it hand-adjudicated 16 of 178
decompiler-behaviour rows, found no further database defect, and said plainly that
16 of 178 is not a census. It also **declined to publish 29 x87 return-type
candidates** because its FLD-versus-FST heuristic is noisy — the right call, with
the falsifier named.

Two smaller carries. A citation fix turned out to hide a **value** finding: the
constant at `0x0056d647` is the 80-bit long double **0.1**, not 10 — `cc`×8,
`fb`, `3f`, exponent `0x3ffb` at bias−4 and significand 1.6, laid out as a CRT
`_LDBL12`. And `0x004af110`/`0x004aede0` carry a clean three-cell **column
rotation** in the ledger, with otherwise correct content: a ledger fix, not an
extractor fix.

**The no-rollback finding extends, and this governs every future ceremony.**
Opening a project **without** `-readOnly` rolls the database file version on
close *even when the post-script refused and wrote nothing*. So a refused row
still moves the live version, "tracked still `PRE`" must be argued
**semantically** — a full readback bit-identical at program scope and across all
8,329 function rows — never by file digest, and gate provocations must never run
in write mode against live. Reversibility remains restore-from-backup only.

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
- **2026-08-14 — the then-active geometry was reseeded as Generation 24.** The literal-
  pinned canonical and reproduction-only replica replays account for all 8,280
  functions in that cut and all 27,780 eligible Generation-23 carry rows. The 154
  structural additions enter the campaign as OPAQUE; no semantic, runtime,
  Ghidra, executable, rebuild, or completion claim was added. The next valid
  campaign generation at that freeze was 25.
- **2026-08-14 — five body fragments promoted.** A separately backed-up live
  ceremony repaired five existing bodies without changing the 8,280-function
  count. Exact body ownership advances by 1,258 bytes to 93.072115377%, the
  live/tracked project advances to `db.18614`, and all 8,275 non-target rows
  remain byte-identical. Generation 24 stays frozen on its `db.18613` input;
  the next campaign had to re-ground that geometry rather than repinning
  that reducer.
- **2026-08-14 — db.18614 geometry reseeded as Generation 25.** Two
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
- **2026-08-14 — db.18615 geometry reseeded as Generation 26.** Two
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
- **2026-08-14 — db.18616 geometry reseeded as Generation 27.** Two
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
  then structural census to 8,329 functions / 8,459 ranges, and raises saved-body
  ownership by 248 bytes to 93.912966399%. Generation 28 remains frozen on its
  prior db.18617 geometry; the two new rows receive no semantic or runtime grade
  here.
- **2026-08-17 — full-RE mandate sharpened and the DeepSeek corpus relocated
  into the repo.** The maintainer directed complete reverse engineering as the
  prime directive and authorized autonomous delegated execution for a ~5-hour
  window. `F:\DS DEEP Review`, `F:\DS DEEP Review Extended`, and `F:\rows.tsv`
  were copied into gitignored `local-lab\` (`ds-deep-review`,
  `ds-deep-review-extended`, plus `rows.tsv`) with byte-exact verification,
  then staged out of F:/H: via `tools\lab_quarantine.py`. **As of 2026-08-18
  those F: paths do not exist**; F: holds `GhidraBackups` only. The harness
  goal now proxies this directive.
- **2026-08-18 — pin hygiene only; mandate unchanged.** Generation 31 v1,
  729/729 as a live Core count, dated "lanes still running" sentences, and
  present-tense `F:\DS DEEP *` paths were superseded in place. The standing
  constraints (pristine read-only, save preservation, no hard-delete, Core
  determinism, one live-Ghidra lock, two-witness claims) are untouched.
- **2026-08-19 — 730 dated as last measured, not live; 2026-08-17 frontier
  list marked superseded.** Static Core inventory after later L100 owners
  is 856 `[Fact]`+`[InlineData]`. Handoff pointer is
  `CHECKPOINT-2026-08-19-90pct.md`. Mandate unchanged.
- **2026-08-16 — DS DEEP Review integration frontier recorded.** The maintainer
  set a long-horizon goal covering integration of the external
  `local-lab\ds-deep-review` drop alongside coequal rebuild advancement. That
  goal is a short proxy that points at this section for revisable specifics, so the
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

## Replay authority routing (do not restate volatile counts here)

Standing complete-RE progress is **not** the Gen10 handoff below and is no
longer selected from the damaged Generation-73 candidate chain. Read
`developer_state.json` → `current_re_authority`. Its generation, READY/reducer
pins, grades, verify command, and next-valid generation live only there and are
deliberately not restated here. The Generations 12-29 narrative that
follows is a frozen 2026-08-14 historical record, not a live selector.
Generation 73 supplied a
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
then-active 8,280-function/db.18613 geometry: all 27,780 eligible carry rows are accounted
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
carries both new rows as OPAQUE/DARK without changing a semantic grade. At
that freeze the next valid generation was 30; live authority and the next-valid
value are owned only by `current_re_authority`.
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
