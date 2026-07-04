# Ghidra MessageLog Wave451 Evidence

Date: 2026-05-16

## Scope

Wave451 saved Ghidra name/signature/comment/tag corrections for `11` MessageLog/overlay targets:

`0x004b8850`, `0x004b8dd0`, `0x004b8e50`, `0x004b8e70`, `0x004b8ef0`, `0x004b8f00`, `0x004b9010`, `0x004b93f0`, `0x004b9a80`, `0x004b9ea0`, and `0x004b9ec0`.

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave451-messagelog-overlay-current/`
- Apply script: `tools/ApplyMessageLogWave451.java`
- Probe: `tools/ghidra_messagelog_wave451_probe.py`
- Test alias: `npm run test:ghidra-messagelog-wave451`
- Dry summary: `updated=0 skipped=11 created=0 would_create=0 renamed=0 would_rename=5 missing=0 bad=0`
- Apply summary: `updated=11 skipped=0 created=0 would_create=0 renamed=5 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=11 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports verified `11` metadata rows, `11` tag rows, `19` xref rows, `11` decompile exports, and focused return-cleanup instruction evidence.
- Queue after refresh: `6057` functions, `1965` commented, `4092` commentless, `1734` undefined signatures, `1680` `param_N` signatures.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260516-124114_post_wave451_messagelog_verified` (`19` files, `156568455` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Boundary

This is static retail-binary evidence only. Runtime message-log display, scroll/back input behavior, exact overlay layout, concrete MessageLog/MessageBox layouts, exact source identities, BEA launch behavior, game patching, and rebuild parity remain unproven.
