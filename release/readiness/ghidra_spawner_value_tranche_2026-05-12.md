# Ghidra Spawner Value Tranche - 2026-05-12

Status: GREEN static Ghidra correction evidence.

## Scope

Wave 339 continued the `CPhysicsScriptStatements.cpp` static re-audit after the round-value tail tranche. It saved names, signatures, comments, and tags for twenty-four spawner-value or adjacent shared vtable targets.

The pass recovered seventeen missing function boundaries in the spawner-value family, hardened the type-6 spawner value factory, and corrected two older owner-specific no-op labels to shared behavior names after vtable-slot evidence showed unrelated classes use the same targets.

| Address | Saved state | Evidence summary |
| --- | --- | --- |
| `0x004014c0` | `void __thiscall SharedVFunc__NoOpOneArg_004014c0(void * this, int arg0)` | Supersedes the older frontend-specific label; vtable evidence shows a shared one-argument no-op target. |
| `0x00405930` | `int __thiscall SharedVFunc__ReturnZero_00405930(void * this)` | Supersedes the older controller-specific label; vtable evidence shows a shared return-zero target. |
| `0x00434b60` | `void __thiscall CPhysicsScriptValue__LoadScalarAt08FromMemBuffer(void * this, void * memBuffer)` | Recovered shared scalar load boundary for value objects. |
| `0x004398f0` | `int __fastcall CPhysicsScriptValue__GetOwnedStringAt08SerializedSize(void * this)` | Recovered shared owned-string serialized-size boundary. |
| `0x00439b40` | `void * __cdecl CPhysicsScriptStatements__CreateStatementType6(int valueType)` | Hardened the bounded type-6 spawner value factory. |
| `0x00439e70` | `void __thiscall CSpawnerBasedOn__ApplyToSpawnerByName(void * this, char * spawnerName)` | Applies base-spawner fields after resolving the named spawner record. |
| `0x0043a040` / `0x0043a050` | `CPhysicsSpawnerValue__dtor_base` / `CPhysicsSpawnerValue__scalar_deleting_dtor` | Hardened the base destructor body and recovered the adjacent scalar-deleting wrapper. |
| `0x0043a080` through `0x0043a7b0` | spawner apply helpers | Recovered and named the `CSpawnerUnit`, `Delay`, `Amount`, `Conditions`, `SquadSize`, `SquadDelay`, `SeekDelay`, `Recall`, `MinRange`, `MaxRange`, `PreSpawnDelay`, `PostSpawnDelay`, and `Infinite` apply helpers. |
| `0x0043a840` | `void * __thiscall CPhysicsSpawnerValueLeaf__shared_scalar_deleting_dtor(void * this, int flags)` | Shared leaf scalar-deleting destructor wrapper for spawner value objects. |
| `0x0043b1a0` | `void __thiscall CPhysicsScriptValue__LoadOwnedStringAt08FromMemBuffer(void * this, void * memBuffer)` | Recovered shared owned-string load boundary. |
| `0x004db8c0` | `int __fastcall CPhysicsScriptValue__GetScalarSerializedSize4(void * this)` | Recovered shared scalar-size helper returning the fixed serialized size `4`. |

## Evidence

- Initial read-only exports found missing function boundaries for the spawner-value apply and shared serialization targets, plus vtable evidence for `CSpawnerConditions`, `CSpawnerInfinite`, `CSpawnerBasedOn`, `CSpawnerPostSpawnDelay`, `CSpawnerPreSpawnDelay`, `CSpawnerMaxRange`, `CSpawnerMinRange`, `CSpawnerRecall`, `CSpawnerSeekDelay`, `CSpawnerSquadDelay`, `CSpawnerSquadSize`, `CSpawnerAmount`, `CSpawnerDelay`, `CSpawnerUnit`, and `CPhysicsSpawnerValue`.
- `tools/ApplySpawnerValueTranche.java` dry/apply reported `targets=24`, `changed_or_would_change=23`, and `failed=0`, with `REPORT: Save succeeded` on apply.
- Final read-back verified `24/24` metadata rows, `24/24` decompile exports, `1794` xref rows, `3576` instruction rows, `24/24` tag rows, and `60` vtable-slot rows for the checked vtable targets.
- `py -3 tools\ghidra_spawner_value_tranche_probe_test.py` passed `3/3`; `py -3 -m py_compile tools\ghidra_spawner_value_tranche_probe.py tools\ghidra_spawner_value_tranche_probe_test.py` passed.
- `cmd.exe /c npm run test:ghidra-spawner-value-tranche` passed against the saved read-back artifacts.
- The refreshed whole-database queue reports `5924` functions, `983` commented functions, `4941` commentless functions, `1978` undefined signatures, and `2154` `param_N` signatures.
- The post-mutation live Ghidra backup was verified at `[maintainer-local-ghidra-backup-root]\BEA_20260512_132313_post_wave339_verified` with `19` files, `152341383` bytes, and `DiffCount=0`.

## Claim Boundary

This is saved static Ghidra boundary/name/signature/comment/tag evidence only. It improves the current spawner-value family and shared vtable helper labels, but it does not prove exact source identities for every helper, concrete spawner or value class layouts, local variable recovery, structure typing, runtime physics-script behavior, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/spawner-values-wave339/current/`.
