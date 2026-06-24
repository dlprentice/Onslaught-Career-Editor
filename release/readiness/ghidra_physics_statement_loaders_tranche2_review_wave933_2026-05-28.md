# Ghidra Physics Statement Loaders Tranche2 Review Wave933 Readiness Note

Status: complete read-only static review
Date: 2026-05-28
Scope: `physics-statement-loaders-tranche2-review-wave933`

Wave933 re-reviewed the remaining PhysicsScript top-level/value-list load helpers for spawner, explosion, component, feature, and hazard statement families. The review continued the Wave917 loader pattern and the Wave918 factory context. Wave933 no mutation status: no Ghidra mutation, rename, signature change, function-boundary change, or executable-byte change was warranted.

Primary targets:

| Address | Saved state | Fresh evidence |
| --- | --- | --- |
| `0x004306e0 CSpawnerStatement__LoadFromMemBuffer` | `void __thiscall CSpawnerStatement__LoadFromMemBuffer(void * this, void * memBuffer)` | Vtable DATA ref `0x005d9834`; reads the statement name, allocates `CPhysicsSpawnerValueList`, dispatches `CPhysicsScriptStatements__CreateStatementType6` load slot `+0xc`, skips unknown payload bytes, and recurses through the value-list chain. |
| `0x00430800 CPhysicsSpawnerValueList__LoadFromMemBuffer` | `void __thiscall CPhysicsSpawnerValueList__LoadFromMemBuffer(void * this, void * memBuffer)` | Called by the spawner statement loader and by its own recursive chain; uses type-6 factory context. |
| `0x00430b60 CExplosionStatement__LoadFromMemBuffer` | `void __thiscall CExplosionStatement__LoadFromMemBuffer(void * this, void * memBuffer)` | Vtable DATA ref `0x005d9820`; uses `CPhysicsScriptStatements__CreateStatementType7`. |
| `0x00430c80 CPhysicsExplosionValueList__LoadFromMemBuffer` | `void __thiscall CPhysicsExplosionValueList__LoadFromMemBuffer(void * this, void * memBuffer)` | Called by the explosion statement loader and by its own recursive chain; uses type-7 factory context. |
| `0x00431050 CComponentStatement__LoadFromMemBuffer` | `void __thiscall CComponentStatement__LoadFromMemBuffer(void * this, void * memBuffer)` | Vtable DATA ref `0x005d980c`; uses `CPhysicsScriptStatements__CreateStatementType10`, the component value-family factory. |
| `0x00431170 CPhysicsComponentValueList__LoadFromMemBuffer` | `void __thiscall CPhysicsComponentValueList__LoadFromMemBuffer(void * this, void * memBuffer)` | Called by the component statement loader and by its own recursive chain; uses type-10 factory context. |
| `0x004314a0 CFeatureStatement__LoadFromMemBuffer` | `void __thiscall CFeatureStatement__LoadFromMemBuffer(void * this, void * memBuffer)` | Vtable DATA ref `0x005d97f8`; uses `CPhysicsScriptStatements__CreateStatementType8`. |
| `0x004315c0 CPhysicsFeatureValueList__LoadFromMemBuffer` | `void __thiscall CPhysicsFeatureValueList__LoadFromMemBuffer(void * this, void * memBuffer)` | Called by the feature statement loader and by its own recursive chain; uses type-8 factory context. |
| `0x004318f0 CHazardStatement__LoadFromMemBuffer` | `void __thiscall CHazardStatement__LoadFromMemBuffer(void * this, void * memBuffer)` | Vtable DATA ref `0x005d97e4`; uses `CPhysicsScriptStatements__CreateStatementType9`. |
| `0x00431a10 CPhysicsHazardValueList__LoadFromMemBuffer` | `void __thiscall CPhysicsHazardValueList__LoadFromMemBuffer(void * this, void * memBuffer)` | Called by the hazard statement loader and by its own recursive chain; uses type-9 factory context. |

Context exports covered the type-6 through type-10 factories, paired serialized-size helpers, `0x0043e630 CFlexArray__SkipBytesFromMemBuffer`, and the Wave917 sibling pair `0x00430210 CRoundStatement__LoadFromMemBuffer` / `0x00430330 CPhysicsRoundValueList__LoadFromMemBuffer`.

Evidence:

- Primary exports: 10 metadata rows, 10 tag rows, 25 xref rows, 945 instruction rows, and 10 decompile rows.
- Context exports: 18 metadata rows, 18 tag rows, 31 xref rows, 1305 instruction rows, and 18 decompile rows.
- Composer 2.5 consult independently recommended this tranche as the most coherent Wave933 cluster and expected read-only outcome unless live Ghidra contradicted Wave331-Wave344/Wave917/Wave918 evidence.
- Wave911 focused re-audit progress after Wave933: `140/1408 = 9.94%`.
- Static export-contract closure remains `6113/6113 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260528-003302_post_wave933_physics_statement_loaders_tranche2_review_verified`, 19 files, 173247367 bytes, `DiffCount=0`.

What this proves:

- The saved names, signatures, tags, xrefs, instruction bodies, and decompiles for the ten primary loader rows remain coherent with the paired size helpers, type-6 through type-10 factory dispatch, and the Wave917 sibling loader pattern.
- The loader surface now has a fresh static review for Unit/Weapon/WeaponMode/Round from Wave917 and Spawner/Explosion/Component/Feature/Hazard from Wave933.

What remains unproven:

- Exact serialized physics-script format coverage remains open.
- Concrete statement/value-list/value-object layouts.
- Runtime spawner, explosion, component, feature, hazard, or physics-script behavior.
- Exact source-body identity, BEA patch behavior, and rebuild parity.
