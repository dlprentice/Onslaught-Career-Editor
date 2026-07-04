# PhysicsScript Static Contract Wave1103 Readiness Note

Status: complete static documentation/probe consolidation
Date: 2026-06-04
Scope: `physics-script-static-contract-wave1103`

Wave1103 consolidated the saved PhysicsScript Ghidra evidence into `reverse-engineering/binary-analysis/physics-script-static-contract.md` and added a focused probe for the contract/mirror/index/package wiring. This wave made no Ghidra mutation, no executable-byte change, no BEA launch, and no installed-game or runtime-file mutation.

Static contract anchors:

| Area | Evidence |
| --- | --- |
| Manager lifecycle | `0x0042e880 CPhysicsScript__Create`, `0x0042e8f0 CPhysicsScript__Destroy`, `0x0042e950 CPhysicsScript__Load`, `0x0042ea60 CPhysicsScript__Update`, and `0x0042eb90 CPhysicsScript__CreateStatement`. |
| Global/debug paths | `0x0066e99c g_pPhysicsScript`, `0x0062568c [maintainer-local-source-export-root]\CPhysicsScript.cpp`, and `0x00625818 [maintainer-local-source-export-root]\CPhysicsScriptStatements.cpp`. |
| Load contract | Wave1043 statement/value-list loaders from `0x0042f2b0 CUnitStatement__LoadFromMemBuffer` through `0x00431a10 CPhysicsHazardValueList__LoadFromMemBuffer`, with `CPhysicsScriptStatements__CreateStatementType2` through `CPhysicsScriptStatements__CreateStatementType10`. |
| Create/recurse contract | Wave1047 create/recurse rows from `0x0042ede0 CUnitStatement__CreateUnitAndRecurse` through `0x00431760 CHazardStatement__CreateHazardAndRecurse`, including `DAT_008553fc` and `CStatementChain__InvokeVFunc04OnNodes`. |
| Registry/apply roots | `DAT_008553f4`, `DAT_008553f8`, `DAT_00855400`, `DAT_00855404`, `DAT_00855408`, `Fenrir Main Gun`, and `Fenrir`. |
| Lifetime | Wave950 statement destructor chain plus Wave1040 value-list scalar-deleting destructor correction to `CDXMemoryManager__Free(&DAT_009c3df0, this)` through `0x00549220`. |

Read-back sources:

- Wave1019 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-211749_post_wave1019_physics_script_manager_lifecycle_review_verified`.
- Wave1043 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-100128_post_wave1043_physics_statement_load_review_verified`.
- Wave1047 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-124915_post_wave1047_physics_statement_create_recurse_review_verified`.
- Latest completed Ghidra review backup remains Wave1100: `[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

Current dashboard context: static Ghidra function-quality closure `6410/6410 = 100.00%`; commentless / exact-undefined / `param_N` debt `0 / 0 / 0`; expanded post-100 static surface `1560/1560 = 100.00%`; Wave911 focused `812/1408 = 57.67%`; Wave911 top-500 `500/500 = 100.00%`.

What this proves:

- The PhysicsScript manager, statement-family, loader, create/recurse, registry/apply, and lifetime evidence is now consolidated as a single static contract.
- The contract is linked from the binary-analysis indexes and function owner docs.
- The mirror and package-script wiring are machine-checked by `tools/physics_script_static_contract_probe.py`.

What remains unproven:

- Runtime PhysicsScript behavior.
- Serialized physics-script file-format completeness.
- Exact statement/value-list/concrete record layouts.
- Exact source-body identity.
- MissionScript or resource-script outcome behavior.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.
