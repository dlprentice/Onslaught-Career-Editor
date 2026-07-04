# Ghidra CSpawner Type Allowed Wave845 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `spawner-type-allowed-wave845`

Wave845 CSpawner Type Allowed hardened `0x0050f680 CSpawnerThng__IsSpawnTypeAllowed` from `int __cdecl CSpawnerThng__IsSpawnTypeAllowed(int spawn_type)` to `bool __cdecl CSpawnerThng__IsSpawnTypeAllowed(int spawn_type)` after serialized headless dry/apply/read-back with the `spawner-type-allowed-wave845` and `wave845-readback-verified` tags. The pass made no rename, no function-boundary change, and no executable-byte change.

This is compact but important connective spawner infrastructure. The function is reached from `CSpawnerThng__Init` at `0x004e32cc` and `CSpawnerThng__Constructor` at `0x004e39b2`; both callers push a definition type enum from `+0xe0`, call this helper, and then `TEST EAX,EAX` before branching. The body subtracts `4` from `spawn_type`, bounds-checks against `0x14`, dispatches through the jump table at `0x0050f6a4/0x0050f6ac`, returns false for observed values `4 through 0x14 and 0x16 through 0x18`, and returns true for default/out-of-range values plus the unlisted `0x15` slot.

Read-back evidence:

- `ApplyCSpawnerTypeAllowedWave845.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyCSpawnerTypeAllowedWave845.java apply`: `READBACK_OK`, `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyCSpawnerTypeAllowedWave845.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 2 xref rows, 241 instruction-window rows, 98 caller-site instruction rows, 7 context metadata rows, 7 context tag rows, and 1 decompile row.
- Queue after Wave845: 6098 total, 5669 commented, 429 commentless, 0 exact-undefined signatures, 0 `param_N` signatures, comment-backed proxy `5669/6098 = 92.96%`, strict clean-signature proxy `5669/6098 = 92.96%`.
- Next raw commentless row: `0x00510520 CWorldPhysicsManager__ResolveLoadedDefinitionReferences`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-053251_post_wave845_spawner_type_allowed_verified`, 19 files, 171871111 bytes, `DiffCount=0`.

Probe token anchor: Wave845 CSpawner Type Allowed; spawner-type-allowed-wave845; `0x0050f680 CSpawnerThng__IsSpawnTypeAllowed`; `bool __cdecl CSpawnerThng__IsSpawnTypeAllowed(int spawn_type)`; `0x004e32cc`; `0x004e39b2`; `0x0050f6a4/0x0050f6ac`; `4 through 0x14 and 0x16 through 0x18`; `5669/6098 = 92.96%`; `0x00510520 CWorldPhysicsManager__ResolveLoadedDefinitionReferences`; `[maintainer-local-ghidra-backup-root]\BEA_20260525-053251_post_wave845_spawner_type_allowed_verified`.

Boundary note: this wave proves saved static Ghidra metadata/decompile/xref evidence for the CSpawnerThng spawn-type predicate only. Exact enum names, source method identity, concrete spawner/definition field meanings, runtime spawn admission behavior, BEA patching, and rebuild parity remain deferred.
