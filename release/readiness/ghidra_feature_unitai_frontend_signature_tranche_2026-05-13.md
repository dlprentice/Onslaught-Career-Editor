# Ghidra Feature / UnitAI / FrontEnd Signature Tranche - 2026-05-13

Status: GREEN public-safe saved-Ghidra evidence.

This note records a serialized headless dry/apply/read-back tranche that corrected or hardened `12` saved Ghidra functions in the feature, UnitAI, FrontEnd, monitor, and pickup-spawn cluster around `0x004480c0` through `0x0044e300`.

## Saved Targets

| Address | Saved name | Evidence boundary |
| --- | --- | --- |
| `0x004480c0` | `CUnitAI__CanContinueDoorWingTransition` | Door/wing transition predicate with spawned-child and ballistic-arc context. |
| `0x0044ca30` | `CFeature__Init` | Corrects stale generic feature vfunc label; records feature data copy, actor init, occupancy-grid, shadow, and random-sample context. |
| `0x0044cbe0` | `CFeature__ShutdownAndRemoveFromWorld` | Corrects stale generic feature vfunc label; records sample kill, occupancy removal, visibility update, and base cleanup context. |
| `0x0044cd20` | `CUnitAI__DecayEngagementMetricAndMaybeTriggerVFunc200` | Hardens four-stack-argument signature with delta decay, profile clamp, and vfunc dispatch context. |
| `0x0044cee0` | `CFeature__MaybeSpawnRandomPickupFromData` | Corrects stale `CExplosionInitThing` label; owner is inferred from caller/feature fields and remains less certain than the observed pickup-spawn behavior. |
| `0x0044d1f0` | `CUnitAI__RunHelper2000AndDispatchVFunc0x38IfFlag4` | Hardens UnitAI timestamp/flag/vfunc-dispatch helper. |
| `0x0044d210` | `CUnitAI__RenderWithStaticShadowVisibilityUpdate` | Hardens one-stack-argument render signature and static-shadow visibility context. |
| `0x0044d6f0` | `CFrontEnd__RenderAndProcessModalPanel` | Hardens modal panel draw/input helper receiver. |
| `0x0044dd60` | `CFrontEnd__HandleModalPanelButton` | Hardens two-stack-argument modal button handler. |
| `0x0044dea0` | `CFrontEnd__IsMouseInputReady` | Hardens boolean frontend modal/mouse-input predicate. |
| `0x0044e2c0` | `CMonitor__CheckSVFAnimationAndAdvanceState` | Hardens monitor receiver signature for the `SVF` animation gate helper. |
| `0x0044e300` | `PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300` | Corrects stale `CExplosionInitThing` label to an owner-neutral attached pickup-spawn helper. |

## Validation

| Check | Result |
| --- | --- |
| Focused probe tests | `py -3 tools\ghidra_feature_unitai_frontend_signature_probe_test.py` passed `2/2` tests. |
| Python compile | `py -3 -m py_compile tools\ghidra_feature_unitai_frontend_signature_probe.py tools\ghidra_feature_unitai_frontend_signature_probe_test.py` passed. |
| Headless dry/apply | `ApplyFeatureUnitAiFrontendSignatureTranche.java` dry and apply each reported `targets=12 changed_or_would_change=12 failed=0`; apply printed `REPORT: Save succeeded`. |
| Read-back exports | Metadata `12` rows, decompile `12` exports, xrefs `27` rows, instructions `6252` rows, tags `12` rows, vtable slots `224` rows. |
| Focused npm probe | `cmd.exe /c npm run test:ghidra-feature-unitai-frontend-signature` passed with status `PASS`, `12` targets, and `12` metadata rows. |
| Whole-database baseline | `cmd.exe /c npm run test:ghidra-static-reaudit-baseline` passed with `6013` total functions, `0` legacy weak names, `1948` undefined signatures, and `1992` `param_N` signatures. |
| Whole-database queue | `cmd.exe /c npm run test:ghidra-static-reaudit-queue` passed with `1292` commented functions and `4721` commentless functions. |
| Ghidra backup | Live project backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260513_085340_post_wave368_feature_unitai_frontend_verified` with `19` files, `153357191` bytes, and `HashDiffCount=0`. |

The live queue counters did not move in this tranche because the checked functions were already in the broad counted buckets. The pass still improves the saved project by correcting stale owner labels, tightening receiver and stack-argument names, and writing proof-boundary comments/tags.

Current whole-project confirmation proxies remain telemetry only: comment-backed `1292/6013 = 21.49%`; strict comment-plus-no-`undefined`-or-`param_N` proxy `1230/6013 = 20.46%`. These are not milestones or completion gates.

## Claim Boundary

This is saved static retail Ghidra evidence only. It does not prove exact Stuart-source method identity, concrete layouts/types, local variables, runtime feature/AI/frontend/monitor/pickup behavior, BEA launch behavior, game patching, or rebuild parity.

Adjacent no-function/vtable follow-up targets such as `0x0044e4e0`, `0x0044e550`, and `0x0044e570` remain future boundary-recovery work.
