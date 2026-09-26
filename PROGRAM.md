# Execution Program

Status: durable backlog; Linux development phase active; internal preparation complete
Last updated: 2026-09-25 (Level 100 final-wave contract for the rebuild; 2026-09-23 coupled settings and sound-manager initialization; 2026-09-19 companion P10 native migration; other lanes retain their stated evidence)
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

### Dedicated RE lane — current continuation

David resumed this dedicated RE task on September 22 from the preserved pause.
The interrupted language-cleanup control had watched the wrong input-state
address. Original instructions resolve that arithmetic error; the corrected
experiment now passes 26 cases while retaining the old address as an unchanged
control. Failed runs remain in the existing private owner. No retail body was
changed to make the checks pass.

Separate tasks own rebuild and companion implementation. The working branch is
`codex/retail-re-20260919`. Current database and recovery identities remain in
`developer_state.json` → `current_re_authority.latestLiveGhidraState`; use those
pointers rather than selecting a project by date or database number.

The resumed investigation confirmed CLIParams ownership of the initializer at
`004239f0`; its former Unit AI name is corrected through the
[one-row preservation/readback workflow](reverse-engineering/ghidra/README.md#cli-initializer-ownership--september-19).
Four isolated original-code cases establish its bounded defaults and preserved
memory. The complete [parser contract](reverse-engineering/binary-analysis/functions/CLIParams.cpp/CLIParams__ParseCommandLine.md)
now records all 25 comparisons, sequential argument consumption, the initial
zero windowed guard, and directory/logger-filename side effects. Retail startup
acceptance remains separate from the isolated parser execution below.

The follow-up passed 47 isolated cases through the unchanged parser and native
CRT conversion code, with OS/printf boundaries intercepted. It identified ten
absolute reads of the developer selector, corrected its old frontend-state
identity, and separated autoconfig/cheat-query admission and the frontend
startup override from `-level`. No active consumer of either trace-request
field or later deliberate developer-selector writer was identified. That is
bounded static evidence, not proof against computed or external writes.

David's current priority is to recheck save files, settings and startup as one
compatibility chain. Existing notes, prior agent work and this lane's earlier
conclusions are fallible leads. Reproduce consequential claims against selected
pristine bytes and controlled execution before carrying them forward. Keep the
full-retail mandate and separate implementation owners.

The [save/startup contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md)
now separates the startup reader, normal menu load and writer, active settings,
serializer, and campaign reset. Original-code controls establish read/write
filename differences, menu forwarding into the next boot, binding/preset effects,
active-language ownership and volume application. Six preserved language files
also pass bounded original parsing and lookup. File/heap/device boundaries
remain explicit; these results do not establish complete retail startup.

The audio reset/bank controls resolve caller ordering, init-return admission,
shutdown versus Stop, Level 100 music restoration and early path caching that
can suppress a same-path retry after a failed or skipped bank load. Actual
platform services, lifetime effects and playback remain open; the direct sample
decode/quality path now has the bounded original-code evidence below.

Fifteen native Load/Save/reinitialize/Load/Save cases now include direct handoff
of the first serializer buffer. Both gold controls preserve all 10,004 bytes;
private derivatives distinguish progress-flag writes, counter normalization,
preset restoration and preservation-mode volumes. Linux generated-copy readback
is checked; retail file publication and full process restart are not. The
intervening career static initializer must not be confused with Blank.

Seventeen extended startup cases now execute Blank's original Goodie
recomputation with descriptor initialization. The final canonical reset has nine
instruction-state Goodies, no unlocked entries, preserved settings and unused
record storage. This closes the former Goodie hook for the reset route, not the
complete unlock table or its UI. Exact commands, artifacts and limits belong in
[VALIDATION.md](VALIDATION.md#original-load-save-and-reload-controls--september-20).

Nonnull language cleanup now executes the original outer/nested menu teardown,
list recycling, resource decrements and monitored-pointer clearing. Composed
SetLanguage calls retain old text throughout teardown, clear the outer owner,
then replace the active buffer; repeat selection copies again. Heap operations
and optional child destruction remain explicit boundaries. The
[cleanup contract](reverse-engineering/binary-analysis/functions/FrontEnd.cpp/CFrontEnd__SetLanguage.md#nonnull-cleanup-before-text-replacement)
and [saved controls](VALIDATION.md#original-nonnull-language-cleanup--september-22)
record exactly what this establishes.

Direct sample controls now execute the original cached reader, buffer factory,
ADPCM decoder and quality converter with two real English-bank records. They
expose different rounding in requested versus written sizes, and distinguish
returning a sample object from successfully decoding it. The current materializer's
pure decoder matches both complete high-quality PCM outputs. This does not
establish all-bank loading, real device outcomes or playback; see the
[sample contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#original-sample-decoding-and-saved-quality).

The outer caller now has original-code reuse/list/name-copy controls, including
insertion despite a supplied device-create failure. Its filename-route stub and
working buffer loader contradict inherited semantic labels; the
[caller contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#outer-sample-admission-and-registration)
records the evidence; the [four-function Ghidra correction](reverse-engineering/ghidra/README.md#sample-loading-metadata--september-22)
now preserves it in the working database with unchanged types and storage.
Original destruction now has 23 standalone controls and 11 composed failed-load
controls. A zero payload read removes a reused sample; old storage and sample
buffers are released once, while failed fresh creation preserves existing samples
and events. Heap reclamation, device lifetime and mutating callbacks remain
intercepted. Original bank loading, file Open/refill/Close and decoding now pass
11 cases: all 164 English samples, reload identity/duplication, quality changes,
tag/trailer admission and supplied device failures. The materializer's pure
decoder matches every complete high-quality output. The
[bank contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#complete-original-bank-loading-and-reloads)
separates parser, publication and device success. Nine subsequent original
Load/Save/reload controls expose a routing distinction: changing language and an
audio word together preserves the cached old bank path, while language-only
refresh replaces it. The same serialized result fixes the path on the next Load.
Device Init and the final bank entry remain explicit boundaries in this paired
control. Separate original Init controls now establish device-index normalization,
capability-derived state, enumeration and failure cleanup under supplied API
responses. Ten original outer-manager controls now establish pool/registration
setup, timer sampling and the caller-owned initialized byte: failed device Init
clears that byte without undoing setup. SFX parsing remains a boundary. Eight
composed Load/reset/Init/Save controls now prove that device-index normalization
can persist even when subsequent device creation fails; zero admitted devices
instead preserves the saved index. Failed reset retains the initialized flag,
allowing the second Load to request a language-bank refresh with null device
pointers. Separate original-bank controls now reproduce a null-device dereference
before the sample factory's COM error check; a valid zero-count bank avoids it.
Next connect this bank dependency to the composed route without replacing the
failed manager state, and retain the full startup/save compatibility objective.
Actual device/playback and cold-start acceptance remain open. The
[coupled contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#coupled-language-and-audio-settings-routing)
and [device/save contract](reverse-engineering/binary-analysis/save-options-static-review-2026-05-26.md#original-device-effects-during-load-and-save)
record the exact prior state and limits.
Keep original-code evidence distinct from decoder self-tests,
retail file durability and player acceptance. The retained AppCore sensitivity
clamp and display-mode naming discrepancy are implementation-consumer findings;
this RE task does not own those production changes.

The rebuild's failing cold full-combat route now has a
[final-wave contract](reverse-engineering/game-mechanics/level100-final-drone-wave.md):
the abort is a designed retail branch, and retail adds friendly turrets after
Help Player and the jet Missile Pod. An original-code control shows activated
turrets can select the script-spawned enemy drones. The turret aim, Missile Pod
lock, crosshair and auto-aim refresh, seeking-round and per-round draw laws are
static contracts there. Open: a composed runtime control of those laws and the
ordered RNG draws of the base-world AI owners and the Battle Engine.

Preserve the aircraft/weapon continuation: pool initialization precedes logger
resets after parsing; arbitrary warning state, enabled-logger callbacks and
complete-shot RNG remain unresolved. A read-only frontend review identified
`00459810` as a card-selection setter and `00465f10` as the outer frontend
constructor; their saved metadata still needs the scoped byte-backed correction
workflow. Do not use their old multiplayer/page-ID names as behavior evidence.
These saved labels are also wrong, each shown by the bytes cited in the named
owner, and queue for the same workflow:

| Address | Saved label | What it is | Owner |
| --- | --- | --- | --- |
| `0055dcb0` | `CRT__AcosDispatch_ST0` | CRT asin (error record `00653310` names `asin`) | [final wave](reverse-engineering/game-mechanics/level100-final-drone-wave.md#turret-aiming) |
| `0042efd0` | `CUnitAI__InitDefaults` | Unit profile defaults (turret yaw limit `+0xdc` = 2π) | [final wave](reverse-engineering/game-mechanics/level100-final-drone-wave.md#turret-aiming) |
| `00506010` | `ProjectileBurst__SpawnFromPercentBucketFallback` | `CWeapon::Fire` | [stores](reverse-engineering/game-mechanics/battle-engine-weapon-stores.md#fire-empty-stores-and-locks) |
| `00509c80` | `CBattleEngine__ComputeProjectileMetricFromTargetProfile` | `CWeapon::GetActualMaxRange` | [final wave](reverse-engineering/game-mechanics/level100-final-drone-wave.md#crosshair-and-auto-aim-refresh) |
| `004f8140` | `Mat34__SetFromEulerDegrees` | Euler matrix from integer angles in units of 2π/4096 | [burst](reverse-engineering/contracts/render-platform/ProjectileBurst__SpawnFromCurrentPreset__005069f0.md) |
| `0040c2e0` | `CBattleEngine__CanSpawnBurstForResolvedEntry` | `CBattleEngine::WeaponFired` | [burst](reverse-engineering/contracts/render-platform/ProjectileBurst__SpawnFromCurrentPreset__005069f0.md) |
| `0040c340` | `CBattleEngine__RandomizeBurstOffsetsAndAccumulateRange` | `CBattleEngine::RecoilWeapon` | same |
| `00407940` | `CBattleEngine__RandomizeOffsets4B8_4C0` | `CBattleEngine::AddShockShake` | same |
| `00407310` | `CBattleEngine__DisplayLock` | is this weapon the current part's weapon | same |

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
8,330 internal-function rows, 32,688 return/parameter/local rows, 410 types, 2,300
bookmarks, actual body ranges, direct calls and saved analysis options.
They establish an inventory of existing analysis, not complete semantic review.
The first exact correction restores the Plane controller's incoming event
argument, with full readback and independently restored recovery. Its old
missing-boundary question was stale documentation: both call sites already
belong to the saved function. The decompiler's remaining stack-expression
artifact is explicit in the [controller evidence](reverse-engineering/binary-analysis/functions/CComplexThing.cpp.md).

Continue structural and semantic RE through the existing owners. The
[script callback audit](reverse-engineering/binary-analysis/functions/IScript.cpp.md#native-callback-transport--september-12-static-audit)
corrected two missing callback prototypes and distinguishes the native argument
count from script arguments. The remaining default signatures need per-body
review; shared cleanup is not permission to assign one prototype wholesale. Aircraft integration must preserve separate Unit
AI/controller state and the scheduled selected-provider/common-AI chain;
retiming the current per-Move target refresh alone would omit real behavior.
The bounded weapon selector now matches isolated original-code cases and has
focused Core coverage. Original-code Unit preparation/fire phase experiments
also passed, and five misleading provider/helper names were corrected in Ghidra.
The recovered provider contracts are not yet wired to actor firing. Core now
executes the separate aircraft exit listener, retains its owner/selector/deadline,
and submits script Ready at the scheduled handoff. New bursts wait for normal
control; pending bursts retain their continuation. Exit completion clears the
collision-ignore pointer and preserves guide state. Spawner loss marks the
Plane dying without declaring immediate shutdown. These are bounded source
and in-process checks, not full aircraft or tutorial acceptance.
The reduced-fixture returning driver again clears all 22 targets without
abort. The cold shipping-manifest route still aborts after one final-wave kill;
its client and direct-Core inputs agree. Preserve that failed completion gate
while replacing the remaining approximate combat owners.
The shared initializer attribution and both dispatcher/exit event-pointer
parameters are now corrected in the working Ghidra project with full readback
and independent recovery. The exit comment now identifies GetVulnerable,
the distinct CST collision-ignore pointer and TRUE GoTo override, with the
same preservation gate. A composed original-code experiment passes 21 cases:
slot-4 refresh precedes readiness, preparation can select twice, and an already
ready weapon can fire despite newly failed feasibility. Pending preparation
retains its earlier aim point. These contracts still need production integration.
The selected GunA/GunB selector1 model transforms and ordered Unit weapon uses
now reach Core as immutable inputs. An unchanged-code attachment experiment
passes 27 cases / 33 calls, distinguishing current/interpolated pose and
same-frame direct-cache reuse. Carry those measured paths into runtime cache
ownership. Native population now passes 11 cases / 17 calls over the full
12-part training mesh; its frame-zero poses match stored CPOS/CORI under both
tested precision modes. The cache stamp counts renders, not gameplay updates:
MainLoop permits multiple renders per update and pre-run updates without
rendering. Resolve ordered render context and camera-latch lifetime, and complete B feasibility's
real line query alongside retained aim,
preparation/readiness and scheduled bursts,
including terminal callbacks and next-frame round movement, before replacing
the old all-slots loop. Details remain in the controller evidence owner above.
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

### P10 — Godot toolkit companion — NATIVE SAVE LAB IMPLEMENTED

The September 19 companion lane uses Godot 4.8 dev6 .NET and native GDScript
for editable scenes, save inspection/planning, comparison and media metadata.
Linux headless execution now covers open → explicit preview → separate verified
copy → reopen through the actual scene and in-process C# file adapter. Byte-identical career
recovery copies and read-only comparisons are native workflows. See the
[companion goal/acceptance](companion/OnslaughtToolkit.Godot/README.md#migration-goal-and-acceptance)
and [executed evidence](CURRENT_CAPABILITIES.md#godot-save-lab--first-workflow).

GDScript lacks the required OS file identity/no-clobber primitives. David clarified
that necessary C# should run inside Godot's .NET edition. The thin adapter links
existing file safety unchanged, with GDScript owning save semantics and presentation.
There is no production helper process. Unsupported protection fails closed.
WinUI/AppCore and the old C# scene script remain reference material. The legacy
[Windows release procedure](README.RELEASE.md) remains historical, not a release task.

Remaining coherent increments are broader career/options editing, whole-game
safe-copy/rescue, catalog-backed patch preview/apply/restore, media playback and
replacement, lore and asset views. Keep MIT application, GPL rebuild and private
retail data separate. No unrelated launcher/store/community expansion is planned.
Windows cross-export/package checks do not establish Windows execution; actual
Windows acceptance and human desktop interaction remain open. The companion lane
does not own retail RE/Ghidra contracts or the faithful rebuild's Godot migration.

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
