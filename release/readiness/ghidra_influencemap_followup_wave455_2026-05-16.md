# Ghidra InfluenceMap Follow-Up Wave455 Evidence

Date: 2026-05-16

## Scope

Wave455 saved Ghidra name/signature/comment/tag corrections for `8` older InfluenceMap-flavored follow-up entries:

`0x004ad7f0`, `0x004bf9e0`, `0x004d30d0`, `0x004d38c0`, `0x004d39d0`, `0x004d3a00`, `0x0050b930`, and `0x0050b950`.

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave455-influencemap-followup-current/`
- Apply script: `tools/ApplyInfluenceMapFollowupWave455.java`
- Probe: `tools/ghidra_influencemap_followup_wave455_probe.py`
- Test alias: `npm run test:ghidra-influencemap-followup-wave455`
- Dry summary: `updated=0 skipped=8 created=0 would_create=0 renamed=0 would_rename=5 missing=0 bad=0`
- Apply summary: `updated=8 skipped=0 created=0 would_create=0 renamed=5 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=8 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports verified `8` metadata rows, `8` tag rows, `13` xref rows, `8` decompile exports, and `1032` focused instruction rows.
- Revalidated InfluenceMap-related helpers: `CInfluenceMap__SetTrackedThingAndClearCachedObject`, `OID__InitInfluenceMapObject`, `CInfluenceMap__AccumulateThingFlags`, `CInfluenceMapManager__scalar_deleting_dtor`, and `CInfluenceMapManager__dtor`.
- Corrected stale InfluenceMap ownership for `0x004d38c0` to `CUnit__TryDestroyedCleanupAndResetDeploymentGraph`.
- Corrected stale InfluenceMap ownership for `0x004d39d0` and `0x004d3a00` to `CPolyBucket__InitFields` and `CPolyBucket__FreeBuffers`.
- Queue after refresh: `6057` functions, `1997` commented, `4060` commentless, `1732` undefined signatures, `1668` `param_N` signatures.
- Current telemetry proxies: comment-backed `1997/6057 = 32.97%`; strict comment-plus-clean-signature `1934/6057 = 31.93%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260516-144540_post_wave455_influencemap_followup_verified` (`19` files, `156765063` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Boundary

This is static retail-binary evidence only. Runtime InfluenceMap AI behavior, CUnit cleanup lifecycle behavior, PolyBucket render/collision behavior, concrete layouts, exact source identities, BEA launch behavior, game patching, and rebuild parity remain unproven.
