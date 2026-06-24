# Ghidra CUnit Render Distance-Fade Wave545 Readiness Note

Date: 2026-05-18

## Scope

Wave545 saved a static Ghidra signature/comment/tag hardening pass for one CUnit render helper:

| Address | Saved name | Saved signature |
| --- | --- | --- |
| `0x004f6fd0` | `CUnit__RenderWithDistanceFade` | `bool __thiscall CUnit__RenderWithDistanceFade(void * this, uint render_flags)` |

`OID__RenderWithState1BOverride` calls this helper only when `this+0x48` is non-null and treats the low-byte return as handled/not-handled. The target body ends with `RET 0x4`, reads one stack `render_flags` argument after ECX `this`, writes a rounded fade value to global `0x0063012c` for a nested `CThing__Render(this, render_flags)` call, restores `0x0063012c` to `0xff`, and returns true. The nonpositive/NaN path returns false.

## Evidence

- Apply script: `tools/ApplyCUnitRenderDistanceFadeWave545.java`.
- Probe: `tools/ghidra_cunit_render_distance_fade_wave545_probe.py`.
- Read-back artifacts: `subagents/ghidra-static-reaudit/wave545-cunit-render-distance-fade-004f6fd0/`.
- Dry run: `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`.
- Apply: `updated=1 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Verify dry: `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`.
- Post read-back verified `1` metadata row, `1` tag row, `1` xref row, `321` instruction rows, `1` target decompile export, and `1` caller decompile export. The caller decompile now passes only `render_flags`; the stale third argument is gone.
- Focused probe: `py -3 tools\ghidra_cunit_render_distance_fade_wave545_probe.py --check` PASS.
- Queue refresh: `py -3 tools\ghidra_static_reaudit_queue_probe.py --check --json` PASS after refreshing the live quality snapshot.
- Backup: `G:\GhidraBackups\BEA_20260518-105700_post_wave545_cunit_render_distance_fade_verified`, `19` files, `159320967` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

## Queue Snapshot

Fresh queue telemetry after Wave545:

| Metric | Value |
| --- | ---: |
| Function objects | `6089` |
| Commented functions | `2651` |
| Commentless functions | `3438` |
| Exact-undefined signatures | `1535` |
| `param_N` signatures | `1290` |
| Comment-backed proxy | `2651/6089 = 43.54%` |
| Strict comment-plus-clean-signature proxy | `2597/6089 = 42.65%` |

This is telemetry only, not a completion milestone.

## Not Proven

- Exact fade field meaning at `*(this+0x48)+0xbc`.
- Exact render-state/global meaning for `0x0063012c`.
- Runtime rendering behavior.
- Source identity, source-body parity, BEA launch, executable patching, and rebuild parity.
