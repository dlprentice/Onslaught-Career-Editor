# Ghidra String Scratch Wave547 Readiness Note

Date: 2026-05-18

## Scope

Wave547 saved a static Ghidra name/signature/comment/tag hardening pass for two rotating string-scratch helpers:

| Address | Saved name | Saved signature |
| --- | --- | --- |
| `0x004f7c70` | `StringScratch__CopyToRotating4KBufferA` | `char * __cdecl StringScratch__CopyToRotating4KBufferA(char * source_string)` |
| `0x004f7cd0` | `StringScratch__CopyToRotating4KBufferB` | `char * __cdecl StringScratch__CopyToRotating4KBufferB(char * source_string)` |

Both helpers strlen-scan the stack `source_string`, advance a global modulo-4 slot counter, copy bytes into a 4 KiB rotating scratch bank at `bank + slot*0x1000`, write the NUL terminator, and return the selected bank pointer. Buffer A uses counter `0x00854d44` and bank `0x00848d40`; Buffer B uses counter `0x00854d48` and bank `0x00844d40`.

## Evidence

- Apply script: `tools/ApplyStringScratchWave547.java`.
- Probe: `tools/ghidra_string_scratch_wave547_probe.py`.
- Read-back artifacts: `subagents/ghidra-static-reaudit/wave547-string-temp-buffers-004f7c70/`.
- Dry run: `updated=0 skipped=2 renamed=0 would_rename=2 missing=0 bad=0`.
- Apply: `updated=2 skipped=0 renamed=2 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Verify dry: `updated=0 skipped=2 renamed=0 would_rename=0 missing=0 bad=0`.
- Post read-back verified `2` metadata rows, `2` tag rows, `25` xref rows, `562` instruction rows, and `2` decompile exports.
- Focused probe: `py -3 tools\ghidra_string_scratch_wave547_probe.py --check` PASS.
- Queue refresh: `py -3 tools\ghidra_static_reaudit_queue_probe.py --check --json` PASS after refreshing the live quality snapshot.
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260518-114408_post_wave547_string_scratch_verified`, `19` files, `159320967` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

## Queue Snapshot

Fresh queue telemetry after Wave547:

| Metric | Value |
| --- | ---: |
| Function objects | `6089` |
| Commented functions | `2654` |
| Commentless functions | `3435` |
| Exact-undefined signatures | `1535` |
| `param_N` signatures | `1287` |
| Comment-backed proxy | `2654/6089 = 43.59%` |
| Strict comment-plus-clean-signature proxy | `2600/6089 = 42.70%` |

This is telemetry only, not a completion milestone.

## Not Proven

- Exact source identity or source-body parity.
- Caller lifetime contract for returned scratch pointers.
- Runtime formatting behavior.
- Behavior with overlong input strings.
- BEA launch, executable patching, and rebuild parity.
