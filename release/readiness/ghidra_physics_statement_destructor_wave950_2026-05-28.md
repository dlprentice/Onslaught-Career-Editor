# Ghidra Physics Statement Destructor Wave950 Readiness Note

Status: complete read-only static evidence
Date: 2026-05-28
Scope: `physics-statement-destructor-wave950`

Mutation status: no mutation.

Wave950 re-reviewed the `CPhysicsScriptStatements.cpp` top-level statement destructor chain after Wave949. The pass was read-only: no Ghidra mutation, no rename, no signature change, no comment change, no function-boundary change, no executable-byte change, and no BEA launch.

Primary targets:

| Address | Evidence |
| --- | --- |
| `0x0042f4f0 CUnitStatement__scalar_deleting_dtor` | Vtable DATA xref `0x005d9878`; calls `CUnitStatement__dtor`, checks delete flag, and frees through `CDXMemoryManager__Free`. |
| `0x0042f510 CUnitStatement__dtor` | Called from `0x0042f4f3`; installs the derived vtable, deletes child pointer `+0x10c` through vtable slot 0, then restores base statement vtable `0x005d9894`. |
| `0x0042f570 CPhysicsScriptStatement__dtor` | Base statement destructor reached from nine SEH unwind cleanup refs; restores base statement vtable `0x005d9894`. |
| `0x0042f9c0 CWeaponStatement__scalar_deleting_dtor` / `0x0042f9e0 CWeaponStatement__dtor` | Vtable DATA xref `0x005d9850`; paired destructor follows the same child-`+0x10c` release and base-vtable restore pattern. |
| `0x0042fee0 CWeaponModeStatement__scalar_deleting_dtor` / `0x0042ff00 CWeaponModeStatement__dtor` | Vtable DATA xref `0x005d9864`; paired destructor follows the same child-`+0x10c` release and base-vtable restore pattern. |
| `0x00430450 CRoundStatement__scalar_deleting_dtor` / `0x00430470 CRoundStatement__dtor` | Vtable DATA xref `0x005d983c`; paired destructor follows the same child-`+0x10c` release and base-vtable restore pattern. |
| `0x00430920 CSpawnerStatement__scalar_deleting_dtor` / `0x00430940 CSpawnerStatement__dtor` | Vtable DATA xref `0x005d9828`; paired destructor follows the same child-`+0x10c` release and base-vtable restore pattern. |
| `0x00430da0 CExplosionStatement__scalar_deleting_dtor` / `0x00430dc0 CExplosionStatement__dtor` | Vtable DATA xref `0x005d9814`; paired destructor follows the same child-`+0x10c` release and base-vtable restore pattern. |
| `0x00431290 CComponentStatement__scalar_deleting_dtor` / `0x004312b0 CComponentStatement__dtor` | Vtable DATA xref `0x005d9800`; paired destructor follows the same child-`+0x10c` release and base-vtable restore pattern. |
| `0x004316e0 CFeatureStatement__scalar_deleting_dtor` / `0x00431700 CFeatureStatement__dtor` | Vtable DATA xref `0x005d97ec`; paired destructor follows the same child-`+0x10c` release and base-vtable restore pattern. |
| `0x00431b30 CHazardStatement__scalar_deleting_dtor` / `0x00431b50 CHazardStatement__dtor` | Vtable DATA xref `0x005d97d8`; paired destructor follows the same child-`+0x10c` release and base-vtable restore pattern. |

Read-back evidence:

- Primary exports: 19 metadata rows, 19 tag rows, 27 xref rows, 308 instruction rows, and 19 decompile rows.
- Context exports: 31 metadata rows, 31 tag rows, 66 xref rows, 4566 instruction rows, and 31 decompile rows.
- Vtable export: 13 vtable anchors and 520 slot rows, with scalar-deleting statement destructor slots present at `0x005d9878`, `0x005d9850`, `0x005d9864`, `0x005d983c`, `0x005d9828`, `0x005d9814`, `0x005d9800`, `0x005d97ec`, and `0x005d97d8`.
- Wave911 focused re-audit progress after Wave950 is `266/1408 = 18.89%`.
- Static export-contract function-quality closure remains `6150/6150 = 100.00%`.
- Verified read-only backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-081335_post_wave950_physics_statement_destructor_review_verified`, 19 files, 173542279 bytes, `DiffCount=0`.

What remains unproven:

- Exact source method identity.
- Concrete statement/value/list layouts.
- Runtime physics-script load, apply, and destruction behavior.
- Runtime allocator behavior.
- BEA patching behavior.
- Rebuild parity.
