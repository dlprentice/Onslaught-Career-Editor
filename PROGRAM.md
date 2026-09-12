# Execution Program

Status: durable backlog; Linux development phase active; internal preparation complete
Last updated: 2026-09-12 (remote integration validated; Ghidra audit resumed)
Summary: remaining work, acceptance gates, and completed program items without the execution diary.

The [standing goal](GOAL.md) keeps retail RE, the Godot rebuild, and the Godot
toolkit companion coequal. On September 6 David accepted the baseline and explicitly
resumed the rebuild-led phase below. The historical storage hold no longer blocks its
normal implementation. Save/evidence protections remain; no Windows VM activation,
external archive cleanup, production work or repository split is included.

Use `developer_state.json` → `current_re_authority` as the sole live campaign
selector. Capability claims belong in [CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md),
validation in [VALIDATION.md](VALIDATION.md), and database state in
[Ghidra's guide](reverse-engineering/ghidra/README.md). Dated receipts and prior
queue revisions remain in Git and existing evidence owners; do not recreate a diary here.

## Open work

### Remote checkpoint integrated on Linux — September 12

The complete remote difference from `135775772a126af48b9930a8fcfd4140000a4af9`
to `f6ad243f45e115ddc906a0d9dd79490d34d97171` was fetched and reviewed in
an isolated repo-local worktree. All six code/tool corrections are retained,
including the independently duplicated actor-script restore fix. The newer
Windows-staging retirement and local aircraft follow-up were preserved.
No main merge, release, desktop control or CI run was involved.

The incoming C# changes now compile and their owning tests pass. The final
focused Core selection passed 150/150; Client passed 907 with two existing
capture-dependent skips. All 52 added admission/guard cases ran. Negative
controls against the previous implementations failed as expected. Python
launcher/exporter checks passed, and the updated Java packet exporter compiled
and produced 14 verified packets from a read-only Ghidra copy. Exact commands,
limits and private logs are in [VALIDATION.md](VALIDATION.md#remote-source-review--2026-09-09-execution-pending).

The unpublished smoke suggestion was reproduced independently: closing a
smoke run could return zero before the completion report existed. The Linux
launcher now requires that completed lifecycle report and retains timeout
diagnostics. This bounded check does not replace gameplay, visual or audio
acceptance. The forty-step hash difference was isolated to the new arithmetic
mode byte; the separate older Headless fingerprint now checks its current
bounded Walker state. Full-combat and Save Lab UI acceptance remain open.

**The executable-backed Ghidra audit is active.** Initial read-only exports covered
8,330 function rows, 32,688 return/parameter/local rows, 410 types, 2,300
bookmarks, actual body ranges, direct calls and saved analysis options.
They establish an inventory of existing analysis, not complete semantic review.
The first exact correction restores the Plane controller's incoming event
argument, with full readback and independently restored recovery. Its old
missing-boundary question was stale documentation: both call sites already
belong to the saved function. The decompiler's remaining stack-expression
artifact is explicit in the [controller evidence](reverse-engineering/binary-analysis/functions/CComplexThing.cpp.md).

Continue structural and semantic RE through the existing owners. The
[script callback audit](reverse-engineering/binary-analysis/functions/IScript.cpp.md#native-callback-transport--september-12-static-audit)
identifies missing callback arguments and distinguishes the native argument
count from script arguments. Aircraft integration must preserve separate Unit
AI/controller state and the scheduled selected-provider/common-AI chain;
retiming the current per-Move target refresh alone would omit real behavior.
Keep conditional random draws, ordered avoidance candidates and monitored
reference lifetime. The remaining controls-remap boundary is a candidate for
its own instruction-bounded correction. No broad cleanup, unreviewed bulk
prototype assignment or new campaign is needed to pursue these findings.

### Active phase — Linux playable slices and first Save Lab workflow

David retains desktop control until he explicitly releases it. Prioritize
RE and rebuild source/headless work meanwhile; live retail/rebuild playthroughs
and the Save Lab UI workflow remain pending.

David delegated project and companion direction on September 8. Prioritize a
faithful Godot game that the community can play and inspect, with Windows as the
primary audience and native Linux support. Keep a later enhanced version separate
from retail defaults. Native execution of selected original routines supports RE;
building a second complete port is not an additional active deliverable.
The first actual Godot development video is recorded in
[CURRENT_CAPABILITIES.md](CURRENT_CAPABILITIES.md#reconstruction), with its
revision, input route and known limitations. An isolated display may render footage
without controlling David's desktop; a synthetic demonstration is not a player
acceptance run. Keep the existing capture/launcher owners rather than creating a
separate presentation or test framework.
The same isolation now supports a copied-retail WineD3D observation, including
measured Plane control words and Euler transitions. Its development `-level`
entry does not close the player route; use these observations to replace the
remaining approximate aircraft transaction, with limits recorded in the existing
[Unit evidence](reverse-engineering/binary-analysis/functions/CComplexThing.cpp.md).

David's September 7 priority is startup, menus and complete Level 100 parity.
Audit the actual Ghidra database in bounded cohorts against pristine bytes and
pinned source, correct misleading names/comments/signatures or boundaries when
proved, and carry recovered contracts into production code. Existing pipelines,
tests and agent reports are fallible inputs. Further World 110 expansion is
paused until this first route is established; its completed source stays useful.

1. Establish native Linux Godot build, launch, real input, audio, pause/focus,
   capture and live tape recording/replay using the installed pinned tools.
2. Complete the cold first-career Level 100 tutorial through player input and
   player-observable information, including completion/debrief/return and retry/
   failure. Compare presentation, audio, timing, controls and world behavior with
   retail; neither the synthetic smoke route nor a single Won establishes parity.
3. Resolve blocking systems with targeted, specimen-bound RE and implemented
   contracts. Keep the independent full-retail mandate and existing evidence owners.
4. Deliver a separate Godot Save Lab: open a real save, edit one supported field
   to a new copy, reopen and verify the original and every unselected byte.
5. Construct real World 110 from its own admitted inputs, then demonstrate the
   100→110 transition, useful play, retry and return without substituting World 100.

Refactor responsibilities where these steps expose a concrete problem. Reuse useful
Core/Client/AppCore code and retain WinUI migration material. Validate focused changes,
commit/push coherent milestones, update the existing capability/validation documents,
and stop with a phase report when these deliverables are complete. This phase does not
complete the full retail RE, game-parity or companion mandate.

### P6 — Campaign bookkeeping relief — OPEN; NOT IMPLEMENTED

Close already-triaged-out questions with their existing terminal verdicts and
decouple campaign generations from purely structural Ghidra promotions, re-grounding
when semantic grades require it. This is proposed policy, not today's authority.
Acceptance: a verified generation cut closes the intended rows with zero semantic
movement and the policy is recorded in campaign owner documents. This bookkeeping
proposal is not a prerequisite for the active playable slices.

### P7 — World-110 generalization — PARTIAL; NOT PLAYABLE

Accepted pieces include exact serialized player-start admission, the bounded
height-clamp prefix, ordered start-list selection, standalone player/engine assignment,
ordered composition over adapter-supplied identities, and all-40 initial-object seed
admission. These deterministic pieces do not construct a playable world.

The active phase now constructs an explicitly incomplete World 110 stage from
its own terrain and 43 admitted direct actors, with real authored transforms,
behavior selectors and physics life. It also owns detached Start/engine/player
shells with measured configuration and reader fields. Concrete class Init,
ordinary-object publication and event ordering are still missing; these shells
are not a completed session or a reason to claim 100→110 play.

The complete static Actor/base and Unit initialization order is now recorded in
the existing [Actor owner](reverse-engineering/binary-analysis/functions/Actor.cpp.md)
and [Unit owner](reverse-engineering/binary-analysis/functions/Unit.cpp/CUnit__Init.md).
Implementing that order still requires actual render/mesh state, collision and
publication effects, and recursive child initialization; static body closure
does not complete those runtime objects.

The four landing-craft Component inputs now use their actual mesh attachment,
parent float pose and matrix-to-Euler conversion. Native x87 arithmetic and
focused Core checks agree on their meaningful output words. This closes an
incoming-argument dependency; child allocation, Init and event/world publication
remain unfinished.

The construction owner retains both explicit-tree tables and can now construct
the 1,481 base-world pines with real MapWho entries, live neighbor traversal and
owned collision-readiness events. The prefix requires an explicit incoming RNG
seed and uses a stated nearest/53-bit arithmetic assumption. It shares object/
reader identity allocation with subsequent detached player shells. Actual retail
FP/seed state, final tree orientation, complete collision response and ordinary
actor initialization remain open. The first lander/child collision exclusions
and separate Unit/animation/AI listeners are recorded in the
[World-110 owner](reverse-engineering/game-mechanics/world-110-initial-constructor-seeds.md),
along with the first three Buildings' render/animation route and the Feature
contract. PostLoad spatial sorting is implemented separately and awaits the
complete load sequence. Startup RE narrows the seed/FP witnesses without claiming
those runtime values were measured.
The first three Buildings now use those shared owners, the existing Actor state,
64 real destructible segments and distinct AI readers/listeners. The factory
prepares its attached Sabre template; the repair pad constructs its actual
weapon using shared charge/selection state and effect-list nodes. No tank is
spawned and no repair shot is fired by this Init prefix. The same shared
Actor/Unit transaction continues through the inactive SAT turret and six iceberg
Features, including their actual weapon/animation state, current-versus-old
poses and type-dependent collision centres. The remaining ordinary objects and
renderer/resource caches still need integration before world event delivery,
reset and play. Keep the same spatial/event/RNG ownership when extending the
remaining authored objects; this prefix is not a playable world.
The old test-only Simulation route that ran Level100 Setup under a World110
stamp is explicitly rejected; direct World110 mission and hash tests remain.

Remaining: complete start/actor/player/Battle Engine construction, real ownership
and reader identities, physics/coordinate enrichment, squad/spawner expansion and
publication order, policy effects, player initialization, registry/state hashing,
real headless/interactive session, Godot lifecycle, and campaign 100→110 play.
The host still constructs only world 100. Acceptance: evidence-backed contracts
and focused production-path tests recorded in [PARITY.md](rebuild/PARITY.md),
working second-world lifecycle and campaign transition, and the current-truth
section of [rebuild/README.md](rebuild/README.md) updated without widening partial claims.
The serialized-seed ceiling is in
[world-110-initial-constructor-seeds.md](reverse-engineering/game-mechanics/world-110-initial-constructor-seeds.md).

### P8 — Player-input replay tapes — IN PROGRESS

Record an actual play session as a `CommandTape`, then replay it twice under
`--expect` with identical results. Acceptance: both runs pass and the recording
procedure is documented under `rebuild/tools/`. Native Linux input capture is now
in scope. Expected hashes must be measured during live play; a synthetic tape or
expectations generated by replaying the same tape do not meet this gate.
The September 6 mostly idle native session passed both expected hashes across
two replays. Recording now works; a substantial player-input tutorial recording
and its workflow acceptance remain open.

### P10 — Godot toolkit companion — FIRST WORKFLOW IN PROGRESS

David replaced the WinUI 3 lane with a Godot companion for Linux and Windows on
September 6. Retain the existing WinUI/AppCore source and tests as migration material;
the merged v1.0.12 source cut and its open Windows acceptance are historical status,
not a queued WinUI release. [README.RELEASE.md](README.RELEASE.md) retains that artifact's
procedure. The active phase begins with the portable AppCore-backed Save Lab workflow.

The companion's product direction is a focused cross-platform front door:
locate retail data, launch the rebuild, manage careers and recovery copies, and
explain optional patches before applying them. Finish useful end-to-end workflows
before migrating secondary catalogs or maintainer UI. Reuse one AppCore
implementation of file safety and save correctness. Windows and Linux packaging
are both targets; Linux checks do not establish Windows runtime acceptance.

Convert the companion while preserving careers,
saves, safe copies, patching, media and related toolkit capabilities. Acceptance:
usable Godot workflows validated on Linux and Windows, preserved unknown save bytes
and guarded writes, and current capability/provenance documentation. The shared engine
does not collapse the companion and retail-parity rebuild into one outcome.

### P11 — CLI parity — OPEN

The documented remaining gaps are cheat-named save-copy creation, trainer hotkeys,
and music playback. `media list`, `lore search/show`, and advanced `saves patch`
options already exist; `trainer music --out` renders audio but does not play it.
Standalone asset-library parity remains unverified and in scope until the implemented
command surface and per-verb Windows tests establish it.
Acceptance: close the remaining gaps with per-verb Windows tests, keep
[CLI.md](CLI.md) aligned with the implemented command surface, and keep public
copy free of internal process language. Source inspection is not Windows acceptance.

### P12 — Repository preparation — INTERNAL BASELINE COMPLETE; EXTERNAL AUDIT OPEN

The complete checkout now lives at `/srv/archive-b/Onslaught-Career-Editor`,
with a bind/automount at `/home/xsniper80/Projects/game-dev/Onslaught-Career-Editor`.
`local-lab/` and `local-data/` remain real ignored children of that one checkout.
The old ProjectData route stays absent. Current mount and recovery rules belong
in [AGENTS.md](AGENTS.md) and the existing local data guides.

David's September 6 repository-internal preparation and independent follow-up audit
are complete. He subsequently authorized the active development phase above.
Completed preparation scope:

- [x] Align current guides, implementation maps, platform boundaries and timing prose;
  retain all three goals, evidence grades, save/provenance rules and development holds.
- [x] Repair the packet exporter's Linux launcher, dry-run/refusal behavior,
  verified incremental reuse and recoverable publication; repair canonical probe-ledger
  routing and the case-sensitive authoring fixture. Correct host-attestor diagnostics
  without changing any frozen campaign selector, pin, grade or receipt.
- [x] Group the four recovery packages under `local-data/recovered/`, preserving
  all 120 files / 28,217,115 bytes and recorded metadata. Retain both unselected
  seed stages under `local-data/recovered/seed-staging/` and fourteen historical
  validation files under `local-data/test-runs/retained-lab-records/`: another
  126 files / 68,827,682 bytes, with unchanged hashes and recorded metadata.
  The existing migration queue and local-data owner map record exact paths.
- [x] Close the bounded lab-root and tool reviews, retaining failed attempts,
  distinct staging trees and all frozen contents. Review findings and their
  reproduced resolutions live under `local-lab/reviews/preparation-20260906/`.
- [x] Close the independent follow-up findings: refuse unregistered packet replacement
  and output inside a bind-aliased project; explicitly report the four Windows-only
  tools suites as skipped on Linux. Retire three superseded tracked roadmap/signoff
  documents, remove obsolete execution and approval diaries from active state, and
  correct the current write-safety, native Lore and natural-Damage summaries.
  Retire seven unused fixed-model review helpers and condense review guidance to
  its evidence/preservation rules; preserve the generated historical review trees.
- [x] Retain four more historical validation logs and one obsolete instruction patch
  under their operational owners: 5 files / 29,048 bytes, every hash and recorded
  metadata field unchanged. Recheck the earlier 246-file grouping successfully.
- [x] Correct the three Linux test assertions that expected Windows namespace
  messages. The affected class passes 22/22 without skips or production behavior
  changes; no new broad Core or Windows runtime result is claimed.
- [x] Pass the affected existing tool suites and documentation/public-payload
  gates. [VALIDATION.md](VALIDATION.md) records the focused results and limits.

KEEP in place: the reviewed and writable Ghidra homes, frozen campaign inputs
and receipt graphs, explicitly retained historical/rehearsal projects,
`local-data/_recovered-worktrees/` and `local-data/windows-profile-2026-08-28/`.
Ignored status and a historical name do not establish redundancy. Existing dated
logs, manifests and citations remain evidence, not a new execution queue.

The storage owner's later September 6 closeout retired both B-side lab/cold
mirrors and moved remaining non-project B collections to A. It also retired a
few proven Archive A duplicates. The current checkout/lab/data stay on B, with
independent Ghidra cold recovery on A; this is not a whole-lab backup. Other
graveyard material and historical ignored non-lab recovery remain unresolved.
The migration queue owns those receipts; this development phase does not reopen
external cleanup or backup work. David separately retired the never-built Windows VM
staging on September 12; no Windows validation host is provisioned. Native Linux Godot now
runs, while complete runtime acceptance and the P7/P8/P10/P11 gaps remain open.

## Completed items

| Item | Completed scope and owner |
| --- | --- |
| P0 — Integration spine | Source/doc integration and branch consolidation landed. Later causal round-ID evidence superseded the geometric Blaster observer; measured tests belong in VALIDATION.md. |
| P1 — Sealed static-receipt reseat | The campaign cut completed. Select current state through `current_re_authority`; historical receipts do not select a parent. |
| P2 — Ghidra promotion/integration | The named cohort ceremonies and corrected offline integration completed. Read the Ghidra owner before any further promotion. |
| P3 — Simplify developer state | Retired 554 superseded top-level fields and unconsumed nested diaries from active loading. `_history` gives exact Git recovery; required compatibility values, current authority, hold, evidence limits and explicit KEEP controls survive. Archived follow-ups are not declared closed. |
| P4 — Function-triage packets | The exporter produced complete packets in one read-only headless run and served an RE question. Tool usage and focused tests are in tools/README.md. |
| P5 — Coverage index/query | The receipt-based index and preregistered cross-trace query completed. Raw TTD recordings were subsequently retired; this milestone does not promise raw replay or intact historical paths. |
| P9 — Ferry sweep split | The expensive sweep is separate from the default Core suite; the explicit command remains in VALIDATION.md. |

Completion requires the named acceptance evidence, not effort or an unrelated green
suite. Preserve fail-closed checks and use the smallest relevant existing validation.
Completed bookkeeping, document cleanup, or a partial World-110 owner does not close
the full RE, reconstruction, or toolkit goal.
