# Ghidra Options Detail Wave466 Evidence

Date: 2026-05-16

## Scope

Wave466 saved Ghidra name/signature/comment/tag corrections for `6` options/detail menu targets:

`0x004ceef0`, `0x004cef30`, `0x004cef50`, `0x004cf030`, `0x004cf8e0`, and `0x004cffd0`.

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave466-options-detail-current/`
- Apply script: `tools/ApplyOptionsDetailWave466.java`
- Probe: `tools/ghidra_options_detail_wave466_probe.py`
- Test alias: `npm run test:ghidra-options-detail-wave466`
- Dry summary: `updated=0 skipped=6 created=0 would_create=0 renamed=0 would_rename=4 missing=0 bad=0`
- Apply summary: `updated=6 skipped=0 created=0 would_create=0 renamed=4 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=6 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports verified `6` metadata rows, `6` tag rows, `10` xref rows, `6` decompile exports plus `index.tsv`, and `222` focused instruction rows.
- Corrected or hardened landscape-detail setter/getter signatures, the tree-detail quality setter, mouse-sensitivity scalar-deleting destructor, multisample sample-count label resolver, and video-detail preset recognizer.
- Queue after refresh: `6057` functions, `2114` commented, `3943` commentless, `1705` undefined signatures, `1582` `param_N` signatures.
- Current telemetry proxies: comment-backed `2114/6057 = 34.90%`; strict comment-plus-clean-signature `2047/6057 = 33.80%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260516-202900_post_wave466_options_detail_verified` (`19` files, `157092743` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Boundary

This is static retail-binary evidence only. Runtime options-menu rendering/device behavior, exact menu-item/profile layouts, exact source identities, BEA launch behavior, game patching, and rebuild parity remain unproven.
