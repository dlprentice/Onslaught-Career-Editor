# Ghidra CPlayer Lifecycle / View Wave470 Readiness

Date: 2026-05-16

## Scope

Wave470 saved a bounded Ghidra name/signature/comment/tag correction for seven adjacent `CPlayer` lifecycle/view helpers:

- `0x004d2780` `CPlayer__ctor`
- `0x004d2810` `CPlayer__scalar_deleting_dtor`
- `0x004d2830` `CPlayer__dtor_base`
- `0x004d28a0` `CPlayer__Init`
- `0x004d28c0` `CPlayer__GotoFPView`
- `0x004d29c0` `CPlayer__Goto3rdPersonView`
- `0x004d2a50` `CPlayer__GotoControlView`

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave470-cplayer-view-current/`
- Apply script: `tools/ApplyCPlayerViewWave470.java`
- Focused probe: `tools/ghidra_cplayer_view_wave470_probe.py`
- Probe test: `tools/ghidra_cplayer_view_wave470_probe_test.py`
- Source bridge: `references/Onslaught/Player.cpp` and `references/Onslaught/Player.h`

## Result

`ApplyCPlayerViewWave470.java` reported:

- Dry: `updated=0 skipped=7 created=0 would_create=0 renamed=0 would_rename=3 missing=0 bad=0`
- Apply: `updated=7 skipped=0 created=0 would_create=0 renamed=3 would_rename=0 missing=0 bad=0`
- Verify dry: `updated=0 skipped=7 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Save: `REPORT: Save succeeded`

Read-back verified `7` metadata rows, `7` tag rows, `16` xref rows, `7` target decompile exports plus `index.tsv`, `1547` focused instruction rows, and focused probe status `PASS`.

## Queue Snapshot

Fresh queue after Wave470:

- Function objects: `6057`
- Functions with comments: `2143`
- Commentless functions: `3914`
- Undefined signatures: `1703`
- `param_N` signatures: `1573`
- Comment-backed proxy: `2143/6057 = 35.38%`
- Strict clean-signature proxy: `2076/6057 = 34.27%`

These percentages are telemetry only, not certification.

## Backup

Verified saved-project backup:

```text
G:\GhidraBackups\BEA_20260516-220000_post_wave470_cplayer_view_verified
SourceCount 19
BackupCount 19
BackupBytes 157125511
MissingCount 0
ExtraCount 0
HashDiffCount 0
```

## Boundary

This is static Ghidra refinement only. Runtime camera behavior, exact `CPlayer` layout, BEA launch, game patching, and rebuild parity remain deferred.
