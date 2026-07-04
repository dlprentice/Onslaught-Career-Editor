# Ghidra PauseMenu Tail Wave465 Evidence

Date: 2026-05-16

## Scope

Wave465 saved Ghidra name/signature/comment/tag corrections for `10` compact menu-item and PauseMenu tail targets:

`0x004d01c0`, `0x004d0290`, `0x004d0490`, `0x004d04b0`, `0x004d0510`, `0x004d05e0`, `0x004d06e0`, `0x004d0810`, `0x004d0db0`, and `0x004d0e40`.

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave465-pausemenu-tail-current/`
- Apply script: `tools/ApplyPauseMenuTailWave465.java`
- Probe: `tools/ghidra_pausemenu_tail_wave465_probe.py`
- Test alias: `npm run test:ghidra-pausemenu-tail-wave465`
- Dry summary: `updated=0 skipped=10 created=0 would_create=0 renamed=0 would_rename=6 missing=0 bad=0`
- Apply summary: `updated=10 skipped=0 created=0 would_create=0 renamed=6 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=10 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports verified `10` metadata rows, `10` tag rows, `40` xref rows, `10` decompile exports plus `index.tsv`, and `370` focused instruction rows.
- Corrected compact menu-item vtable reset/destructor wrappers, controller-back binding-capacity rendering, CPauseMenu scalar/base destructors, pause texture loading, resume/defaultoptions persistence, button dispatch, binding-prompt action-node init, and compact CGameMenu base init.
- Queue after refresh: `6057` functions, `2108` commented, `3949` commentless, `1707` undefined signatures, `1586` `param_N` signatures.
- Current telemetry proxies: comment-backed `2108/6057 = 34.80%`; strict comment-plus-clean-signature `2041/6057 = 33.70%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260516-194317_post_wave465_pausemenu_tail_verified` (`19` files, `157092743` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Boundary

This is static retail-binary evidence only. Runtime pause-menu input/render/save behavior, exact menu-item/pause-menu layouts, exact source identities, BEA launch behavior, game patching, and rebuild parity remain unproven.
