# Ghidra Platform Directory Wave473 Readiness

Date: 2026-05-16

## Scope

Wave473 saved bounded Ghidra signature/comment/tag corrections for:

- `0x004d2600` `Platform__CreateDirectoryPath`
- `0x0055f347` `Platform__CreateDirectoryWithErrno`

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave473-platform-directory-path/`
- Apply script: `tools/ApplyPlatformDirectoryPathWave473.java`
- Focused probe: `tools/ghidra_platform_directory_wave473_probe.py`
- Probe test: `tools/ghidra_platform_directory_wave473_probe_test.py`
- Prior index context: `reverse-engineering/binary-analysis/functions/Platform.cpp/_index.md`

## Result

`ApplyPlatformDirectoryPathWave473.java` reported:

- Dry: `updated=0 skipped=2 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Apply: `updated=2 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Verify dry: `updated=0 skipped=2 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Save: `REPORT: Save succeeded`

Read-back verified `2` metadata rows, `2` tag rows, `3` xref rows, `2` target decompile exports plus `index.tsv`, `68` disassembly rows for `0x004d2600`, `25` disassembly rows for `0x0055f347`, `146` wide caller-instruction rows, and focused probe status `PASS`.

## Boundary

This is static Ghidra refinement only. Runtime filesystem behavior, path length safety, exact CLI/save-directory caller intent, errno consumers, BEA launch, game patching, and rebuild parity remain deferred.

## Queue Snapshot

Fresh queue after Wave473:

- Function objects: `6057`
- Functions with comments: `2149`
- Commentless functions: `3908`
- Undefined signatures: `1702`
- `param_N` signatures: `1567`
- Comment-backed proxy: `2149/6057 = 35.48%`
- Strict clean-signature proxy: `2083/6057 = 34.39%`

These percentages are telemetry only, not certification.

## Backup

Verified saved-project backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260516-230437_post_wave473_platform_directory_verified
SourceCount 19
BackupCount 19
BackupBytes 157158279
MissingCount 0
ExtraCount 0
HashDiffCount 0
```
