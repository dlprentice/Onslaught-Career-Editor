# Wave1203 PhysicsScript Registry/Apply Residual Current-Risk Review

Status: complete read-only static evidence pending validation, commit, and push
Date: 2026-06-07
Tag: `wave1203-physics-script-registry-apply-residual-current-risk-review`

Wave1203 re-read `7 PhysicsScript registry/apply residual current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator. Codex read-only consult recommended this coherent PhysicsScript registry/apply cluster; Codex root made the final selection and verified fresh Ghidra evidence.

Representative anchors:

| Address | Name | Evidence |
| --- | --- | --- |
| `0x00427dd0` | `CComponent__CreateWeaponComponent` | Compares component/config names against `Fenrir Bomb Launcher`, `Fenrir Main Gun`, and `Carrier Health Pad`, allocates `0x60` byte AI/weapon component records, calls `CWarspite__Init`, and stores the result at `this+0x13c`. |
| `0x0042f3d0` | `CPhysicsUnitValueList__LoadFromMemBuffer` | Reads child statement type and serialized size, dispatches `CPhysicsScriptStatements__CreateStatementType2` load slot `+0xc` when present, skips unknown payload bytes otherwise, and recursively loads the next node. |
| `0x00430510` | `CSpawnerData__CreateAndRegisterByName` | Creates a `0x3c` spawner-data-like record by name and appends it to `DAT_008553f4`. |
| `0x00438b40` | `CRoundGridOfFear__ApplyToRoundByName` | Searches `DAT_008553f0` by round name and writes `ROUND(this+0x8)` into the round record `+0x58`. |
| `0x00439e70` | `CSpawnerBasedOn__ApplyToSpawnerByName` | Searches `DAT_008553f4` by target spawner and source/base name, then copies selected spawner fields and owned string state. |
| `0x0043a080` | `CSpawnerUnit__ApplyToSpawnerByName` | Searches `DAT_008553f4` and replaces/copies the owned unit string into spawner record `+0x4`. |
| `0x0043abd0` | `CExplosionBasedOn__ApplyToExplosionByName` | Searches `DAT_008553f8` by target explosion and source/base name, then copies selected owned effect/sound strings and scalar fields. |

Fresh Ghidra export evidence:

- `7` metadata rows.
- `7` tag rows.
- `10 xref rows`.
- `902 instruction rows`.
- `7 decompile rows`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-005927_post_wave1203_physics_script_registry_apply_residual_current_risk_review_verified`.

Mutation status: read-only review. The wave made no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.

Accounting:

- Static Ghidra function-quality closure remains `6411/6411 = 100.00%`.
- Commentless / exact-undefined / `param_N` debt remains `0 / 0 / 0`.
- Corrected active current-risk progress is `1062/1179 = 90.08%`.
- Remaining active focused work: `117`.
- Current risk candidates: `6166`.
- Current focused candidates: `1141`.
- Live regenerated current focused candidates: `1141`.
- The legacy additive counter is deprecated (`1093/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5.
- Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; this is not Wave911 reconstruction.
- Active target remains `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`.

Boundary: this proves fresh static Ghidra metadata/tag/xref/instruction/decompile read-back for the listed PhysicsScript registry/apply rows only. Runtime PhysicsScript behavior, runtime registry/apply behavior, serialized file-format completeness, exact layouts, exact source-body identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Probe token anchor: Wave1203; wave1203-physics-script-registry-apply-residual-current-risk-review; 7 PhysicsScript registry/apply residual current-risk rows; 1062/1179 = 90.08%; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 117; current risk candidates: 6166; fresh Ghidra export; read-only review; no rename; no signature change; no comment change; no tag change; no function-boundary change; no executable-byte change; Codex read-only consult used; CComponent__CreateWeaponComponent; CPhysicsUnitValueList__LoadFromMemBuffer; CSpawnerData__CreateAndRegisterByName; CRoundGridOfFear__ApplyToRoundByName; CSpawnerBasedOn__ApplyToSpawnerByName; CSpawnerUnit__ApplyToSpawnerByName; CExplosionBasedOn__ApplyToExplosionByName; DAT_008553f0; DAT_008553f4; DAT_008553f8; CWarspite__Init; CPhysicsScriptStatements__CreateStatementType2; 0 / 0 / 0; 6411/6411 = 100.00%; 10 xref rows; 902 instruction rows; 7 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260607-005927_post_wave1203_physics_script_registry_apply_residual_current_risk_review_verified; static-reaudit-current-risk-ledger.json; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.
