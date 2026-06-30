# Active Goal Slice

Status: active
Last updated: 2026-06-30
Policy: `goal.policy.md`

## Current Slice

The receipt-boundary integration wave has accepted a test-only PatchBench
primitive projection guard:

- `OnslaughtCareerEditor.UiTests/PatchBenchPrimitiveProjectionBoundaryTests.cs`
  now guards future PatchBench receipt/source presentation helpers with
  recursive helper/model discovery, path-keyed boundary profiles, profile-scoped
  sensitive identifier checks, broad `GameProfile*` rejection for receipt/source
  projection surfaces, hostile static samples, output leak sentinels, and page
  ownership tripwires.

The next executable product slice is formatter behavior coverage before any
receipt helper extraction: add focused tests for receipt output layout,
hostile path/proof-id/command-preview redaction boundaries, online-ready wording
rejection, and Host/Join boundary rendering exactly once. Do not extract the
receipt formatter until those behavior tests exist and pass. Do not extract
source-summary helpers until path/redaction projection is explicitly tested.

## Current Truth

- `roadmap/patchbench-primitive-projection-contract.md` remains the design-only
  primitive presentation contract. It is not behavior movement, extraction
  approval, AppCore ownership movement, runtime proof, or release evidence.
- `PatchBenchPrimitiveProjectionBoundaryTests` is test-only static guard
  coverage. It is not formatter output proof, UIA proof, runtime proof,
  Host/Join behavior proof, or extraction readiness by itself.
- The current boundary scanner covers `PatchBench*.cs` files under WinUI
  `Helpers/` and `Models/`. `BinaryPatchesPage` remains protected by explicit
  ownership tripwires, not by the helper/model profile scanner.
- Cross-file primitive record/enum support is covered by synthetic guard
  samples. A future real receipt/source extraction that splits primitive models
  across files must wire and validate those files under the receipt/source
  profile before claiming extraction readiness.
- `BinaryPatchesPage` still owns page projection, File/Path checks, service
  calls, UI assignment, operation-log text, `AppStatusService` updates, launch
  option tuples, selected-state mutation, matching logic, launch argument
  construction, safe-copy launch planning, process control, patch/catalog
  semantics, source-summary decisions, Host/Join fallback ownership, online
  claim boundaries, and runtime-proof boundaries.
- AppCore still owns receipt truth, receipt construction, patch planning,
  copied-profile safety, save/options correctness, and core redaction or
  behavior contracts.
- Future PatchBench presentation helpers may receive only display-safe
  primitive or primitive-record values: strings, booleans, counts, small enums,
  nullable primitive fields, and sanitized display lists.
- The prior adversarial receipt-boundary findings for filename routing,
  sensitive primitive/member leakage, record/member parsing, incomplete
  `GameProfile*` result coverage, and non-recursive helper/model discovery are
  addressed at the static guard layer. Formatter output/redaction and Host/Join
  exactly-once behavior proof remain future extraction gates.
- Storage taxonomy remains read-only/no-delete. High-confidence deletion
  candidates are 0, deletion performed is false, and authorized reclaimed
  storage is 0 GiB.
- Future medium/low storage values are non-authorized logical review ceilings
  only. They are not reclaimable storage, not unique physical-size estimates,
  and not deletion budgets. Future deletion still requires explicit authority,
  candidate-specific evidence, retained alternatives, dry-run/quarantine and
  rollback proof, workspace-safe consults, and independent acceptance.
- Runtime proof remains private pre-arm readiness only. Public runtime flags
  remain `readyToRunLiveAttempt=false`, `liveArmAllowed=false`,
  `runtimeAudibleOutputProof=false`, and
  `preArmReadiness.status=prearm-readiness-not-proven`.
- No live execution, BEA launch, CDB attach, audio capture, proof archive
  write, copied executable mutation, Ghidra mutation/read-back,
  installed-game mutation, original `BEA.exe` mutation, runtime audible-output
  proof, all-cue proof, release readiness, gameplay proof, rebuild proof, or
  parity proof is claimed.
- Consult compliance must stay split: the receipt-boundary write worker and
  repair lanes are six-lane complete; storage and runtime read-only reports are
  six-lane complete; the next-helper read-only report is fallback-compliant but
  matrix-incomplete; the consult-compliance smoke had tainted/unavailable lanes
  and is not independent sanitization verification.
- External consult sanitization is report-attested only unless raw prompts and
  outputs are separately audited. Use "no recorded blocking dissent among
  completed lanes," not blanket no-dissent wording.
- Online multiplayer remains not player-ready. Host/Join stays disabled or
  unavailable until distinct-endpoint command-source proof and source-bound
  copied-runtime causality proof are both accepted.
- Static RE closure is not runtime, gameplay, visual, online, rebuild, or
  no-noticeable-difference proof.
- Hard payloads remain outside git and release ZIPs: game executables, copied
  executables, copied runtime output, arbitrary saves/options, raw proof logs,
  screenshots or frame dumps, full Ghidra databases, secrets, `.env*`, local
  runtime caches, build output, and package output.
- Installed game files and original `BEA.exe` remain read-only.
- No release, tag, package, signing, installer, announcement, hosted workflow,
  or publication action is part of this integration.

## Evidence Pointers

- Receipt/source static guard tests:
  `OnslaughtCareerEditor.UiTests/PatchBenchPrimitiveProjectionBoundaryTests.cs`
- Primitive projection contract:
  `roadmap/patchbench-primitive-projection-contract.md`
- PatchBench page orchestration:
  `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml.cs`
- Launch/control preset presentation helper:
  `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchLaunchPresetText.cs`
- Runtime pre-arm readiness note:
  `release/readiness/winui_music_live_bundle_prearm_readiness_2026-06-29.md`
- Storage hygiene boundary:
  `LOCAL_LAB_OVERLAY.md`
- Coordination contracts:
  `coordination/README.md`, `coordination/WORKSTREAM_CONTRACT.md`,
  `coordination/REPORT_CONTRACT.md`, and `coordination/RESOURCE_LEASES.md`
- Canonical state batons:
  `developer_agent_state.json`, `documentation_agent_state.json`, and
  `re_orchestrator_state.json`

## Next Executable Work

1. Add receipt formatter behavior tests before extraction. Cover headline,
   label/value rows, section headings, bullet formatting, trimming,
   hostile path/proof-id/command-preview output sentinels, online-ready wording
   rejection, and Host/Join boundary rendering exactly once.
2. Keep `GameProfilePreflightService.BuildPrepareReceipt`, AppCore receipt DTO
   consumption, Host/Join fallback normalization, File/Path/I/O, launch
   planning, process control, catalog semantics, online boundaries, and runtime
   proof boundaries out of presentation helpers.
3. Extract a narrow receipt formatter only after the behavior tests and static
   boundary tests are green, using WinUI-local primitive state.
4. Keep source-summary extraction deferred until raw path and catalog reads are
   projected by the page and path/redaction projection tests exist.
5. For storage, do only read-only manifest/hash/reference work until a future
   task records explicit deletion authority, candidate-specific retained
   alternatives, dry-run evidence, consults, rollback/quarantine plan, and
   independent acceptance.
6. For runtime music proof, the only safe next baton is private pre-arm
   readiness under separate explicit authority. Do not issue a live arm phrase
   or run BEA/CDB/audio/live proof from this public baton.

## Stop Conditions

- Any step would mutate the installed game folder or original `BEA.exe`.
- Any tracked file would add hard payloads, raw proof logs, screenshots/frame
  dumps, copied executable output, full Ghidra databases, secrets, `.env*`,
  build output, package output, local runtime caches, raw local proof paths, raw
  manifests, thread IDs, or local campaign/worktree paths.
- Any claim would promote online readiness, Host/Join availability, runtime
  audio proof, gameplay parity, visual parity, release readiness, release
  publication, rebuild parity, or no-noticeable-difference parity beyond
  accepted evidence.
- Storage work would move, quarantine, delete, or reclaim material without the
  required future authority and candidate-specific evidence.
- Required validation fails without a bounded explanation and correction path.
