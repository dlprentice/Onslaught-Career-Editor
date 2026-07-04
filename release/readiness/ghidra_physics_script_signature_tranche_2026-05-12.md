# Ghidra PhysicsScript Signature Tranche - 2026-05-12

Status: GREEN static Ghidra correction evidence.

## Scope

This wave revisited the already named `CPhysicsScript` manager cluster after fresh saved-project metadata, decompile, xref, instruction, and tag read-back. It updated saved Ghidra signatures, comments, and tags for five functions:

- `0x0042e880` `CPhysicsScript__Create`
- `0x0042e8f0` `CPhysicsScript__Destroy`
- `0x0042e950` `CPhysicsScript__Load`
- `0x0042ea60` `CPhysicsScript__Update`
- `0x0042eb90` `CPhysicsScript__CreateStatement`

No function names were changed. The saved signatures now model the manager lifecycle helpers as `void __cdecl` where appropriate, `CPhysicsScript__Load` as `bool __cdecl CPhysicsScript__Load(void * memBuffer)`, and the statement factory as `void * __cdecl CPhysicsScript__CreateStatement(int statementType)`.

## Evidence

- `tools/ApplyPhysicsScriptSignatureTranche.java` dry run: `updated=0 skipped=5 renamed=0 missing=0 bad=0`.
- `tools/ApplyPhysicsScriptSignatureTranche.java` apply: `updated=5 skipped=0 renamed=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Final read-back verified `5/5` metadata rows, `5/5` decompile exports, `5` xref rows, `425` instruction rows, and `5/5` tag rows.
- `cmd.exe /c npm run test:ghidra-physics-script-signature-tranche` passed against the saved read-back artifacts after the queue refresh.
- The refreshed whole-database queue reports `5884` functions, `823` commented functions, `5061` commentless functions, `1983` undefined signatures, and `2269` `param_N` signatures.
- The actual live Ghidra project was copied to `[maintainer-local-ghidra-backup-root]\BEA_20260512_041459_post_wave330_verified`; verification compared `19` files, `151751559` bytes, and reported `DiffCount=0`.

## Claim Boundary

This is saved static Ghidra signature/comment/tag evidence only. It does not prove runtime physics-script behavior, exact source body identity, complete statement subtype names or layouts, local variable recovery, structure typing, BEA launch, game patching, asset or save mutation, or rebuild parity.

Raw machine-readable proof remains under ignored `subagents/ghidra-static-reaudit/physics-script-wave330/current/`.
