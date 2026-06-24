# Ghidra PhysicsScript Statement Tranche 3 - 2026-05-12

Status: GREEN static Ghidra correction evidence.

## Scope

This wave continued the saved-Ghidra re-audit of the `CPhysicsScriptStatements.cpp` statement-family region immediately after the Component tranche. Fresh metadata, decompile, xref, instruction, and tag read-back showed the Feature/Hazard statement clusters had the same top-level boundary versus value-list split as the earlier Unit/Weapon/Round/Spawner/Explosion/Component families.

The wave recovered `4` missing function boundaries and saved names, signatures, comments, and tags for `21` targets:

- `CComponentStatement` destructor tail.
- `CFeatureStatement` and `CPhysicsFeatureValueList`.
- `CHazardStatement` and `CPhysicsHazardValueList`.
- The adjacent type-2/unit value factory signature/comment boundary.

## Corrected Boundaries

| Address | Saved name | Evidence summary |
| --- | --- | --- |
| `0x00431420` | `CFeatureStatement__GetSerializedSize` | Recovered top-level feature-statement serialized-size boundary. |
| `0x004314a0` | `CFeatureStatement__LoadFromMemBuffer` | Recovered top-level feature-statement load boundary. |
| `0x00431870` | `CHazardStatement__GetSerializedSize` | Recovered top-level hazard-statement serialized-size boundary. |
| `0x004318f0` | `CHazardStatement__LoadFromMemBuffer` | Recovered top-level hazard-statement load boundary. |

## Corrected Labels

- `0x00431290` is now `CComponentStatement__scalar_deleting_dtor`.
- `0x004312b0` is now `CComponentStatement__dtor`.
- `0x00431310` is now `CFeatureStatement__CreateFeatureAndRecurse`.
- `0x00431350` is now `CFeatureStatement__CreateAndRegisterByName`.
- `0x00431470` is now `CPhysicsFeatureValueList__GetSerializedSize`, not a UnitAI helper.
- `0x004315c0` is now `CPhysicsFeatureValueList__LoadFromMemBuffer`.
- `0x004316a0` is now `CPhysicsFeatureValueList__scalar_deleting_dtor`.
- `0x004316e0` is now `CFeatureStatement__scalar_deleting_dtor`.
- `0x00431700` is now `CFeatureStatement__dtor`.
- `0x00431760` is now `CHazardStatement__CreateHazardAndRecurse`.
- `0x004317a0` is now `CHazardStatement__CreateAndRegisterByName`.
- `0x004318c0` is now `CPhysicsHazardValueList__GetSerializedSize`, not a UnitAI helper.
- `0x00431a10` is now `CPhysicsHazardValueList__LoadFromMemBuffer`.
- `0x00431af0` is now `CPhysicsHazardValueList__scalar_deleting_dtor`.
- `0x00431b30` is now `CHazardStatement__scalar_deleting_dtor`.
- `0x00431b50` is now `CHazardStatement__dtor`.
- `0x00431bb0` keeps the saved `CPhysicsScriptStatements__CreateStatementType2` name but now has a bounded `valueType` signature and value-factory comment.

## Evidence

- `CreateFunctionsFromAddressList.java` dry run reported `targets=4`, `would_create=4`, and `failed=0`.
- `CreateFunctionsFromAddressList.java` apply reported `created=4`, `renamed=4`, and `failed=0`, with `REPORT: Save succeeded`.
- `ApplyPhysicsScriptStatementTranche3.java` dry run accepted `21` targets.
- `ApplyPhysicsScriptStatementTranche3.java` apply reported `targets=21`, `changedNames=16`, with `REPORT: Save succeeded`.
- Final read-back verified `21/21` metadata rows, `21/21` decompile exports, `30` xref rows, `5145` instruction rows, and `21/21` tag rows.
- `cmd.exe /c npm run test:ghidra-physics-script-statement-tranche3` passed against the saved read-back artifacts.
- The refreshed whole-database queue reports `5904` functions, `910` commented functions, `4994` commentless functions, `1982` undefined signatures, and `2203` `param_N` signatures.
- The actual live Ghidra project backup after the saved mutation is `G:\GhidraBackups\BEA_20260512_071711_post_wave333_verified` with `19` files, `152046471` bytes, and `DiffCount=0`.

## Claim Boundary

This is saved static Ghidra boundary/name/signature/comment/tag evidence only. It does not prove exact source body identity, complete concrete class layouts, local variable recovery, structure typing, every remaining PhysicsScript subtype, runtime physics-script behavior, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/physics-script-statements-wave333/current/`.
