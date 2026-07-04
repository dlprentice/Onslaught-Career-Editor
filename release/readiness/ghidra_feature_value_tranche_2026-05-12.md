# Ghidra Feature Value Tranche - 2026-05-12

Status: GREEN static Ghidra correction evidence.

## Scope

Wave 341 continued the `CPhysicsScriptStatements.cpp` static re-audit after the explosion-value tranche. It saved names, signatures, comments, and tags for eleven feature-value targets.

The pass recovered six missing function boundaries in the feature-value family, hardened the type-8 feature value factory, and corrected stale feature constructor/vfunc labels to destructor and apply-helper evidence.

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x0043b990` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType8(int valueType)` | Hardened the bounded type-8 feature value factory over ids `0x1..0x7`. |
| `0x0043bb30` / `0x0043bbf0` | `CFeatureScalar18__ApplyToFeatureByName` / `CFeatureScalar1C__ApplyToFeatureByName` | Recovered scalar apply helpers for feature record fields `+0x18` and `+0x1c`; scalar field semantics remain unproven. |
| `0x0043bc80` / `0x0043bd40` | `CFeatureFlag10__ApplyToFeatureByName` / `CFeatureFlag14__ApplyToFeatureByName` | Recovered flag-style apply helpers that compare the value scalar with `0.0` before writing feature record fields `+0x10` and `+0x14`. |
| `0x0043be00` / `0x0043bbc0` / `0x0043bff0` | `CPhysicsFeatureValue__dtor_base`, `CPhysicsFeatureValue__scalar_deleting_dtor`, and `CPhysicsFeatureValueLeaf__shared_scalar_deleting_dtor` | Corrected stale constructor/vfunc labels to the feature-value destructor family. |
| `0x0043be10` / `0x0043bf00` | `CFeatureMesh__ApplyToFeatureByName` / `CFeatureNoise__ApplyToFeatureByName` | Corrected stale vfunc labels to owned-string apply helpers against the feature record context. |
| `0x0043c010` | `CFeatureTexture__ApplyToFeatureByName` | Recovered the texture apply boundary; it resolves the feature record and calls the existing texture-name/index helper. |

## Evidence

- Initial read-only metadata, decompile, xref, instruction, tag, and vtable-slot exports selected the feature-value targets and recovered six missing vtable-target function boundaries.
- `tools/ApplyFeatureValueTranche.java` dry/apply reported `targets=11`, `failed=0`, and apply reported `changed_or_would_change=11` with `REPORT: Save succeeded`.
- Final read-back verified `11/11` metadata rows, `11/11` decompile exports, `18` xref rows, `1859` instruction rows, `11/11` tag rows, and `40` vtable-slot rows for the checked vtable targets.
- `py -3 tools\ghidra_feature_value_tranche_probe_test.py` passed `3/3`; `py -3 -m py_compile tools\ghidra_feature_value_tranche_probe.py tools\ghidra_feature_value_tranche_probe_test.py` passed.
- `cmd.exe /c npm run test:ghidra-feature-value-tranche` passed against the saved read-back artifacts.
- The refreshed whole-database queue reports `5938` functions, `1014` commented functions, `4924` commentless functions, `1976` undefined signatures, and `2139` `param_N` signatures.
- The post-mutation live Ghidra backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260512_154029_post_wave341_verified` with `19` files, `152505223` bytes, and `DiffCount=0`.

## Claim Boundary

This is saved static Ghidra boundary/name/signature/comment/tag evidence only. It improves the current feature-value family labels, but it does not prove exact source identities for every helper, concrete feature or value class layouts, scalar or flag field semantics, local variable recovery, structure typing, runtime physics-script behavior, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/feature-values-wave341/current/`.
