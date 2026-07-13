# Out-of-the-Box Architecture Challenge

Status: independent strategy audit
Date: 2026-07-13
Evidence base: `82bbc2c0`
Decision: **GO WITH MAJOR COURSE CORRECTION**

## Executive Verdict

Onslaught is solving the right broad problem: preserve and safely modify the
retail game while turning evidence into an original-code successor. Its strongest
architecture is also its least glamorous:

- AppCore owns byte preservation, copied-target safety, atomic publication, and
  process identity below the UI;
- deterministic rebuild Core is independent of presentation; and
- Godot is a replaceable snapshot/input adapter rather than simulation truth.

Do not rewrite WinUI, AppCore, Core, or Godot now. There is no measured user,
fidelity, or contributor outcome that would repay the migration.

The campaign does need a major course correction. Evidence governance has become
a product of its own. The repository contains 19,389 tracked files, including
13,395 under `reverse-engineering/`, 2,647 under `tools/`, 1,712 under `release/`,
and 1,143 under `lore-book/`, versus 54 WinUI files, 49 AppCore files, and 65
rebuild files. The root package exposes 1,517 scripts, 1,483 of them test-prefixed.
Recursive proof-plan, readiness, and checklist families occupy tens of megabytes;
individual public-safe JSON artifacts reach roughly 1.5--1.9 MB. Meanwhile, the
rebuild still has no accepted retail-measured movement, morph, or camera contract.

The next campaign scoreboard should be accepted user outcomes and behavior
contracts consumed by executable code, not addresses named, scripts retained,
proof rows validated, or negative claims repeated.

## Evidence Method

This audit was read-only apart from this strategy document. It did not launch
WinUI, Godot, BEA, CDB, or Ghidra; mutate game files or canonical state; or inspect
private payload/proof material. Findings came from current policy, source, tests,
catalogs, front doors, representative RE/Lore material, file and command
inventories, and recent campaign evidence.

The review envelope contained:

- independent normal Codex review;
- independent adversarial Codex review;
- a sanitized normal Cursor/Grok consult; and
- a sanitized adversarial Cursor/Grok consult.

Both external consults used `cursor-grok-4.5-high-fast`, an empty temporary
workspace, an allowlisted environment, and read-only reconstructed public facts.
Both exited successfully. Consults were advisory; this report reconciles their
claims against repository evidence.

Important evidence:

- [goal.policy.md](../goal.policy.md) prohibits recursive proof-plan chains when
  executable code, a focused test, or one concrete blocker is more direct.
- [goal.md](../goal.md) records twelve failed morph-canary runtime attempts, no
  accepted matrix, and the eventual decision to timebox that work.
- [CURRENT_CAPABILITIES.md](../CURRENT_CAPABILITIES.md) is 136,702 characters and
  accurately distinguishes many proof classes, but gives future/negative proof
  status far more front-door space than ordinary product posture.
- The short header of [RE-INDEX.md](../reverse-engineering/RE-INDEX.md) is useful;
  the remaining 612,000-plus characters quickly return to recursively named
  proof-plan history.
- [VALIDATION.md](../VALIDATION.md) reports that 1,087 Ghidra/wave commands and 98
  copied-runtime commands are historical/runtime proof rather than the normal
  quick profile. That classification is sound; the namespace remains costly.
- [GameProfilePreflightService.cs](../OnslaughtCareerEditor.AppCore/GameProfilePreflightService.cs)
  recursively copies selected required and optional trees while rejecting
  reparse points and hardlinks. This proves the full-copy mechanism is real, not
  merely a stated policy.
- [CATALOG_CONTRACT.md](../patches/CATALOG_CONTRACT.md) correctly treats exact
  bytes, dependencies, conflicts, evidence, and rollback as backend contracts.
  The current catalog has 29 rows: 10 stable, 19 experimental, 20 visible, and 9
  hidden companions. Five selectable safe-copy profiles already provide a
  higher-level product vocabulary.
- `BinaryPatchesPage.xaml` and its code-behind contain 1,431 and 2,791 lines;
  `AssetLibraryPage.xaml.cs` contains 1,995; and
  `OnlineMultiplayerReadinessService.cs` contains 1,786 even though online play
  remains unavailable. In contrast, rebuild `Simulation.cs` is 358 lines and the
  main Godot adapter is 441.
- [rebuild/PROVENANCE.md](../rebuild/PROVENANCE.md) correctly labels the active
  implementation RE-informed and GPL, and separates a future strict clean-room
  lane that has not occurred.

Counts are repository-shape evidence, not quality judgments by themselves. The
conclusions below depend on the combination of scale, navigation, repeated
non-execution, and limited conversion into user/rebuild behavior.

## Assumption Inventory

| Assumption | Disposition | Evidence-based answer | Confidence |
| --- | --- | --- | --- |
| The project needs two deliverables | Keep | WinUI manages a user-owned retail installation; the rebuild runs without it. Combining them would not remove either responsibility. | High |
| WinUI must remain the primary Toolkit shell | Keep provisionally | Native Windows file, process, UIA, and accessibility work is mature. No alternative has demonstrated a user benefit worth porting it. The current mega-pages are not evidence against WinUI. | High |
| AppCore should own correctness | Keep | Save preservation, patch planning, filesystem identity, safe-copy publication, and process ownership belong below any shell. | High |
| Godot is the right rebuild renderer forever | Unsupported | Godot is adequate and replaceable. No current fidelity requirement selects Godot, Stride, MonoGame, or custom rendering decisively. | Medium |
| Godot should be replaced now | Reject | Core is already renderer-independent and the adapter is small. An engine migration would spend months before delivering a retail behavior contract. | High |
| Safe-copy is the correct safety contract | Keep | The installed game and original executable must remain immutable. That outcome is non-negotiable. | High |
| A full recursively materialized copy is the only safe mechanism | Test | It is the only proven production mechanism, not the only possible design. A write-set/base-generation experiment could disprove its necessity. | Medium |
| Patch catalogs are the right mod abstraction | Split answer | Exact rows are the correct mutation graph. Profiles/capabilities, not byte rows, should be the normal player and mod-author vocabulary. | High |
| Static RE closure produces rebuild-grade knowledge | Reject | The 6,411-address inventory stayed complete while important ownership metadata was wrong, and rebuild mechanics remain synthetic. | High |
| The RE evidence hierarchy is wrong | Reject | Source hypothesis, Steam static evidence, copied-runtime measurement, and rebuild contract are correctly separated. Throughput, not the hierarchy, is failing. | High |
| More runtime gates always increase confidence | Reject | Twelve canary failures produced valuable identity/cleanup infrastructure but no behavior matrix. Harness work is not automatically behavior advancement. | High |
| Lore, current RE, tools, history, and projections all need one physical repo | Test | Co-location improves traceability; current/history/projection interleaving imposes large clone, search, and navigation costs that have not been benchmarked. | Medium-high |
| The future clean-room lane is an active product requirement | Reject for now | The naming is correct, but it is a dormant option without separate staff, legal/distribution purpose, or budget. | High |
| Existing reviews and tests are proportionate | Mixed | Deep mutation, save, payload, process, and provenance tests are proportionate. Recursive not-run/checklist/proof-of-proof chains are not. | High |
| The current CMSH-to-OBJ slice is churn | Reject if bounded | It targets an identified missing parser, uses a generated fixture, and yields a visible result without reviving the blocked legacy toolchain. It must stop at the frozen profile. | Medium-high |

## Ten Hardest Questions

### 1. What are the actual user jobs?

Today they are: inspect and patch existing saves/options; prepare, verify, launch,
and recover copied game profiles; browse owned media/assets; and read curated
preservation material. A future job is to play an authentic original-code slice.
The eight-tab shell and research loaders expose more project structure than these
jobs require. **Answer:** keep the jobs, collapse the normal journey, and move
research diagnostics behind Lab/CLI. **Confidence: high.**

### 2. Do we need a separate WinUI Toolkit?

Yes for now. It serves Windows-specific filesystem and process work that the
Godot client should not own. A webview, Godot shell, or cross-platform rewrite
would still require AppCore and would reimplement mature accessibility and native
integration. **Answer:** retain WinUI; refactor page concentration rather than
holding a framework tournament. **Confidence: high.**

### 3. Is Godot the right rebuild client?

It is a reasonable current client, not a permanent truth. Core's clean boundary
makes client replacement possible later. Stride, MonoGame, or custom rendering
become credible only when a measured visual/input/tooling requirement fails in
Godot and a prototype demonstrates the alternative. **Answer:** keep Godot, but
do not expand presentation as a substitute for behavior fidelity. **Confidence:
medium-high.**

### 4. Is safe-copy the right product contract?

Immutable original input is the right contract. Full copy is a proven mechanism,
but it may cost disk, time, and clarity. Hardlinks, reparse overlays, filesystem
drivers, and shared mutable files would weaken the boundary and are not acceptable
shortcuts. **Answer:** keep full-copy in production while measuring whether an
app-owned immutable verified base plus disposable generations can preserve the
same invariants. **Confidence: high on the invariant, medium on the mechanism.**

### 5. Are patch/mod catalogs the right abstraction?

They are right as an exact specimen/byte/dependency/conflict/rollback graph. They
are wrong as the main player mental model and incomplete as a general mod package,
which may also need copied options, resources, launch arguments, compatibility,
and restore policy. **Answer:** make versioned capability profiles primary; keep
rows in Lab/details; design a broader package schema only after a real third-party
mod needs it. **Confidence: high.**

### 6. Is current RE yielding rebuild-grade knowledge?

Not at an efficient rate. The process can produce rebuild-grade contracts, but it
has mostly produced metadata, infrastructure, and bounded negatives. The campaign
should measure accepted behavior parameters consumed by Core per person-day and
stop expanding inventories that do not close a contract. **Answer:** sound method,
insufficient conversion. **Confidence: high.**

### 7. Are preservation, modding, RE-informed, and clean-room boundaries named and staffed correctly?

The current GPL RE-informed label and hard-payload boundary are honest. The future
strict clean-room description is also accurate, but the lane is not staffed and
should consume no material capacity until a concrete legal/distribution objective
funds it. Modding and preservation need clearer player-facing vocabulary than
research proof levels. **Confidence: high.**

### 8. Are Lore and tooling in one repo helpful?

Canonical current Lore, behavior contracts, and the tools that reproduce them
benefit from proximity. Historical waves, generated projections, old reports, and
one-off command surfaces do not need to dominate normal navigation. **Answer:**
keep current truth close; benchmark a versioned evidence archive or optional data
pack before splitting anything. **Confidence: medium-high.**

### 9. Are tests, docs, proof artifacts, and multi-agent review proportionate?

For executable/save writes, payload boundaries, runtime identity, and provenance,
yes. For routine docs/static work and long chains proving that another stage was
not executed, no. The non-recursive four-lane envelope is adequate; do not recurse
it per follow-up. **Answer:** preserve risk-based verification and freeze proof
inflation. **Confidence: high.**

### 10. Is the campaign solving the right problem efficiently?

It is solving the right problem inefficiently. Recent corrections—`npm test`, the
short RE front door, timeboxing Retry 13, and choosing CMSH v0—move in the right
direction. They must become the operating model rather than exceptions inside a
campaign whose completion criteria span product UX, repo reform, Lore, static RE,
runtime proof, modding, and rebuild fidelity simultaneously. **Confidence: high.**

## Stakeholder Rejection Test

- **New maintainer:** rejects 19,389 files, 1,517 commands, recursive current/history
  interleaving, and several 1,000--2,800-line product files before understanding
  the blessed path.
- **Player:** rejects unsigned-package trust friction, whole-copy cost, research
  jargon, disabled-future status, and eight destinations for a few common tasks.
- **Mod author:** rejects a centralized byte-row catalog as the only extension
  model and needs a stable capability/package contract with compatibility and
  rollback.
- **Speedrunner:** wants reproducible profiles, receipts, CLI verification, and
  measured timing/handling contracts—not broad patch menus or static address
  counts.
- **Preservationist:** values immutable originals and payload boundaries but rejects
  equating a 949-document pack with curation, freshness, or rights review.
- **Legal reviewer:** would want one crisp artifact/provenance matrix for MIT
  Toolkit, GPL rebuild/reference material, local proprietary inputs, and release
  contents. This is a process observation, not legal advice.
- **Reverse engineer:** rejects metadata closure and wave counts as progress proxies
  when accepted behavior contracts remain scarce.

## Credible System Shapes

All costs are rough engineering estimates for comparison, not commitments.

### Shape A — Sharpened two-deliverable architecture (recommended)

Keep WinUI/AppCore/CLI and deterministic Core/Godot. Make WinUI a short player
task shell; extract Expert Lab/diagnostics from the ordinary Windowed & Mods
journey; use profiles as the player vocabulary; split oversized coordinators;
keep current contracts and recent evidence in the normal front door; archive
history behind stable indexes.

- Expected cost: 2--4 engineer-weeks, staged.
- Value: improves the product and contributor path without migrating correctness
  or render code.
- Migration: alternate feature-flagged routes first; retain automation IDs and
  AppCore calls.
- Rollback: remove the new route and keep the existing page.
- Stop: if task completion does not improve or logic must move out of AppCore.

### Shape B — AppCore capability platform with optional shells

Promote a versioned local command/receipt contract for inspect, plan, prepare,
verify, launch, restore, and report. WinUI and CLI become first-class consumers;
future shells use the same contract. Godot remains only the rebuild renderer.

- Expected cost: 4--8 engineer-weeks.
- Value: portable automation and a credible mod-author interface.
- Risk: turns simple in-process calls into IPC/versioning/security ceremony.
- Migration: adopt only for the first operation duplicated by a real second
  client; preserve direct in-process WinUI use until then.
- Rollback: keep the capability contract as a CLI surface and remove IPC.
- Stop: if no second consumer appears or lifecycle/error semantics duplicate more
  code than they remove.

### Shape C — Current-source repo plus versioned evidence archive/data pack

Keep current source, behavior contracts, recent summaries, and canonical Lore in
the main repo. Move immutable historical Ghidra exports, wave artifacts, generated
projections, and broad offline packs behind a pinned archive/data package with
stable generated indexes.

- Expected cost: 1--3 engineer-weeks after a read-only benchmark.
- Value: potentially large clone/search/navigation improvement.
- Risk: broken historical links and checker assumptions; history must not be
  filtered destructively.
- Migration: build a disposable prototype archive and redirect generated indexes.
- Rollback: pin/mount the archive back into the existing paths.
- Stop: if common task improvement is below 40%, migration exceeds three weeks,
  or current-contract checks require broad manual remapping.

### Rejected near-term shapes

- **Unified Godot desktop Toolkit:** estimated 2--4 months plus accessibility,
  native-dialog, process, packaging, and licensing risk, with AppCore still
  required.
- **Stride/MonoGame/custom renderer migration:** no measured engine blocker or
  fidelity benchmark pays for the move.
- **Toolkit-only / archive rebuild:** useful as a future stop option if measured
  contracts remain unavailable, but premature while the small Core seam is sound
  and the CMSH/behavior experiments are cheap.

## What Must Remain Unchanged

1. Installed game files and original `BEA.exe` remain read-only.
2. Executable mutation remains copied-target-only, exact-specimen/byte verified,
   atomically published, backed up, read back, and recoverable.
3. Saves/options remain baseline-derived with exact allowed-byte diffs and unknown
   bytes preserved.
4. Proprietary payloads, arbitrary saves, copied executables, private proof, raw
   captures, full Ghidra stores, paths, and secrets stay outside Git/releases.
5. Static identity, runtime observation, patch behavior, visual evidence, online
   proof, and rebuild parity remain separate claim classes.
6. Deterministic Core remains independent of WinUI, Godot, filesystems, clocks,
   processes, networks, and GPU APIs.
7. Render clients remain input/snapshot adapters.
8. The rebuild remains GPL and explicitly RE-informed; it cannot validate retail
   truth by agreeing with itself.
9. Host/Join remains unavailable until distinct-endpoint command-source and
   source-bound copied-runtime causality evidence exists.
10. Stable automation IDs, accessibility, focused local gates, and proportional
    independent review remain.

## Small Reversible Experiments

These are proposals, not implementation authority.

| Experiment | Owner and disjoint scope | Measurable hypothesis | Cost | Migration / rollback | Stop rule |
| --- | --- | --- | --- | --- | --- |
| Player task-shell A/B | WinUI product worker; isolated alternate route/view-model and tests, no AppCore/catalog changes | Five unfamiliar users or equivalent scripted moderated sessions prepare and launch a safe copy with at least 80% unassisted success and 30% lower median time when research/online diagnostics are absent | 2--4 days | Feature flag over existing AppCore calls; remove route/flag to roll back | Stop below 20% time improvement, on accessibility regression, or if behavior must be duplicated outside AppCore |
| Retail write-set observation | Runtime-safety worker; ignored local proof plus one reviewed public-safe summary, no production code | Two normal copied-profile sessions show a stable write set materially smaller than the full copied tree | 1 day, at most 2 live attempts | Observation only; delete ignored captures and retain full-copy | Stop on identity ambiguity, any installed/shared-data write, attempt 2, or unstable write set |
| Immutable base/profile generation prototype | AppCore experiment worker; new isolated prototype/tests only, no production preflight change | Preparation time and incremental disk usage fall at least 60% while base/source hashes remain unchanged and every writable target is physically isolated | 3--5 days after write-set success | Optional backend behind existing prepare contract; delete generations and use full-copy | Stop if it needs hardlinks to mutable files, reparse routing, a driver, elevation, or unverifiable write assumptions |
| Behavior-yield canary | RE/runtime owner, then separate Core consumer; one ignored observation and one public contract, no Core edit until accepted | Within 16 staff-hours and at most 2 live attempts, one movement/morph/camera parameter plus tolerance becomes an accepted Core test input | 2 days plus 1 implementation day if accepted | Synthetic value remains until acceptance; retain only a concise negative result on rollback | Stop after attempt 2, on identity ambiguity, or when new harness code exceeds the eventual consumer |
| Command-surface compaction | Tooling/DX worker; generated registry/index plus package aliases, preserve legacy dispatch initially | Fewer than 100 curated commands cover all current contributor tasks while `npm test` and legacy commands remain unchanged | 2--3 days | Additive generated layer; remove aliases/index to roll back | Stop if release/docs checks need manual remapping or startup/regeneration cost grows materially |
| Repo-topology benchmark | Repo-governance worker; disposable clone/archive prototype and report only | Excluding historical exports/projections improves checkout and common search tasks at least 70% without changing current source/test contracts | 1 day | Delete prototype; no history rewrite | Stop below 40% improvement or above three-week migration estimate |
| Patch capability-package spike | Patch/AppCore designer; schema and synthetic fixture only, no catalog or UI mutation | One versioned profile can express patch rows, copied options, resources, launch arguments, compatibility, evidence, and restore without weakening row-level verification | 1--2 days | Map to existing five profiles; discard schema if it adds no real extension value | Stop if no concrete mod requires more than the current profile catalog |
| Lore current-pack benchmark | Lore editor; disposable current-only index/package, no canonical edits | A current curated set serves representative player/contributor searches with at least 90% task success using far fewer than 949 documents | 1--2 days | Keep existing pack until measured; discard prototype | Stop if omitted material blocks current tasks or claim-level provenance cannot be preserved |

The repository currently forbids hosted CI. A hosted quick-check design may be
reconsidered only through a separate policy/authority decision; it is not an
authorized experiment here.

## Top Course Corrections

1. **Change the scoreboard.** Track player task completion, accepted safe-copy
   profiles, accepted behavior contracts consumed by Core, executable vertical
   slices, and bounded defects closed. Stop treating file, script, wave, address,
   or proof-row counts as advancement.
2. **Freeze recursive proof creation.** No new readiness/checklist/proof-plan
   artifact unless the same bounded slice consumes new observation/code and
   replaces one current blocker. Prefer a test, contract, or concise blocker.
3. **Separate Player from Expert Lab.** Keep one plain online-unavailable statement
   in the normal path. Move artifact loaders, readiness matrices, and experimental
   patch rows to Lab/CLI.
4. **Prioritize behavior yield after CMSH v0.** Complete the frozen geometry slice,
   then accept the smallest retail-measured behavior contract before expanding
   assets, visuals, or generic First Flight mechanics.
5. **Timebox live RE.** At most two attempts for one observable before selecting a
   simpler observable. Infrastructure hardening becomes a separately justified
   deliverable, not automatic behavior progress.
6. **Keep frameworks; refactor concentration.** Decompose BinaryPatches,
   AssetLibrary, online readiness, and large AppCore services along task boundaries.
7. **Benchmark before repository surgery.** Compact command/front-door surfaces
   additively; split archives only after quantified clone/search/task gains clear
   the migration cost.
8. **Make strict clean-room dormant.** Preserve the truthful description, but spend
   no capacity until separate staffing and a concrete legal/distribution objective
   exist.

## Final Answer

The campaign is aimed at the right problem but is not solving it efficiently.
Its safety architecture and deterministic simulation seam are unusually strong
and should remain. Its campaign architecture is too broad, its player surface is
too exposed to research machinery, and its evidence surface has grown far faster
than accepted rebuild behavior.

Proceed with the current CMSH v0 slice, but treat it as the last permission to
expand presentation before one small measured behavior contract reaches Core.
Adopt the sharpened two-deliverable shape, freeze recursive proof chains, separate
Player and Expert Lab, timebox live RE, and benchmark command/repository compaction.
If those experiments fail to improve outcomes, revisit the product split. Do not
pay for a framework rewrite before the existing seams fail a measured requirement.

## Handoff

- Changed path: this strategy audit only.
- Canonical goal/state disposition: no edits; integration owner should decide
  whether and how to reconcile accepted corrections.
- Private/public boundary: no payload, private proof, path, credential, raw consult,
  or runtime material included.
- Installed game/original executable mutation: none.
- Runtime/process actions: none.
- Recommended validation: `git diff --check`, current doc-command validation, and
  public-core Markdown links.
- Terminal classification: `ADVANCEMENT` if accepted by the primary coordinator;
  otherwise advisory strategy evidence only.
