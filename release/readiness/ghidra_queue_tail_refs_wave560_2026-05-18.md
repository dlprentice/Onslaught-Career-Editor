# Ghidra Queue-Tail Reference Resolver Wave560 Readiness Note

Date: 2026-05-18

Wave560 saved static Ghidra signature/comment/tag evidence for a seven-target queue-tail reference resolver tranche from `0x005113f0` through `0x00511db0`. The bounded probe label for this tranche is `queue-tail reference resolver`.

## Saved Scope

- Signature/comment fixes: `CWeaponRound__SetReaderFromGlobalListByIndex`, `CUnit__GetTypePriorityWeight`, and `CVBufTexture__FindListEntryByPair`.
- Owner/signature corrections: `CFeatureTexture__SetTagListIndexOrMinusOne`, `CWorldPhysicsManager__ResolveWeaponModeStatementRefs`, `CWorldPhysicsManager__ResolveTagDefinitionRefs`, and `CWorldPhysicsManager__ResolveThingOrComponentDefinitionRefs`.

## Evidence

- `ApplyQueueTailRefsWave560.java` dry run: `updated=0 skipped=7 renamed=0 would_rename=4 missing=0 bad=0`.
- Apply: `updated=7 skipped=0 renamed=4 would_rename=0 missing=0 bad=0`.
- Final dry verification: `updated=0 skipped=7 renamed=0 would_rename=0 missing=0 bad=0`.
- Read-back exports: `7` metadata rows, `7` tag rows, `15` xref rows, `637` target instruction rows, `285` focused callsite instruction rows, and `7` decompile rows.
- Focused probe: `tools/ghidra_queue_tail_refs_wave560_probe.py`.
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260518-184900_post_wave560_queue_tail_refs_verified` with `19` files, `159812487` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Queue Telemetry

Post-Wave560 queue refresh:

- Total functions: `6089`
- Commented: `2772`
- Commentless: `3317`
- Exact-undefined signatures: `1513`
- `param_N` signatures: `1194`
- Strict clean-signature proxy: `2718/6089 = 44.64%`

## Limits

This is static retail-binary evidence only. Exact definition schemas, concrete feature/tag/weapon-mode/thing/component/unit cache layouts, source method identities, runtime resolve/spawn-accounting/transform behavior, BEA launch, patching, and rebuild parity remain unproven.
