# PhysicsScript Schema/Parser Proof Plan Readiness Note

Status: schema/parser proof checklist complete, not runtime proof
Date: 2026-06-08
Scope: PhysicsScript parser/spec planning from `physics-script-static-contract.md`

The PhysicsScript schema/parser slice adds a public-safe proof plan at `reverse-engineering/binary-analysis/physics-script-schema-parser-proof-plan.md`. This is not a new static re-audit wave, not a Ghidra mutation, and not a parser-corpus proof result.

Static closeout remains unchanged:

| Track | Current |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Active current-risk focused accounting | `1179/1179 = 100.00%` |
| Remaining active focused work | `0` |

Static anchors retained for the parser/spec checklist:

- `physics-script-static-contract.md` and `physics-script-static-contract-wave1103`.
- `0x0042e950 CPhysicsScript__Load` stream header/token value `0x12`, statement type loop, `-1` terminator, load slot `+0xc`, and unknown-payload skip behavior.
- `0x0042eb90 CPhysicsScript__CreateStatement` observed top-level statement type ids `1..9`.
- `CPhysicsScriptStatements__CreateStatementType2` through `CPhysicsScriptStatements__CreateStatementType10`.
- `CUnitStatement__LoadFromMemBuffer` through `CPhysicsHazardValueList__LoadFromMemBuffer`.
- `CStatementChain__InvokeVFunc04OnNodes`.
- Registry roots `DAT_008553f4`, `DAT_008553f8`, `DAT_00855400`, `DAT_00855404`, `DAT_00855408`, and `DAT_008553fc`.
- Latest completed PhysicsScript Ghidra review backup: `G:\GhidraBackups\BEA_20260607-005927_post_wave1203_physics_script_registry_apply_residual_current_risk_review_verified`.

Corpus requirements for the next executable slice:

- Use copied/app-owned script/resource evidence only.
- Treat the private copied `data/default physics.dat` file shape as corpus input when present; raw bytes, AST/string dumps, hashes, and absolute paths remain in ignored/private evidence.
- Record exact filename spelling from the copied corpus; do not assume `default_physics.dat` if the copied file is `default physics.dat`.
- Keep `MissionScripts/*.msl` separate from PhysicsScript binary parser input.
- Preserve unknown or layout-sensitive payload bytes in ignored evidence and publish only aggregate counts.

What this proves:

- The project has a bounded Schema/parser proof checklist and corpus requirement list for turning the saved PhysicsScript static contract into a copied-corpus parser/spec slice.
- The planned parser proof is constrained to stream framing, statement/value-list record accounting, byte-consumption checks, unknown-skip handling, raw-byte preservation, and public-safe aggregate inventory output.
- The static percentages and current-risk ledgers are unchanged by this planning slice.

What remains separate proof:

- Runtime PhysicsScript behavior.
- MissionScript or resource-script outcome behavior.
- Serialized physics-script file-format completeness.
- Exact statement/value-list/concrete record layouts.
- Exact source-body identity.
- Gameplay outcomes.
- BEA patching behavior.
- Visual QA.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

No mission outcome or serialized completeness claim until corpus proof exists.

No runtime PhysicsScript behavior, exact layouts, mission/resource-script outcomes, BEA patching behavior, rebuild parity, or no-noticeable-difference parity claim.
