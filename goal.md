# Active Goal Slice

Status: active
Last updated: 2026-07-01
Policy: `goal.policy.md`

## Current Slice

The failed-wave rescue integration has folded the accepted rescue work into
local `main` for final serial validation and remote sync:

- Private Ghidra project/store/backup pointers were removed from the tracked
  local overlay guide while public/local boundaries stayed intact.
- The public-safe `tmm-arm4-readiness-gate` proof-plan/checker path was
  hardened for active-slot continuity, fail-closed wording, and overclaim
  guards.
- Lore content-pack loading now fails closed for incomplete or empty pack
  signals and malformed generated document ids, while keeping user-facing load
  failures generic.
- Asset Library passive material-package status now summarizes the output root
  while explicit Open/Copy full-path actions remain, and source tests guard the
  page's polite live-region scope.

This slice is not terminal until the integrated tree passes the final serial
validation matrix, pushes to `origin/main`, and verifies local `HEAD`,
`origin/main`, and live remote `refs/heads/main` are identical.

## Current Truth

- `PatchBenchSafeCopyReceiptText` remains an unwired WinUI-local primitive
  scaffold. It is a contract/test target only, not a live production formatter,
  extraction completion, or runtime hostile-value rejection proof.
- `BinaryPatchesPage` still owns live page receipt projection, AppCore receipt
  DTO consumption, File/Path/I/O, service calls, UI assignment, operation-log
  text, `AppStatusService` updates, launch option tuples, selected-state
  mutation, matching logic, launch argument construction, safe-copy launch
  planning, process control, patch/catalog semantics, source-summary decisions,
  Host/Join fallback ownership, online claim boundaries, and runtime-proof
  boundaries.
- The PatchBench next gate remains: add concatenated/interpolated forbidden
  sentinel tests, decide and encode manifest filename display policy, cover
  Host/Join partial/variant boundaries, and add page-versus-helper parity tests
  before any helper wiring.
- The `tmm-arm4-readiness-gate` artifact is a public-safe proof-plan/checker
  continuity guard only. It is not readiness-gate execution, command arming,
  shell dispatch, importer execution, private asset read, generated payload
  output, runtime proof, visual/gameplay proof, rebuild parity, runtime parity,
  or no-noticeable-difference parity.
- Lore pack relativePath index/content equality is still owned by builder/check
  tooling today. AppCore content-pack loading validates loaded document
  metadata, incomplete/empty pack signals, malformed generated ids, duplicate
  ids/paths, hash mismatch, and stale pack retention boundaries.
- Lore package ZIP probe parity remains a next hardening candidate:
  `tools/winui_zip_package_probe.py` should eventually enforce the same
  `relativePath` grammar.
- Lore hardening is not release readiness, broad ZIP packaging parity, runtime
  UI proof, or a complete filesystem traversal vulnerability fix.
- Asset Library path/accessibility work is a bounded source/test improvement:
  passive status summarizes the output root, explicit full-path Open/Copy
  actions remain, and the page has a single source-declared polite live region.
  This is not a runtime UIA/screen-reader proof or broad UX redesign.
- WinUI residual UX/copy debt remains open, including broader path redaction,
  PatchBench proof/CDB/manifest/offset wording, online diagnostic placement,
  first-run clarity, accessibility labeling/live-region risks, and Home/About/
  Save Lab copy polish.
- Storage taxonomy remains read-only/no-delete. High-confidence deletion
  candidates are 0, deletion performed is false, authorized reclaimed storage is
  0 GiB, and actual reclaimed storage is 0 GiB.
- Runtime proof remains private pre-arm/no-live only. Public runtime flags remain
  `readyToRunLiveAttempt=false`, `liveArmAllowed=false`,
  `runtimeAudibleOutputProof=false`, and
  `preArmReadiness.status=prearm-readiness-not-proven`.
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
  publication, runtime proof, storage deletion, Ghidra mutation/read-back, or
  Host/Join enablement is part of this integration.

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
- Asset Library page:
  `OnslaughtCareerEditor.WinUI/Pages/AssetLibraryPage.xaml`
- Asset Library source tests:
  `OnslaughtCareerEditor.UiTests/WinUiProductLaneTests.cs` and
  `OnslaughtCareerEditor.UiTests/WinUiAccessibilityAuditTests.cs`
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

1. Finalize this rescue only after final serial validation passes and remote
   sync is verified.
2. PatchBench next: add tests for concatenated/interpolated forbidden
   sentinels, manifest filename policy, Host/Join partial/variant boundary
   cases, and page-versus-helper parity before any helper wiring.
3. PatchBench follow-up after those tests pass: project AppCore receipt DTOs
   into WinUI-local primitive state and consider wiring the helper without
   moving File/Path/I/O, receipt construction, launch planning, process
   control, catalog semantics, online boundaries, or runtime-proof boundaries.
4. Lore next: add ZIP package probe parity for lore-pack `relativePath`
   validation, keep user-visible load errors generic, and decide whether
   AppCore should also enforce index/content relativePath equality instead of
   leaving that to builder/check tooling.
5. RE/rebuild next: run only public-safe checker/proof-plan advancement until a
   separate task grants explicit readiness-gate authority; do not treat
   `tmm-arm4-readiness-gate` as executed.
6. WinUI UX next: address one residual high-confidence path-redaction,
   proof-jargon, first-run, or accessibility issue at a time with focused
   tests/build evidence.
7. Storage next: do only read-only manifest/hash/reference work until a future
   task records explicit deletion authority, candidate-specific retained
   alternatives, dry-run evidence, consults, rollback/quarantine plan, and
   independent acceptance.
8. Runtime next: keep music proof as private pre-arm checklist-only work unless
   a future task grants explicit runtime-proof authority, leases, private proof
   root readiness, arm phrase handling, and cleanup validation.

## Stop Conditions

- Any step would mutate the installed game folder or original `BEA.exe`.
- Any tracked file would add hard payloads, raw proof logs, screenshots/frame
  dumps, copied executable output, full Ghidra databases, secrets, `.env*`,
  build output, package output, local runtime caches, raw local proof paths,
  raw manifests, thread IDs, local campaign/worktree paths, or private proof
  artifacts.
- Any claim would promote online readiness, Host/Join availability, runtime
  audio proof, gameplay parity, visual parity, release readiness, release
  publication, rebuild parity, complete traversal protection, runtime
  screen-reader proof, or no-noticeable-difference parity beyond accepted
  evidence.
- Storage work would move, quarantine, delete, or reclaim material without the
  required future authority and candidate-specific evidence.
- Required validation fails without a bounded explanation and correction path.
