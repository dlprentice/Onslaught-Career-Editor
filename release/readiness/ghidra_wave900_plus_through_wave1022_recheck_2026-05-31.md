# Ghidra Wave900+ Through Wave1022 Recheck

Status: complete local validation
Date: 2026-05-31

This gate extends the Wave900+ structural static re-audit evidence sweep through Wave1022 (`object-lifecycle-dtor-review-wave1022`).

Validation:

- `npm run test:ghidra-object-lifecycle-dtor-review-wave1022`
- `npm run test:ghidra-wave900-plus-through-wave1022-recheck`
- Expected scope: Wave1022 focused probe/readiness/evidence/backup extension plus the prior Wave900-Wave1021 gate.
- Current queue closure remains `6238/6238 = 100.00%` with 0 commentless, 0 exact-undefined signatures, and 0 `param_N` signatures.
- Wave1022 saves two owner-prefix normalizations: `0x004bfd80 CSpawnerThng__scalar_deleting_dtor` and `0x004bfed0 CSpawnerThng__dtor_base`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-230345_post_wave1022_object_lifecycle_dtor_review_verified`.

This is structural static evidence validation only. Runtime object cleanup behavior, exact layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

Probe token anchor: Wave1022; object-lifecycle-dtor-review-wave1022; 0x004bfd80 CSpawnerThng__scalar_deleting_dtor; 0x004bfed0 CSpawnerThng__dtor_base; 0x004bfe10 CRocket__dtor_base; 0x004bfe70 CWaypoint__dtor_base; 0x004bff40 CSphereTrigger__dtor_base; 0x004c0000 CEscapePod__dtor_base; 539/1408 = 38.28%; 768/1493 = 51.44%; 467/500 = 93.40%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-230345_post_wave1022_object_lifecycle_dtor_review_verified; renamed=2.
