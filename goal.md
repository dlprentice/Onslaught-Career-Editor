# Active Goal Slice

Status: standing wave active; source-only RE map reconciliation
Last updated: 2026-07-02
Policy: `goal.policy.md`

## Current Slice

The chief epic rebuild/Ghidra/Lore/WinUI wave has been integrated, accepted, and
pushed from the accepted worker source commits. Pre-state-update source-ref proof
showed the wave tip `a9fe757e238a237eac8aa8f7f4e12d1bad57ec60` matched
`HEAD`, `origin/main`, and live remote `refs/heads/main` with divergence `0 0`.

Accepted source commits integrated by cherry-pick:

- W1 PatchBench prewiring: `cd7d7bf928c32234e3e59d5021b695c7aeabb63d`
- W3 clean-room rebuild continuity: `301b81a5baba1d5fb870890903961c16eaead5bf`
- W6 original-system mapping: `930c2cf3cdd8d4376bfabf579565de96cb98323d`
- W7 Lore hardening: `98b39b84e2251b775b407d0d2984fc8f9c197409`
- W7 blocker fix follow-up: `1ad0f0cc3f1ba7a796d0c94dc00a5dc69bbd182f`
- W8 WinUI UX/accessibility: `e24c9e6ca7b6a2795ac27144dc575a5ced1ef6b7`
- W9 patch/mod quality: `5d13adeb70e1aa2d1bfdcbdf39d639b2811e9c27`
- W10 release ZIP docs: `af8136583eb2de60672e77ea1c21c7bc827fbaac`
- W11 docs governance: `821fe61f5d192b6a08c0107dd87266139aeb8ffb`

Report-only lanes remain campaign evidence, not source commits: W2 superseded
PatchBench parity, W4 static sentinel, W5 storage/Ghidra backup safety, W12
runtime-proof baton, and W13 consult compliance.

## Current Truth

- PatchBench now has pre-wiring receipt boundary tests and a behavior-free
  helper scaffold. It remains unwired; live page receipt projection, File/Path
  I/O, launch planning, process control, catalog semantics, Host/Join fallback,
  online boundaries, and runtime-proof boundaries stay in the page/AppCore
  owners.
- Patch/mod grouping now shows bounded group scan summaries sourced from visible
  rows and tracks. Integration added focused source/binding coverage for
  `ScanSummary`.
- Lore ZIP/package hardening includes the Reviewer C follow-up. AppCore and the
  ZIP probe now align on above-root packed links, document-id grammar, and
  case-variant content-id hash lookup. This is not broad release readiness or a
  complete filesystem traversal proof.
- The rebuild/readiness-gate update is public-safe continuity hardening only.
  It is not command arming, importer execution, private asset reading,
  generated payload output, runtime proof, rebuild parity, visual/gameplay
  parity, or no-noticeable-difference proof.
- Original-system mapping is a public-safe crosswalk. Source names are candidate
  owners; retail binary/save/runtime evidence remains the higher authority for
  behavior.
- The source-only internal tooling vocabulary map is public-safe planning
  context for future clean-room questions. It is not readiness-gate execution,
  command arming, importer execution, generated payload output, runtime proof,
  rebuild parity, or no-noticeable-difference proof.
- WinUI Home/About copy and static accessibility/product-lane tests improved
  user-facing boundaries. This is not runtime screen-reader, visual, BEA, CDB,
  audio, or gameplay proof.
- Release ZIP docs were clarified without publication, signing, installer, MSIX,
  Store, upload, tag, release asset, or announcement work.
- Docs governance removed stale readiness wording and keeps the current public
  signoff route separate from historical checklists.
- Storage/Ghidra backup details remain local campaign evidence only. Tracked
  docs/state should retain only sanitized conclusions: no deletion in source,
  no live Ghidra mutation, and no raw storage manifests or private paths.

## Known Non-Claims

- No installed game folder or original `BEA.exe` mutation.
- No BEA/CDB/audio launch, live runtime proof, audible-output proof, or visual
  gameplay proof.
- No Host/Join enablement, player-ready online, public matchmaking, or online
  capability promotion.
- No release publication, signing, installer/MSIX/Store work, GitHub Release
  upload, tag, or announcement.
- No Ghidra project mutation or fresh decompiler/read-back verification.
- No static-accounting gate health claim while the Wave1200 support-file
  blocker remains unresolved.
- No docsync/mirror health claim while the pre-existing mirror drift remains
  unresolved or unwaived.
- No rebuild parity, runtime parity, visual/gameplay parity, or
  no-noticeable-difference proof.

## Validation Status

Merged-tree validation passed for the source and package checks required by the
integrated changes:

- `git diff --check`
- state JSON parse and targeted local-campaign/private-drive pattern scan
- `py -3 tools\rebuild_tmm_arm4_readiness_gate_proof_plan_probe.py --self-test --check`
- `py -3 tools\winui_zip_package_probe_test.py`
- `py -3 tools\winui_lore_pack_builder.py --self-test`
- full `LoreBrowserServiceTests`
- `npm run build:winui`
- focused W1/W8/W9 UiTests, including integration-added `ScanSummary` coverage
- `npm run test:winui-patch-engine-safety`
- `npm run test:winui-primary-lane`
- ZIP package probe without optional representative Media smoke
- `npm run test:doc-commands`
- `npm run test:md-links`
- `npm run test:repo-hygiene` after a timeout retry
- `npm run test:public-allowlist`
- `npm run test:hard-payload-safety`

The source-only internal tooling vocabulary map reconciliation additionally
passed:

- `git diff --check`
- `npm run test:doc-commands`
- `npm run test:md-links`
- `npm run test:repo-hygiene`
- `npm run test:hard-payload-safety`
- `npm run test:public-allowlist` after a timeout retry

Phase 0 stale-baton correction is state-only. The `a9fe757e238a237eac8aa8f7f4e12d1bad57ec60`
proof confirms the previous source wave was already pushed and accepted; it is
not fresh runtime, release, Ghidra, static-accounting, or storage proof.

Known pre-existing or intentionally unclaimed gates:

- Static Wave1200 accounting support-file blocker remains unless explicitly
  fixed and rerun.
- `tools/docsync_check.py` mirror drift remains unless explicitly fixed and
  rerun.
- `npm run test:winui-zip-release-candidate-probe` remains unclaimed because
  the optional representative Media smoke failed on extracted-app audio row
  selection; the same ZIP probe without optional Media smoke passed.

## Evidence Pointers

- PatchBench receipt and group-summary tests:
  `OnslaughtCareerEditor.UiTests/PatchBenchSafeCopyReceiptTextTests.cs` and
  `OnslaughtCareerEditor.UiTests/WinUiProductLaneTests.cs`
- PatchBench helpers and models:
  `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSafeCopyReceiptText.cs`,
  `OnslaughtCareerEditor.WinUI/Helpers/PatchBenchPatchGroups.cs`, and
  `OnslaughtCareerEditor.WinUI/Models/BinaryPatchGroupModel.cs`
- Lore pack loader and probes:
  `OnslaughtCareerEditor.AppCore/LoreBrowserService.cs`,
  `tools/winui_zip_package_probe.py`, and
  `tools/winui_zip_package_probe_test.py`
- Rebuild readiness-gate continuity:
  `tools/rebuild_tmm_arm4_readiness_gate_proof_plan_probe.py` and the linked
  proof-plan under `reverse-engineering/game-assets/`
- Original-system crosswalk:
  `roadmap/rebuild-front-door-chain-map.md`
- Source-only internal tooling vocabulary map:
  `reverse-engineering/source-code/original-system-internal-tooling-vocabulary-map.md`
- WinUI UX/accessibility surfaces:
  `OnslaughtCareerEditor.WinUI/Pages/HomePage.xaml`,
  `OnslaughtCareerEditor.WinUI/Pages/AboutPage.xaml`, and
  `OnslaughtCareerEditor.UiTests/WinUiAccessibilityAuditTests.cs`
- Release/docs governance:
  `release/readiness/WINUI-ZIP-README.txt`,
  `release/readiness/release_readiness_checklist.md`, and `COLLABORATION.md`

## Next Executable Work

1. Repair or explicitly bound the Static Wave1200 accounting support-file
   blocker with the relevant static-accounting gate before claiming health.
2. Reconcile or intentionally document `tools/docsync_check.py` mirror drift
   before claiming docsync or mirror health.
3. Decide whether to run the optional representative Media smoke audio-row
   selection in a separately authorized runtime-proof lane; leave it unclaimed
   otherwise.
4. Continue PatchBench only with tests first: decide whether any helper wiring
   is still desirable, preserve page/AppCore ownership of behavior, and keep
   Host/Join and runtime-proof boundaries unchanged.
5. Continue Lore with bounded ZIP/package parity hardening only; do not promote
   it to broad release or traversal-proof claims.
6. Continue RE/rebuild with public-safe proof-plan/checker work until separate
   authority grants live Ghidra mutation, runtime proof, private asset reads, or
   importer execution.
7. Use the internal tooling vocabulary map only to pick one bounded future
   question with an explicit higher-authority proof class.

## Stop Conditions

- Remote `main` changes away from the verified safe base or this integration
  ancestry before push.
- A validation failure affects integrated behavior and cannot be bounded as
  pre-existing or out of scope.
- Any tracked file would add hard payloads, secrets, raw local campaign paths,
  raw storage manifests, private proof paths, thread IDs, screenshots/frame
  dumps, copied executables, full Ghidra databases, `.env*`, build output, or
  package output.
- Any work would mutate installed game files, original `BEA.exe`, live Ghidra
  projects, release assets, or runtime proof state without separate explicit
  authority.
