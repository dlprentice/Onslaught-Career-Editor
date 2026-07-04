# Ghidra World Occupancy / Pathfinding Wave457 Evidence

Date: 2026-05-16

## Scope

Wave457 saved Ghidra name/signature/comment/tag corrections for `13` world occupancy, ExplosionInitThing pathfinding, and static-shadow occupancy targets:

`0x004bc260`, `0x004bc3e0`, `0x004bc480`, `0x004bc510`, `0x004bc6d0`, `0x004bd440`, `0x004bd5c0`, `0x004bd9e0`, `0x004bdf70`, `0x004be050`, `0x004be970`, `0x004bed30`, and `0x004beea0`.

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave457-world-occupancy-current/`
- Apply script: `tools/ApplyWorldOccupancyWave457.java`
- Probe: `tools/ghidra_world_occupancy_wave457_probe.py`
- Test alias: `npm run test:ghidra-world-occupancy-wave457`
- Dry summary: `updated=0 skipped=13 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Initial apply correction: the first apply landed five rows then exposed Ghidra `__thiscall` receiver read-back rendering as `this`; the preserved log is `apply_first_attempt_signature_mismatch.log`.
- Final apply summary: `updated=13 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=13 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports verified `13` metadata rows, `13` tag rows, `115` xref rows, `13` decompile exports plus `index.tsv`, and `8333` focused instruction rows.
- Corrected CWorld occupancy bitplane helpers for init, add/remove unit grid occupancy, bit set/clear, cross-neighbor clearing, footprint rasterization, and bitplane chunk loading.
- Corrected ExplosionInitThing grid/path helpers for segment-block checks, nearest-set-bit search, packed-bit tests, lowest-cost 8-neighbor stepping, and line-of-sight path simplification.
- Corrected `CEngine__BuildStaticShadowVolumesAroundUnit` as the static-shadow helper that samples unit targeting position/radius, terrain shadow height, line volumes, and packed occupancy clears.
- Queue after refresh: `6057` functions, `2018` commented, `4039` commentless, `1730` undefined signatures, `1649` `param_N` signatures.
- Current telemetry proxies: comment-backed `2018/6057 = 33.32%`; strict comment-plus-clean-signature `1955/6057 = 32.28%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260516-155807_post_wave457_world_occupancy_verified` (`19` files, `156830599` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Boundary

This is static retail-binary evidence only. Runtime occupancy behavior, pathing behavior, static-shadow rendering, exact state/layout names, exact source identity, BEA launch behavior, game patching, and rebuild parity remain unproven.
