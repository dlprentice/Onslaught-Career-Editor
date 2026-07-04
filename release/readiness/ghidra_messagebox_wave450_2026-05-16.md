# Ghidra MessageBox Wave450 Evidence

Date: 2026-05-16

## Scope

Wave450 saved Ghidra name/signature/comment/tag corrections for `17` Message/MessageBox/portrait/queue/reveal targets plus adjacent MessageLog and battle-line renderer helpers:

`0x004b6f10`, `0x004b6f70`, `0x004b7160`, `0x004b71e0`, `0x004b7300`, `0x004b7320`, `0x004b7930`, `0x004b7ab0`, `0x004b7b60`, `0x004b7b70`, `0x004b7b80`, `0x004b7ca0`, `0x004b7ea0`, `0x004b8020`, `0x004b82a0`, `0x004b82b0`, and `0x004b8800`.

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave450-messagebox-portrait-current/`
- Apply script: `tools/ApplyMessageBoxWave450.java`
- Probe: `tools/ghidra_messagebox_wave450_probe.py`
- Test alias: `npm run test:ghidra-messagebox-wave450`
- Apply summary: `updated=17 skipped=0 created=0 would_create=0 renamed=10 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=17 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports verified `17` metadata rows, `17` tag rows, `32` xref rows, `17` decompile exports, and focused ret-cleanup instruction evidence.
- Queue after refresh: `6057` functions, `1954` commented, `4103` commentless, `1734` undefined signatures, `1689` `param_N` signatures.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260516-121409_post_wave450_messagebox_verified` (`19` files, `156535687` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Boundary

This is static retail-binary evidence only. Runtime message display, portrait animation/selection behavior, voice playback, battle-line rendering, concrete class layouts, exact source identities, BEA launch behavior, game patching, and rebuild parity remain unproven.
