# Wave1203 PhysicsScript Registry/Apply Residual Current-Risk Review Readiness Note

Status: complete read-only static evidence
Date: 2026-06-07
Scope: `wave1203-physics-script-registry-apply-residual-current-risk-review`

Wave1203 re-read `7 PhysicsScript registry/apply residual current-risk rows` from the active Wave1108 current-risk denominator with fresh Ghidra metadata, tag, xref, instruction, and decompile exports. Codex read-only consult used; no Cursor/Composer. The wave made no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.

Read-back evidence:

- Metadata rows: `7`
- Tag rows: `7`
- Xrefs: `10 xref rows`
- Instructions: `902 instruction rows`
- Decompile: `7 decompile rows`
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-005927_post_wave1203_physics_script_registry_apply_residual_current_risk_review_verified`

Measured status:

| Track | Value |
| --- | ---: |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Corrected current-risk reviewed rows | `1062/1179 = 90.08%` |
| Remaining active focused work | `117` |
| Current risk candidates | `6166` |
| Current focused candidates | `1141` |
| Live regenerated current focused candidates | `1141` |

Representative anchors: `CComponent__CreateWeaponComponent`, `CPhysicsUnitValueList__LoadFromMemBuffer`, `CSpawnerData__CreateAndRegisterByName`, `CRoundGridOfFear__ApplyToRoundByName`, `CSpawnerBasedOn__ApplyToSpawnerByName`, `CSpawnerUnit__ApplyToSpawnerByName`, `CExplosionBasedOn__ApplyToExplosionByName`, `DAT_008553f0`, `DAT_008553f4`, `DAT_008553f8`, `CWarspite__Init`, and `CPhysicsScriptStatements__CreateStatementType2`.

Accounting boundary: active current-risk progress uses unique-address accounting from `static-reaudit-current-risk-ledger.json`; the legacy additive counter is deprecated (`1093/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; not Wave911 reconstruction. Active target remains `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`.

Probe token anchor: current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 117; current risk candidates: 6166; fresh Ghidra export; read-only review; Codex read-only consult used; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`.

Boundary: this proves static PhysicsScript registry/apply metadata/decompile/xref evidence only. Runtime PhysicsScript behavior, runtime registry/apply behavior, serialized file-format completeness, exact layouts, exact source-body identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof. Static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference.
