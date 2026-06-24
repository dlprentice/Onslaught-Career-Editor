# Ghidra CPlayer Snapshot Wave471 Readiness

Date: 2026-05-16

## Scope

Wave471 saved a bounded Ghidra signature/comment/tag correction for four adjacent `CPlayer` current/old view snapshot helpers:

- `0x004d2a70` `CPlayer__GetCurrentViewPoint`
- `0x004d2ae0` `CPlayer__GetCurrentViewOrientation`
- `0x004d2b40` `CPlayer__GetOldCurrentViewPoint`
- `0x004d2bb0` `CPlayer__GetOldCurrentViewOrientation`

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave471-cplayer-snapshot-current/`
- Apply script: `tools/ApplyCPlayerSnapshotWave471.java`
- Focused probe: `tools/ghidra_cplayer_snapshot_wave471_probe.py`
- Probe test: `tools/ghidra_cplayer_snapshot_wave471_probe_test.py`
- Source bridge: `references/Onslaught/Player.cpp` and `references/Onslaught/Player.h`

## Result

`ApplyCPlayerSnapshotWave471.java` reported:

- Dry: `updated=0 skipped=4 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Apply: `updated=4 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Verify dry: `updated=0 skipped=4 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Save: `REPORT: Save succeeded`

Read-back verified `4` metadata rows, `4` tag rows, `10` xref rows, `4` target decompile exports plus `index.tsv`, `421` focused instruction rows, raw disassembly range evidence for the `RET 0x4` epilogues, and focused probe status `PASS`.

## Queue Snapshot

Fresh queue after Wave471:

- Function objects: `6057`
- Functions with comments: `2147`
- Commentless functions: `3910`
- Undefined signatures: `1703`
- `param_N` signatures: `1569`
- Comment-backed proxy: `2147/6057 = 35.45%`
- Strict clean-signature proxy: `2083/6057 = 34.39%`

These percentages are telemetry only, not certification.

## Backup

Verified saved-project backup:

```text
G:\GhidraBackups\BEA_20260516-221501_post_wave471_cplayer_snapshot_verified
SourceCount 19
BackupCount 19
BackupBytes 157125511
MissingCount 0
ExtraCount 0
HashDiffCount 0
```

## Boundary

This is static Ghidra refinement only. Runtime camera behavior, exact `CPlayer`/`FVector`/`FMatrix` layouts, camera-table indexing, BEA launch, game patching, and rebuild parity remain deferred.
