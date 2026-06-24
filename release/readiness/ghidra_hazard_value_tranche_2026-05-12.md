# Ghidra Hazard Value Tranche - 2026-05-12

Status: GREEN static Ghidra correction evidence.

## Scope

Wave 342 continued the `CPhysicsScriptStatements.cpp` static re-audit after the feature-value tranche. It saved names, signatures, comments, and tags for eight hazard-value targets.

The pass recovered three missing function boundaries in the hazard-value family, hardened the type-9 hazard value factory, and corrected stale hazard constructor/vfunc labels to destructor and apply-helper evidence.

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x0043c0b0` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType9(int valueType)` | Hardened the bounded type-9 hazard value factory over ids `0x1..0x4`. |
| `0x0043c1a0` / `0x0043c280` | `CHazardScalar14__ApplyToHazardByName` / `CHazardScalar18__ApplyToHazardByName` | Recovered offset-backed scalar apply helpers for hazard record fields `+0x14` and `+0x18`; scalar field semantics remain unproven. |
| `0x0043c230` / `0x0043c250` / `0x0043c310` | `CPhysicsHazardValueLeaf__shared_scalar_deleting_dtor`, `CPhysicsHazardValue__scalar_deleting_dtor`, and `CPhysicsHazardValue__dtor_base` | Corrected stale constructor/vfunc labels and recovered the base scalar-deleting wrapper for the hazard-value destructor family. |
| `0x0043c320` / `0x0043c410` | `CHazardNoise__ApplyToHazardByName` / `CHazardEffect__ApplyToHazardByName` | Corrected stale vfunc labels to owned-string hazard apply helpers for record fields `+0xc` and `+0x8`. |

## Evidence

- Initial read-only metadata, decompile, xref, instruction, tag, and vtable-slot exports selected the hazard-value targets and recovered three missing vtable-target function boundaries.
- `tools/ApplyHazardValueTranche.java` dry/apply reported `targets=8`, `failed=0`, and apply reported `changed_or_would_change=8` with `REPORT: Save succeeded`.
- Final read-back verified `8/8` metadata rows, `8/8` decompile exports, `12` xref rows, `296` instruction rows, `8/8` tag rows, and `25` vtable-slot rows for the checked vtable targets.
- `py -3 tools\ghidra_hazard_value_tranche_probe_test.py` passed `3/3`; `py -3 -m py_compile tools\ghidra_hazard_value_tranche_probe.py tools\ghidra_hazard_value_tranche_probe_test.py` passed.
- `cmd.exe /c npm run test:ghidra-hazard-value-tranche` passed against the saved read-back artifacts.
- The refreshed whole-database queue reports `5941` functions, `1022` commented functions, `4919` commentless functions, `1975` undefined signatures, and `2135` `param_N` signatures.
- The post-mutation live Ghidra backup was verified at `G:\GhidraBackups\BEA_20260512_161208_post_wave342_verified` with `19` files, `152537991` bytes, and `DiffCount=0`.

## Claim Boundary

This is saved static Ghidra boundary/name/signature/comment/tag evidence only. It improves the current hazard-value family labels, but it does not prove exact source identities for every helper, concrete hazard or value class layouts, scalar or string field semantics, local variable recovery, structure typing, runtime physics-script behavior, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/hazard-values-wave342/current/`.
