# Ghidra Explosion Value Tranche - 2026-05-12

Status: GREEN static Ghidra correction evidence.

## Scope

Wave 340 continued the `CPhysicsScriptStatements.cpp` static re-audit after the spawner-value tranche. It saved names, signatures, comments, and tags for twenty explosion-value targets.

The pass recovered eight missing function boundaries in the explosion-value family, hardened the type-7 explosion value factory, and corrected stale explosion constructor/vfunc labels to destructor and apply-helper evidence.

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x0043a860` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType7(int valueType)` | Hardened the bounded type-7 explosion value factory over ids `0x1..0xf`. |
| `0x0043abd0` | `void __thiscall CExplosionBasedOn__ApplyToExplosionByName(void * this, char * explosionName)` | Resolves the target and source/base explosion records through `DAT_008553f8` context before copying selected fields. |
| `0x0043aea0` / `0x0043af10` | `CExplosionBasedOn__CopySoundString28` / `CExplosionBasedOn__CopyWaterSoundString2C` | Hardened string-copy helpers for sound and water-sound fields. |
| `0x0043af80` / `0x0043af90` | `CPhysicsExplosionValue__dtor_base` / `CPhysicsExplosionValue__scalar_deleting_dtor` | Corrected stale constructor-like evidence to destructor-base and recovered adjacent scalar-deleting wrapper. |
| `0x0043afc0` / `0x0043b0b0` / `0x0043b1c0` / `0x0043b2b0` | explosion effect string apply helpers | Hardened air, ground, water, and unit effect apply helpers. |
| `0x0043b3a0` / `0x0043b430` / `0x0043b4c0` / `0x0043b550` / `0x0043b5e0` / `0x0043b670` / `0x0043b700` | explosion scalar apply helpers | Recovered offset-backed scalar apply helper boundaries for explosion record fields `+0x34`, `+0x38`, `+0x3c`, `+0x44`, `+0x48`, `+0x4c`, and `+0x40`. |
| `0x0043b790` / `0x0043b880` | `CExplosionSound__ApplyToExplosionByName` / `CExplosionWaterSound__ApplyToExplosionByName` | Hardened sound and water-sound apply helpers. |
| `0x0043b970` | `void * __thiscall CPhysicsExplosionValueLeaf__shared_scalar_deleting_dtor(void * this, int flags)` | Corrected stale vfunc-slot label to shared leaf scalar-deleting destructor wrapper evidence. |

## Evidence

- Initial read-only metadata, decompile, xref, instruction, tag, and vtable-slot exports selected the explosion-value targets and recovered eight missing vtable-target function boundaries.
- `tools/ApplyExplosionValueTranche.java` dry/apply reported `targets=20`, `failed=0`, and apply reported `changed_or_would_change=20` with `REPORT: Save succeeded`.
- Final read-back verified `20/20` metadata rows, `20/20` decompile exports, `35` xref rows, `3380` instruction rows, `20/20` tag rows, and `80` vtable-slot rows for the checked vtable targets.
- `py -3 tools\ghidra_explosion_value_tranche_probe_test.py` passed `3/3`; `py -3 -m py_compile tools\ghidra_explosion_value_tranche_probe.py tools\ghidra_explosion_value_tranche_probe_test.py` passed.
- `cmd.exe /c npm run test:ghidra-explosion-value-tranche` passed against the saved read-back artifacts.
- An initial focused probe expectation had two adjacent scalar vtable entries swapped; the read-back TSV showed `0x005da6ec` maps to `CExplosionScalar48__ApplyToExplosionByName` and `0x005da700` maps to `CExplosionScalar4C__ApplyToExplosionByName`, so the probe was corrected to match the saved Ghidra read-back.
- The refreshed whole-database queue reports `5932` functions, `1003` commented functions, `4929` commentless functions, `1977` undefined signatures, and `2143` `param_N` signatures.
- The post-mutation live Ghidra backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260512_143022_post_wave340_verified` with `19` files, `152505223` bytes, and `DiffCount=0`.

## Claim Boundary

This is saved static Ghidra boundary/name/signature/comment/tag evidence only. It improves the current explosion-value family labels, but it does not prove exact source identities for every helper, concrete explosion or value class layouts, scalar field semantics, local variable recovery, structure typing, runtime physics-script behavior, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/explosion-values-wave340/current/`.
