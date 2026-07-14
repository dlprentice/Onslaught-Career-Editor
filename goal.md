# Active Goal

Status: ACTIVE
Last updated: 2026-07-14
Policy: `goal.policy.md`

## Objective

Aggressively reconstruct Battle Engine Aquila from the provided Onslaught C++
source, the pinned legacy AYA extractor, the existing safe Python extraction
pipeline, the repository's accumulated RE corpus, Steam static evidence, and
controlled copied-runtime measurements. Complete deterministic local extraction
coverage for every observed retail resource family and rebuild source-named
game systems in deterministic Core. Keep proprietary payloads local, preserve
the installed game and original executable, and label source hypotheses, Steam
agreements, runtime measurements, rebuild contracts, and unresolved differences
separately.

## Current Slice

Continue from pushed integration main at `297afde2` (walker phase ExitCode
native-handle fix) after estimator/source-reference/reconciliation/prebuild
restore landings. The source crosswalk, bounded AYA observation/export/
reconciliation producers, retained CMSH attributes, tick-aware walker
trajectory estimator, walker source-reference fixture boundary, generation-
phase runner restore, CreateProcess-handle phase exit codes, and corrected
two-attempt Runtime lifecycle are integrated. The Home hierarchy/focus policy
is integrated as source/non-native behavior only; native first-run focus remains
unaccepted.

1. obtain a fresh separately authorized pair of exactly two accepted copied-
   runtime walker-forward measurements using the integrated Runtime tooling;
2. publish a bounded scalar-response contract in declared retail coordinate
   units only if both attempts pass, then separately accept the coordinate-
   scale, tick-response, rounding, quantization-error, and overflow translation
   policy before changing deterministic Core or verifying through headless and
   Godot clients;
3. extend the accepted inventory/export producer contracts into complete local
   corpus coverage for every observed archive/tag/extension and deterministic
   output family, keeping proprietary payloads ignored/local;
4. preserve the accepted `tools/battleengine_walker_source_reference.py`
   boundary: source-shaped symbolic control flow stays outside `rebuild/`, the
   hardened crosswalk remains authoritative, runtime/Core acceptance remains
   explicitly unsatisfied, and every trace-driving fixture control stays
   serialized and fail-closed; and
5. retain the Home native-focus nonclaim until a fresh native acceptance run.

No release or tag is authorized by this slice.

## Current Slice Progress - 2026-07-14

- Tick-aware walker trajectory estimator is on main at `58d8b5e5`. Wall-clock
  speed uses a fixed physics-tick lag window (50 ms hypothesis); actor velocity
  is treated as per-update displacement with edge, active-window, and
  settled-tail corroboration. Synthetic fixtures accept source-shaped ~20 Hz
  staircases under 100 Hz polling and reject the old continuous units/sec model.
  Focused gate: `npm run test:battleengine-walker-trajectory-sampler` → 27/27.
  Physics-update period and velocity units remain hypothesized, not retail tick
  identity proof.
- Walker source-reference fixture boundary is on main at `d4b9f83e`
  (`tools/battleengine_walker_source_reference.py`). Source-shaped symbolic
  control flow stays outside `rebuild/`; Core translation remains blocked until
  a measured scalar-response contract and separate retail-to-Core translation
  policy are accepted. Focused gate: 20/20.
- Bounded AYA corpus-reconciliation producer (`onslaught.aya-corpus-reconciliation.v1`)
  is integrated in this slice: parser-free terminal-outcome surface coverage
  without private payload reopen. Focused gate:
  `npm run test:aya-export-outcomes` → 11/11. Full private-corpus export remains
  blocked on missing legacy native extractor DLLs / VS C++ targets (MSB4278).
- Next executable critical path remains one fresh exactly-two-attempt
  copied-runtime walker measurement using the tick-aware sampler. Live retries
  today: pair-01 prebuild NETSDK1004 (fixed by generation restore `38e16316`);
  pair-02 prebuild green then profile-phase `.ExitCode` throw on .NET 10
  (fixed by CreateProcess-handle wait/exit `297afde2`); pair-03 profile/launch/
  receipt/focus succeeded then failed resolving the Python adapter host image
  via null `MainModule` (fixed by `QueryFullProcessImageNameW` + retry); orphan
  copied BEA from the crashed session was stopped. Prior 2026-07-13 pair failed
  attempt 1 on null runtime-chain / lifecycle deadline. No accepted contract yet.

## Current Slice Progress - 2026-07-13

- The fixture-backed CMSH static-preview parser and deterministic geometry-only
  OBJ emitter are integrated through `8533796f`. The accepted implementation covers
  the observed stride-36/FVF-0x152/topology-4 subset, exact VBUF reuse and body
  boundaries, bounded malformed input, guarded ignored-local publication,
  held-source revalidation, fatal rollback, and broken-reparse rejection. Its
  REFR-only direct geometry reuse, deterministic owner/instance ordering,
  reference-profile hierarchy validation without transform composition, and
  post-expansion caps. Its focused acceptance passes 28 Python tests; the
  original v0 golden remains unchanged. A guarded ignored session already
  produced 162 simple-profile OBJ candidates and 18 contact sheets. Metadata
  then narrowed the next pass to six multipart BattleEngine-name records. The
  exact-empty REFR wrapper correction is integrated at `b2aca609`; one ignored
  run assembled all six into validated OBJs (40,530 vertices and 35,386 faces)
  and produced an accepted 1536x768 anonymous three-view contact sheet. The
  human selected anonymous candidate 0003 singularly as the normal walker-mode
  Aquila. A guarded player-only local manifest then passed mesh/config preflight
  and one receipt-bound Godot 4.7 launch rendered it in First Flight at 1280x720
  on synthetic terrain. Initial and post-movement views kept the multipart mesh
  upright and bounded with the exact local-player/synthetic-terrain/non-parity
  HUD; input, asset-integrity, owned-process cleanup, and final zero checks
  passed. Candidate 0004 remains distinct despite byte-identical OBJ content.
  This proves local presentation only, not retail identity, transforms, fidelity,
  textures, or parity.
- The selected mapping is now deterministic through the local corpus boundary:
  candidate 0003 maps to lexicographic loose-corpus ordinal 0044,
  `m_f_be1.msh.aya`, and internal `f_be1.msh`. The asset is a non-skeletal but
  articulated 63-part PRNT/CHLD hierarchy with 15 direct REFR instances, rich
  frame data, and four currently visible texture dependencies
  (`cockpit.tga`, `BE_texB.tga`, `Chrome3.tga`, and `BE_texA.tga`). Exact
  parent/runtime transform composition, eight-slot material binding, DDS
  resolution, faction/player role, and released-runtime identity remain open.
- Reference inventory is drafted in
  `reverse-engineering/source-code/reference-submodule-audit-2026-07-12.md`:
  pinned fork/upstream provenance, current tracked counts, source completeness,
  build/test posture, AYA format limits, and component-license gaps are explicit.
- The selected recognizable subsystem is BattleEngine/JetPart movement and
  morphing. Read-only Steam static evidence is crosswalked in
  `reverse-engineering/binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md`.
- High-confidence static corrections identify `0x004081c0` as
  `CBattleEngine__Move`, `0x00410c50` as `CBattleEngineJetPart__Move`, and four
  adjacent JetPart helpers. The old May jet-stall interpretation is withdrawn;
  live Ghidra names remain unchanged under the separate-mutation boundary.
- The old `6411/6411` closure is now explicitly metadata accounting rather than
  whole-binary semantic correctness. This cluster separately scores owner,
  prototype/type, static semantics, source provenance, and runtime confidence.
- The active source slice now adds bounded parser-free terminal-outcome surface
  reconciliation to the accepted inventory/export producer contracts. It
  revalidates canonical observation/outcome identities, closed lane/output
  compatibility, exact observed archive/extension/tag/lane sets, and one
  exported verified representative per deterministic output family; binds the
  exact canonical rendered reports; and fixes nonclaims for exhaustive target
  matrices, successful full-corpus extraction, format completeness, and
  runtime/render fidelity. Focused reconciliation 11/11, inventory 28/28, and
  CMSH 44/44 tests pass. One ignored read-only census accepted all 301 copied
  AYA archives with 23,884 chunks, 16 tag families, and 139 mesh-body
  candidates, but no new full export/outcome reconciliation occurred. The
  required legacy native extractor DLLs are absent, the available build fails
  at `MSB4278` without Visual Studio C++ targets, and no tracked public
  end-to-end synthetic AYA/DDS/FBX fixture exists yet. Normal/adversarial Codex
  and sanitized normal/adversarial Cursor reviews are GO after closing digest,
  renderer, lane/output, and rejected-source gaps.
- The scalar-response contract remains pending copied-runtime evidence, and a
  deterministic Core implementation additionally requires an accepted retail-
  coordinate-to-Core translation policy. First Flight's transform/resource/
  movement choices remain synthetic.
- The rejected ignored walker-reference draft is repaired in the active
  worktree as `tools/battleengine_walker_source_reference.py` with the focused
  `test:battleengine-walker-source-reference` package gate. It reuses the
  hardened source/Steam crosswalk validator; pins the ordered two-water,
  slide/clear, friction/clamp, dash, and walk-cycle source shape; rejects
  impossible or dead branch controls; preserves the dash multiplier and source
  short-circuit order; separates scalar-measurable fields, future probes, and
  fully serialized fixture controls; binds an explicitly unsatisfied and
  publication-unauthorized exactly-two-attempt future gate; and names the
  current Core/constants/replay/scenario/headless candidate target set without
  changing Core. The public measurement schema is now v2 and declares retail
  world-coordinate units for position, speed, acceleration, latency, and
  ratios. Its Core target remains open and blocked until coordinate scale,
  tick-response, rounding, quantization-error, and overflow rules are accepted;
  direct translation into `WalkerSpeedPerTick` is forbidden. Publication now
  revalidates the entire report against a freshly executed canonical fixture or
  catalog, rejecting target, evidence-label, symbolic-value, and nested-fixture
  mutation immediately before serialization. Focused sampler later 27/27 after
  the tick-aware estimator, orchestrator 31/31, source-reference 20/20, and real
  crosswalk 58/58 tests pass. No accepted live measurement or Core behavior
  change has occurred.
- The cleanup-first copied-runtime walker measurement adapter is integrated at
  `9c22a5b6`. Its integrated focused gates pass 20 adapter tests and 49
  safe-copy/lifecycle tests. One later two-attempt aggregate was consumed and
  stopped correctly after attempt 1 failed before Q-down on an unclassified
  null runtime-chain hop and an incorrectly early observer budget; attempt 2
  was absent, cleanup reached zero, and no measurement or contract resulted.
  The six-path one-prebuild/hop-readiness correction is in non-native TDD.
  Exactly two new fresh accepted attempts are still required before publishing
  a contract or changing Core.
- Two dedicated user-owned lanes now aggressively mine the pinned Onslaught C++
  source and the legacy AYAResourceExtractor/current Python extractor. Their
  purpose is executable source-to-Steam reconstruction and extractor/GUI
  completeness, not additional documentation inventories or a second competing
  Python pipeline.
- The user selected the reviewed identity-canary progression. The durable design
  in
  `reverse-engineering/binary-analysis/battleengine-morph-runtime-observer-design-2026-07-12.md`
  starts with an unpatched safe-copy Level 850 control/positive/repeat matrix,
  defers field semantics and timing, and uses Level 100 only as later
  corroboration. The user pre-authorized the recommended continuation. The
  first structured dry run passed; its live control role then failed closed
  before receipt creation, and a fresh controlled retry is pending the bounded
  path-length correction described below.
- The Stage A implementation is decomposed in
  `roadmap/battleengine-morph-identity-canary-implementation-plan-2026-07-12.md`.
  It reuses AppCore and the existing live harness, adds no product API or
  package-script chain, and reserves broad validation for one integrated
  runtime-slice closeout.
- Stage A Task 1 is implemented and pushed through `b1458c0d`. The new private
  renderer parses PE32 sections/relocations, verifies the canonical specimen
  and module-relative code fingerprints, emits four hardware-only execution
  probes, and materializes an exact-schema public control/positive/repeat
  matrix without paths, pointers, code bytes, PIDs, windows, or raw logs. Ten
  focused synthetic tests pass; no game or debugger process was launched.
- Stage A Task 2 is integrated through `078efaf7` and `6fe26639`. A shared
  strict receipt validator binds PID/start time, executable/module/manifest
  identities, PEB-derived launch arguments and working directory, window, and
  command digests. CDB canary attach is local-only with an exact fresh marker,
  held command identity, bounded logs, and exact cleanup; foreground input
  tracks and releases held keys with visible failure on unconfirmed release.
  Independent re-review approved the correction. The integrated runtime-safety
  profile passes 8 profile, 22 CDB, 16 input, and 14 smoke-helper tests without
  launching the game or real debugger.
- Validation simplification is integrated through `7771e404` and `f75f5007`.
  `npm test` is now the proportionate quick profile; runtime-helper safety,
  historical proof, repository-boundary, and release gates remain explicit.
  The executable inventory reports 1,512 scripts and 125 npm dependency edges;
  generated release accounting is current at R0=6,291, R2=0, R3=3,
  R4=13,184, and the 726-file curated manifest remains valid.
- Stage A Task 3 is integrated through `8dc733f4`, `526df1c2`, and `123ca8ac`.
  One protocol choice derives the unpatched Level 850/configuration 2 launch,
  Player 1 `Q`, no patches, no screenshots, canonical command/receipt binding,
  exact marker/input checks, private fresh/create-new artifacts, and ordered
  cleanup through census. Its cleanup phase plan is shared with
  failure-injection tests; independent normal and adversarial Codex re-review
  approved with no Critical or Important findings.
- Stage A Task 4 is accepted and pushed at `3d23c176`. Exact ignored authority
  and lease schemas, canonical no-process dry-run, fixed serialized role order,
  per-role early identity rejection, bounded immutable-byte materialization,
  parent-interrupt invalidation, and manifest-before-summary publication are
  covered by 111 focused non-live tests. Normal and adversarial Codex review
  approved the committed unit; no game or debugger process was launched.
- Task 5 preflight found two non-live contract defects before execution: the
  ambient resource-root `BEA.exe` can differ from the canonical executable that
  AppCore validly selects through the in-root `BEA.exe.original.backup`, and the
  generated profiles root did not match AppCore's canonical AppConfig root.
  The correction hash-binds the ambient executable without treating it as the
  specimen, requires the effective override and copied executable to remain
  canonical, rejects out-of-root/unsupported/reparse/hardlinked overrides, and
  gives every role a fresh private AppConfig-derived `GameProfiles` root. A
  matrix-wide ambient digest now fails closed before each role and again before
  publication. The changed executor and harness suites pass 22 and 30 tests.
  The full six-suite canary/helper set passes 119 tests, the packaged runtime-safety route and
  AppCore/UI preflight gates pass, and the generated runner builds with zero
  warnings. Normal review converged to approve after the matrix-wide baseline
  fix; adversarial review approved with no Critical/Important blocker after one
  stale plan sentence was corrected. The first live matrix stopped in the
  no-input control before receipt creation because the generated private
  profile name produced a 288-unit AppCore mutation-sentinel path. No
  positive role or public materialization ran; owned-process cleanup completed,
  source hashes were unchanged, and the private failed-run evidence is
  preserved. The bounded correction maps the fixed roles to compact private
  profile names, reducing the failed control path to 249 UTF-16 code units and
  the longest matrix path to 251. Both dry run and live harness now reject any
  projected sentinel path at or above the 260-unit legacy Win32 boundary,
  including non-BMP names, before profile creation. The exact six-suite set
  passes 122 tests, the generated C# runner builds with zero warnings, and
  normal/adversarial Codex re-review approved after the UTF-16 correction. The
  correction was pushed at `07a0e398`. A second fresh dry run passed, and its
  live no-input control reached copied-profile launch, receipt creation, and
  CDB startup. The x86 CDB process-object path then resolved as `ntdll.dll`
  rather than `cdb.exe`; the helper failed closed with a null payload, and the
  generated runner mishandled that null while evaluating postconditions. No
  positive role or matrix materialization ran. Ignored receipt/observer/error
  evidence and an explicit failed-run closeout are preserved, the original
  authority/leases remain hash-identical, released-resource census is zero,
  and source/copy integrity held. The focused correction uses the existing
  CIM-first PID resolver before process-module fallbacks, makes generated JSON
  predicates reject non-object values, requires complete marker-ready observer
  binding before any input, and retains the original launched Process object
  through revalidation, kill, and wait. The six focused suites pass 127 tests,
  the generated runner builds with zero warnings, and normal/adversarial Codex
  review approved. That correction was pushed at `aa2ec621`. Retry 3 used a
  fresh authority/lease set and absent proof root; its dry run passed and its
  live no-input control reached copied-profile launch, exact receipt creation,
  and x86 CDB attachment. The generated command then failed before
  `MORPH_CANARY_READY`: it used C++ `&&` under CDB's MASM evaluator, and bare
  `BEA+RVA` was parsed as numeric `0xBEA+RVA` because `BEA` is all hexadecimal
  digits. No input, positive role, or matrix materialization ran. Ignored
  closeout and lease-release evidence are preserved, owned BEA/CDB counts are
  zero, and authority, lease, source, ambient, and effective-executable hashes
  remained unchanged. The bounded correction uses MASM `and`, explicit
  `!BEA+RVA` module symbols, and canary-only `-ee masm`. The six focused suites
  pass 128 tests; a disposable native x86 CDB proof accepted all 32 corrected
  byte comparisons, rejected a deliberate mismatch, and cleaned up exactly.
  Normal and adversarial Codex re-review approved, and the correction was
  pushed at `c39f91de`. Retry 4 then reached exact marker-ready no-input control
  evidence with zero events and complete cleanup, but its outer rejection text
  was lost by an operator wrapper that retained only stream hashes. Offline
  collection/materialization, controls, digests, and ambient revalidation all
  passed; no positive role ran. Retry 5 therefore used fresh controls and
  durably preserved both outer streams. It reproduced the exact child exit 2;
  the control again reached `MORPH_CANARY_READY`, emitted zero events,
  preserved source/copy integrity, and cleaned up before the outer matrix
  stopped without sending positive input. An initial capture-count diagnosis
  was wrong: normal and adversarial control-flow review showed that
  `RunMorphCanary()` returns before the generic capture predicate, so that
  proposed behavior change and its false-positive test were removed. The
  dedicated canary predicate also requires its caught `failure` string to be
  empty, but the v1 private artifact does not preserve that string. The current
  TDD instrumentation therefore writes a create-new private
  `canary-failure.json` only when a caught failure exists; it does not change
  the success predicate, public schema, input, or process behavior. Its 36
  focused tests and a fresh generated-runner build pass with zero
  warnings/errors. Retry 4 and 5 have ignored failed-run closeouts and lease
  releases; neither published a matrix. The diagnostic was reviewed, committed,
  and pushed at `a6a0962e`. Retry 6 then used fresh controls, passed dry run,
  and again reached exact marker-ready no-input control evidence with zero
  events, integrity, and complete cleanup. Its new private diagnostic recovered
  the actual caught failure: the runner reopened active `windbg.log` through
  `File.ReadLines` while CDB still owned a write handle, so the default sharing
  mode threw before input. No positive role or public matrix ran; the failed
  evidence closeout and lease release are preserved. The TDD correction keeps
  the exact pre-input on-disk marker gate but reads through a read-only
  `FileStream` with `FileShare.ReadWrite`, UTF-8/BOM detection, and the same
  exact one-line/duplicate rejection. All 37 focused helper tests pass, a fresh
  generated runner builds with zero warnings/errors, and a disposable .NET
  proof reproduced the old sharing violation while the new reader accepted one
  marker without closing the writer. The correction was reviewed and pushed at
  `9e438c11`. Retry 7 used fresh controls and passed the no-input role with one
  exact ready marker, zero canary events, unchanged source/copy hashes, and
  complete cleanup. The first positive role then failed closed before proving
  Q causality: `SendInput` returned false for every attempted event, the legacy
  helper fallback emitted no canary event, Q release was not confirmed through
  `SendInput`, and the repeat role/public matrix did not run. A private immutable
  correction note supersedes the initial cleanup interpretation; it records
  only a best-effort legacy key-up before exact process teardown. Offline ABI
  inspection found the root cause: the helper's 64-bit `INPUT` union contained
  only `KEYBDINPUT`, marshaled to 32 bytes, while native Win32 requires 40. The
  current TDD correction completes the union, validates 40-byte x64/28-byte x86
  layout before input, records `SendInput` errors, forbids legacy fallback as
  primary canary delivery, truthfully tracks standalone key-up failures, and
  makes the generated runner require exactly two successful `SendInput` events
  with no fallback. All 21 input-helper and 39 smoke-contract tests pass, and a
  fresh generated runner builds with zero warnings/errors. Normal review found
  and closed one fail-closed consumer gap for missing zero-valued counters;
  the strict property/type/value predicate now has a compiled malformed-JSON
  negative probe. Final normal and adversarial review accept the correction.
  The correction was committed and pushed at `2983fef8`. Retry 8 used fresh
  controls and again completed the no-input role. In `positiveTransform`, the
  exact focused Q down/up reached `SendInput` with the valid 40-byte layout,
  two confirmed events, no fallback, and confirmed release, but CDB emitted
  zero exact canary events and the copied target was absent before the
  receipt-bound managed-stop phase. The repeat role and public materialization
  did not run; source/copy integrity held, zero owned BEA/CDB processes
  remained, and an ignored failed-run closeout preserves the bounded truth.
  The target-exit cause remains open.
- A disposable x86 CDB/process lifecycle proof disproved the generic claim that
  force-stopping CDB while `g` is active necessarily kills its target: the
  disposable target remained alive. It also proved that stopping the target
  first lets a queued `q` terminate CDB and emit `quit:` with zero leftovers.
  This establishes the safer cleanup protocol but does not explain Retry 8 or
  prove any BEA hook. The current TDD correction requires exact managed-process
  start ticks, preserves ordinary AppCore already-gone cleanup while rejecting
  it as canary exact-stop evidence, stops only the
  exact root process, binds CDB's effective local `-pd` arguments, retains its
  exact handle through teardown, compares target/CDB exit times, requires one
  queued cleanup marker plus one `quit:` marker from a finalized log, and makes
  census inspection failures fail closed. The generated runner builds with zero
  warnings/errors; 1,317 AppCore and 148 focused runtime/canary tests pass.
  The initial normal review approved while adversarial review found the exact
  identity/order/census gaps now corrected. Fresh post-fix reviewers exhausted
  the available subagent quota and were not substituted. Root acceptance
  reconciled every blocker against the final diff: the retained CDB handle
  prevents PID reopen, exact start ticks plus canary rejection of
  `AlreadyGone` prevent stale-target acceptance, target/CDB exit ordering plus
  unique finalized cleanup/quit markers prove ordered teardown, effective
  local `-pd` arguments are bound, census inspection fails closed, and only
  exact roots are stopped. Fresh final gates pass 1,317 AppCore tests, the
  95-test runtime-helper profile, 23 orchestration tests, 17 process-identity
  tests, 13 renderer/materializer tests, and a zero-warning generated build.
- Retry 9 used fresh ignored controls and an absent proof root. Its dry run
  passed, and the live no-input control launched the exact clean copied retail
  executable, bound CDB before stop, observed the target and debugger physically
  exit, emitted the expected cleanup and `quit:` markers, and ended with a clear
  owned-process census. It still failed closed because AppCore reacquired the
  target by PID without retaining its native process handle; after target exit,
  `Process.ExitTime` could no longer reopen the process, so the canary could not
  prove the exact target exit timestamp. No positive role or public matrix ran.
  A disposable five-run A/B proof reproduced unreadable exit time in 5/5
  unpinned processes and preserved it in 5/5 pinned processes. The TDD
  correction validates the bounded timeout before process acquisition, pins the
  exact process handle before start-time/module identity validation, keeps it
  pinned through close/kill/wait and exact exit-time readback, narrows
  already-gone handling to acquisition failure, and releases the handle in a
  balanced `finally`. The final AppCore suite passes 1,319 tests; the 95 focused
  runtime-helper tests and `git diff --check` pass. Codex normal/adversarial
  review accepted the corrected identity and cleanup boundary. Sanitized serial
  Cursor/Grok normal/adversarial consultation used
  `cursor-grok-4.5-high-fast`; its only material PID-reuse concern was withdrawn
  after reconciliation with the retained Windows process-handle lifetime.
- The exact-handle correction was pushed at `e5a6b275`. Retry 10 then used
  fresh ignored controls, passed dry run, launched the exact clean copied
  retail target, and completed the no-input target/debugger cleanup with exact
  managed target exit-time readback, finalized cleanup/quit markers, unchanged
  source/copy hashes, and a clear process census. It still failed closed and
  published no matrix because the retained CDB process's final `ExitTime` was
  about 160 ms earlier than the managed target's final `ExitTime`. Independent
  normal/adversarial review concluded that cross-process timestamp inequality
  is not a valid Windows debugger lifecycle invariant: CDB can receive the
  target exit debug event and detach/quit before the target's kernel shutdown
  completes. Retry 10 remains failed because its log does not explicitly prove
  which event released `g`. The accepted correction direction requires exact
  receipt-owned target exit-event evidence from CDB (for example a strictly
  parsed `.lastevent` section), preserves every identity/marker/census guard,
  and forbids timestamp tolerance or marker-only acceptance. That correction
  is integrated through `f74ac902`: the exact CDB log stream is retained from
  readiness through final parsing without delete sharing, one bounded global
  `.lastevent` section must identify the exact receipt-owned target PID and a
  nonzero thread, CDB must exit cleanly without a forced stop, and the existing
  exact process/module/receipt, hash, marker, managed-stop, and clear-census
  requirements remain mandatory. Root verification passes the 124-test runtime
  tooling profile, 26 focused event-parser cases, 23 orchestration tests, 17
  process-identity tests, and 13 renderer/materializer tests. Codex normal and
  adversarial review accepted the correction; sanitized serial Cursor/Grok
  normal review accepted it, and the adversarial summary's claimed missing
  start-CDB/census gates was rejected against the exact authority and package
  gate definitions. A fresh Retry 11 is now allowed. Retry 10 remains failed
  and cannot be promoted or reinterpreted.
- Retry 11 used new ignored authority/lease controls, a new absent proof root,
  fresh copied targets, and the integrated exit-event parser. Dry run passed.
  The live no-input role again stopped before either positive role and
  published no matrix. Its retained log contains one exact target exit event
  for the receipt-owned PID, the ordered `.lastevent` delimiters, cleanup
  marker, and `quit:` marker. The exact managed stop succeeded, source/copy
  hashes remained unchanged, and the final owned-process census was clear.
  The role still failed closed because CDB returned `-1` while reporting the
  intentionally stopped target's exit code as `0xFFFFFFFF`; the current runner
  requires CDB exit code zero before parsing the retained evidence. This is now
  a bounded harness-contract investigation. Arbitrary nonzero CDB exits are not
  accepted, Retry 11 remains failed, and no positive-role causality claim exists.
- The Retry 11 exit-status correction is integrated through `647bbaa4`. Normal
  CDB exit zero remains unchanged. Exceptional CDB exit `-1` is accepted only
  when the exact receipt-owned target event reports `0xFFFFFFFF`, managed stop
  proves both force requested and exit observed, and the retained post-readiness
  transcript is semantically clean through EOF: exact generated prelude, exact
  six-line event/time/cleanup/quit region, real invariant debugger timestamp,
  and only explicitly allowed shutdown boilerplate. Any unrelated diagnostic,
  impossible date/offset, duplication, omission, or reordering fails closed.
  All existing process/module/log, no-runner-force, hash, stop, and census gates
  remain mandatory. The four focused suites pass 132 tests, the generated
  runner builds with zero warnings/errors, and Codex plus sanitized Grok
  normal/adversarial review accept. A wholly fresh Retry 12 is authorized;
  Retry 11 remains failed and cannot be reinterpreted.
- Retry 12 used wholly fresh ignored authority/lease controls, a new absent
  proof root, fresh copied target, and a passing dry run. The live matrix again
  stopped in `noInputControl` and published no sanitized result. Exact process,
  module, receipt, code-fingerprint, managed-stop, target-exit, hash, and final
  zero-process checks passed. CDB produced the expected forced target exit and
  ordered terminal markers, but this WinDbg build emitted eleven legitimate
  `NatVis script unloaded` lines after `quit:` while the parser admitted only
  one. The run therefore failed closed on terminal diagnostics before either
  positive role. This is a bounded shutdown-grammar defect, not an identity
  result. Retry 12 remains failed and cannot be reinterpreted; another live run
  requires an integrated, adversarially tested correction and wholly fresh
  controls.
- An independent campaign-governance adversarial review returned
  `GO-WITH-COURSE-CORRECTION`: the canary produced useful runtime-safety
  infrastructure, but twelve failed runs moved it into diminishing-return
  churn. The bounded repeated-NatVis parser correction may finish, but no
  automatic Retry 13 is authorized. Runtime identity is now a timeboxed side
  lane rather than the playable rebuild's critical path.
- A read-only workstation presentation audit found the canonical ignored game
  mirror and pinned Godot cache, but no usable combined AYA/DDS/Fbx runtime
  directory and no exported GLB/OBJ. Normal review initially recommended
  rebuilding the legacy extractor; adversarial code-path review instead found
  that Python already performs bounded AYA inflation/CMSH carving and that the
  missing durable link is a CMSH vertex/index parser. Codex and sanitized Grok
  review converged on one narrow `CMSH profile v0` geometry-only OBJ milestone;
  Visual Studio, Blender, FBX, DDS/textures, and LNDS terrain are deferred.
- A redacted structural inventory then parsed all 213 ignored loose AYA
  archives and disproved the initial strict profile: zero bodies matched its
  topology/counter/record assumptions. The observed common subset uses topology
  field 4, strip semantics, declared body lengths, frame/optional records, and
  explicit first-VBUF reuse. No tracked evidence identifies a player Aquila
  body, so profile support and local visual identity selection are now separate.
- The independent architecture challenge is integrated at `b010589d`. It keeps
  WinUI/AppCore and deterministic Core/Godot, but changes the campaign scoreboard
  to player outcomes and accepted behavior contracts while freezing recursive
  proof growth and framework-rewrite churn.
- The coherent Patch Bench boundary is integrated through `a1924ed5`: the
  ordinary copied-profile journey remains visible while five specialist groups
  live under one collapsed Lab; next-copy choices remain disclosed, copied-
  options values are snapshotted before confirmation, narrow actions are fully
  readable, and native smoke now rejects stale default-path builds.
- The reviewed observed CMSH contract is integrated at `90f46237` and explicitly
  supersedes `3f6c41c4`. Implementation is leased only for the GPL parser,
  generated fixture/tests, pure client safety oracle, and focused package route;
  native Godot/bootstrap and retail identity remain later serialized steps.
- The Lore editorial inventory is integrated through `d7492d3b`: 955 tracked
  packable documents are classified into 11 families, nine canonical/projection
  divergences remain preserved, and generated metadata is explicitly triage
  evidence rather than rights, safety, freshness, or historical approval.
- The community-preservation rights boundary is integrated through `51b79571`:
  personal contact coordinates and unsupported ownership, dissolution, backing,
  and permission conclusions are removed; repository and incorporated-source
  licenses are explicitly limited to the material they cover. The inventory
  remains 955 documents with nine preserved divergences.
- The RE behavior-contract slice is integrated through `76528902`. It orders
  camera, walker, jet, and morph observations under a runtime-required candidate
  and surgically fail-closes only the confirmed stale `0x00411630` and
  `0x00411aa0` CMonitor pairs while preserving unrelated mutator operations.
  The RE lane's accidental unleased full-suite/native output is invalid and was
  not used; exact process cleanup was verified.
- The non-native scalar walker-forward sampler and public-safe two-attempt
  schema are integrated through `aee7916b`. Eighteen synthetic tests cover
  coherent reads, receipt/input/cleanup failure, timing and drift rejection,
  exact two-run stability, and private-data exclusion. No copied-runtime
  attempt, public behavior contract, direction claim, or Core change exists yet.
- The optional local presentation lane is integrated on `main`. It pins the
  Stuart Onslaught reference at `5352a81` and the AYA reference plus narrow
  rectangular-DDS correction at `53b10b0`; adds an ignored exporter/bootstrap
  workspace; and lets the Godot adapter load only bounded, self-contained GLB
  or bounded custom-parsed OBJ presentation meshes. Core remains unchanged,
  ordinary smoke remains synthetic, publication is content-addressed and
  manifest-last, and no asset origin, visual fidelity, handling, or parity is
  inferred. Post-merge rebuild, docs, and 19,523-file payload gates pass. One
  initial smoke-runner helper missed its PID record; an immediate isolated
  rerun passed all six cases and supersedes that transient attempt.
- Windowed & Mods now represents the compatibility base truthfully. The exact
  `resolution_gate` and `force_windowed` rows remain visible in Lab with stable
  automation/details IDs, but are checked, disabled, and labeled required and
  automatically included. Every selection/reset/preset path reasserts them;
  Clear removes optional mods only; both Create entry points share one pure
  readiness projection and synchronous busy latch; and click handling rejects
  invalid selection before confirmation. AppCore injection, catalog rows,
  bytes, receipts, backups, and installed-game boundaries are unchanged. The
  final source/build suite passes 1,319 AppCore and 155 UI tests with two
  expected private-corpus skips; focused preflight and native hands-off proof
  also pass without creating a copy or launching BEA.
- The two normal compatibility actions now keep their exact labels complete at
  760px through centered whole-word wrapping and equal minimum height. Stable
  automation names, handlers, selection semantics, and two-column placement
  are unchanged. A fresh hands-off native run passed with empty pre/post
  process census and no copy or game action; focused integration tests pass.
- The agent-guidance audit is integrated at `56738f9b`. Repo startup now uses
  progressive task routing and targeted validation, makes Steam/runtime
  evidence outrank source hypotheses, and keeps RE-informed versus future
  strict clean-room claims distinct. It also found two separately owned code
  follow-ups: stale BattleEngine probes/mutators can reapply withdrawn
  `CMonitor` ownership, and AYA export preflight omits `Fbx.dll` plus the FBX
  template.
- The dedicated Ghidra full-reaudit closeout is integrated. It independently
  recovered and reviewed the deleted Cursor campaign boundary, verified the
  stable 6,411-function inventory and 459-address endpoint delta, reviewed 92
  unique proposed corrections, applied and exactly read back 91 confirmed rows,
  and rejected the erroneous `0x004dac90` manifest row rather than forcing it.
  The live project and complete pre/post stores are verified; the incomplete
  historical ledger remains explicitly incomplete. Static metadata quality does
  not prove runtime behavior or rebuild parity. `0x004dac90` remains bounded
  metadata debt for a separate review and mutation lease.
- Normal and adversarial review found and closed stale active-index, deep-link
  historical-label, include-parser/count, and current-roadmap contradictions.
  The corrected include inventory is 254 unique quoted targets with 202 absent.
- Source-truth closeout passes exact canonical/Lore synchronization, 4,329
  documented-command checks, 3,663-file/6,323-link Markdown validation, 18,604
  files passing hygiene/line endings, 19,465-file hard-payload safety, 19,649-file
  submodule-aware payload safety, migration inventory, JSON parsing, active
  stale-truth scanning, and `git diff --check`.

Do not expand the generic First Flight arena as a substitute for fidelity. The
target is one small authentic behavior slice whose provenance and differences
from retail are inspectable.

## Verified Starting Point

- Public release `v1.0.9` remains the latest published unsigned portable WinUI
  ZIP. It includes the friendly root layout, SHA-256 sidecar, and 949-document
  offline Lore pack.
- The 29-row patch/profile contract is machine-accounted at 20 visible options
  (9 stable, 11 experimental), 9 hidden companions, 17 dependency edges, and
  118 conflict edges. AppCore binds mutations to exact pinned catalog rows,
  publishes backup/checksum/apply/restore files atomically, and restores
  damaged or truncated copies only from an integrity- and provenance-verified
  full-file backup. The Python patch helper remains a lab surface.
- Windowed & Mods now separates the required compatibility/recovery path and
  two bounded optional Player Mods from a collapsed structured Lab of legacy,
  research, visual, executable, and launch/control diagnostics; no patch bytes
  changed. Save Lab Game Options also presents the official modern-controller
  Steam Input setup path, in-game binding/sensitivity steps, and explicit
  limits: Toolkit edits copied options only and does not configure Steam Input,
  detect a controller, or prove improved control feel.
- The Sol Ultra baseline was committed and pushed at
  `5a7bacecac5e813804355d68a8e51973100e0331`; local `main`, `origin/main`, and
  live remote `refs/heads/main` matched with divergence `0 0`.
- The contributor authority and quick-check advancement was committed and
  pushed at `798c339505fb85cc782abbd4b07df81e143c2284`; `npm test` is now the
  normal active-product baseline.
- The deterministic rebuild Core was accepted and pushed at
  `3cc382e8fa206c3a3f885f9dec4dedd2297b9f97`. The playable First Flight client
  was accepted in source at `0ed4e706753c350ae1ec835d6dd466feddd587c7`;
  its 721-selected/726-materialized plain candidate passed the standalone test
  suite, payload/inventory, 463-file/138-link Markdown, 74-package notices, and
  718-file hygiene/line-ending gates.
- After the Ghidra closeout worktree is retired, Git has four active worktrees:
  this `main` checkout, the player-value task, the bounded runtime-harness
  correction worker, and the Cursor submodule/local-presentation branch under
  final hardening. Completed Task 2, validation, agent-guidance, and Ghidra
  worktrees were removed after integration and preservation checks.
  Seven earlier empty Codex Desktop worktree shells were removed on 2026-07-11.
- Sixty-one historical `campaign/*` and `codex/*` branch tips were preserved
  in a verified local Git bundle before branch cleanup. Twenty-four otherwise
  unreachable commits and all three stashes were also preserved. Both bundles
  passed `git bundle verify` and a disposable restore drill. Four
  `backup/*` refs remain separate and outside every deletion list. After the
  pushed baseline was accepted, the 61 obsolete local branch names were
  removed; no backup ref, stash, archive ref, object, or Git GC was touched.
- The repository currently has 19,389 tracked files, including 13,385 under
  `reverse-engineering/`, 2,614 under `tools/`, and 1,710 under
  `release/`.
- Before this slice, root `package.json` exposed 1,494 scripts, including 1,472
  test scripts and 840 Ghidra wave scripts, with no default `npm test`. The
  history remains, but contributors now get one explicit quick-check entry.
- Baseline checks passed on 2026-07-11:
  - `git diff --check`
  - state JSON parsing
  - `npm run test:doc-commands`
  - `npm run test:repo-hygiene`
  - `npm run test:hard-payload-safety`
  - `npm run test:public-allowlist`
- The WinUI first-use/accessibility closeout passed a zero-warning solution
  build, `npm test` (1,307 AppCore tests; 136 WinUI tests plus 2 expected
  private-catalog skips), twelve explicit Home state/route cases, shell accessibility,
  restored-Video lazy-VLC, compact Patch Bench interaction, real read-only
  audio/video playback, and the 11-screen visual smoke. Full Markdown links,
  notices, public allowlist/hard-payload, and repository hygiene gates passed.

The exhaustive hygiene and payload gates each scan roughly the entire tracked
tree and took about two to four minutes locally. They remain valuable signoff
gates, but they are not an ergonomic default for every small contribution.

## Campaign Completion Criteria

This campaign is complete only when all of the following are true at the same
time. Passing one bounded slice does not satisfy the overall goal.

- **Repository and collaboration:** current docs/state agree; contributor and
  PR workflow is usable; validation is proportionate; finished tasks/worktrees
  are retired after evidence absorption; and clean `main`, `origin/main`, and
  the live remote ref match with divergence `0 0`.
- **WinUI Toolkit:** one coherent first-time player journey is accepted from
  game-source setup through safe-copy creation, optional normal Player Mods,
  launch, and recovery/recreation. Accessibility and native checks cover that
  journey; remaining page/control audit debt is ranked rather than treated as
  an unbounded terminal gate.
- **Patches and mods:** all normal surfaced options are exact-specimen/byte
  bound, dependency/conflict accounted, copied-target-only, truthfully labeled,
  and covered by focused tests. Research/legacy rows are clearly segregated in
  Lab, and no known stale active helper can reapply withdrawn ownership or
  bypass the copied-target boundary.
- **Reverse engineering:** the Ghidra closeout is integrated; accepted
  corrections are reflected in current RE/Lore truth; stale mutators are
  retired; and the selected movement/morph slice has accepted Steam static plus
  copied-runtime identity/behavior evidence. Inventory counts alone do not
  satisfy this criterion.
- **Lore and documentation:** canonical/mirror synchronization, selected
  current-truth checks, provenance boundaries, and contributor front doors are
  accepted for the active product/rebuild path. Broader editorial review remains
  a ranked follow-on program; historical uncertainty stays labeled rather than
  rewritten as fact.
- **Authentic rebuild vertical slice:** a user can reproducibly launch a
  BYO-asset Aquila/terrain experience that is recognizably BEA-like, with at
  least one measured movement/morph/camera behavior contract implemented in
  deterministic Core and consumed by the Godot adapter. Remaining visual,
  handling, mission, audio, and gameplay gaps are explicit.
- **Safety and closeout:** installed game/original `BEA.exe` are untouched; no
  proprietary payload or private proof is published; reviews converge; state is
  reconciled; commits are pushed; and no release/tag/upload occurs without its
  separate current authorization.

These criteria require one authentic, evidence-backed playable vertical slice,
not full-game or perfect parity. A complete retail-equivalent rebuild remains a
longer program after this campaign.

## Authority And Boundaries

The user authorized source, documentation, test, tooling, and local cleanup
work plus verified commits and pushes for this campaign.

- Keep the installed game and original `BEA.exe` read-only.
- Patch and runtime workflows use copied targets or app-owned roots.
- Do not commit proprietary game payloads, copied executables, arbitrary saves,
  extracted assets, screenshots/frame dumps, raw debugger logs, full Ghidra
  databases, secrets, build output, or generated package output.
- Release publication, signing, installer/MSIX/Store work, live Ghidra
  mutation, and destructive private-payload cleanup are separate decisions.
- While the dedicated Ghidra closeout task owns the live-project boundary,
  this coordinator and its workers must not mutate that project or its
  backups. Consume its reviewed handoff only after that lane releases scope.
- Static accounting is not runtime proof. Source naming is not retail behavior
  proof. A clean-room plan is not a runnable rebuild.
- Because the current maintainers and agents have read GPL-licensed source and
  detailed decompilation material, implementation is described as an
  RE-informed original-code prototype unless a separately staffed,
  sealed-spec implementation process and license review support a stronger
  clean-room claim.

## Review Envelope

This campaign follows the global Codex multi-agent lane contract. Under the
current direct user policy, every new or resumed Codex-owned worker uses
`gpt-5.6-sol` at medium effort by default; harder work may raise the supported
Sol effort. Terra/Luna fallback and lower effort require a newer direct user
instruction. The current broad audit covers repository DX, branch
archaeology, WinUI UX, patch/mod safety, binary RE quality, Lore quality,
rebuild provenance/architecture, and holistic normal/adversarial review.

The external Cursor/Grok lane is available through bounded, non-secret,
read-only external consults through the canonical command binding. The completed
filesystem slice received normal and adversarial Cursor/Grok review, focused
follow-ups on challenged assumptions, and separate Codex normal/adversarial
review. The WinUI slice received Codex normal/adversarial review whose two
concrete edge-case blockers were fixed with native regressions; independent
Cursor/Grok normal and adversarial closeout reviews then returned `ACCEPT` with
no commit blockers. First Flight received Codex and bounded Cursor/Grok normal
and adversarial review; the final Codex adversarial follow-up accepted the
suspended-root Job Object ownership model and explicitly heuristic visual-
evidence boundary. Codex root retained edit, validation, state, commit, push,
and final acceptance ownership.

The patch-contract slice received Codex and bounded Cursor/Grok normal and
adversarial review. Review challenges produced pinned-catalog membership,
known-transition attestation, transitive window-pair planning, sidecar-link
guards, case-consistent graph semantics, diagnostic-evidence separation, and
atomic damaged-copy recovery regressions. The accepted residual is no sandbox
claim against an already malicious process running as the same Windows user.

## Current Slice Acceptance

- Anonymous ignored OBJ candidates are produced only by the accepted profile-v0
  parser from the approved local corpus into a fresh guarded session.
- Tracked and external outputs contain no retail filenames, paths, hashes,
  payload bytes, screenshots, or inferred Aquila identity.
- A human selection, not a structural heuristic, chooses the Aquila candidate;
  the selector and role manifest remain ignored and local.
- Any native preview uses a serialized lease, a fresh build, bounded local
  inputs, and an exact zero-process cleanup census.
- The selected role loads through the existing presentation-only Godot bridge
  while deterministic Core remains unchanged and synthetic terrain remains the
  default. No texture, handling, gameplay, visual-fidelity, or parity claim is
  made.
- Focused parser/presentation, payload-boundary, and review gates pass; state is
  reconciled; and `main` is pushed with divergence `0 0`.

## Next Slices

1. Resolve and export the selected BattleEngine texture/material dependencies,
   then compose hierarchy and frame transforms without guessing retail slot or
   articulation semantics.
2. Expand deterministic extraction and private coverage to terrain, world,
   entity, mission/script, camera, audio, animation, and skeletal families.
3. Reconstruct walker, jet, morph, camera, weapons, player/controller, world,
   mission, and AI systems subsystem by subsystem from source, Steam deltas,
   and only the runtime measurements that remain necessary.
4. Make First Flight consume accepted deterministic Core behavior and extracted
   local assets; treat it as a client and integration verifier, never as retail
   evidence by self-agreement.
5. Let WinUI consume path-free extractor catalogs and safe local workflows after
   the underlying extraction contracts exist.
6. Retain the separately staffed sealed-spec clean-room option without
   mislabeling the active RE-informed GPL implementation.

## Stop Conditions

- Main or a target file changes incompatibly during a slice.
- Unique historical work cannot be preserved before cleanup.
- A change would add hard payloads or expose private paths or secrets.
- Runtime, Ghidra, release, or destructive work lacks its separate authority,
  lease, evidence, or rollback plan.
- A security or correctness gate fails and cannot be bounded or fixed.
