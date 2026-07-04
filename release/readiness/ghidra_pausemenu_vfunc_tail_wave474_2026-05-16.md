# Ghidra PauseMenu Vfunc Tail Wave474 Readiness

Date: 2026-05-16

## Scope

Wave474 saved bounded Ghidra name/signature/comment/tag corrections for:

- `0x004d15d0` `CPauseMenu__VFunc_03_HandleMenuControlInput`
- `0x004d1730` `CSimpleGameMenu__scalar_deleting_dtor`
- `0x004d1750` `CSimpleGameMenu__dtor_base`

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave474-pausemenu-vfunc-tail/`
- Apply script: `tools/ApplyPauseMenuVfuncTailWave474.java`
- Focused probe: `tools/ghidra_pausemenu_vfunc_tail_wave474_probe.py`
- Probe test: `tools/ghidra_pausemenu_vfunc_tail_wave474_probe_test.py`
- Function docs: `reverse-engineering/binary-analysis/functions/PauseMenu.cpp/`

## Result

`ApplyPauseMenuVfuncTailWave474.java` reported:

- Dry: `updated=0 skipped=3 created=0 would_create=0 renamed=0 would_rename=3 missing=0 bad=0`
- Apply: `updated=3 skipped=0 created=0 would_create=0 renamed=3 would_rename=0 missing=0 bad=0`
- Verify dry: `updated=0 skipped=3 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Save: `REPORT: Save succeeded`

Saved signatures:

```c
void __thiscall CPauseMenu__VFunc_03_HandleMenuControlInput(void * this, void * control_context, int button_id, int button_context);
void * __thiscall CSimpleGameMenu__scalar_deleting_dtor(void * this, int flags);
void __fastcall CSimpleGameMenu__dtor_base(void * simple_game_menu);
```

Read-back verified `3` metadata rows, `3` tag rows, `3` xref rows, `3` target decompile exports plus `index.tsv`, focused disassembly rows for the `RET 0x0c` and `RET 0x4` epilogues, destructor-body call/cleanup evidence, and focused probe status `PASS`.

## Boundary

This is static retail-binary evidence only. Runtime pause-menu UI behavior, exact menu/simple-menu layouts, exact source method identities, BEA launch behavior, game patching, and rebuild parity remain unproven. The nearby possible raw boundary at `0x004d1810` was not mutated and remains deferred.

## Queue Snapshot

Fresh queue after Wave474:

- Function objects: `6057`
- Functions with comments: `2152`
- Commentless functions: `3905`
- Undefined signatures: `1702`
- `param_N` signatures: `1564`
- Comment-backed proxy: `2152/6057 = 35.53%`
- Strict clean-signature proxy: `2086/6057 = 34.44%`

These percentages are telemetry only, not certification.

## Backup

Verified saved-project backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260516-233051_post_wave474_pausemenu_vfunc_tail_verified
SourceCount 19
BackupCount 19
BackupBytes 157158279
MissingCount 0
ExtraCount 0
HashDiffCount 0
```
