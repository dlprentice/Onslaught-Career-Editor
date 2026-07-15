# Validation Profiles And Current Audit

Status: active contributor guidance
Last updated: 2026-07-12

Validation is selected by the contract a change can affect. The repository keeps
historical proof checkers reproducible, but their presence does not make them
ordinary contributor gates.

## Current Evidence

`py -3 tools\validation_inventory.py --json` emits the machine-readable
package-script inventory as pure JSON; `npm --silent run
report:validation-inventory` is the package shortcut. It derives npm
dependencies, callers, exact duplicate
commands, active and historical doc references, source-string references,
checker self-binding, families, and profile reachability from current tracked
source. `npm run test:validation-inventory` validates its parser and the current
profile contracts.

After this simplification wave the inventory reports 1,512 scripts, 125 npm-run
edges, and two exact duplicate-command groups. It classifies 1,087 Ghidra/wave
commands as historical proof and 98 copied-runtime/original-binary commands as
runtime proof. Those commands remain invocable; they are not in the 12-command
transitive quick profile.

Commands in this matrix target the canonical public-primary source repo. A
materialized curated candidate has an intentionally smaller replacement
`package.json`; use its `npm test` and the commands it retains from
[Public Sign-Off Commands](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md).

The read-only starting measurement was 781.3 seconds:

| Gate | Seconds |
| --- | ---: |
| docs sync | 1.921 |
| documented commands | 26.264 |
| generated-output safety | 14.385 |
| WinUI build | 66.894 |
| AppCore tests | 57.685 |
| WinUI tests | 83.036 |
| deterministic rebuild | 43.316 |
| hard-payload safety | 236.622 |
| repository hygiene | 245.481 |
| Markdown links | 3.633 |

The separately measured WinUI build/AppCore/UI sequence totaled 207.6 seconds.
The revised `test:winui-primary-lane` built the complete solution once, ran the
two test projects from that same build, shut down build servers, and passed in
158.1 seconds: 49.5 seconds (24%) less in this worktree.

## Change-Class Matrix

| Change class | Normal gate | Add when affected | Protected contract |
| --- | --- | --- | --- |
| Minor docs/state | `npm run test:doc-commands`, `npm run test:md-links:public-core` | `npm run test:docsync` for canonical/mirror inputs; `npm run test:doc-commands-all` and `npm run test:md-links` for broad historical/tree changes | current command truth, navigable front doors, mirror integrity |
| AppCore/WinUI | focused project test while editing; `npm run test:winui-primary-lane` before handoff | `npm run test:winui-safe-copy-preflight` for copied-profile setup; `npm run test:winui-patch-engine-safety` for patch/catalog/mutation paths | data/API behavior, accessibility, primary UI, copied-target and patch safety |
| Runtime tooling | changed helper's self-tests and `npm run test:runtime-tooling-safety` | the owning runtime-proof checker only when its evidence/schema changes | app-owned profile prep, exact PID/executable/working-directory identity, input receipt/HWND binding, finally-based key release, bounded CDB commands, cleanup |
| Rebuild | `npm run test:rebuild` | `npm run test:rebuild-godot-smoke` only for engine setup, rendering, native input, launch, or clean-exit changes | deterministic Core/client, frozen trace/final-state contracts, owned-process cleanup |
| Payload/provenance | focused scanner self-test while editing | `npm run test:public-allowlist` for repo shape, submodules, fixture/hash, ignore, export, or boundary changes | hard-payload and secret exclusion, exact exceptions, submodule and migration provenance |
| Release/publication | affected build/accounting gate | the complete commands in [Public Sign-Off Commands](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md), including ZIP candidate proof before publication | notices, package contents/layout, extracted smoke, release accounting |
| Historical proof/checker | the specific checker whose evidence changed | `npm run test:doc-commands-all` if command history changed | reproducibility and bounded historical claims, not current product acceptance |

Home newcomer hierarchy, arrival-focus, or compact-layout changes use
`npm run test:winui-home-native-visual-focus` after focused non-native tests.
That opt-in gate rebuilds the repository WinUI executable, binds the exact
process/start/hash/product assembly/HWND, cross-checks UIA and app-side focus,
checks unchanged input epochs immediately around each capture, and validates
normal plus 760px HWND captures before one-rename publication of an ignored
local manifest. Its wrapper additionally requires an exact 1/1 passed TRX, one
fresh schema-3 manifest with full identity mappings and hashes, and a zero
relevant-process census. Debug/win-x64 is explicit, and an invocation token plus
post-build hashes prevent stale-build acceptance or cleanup of another run's
evidence. It is native Toolkit evidence, not BEA runtime or release evidence.

Save Editor first-use, Game Options workflow, or their compact-layout changes
use `npm run test:winui-save-lab-native-workflow` after focused non-native
tests. This opt-in gate owns two isolated launches, copies the immutable tracked
save fixture, constructs the fixed synthetic options buffer, and uses UIA
patterns without OS input synthesis. Acceptance requires an exact 1/1 TRX,
eight normal/760 receipt-bound captures, two unchanged-input/validated-output
workflow receipts, one fresh schema-1 manifest, full repo-build identity and
hash reconciliation, and zero relevant processes. All `.bes`, `.bea`, app
data, PNG, TRX, and manifest artifacts remain ignored/local. The gate does not
open Explorer or a browser and does not establish retail behavior or format
completeness.

`npm test` is a common active-product check, not public release signoff. It runs
inventory/profile contracts, active docs and public-core links, generated-output
safety, the primary WinUI lane, and deterministic rebuild tests. Whole-tree
payload/hygiene scans, native Godot smoke, copied-runtime proof sweeps, Ghidra,
installer probes, and ZIP publication remain separately triggered.

Receipt-bound walker scalar/resource measurement changes use
`npm run test:battleengine-walker-measurement-contract`. That focused gate owns
the tick-aware sampler, measurement orchestrator, shield correlation scaffold,
generated walker cleanup/input-ownership proof, and live-mode catalog. It is
intentionally separate from
`test:runtime-tooling-safety`; run the broader gate only when its shared
profile/CDB/input/smoke helpers change.

## Retained Protections

- Installed game and original `BEA.exe` remain read-only; patch tests still
  require copied targets and verified transitions.
- `test:runtime-tooling-safety` keeps profile preparation, exact CDB process
  identity, input receipt/HWND binding and key-release cleanup, bounded observer
  commands, and safe-copy cleanup active while the 95-child proof sweep remains
  non-routine.
- The four commands emitted by `OnlineMultiplayerReadinessService` are locked by
  inventory/source-reference tests and remain fail-closed readiness tools.
- `test:public-allowlist` still runs the full payload self-test, one root plus
  submodule scan, and migration inventory. The former aggregate scanned the root
  twice; focused hard-payload and submodule commands remain available for
  diagnosis.
- `test:rebuild` and the full release/ZIP signoff commands are unchanged.

## Rerouted Or Removed Ceremony

- The quick profile now uses the primary WinUI wrapper instead of separately
  rebuilding for `build:winui`, `test:appcore`, and `test:winui`.
- Current front doors use active documented-command validation. The all-history
  command scan remains `test:doc-commands-all`.
- Minor docs can use the non-writing public-core link check; all-tree link
  validation remains a broad closeout gate.
- Three unreferenced compatibility aliases were removed:
  `test:winui-copied-game-preflight`, `test:winui-copied-game-runtime`, and
  `test:winui-copied-game-music-replacement`.
- No historical checker, fixture, proof tool, release command, or safety test was
  deleted.

## Campaign Closeout Evidence

The final broad-enough source closeout passed in 749.2 seconds:

- `npm test`: 210.0s; zero-warning solution build, 1,316 AppCore tests, 138
  WinUI tests with 2 expected private-catalog skips, 38 rebuild Core tests, 21
  rebuild Client tests, 12 toolchain cases, 6 smoke-validator cases, and 6
  owned-process smoke-runner cases.
- `test:runtime-tooling-safety`: 38.6s; 8 profile-prep, 11 exact CDB identity,
  and 14 safe-copy smoke-helper tests.
- all-history documented commands: 3,766 files and 4,363 commands in 5.0s.
- all-tree Markdown links: 3,674 files and 6,336 local links in 3.8s.
- public allowlist: payload self-test, one 19,474-file root-plus-submodule scan,
  and migration inventory in 331.3s.
- repository hygiene: 39 rule tests, 29 text rules, 2 path rules, 1 required
  marker, and 18,619 explicit text-file line-ending checks in 159.9s.

Release profile, curated-manifest, docsync, JSON, and diff checks also passed.
No live-game, Ghidra, native Godot, installer, ZIP, signing, publication, or
release action was run.

A focused integration follow-up added the previously omitted window-input helper
self-test to both runtime safety profiles. After the Stage A receipt-hardening
integration, `test:runtime-tooling-safety` runs 8 profile-prep, 22 exact CDB
identity, 16 input-helper, and 27 safe-copy smoke-helper tests (73 total).

## Residual Risks

- The package namespace is still large. Removing historical entries requires a
  separate per-family migration of checker self-binding and dated evidence
  references; zero npm callers is not sufficient evidence.
- The 95-child copied-runtime proof aggregate remains expensive and may require
  ignored local evidence. It is maintainer research, not an ordinary PR gate.
- Whole-tree payload and hygiene checks remain multi-minute scans. Their cost is
  accepted at boundary and broad closeout points because their coverage is not
  replaced by a narrower test.
- Inventory reference discovery recognizes exact `npm run <name>` strings and
  direct Python checker self-binding. Human invocation outside tracked source is
  not proof that a command is safe to remove.
