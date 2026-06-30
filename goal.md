# Active Goal Slice

Status: active
Last updated: 2026-06-30
Policy: `goal.policy.md`

## Current Slice

The parallel rebuild/lore/WinUI integration wave has folded in four bounded
tracked improvements:

- PatchBench now has pre-extraction receipt formatter behavior tests and an
  unwired primitive formatter scaffold:
  `OnslaughtCareerEditor.UiTests/PatchBenchSafeCopyReceiptTextTests.cs`,
  `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSafeCopyReceiptText.cs`, and
  `OnslaughtCareerEditor.WinUI/Models/PatchBenchSafeCopyReceiptTextState.cs`.
- Public-safe RE/rebuild work now has a materialized
  `tmm-arm4-readiness-gate` proof-plan slot and checker:
  `reverse-engineering/game-assets/texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan.md`
  and `tools/rebuild_tmm_arm4_readiness_gate_proof_plan_probe.py`.
- Lore pack building/checking now fails closed on unsafe or inconsistent
  `relativePath` metadata, and AppCore content-pack loading now fails closed on
  unsafe loaded document paths, duplicate ids/paths, content hash mismatch, and
  stale-pack retention without echoing row-controlled path/id values through
  current AppCore content-pack load exceptions.
- The WinUI shell now restores a persisted `LastTab` value of `0` back to Save
  Lab, with source-level product-lane coverage.

The next executable product slice is PatchBench receipt extraction readiness
hardening before any live page wiring: add focused tests for concatenated or
interpolated forbidden output sentinels, decide and encode the manifest-filename
display policy, cover Host/Join partial/variant boundary cases, and add
page-versus-helper parity tests with documented intentional deltas. Only after
those tests are green should a later slice project AppCore receipt DTOs into
WinUI-local primitive state and consider wiring the helper.

## Current Truth

- `PatchBenchSafeCopyReceiptText` is an unwired WinUI-local primitive scaffold.
  It is a contract/test target only. It is not a live production formatter,
  not extraction completion, and not runtime hostile-value rejection proof.
- `BinaryPatchesPage` still owns page receipt projection, receipt DTO
  consumption, File/Path/I/O, service calls, UI assignment, operation-log text,
  `AppStatusService` updates, launch option tuples, selected-state mutation,
  matching logic, launch argument construction, safe-copy launch planning,
  process control, patch/catalog semantics, source-summary decisions,
  Host/Join fallback ownership, online claim boundaries, and runtime-proof
  boundaries.
- AppCore still owns receipt truth, receipt construction, patch planning,
  copied-profile safety, save/options correctness, and core behavior contracts.
- Future PatchBench presentation helpers may receive only display-safe
  primitive or primitive-record values: strings, booleans, counts, small enums,
  nullable primitive fields, and sanitized display lists.
- The static primitive projection guard now covers the new receipt helper/model
  split and still protects `PatchBench*.cs` files under WinUI `Helpers/` and
  `Models/`. `BinaryPatchesPage` remains protected by explicit ownership
  tripwires.
- The PatchBench reviewer left one non-blocking future caveat: static
  output-leak sentinels need concatenation/interpolation adversarial samples,
  and the manifest filename policy must be made explicit before helper wiring.
- The `tmm-arm4-readiness-gate` artifact is a public-safe proof-plan and
  continuity checker only. It is not readiness-gate execution, command arming,
  importer execution, generated payload output, private asset read, runtime
  proof, visual/gameplay proof, rebuild parity, runtime parity, or
  no-noticeable-difference parity.
- Lore pack `relativePath` metadata hardening is metadata integrity and
  public/private-boundary hardening. Builder/checker validation owns
  index/content relativePath equality today; AppCore loading validates loaded
  document metadata and generic failure messages. This is not release
  readiness, broad ZIP packaging parity, or a proven filesystem traversal
  vulnerability fix.
- Lore package ZIP probe parity remains a next hardening candidate:
  `tools/winui_zip_package_probe.py` should eventually enforce the same
  `relativePath` grammar.
- The WinUI UX audit resolved only Save Lab route restoration for persisted
  tab `0`. Residual UX/copy debt remains open, including Asset Library path
  redaction, PatchBench proof/CDB/manifest/offset wording, online diagnostic
  placement, first-run clarity, accessibility labeling/live-region risks, and
  broader Home/About/Save Lab copy polish.
- Storage taxonomy remains read-only/no-delete. High-confidence deletion
  candidates are 0, deletion performed is false, authorized reclaimed storage
  is 0 GiB, and actual reclaimed storage is 0 GiB.
- Future medium/low storage review values are non-authorized logical review
  ceilings only. They are not reclaimable storage, unique physical-size
  estimates, candidate pools, urgency signals, cleanup targets, or deletion
  budgets.
- Future storage deletion still requires explicit authority, scoped lease,
  exact private manifest row ids and digest, retained alternatives,
  reference/hash/provenance review, containment and unique-size proof, dry-run,
  quarantine/rollback/restore proof, candidate-specific consults, and
  independent acceptance.
- Runtime proof remains private pre-arm/no-live only. Public runtime flags
  remain `readyToRunLiveAttempt=false`, `liveArmAllowed=false`,
  `runtimeAudibleOutputProof=false`, and
  `preArmReadiness.status=prearm-readiness-not-proven`.
- Producer coverage for music proof is not live authority, proof readiness, or
  audible-output proof. Future live work needs separate explicit private
  authority, leases, freshness/root/process-census binding, no stale readiness
  replay, and no public arm phrase or runnable live command leakage.
- Consult compliance for this wave is report-attested and sanitized-bundle
  scanned only. It is not raw prompt/output reconstruction or exact Cursor
  command-line proof. Use "no recorded blocking dissent among completed lanes,"
  not blanket no-dissent wording.
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
  publication, or push action is part of this integration.

## Evidence Pointers

- PatchBench receipt behavior tests:
  `OnslaughtCareerEditor.UiTests/PatchBenchSafeCopyReceiptTextTests.cs`
- Primitive projection guard:
  `OnslaughtCareerEditor.UiTests/PatchBenchPrimitiveProjectionBoundaryTests.cs`
- Primitive receipt scaffold:
  `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSafeCopyReceiptText.cs`
- PatchBench page orchestration:
  `OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml.cs`
- RE/rebuild readiness-gate proof plan:
  `reverse-engineering/game-assets/texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan.md`
- RE/rebuild readiness-gate checker:
  `tools/rebuild_tmm_arm4_readiness_gate_proof_plan_probe.py`
- Lore pack loader:
  `OnslaughtCareerEditor.AppCore/LoreBrowserService.cs`
- Lore pack builder/checker:
  `tools/winui_lore_pack_builder.py`
- Save Lab route persistence:
  `OnslaughtCareerEditor.WinUI/MainWindow.xaml.cs`
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

1. PatchBench next: add tests for concatenated/interpolated forbidden sentinels,
   manifest filename policy, Host/Join partial/variant boundary cases, and
   page-versus-helper parity before any helper wiring.
2. PatchBench follow-up after those tests pass: project AppCore receipt DTOs
   into WinUI-local primitive state and consider wiring the helper without
   moving File/Path/I/O, receipt construction, launch planning, process
   control, catalog semantics, online boundaries, or runtime-proof boundaries.
3. Lore next: add ZIP package probe parity for lore-pack `relativePath`
   validation, keep user-visible load errors generic, and decide whether
   AppCore should also enforce index/content relativePath equality instead of
   leaving that to builder/check tooling.
4. RE/rebuild next: run only public-safe checker/proof-plan advancement until a
   separate task grants explicit readiness-gate authority; do not treat
   `tmm-arm4-readiness-gate` as executed.
5. WinUI UX next: address one residual high-confidence path-redaction,
   proof-jargon, first-run, or accessibility issue at a time with focused
   tests/build evidence.
6. Storage next: do only read-only manifest/hash/reference work until a future
   task records explicit deletion authority, candidate-specific retained
   alternatives, dry-run evidence, consults, rollback/quarantine plan, and
   independent acceptance.
7. Runtime next: keep music proof as private pre-arm checklist-only work unless
   a future task grants explicit runtime-proof authority, leases, private proof
   root readiness, arm phrase handling, and cleanup validation.

## Stop Conditions

- Any step would mutate the installed game folder or original `BEA.exe`.
- Any tracked file would add hard payloads, raw proof logs, screenshots/frame
  dumps, copied executable output, full Ghidra databases, secrets, `.env*`,
  build output, package output, local runtime caches, raw local proof paths, raw
  manifests, thread IDs, local campaign/worktree paths, or private proof
  artifacts.
- Any claim would promote online readiness, Host/Join availability, runtime
  audio proof, gameplay parity, visual parity, release readiness, release
  publication, rebuild parity, or no-noticeable-difference parity beyond
  accepted evidence.
- Storage work would move, quarantine, delete, or reclaim material without the
  required future authority and candidate-specific evidence.
- Required validation fails without a bounded explanation and correction path.
