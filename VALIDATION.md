# Validation

Status: active — the gate-selection table
Last updated: 2026-09-08 (first-training clock, contacts and Ghidra corrections).
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
WinUI, Windows-targeted CLI and ZIP procedures remain Windows-gated; the evaluation
VM is inactive. Historical Windows rebuild launchers use explicit `:windows` aliases
and need their older engine manifest revalidated against the current managed SDK.
No Linux result is Windows runtime acceptance. The dated August 30 full AppCore
run was **1,575 passed / 26 failed / 1,601 total**; its Windows-dependent failures
are not replaced by the focused portable results below.

| Change | Focused evidence |
| --- | --- |
| Documentation or deletion only | `git diff --check`, `npm run test:docs`, and the affected generator/reference check |
| A new or edited tracked `.md` header | `npm run test:doc-headers`, which is also inside `test:docs`. The contract is [`DOCUMENTATION.md`](DOCUMENTATION.md); the backlog of pre-standard documents is `tools/doc_header_backlog.txt` and may only shrink |
| AppCore behavior | `npm run test:save-lab` covers the supported Linux workflow on .NET 8; select an affected portable fixture and framework for other source changes. `test:appcore` retains the full Windows-dependent suite. |
| WinUI behavior or copy | In the Windows VM, `npm run test:ui` or the affected test fixture, then one real-app workflow smoke |
| Save, options, copied-target, or patch safety | Save Lab changes use `test:save-lab`, including the real baseline, original/unselected-byte preservation and Linux publication guards. Other services need their own affected fixture. The retained Windows `test:safe-copy` includes UI regressions. |
| CLI | In the Windows VM, `npm run test:cli` and the relevant AppCore test |
| Lore inputs/reader | `npm run test:lore-pack` is portable; run the LoreBrowserService/AppCore fixture in the Windows VM unless that exact fixture has been demonstrated platform-neutral |
| Public payload/provenance boundary | `npm run test:safety` |
| Rebuild Core | `npm run test:rebuild-core` is the focused cross-host command and excludes only `Level100FerryLandingTests`; use `npm run test:rebuild-ferry-sweep` for that complete explicit oracle. The larger `npm run test:rebuild` aggregate additionally includes Windows-only Godot/capture gates and therefore runs only in the VM. **Current broad default receipt, 2026-08-31, at combined tip `c0e994ef` over causal Blaster commit `b8fca9ea`:** `dotnet test rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj --nologo --no-restore --filter 'FullyQualifiedName!~Level100FerryLandingTests' --logger 'console;verbosity=minimal'` measured **1,130 passed / 3 known failed / 1,133 total / 0 skipped**, **34 m 23 s**. The only failures in that dated run were the Linux-host Windows-message assertions `TapeFileWriteNew_RejectsExtendedNamespaceAliasInsideSuppliedKnownRoot`, `TapeFileWriteNew_RefusesUnsupportedDeviceNamespaceDestinations`, and `TapeFileWriteNew_EvaluatesResolvedIdentityOfExtendedAliasWithDotSegments`; the September 6 focused correction and result below close those failures without claiming a new broad run. The former `BlasterMissLaw_SeparatesTheRunsOwnHitsFromItsMisses` population mismatch now passes through exact internal round identity, and no assignment/start failure appeared. The 2026-08-30 **1,118/4/1,122** receipt remains historical. **PROGRAM P9 historical receipt, 2026-08-23, pre-change HEAD `221d7811`:** the actual runner first discovered 939 tests, including exactly the six ferry facts. After the split and three gate-composition facts, runner discovery proved **942 = 936 default + 6 sweep**, intersection zero, with the all-minus-default and explicit-sweep sets both exactly those six facts. The gate guard was RED 0/3 before script registration and GREEN 3/3 after. The explicit command passed **6/6** over the unchanged **20 perturbations × 2 arms = 40 runs**; VSTest reported **6 m 38 s**, while fleet-loaded wall time was **67 m 39 s**. Its pre-change 112.6 m overloaded run and the 2026-08-21 **862 passed / 1 failed / 863 total** run remain dated history, not current counts |
| Rebuild client/adapters | `npm run test:rebuild-client` |
| Godot toolchain or native behavior | `test:godot-host` checks launcher routing/process cleanup with fake tools. `build:companion-godot` and `build:rebuild-godot` build without a visible app. On an available desktop, `test:rebuild-godot-smoke` is a native synthetic smoke; actual input/audio and the Save Lab UI need a separate live workflow. |
| Frontend page drawing | Linux `capture:rebuild-godot -- -- --capture-plan=mainmenu` produces native captures. Compare them with the existing `tools/compare_capture.py` scorer and appropriate retail reference; capture success alone is not parity. The historical Windows `Capture-Frontend.ps1` combines capture and scoring. |
| Portable ZIP inputs or layout | In the Windows VM, `npm run release:winui-zip` |
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
Managed trig remains provisional outside those finite cases. This primitive
does not yet replace aircraft movement; no new full-route result or replay
fingerprint is claimed for it.

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
