# Ghidra PhysicsScript Statement Tranche 2 - 2026-05-12

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x004309e0` → `ExplosionDefinition__CreateAndRegisterByName` (was `CExplosion__CreateAndRegisterByName`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: GREEN static Ghidra correction evidence.

## Scope

This wave continued the saved-Ghidra re-audit of the `CPhysicsScriptStatements.cpp` statement-family region immediately after the Round tranche. Fresh metadata, decompile, xref, instruction, and tag read-back showed more top-level statement boundaries and value-list helpers that needed separation.

The wave recovered `6` missing function boundaries and saved names, signatures, comments, and tags for `31` targets:

- `CRoundStatement` tail and `CPhysicsRoundValueList`
- `CSpawnerStatement`, `CSpawnerData`, and `CPhysicsSpawnerValueList`
- `CExplosionStatement` and `CPhysicsExplosionValueList`
- `CComponentStatement`, `CPhysicsComponentValueList`, and the adjacent statement-chain dispatcher

## Corrected Boundaries

| Address | Saved name | Evidence summary |
| --- | --- | --- |
| `0x00430660` | `CSpawnerStatement__GetSerializedSize` | Recovered top-level spawner-statement serialized-size boundary. |
| `0x004306e0` | `CSpawnerStatement__LoadFromMemBuffer` | Recovered top-level spawner-statement load boundary. |
| `0x00430ae0` | `CExplosionStatement__GetSerializedSize` | Recovered top-level explosion-statement serialized-size boundary. |
| `0x00430b60` | `CExplosionStatement__LoadFromMemBuffer` | Recovered top-level explosion-statement load boundary. |
| `0x00430fd0` | `CComponentStatement__GetSerializedSize` | Recovered top-level component-statement serialized-size boundary. |
| `0x00431050` | `CComponentStatement__LoadFromMemBuffer` | Recovered top-level component-statement load boundary. |

## Corrected Labels

- `0x00430330` is now `CPhysicsRoundValueList__LoadFromMemBuffer`, not a constructor-like body.
- `0x00430410`, `0x004308e0`, `0x00430d60`, and `0x00431250` are value-list scalar-deleting destructor wrappers.
- `0x00430450`, `0x00430920`, and `0x00430da0` are statement scalar-deleting destructor wrappers.
- `0x00430470`, `0x00430940`, and `0x00430dc0` are statement destructor bodies.
- `0x004304d0`, `0x004309a0`, and `0x00430e20` are top-level create-and-recurse statement update bodies.
- `0x00430510`, `0x004309e0`, and `0x00430e60` are object registry creation helpers for spawner, explosion, and component data.
- `0x004306b0`, `0x00430b30`, and `0x00431020` are value-list serialized-size helpers, not top-level statement bodies.
- `0x00430800`, `0x00430c80`, and `0x00431170` are value-list load helpers.
- `0x00430fa0` is now `CStatementChain__InvokeVFunc04OnNodes` with a bounded statement-chain dispatcher signature.

## Evidence

- `CreateFunctionsFromAddressList.java` dry run reported `targets=6`, `would_create=6`, and `failed=0`.
- `CreateFunctionsFromAddressList.java` apply reported `created=6`, `renamed=6`, and `failed=0`, with `REPORT: Save succeeded`.
- `ApplyPhysicsScriptStatementTranche2.java` dry run reported `updated=0 skipped=31 renamed=0 missing=0 bad=0`.
- `ApplyPhysicsScriptStatementTranche2.java` apply reported `updated=31 skipped=7 renamed=24 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Final read-back verified `31/31` metadata rows, `31/31` decompile exports, `54` xref rows, `7595` instruction rows, and `31/31` tag rows.
- `cmd.exe /c npm run test:ghidra-physics-script-statement-tranche2` passed against the saved read-back artifacts.
- The refreshed whole-database queue reports `5900` functions, `889` commented functions, `5011` commentless functions, `1983` undefined signatures, and `2219` `param_N` signatures.

## Claim Boundary

This is saved static Ghidra boundary/name/signature/comment/tag evidence only. It does not prove exact source body identity, complete concrete class layouts, local variable recovery, structure typing, every remaining PhysicsScript subtype, runtime physics-script behavior, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/physics-script-statements-wave332/current/`.
