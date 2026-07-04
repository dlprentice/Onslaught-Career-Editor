# Ghidra CPlayer AssignBattleEngine Wave472 Readiness

Date: 2026-05-16

## Scope

Wave472 saved a bounded Ghidra signature/comment/tag correction for:

- `0x004d3080` `CPlayer__AssignBattleEngine`

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave472-cplayer-assign-battleengine/`
- Apply script: `tools/ApplyCPlayerAssignBattleEngineWave472.java`
- Focused probe: `tools/ghidra_cplayer_assign_wave472_probe.py`
- Probe test: `tools/ghidra_cplayer_assign_wave472_probe_test.py`
- Source bridge: `references/Onslaught/Player.cpp` and `references/Onslaught/Player.h`

## Result

`ApplyCPlayerAssignBattleEngineWave472.java` reported:

- Dry: `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Apply: `updated=1 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Verify dry: `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Save: `REPORT: Save succeeded`

Read-back verified `1` metadata row, `1` tag row, `4` xref rows, `1` target decompile export plus `index.tsv`, `129` focused instruction rows, `26` raw disassembly rows, `68` caller-instruction rows, and focused probe status `PASS`.

## Queue Snapshot

Fresh queue after Wave472:

- Function objects: `6057`
- Functions with comments: `2147`
- Commentless functions: `3910`
- Undefined signatures: `1703`
- `param_N` signatures: `1568`
- Comment-backed proxy: `2147/6057 = 35.45%`
- Strict clean-signature proxy: `2084/6057 = 34.41%`

These percentages are telemetry only, not certification.

## Backup

Verified saved-project backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260516-223635_post_wave472_cplayer_assign_verified
SourceCount 19
BackupCount 19
BackupBytes 157125511
MissingCount 0
ExtraCount 0
HashDiffCount 0
```

## Boundary

This is static Ghidra refinement only. Runtime camera/player behavior, exact `CPlayer`/`CBattleEngine` layouts, exact virtual method identities, BEA launch, game patching, and rebuild parity remain deferred.
