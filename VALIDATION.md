# Validation

Status: active — the gate-selection table
Last updated: 2026-09-12 (aircraft weapon model inputs, causal replay identity checks and model-time fragment).
Summary: choosing the smallest evidence that proves the contract you changed.
[`package.json`](package.json) owns the commands.

Validation is proportional to the contract changed. Root
[`package.json`](package.json) is the command authority; the commands below are
options, not a required sequence.

Linux is the active development and native Godot host. `npm test` runs the
supported Save Lab service/gate checks and both fake-tool launcher suites without
opening a window. `npm run build` and `npm run dev` build/run the Godot companion.
The rebuild has native Linux build/run/smoke/capture commands; live input checks
need an available desktop. Source and headless tests alone do not establish native
input, audio, focus or full tutorial behavior.

The retained WinUI default is `npm run test:winui`. The full legacy AppCore suite,
WinUI, Windows-targeted CLI and ZIP procedures remain Windows-gated. The unused
evaluation VM was retired; no Windows host is provisioned here. The Windows entries
below require a separately provided Windows validation host, not a Linux prerequisite
or an instruction to recreate the VM. Historical rebuild launchers use explicit `:windows` aliases
and need their older engine manifest revalidated against the current managed SDK.
No Linux result is Windows runtime acceptance. The dated August 30 full AppCore
run was **1,575 passed / 26 failed / 1,601 total**; its Windows-dependent failures
are not replaced by the focused portable results below.

| Change | Focused evidence |
| --- | --- |
| Documentation or deletion only | `git diff --check`, `npm run test:docs`, and the affected generator/reference check |
| A new or edited tracked `.md` header | `npm run test:doc-headers`, which is also inside `test:docs`. The contract is [`DOCUMENTATION.md`](DOCUMENTATION.md); the backlog of pre-standard documents is `tools/doc_header_backlog.txt` and may only shrink |
| AppCore behavior | `npm run test:save-lab` covers the supported Linux workflow on .NET 8; select an affected portable fixture and framework for other source changes. `test:appcore` retains the full Windows-dependent suite. |
| WinUI behavior or copy | On Windows, `npm run test:ui` or the affected test fixture, then one real-app workflow smoke |
| Save, options, copied-target, or patch safety | Save Lab changes use `test:save-lab`, including the real baseline, original/unselected-byte preservation and Linux publication guards. Other services need their own affected fixture. The retained Windows `test:safe-copy` includes UI regressions. |
| CLI | On Windows, `npm run test:cli` and the relevant AppCore test |
| Lore inputs/reader | `npm run test:lore-pack` is portable; run the LoreBrowserService/AppCore fixture on Windows unless that exact fixture has been demonstrated platform-neutral |
| Public payload/provenance boundary | `npm run test:safety` |
| Rebuild Core | `npm run test:rebuild-core` is the focused cross-host command and excludes only `Level100FerryLandingTests`; use `npm run test:rebuild-ferry-sweep` for that complete explicit oracle. The larger `npm run test:rebuild` aggregate additionally includes Windows-only Godot/capture gates and therefore requires a separately provided Windows host. **Current broad default receipt, 2026-08-31, at combined tip `c0e994ef` over causal Blaster commit `b8fca9ea`:** `dotnet test rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj --nologo --no-restore --filter 'FullyQualifiedName!~Level100FerryLandingTests' --logger 'console;verbosity=minimal'` measured **1,130 passed / 3 known failed / 1,133 total / 0 skipped**, **34 m 23 s**. The only failures in that dated run were the Linux-host Windows-message assertions `TapeFileWriteNew_RejectsExtendedNamespaceAliasInsideSuppliedKnownRoot`, `TapeFileWriteNew_RefusesUnsupportedDeviceNamespaceDestinations`, and `TapeFileWriteNew_EvaluatesResolvedIdentityOfExtendedAliasWithDotSegments`; the September 6 focused correction and result below close those failures without claiming a new broad run. The former `BlasterMissLaw_SeparatesTheRunsOwnHitsFromItsMisses` population mismatch now passes through exact internal round identity, and no assignment/start failure appeared. The 2026-08-30 **1,118/4/1,122** receipt remains historical. **PROGRAM P9 historical receipt, 2026-08-23, pre-change HEAD `221d7811`:** the actual runner first discovered 939 tests, including exactly the six ferry facts. After the split and three gate-composition facts, runner discovery proved **942 = 936 default + 6 sweep**, intersection zero, with the all-minus-default and explicit-sweep sets both exactly those six facts. The gate guard was RED 0/3 before script registration and GREEN 3/3 after. The explicit command passed **6/6** over the unchanged **20 perturbations × 2 arms = 40 runs**; VSTest reported **6 m 38 s**, while fleet-loaded wall time was **67 m 39 s**. Its pre-change 112.6 m overloaded run and the 2026-08-21 **862 passed / 1 failed / 863 total** run remain dated history, not current counts |
| Rebuild client/adapters | `npm run test:rebuild-client` |
| Godot toolchain or native behavior | `test:godot-host` checks launcher routing/process cleanup with fake tools. `build:companion-godot` and `build:rebuild-godot` build without a visible app. On an available desktop, `test:rebuild-godot-smoke` is a native synthetic smoke; actual input/audio and the Save Lab UI need a separate live workflow. |
| Frontend page drawing | Linux `capture:rebuild-godot -- -- --capture-plan=mainmenu` produces native captures. Compare them with the existing `tools/compare_capture.py` scorer and appropriate retail reference; capture success alone is not parity. The historical Windows `Capture-Frontend.ps1` combines capture and scoring. |
| Portable ZIP inputs or layout | On Windows, `npm run release:winui-zip` |
| Tip census claim in docs | Re-read `developer_state.json` → `current_re_authority`, require its literal READY/reducer/authority-receipt pins, and run the named full replay. Historical Gen10 and candidate Gen73 blocks are not current routing |
| Campaign ledger / generation TSVs | The externally pinned frozen bootstrap in `current_re_authority.verify`; a generation number, matching ledgers, self-derived pins, integrity-only success, or candidate reducer is not authority |
| Tracked evidence register or current authority pointer | `python ./tools/re_evidence_register_export.py --state developer_state.json --check-header-only` for the portable header gate; on the maintainer host, omit `--check-header-only` and use `--check` for literal-pinned full replay plus byte equality |
| C1 PE plate apply | Exact current pack path/bytes/SHA, entity/body identity, pristine-byte validation, and a field-scoped reducer. Independent normal/adversarial review is strongly advised for consequential changes but is not a fixed model matrix; see `reverse-engineering/REVIEW-PROTOCOL.md` |
| C2_BOUNDED_RUNTIME claim | Entity-scoped controlled runtime + can-fail refuter; refuse PE-only bulk C2 |
| Ghidra mutation | A declared cohort within the authorized task and the preservation/rehearsal/readback gate in `reverse-engineering/ghidra/README.md`; no writable opening of the tracked or cold owner. |

Rebuild commands materialize their exact retail inputs to ignored paths. Linux
selects canonical `local-lab/rebuild-godot` and discovers Steam library roots;
`-- --game-root "/absolute/game/root"` overrides discovery. A fresh checkout needs
its private canonical lab owner; worktrees reuse it. `prepare:rebuild-assets`
is sufficient when only that boundary changed.

The retained Windows `test:winui` builds one WinUI solution, then runs selected
AppCore contracts, UI tests excluding `WinUIRuntime`/`LegacyWpf`, and CLI tests.
It is not the Linux default or a replacement for native acceptance.

September 6 Linux phase results are in
`local-data/test-runs/linux-route-20260906-af1sa_l9/`: the default gate passed
**24/24** Save Lab/composition tests and **14/14** fake-tool launcher tests;
startup cache/audio tests passed **16/16**. Focused recorder/headless tests passed
**59/59**, and client launch/career tests **12/12**. The native First Flight smoke
completed, and the separately recorded **9,367-tick** session replayed twice with
both live expected hashes verified. That session was mostly idle and did not
complete the tutorial. The companion's native shell/file dialog opened, but its
UI write/reopen flow remains pending. Startup logo/montage audio decoded with
format/length readback; native playback of those new tracks remains pending.
These are bounded results, not a new broad Core, Windows or full parity receipt.

September 7 first-training corrections passed **43/43** Client tests selected by
`RetailFrontendSessionTests|RetailCareerLoadFlowTests`, then **68/68** focused
weapon Core tests and **5/5** Client input/smoke tests. The latter include held
Twin Vulcan input, Pulse hold/release/tap, release latching, destruction-event
aggregation and `FirstFlightSmokeScenario_ReachesFiringRangeAndCompletesWaypoint`.
The Jet check composes actual Client button samples with the existing isolated
flight fixture; it is not a complete flight playthrough. Two materialized smoke
input runs reproduced the new weapon-state hash before its focused and retained
Windows-launcher pins changed. Test output is retained in this task's transcript,
not a newly claimed log file. Native Godot built without warnings/errors; no
visible launch or Windows execution followed these changes. The shared Ghidra
cohort framework passed **88** focused tests; its actual isolated rehearsal,
stale-comment refusal, live apply, separate readback and PRE/POST restore probes
are recorded by the [Ghidra owner](reverse-engineering/ghidra/README.md).

September 8 focused checks passed **46/46 Core and 8/8 Client** for the shared
retail clock, reset/pause behavior, readiness boundaries and canonical state;
**73/73 materializer and 22/22 contact tests** for raw serialized geometry; and
**38/38 Core and 4/4 Client** for Large Pulse launch/contact and affected weapons.
These selections overlap and are not a new total-suite census. The existing
forty-step and FirstFlight fingerprints held without repinning. Logs share the
Linux run directory above: `retail-clock-{core,client}-20260908.log`,
`contact-float-geometry-materializer.log`, and `large-pulse-{core,client}-20260908.log`.
That contact change introduced schema v5; conditional canonical schema 45 retains an event frame
count when pause makes it differ from the already-hashed mission tick. The
checks do not establish a complete spatial blast, exact motion/expiry, event
dispatch ordering or a live playthrough.

The charged Pulse zero-spread correction first failed its direction regression
with 2,124 microradians of unwanted yaw, then passed **8/8 Core and 1/1 Client**
checks. Both scatter random draws remain, and no fingerprint changed. The
`large-pulse-zero-scatter-{red,green,client}-20260908.log` files retain the runs.

Contact schema v6 additionally preserves all 362 original part records,
including hierarchy inputs, opaque words and absent CPOS/CORI caches. Stripping
only those additions and restoring the old schema reproduces the exact v5
payload hash. The full materializer suite passed **74/74** and contact tests
**23/23**; the former log is `contact-v6-materializer-full-20260908.log` in the
Linux run directory above. Runtime sweeps remain unchanged. These inputs do
not establish the selected collision pose or runtime explosion report.
The subsequent mesh-pose arithmetic passed **7/7** focused tests, covering raw
Warehouse hierarchy inputs, signed zero and distinct matrix/store ordering.
Those results were captured in the task transcript. They do not establish
runtime cache/controller execution or the live FPU state.

The subsequent passive-bounds and geometry precision correction passed **43/43**
focused contact/pose tests. Eight new expectations first failed under the old
53-bit model. The corrected model rounds each operation to 24 significand bits,
retains intermediate exponent range and preserves the shipped three-axis bounds
quirk. A separate native x87 PC24/RN probe passed **9/9** synthetic arithmetic
checks, including a tangency decision and cancellation outside float32's
exponent range; it restored its process control word and did not run the game.
Logs are `geometry-pc24-{red,green}-20260908.log` and
`geometry-pc24-x87-probe.log` in the Linux run directory above. These establish
the bounded arithmetic model, not live gameplay precision or an integrated
spatial explosion scan. The preceding 33-test bounds run used the now-superseded
53-bit assumption and is retained as a dated result only.

Warehouse report construction and local sphere conversion then passed **49/49**
focused contact/pose tests; the materializer passed **74/74**. Tests exercise
the cached transpose, Z/Y/X accumulation, stored centre subtraction, signed zero,
reference geometry with a separate pose/identity, and the first-six cap before
a closer seventh contact. Initial test assumptions about root preview eligibility
and empty BBOX padding were corrected from the actual retained words.
Contact schema v7 adds only original `NumNmic/IsNmic` words; removing those fields
and restoring the schema reproduces the complete v6 payload exactly. Logs are
`warehouse-bounds-report-final-20260908.log` and
`contact-v7-materializer-20260908.log` in the same directory. Caller-supplied
poses/eligibility remain explicit; this does not validate the segment lifecycle
or connect the report to Simulation's explosion path.

The Warehouse immediate core2 cascade passed **40/40** contact tests and
**4/4** cold-start/pointer-route checks. Four causal expectations first failed
against the old single-part break. The correction preserves reverse child-list
order, leaves queued chimney parts unchanged, rejects a short event buffer before
mutation, and preserves component health/eligibility through snapshots and hashes.
Logs are `warehouse-cascade-red-behavior-20260908.log`,
`warehouse-cascade-final-20260908.log` and `warehouse-cascade-routes-20260908.log`
in the Linux run directory above. The snapshot test uses a component serialization
envelope, not a complete matching-registry runtime restore. Queued lifecycle,
debris rendering and native controller notification order remain open.

The subsequent subtree-sum and threshold correction passed **55/55** focused
contact/pose tests and **5/5** cold-start/pointer/handoff checks. Both new behavioral discriminators first failed: an actual
part-data leaf sequence emitted the wrong sum word, and a synthetic equality
state terminated early. A native x87 PC24/RN probe separately passed **2/2**
coefficient checks without executing game code. Logs are
`warehouse-sums-{red,green,routes}-20260908.log` and `warehouse-threshold-x87-probe.log`
in the same Linux directory. The leaf calls use supplied lethal amounts; the
boundary state is artificial. Neither is native player acceptance.

The Tank/Truck shutdown correction passed **123/123** focused Core checks:
contact/lifetime, Thing/Actor state, existing event scheduler, actor scripts,
tutorial progression and the established loss/pause-clock scenario. Four
behavioral expectations first failed against immediate removal/terminal damage
discard. Tests cover the frame-13 due-word discriminator (delivery at frame 23
even though the clock is below due), ring wrap, repeat damage without renewed
death/timer, immediate script teardown/objective clearing, pending restore/hash,
equal-time insertion order and visible zero-health target projection. The pause
timer test directly repeats BeginTick without advancing the manager; the loss
scenario separately exercises Simulation's paused clock. The input-only static
target run now measures four impacts **at death**, separately from accepted
post-death impacts, and stops after its three target objectives instead of
continuing through unrelated exercises. No driving commands were retuned.
Logs are `ground-shutdown-{red,green-initial,green,integration,final}-20260908.log`
in the same Linux directory. The subsequent cold-start/pointer/handoff selection
passed **5/5** (`ground-shutdown-routes-20260908.log`), with the same input drivers
and full-client/direct-control equality requirements. The Client first-flight
smoke passed **1/1** (`ground-shutdown-client-20260908.log`). The intermediate failures preserve obsolete
immediate-removal expectations and their corrections. These are deterministic
tests and static-byte contracts, not a native retail/Godot death playthrough.

Pending ground movement passed **83/83** focused mechanics, base-state,
contact and tutorial-progression tests (`ground-dying-motion-final-20260908.log`
in the same directory). All four cadence positions first failed against the
immediate-stop implementation (`ground-dying-motion-red-behavior-20260908.log`).
The final selection covers retained lite velocity, full-update stop, distinct
old position/orientation, mid-phase restore, deactivated pending actors and
Tank/Truck terrain clamping without a velocity rewrite. The earlier `red` log
records a corrected test literal compilation error, not a behavioral result.
Native float motion, initial cadence alignment and full surface behavior remain
open. The subsequent cold-start/pointer/handoff selection passed **5/5**
(`ground-dying-motion-routes-20260908.log`) without driver or fingerprint changes.
These results do not establish live play parity.

The retail-to-Core basis correction passed **112/112** focused Core checks
(Thing/Actor projection, mechanics, contacts, registry and existing World 110
construction) and **76/76** materializer checks. Both exact quarter-turn offset
cases and signed-zero preservation first failed against the old unsigned
permutation. The Core cases also check the resulting rendered point without
launching Godot. Real materialization reproduced **389 exact files**. The two
changed manifests contain only projected-basis signed-zero changes: 237 words
across Level 100's 44 actors/10 spawns, and 189 across World 110's 43 actors.
Raw retail words, positions and non-pose fields are unchanged. Logs are
`actor-basis-{core,python}-red-20260908.log`,
`actor-basis-{core,python}-final-20260908.log` and
`actor-basis-materialize-20260908.log` in the same Linux directory.
The materialized Client selection passed **7/7** after updating the manifest
identity and reproducing the new first-flight fingerprint twice; the earlier
`client-initial` and `client-pin` logs preserve the stale-pin failures.
The five existing cold-start/handoff tests also pass (`actor-basis-routes-20260908.log`),
but use reduced hand-built definitions and do not validate the new manifest.
The coupled waypoint/flyby checks passed **10/10** after preserving the four
negative-zero words in their authored Trainer basis; the prior mismatch and
the correction are retained in `actor-basis-waypoints-20260908.log` and
`actor-basis-waypoints-final-20260908.log`.

The subsequent cold-start harness correction passed **4/4**
(`cold-shipping-definitions-initial-20260908.log` in the same directory).
Both client and direct pointer control now use the production manifest decoder
and assert its definition identity and 44 authored actors. The unchanged driver
clears 22 targets, keeps abort false, completes primary objective 4 and reaches
Won; complete state and pose-trace equality remain required. Spawned Tank 1 is
selected by target group/ordinal and verified definition/script/owner, replacing
the reduced fixture's allocation-dependent name. The separate returning and
negative controls remain synthetic. This is a deterministic regression, not
player-observable live acceptance.

The Air Trainer initial-life correction passed **22/22** focused Core checks,
**6/6** materialized Client checks and **76/76** materializer checks. Both
authored and spawned creation first failed with zero life, then supplied the
physics profile's 3000 milli-life and retained it through snapshot restoration.
The ambient Trainer remains outside mission targets despite its positive life.
Materialization reproduced **389 exact files**; exactly two manifest leaves
change, both `initialHealth`. Logs are `trainer-life-red-20260908.log`,
`trainer-life-{core,client-final,python,materialize}-20260908.log` in the same
directory. Initial health does not close aircraft damage or death behavior.
The shipping-data cold-start selection then passed **4/4**
(`trainer-life-cold-start-20260908.log`). Both input adapters still reach Won
at tick 9191 with hull 8545 and identical full state/pose traces; their new state
hash is `7ddb32258aff65782bd232ba49c9d33a0b3c6c806f766c81f4271e48311c1ea8`.
No driver changes or live player acceptance are involved.

The finite Unit Euler update passed **19/19** native-output cases, then
**32/32** with adjacent PC24 mesh-pose arithmetic checks
(`unit-euler-core-final-20260908.log` in the same directory). Expected words
come from isolated execution of the unchanged retail routine under controlled
PC24; its PC53 comparison is also retained in `unit-euler-native-final-20260908.log`.
Coverage includes strict angle boundaries, pitch without wrapping, one-pass
normalization, multiplier four, signed zero, the float coefficient and a
subnormal step retained until the final store. Review replaced one initial
coefficient example that did not distinguish multiplication from division.
The subsequent matrix implementation passed **50/50** focused Core cases:
nineteen angle updates and thirty-one matrix outputs
(`unit-euler-live-matrix-20260908.log`). Twelve additional inputs came from
actual Plane calls in the private copied-game WineD3D run; the unchanged native
oracle also matched eleven consecutive live Euler/basis transitions. Its
constructor/cache/Euler samples all read PC24/RN. The exact private route and
receipts are in the [Unit evidence](reverse-engineering/binary-analysis/functions/CComplexThing.cpp.md).
Managed trig remains provisional outside those finite cases. The subsequent
`observe-plane-motion-a` run supplied 32 complete Move transactions (128 boundary
samples); `managed-plane-comparison.log` records 352 matching grouped compiled-Core
comparisons. The live mover now uses the ordered raw free-flight transaction.
Guide/controller observations supplied to that comparison do not validate the
whole production event, avoidance, contact or effect graph.

The living-Plane turn-rate correction passed **34/34** mechanics/Euler checks
and **1/1** repeated Client FirstFlight check. Both aircraft first failed at
14,544 rather than 43,633 microradians. Logs are
`living-plane-turn-{red,final-core,client-final}-20260908.log` in the same
Linux directory. The Godot build also passed with zero warnings/errors.
The native Godot smoke then completed at 2,148 ticks with the same fingerprint
on a private authenticated Xvfb display, at both 60 and 20 recording frames/s.
Only 20 frames/s matches this synthetic runner's one 20 Hz tick per frame.
The two `first-flight-smoke.json` reports are under `movie/` and
`movie-realtime/` in `local-data/first-flight/progress-video-20260908-a/`.
They establish the smoke route, including retry/return, without desktop access;
they do not establish live player acceptance. The recording's four ObjectDB leaks
were subsequently reproduced and corrected as described below.

The audio shutdown correction passed **174/174** focused Client audio, music,
startup, frontend and pause checks (`audio-retirement-client-20260908.log` in
the same Linux test directory), and the Godot build passed with zero warnings/errors.
Under the same private display/Dummy-audio route, `lifecycle-smoke-red-command.log`
reported four leaked objects. Stream-identity instrumentation in
`lifecycle-stream-identity-command.log` mapped eight leaked objects to the final
frontend and just-retired tutorial Ogg playback graphs. The instrumentation was
removed. `lifecycle-retirement-green-b-command.log` then completed the full smoke
without leaked objects or shutdown timeout. Its report retains tick 2,148, the
same state hash, fresh retry session and released world on return. Wall-clock
voice progress differs between runs and is not a deterministic/audio-parity claim.
The window-close check (`lifecycle-window-close-d-command.log`) and main-menu
capture (`lifecycle-capture-close-command.log`, 161/161 saved, screen-matched
frames) also exited cleanly. All five logs and the reports are under
`local-data/first-flight/progress-video-20260908-a/`. Earlier close-test attempts
failed in the private display setup; the accepted run pre-created the close
protocol atom that Godot expects a window manager to provide. No host desktop
input was used. The private driver's V-Sync warning remains; Windows and audible
output were not tested by these runs.

The shutdown mechanism follows the pinned engine's deferred playback deletion
in [AudioServer](https://github.com/godotengine/godot/blob/ed1daf0bf/servers/audio/audio_server.cpp).
The adapter polls native weak references through disposed Variants, avoiding a
new managed reference while waiting for retirement. It reports a failed drain
and nonzero exit after five seconds instead of treating a fixed delay as success.

The broader cold/returning selection passed **6/9**
(`living-plane-turn-routes-20260908.log`). Two failures remain real full-combat
gaps: the unchanged cold driver aborts with one final-wave kill, and the
returning driver aborts with five. Both cold input adapters still match exactly
at Won/tick 7260/hull 2750, hash
`72defa3e803b75a263687945a34f30c1b64afaa6c432fba7a4752b64a32c3d4f`.
Their full-combat assertions remain intact; the earlier successful routes below
predate this corrected flight behavior.

The third failure was an unsupported statistical hit-rate requirement. A
focused old-cap control passed its former limits, showing route sensitivity;
the source was restored to the measured full cap afterward. The test now checks
causal hit/miss receipts, unique round identities, damage and disappearance,
without treating an earlier sortie's percentages as a retail invariant.
That check passed separately: each control's 67 damage events matched 67 named
round hits (`living-plane-turn-{old-cap-control,causal-receipts}-20260908.log`).
Existing finite-cylinder contact tests and both full-combat requirements remain.

The test pilot's reticle-origin correction then passed **2/2** focused cases
that had both failed with its fictitious muzzle-height offset
(`reticle-fire-gate-{red,focused}-20260908.log`). The affected route selection
passed **6/8** (`reticle-fire-gate-routes-20260908.log`): returning combat still
aborts after five final-wave kills; cold combat now aborts with none. Both cold
adapters match at Won/tick 7194/hull 7050, hash
`53a682fd6693ccee442655189df25c7ff524cb646e1fe88d2e2be0b60b146b76`.
This fixes the driver's stated geometry, not the unfinished combat route.
Simulation code, steering gains and full-combat assertions were unchanged.

The direct-controller phase correction passed **23/23** focused Core checks,
then **1/1** Client FirstFlight smoke and **5/5** final cold/returning-route
tests. Causal regressions first reproduced firing on the unlock update, losing
a shot before the disable callback and using the moved emitter. The corrected
cold pointer route clears all targets without abort and exactly matches its
same-input direct-Core control's state hash and pose trace. The former
unquantized cold fixture issued different commands and lost to water; it was
retired as an invalid adapter-comparison requirement. The separate returning,
naive and trigger-disabled controls remain.

After the living-Plane rate correction, the repeated FirstFlight
fingerprint is `bc5d99c7f1fbd5e2bf86363e5309e5aa77f0ad132241ef08a9e61b15d75b3dfd`
(`living-plane-turn-client-final-20260908.log`). Its retained Windows-launcher
expectation was updated for the same tape, without Windows execution. The
earlier controller-phase logs are `controller-phase-final-focused-20260908.log`,
`controller-phase-final-smoke-20260908.log` and
`controller-phase-final-consolidated-routes-20260908.log` in the Linux directory
above. These are in-process regression results, not desktop tutorial acceptance
or a new broad-suite/ferry sweep. Full axis and event-priority parity remain open.

The World 110 integration review exposed a setter/restore mismatch: script
assignment still used the World 100 list. The new focused regression failed
before repair, then **24/24** affected construction/registry tests passed.
The existing Level 100 fingerprint passed separately without repinning.
Both Godot projects then built through the shared Linux launcher with zero
warnings/errors. This remains partial construction, not second-world runtime.

September 7 targeted RE reproduced a Core scheduler overflow-count mismatch:
the new callback regression failed before the fix, then the complete affected
`RetailEventSchedulerTests` fixture passed **32/32, zero skipped**. The
[event-system owner](reverse-engineering/source-code/io/event-system.md) records
the pristine instruction sites, body hashes and test's artificial callback
boundary. Its `scheduler-overflow-{red,green}.log` files share the Linux run
directory above. Actor/base and Unit initialization extensions are static
evidence, independently checked against selected complete pristine bodies;
no new runtime, full-campaign or broad Core result is claimed.

The subsequent World110 attachment change passed **20/20 Core facts, zero
skipped**: attachment arithmetic, real initial construction, detached player
construction and the existing World100 forty-step fingerprint. The unchanged
fingerprint was not repinned. The materializer's affected fixtures passed
**12/12**; the existing synthetic mesh parser/re-emitter fixtures plus new
emitter framing cases passed **65/65**, without running a corpus census.
The two real factory meshes produced the same four spawner transforms before
and after the parser change. The existing materializer published only the
changed 38,751-byte World110 actor/input asset.

An original native x87 probe under explicit `0x027f` checked all four attachment
positions, nine-component bases and child Euler outputs; it executed no retail
code. Exact source/log hashes and static body evidence are in the
[Unit transform owner](reverse-engineering/binary-analysis/functions/Unit.cpp/CUnit__UpdateTransform.md).
The `world110-attachment-{core,materializer,docs,safety}.log` and
`mesh-emitter-tests.log` files use the existing Linux run directory above.
Read-only reviews found no remaining parser or arithmetic defects after the
misplaced test assertions were corrected. These results do not establish
complete child initialization, second-world play or general animated/x87 parity.

The World110 tree-input and Simulation-boundary change passed **71/71 Core
facts, zero skipped**, plus **14/14 focused materializer checks**. The initial
adjacent hash check exposed the old test-only World110 Simulation running
Level100 Setup; that unsupported route now fails before initialization. Direct
native-88/native-84 mission coverage, definition/world mismatch checks, actual
construction/player tests and the unchanged World100 forty-step hash passed.
Logs are `world110-trees-core.log` (initial failure),
`world110-trees-core-fixed.log` and `world110-trees-materializer.log` in the
existing Linux run directory.

An in-memory counterexample at Level100 RLWD offset 52,498 changed a variant
to 4: the previous committed parser accepted it; the shared reader rejected it.
The exact archive pin already protected ordinary source selection. Independent
old/new parser comparison preserved the complete actual100/110 base actor/pine
outputs in both name modes and all actual100 level actors/waypoint paths.
Only the new 155,972-byte World110 input asset was published locally. Both tree
tables' raw record digests also reproduced after Core decoding. That step did
not initialize trees or integrate live listeners; the following step extends it.

The connected base-tree prefix passed **69/69 Core facts, zero skipped**, and
**10/10 World110 materializer checks**. The Core selection covers actual pine
construction, float terrain/mesh fields, one shared draw per tree, 1,481 real
readiness callbacks, world/player/reader identity separation, live sector-list
ordering and mutation, shared Actor state, existing scheduler laws and the
unchanged World100 forty-step hash. An initial radius-boundary test expected
the next float to cross a layer; direct arithmetic showed its product still
stores as 8.0f. The corrected test preserves that additional equality case and
checks the following float crosses. Logs are `tree-prefix-core.log`,
`tree-prefix-core-fixed.log` and `tree-prefix-materializer.log` in the same
existing Linux run directory. The ignored World110 asset is now 157,121 bytes;
only that derived input was regenerated. Read-only review also exposed and
closed mutable collection/index escape routes from the world owner.

These checks execute the reconstruction under explicit nearest/53-bit numerical
assumptions and a supplied incoming seed. They do not measure the retail load's
control word/seed, final tree orientation, full collision responses, transition
reset or World110 play. No desktop, Ghidra or broad runtime campaign was used.

The subsequent PostLoad sort change passed **73/73 selected Core facts, zero
skipped**, including the unchanged World100 forty-step hash. Four additional
MapWho facts cover original-tail rotation, mixed entries and repaired links,
the four finer layers, the preserved shared cursor and unchanged empty/single/
ordinary sectors. Intentionally including layer 0 failed its exact order check
(expected `[2,1]`, actual `[1,2]`); source restoration returned that fact to green.
Logs are `mapwho-postload-core.log`, `mapwho-postload-mutation.log` and
`mapwho-postload-restored.log` in the same existing Linux run directory.
Sort remains separate from the incomplete world-load sequence. Building,
Feature and startup findings in this pass are static evidence, not live checks.

The first Control Tower Core construction passed **96/96 focused Core facts**
and **11/11 World110 materializer checks**, zero skipped. Checks cover the
existing Actor/raw-pose owner, real 15-pine collision rejection, 29 segment
allocations/eight cores, exact graph/scale words, five undelivered shared events,
AI reader cells, world memberships and rejection of unsupported lifecycle,
restore and hashing. The existing World100 forty-step hash remains unchanged.
A deliberate child-tail mutation failed the independent sibling-order oracle
(expected `[33,32,31,30,2]`, actual `[2,30,31,32,33]`); original bytes were restored
and the expanded 96-fact selection passed,
including the existing World100 registry suite.
Logs are `control-tower-core.log`, `control-tower-materializer.log` and
`control-tower-mutation.log` in the same Linux run directory. Only the ignored
164,510-byte v5 World110 actor input was regenerated. These are headless
reconstruction checks under explicit fresh resource-route and numerical
assumptions. No renderer-cache, frame-delivery, damage, reset, retail runtime
or full parity acceptance is claimed.

The extension through the factory and repair pad passed **174/174 focused Core
facts** and **13/13 World110 materializer checks**, zero skipped. The selection
includes existing charge/selection laws and the World100 forty-step hash check.
It checks 64 segment owners, repair aliases and exact health words, factory
big-list/active-state behavior, copied spawner inputs, repair mode/charge state,
the shared effect chain, and 15 events with three Actor draws. Reversing the
weapon's two effect-node constructors deliberately failed its instance/order
assertion (expected weapon `+0x1c`, actual `+0x14`); source was restored byte for
byte before rerunning the selection. Logs are `initial-buildings-core.log`,
`initial-buildings-materializer.log` and `initial-buildings-mutation.log` in the
same Linux run directory. Only the ignored 175,671-byte v6 actor input was
regenerated. These are construction checks; they establish neither tank
spawning, repair firing, rendered World110 nor runtime parity.

The extension through SAT and all six icebergs passed **183/183 focused Core
facts** and **14/14 World110 materializer checks**, zero skipped. This adds six
connected-construction facts and the three existing attachment-pose checks to
the prior selection. It covers authored order, mixed world memberships, SAT's
mode-ID/index distinction and shared weapon state, Feature current/old poses,
collision spheres and distinct rounding stores, 1,513 pending events and the
1,491-draw stream. The World100 forty-step hash remains unchanged.
Two controlled mutations failed their exact facts: water Teleport overwrote
authored old Z; an inverted centre branch lost Building BBOX transformations.
Source was restored byte-for-byte before the full focused selection passed again.
Logs are `initial-icebergs-core.log`, `initial-icebergs-restored.log`,
`initial-icebergs-materializer.log`, `initial-icebergs-water-mutation.log` and
`initial-icebergs-centre-mutation.log` in the same Linux run directory.
Only the ignored 234,999-byte v7 actor input was published. This remains
headless construction evidence under explicit numerical/resource assumptions;
no retail/Godot runtime, Ghidra database or desktop was opened.

### Aircraft integration follow-up — September 12

`npm run test:rebuild-core` built successfully and finished with **1,354 passed,
8 failed, zero skipped**. Six failures exposed outdated component fixtures or
fingerprints after raw aircraft construction; the other two are the still-failing
cold and returning full-combat routes. This is not a passing broad-suite receipt.
The follow-up filter covering `Level100DestructionContactTests`, the weapon-state
hash variants, both direct-spawn drone cases, `HeadlessApplicationTests`, the
Hangar restore regression and the forty-step hash passed **78/78**. Logs are
`plane-integration-core-20260912.log` and
`plane-integration-focused-20260912.log` under
`local-data/test-runs/linux-route-20260906-af1sa_l9/`.

Actor-script restore now retains spawn admission and event-clock callbacks;
`RestoreDuringHangarPausePreservesNativeSpawnAdmissionAndCurrentClock` passed
through the native Hangar Pause/SpawnThing continuation. Standalone spawn
fixtures now invoke the same creation owner as production. Component-only
ground-death snapshots use the existing legacy hash envelope instead of claiming
an aircraft event clock they never advanced. Their lifetime, ordering and restore
assertions remain; full raw-aircraft restore has its own tests.

The forty-step golden-hash diagnosis is byte-exact, not a repeatability inference.
The current 41,057-byte canonical state hashes to `f121a469…f55b8`.
Flipping only `PlaneEvents.Float24Arithmetic` changes byte 40,798; removing that
one mode byte exactly reproduces the former `5e642166…caa54` fingerprint.
The ignored `hash-cause-20260912/` probe and `hash-cause-20260912.log` preserve
the command source and both full hashes. The mode is future-affecting state:
aircraft now use measured PC24 scheduling, while legacy scheduler callers retain
their default arithmetic. This diagnoses the missed pin update in the raw-plane
commit without treating the former state as a restorable current snapshot.

The compiled Headless first-flight tape replayed twice for 838 ticks with no
divergence: trace `0d835c29…591518`, final state `5edc8900…c9239`.
This is a revision fingerprint after accumulated changes since schema 42,
including raw aircraft motion and scheduler state. The test checks the bounded
startup state: the player has activated and moved in Walker mode, has no flight
permission, projectiles or kills, and the running mission retains raw Trainer
state and its PC24 scheduler. Direct replay measured activation at tick 665;
an older test comment's 996-tick value was not current. Despite its historical
name this tape does not exercise player flight. The forty-step byte-isolation proof above does
not explain every intervening change to this separate tape. The JSON and stderr log are
`plane-first-flight-replay-20260912.*` in the same directory. No assertion on
combat completion, native input, audio or rendering is weakened by these updates.
The cold and returning full-combat runs still reach Won through the low-health
abort, with objective 4 failed and no final-wave kills; they remain failures.

New general check output belongs under ignored `local-data/test-runs/` or a
descriptive child of `local-data/`. Preserve existing coupled `.artifacts/` and
specimen-bound `local-lab/` evidence paths. Validation output is not release content
or proof of unrelated runtime behavior.

The dated live-window attempt produced blank captures and established neither
input delivery nor a walkthrough; PrintWindow success alone is not pixel evidence.
Its historical correction is recoverable through `developer_state.json` → `_history`.

September 6 repository preparation used the existing focused checks: packet exporter
**21/21**, probe refuter **46/46**, probe author **43 checks with 17 falsifiable guards**,
and host-attestor unit tests **13/13**. The exporter tests use fake headless launchers;
no Ghidra project was opened. The probe author retained the three protected input hashes.
The attestor's help/diagnostic correction did not rerun full campaign verification.
Documentation and public-payload gates passed.

The independent follow-up reproduced two unsafe unregistered-packet cases and the
bind-alias output-admission defect before repair. The completed exporter suite passed
**24/24** with fake headless launchers. The tool runner passed **4/4** self-tests,
including Linux skip accounting and simulated Windows dispatch for the four identified
Windows suites; the full tools aggregate was not rerun. Evidence-register unit tests
passed **6/6**, the installed-write claim guard passed **14/14** classifier cases and
its tracked scan, and the docs/public-payload gates passed. State reduction compared
all protected values with the exact pre-cleanup Git blob; this is not full campaign
replay or native runtime evidence. The only Core source edit in this follow-up corrects
a historical replay comment; it changes no executable behavior.

The three Linux namespace-message failures in the August 31 Core receipt were
reproduced on September 6. The tests now expect Linux's earlier absolute-path refusal
and retain their Windows-specific assertions; production `TapeFile` behavior is unchanged.
The complete affected class passed **22/22, zero skipped** using
`dotnet test rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj --no-restore --nologo --filter FullyQualifiedName~HeadlessApplicationTests`.
Before/after TRX files are in `local-data/test-runs/preparation-20260906/`.
This focused result closes those three failures; it does not replace the dated broad
receipt or establish Windows/Godot runtime acceptance.

Do not add a new test during cleanup unless implementation behavior changed,
the regression is consequential, and no focused existing check covers it. Do
not fix unrelated failures discovered outside the changed contract.

## Remote source review — 2026-09-09 (execution pending)

The following is the September 9 remote handoff record; its host execution is
recorded below. At remote closeout it was pending verification. Source changes
are on `codex/onslaught-remote-integration-20260908`, following `82af1a41`.
Native-command and Python probes returned `TransportTimeoutError` without program
output; no compiler, test suite, Godot, Ghidra or retail program ran in this pass.
GitHub commit diffs were inspected and branch updates were read back separately.
Those checks establish source/publication state, not executable correctness.

| Source change | Added cases declared in source | Required verification |
| --- | ---: | --- |
| `f9d2e6dd`: FirstFlight launch admission | 14 | Existing `FirstFlightLaunchOptionsTests`, including legal repeated careers and capture with recording; reject smoke/capture conflicts and duplicate output arguments before file-opening adapters. |
| `752f913e`: command-tape JSON admission | 30 | `CommandTapeJsonAdmissionTests`, then existing replay/recorder/headless checks. Test duplicate decoded names, hidden schema/command/hash replacements, escaped keys, strict v4 migration, invalid roots and unchanged canonical identities for valid v4/v5 inputs. |
| `e8178614`: scheduler Update guard | 8 | `RetailEventSchedulerUpdateGuardTests` and existing `RetailEventSchedulerTests`. Test caught/uncaught nesting, interrupted retries, ring wrap, PC24/default arithmetic, retained rearm state, subsequent delivery/recycling and Init recovery. |

The 52 additional cases are an authored count, not runner discovery or passes.
Existing tests were retained. No tape schema, serializer output, scenario fixture,
golden fingerprint, normal scheduling arithmetic or gameplay constant was changed.
The scheduler guard is a reconstruction API correction; it adds no retail contract
grade or Ghidra correction. Microsoft's documented last-definition behavior for
[JsonElement.TryGetProperty](https://learn.microsoft.com/en-us/dotnet/api/system.text.json.jsonelement.trygetproperty?view=net-8.0)
supports the JSON ambiguity analysis; the fix uses .NET 8 enumeration APIs rather
than adding a newer-framework duplicate-property option.

On a functioning host, first prepare the existing admitted retail inputs and
perform the pinned project restore without changing locks, targets or engine.
The test projects reference Core's materialized resources even when an individual
fixture only checks parsing. With that setup already successful, run from the
repository root (these commands were NOT executed remotely):

```bash
dotnet test rebuild/OnslaughtRebuild.Client.Tests/OnslaughtRebuild.Client.Tests.csproj --no-restore --nologo --filter 'FullyQualifiedName~FirstFlightLaunchOptionsTests'
dotnet test rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj --no-restore --nologo --filter 'FullyQualifiedName~CommandTapeJsonAdmissionTests|FullyQualifiedName~RetailEventSchedulerUpdateGuardTests'
dotnet test rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj --no-restore --nologo --filter 'FullyQualifiedName~RetailEventSchedulerTests|FullyQualifiedName~ReplayTests|FullyQualifiedName~HeadlessApplicationTests'
npm run test:docs
npm run test:safety
```

Require nonempty runner discovery and preserve failures. Inspect the new negative
cases against the pre-fix implementations in an isolated review worktree when
establishing regression evidence; source reasoning alone is not a red/green run.
Broaden to affected Client/recording integration as results warrant. A native
Godot launch/capture check is still separate from argument-parser unit tests.

Review the full remote branch from the `13577577` feature baseline, not just these
three commits. Earlier `3654eb73` fixed actor-script restoration but still needs
`RestoreDuringHangarPausePreservesNativeSpawnAdmissionAndCurrentClock` executed.
`CanonicalHash_BindsRawPlaneStateAndWorld110SecondaryState` remains an unresolved
baseline diagnosis, not permission to replace its expected hash. Earlier remote
launcher/exporter commits contain dated test reports; this pass did not rerun them.
The proposed Python smoke report/log gate remains unpublished and unverified.
Record actual commands, outcomes and output locations here before integration;
do not transform these pending entries or historical receipts into claimed passes.

### Linux execution of the remote checkpoint — September 12

Reviewed the complete `13577577..f6ad243f` difference in
`.worktrees/remote-review-20260912`, preserving `031c975d` Windows retirement
and `31e9b437` local aircraft follow-up. Locked Core/Client restore succeeded
without target or dependency-lock changes. The integrated Core filter passed
**150/150**: new JSON/scheduler fixtures, existing scheduler/replay/recorder,
Headless, Hangar restore, forty-step canonical hash and raw Plane creation.
The new source's initial bounded Core selection passed **118/118**. The full
Client suite initially passed 905 with two failures and two existing skips;
after fixing the old spawn-pose expectation and the pre-raw-aircraft smoke
fingerprint, it passed **907, zero failed, two skipped**. Both failures preceded
the remote fixes. Emitter height remains above its seated Airfield; the
2,148-step smoke's gameplay assertions and independent input repeat still pass.
No flight/combat assertion or gameplay constant was relaxed.

All 52 new remote cases executed successfully. With the original four C#
implementations temporarily substituted in the isolated worktree, the selected
Core controls failed **29/39** and Client launch controls failed **13/23**.
Incoming source was restored byte-for-byte before the final passing runs.
Commands and results are in `remote-core-*.log` and `remote-client-*.log` under
`local-data/test-runs/linux-route-20260906-af1sa_l9/`. Core filters select
`CommandTapeJsonAdmissionTests`, `RetailEventSchedulerUpdateGuardTests`,
`RetailEventSchedulerTests`, `ReplayTests`, `CommandTapeRecorderTests`,
`HeadlessApplicationTests`, the named Hangar/canonical-hash regressions, and
`Level100RawPlaneCreationTests`; no empty selection is counted as a pass.

`python tools/godot_host_tests.py` passed **10/10**;
`python tools/export_packets_tests.py` passed **32/32**. First Flight initially
passed its 11 existing tests, but a new fake-engine control reproduced exit zero
with no report. `python rebuild/tools/first_flight_tests.py` now passes **14/14**,
including missing/malformed/incomplete completion reports, normal completion,
retained nonzero exit and captured timeout diagnostics. These are fake-tool
results. The new gate checks the completed smoke lifecycle; it does not port
or claim the entire retained Windows report/log validator. Logs are
`remote-godot-host-20260912.log`, `remote-export-packets-20260912.log`, and
`remote-smoke-completion-{red,green}-20260912.log` in the same owner.

Ghidra 12.1.3 compiled the changed packet exporter and exported 14 selected
functions from a verified read-only replica. The full 8,330-row function export
and program metrics matched the retained working POST exactly; the designated
working payload remained unchanged. Private outputs are in
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260912/`.
This verifies exporter execution and preserved structural state, not a complete
semantic audit, retail run, or native Godot acceptance.

### Plane-controller prototype and structural audit — September 12

The selected pristine executable was freshly hashed to the identity in the
[Ghidra owner](reverse-engineering/ghidra/README.md#plane-controller-event-argument-2026-09-12).
The reviewed checkpoint was inspected by file hashes only. The existing
Archive A working PRE was freshly copied, compared and reopened read-only.
The one-function manifest then passed isolated census/dry/apply and a separate
readback, independent raw-byte review, a sealed dry/apply/readback, and the
same live dry/apply/separate-readback sequence. Every headless invocation used
`-process BEA.exe -noanalysis`; only the declared isolated/live apply steps
omitted `-readOnly`. Exact live command arrays and receipts are retained in
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260912/plane-event-argument/`.

Full live function/program/variable/type/bookmark exports equal the sealed
rehearsal. Exactly one of 8,330 function rows changed. All other function and
variable rows, all program metrics and the complete saved stack-purge export
stayed identical. The POST recovery copy on Archive A passed a separate
restore/reopen with no missing, extra, size-different or hash-different file.
The function/variable exports cover internal functions; external/import
semantics are not certified by these comparisons. This does not certify every
decompiled expression: the spurious return-address
and vector-local artifacts persist and are documented in the controller owner.

`python -m unittest tools.ghidra_cohort_framework_tests` discovered **91 tests:
85 passed, six existing skips**. The new test executes the production Java
column-policy method. Five actual Ghidra refusal cases exercise stale, empty
and absent current-convention bindings, an undeclared prototype verb and
readback against PRE; a sixth runs the stale binding in actual apply mode.
All refuse without writes. Logs are `plane-argument-framework-*-20260912.log`
under `local-data/test-runs/linux-route-20260906-af1sa_l9/` and
`negative-controls/*.json` under the cohort owner. Initial incomplete census
bindings and a missing packet output directory were refused; corrected
invocations and their outputs are retained separately. No failed invocation
is counted as a successful export or mutation.

### Two native script callback signatures — September 12

`SetSpawnScript` and `IScript__SetAIState` passed exact raw dispatcher/body
review, isolated and sealed apply/separate-readback, independent full metadata
comparison, live dry/apply/separate-readback, and independently restored POST
recovery. A stale signature in the second manifest row was rejected in actual
apply mode before either row was written. All 8,328 non-target function rows,
all program metrics/types/bookmarks, and the entire saved stack-purge export
remained identical. Exactly eight parameter rows were added; the unknown
return rows stayed byte-identical. Native `RET 0ch`, declared parameter size
12 and saved UNKNOWN purge are recorded as separate facts.

`python -m unittest tools.ghidra_cohort_framework_tests` again discovered 91:
**85 passed, six existing skips**, including the production Java column probe.
Its tiny temporary source file now uses the platform temporary directory,
removing a Linux-only test-path assumption. The applier's only further change
is the independently reviewed two-row live grant. No C# code changed in this
cohort and no engine build/playthrough was needed. Command arrays, full exports,
negative control and recovery receipts are under
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260912/script-callback-arguments/`;
`script-callback-framework-20260912.log` is in the existing Linux test owner.

### Bounded Unit weapon selector — September 12

`python local-data/test-runs/linux-route-20260906-af1sa_l9/provider-selection-20260912.py`
passed **37** isolated original-code selection/reader cases. It executes ten
unchanged routine bodies plus three constants from the verified pristine
specimen at their original addresses. Its `.inputs.bin`, `.outputs.bin` and
`.results.json` stay private beside the script. Empty spawner lists, current
modes and nonnull nonballistic projectiles are admitted; terrain sampling and
reader clearing are stubs. This is not a retail playthrough or complete firing
acceptance. The script asserts 21 winning-score words and the new PC24
distance discriminator; other retained distances are observations. Independent
read-only review checked the initial 35-case artifact's actual ELF load mappings,
retained inputs/outputs and instruction-derived arithmetic; it did not rerun it.

The new `RetailUnitWeaponSelectionTests` passed **44/44**. With existing
`RetailWeaponSelectionTests` and `RetailWeaponChargeTests`, the final Core
filter passed **117/117**, zero skips:

```bash
dotnet test rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj --no-restore --nologo --filter 'FullyQualifiedName~RetailUnitWeaponSelectionTests|FullyQualifiedName~RetailWeaponSelectionTests|FullyQualifiedName~RetailWeaponChargeTests'
```

Negative controls used the same project and `--filter` with the exact owning
method. Last-wins selection failed **2/2** `EqualScoresRetainAttachmentOrder`
cases. Widened distance arithmetic initially survived **3/3**
`RawDistanceMatchesOriginalPc24Observations` cases. The original routine then
confirmed `(0.1f,0.1f,1.1f)` distance `3f8df578`, where the widened norm gives
`3f8df579`; adding this case made the mutation fail **1/4**. Source bytes were
restored exactly and the final 117-case run rebuilt the correct implementation.
The initial survivor is retained, not counted as a successful negative control.
Commands, TRX files, logs and restoration hash are under the same owner in
`provider-{last-wins,wide-distance,wide-distance-discriminator,final}-20260912.*`
and `provider-mutations-20260912.results.json`.

This additive selector does not yet change the actor firing loop. No gameplay
hash, scheduler behavior or combat assertion changed; no broad combat rerun,
desktop control or new Ghidra mutation was needed for this step.
`git diff --check`, `npm run test:docs` and `npm run test:safety` passed;
the public-payload check examined 3,978 candidates. The npm logs use the
`provider-{docs,safety}-20260912.log` names in the same private owner.

### Weapon provider Ghidra correction — September 12

The five-row `weapon-provider-semantics` manifest passed pristine-body and
independent semantic review, isolated dry/apply/separate-readback, full metadata
comparison, final-spec review, sealed rehearsal, live dry/apply/separate-readback
and independent POST recovery. All 8,325 non-target function rows and target
ABI/bodies/repeatable comments remained unchanged. All variables, types,
bookmarks, saved stack metadata and Plane-depth exports held. The only changed
program metric is `commentsSha256`; all eight live exports equal sealed POST.

A deliberately stale tag set in the fifth row was rejected in actual apply
mode before any row was written. Its separate function/program export matches
PRE byte-for-byte. PRE and POST recovery were restored to new local paths and
opened read-only; the tracked checkpoint was freshly hash-compared and preserved.
Exact command arrays, manifests, exports, control and recovery receipts are in
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260912/weapon-provider-semantics/`.

`python -m unittest tools.ghidra_cohort_framework_tests` passed **91/91**,
with no skips on this invocation. Its production-Java and exact live-twin
derivation checks passed; no framework gate changed. The live twin adds only
this reviewed cohort to its allowlist. Output is
`local-data/test-runs/linux-route-20260906-af1sa_l9/weapon-provider-framework-20260912.log`.

The documentation gate, name-checker self-test and `git diff --check` passed;
all 8,330 projected current names also match the live export. The first payload
check refused the encoded comment manifest. Its ten decoded analytic comments
(8,032 bytes) passed the existing content/secret guards and independent review;
the existing exact-path/hash register now admits only that reviewed file.
The final safety check passed for **3,980 candidates**. The initial refusal and
final pass remain separate `weapon-provider-safety-20260912.log` and
`weapon-provider-safety-final-20260912.log` files in the same test owner;
docs and name self-test logs use the matching `weapon-provider-` prefix.

### Aircraft weapon model inputs and model-time fraction — September 12

`npm run prepare:rebuild-assets` materialized **389 exact files**. The new
166,705-byte static-world manifest has SHA-256
`17d6112a96d548fb546999b79d3980d173ce5bb0a6f0da4573eae28fc5b62c09`.
It equals the independently projected update byte-for-byte. Removing only
the two aircraft profiles' `weaponMounts` and the corresponding provenance
entry recovers every previous JSON field. The prior 165,541-byte manifest and
expected update are retained as `aircraft-mount-input-pre-20260912.json` and
`aircraft-mount-input-expected-20260912.json` in
`local-data/test-runs/linux-route-20260906-af1sa_l9/` (the owner below).
The aircraft mesh remains separately hash-pinned; the static-mesh aggregate
and animation manifest were not widened to imply different source coverage.

`python rebuild/tools/materialize_retail_assets_tests.py` passed **90/90**;
the initial selected aircraft/Airfield/physics gate passed **17/17**. Tests
retain the legitimate earlier GunA/2, exact selector1, ordered uses/raw flags,
CPOS/CORI words, padding exclusion, cache ownership and constant ancestors.
Malformed tuples and ambiguous/missing bindings are rejected.

`TMPDIR=/var/tmp dotnet test rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj --no-restore --nologo`
passed **135/135** with the exact filter
`FullyQualifiedName~Level100ActorRegistryTests|FullyQualifiedName~Level100WaypointFixtureTests|FullyQualifiedName~SimulationTests|FullyQualifiedName~HeadlessApplicationTests|FullyQualifiedName~RetailWorld110InitialObjectSeedAdmissionTests|FullyQualifiedName~RetailWorld110LevelActorsTests`.
The final log/TRX stem is `aircraft-mount-core-final-20260912`; all logs and
TRX files use the owner above. New cases cover both immutable lookup views,
raw-word/use/order identity, nonfinite rejection and cross-definition restore.

`TMPDIR=/var/tmp dotnet test rebuild/OnslaughtRebuild.Client.Tests/OnslaughtRebuild.Client.Tests.csproj --no-restore --nologo`
passed **907 tests**, with the same two existing capture skips (header-font
retail glyph runs and the captured-water envelope). The final log/TRX stem
is `aircraft-mount-client-final-20260912`. Both final dotnet invocations used
`--results-directory local-data/test-runs/linux-route-20260906-af1sa_l9`, a
named TRX logger and `console;verbosity=minimal`. No engine or visible launch
was part of these checks.
`npm run test:docs`, `git diff --check` and `npm run test:safety` passed;
the safety gate checked 3,986 candidates. Their logs use the same owner and
`aircraft-mount-docs-20260912` / `aircraft-mount-safety-20260912` stems.

Definition format 8 adds model input; these runs retain world-state schema 47.
The 838-step Headless route compares **complete canonical bytes each tick**
against an independently stepped format-7 run after replacing only the new
definition identity. Both format-7 and older format-6 state/trace fingerprints
are recovered; the final `--expect` and two-repeat application checks pass.
The Client 2,148-step route uses the public canonical hash each step for the
same counterfactual, retaining both historical fingerprints and its existing
gameplay assertions. This proves input-identity causation on those routes,
not retail parity or full combat. Current fingerprints are owned by the tests:

| Route | State SHA-256 | Trace SHA-256 |
| --- | --- | --- |
| Core 40 steps | `0a0b24633f25bb96ac2e8b98443524de47e065b3744b9a15871c09595127a19d` | — |
| Headless 838 steps | `69bd64ac4b2f344c1300d64e6619931f57dc06d768dbd70a5f1b816aedb1f59a` | `0872e009a2fb254927a3014d539ae1039332ad5eb8bd8af38a6e77cc86575ec9` |
| Client 2,148 steps | `53c1cc64ace55542f48534d0554d6ffed57dda0eae48c9f2a55a928fea096e5e` | — |

Initial Core execution passed 131/135: two current pins required this causal
check, and two World110 isolation tests carried an already-old duplicate
fingerprint. Those isolation tests now compare complete before/after-admission
bytes; `SimulationTests` retains the golden owner. Initial Client compilation
rejected an internal canonical-byte helper; the existing public hash API now
checks each step without widening Core's public surface. Subsequent focused
Client execution reached only its expected old-pin failure after all causal
checks passed. These initial logs remain separate from final results. The
retained Windows smoke validator's older `bc5d…` pin was not repinned from a
Linux in-process result; its native route still requires separate validation.

`python local-data/test-runs/linux-route-20260906-af1sa_l9/plane-model-fraction-20260912.py`
passed **8/8 synthetic cases**. The selected pristine executable was freshly
hash-checked against `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The actual ELF load mapping contains unchanged `[0046ef40,0046efd5)`:
149 bytes, SHA-256 `72fba6a65a6d45e0104ea275f634c1cbb5e3beca98aefd36f489a0bd33b3e356`.
The appended return is outside this range. Supplied base times 0, 256, 65,536
and 1,048,576 use frame-length word `3d4ccccd`, each under PC24/RN and PC53/RN.
At 256 the respective fraction words are `3f7ff000` and `3f800000`, despite
identical stored frame time. Source, ELF, input/output, log and result JSON
share the script stem. The 2,099-byte result JSON has SHA-256
`07dca8819e7ecb20e01c8f1bb19b60cbe45d334ce6088f79b835564d0fa9aa28`.
Both 8,192-byte I/O files and all receiver writes were independently reconciled
against the saved cases. Stack/register checks, x87 TOP/invalid checks and
control-word readback pass; precision status flags are expected. No complete
MainLoop, CGame update, attachment query, renderer or desktop ran. This is a
counterexample to simplifying the supplied fraction calculation, not an
observation of ambient precision/time across retail play. The separate bounded
attachment composition below extends this evidence; production firing remains
open. Ghidra is unchanged.

### Aircraft attachment composition — September 12

`python local-data/test-runs/linux-route-20260906-af1sa_l9/plane-attachment-paths-20260912.py`
passed **27 synthetic cases / 33 calls**, including the follow-up assertions
over saved direct-cache keys and all meaningful cached pose words. It executes
unchanged Unit `004fc4e0` with native tag routing, list/mesh lookup, renderer
dispatch/refresh entry, direct evaluator, Actor getters and math. The ELF's
actual load mappings contain **21 unchanged routine bodies**, the jump table,
GunA/GunB strings, constants and selected Plane vtables; each is compared with
PE-mapped pristine bytes. The executable was freshly verified as 2,506,752 bytes,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The exact aircraft mesh is freshly checked against the separate pin in the
model-input section above. The synthetic emitter table retains the three
relevant records from the eleven-emitter mesh: GunA/2 before GunA/1, with
GunB/1 following; renderer-cache entries use actual part ordinals.

All source, ELF, assembly/object, I/O, log and result artifacts share that
private script stem. The script is 18,183 bytes, SHA-256
`8515aef582c6027c3720dd30b26a26dd3468aae49d9ecd5ae08cb3355da8cff5`.
The 26,556-byte result JSON has SHA-256
`badc59208887ea105562992486736c3945ab0c7b53ef3c6ae98ff621b1f057dc`.
Both I/O files are 552,960 bytes: input SHA-256
`732b7454bb3c5ef8e07ba6cff400e93560e96fd39a7611deb369654597d4d83f`,
output SHA-256 `49af51a963700de475ec46d3b2ebbc8b3c9b5693baaf739f2e8008ad9c9e8323`.
The stronger cache assertions leave these observed I/O/result bytes unchanged.
Independent read-only review reconciled all 25 mapped ranges, all 27 input
graphs, 33 output records and exact cache transitions against the saved artifacts;
it did not rerun the experiment. The ELF SHA-256 is
`1a49e3830627e92980a0a2c4a05f7a0ef3bd77ebe4cdd932af7617c03ec947d0`.

Predictions cover all twelve meaningful position/basis words. Tests preserve
the stack and nonvolatile registers, read back explicit PC24/PC53 control words,
reject x87 stack/invalid faults and check every arena byte outside the declared
output/current-X/profile-cursor writes. Fourth-word padding is not a meaningful
pose claim. The direct-cache snapshots bind the actual receiver/part, model
frame zero and supplied integer frame; other paths leave that cache zero.

The [Unit evidence owner](reverse-engineering/binary-analysis/functions/Unit.cpp/CUnit__UpdateTransform.md#isolated-aircraft-attachment-composition)
records the causal comparisons: supplied fraction below one changes fallback
pose; a synthetic basis distinguishes accumulation order; same-frame direct
reuse survives current-pose changes but not a frame advance or selected-part
change. This experiment prepopulates the two warm caches and supplies native
one-pose records through synthetic objects. It does not execute the loader,
cache population, animated/recursive hierarchy, nonnull motion, camera state,
complete game or weapon/round delivery. Unexpected selected-boundary calls
are rejection sentinels, never replacement pose implementations. No desktop
control or Ghidra opening occurred; the firing approximation is unchanged.
Actor translation varies only along X; these fixtures do not claim arbitrary
3D arithmetic or independently establish every Y/Z interpolation spill.
`npm run test:docs` and `git diff --check` passed for the existing evidence-owner
updates; the docs log is `plane-attachment-docs-20260912.log` in the same owner.

### Common controller and Unit weapon composition — September 12

`python local-data/test-runs/linux-route-20260906-af1sa_l9/plane-common-weapon-phases-20260912.py`
passed **21/21 synthetic cases, 27 calls**, including the rerun with complete
four-word retained/forwarded-vector assertions. It executes ten unchanged
retail routines, including common update, slot-4 refresh and the earlier Unit
phase bodies. The selected specimen remains 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
New raw-body identities are:

| Range | Bytes | SHA-256 |
| --- | ---: | --- |
| `004fef40..004ff322` | 994 | `7aca029cc9b576958d86a01282e847e6b624d29dcbc23b4ae2b89cbf8193fffe` |
| `004ff4f0..004ff70b` | 539 | `4bf6a880bceb0db303c5adab07deb05430df97d61a8bdbe34b99cb608958f60d` |
| `004fbc90..004fbcae` | 30 | `b5a96a9c821defad155def39a7ff2e12ac40d82fc9b1cda0aeeb0ed2f2fbee6d` |

The private source, ELF, exact input/output and result JSON share that stem.
The result JSON is 16,670 bytes, SHA-256
`29205cbcad5ce400f9d0732fee7a16a1bc392aa5db27589561eec70e96899120`.
The 86,016-byte inputs and 107,520-byte outputs were independently reconciled
against all cases, call traces and final receiver snapshots. The harness also
checks unchanged original bytes in ELF load mappings, preserved registers and
stack, x87 stack/error conditions and PC24/RN control word `007f`.

Counterexamples distinguish ready firing from the newly failed preparation
gate, preserve the earlier aim through phase 1, expose two selection calls,
and retain post-fire behavior when WeaponFire returns zero or negative.
Target aim capture/application, A/B feasibility, selection, acquisition,
reader registration, RNG, WeaponFire and waiting animation are explicit stubs;
support/spawner membership is absent. Positive delays and clear-after-fire are
synthetic branch cases. Phase completion is invoked directly. No real projectile,
Plane/Move scheduling, burst delivery, automatic acquisition or geometry is tested.
`plane-normal-static-boundaries-20260912.log` in the same owner binds the
attachment and line-query findings to exact bytes and the freshly hashed physics
records. [The Unit owner](reverse-engineering/binary-analysis/functions/CComplexThing.cpp.md#remaining-selected-provider-integration)
records the consequences and remaining production work.

### UnitAI exit comment correction — September 12

The exact one-comment manifest passed the preserved rehearsal/live/readback/
independent-recovery route in [Ghidra's owner](reverse-engineering/ghidra/README.md#unitai-exit-contract-comment-2026-09-12).
Only `004ffbb0`'s nonrepeatable comment changes; all eight live exports equal
the isolated rehearsal. The tracked checkpoint remains unchanged.
`python -m tools.ghidra_cohort_framework_tests` passed **91/91**.
The direct script invocation first failed to import `tools`; module invocation
uses the existing package without changing the framework's behavior.
The cohort receipts and exact commands are under
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260912/unit-ai-exit-contract/`.
No engine/runtime acceptance was inferred from these metadata and RE checks.
The first payload gate refused the new encoded-comment manifest. Its two
decoded analytic comments (3,509 bytes) passed control/secret/payload inspection;
only that exact manifest path and SHA-256 were registered through the existing
reviewed-comment mechanism. Other payload guards remain active. Final docs and
safety receipts are `plane-common-exit-docs-final-20260912.log` and
`plane-common-exit-safety-final-20260912.log` in the test-run owner above.

### Unit weapon preparation and fire phases — September 12

`python local-data/test-runs/linux-route-20260906-af1sa_l9/weapon-phases-20260912.py`
passed **26 synthetic cases / 32 calls**. Seven unchanged routine bodies and
one constant execute at their original addresses, checked through actual ELF
load mappings against the pristine specimen. The `.inputs.bin`, `.outputs.bin`
and `.results.json` remain private beside the script. Every case checks return
values where meaningful, phase/deadline/request/prepared words, call counts,
balanced x87 stack/control word, and that no other input bytes changed.

Cases distinguish strict reload readiness, zero/positive/negative preparation
delay, phase-1 completion at equality versus phase-2 completion after equality,
fire refusal clearing flags, and accepted Unit fire despite zero/negative
Weapon Fire returns. A canceled phase-1 case confirms that the outer completion
clears the phase after the real post callback set phase 2, retaining its deadline.
Independent read-only review checked all retained cases, ELF mappings, stubs
and instruction ordering; the reviewer did not rerun the executable.

Inputs use a current-mode weapon, empty spawner list, no deploy prerequisite
and no preparation/post effects. Weapon Fire and waiting animation are stubs;
the post callback and its empty-effect helper execute original code. These
checks establish no projectile, effects, phase-3 pose restoration, player route
or combat acceptance. No desktop control or C# runtime change was involved.

### Aircraft spawner exit inputs — September 12

All output below uses the existing private owner
`local-data/test-runs/linux-route-20260906-af1sa_l9/`.
The unchanged-code scripts `plane-controller-init-20260912.py` and
`plane-controller-exit-20260912.py` passed **18** and **26** synthetic cases.
Their original bodies/constants were checked in ELF load mappings; the first
executes the native SEH chain push/pop against private FS memory, and the
second executes the real state-1 transition helper. Full synthetic receiver
bytes, ABI, call order and event arguments are checked. The separate
`plane-controller-scheduling-20260912.py` passed **18** cases, extending the
retained eleven-case probe with supplied common-return, dying-owner,
missing-target and event-reuse controls. Inputs, outputs and JSON results remain
beside each script. Read-only reviewers checked the code and retained records;
they did not rerun them. Scene/reader/terrain/RNG/AddEvent stubs do not establish
actual event delivery, total transitive randomness or a completed exit.

Actual static-world materialization regenerated **66 outputs** in
`local-lab/rebuild-godot/airfield-exit-20260912-y8_etv9r/`.
Only `level100-static-world.json` changed: four Airfield spawn rows gained
`spawnerExitWaypoints`. Its 165,541 bytes exactly match a separately composed
expected document; deleting just those four added fields recovers the old
document. The other 65 outputs are byte-identical. PRE, expected, regeneration
log and publication receipt are `airfield-exit-manifest-{pre,expected}-20260912.json`
and `airfield-exit-materialize-20260912.{log,results.json}`. The new manifest hash
is `52a17547c8a91a8bae9abe3df291c02ba1a106bbf39e10c71642a0f32fd34879`.
The first extraction attempt refused missing CORI on the waypoint parts;
native cache-owner inspection then established their declared root inheritance.
No default orientation or launch transform was substituted.

`npm run prepare:rebuild-assets` accepted **389 exact files** after publication
(`airfield-exit-assets-ready-20260912.log`).
`python -m unittest materialize_retail_assets_tests`, from `rebuild/tools`,
passed **82/82**, with no skips (`airfield-exit-materializer-final-20260912.log`).
The selected Core run uses `dotnet test` with `--no-restore --nologo`, the Core
test project and filter
`FullyQualifiedName~Level100RawPlaneCreationTests|FullyQualifiedName~Level100ActorRegistryTests|FullyQualifiedName~Level100ActorPlaneRuntimeTests|FullyQualifiedName~SimulationTests|FullyQualifiedName~RetailMeshPartPoseTests|FullyQualifiedName~Level100ActorScriptRuntimeTests`.
It passed **113/113**, no skips; exact results and logs are
`airfield-exit-core-final-20260912.{trx,log}`. Coverage includes exit selectors,
independently calculated A/B pose words, input ownership, restore rejection,
legacy missing-input distinction, raw Plane creation and existing script flow.
The calculated pose cases are not retail observations.

The initial Core run passed 27 cases and failed its old canonical-hash pin.
The cause check then restored only the old definition identity and compared
**every canonical byte** with a forty-step run lacking the new exit inputs;
that comparison and the old `f121a469…` fingerprint passed before the deliberately
unchanged final pin failed. The final test retains those assertions and pins
`5a71982008e1a30f1684030e562fd45580cde149a3bcd3c3a4649201d4bb2750`.
Initial/cause results remain `airfield-exit-core-20260912.{trx,log}` and
`airfield-exit-hash-cause-20260912.{trx,log}`. Definition format 7 binds exit
selectors/model words; sets with no recovered exit inputs retain format 6.
No gameplay constant, scheduled aircraft behavior or combat assertion changed.

The complete Client suite then passed **907**, with its two existing capture
skips and no failures (`airfield-exit-client-complete-20260912.{trx,log}`).
It used `dotnet test rebuild/OnslaughtRebuild.Client.Tests/OnslaughtRebuild.Client.Tests.csproj`
with `--no-restore --nologo`, the same results directory and no filter.
The first run had 906 passes and one old First Flight hash failure
(`airfield-exit-client-20260912.{trx,log}`). The corrected test runs the complete
2,148-step input route with and without the exit definitions and recovers the
old `107e827d…` hash by changing only the definition identity. All route
assertions remain required; the new pin is
`2f5f634f8b785a304508fc39bba8f373148fc1292ec67271a1a21888a60d65de`.
A test-only intermediate compile failure attempted to call Core's internal
canonical-byte helper from Client tests; the final comparison uses the public
state hash, without widening that API (`airfield-exit-client-final-20260912.log`).
The Core test above retains its direct complete-byte comparison.

`git diff --check`, `npm run test:docs` and `npm run test:safety` passed;
the safety gate checked **3,980 candidates**. Their logs use
`airfield-exit-docs-20260912.log` and `airfield-exit-safety-20260912.log`.
These are in-process reconstruction checks, not native Godot, retail runtime,
full-combat or desktop acceptance.

### UnitAI initializer and event arguments — September 12

The `unit-ai-initializer` and `unit-ai-event-arguments` cohorts passed exact
pristine body/RTTI/comment review, isolated dry/apply, separate full readback,
sealed POST checks, live dry/apply and separate live readback. Commands and
results are in their respective children under
`local-lab/ghidra-first-training-20260907-v1/aircraft-audit-20260912/`.
Each `*.command.json` records the actual argv; `rehearsal-comparison.json`
records the independent full comparison, and `live-comparison.json` confirms
all eight live exports equal rehearsal. The first initializer dry run refused
unprefixed addresses before any writes; its corrected run passed. No guard
was weakened to admit that input.

The initializer changes one name/display signature, nonrepeatable comment and
tag membership; 8,329 other rows and all ABI/variable/stack metadata remain
unchanged. The event cohort changes two function signatures/comments and only
two explicit parameter rows: dispatcher name/type and exit parameter name.
Its other 8,328 function rows, parameter storage/source, automatic receivers,
provisional returns, saved stack/frame fields, types and bookmarks are preserved.
Program metrics change only the comment digest in each cohort.

The exact source project was byte-matched to the preceding independent POST
before each apply. Both new Archive A POST copies were copied, hash-compared,
restored elsewhere and opened read-only successfully. Each owner retains
`source-{pre,post}.json`, `tracked-pre.json` and `post-working-restore.json`.
The initializer's fresh PRE restore is `pre-working-restore.json`; its restored
POST then supplies the second cohort's PRE. The reviewed tracked checkpoint
was freshly compared and remained unchanged.

`python -m unittest tools.ghidra_cohort_framework_tests` passed **91/91**, no
skips (`local-data/test-runs/linux-route-20260906-af1sa_l9/unit-ai-framework-final-20260912.log`).
An intermediate run found two derivation failures because direct-script module
resolution had prevented emitting the live twin; module invocation corrected
the invocation, and the final diff adds only the two cohort IDs to that twin.
The initial result remains `unit-ai-framework-20260912.log`. The new comment
manifests contain six reviewed analytic comments, **5,762 decoded bytes**;
all pass the existing content/secret guards, and only their exact file hashes
are registered. No retail payload or database copy was added to Git.

The name-checker self-test, documentation gate and `git diff --check` passed.
All **8,330** current projected names also match the final live function export
(`unit-ai-event-arguments/current-name-comparison.json`). The initial docs gate
found a missing source-provenance header in the edited ThunderHead note; the
note now has its complete header, a fresh bounded caller inspection and no
unsupported Warspite-specific pseudocode. The header backlog shrank by one.
The public safety check passed for **3,984 candidates**. Gate logs in the same
test owner are `unit-ai-name-selftest-20260912.log`,
`unit-ai-docs-{,final-}20260912.log` and `unit-ai-safety-20260912.log`.
These checks establish the declared metadata corrections and preservation,
not full semantic audit or runtime acceptance.

### Aircraft exit lifecycle integration — September 12

Outputs below remain in `local-data/test-runs/linux-route-20260906-af1sa_l9/`.
`python local-data/test-runs/linux-route-20260906-af1sa_l9/plane-controller-exit-goto-20260912.py`
passed **26/26** synthetic cases with unchanged exit, transition, AirUnit GoTo
and Guide GoTo bodies at their retail addresses. The input executable was
verified as 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
The script, native ELF, inputs, outputs and `.results.json` retain body/constant
load-map checks, all controller words, ABI and x87 state. Separate CST/guide
receivers distinguish collision-ignore clearing from unchanged guide state;
the real GoTo adds its second altitude clamp after the exit arrival comparison.
Terrain, scene queries, vulnerability, StartDying, RNG and event admission are
stubs. The reviewer inspected the code and recorded results without rerunning
them. This is original-code experiment evidence, not a live game observation.

`plane-exit-static-boundaries-20260912.log` records bounded pristine disassembly
of the death path, vulnerability getter, collision-ignore write and MinAltitude
default/field setter. It also records the freshly verified physics input and
all 25 hash-pinned Level100 script objects: 1,925 instructions, no native-32
SetVulnerable call. The [Unit evidence](reverse-engineering/binary-analysis/functions/CComplexThing.cpp.md#aircraft-spawner-exit-and-script-readiness--september-12)
owns the interpretation. No Ghidra database was opened or changed for this step.

The final affected Core run passed **317/317**, no skips
(`plane-exit-core-final-20260912.{log,trx}`). It uses
`dotnet test rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj`
with `--no-restore --nologo --filter` selecting `Level100ActorPlaneRuntimeTests`,
`Level100ActorMechanicsTests`, `Level100ActorWeaponTests`,
`Level100DestructionContactTests`, `Level100RawPlaneCreationTests`,
`Level100ActorRegistryTests`, `Level100ActorScriptRuntimeTests`, `SimulationTests`,
`ReplayTests`, `HeadlessApplicationTests`, `RetailEventSchedulerTests` and
`RetailEventSchedulerUpdateGuardTests` by `FullyQualifiedName~` joined with `|`.
The log preserves the exact argv. The complete Client suite passed **907**, with
the same two capture-dependent skips and no failures
(`plane-exit-client-final-20260912.{log,trx}`); it uses the Client test project
with `--no-restore --nologo` and no filter. The existing forty-step and 2,148-step
fingerprints still pass unchanged.

The narrower **22/22** lifecycle selection is retained as
`plane-exit-lifecycle-focused-v3-20260912.{log,trx}`. It covers both restore
boundaries, targeted Ready while Init is paused, strict arrival/deadline edges,
both altitude clamps, distinct owner lifetimes, deleted listeners, hash/admission
guards, burst suppression/continuation and next-tick round movement. Before the
repair, both spawner-loss variants failed because generic StartDieProcess also
set DeclaredShutdown (`plane-exit-unit-death-red-20260912.{log,trx}`). The narrow
Unit transition now retains Dying, StartedDying notification, health/parts and
Move recurrence without manufacturing Died/Shutdown. Initial compilation and
the earlier 16/19-case results remain under `plane-exit-lifecycle-*`; the first
compile failure was nullable attachment access and was corrected with `.Value`.

The first adjacent selection passed 314 and failed three cases
(`plane-exit-core-affected-20260912.{log,trx}`). Two rate-cap fixtures supplied
Attack immediately after spawn; they now supply controlled normal-guide input
directly to the same production mover, retaining all original expected values.
The remaining Headless pin had missed the preceding exit-input materialization.
`plane-exit-legacy-fixtures-cause-20260912.{log,trx}` passes the two rate checks
and fails only the deliberately unchanged pin after proving that substituting
only the previous definition identity recovers every prior canonical byte across
all 838 ticks, including the previous complete trace. The final test retains
that proof. Its current trace is
`2da46d641e2187ead860869dd25b5abdf54f59aa5bac8830f7e661babe000309`,
final state `6ec3dfbbfd2351f824e4bab7685503e8e014a57f9e6990ad2c13a78dfc44ad4d`.
The direct `dotnet rebuild/OnslaughtRebuild.Headless/bin/Debug/net8.0/OnslaughtRebuild.Headless.dll --repeat 2`
result is `plane-exit-headless-observed-20260912.json` with no replay divergence.

The two full-combat drivers ran with their existing completion requirements
(`plane-exit-combat-boundary-20260912.{log,trx}`). The returning-career driver,
using its reduced fixture definitions, destroyed all 22 targets, damaged and
killed all six final drones for 6000 damage, completed objective 4 and reached
Won without abort at tick 5588/hull 11450. Its first run passed those assertions
and failed only the old exact tick 7621 pin. Those reconstruction endpoint
readings were updated; no driver commands, steering/damage constants or semantic
completion requirement changed. Exit scheduling, its RNG consumption and delayed
Ready all changed, so this result does not isolate one contributor to each shot.
The repeated returning run and existing causal-damage, abort-silencing and
weapon-event checks then passed **4/4**, no skips
(`plane-exit-returning-combat-final-20260912.{log,trx}`). This uses the same Core
command with a four-method `FullyQualifiedName~` filter recorded in that log.

The cold shipping-manifest route **still fails** the original six-kill assertion:
one final-wave kill, objective 4 Failed, abort at tick 7805 and Won at tick 8141
with hull 4400. Its client and pointer-quantized Core control have no divergent
tick and the same final hash
`b163d10bbd55bf1f183cad36c146f41c5cfa8016ff4a1480a05ab3b5faf6dc30`.
That failure remains visible; it was not repinned or weakened. Both drivers
read internal state and are in-process reconstruction instruments, not player
or retail acceptance. The earlier broad Core run remains a dated failing receipt.

`git diff --check`, the docs gate and public safety gate passed; the latter
checked 3984 candidates. Logs are `plane-exit-docs-20260912.log` and
`plane-exit-safety-20260912.log`; the final documentation refresh uses
`plane-exit-docs-final-20260912.log`.

This closes the selected exit prefix through scheduled Ready and handoff to the
existing approximate normal-control bridge. It does not close provider/common-AI
execution, complete dying flight, contacts, avoidance, full event/RNG order,
or the player-input tutorial and Save Lab UI acceptance routes. No desktop
control, visible launch, asset regeneration or gameplay-constant adjustment was
used. Schema 48 binds spawned exit ownership; unspawned schema 47 stays intact.
