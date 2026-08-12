# Reverse-Engineering Index

Status: active — the RE evidence front door
Last updated: 2026-08-11
Summary: where RE evidence lives, what each store is authoritative for, and the
rules a claim about the shipped binary has to meet before it is written down.
Current replay authority is Generation 19 via
`developer_state.json` → `current_re_authority`; Generation 73 is a projection
oracle only, and the Generation-10 block below is historical.

This directory preserves evidence that materially supports the toolkit,
rebuild, modding work, or contributor understanding. Git history holds completed
waves, superseded plans, and generated accounting.

**Every authority figure under "Current static authority" below is dated
2026-07-27 and must be re-measured before it is used.** The residual, both
denominators, and each per-ledger count are readings taken against a live
maintainer database that has moved since. The section says so ledger by ledger;
it is said once here so that nobody quotes a number off this page without
re-running the grader that produced it.

## Evidence rules

- Static names, types, strings, and call relationships prove only the structures
  they directly demonstrate.
- Stuart Gillam's source and the AYA extractor are references, not proof of the
  Steam executable's implementation or complete format support.
- Controlled copied-runtime observations establish only the measured behavior
  and specimen described by their evidence.
- Deterministic rebuild agreement does not re-prove retail behavior or establish
  gameplay, visual, or rebuild parity.
- Retail executables, saves, debugger logs, and runtime frames remain untracked
  local inputs. Retail assets and conversions are locally materialized and
  ignored. The reviewed canonical Ghidra project and narrow save fixture are
  the explicit tracked payload exceptions.

## Start here

| Area | Canonical entry point |
| --- | --- |
| First-party development sources | [Development source index](DEVELOPMENT_SOURCE_INDEX.md) |
| Build/dump identity and equivalence | [Build and dump matrix](BUILD_AND_DUMP_MATRIX.md) |
| Cross-platform engine architecture | [GDC deck / binary synthesis](ENGINE_ARCHITECTURE.md) |
| PC demo versus retail | [Build and virtual-target comparison](DEMO_VS_RETAIL.md) |
| Cross-source synthesis | [Data/source/executable delta](delta.md) |
| Agentic parity and function discovery | [Parity lab](parity-lab.md) |
| Function and behavior contract system | [Contract front door](../CONTRACTS.md) |
| Installed data narrative | [Measured installation census](installed-corpus-census.md) |
| Executable/Ghidra narrative | [Ghidra function synthesis](ghidra-functions.md) |
| Complete executable string inventory | [Binary strings](binary-analysis/binary-strings.md) |
| Pinned-source narrative | [Stuart source synthesis](source-code/stuart-source-synthesis.md) |
| Save and options formats | [Save-file index](save-file/_index.md) |
| Retail binary analysis | [Binary-analysis index](binary-analysis/_index.md) |
| Canonical Ghidra project | [Distributable database](ghidra/README.md) |
| Pinned source references | [Source-code index](source-code/_index.md) |
| Measured mechanics | [Game-mechanics index](game-mechanics/_index.md) |
| Assets and mission data | [Game-assets index](game-assets/_index.md) |
| Compact lookups | [Quick-reference index](quick-reference/_index.md) |
| Attribution and known limits | [Project metadata](project-meta/_index.md) |

Further down this page, past the authority block: the patch recipes, the
per-subsystem static contracts, the 2026-05-26 review cohort, the lane
reference and runbooks, and the retail → Core translation policies.

## Current complete-RE replay authority — machine-local evidence (2026-08-09)

The tracked Ghidra snapshot was refreshed from live on 2026-08-09; the dated
2026-07 name ledgers still lag current work. Select campaign authority from `developer_state.json` →
`current_re_authority`: canonical Generation 19 at
`local-lab/re-campaign-incident-recovery-20260808-v1/generation-19-mission-native-unsetobjective-reproof-v1/`,
READY `f83dbb6eddaa16deed5f2a2460d393dc4525a63ae243b6cac0c656056b69ab9a`,
frozen reducer `151acbe5c1571dca2c53c68dd79281cf20c69af609523d54f25953643dcff3e2`,
external selector `72c22f02…2360`. It contains 8,126 functions, 217 C1,
seven bounded C2, 7,902 opaque functions, 17 open residuals, and no rebuild-ready
contract. Generation 12 admitted bounded `CBattleEngine::Damage`/`Hit` field
writes and a partial rebuild mapping; Generation 13 admitted one replicated
zero-shield `CUnit::ApplyDamage` entry/write contract and its exact overkill
parity vector; Generation 14 closes one exact residual as the adjacent
`CTokenArchive::ReadNextToken` dispatch-data partition without naming its seven
categories; Generation 15 closes another by proving the exact Mission-native
`IScript__SetPos` boundary and C1 static call shape. Generation 16 advances only
two replicated script-visible SetPos position-copy roundtrips to bounded C2 and
a partial rebuild mapping; its complete writes, side effects, broader inputs,
and failure behavior remain open. Generation 17 admits only LockHit's retained
non-null, sole-matching-node removal path; its other list paths, free-head,
destructor, return, identity, and rebuild questions remain open. Positive-shield absorption, raw return
pairing, death/effect ordering, and other paths remain open. Generation 18
admits an exact static `CTokenArchive::ReadNextToken` parser/corpus/factory
contract at C1 only: all 124 token names, 125 parse-index entries, 141 direct
writer-call encodings, and 13 descriptor factory/RTTI/loader mappings are
accounted for, while runtime/refuter verdicts, malformed input, allocation,
overflow, named token 32, and full downstream behavior remain open. Its focused
rebuild mapping is `PARTIAL_CONTRACT`. Generation 19 retires the 19-byte
Mission-native UnsetObjective residual as exact 3-byte NOP / 13-byte wrapper /
3-byte NOP children and admits only the wrapper's C1 static call/bit-clear
contract. Runtime, HUD/lifetime behavior, and opaque callee `0x004E5BD0`
remain open; its rebuild mapping is also `PARTIAL_CONTRACT`, and it made no live
Ghidra mutation. The independent replica is
reproduction-only. Generation 73 remains a projection oracle, never a parent or
authority. The next valid campaign generation is 20. Model review is
situational and harness-agnostic under `REVIEW-PROTOCOL.md`.

**Current static-envelope closure (2026-08-11):** the reviewed
[`function-c1-closure-2026-08-11.tsv`](binary-analysis/function-c1-closure-2026-08-11.tsv)
accounts for the current 8,136-function inventory at 8,129 bounded C1 and seven
bounded C2 functions, with zero static `OPAQUE` rows. It joins 53 disjoint
sealed receipts covering 7,945 functions, ten post-Gen19 Mission-native
boundaries, and 181 pre-existing C1/C2 rows. This is a distinct authority for
static-envelope accounting; Generation 19 remains the immutable replay owner
for its admitted runtime evidence and READY/reducer lineage. See the
[closure report](binary-analysis/function-c1-closure-2026-08-11.md) for exact
hashes and limits.

**Current PC demo/retail frontier (2026-08-11):** the conservative 8,086-entry
address map plus exact second-pass reports, caller propagation, equal-delta
body-union audit, and whole-demo fingerprint scan now account for 8,119
normalized-identical bodies and 13 bounded semantic divergences. The
[gapless CRT/FPU closure](binary-analysis/pc-demo-retail-gapless-closure-2026-08-11.md)
resolves the final nine mapped false negatives, corrects two stale FPU helper
plates, and recovers six more exact address pairs. The subsequent
[equal-delta closure](binary-analysis/pc-demo-retail-equal-delta-closure-2026-08-11.md)
accepts 29 further pairs only after complete corrected-body and encoded-operand
audits. The subsequent
[exact-fingerprint closure](binary-analysis/pc-demo-retail-exact-fingerprint-closure-2026-08-11.md)
maps 11 more entries through global exact-body, mapped-caller, unique-callee,
and ordered-block evidence with an independent replay. All 8,132 mapped entries
are accounted for; the tracked
[four-row address frontier](binary-analysis/pc-demo-retail-address-unmapped-frontier-after-exact-fingerprint-2026-08-11.tsv)
owns the remaining queue. See [`DEMO_VS_RETAIL.md`](DEMO_VS_RETAIL.md) for the
exact accounting and proof boundaries.

## Historical Gen10 dual-authority / TTD admission (2026-08-04)

Generation 10 remains a valid **historical frozen-integrity**
function/range/contract admission for Level 521 call-context evidence, not the
current replay authority:
`local-lab/ttd-call-context-level521-impact-generation10-20260804-v1/generation-10-ttd-call-context-observation-v2/`:
8,124 functions, 6,117 exact `.text` residuals, 15,241 open/closed questions,
72 scenarios, 915 levers, 14,241 contracts, 6 adjudications, and 584 exact
supersessions. Its READY SHA-256 is
`b349f0b2895849ba320b0b0b783c60a98794d01f375d57d9a04bbe4a5aebabb2`.
The exact post-promotion coverage snapshot is
`local-lab/console-callback-atomic14-post-campaign-20260803-v1/snapshot/ledger.ready.json`,
SHA-256 `efabd9c2ae7a0be5adee2bf478df0cbec69482918197ae87ed7d6a9fc3ac6b3f`.
Its intact ledgers can be checked with its frozen `_reducer` (ID
`7dfa4015aad676bfeb22977adf3aadcddac49ba31fa8203a63a32f76d941f5d9`);
the evolving working dependency bundle is not interchangeable. The deleted
historical Atomic14 formal READY prevents full replay of this original lineage;
the post-loss 8R→11 branch is the full-replay replacement without substituting
that lost identity.

Current local boundaries that materially change the discovery lane:

- `local-lab/logger-oracle-pilot-2026-08-02/logger-oracle.ready.json`, SHA-256
  `b4ae49e3344ec96b72248a657af8daa7627b79f865d6f6287a369daeeb14a1a6`,
  proves that, with a writable relative path in both arms, a one-byte
  copied-binary gate lets generated Mission `Print` bytecode export exact
  string/int/six-decimal float text and resume after `Pause`. Unmodified retail
  remains inert; the channel is external write-only and does not expose
  arbitrary private state.
  The frozen boundary also replays the generic refuter byte-identically: all
  16 rules pass, three preregistered predictions resolve, and two rival causes
  are eliminated across six arms and two independent replications.
- `local-lab/console-logger-bridge-20260803-v1/console-logger-bridge.ready.json`,
  SHA-256 `ec6755c4c9c23fcae07b112cb0f7f8d243420b7faaaaa5f675be225066618297`,
  freezes two A/B replications of a 16-byte disposable bridge from the four
  `ShowCmds`/`ShowVars` output sites to that logger. Level 100 realizes 31
  commands and 56 variables; static registration contains 32/59, with
  `fmv_play` and three debris variables absent on that path. This is authored
  instrumentation, not a retail-default logging path or a callback-semantics
  claim.
- `local-lab/vm-trace-pilot-2026-08-02/vm-trace.ready.json`, SHA-256
  `ad373947273ad083c9c37a53aba876e28399cba26821ae067df59d207e4ced09`,
  proves that stock Level 100 `Setup.trailerA = 1` enables deterministic
  post-instruction index/stack-size/flags lines. Two replicated triangles plus
  two exact-comparison value `2` controls distinguish the script field, logger gate,
  and ordinary diagnostics. Traced-run timing is invalid because output is
  synchronous per instruction.
  Its replayed generic refuter passes 16/16 rules with four resolved predictions,
  two eliminated rivals, and discriminating `n = 6` at two replications.
- `local-lab/crt-recursive-cohort-2026-08-02/architect/derivation.ready.json`,
  SHA-256 `59b64f11ce4e9d0a8f994c15a438c4a5f98e8dcb40626a55f1c451e843f2628b`,
  reproduces 547 hard missing CRT entries (537 instruction-present, 10 requiring
  disassembly) and quarantines two weak tail candidates. The later
  `clean520-boundary-v3-canary-refuted/boundary-targets.ready.json`, SHA-256
  `53ab9de5bc113ad45d593f3732627860f2639c819d21c771d8369d139a4c6832`,
  narrows that evidence to 520 exact one-residual bodies (58,157 bytes), preserves
  16 structural cases in quarantine, and excludes the refuted original canary.
  The later `local-lab/formal-global-init515-proof-20260803-v4/proof.ready.json`,
  SHA-256 `0fa28300606f55d96e9e4c4168501c39d8eee25823033042d89339ae58d40729`,
  formally partitions that cohort into 515 admissible targets and five listing
  repairs that remain quarantined. Two independent replicas produce the exact
  7,595 -> 8,110 boundary delta with no instruction or pre-existing-function
  change; a late poison fails and separate-process readback agrees. The separate
  live owner then completed the authorized promotion once:
  `local-lab/global-init515-live-promotion-20260803-v4/promotion/promotion.ready.json`,
  SHA-256 `57015dd561fed34cbc9c7b322a63d3774cf234aef3138436e68f297fd17929cf`.
  Exact PRE/POST identity, quiescence, verified backup, clone controls, one live
  apply, separate-process readback, byte-identical POST backup/restore drill, and
  generation-7 reseed all survived. This promotes boundaries only; it does not
  authorize names, signatures, semantic contracts, library classification,
  rebuild parity, or the five quarantined repairs.
- `local-lab/console-callback-atomic14-live-promotion-20260803-v2/promotion/promotion.ready.json`,
  SHA-256 `f3d58ccb74891a20bade971f043382ab77b3c32bebdef977fabcd76274752541`,
  records the later authorized 8,110 -> 8,124 boundary-only promotion. Its
  formal proof (`a504c24b…a83e6`), exact target/padding manifests, separate-process
  readback, POST backup/restore drill, and Generation-8 reducer agree that the
  old `[0x004295BC,0x00429BC0)` residual is exactly 14 functions / 1,433 bytes
  plus 15 NOP-padding ranges / 107 bytes. No semantic name, signature, ABI,
  behavior, thunk, or rebuild claim was promoted.
- `local-lab/ghidra-target-lock-semantic-live-promotion-20260804-v2/promotion/promotion.ready.json`,
  SHA-256 `77f635e552b7a2dd8425af012204f8172eadcb1de8ecdb02a30e2c12ff9b9945`,
  records the later backed-up, scratch-reproduced, separately read-back
  correction of five same-range rows: `StartLock @ 0x00406FC0`, `FireLock @
  0x00407060`, `LockHit @ 0x00407140`, `GetCurrentTarget @ 0x004071B0`, and
  `DisplayLock @ 0x00407310`. The live POST fileset is
  `f803cd83217df76ab7fc6c6928f44312b8fc6a2ba92affe21f5184afa2780702`.
  Generation 9 carries exactly those metadata/evidence-reference corrections;
  it changes no boundary/entity key, closes no question, advances no contract
  grade, creates no supersession, and proves no rebuild parity.
- `local-lab/binary-strings-20260803-v2/binary-strings.ready.json`, SHA-256
  `b088739efd9e514da05d3013f9ab55afa7f06837dc14ac67103f1c1f584d5dd9`,
  binds the pristine specimen to 9,059 Ghidra-defined string occurrences (8,541
  distinct values) and a separately graded raw printable scan. The joined local
  corpus contains 23,459 occurrences / 16,244 distinct values; raw-only rows may
  be instruction or packed-data noise. [`../binary-analysis/binary-strings.md`](binary-analysis/binary-strings.md)
  renders the complete Ghidra-defined inventory; xrefs narrow investigation but
  do not prove a dormant feature is live.
- `local-lab/source-unit-census-v1-ready/source-unit-census.ready.json`,
  SHA-256 `63099dbf88d031bcbc186303627f6692e157cc80a270670018a5ed68744ff2b4`,
  rederives 1,870 exact embedded `__FILE__` plates into 162 canonical paths:
  151 CPP translation units and 11 headers. Exact fragmented-body joins touch
  987 current functions and 20 residual entities; 368 functions have direct CPP
  anchors. Closed spans and neighbours remain order priors, headers never own a
  translation unit, and the owner-crossing call at `0x00437A3A` stays open.
  Replay with the frozen `source-unit-owner.py`; the tool assigns no names and
  authorizes no Ghidra promotion.
- The current TTD corpus contains 75 traces / 497.31 GiB. Replay executed-byte
  coverage exists for 73 traces, but 65 traces remain coverage-only and no
  normalized corpus-wide semantic ledger exists. Schema-v3 call-context replay
  clears pending/active associations across its conservative global barriers.
  The `verify-cwd-fix` calibration owns exact `1/1/2/0` calls, four paired
  entries, four raw return boundaries, three validated returns, one orphan, and
  three gap-free envelopes; raw register/stack carriers remain untyped. Tiny-cap
  and wrong-count controls fail closed, and an executed interior address remains
  `ENTRY_ONLY`. Existing v3 receipts are conservative evidence; a proposed
  per-thread ContextSwitch refinement requires a new schema and replay rather
  than retroactive reinterpretation.
- `local-lab/ttd-call-context-level521-impact-schema3-20260804-v1/` is the
  replicated existing-trace evidence admitted by Generation 10. Two runs
  have identical 17,804 path-neutral evidence bytes, SHA-256
  `3e12c0a391540ba79e50ee559bc04ccff344729fcbe0cec288731e12c5dc7558`.
  In the exact window, callsite `0x004268CB` dispatches slot 39 to un-named
  `0x004D8AE0`; that routine calls `Damage @ 0x0040A890` with raw
  `0.05f`/projectile/`1`/`-1` carriers; the collision resolver then calls `Hit @
  0x00407350` with the same projectile and collision-report carriers. Four raw
  returns yield one validated `Hit` return and three orphans. `StartDie` is only
  a bounded zero-call observation. No name for `0x004D8AE0`, typed return,
  memory write, or behavior outside the window is proved. Generation 10 closes
  three prior questions as `SURVIVED`, creates three changed successor
  questions, and advances only `0x004D8AE0`, `0x0040A890`, and `0x00407350` to
  `C2_BOUNDED_RUNTIME`. `StartDie` remains `OPEN / C0_OPAQUE`; no name, range,
  rebuild mapping, parity result, or supersession changed.
- **2026-08-10 successor join:** the historical Gen10 observation remains
  unchanged, but exact bytes, strict RTTI/vtables, source virtual order, the
  raw round-field map, and both runtime replicas now identify `0x004D8AE0` as
  [`CRound::Hit`](binary-analysis/cround-hit-damage-path-2026-08-10.md), with
  `void __thiscall (CRound*, CThing*, CCollisionReport*)` ABI and a bounded
  direct `CRoundDamage` dispatch. The early null-report branch is not a safe
  damage path because the report is dereferenced at `0x004D8CBC`. The same
  document recovers `CExplosion::Hit`/`Move`, the radial `CExplosionDamage`
  formula, and `CWorldPhysicsManager::CreateExplosion`; PC-demo twins preserve
  the instruction laws after relocation normalization. The exact mode-3 helper
  closes configured round-to-explosion creation. The inherited `CThing` init,
  `CCSPersistentThing` ready gate, 3x3 MapWho scan, pair dispatcher, and shared
  collision-response slot now close the synchronous small-explosion path back
  into `CExplosion::Hit`. For the surviving tutorial Target Drone this joins
  direct `0.8` and radial `1.0` as the measured conditional same-receiver `1.8`.
  The contrasting invocation's rejecting gate, exact second mesh part,
  expanding-radius timing, and rebuild parity remain open; live Ghidra
  promotion is separate.
- **2026-08-10 recursive caller correction:** the exact direct-xref census for
  `CWorldPhysicsManager::CreateExplosion` contains 24 calls: two in the
  recovered `CRound` switch and 22 bounded function callers. Joined
  configuration adapters identify `CUnitExplosion`, `CUnitSmallExplosion`, and
  `CUnitStompExplosion`; strict RTTI fixes the virtual owners and slots. This
  disproves the remaining pickup labels across unit death, small/stomp
  explosion, feature, rocket, and Gill-M activation paths. The corrected table
  and evidence boundary are in
  [`cexplosion-factory-callers-2026-08-10.md`](binary-analysis/cexplosion-factory-callers-2026-08-10.md).
- The separate exact-window data-write lane has a source-bound,
  independently-refuted first semantic plate. In one Level 521
  `CBattleEngine::LockHit @ 0x00407140` invocation, five ordered field
  transitions remove the supplied target's sole `mFiredLocks` node and leave
  the container empty. Three replays have identical 22 non-metadata rows,
  SHA-256 `AF8CD84F...FC57D`; the final READY is `92E74EC7...4615` and binds
  wrapper/collector sources, binary, runtime, target table, and outputs. Global
  free-list reattachment is a gap-free static/runtime path proof, not a direct
  global-head watch; payload destruction, full return, other paths, and parity
  remain open. Owner:
  `local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/README.md`.
- `local-lab/source-allocation-census-v1-ready/READY.json`, SHA-256
  `16c858e1ee7f0961ed0fce8d53bb69536e90b295db91bf6082b1fa8f3dea4635`,
  classifies all 1,870 source plates as 1,377 allocation and 493 unwind calls.
  It recovers 1,867 immediate type constants, one conservatively proved local
  constant, two dynamic definitions, 1,060 immediate allocation sizes, and 317
  register sizes. Of the sites, 1,845 are function-owned and 25 residual-owned;
  the `0x00437A2C` plate crosses into residual `0x00437A3A` and remains a range-
  repair lead. Eight logical-type-42 sites use the runtime fallback `Name not
  found`; requested byte counts are not C++ `sizeof` identities or proof that an
  allocation succeeded. The frozen owner authorizes no automatic name or
  boundary promotion.
- `local-lab/msl-logger-census-2026-08-03-v2-ready/READY.json`, SHA-256
  `ce9a0a7b29f70b346d020a7c7e01193eed1f229fd3dd883bf63262a8da5ab92d`,
  freezes the 733-file source corpus, 301 compiled resource archives, the 144-row
  native registry, and the 72-index coverage join. It finds 726 source `Print`
  calls, 783 compiled calls, 9,382 source native calls using 110 names, and 9,236
  compiled native calls using 108 names. The pristine binary has exactly 380
  direct calls to `CConsole__Printf`: 253 use the dormant-debug receiver and 127
  use setup history; Ghidra maps 377, leaving call sites `0x004F22FA`,
  `0x005351F0`, and `0x00536BA9` residual-owned. The older 329-call W* export
  subset is not the binary denominator. Census membership does not prove that a
  source site executes in a particular run.

These paths are ignored and absent from a fresh clone. They are routing pointers,
not substitutes for re-running their verifiers.

## Current static authority

### The name-grading residual — current figure, and the flag it requires

**`1,867` of a human-namable `6,376` = 29.3 %**, as of 2026-07-27.

**This figure is meaningless without its precondition.** It is only valid when
the grader is run with `--reference-source references/Onslaught`. **Without that
flag the same inventory grades to `2,089`** — a difference of 222. A residual
quoted bare is ambiguous and must not be relied on; state the flag every time.

The denominator moved and the residual did not. Three Ghidra mutation waves and
the naming wave, all applied to the live maintainer DB on 2026-07-27, took the
graded function count `6,969 → 7,555` and the human-namable denominator
`5,790 → 6,376`, because the Instruction Finder created real functions. The
residual stayed at `1,867` throughout — these waves extend *coverage*; they
recover no developer-authored name. So the ratio improved from
`1,867 / 5,790 = 32.2 %` to `1,867 / 6,376 = 29.3 %` **without a single name
being recovered**, which is exactly the trap this metric sets.

*(Added 2026-07-27. The per-ledger figures below are dated snapshots against the
**6,969**-function inventory and are quoted as those ledgers state them; they
are not the current figure. The tracked `ghidra/` snapshot was promoted to the
8,136-function live state on 2026-08-09; the 7,555-row name projection remains a
dated table. Historical live/snapshot distinction and mutation-wave reconciliation
are tracked in [`ghidra-functions.md`](ghidra-functions.md); bulky working
exports remain ignored under `local-lab/`.)*

### Specimen, coverage, and symbol ground truth

**Name the specimen and its hash on every byte finding.** There are two retail
binaries on this project and they are not interchangeable — the installed Steam
executable carries local patches. The rule and the three authoritative hashes:

- [Retail specimen baseline — which binary, which hash, and why it matters](binary-analysis/retail-specimen-baseline.md)

*(Indexed 2026-07-27. These four entries were previously reachable from no
tracked document, or — for the specimen baseline — only from
`binary-analysis/_index.md`. The repo-wide link check passes on all of them
because it validates link **targets**, not document **reachability**; the two are
different failure modes and only the first was being tested.)*

- [RE coverage baseline — what the 6,411-function pass actually covers](binary-analysis/re-coverage-baseline-2026-07-25.md)
  — 2026-07-25. The functions that exist are sound; the **set** of functions is
  incomplete. 468,804 exported instructions verified against the pristine binary
  with **0 byte mismatches**, 6,351 of 6,411 functions fully clean — but only
  **79.8268 % of `.text` was covered by those 6,411 historical bodies**.
  Coverage of the current 7,555-row inventory is **UNKNOWN** until a fresh
  interval export is measured. Reproducible for the historical population in
  under a minute with `tools/re_verify.py`.
- [RTTI and source-path evidence — a documented ground truth was wrong](binary-analysis/rtti-and-source-path-evidence-2026-07-25.md)
  — 2026-07-25. **Read this before repeating "the binary has no symbols."**
  Direct ASCII scan of the pristine specimen finds **667 RTTI type descriptors**
  and **166 source-file path strings** (`C:\dev\ONSLAUGHT2\*.cpp`/`.h`). The PE
  debug directory *is* stripped and there is no `.pdb` — that half of the old
  claim holds — but "no symbols, nothing was missed" was an over-generalisation
  from it. The RTTI owners and `__FILE__` translation-unit names that the 2026-07
  naming waves are built on come from exactly this material.
- [Retail capture provenance — what the reference screenshots actually show](binary-analysis/retail-capture-provenance-2026-07-25.md)
  — 2026-07-25. The frontend/HUD reference captures were taken from a **safe copy
  of the installed `BEA.exe`, not from pristine retail**. Anything that binary
  draws differently from pristine is a false parity target that will be
  faithfully reproduced as a defect — and at least one already was. Static byte
  comparison of both binaries plus direct pixel measurement; no decompiler
  output involved.

### Ghidra name grading and the fullpass expedition

- [2026-07 fullpass expedition handoff](binary-analysis/ghidra-fullpass-expedition-handoff-2026-07-25.md)
  — **historic; the branch it reports on no longer exists.**
  `ghidra/fullpass-quality-2026-07-23` was **merged into `main` at `af22af95`**
  on 2026-07-25 and the branch ref was deleted on 2026-07-27. Its history is in
  `main`. The document still carries standing instructions for a live branch
  ("Do not merge to main unless the user asks", a worktree path that no longer
  exists); read it as a record of that expedition, not as a live work item.
  *(Corrected 2026-07-27: this entry was labelled "(branch status)" and led the
  list as current authority.)*
- [Name-grading ledger — every name graded by its evidence](binary-analysis/name-grading-ledger-2026-07-26.md)
  — 2026-07-26 revision. Corrects `SOURCE_BACKED` (1,009 → **528**; the old figure
  matched elaborated type specifiers, and `CDXTexture` alone backed 368 rows with
  no definition anywhere), partitions `UNBACKED` into seven measured cohorts of
  which **1,179 are MSVC unwind funclets that can never carry a developer name**,
  and records the 13 renames applied to the live database. Honest residual **as
  that ledger states it**: 1,866 of a human-namable 5,790 (the ledger's own
  §"honest residual"; a demotion inside the same wave took it from 1,865 to
  1,866). **Snapshot, not current** — see the current figure above:
  **1,867 of 6,376**, with `--reference-source references/Onslaught`.
- [The second demotion — `0x005386d0`, and the residual goes up again](binary-analysis/name-grading-ledger-2026-07-27-demotion2.md)
  — 2026-07-27. Amends the 07-26 ledger **in two cells only**: the false name
  `CScriptEventNB__Destructor` on `CPostEventData`'s destroy path is withdrawn to
  `DestructorBody_005386d0`, taking the honest residual to **1,867** — of 5,790
  as that document states it, **of 6,376 today**; the residual itself has not
  moved since. Also restates the limit that keeps getting dropped: the sweep behind these
  demotions sees **only the destructor channel**, so its six findings are a
  **floor, not a bound**.
- **Aggressive Ghidra analysis does not reduce that residual — measured, not
  assumed.** Six isolated analyser passes on a disposable canary (Aggressive
  Instruction Finder, Decompiler Parameter ID, address/switch-table aggression,
  external-parameter propagation, variadic override, and a combined pass) left
  the residual **unmoved: 1,866 before and 1,866 after**, that pair being the
  experiment's own canary measurement against its then-baseline of 1,866, before
  the `0x005386d0` demotion above. **The current residual is 1,867 of 6,376**;
  the "does not reduce" verdict is what carries forward, not the baseline.
  The Instruction Finder
  recovered ~4,404 bytes of real application code but those land in `UNNAMED`,
  enlarging the namable denominator without moving the residual; external-
  parameter propagation moved it *up*, to 1,867, by correctly naming one
  function. Seven of the nine analysers the exercise set out to enable were
  **already on**. Do not re-run this as an untried lever. Evidence and
  per-pass verdicts: `local-lab/GHIDRA-AGGRESSIVE-ANALYSIS-2026-07-27.md`
  (untracked); tooling is `tools/ListAnalysisOptions.java`,
  `tools/RunIsolatedAnalyzer.java`, `tools/ExportFullFunctionInventory.java`,
  `tools/ExportLooseInstructions.java`, and `tools/ghidra_inventory_diff.py`.
  The [2026-07-25 revision](binary-analysis/name-grading-ledger-2026-07-25.md) is
  **superseded in its counts** and retained as the record of the RTTI re-prefix
  wave and the 0x08-byte incident.
- [PhysicsScript round and weapon-mode value ids — resolved](binary-analysis/physics-round-value-ids-2026-07-25.md)
- [Direct3D fog render states — `D3DFOG_EXP` slot, parameters, and far plane](binary-analysis/d3d-fog-render-state-static-contract-2026-07-25.md)
- [Player camera attach, projection FOV, and mesh `HFOV`](binary-analysis/player-camera-attach-and-mesh-hfov-2026-07-26.md)
- [Terrain shade plane — origin, ownership, and axis order](binary-analysis/terrain-shade-plane-origin-2026-07-26.md)
- [Terrain shade interpolation — the exact 8.8 fixed-point stepping, decoded from bytes](binary-analysis/terrain-shade-bilinear-decode-2026-07-26.md)
- [Terrain draw — texture-stage flags, and the falsification of both settings](binary-analysis/terrain-draw-stage-flags-2026-07-26.md)
- [Terrain gain — frame-global falsified, and the root-map oracle is circular](binary-analysis/terrain-gain-frame-global-falsified-2026-07-26.md)
- [Terrain per-node colour light — dead builder, and a null array in all 67 shipped heightfields](binary-analysis/terrain-per-node-colour-absent-2026-07-26.md)
- [Retail's implied macro cache, inverted from its own pixels — it exceeds the compositor's ceiling](binary-analysis/terrain-implied-macro-inversion-2026-07-26.md)
- [The sun colour and the terrain draw — all ten references, and a precise negative](binary-analysis/terrain-sun-colour-route-2026-07-26.md)
- [The terrain material record and the `LANDSCAPE_LIGHTING` gate — both loose ends are live](binary-analysis/terrain-ambient-light-material-2026-07-26.md)
- [The terrain ambient-light term, implemented and measured](binary-analysis/terrain-ambient-light-applied-2026-07-26.md)
- [The terrain third light — falsified; `SetupLights` dominates every terrain draw, and the three-light rig is a front-end page](binary-analysis/terrain-third-light-2026-07-26.md)
- [No missing high-frequency terrain term — the spectra match, and the frame is half a pixel out](binary-analysis/terrain-spatial-dispersion-negative-2026-07-26.md)
- [The default render-state block `0x004EB1E0` — re-derived from bytes; the API is D3D9, `COLORVERTEX` is `0x8D` not `60`, and the function has 7 callers not 547](binary-analysis/d3d-default-render-state-block-2026-07-27.md)
  — 2026-07-27. Promotes the static block that several committed rendering
  decisions rested on while living only in agent reports. Bounded to
  `[0x004EB1E0, 0x004EB99D)`. Corrects the "Direct3D 8" attribution, the 547
  figure (`440 + 50 + 57`, where the 57 are `SetTexture`; the render-state total
  is **490**), and the `COLORVERTEX` state id. Records which of the decisions
  have a runtime capture behind them — only *lighting-on* does.
- [The cockpit lighting law — decoded, and already what the reconstruction computes](binary-analysis/cockpit-lighting-law-2026-07-26.md)
- [The cockpit world matrix — the third upload site, traced by hand and confirmed at runtime](binary-analysis/cockpit-world-matrix-static-2026-07-26.md)
- [Controlled copied-runtime observations — four questions static reading could not settle](binary-analysis/controlled-runtime-observations-2026-07-26.md)
- [The terrain chain's temporal drift — the cloud scroll identified; its RATE partially superseded, origin since fixed and confirmed](binary-analysis/terrain-chain-temporal-drift-2026-07-26.md)
- [The half-pixel pixel-centre offset, corrected in the projection and measured](binary-analysis/pixel-centre-projection-offset-applied-2026-07-26.md)
- [View distance, cull, and LOD constants](binary-analysis/view-distance-and-lod-constants-2026-07-25.md)


- [2026-07-13 full Ghidra re-audit closeout](binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md)
- [Per-address reviewed correction plan](binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json)
- [2026-07 fullpass discovery findings](binary-analysis/ghidra-fullpass-findings/) (waves W001–W018)
- [Battle Engine movement crosswalk](binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md)
- [Battle Engine morph observer design](binary-analysis/battleengine-morph-runtime-observer-design-2026-07-12.md)
- [Pinned reference-submodule audit](source-code/reference-submodule-audit-2026-07-12.md)

The `6,411/6,411` closeout is a metadata/export accounting result, not a claim
that every function is semantically correct. Fullpass wave notes are discovery
evidence only; they do not claim complete semantic correctness of the database.
Current per-function notes live under
[`binary-analysis/functions/`](binary-analysis/functions/_index.md).

### 2026-07 fullpass correction expedition (authority map)

| Layer | Location | Role |
| --- | --- | --- |
| Discovery findings | [`binary-analysis/ghidra-fullpass-findings/`](binary-analysis/ghidra-fullpass-findings/) | Tracked wave reviews (W001–W018) |
| Correction ops | `local-lab/ghidra-fullpass-2026-07-23/` (gitignored) | Queues, dual QC, apply logs; closeout 2026-07-25 |
| Live applied DB | Maintainer Ghidra Projects (machine-local) | Working database that may receive dual-cleared applies |
| Tracked snapshot | [`ghidra/`](ghidra/README.md) (snapshot date 2026-08-09) | Distributable reviewed snapshot; exact to the verified live state at promotion time |

Host install paths, headless entry, and local project layout:
[`ghidra/README.md`](ghidra/README.md). Expedition overlays stay under ignored
`local-lab/`; do not treat discovery notes as proof that the tracked snapshot
or live DB was mutated.

## Patch recipes — analysis documents, not write authorization

These are analysis documents. They record where a byte lives, which function
owns it, what the clean bytes are, and what was observed when an **app-owned copied**
executable carried the change. Those observations authorize only their measured
copied targets. Applying a proved recipe to an installed target is a separate
user choice behind the owning verified-backup precondition; the original
`BEA.exe.original.backup` is never a target. Documenting patch knowledge is not
write authorization, and hiding these notes would not make a game safer—only the
evidence harder to find.

The normative authority for the byte definitions and for the copied-target
boundary is the [patch catalog contract](../patches/CATALOG_CONTRACT.md), with
[`patches/README.md`](../patches/README.md). The notes below explain why the
rows exist and what was actually observed; where a note and the catalog
disagree, the catalog wins.

**Two documents in this family carry a withdrawn claim.** The 2026-07-28
guard-byte correction struck a hex-edit recipe out of both
`windowed-mode-analysis.md` and `widescreen-patch-analysis.md`. Both keep the
withdrawn text visible and struck through rather than deleting it. Read the
correction before acting on either.

### The widescreen family — one external patch, fully accounted

| Document | What it settles |
| --- | --- |
| [Widescreen patch analysis](binary-analysis/widescreen-patch-analysis.md) | The `BEA_Widescreen.exe` diff: **191 changed bytes across 28 regions**, file length unchanged, code-cave-plus-trampoline technique, both SHA-256s recorded. Historical **external** patch analysis — explicitly *not* the current WinUI/AppCore catalog patch contract. Its guard-byte normalization section is **withdrawn (2026-07-28)**. |
| [28-region diff table](binary-analysis/widescreen-diff-regions-28.tsv) | The machine-readable canon: file offsets, VAs, before/after bytes, `owner_fn`, `evidence_refs`, behavior classification. A `.tsv`, not prose — read it when the exact region is what you need. |
| [Unresolved-region tracker](binary-analysis/widescreen-diff-unresolved.md) | The queue, and it is **empty**: 14 `known-functional`, 14 `known-supporting`, **0 `unknown-needs-RE`**. The part worth reading is the three reopen criteria — this is a closed queue, not a solved subject. |
| [Regions 8–11 validation](binary-analysis/widescreen-regions-8-11-validation.md) | How the last four uncertain regions were closed: hook sites and cave payloads disassembled from both binaries. |

### Per-feature patch notes

| Document | Anchor, and how far the claim reaches |
| --- | --- |
| [Windowed mode](binary-analysis/windowed-mode-analysis.md) | **Partially superseded 2026-07-28, and the withdrawn half is the half people used.** `-forcewindowed` is real and reachable, but its parser gate `DAT_00662f3e` is **BSS — zero at load** and is set only by `-testeur` appearing *earlier on the same command line*. The old "normalize the guard byte in a hex editor" recipe was false: there is no file byte to edit. The two-gate model and the startup-flow patch at file offset `0x12A644` stand. |
| [Extra-graphics feature gate](binary-analysis/extra-graphics-feature-gate-patch.md) | `GEFORCE_FX_POWER` registers with default `0`; `0x004CDD40`, `6A 00` → `6A 01`. Carries the companion row that ignores `cardid.txt` vendor/device matching. |
| [Version overlay](binary-analysis/version-overlay-patch.md) | The opt-in `V1.00 - PATCHED` marker as a **pair**: a visible pointer row plus a hidden cave-string payload row. One bounded copied-game title/menu run confirmed the marker; no broader overlay or parity claim. |
| [Frontend clear-screen colour](binary-analysis/frontend-clear-screen-color-patch.md) | Three mutually exclusive immediates at `0x00540F88` in `CDXFrontEnd__RenderStart`; source anchor `references/Onslaught/DXFrontend.cpp`. |
| [Goodies gallery display unlock](binary-analysis/goodies-gallery-display-unlock-patch.md) | Forces the existing display flag inside `CFEPGoodies__Process` (`0x0045D7F4`). **Display only — it does not alter save progression.** Also records the earlier candidate rejected for omitting the stack repair, before any behavior claim was made. |
| [Free-camera Aurore-gate bypass](binary-analysis/free-camera-aurore-gate-bypass-patch.md) | NOPs the `IsCheatActive(4)` gate on `BUTTON_TOGGLE_FREE_CAMERA` in `CGame__ReceiveButtonAction`, plus eight mutually exclusive keyboard cave variants. **Experimental**: establishes the gate effect in one controlled comparison, not general camera safety. |
| [Pause-key default row](binary-analysis/pause-key-default-row-patch.md) | One immediate in `OptionsEntries__InitDefaultSingleBindingsTable` (`0x005144CD`, `01` → `18`). **Experimental**, one bounded pause/resume observation. |

## Static contracts — per subsystem

Bounded static maps, one subsystem each. They establish addresses, call
relationships, constants, and structures visible in the analyzed specimen, and
nothing about runtime behavior, exact object layouts, source-body identity,
patch safety, or rebuild parity.
[`binary-analysis/mapped-systems.md`](binary-analysis/mapped-systems.md) is the
routing table naming the **current** owner per system; the list below is the
flat inventory.

| Subsystem | Contract |
| --- | --- |
| MissionScript / IScript | [missionscript-iscript-static-contract.md](binary-analysis/missionscript-iscript-static-contract.md) |
| PhysicsScript | [physics-script-static-contract.md](binary-analysis/physics-script-static-contract.md), with the [copied-corpus parser proof](binary-analysis/physics-script-copied-corpus-parser-proof.md) |
| Meshes and resources | [mesh-resource-render-static-contract.md](binary-analysis/mesh-resource-render-static-contract.md) |
| Render/resource bridge | [render-resource-bridge-static-contract.md](binary-analysis/render-resource-bridge-static-contract.md) |
| Texture decode | [texture-resource-decode-static-contract.md](binary-analysis/texture-resource-decode-static-contract.md) |
| HUD and frontend overlay | [hud-frontend-overlay-static-contract.md](binary-analysis/hud-frontend-overlay-static-contract.md) |
| Destroyable segments | [destroyable-segments-static-contract.md](binary-analysis/destroyable-segments-static-contract.md) |
| Units, movement, weapons | [unit-battleengine-gameplay-static-contract.md](binary-analysis/unit-battleengine-gameplay-static-contract.md) |
| Local multiplayer | [local-multiplayer-static-runtime-contract.md](binary-analysis/local-multiplayer-static-runtime-contract.md) |
| Career progression bridge | [career-progression-static-bridge-contract.md](binary-analysis/career-progression-static-bridge-contract.md) |
| CMSH `CPOS`/`CORI` identity | [cmsh-cpos-cori-identity-2026-07-25.md](binary-analysis/cmsh-cpos-cori-identity-2026-07-25.md) |

Machine-readable siblings, for consumers that should not be parsing prose:

- [MissionScript VM datatype/opcode schema](binary-analysis/missionscript-vm-datatype-opcode-schema.v1.json)
- [First-flight camera/movement/morph contract](binary-analysis/first-flight-camera-movement-morph-contract-candidate.v1.json)
  — a **candidate**, as its own filename says; not an accepted contract.
- [Retail specimen manifest](binary-analysis/retail-specimen-manifest-2026-03-14.json)
- [2026-07-27 function name table](binary-analysis/ghidra-function-name-table-2026-07-27.tsv)
  — the newer address-to-name authority.

The MissionScript **command-descriptor** schema that used to sit beside these
was deleted in `981c3379`; the 144-entry native registry it duplicated now lives
in [`ghidra-functions.md`](ghidra-functions.md). Most of the contracts above
have no `.json` sibling at all. Do not go looking for one.

## The 2026-05-26 static-review cohort — the oldest layer here

Six system slices from the May 2026 wave era, all dated `2026-05-26`. **This is
the oldest cohort in the store and the one most likely to mislead.** Read them
for subsystem shape, not for numbers: their prose carries live-database
accounting (`6113/6113`, `6411/6411`, wave and candidate counts) that was a
reading of the maintainer's database at the time. For what a function count can
mean today, use the
[RE coverage baseline](binary-analysis/re-coverage-baseline-2026-07-25.md); for
anything at function granularity,
[`binary-analysis/functions/`](binary-analysis/functions/_index.md) supersedes
these slices wherever a note exists.

The standing column below is read off `mapped-systems.md`'s owner table, not
asserted here — where that table still names the 05-26 document, so does this one.

| Slice | Standing |
| --- | --- |
| [Save and options](binary-analysis/save-options-static-review-2026-05-26.md) | **Still current.** The cited owner for options and control bindings, and the contract behind the save/options persistence chains. |
| [Audio, media, cutscene](binary-analysis/audio-media-cutscene-static-review-2026-05-26.md) | **Still the cited owner** for audio, media, cutscenes, and camera. The wave counts inside it are snapshots. |
| [Frontend, input, game loop](binary-analysis/frontend-input-game-loop-static-review-2026-05-26.md) | Superseded for frontend/HUD by [hud-frontend-overlay-static-contract.md](binary-analysis/hud-frontend-overlay-static-contract.md). Its companion proof-plan file no longer exists in the tree; the 2026-07-28 correction inside it gives the `git show` needed to recover it. |
| [Unit / BattleEngine gameplay](binary-analysis/unit-battleengine-gameplay-static-review-2026-05-26.md) | Superseded by [unit-battleengine-gameplay-static-contract.md](binary-analysis/unit-battleengine-gameplay-static-contract.md) (2026-07-16). |
| [Mesh, motion, world, particle](binary-analysis/mesh-motion-world-particle-static-review-2026-05-26.md) | Superseded for meshes and resources by [mesh-resource-render-static-contract.md](binary-analysis/mesh-resource-render-static-contract.md) and [render-resource-bridge-static-contract.md](binary-analysis/render-resource-bridge-static-contract.md). |
| [Texture and render](binary-analysis/texture-render-static-review-2026-05-26.md) | Superseded for decode by [texture-resource-decode-static-contract.md](binary-analysis/texture-resource-decode-static-contract.md), and for render state by the 2026-07 terrain and D3D notes above. |

## Operating the lane — reference, routing, and runbooks

| Document | Use it for |
| --- | --- |
| [Ghidra workflow reference](binary-analysis/GHIDRA-REFERENCE.md) | The active workflow for the Steam `BEA.exe` database: record specimen and database identity, export the smallest slice that answers the question, keep observed bytes separate from inferred names. The reviewed snapshot under `ghidra/` and narrow metadata projections are the tracked exceptions; the maintainer's loaded database is not. |
| [Mapped systems](binary-analysis/mapped-systems.md) | The routing table from a system to its current smallest evidence owner *and* to the code that consumes it. Start here when you know the subsystem but not the document. Not a function-completion ledger. |
| [High-impact call chains](binary-analysis/high-impact-call-chain-appendix.md) | Static chains with the product consequence spelled out — that loading a retail save can rewrite the boot-time options snapshot, that resume/exit can persist both career and `defaultoptions.bea`. This is the appendix explaining *why* AppCore patches real baselines and preserves unknown bytes instead of synthesizing saves. |
| [Executable analysis](binary-analysis/executable-analysis.md) | PE identity, hashes, size, DLL imports, the D3D9 confirmation, and the Lost Toys/Encore branding note. Its function-count row now carries the whole moving chain — 5,771 → 6,411 → **6,969** — and says plainly that this is a recovery count, not a property of the binary. |
| [WinDbg/CDB runbook](binary-analysis/windbg-cdb-runbook.md) | The only sanctioned debugger workflow: a copied `BEA.exe` from an app-owned profile, specimen hashes confirmed first, attach by exact PID and identity, command files deliberately untracked. Never the installed directory. |

## Retail → Core translation policies

[`game-mechanics/_index.md`](game-mechanics/_index.md) lists the measurements.
It does not list the **policies** that convert a measured retail quantity into a
deterministic-Core constant — and those are the documents a Core edit is
supposed to cite.

**Four of the seven were superseded on 2026-07-28, and the supersession is
partial in a way that is easy to misread.** In each case the *retail
measurement* stands and the *Core mapping* does not: the authority for the Core
value moved from copied-runtime measurement pairs to the shipped
`data/battle engine configurations.dat` bytes, and flat scalars became
two-ended envelopes. Citing one of these for its measurement is fine; citing it
to authorise a Core constant is not.

| Policy | Status, as the document itself now states it |
| --- | --- |
| [Jet forward scalar](game-mechanics/jet-forward-retail-to-core-translation-policy.md) | Accepted (2026-07-14) **for the retail measurement**; **superseded 2026-07-28 for the Core mapping.** `JetSpeedPerTick` no longer exists; Core carries a min/max envelope read from shipped data. |
| [Jet energy drain](game-mechanics/jet-energy-drain-retail-to-core-translation-policy.md) | Accepted (2026-07-14) **for the retail measurement**; **superseded 2026-07-28 for the Core mapping.** The flat scalar became a thruster-interpolated pair. |
| [Energy drain/regen](game-mechanics/energy-retail-to-core-translation-policy.md) | **Superseded 2026-07-28 for both halves.** The `energy-p02` measurement stands; walker regen is no longer provisional — and the old "provisional" label had become actively misleading. |
| [Projectile speed](game-mechanics/projectile-speed-retail-to-core-translation-policy.md) | **Draft — but a Core constant shipped anyway; superseded in part 2026-07-28.** Whether the measurement clears the dual-accept bar is recorded as an explicit `UNKNOWN` maintainer decision. |
| [Walker ↔ jet transform/morph](game-mechanics/walker-transform-morph-retail-to-core-translation-policy.md) | **Accepted bounded mapping.** Unchanged. |
| [Shield](game-mechanics/shield-retail-to-core-translation-policy.md) | **Ownership source-backed; the rate remains blocked.** Unchanged. |
| [Fire cooldown](game-mechanics/fire-cooldown-retail-to-core-translation-policy.md) | **Draft — blocked on a dual-accept that has not landed.** Authorization for nothing. |

Three of the seven have a machine-readable measurement behind them. The other
four do not, and the policy `.md` is the whole record — there is no
`*-translation-policy.json`:

- [jet-forward-scalar-response-v1](game-mechanics/jet-forward-scalar-response-v1.md)
  / [`.json`](game-mechanics/jet-forward-scalar-response-v1.json)
- [jet-energy-drain-scalar-response-v1](game-mechanics/jet-energy-drain-scalar-response-v1.md)
  / [`.json`](game-mechanics/jet-energy-drain-scalar-response-v1.json)
- [walker-transform-morph-timing-v1](game-mechanics/walker-transform-morph-timing-v1.md)
  / [`.json`](game-mechanics/walker-transform-morph-timing-v1.json)

## Product-facing summaries

- [Save/options boundary](public-save-options.md)
- [Assets and modding boundary](public-assets-and-modding.md)
- [Static contracts](public-static-contracts.md)

Reusable read-only Ghidra exporters, guarded asset tools, parsers, and copied-
runtime helpers live under [`tools/`](../tools/README.md). Applying a proved patch
to an installed target is a separate, explicit user choice behind a verified
pre-write backup. The pristine `74154bfa…` specimen is never writable.
