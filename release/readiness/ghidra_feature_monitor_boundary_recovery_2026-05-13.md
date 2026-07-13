# Ghidra Feature / Monitor Boundary Recovery - 2026-05-13

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x0044e640` → `CFenrirMainGunAI__ScanListsAndSelectSupportTarget` (was `CSquadNormalReader__ScanListsAndSelectSupportTarget_0044e640`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: GREEN public-safe saved-Ghidra evidence.

This note records a serialized headless dry/apply/read-back tranche that recovered `7` adjacent feature, monitor, component-targeting, and global-callback function boundaries around `0x0044dfb0` through `0x0044e9e0`.

## Saved Targets

| Address | Saved name | Evidence boundary |
| --- | --- | --- |
| `0x0044dfb0` | `FenrirEffects__InitBurningAndEngineHandles_0044dfb0` | Data/vtable-slot boundary that initializes fields near `+0x27c/+0x280` and resolves the `Fenrir Inside Burning` and `Fenrir Engines` effect strings. |
| `0x0044e4e0` | `PickupSpawn__UpdateAttachedPickupBurst_0044e4e0` | Adjacent pickup-spawn helper that dispatches transform/animation virtual slots and calls `PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300` twice. |
| `0x0044e550` | `GlobalCallback__ClearMatrixBlock006776E8` | Zero-argument callback from table `0x00622230`; clears the `0x006776e8` matrix-style block head. |
| `0x0044e570` | `GlobalCallback__InitMatrixBlock006776B8` | Zero-argument callback from table `0x00622230`; initializes the `0x006776b8` matrix-style block with identity/zero context. |
| `0x0044e640` | `ComponentTargeting__ScanListsAndMaybeTriggerAction_0044e640` | Owner-deferred component-targeting boundary that scans list heads, compares candidate positions/ranges, and conditionally dispatches helper `0x004ffdd0`. |
| `0x0044e9c0` | `GlobalCallback__ClearMatrixBlock00677768` | Zero-argument callback from table `0x00622230`; clears the `0x00677768` matrix-style block head. |
| `0x0044e9e0` | `GlobalCallback__InitMatrixBlock00677738` | Zero-argument callback from table `0x00622230`; initializes the `0x00677738` matrix-style block with identity/zero context. |

This closes the Wave368 adjacent no-function follow-up for `0x0044e4e0`, `0x0044e550`, and `0x0044e570`, and also recovers `0x0044dfb0`, `0x0044e640`, `0x0044e9c0`, and `0x0044e9e0`.

## Validation

| Check | Result |
| --- | --- |
| Focused probe tests | `py -3 tools\ghidra_feature_monitor_boundary_probe_test.py` passed `2/2` tests. |
| Python compile | `py -3 -m py_compile tools\ghidra_feature_monitor_boundary_probe.py tools\ghidra_feature_monitor_boundary_probe_test.py` passed. |
| Headless dry/apply | `ApplyFeatureMonitorBoundaryTranche.java` dry and apply each reported `targets=7 changed_or_would_change=7 failed=0`; apply printed `REPORT: Save succeeded`. |
| Read-back exports | Metadata `7` rows, decompile `7` exports, xrefs `7` rows, instructions `2695` rows, tags `7` rows, vtable slots `48` rows. |
| Focused npm probe | `cmd.exe /c npm run test:ghidra-feature-monitor-boundary` passed with status `PASS`, `7` targets, and output under ignored `subagents\ghidra-static-reaudit\feature-monitor-boundary-wave369\current\`. |
| Whole-database baseline | Refreshed `ExportWeakFunctionList.java` all-functions export plus `cmd.exe /c npm run test:ghidra-static-reaudit-baseline` passed with `6020` total functions, `0` legacy weak names, `1980` `param_N` signatures, and `1948` undefined signatures. |
| Whole-database queue | Refreshed `ExportFunctionQualitySnapshot.java` plus `cmd.exe /c npm run test:ghidra-static-reaudit-queue` passed with `1311` commented functions and `4709` commentless functions. |
| Ghidra backup | Live project backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260513_093318_post_wave369_feature_monitor_boundary_verified` with `19` files, `153389959` bytes, and `HashDiffCount=0`. |

Current whole-project confirmation proxies remain telemetry only: comment-backed `1311/6020 = 21.78%`; strict comment-plus-no-`undefined`-or-`param_N` proxy `1249/6020 = 20.75%`. These are not milestones or completion gates.

## Claim Boundary

This is saved static retail Ghidra evidence only. It does not prove exact Stuart-source method identity, concrete owner classes, concrete layouts/types, local variables, runtime feature/monitor/component/global-callback behavior, BEA launch behavior, game patching, or rebuild parity.
