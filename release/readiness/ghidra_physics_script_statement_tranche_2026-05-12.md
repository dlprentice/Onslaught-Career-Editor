# Ghidra PhysicsScript Statement Tranche - 2026-05-12

Status: GREEN static Ghidra correction evidence.

## Scope

This wave revisited the `CPhysicsScriptStatements.cpp` statement-family region immediately after the `CPhysicsScript` manager tranche. Fresh saved-project metadata, decompile, xref, instruction, and tag read-back showed that several prior labels were stale or were sitting on value-list helper bodies rather than top-level statement bodies.

The wave recovered `10` missing function boundaries and saved names, signatures, comments, and tags for `35` statement-family targets:

- `CUnitStatement` plus `CPhysicsUnitValueList`
- `CWeaponStatement` plus `CPhysicsWeaponValueList`
- `CWeaponModeStatement` plus `CPhysicsWeaponModeValueList`
- `CRoundStatement` plus `CPhysicsRoundValueList`
- shared `CPhysicsScriptStatement` destructor wrappers

## Corrected Boundaries

| Address | Saved name | Evidence summary |
| --- | --- | --- |
| `0x0042ede0` | `CUnitStatement__CreateUnitAndRecurse` | Recovered missing statement update boundary; creates/registers UnitAI context and recurses into child statements. |
| `0x0042f230` | `CUnitStatement__GetSerializedSize` | Recovered top-level unit-statement serialized-size boundary. |
| `0x0042f2b0` | `CUnitStatement__LoadFromMemBuffer` | Recovered unit-statement load boundary. |
| `0x0042f580` | `CPhysicsScriptStatement__scalar_deleting_dtor` | Recovered base statement scalar-deleting destructor wrapper. |
| `0x0042f700` | `CWeaponStatement__GetSerializedSize` | Recovered top-level weapon-statement serialized-size boundary. |
| `0x0042f780` | `CWeaponStatement__LoadFromMemBuffer` | Recovered weapon-statement load boundary. |
| `0x0042fc20` | `CWeaponModeStatement__GetSerializedSize` | Recovered top-level weapon-mode-statement serialized-size boundary. |
| `0x0042fca0` | `CWeaponModeStatement__LoadFromMemBuffer` | Recovered weapon-mode-statement load boundary. |
| `0x00430190` | `CRoundStatement__GetSerializedSize` | Recovered top-level round-statement serialized-size boundary. |
| `0x00430210` | `CRoundStatement__LoadFromMemBuffer` | Recovered round-statement load boundary. |

## Corrected Labels

- `0x0042f280` is now `CPhysicsUnitValueList__GetSerializedSize`, not a `CUnitAI` recursive-size helper.
- `0x0042f3d0`, `0x0042f8a0`, and `0x0042fdc0` are value-list load helpers, not constructor-like bodies.
- `0x0042f4b0`, `0x0042f980`, and `0x0042fea0` are scalar-deleting destructor wrappers for value-list nodes.
- `0x0042f5b0`, `0x0042fa40`, and `0x0042ff60` are top-level create-and-recurse statement update bodies.
- `0x0042f750`, `0x0042fc70`, and `0x004301e0` are value-list serialized-size helpers, not top-level statement size bodies.
- `0x0042f510`, `0x0042f9e0`, and `0x0042ff00` are destructor bodies, not constructor-like bodies.

## Evidence

- `CreateFunctionsFromAddressList.java` dry run reported `targets=10`, `would_create=10`, `failed=0`.
- `CreateFunctionsFromAddressList.java` apply reported `created=10`, `renamed=10`, `failed=0`, with `REPORT: Save succeeded`.
- `ApplyPhysicsScriptStatementTranche.java` dry run reported `updated=0 skipped=35 renamed=0 missing=0 bad=0`.
- `ApplyPhysicsScriptStatementTranche.java` apply reported `updated=35 skipped=0 renamed=20 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Final read-back verified `35/35` metadata rows, `35/35` decompile exports, `57` xref rows, `7735` instruction rows, and `35/35` tag rows.
- `cmd.exe /c npm run test:ghidra-physics-script-statement-tranche` passed against the saved read-back artifacts.
- The refreshed whole-database queue reports `5894` functions, `858` commented functions, `5036` commentless functions, `1983` undefined signatures, and `2244` `param_N` signatures.
- The actual live Ghidra project was copied to `G:\GhidraBackups\BEA_20260512_054704_post_wave331_verified`; verification compared `19` files, `151849863` bytes, and reported `DiffCount=0`.

## Claim Boundary

This is saved static Ghidra boundary/name/signature/comment/tag evidence only. It does not prove exact source body identity, complete concrete class layouts, local variable recovery, structure typing, every adjacent PhysicsScript subtype, runtime physics-script behavior, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/physics-script-statements-wave331/current/`.
