# Ghidra SafeSide Shutdown Wave542 Readiness Note

Date: 2026-05-18

## Scope

Wave542 saved a static Ghidra owner/name/signature/comment/tag correction for the deferred SafeSide vtable target from Wave498:

| Address | Saved name | Saved signature |
| --- | --- | --- |
| `0x004de1d0` | `CSafeSide__ShutdownAndUnlinkFactionAnchor` | `void __fastcall CSafeSide__ShutdownAndUnlinkFactionAnchor(void * this)` |

The prior saved name was `CSafeSide__VFunc_02_004de1d0`. Fresh retail evidence shows a register-only body that removes `this` from global list `DAT_00855160` through `CSPtrSet__Remove`, then forwards to `CComplexThing__Shutdown`. `DAT_00855160` is also scanned by `CUnit__FindNearestFactionAnchor`, so the list role is bounded as faction-anchor context. No matching Stuart-source `CSafeSide` body was found; the owner was retained from the existing retail label and the behavior claim is static.

## Evidence

- Apply script: `tools/ApplySafeSideShutdownWave542.java`.
- Probe: `tools/ghidra_safeside_shutdown_wave542_probe.py`.
- Read-back artifacts: `subagents/ghidra-static-reaudit/wave542-safeside-vfunc-004de1d0/`.
- Dry run: `updated=0 skipped=1 renamed=0 would_rename=1 missing=0 bad=0`.
- Apply: `updated=1 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Verify dry: `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`.
- Post read-back verified `1` metadata row, `1` tag row, `1` xref row from `0x005dcce4`, `241` instruction rows, `1` decompile export, and `96` vtable rows.
- Focused probe: `py -3 tools\ghidra_safeside_shutdown_wave542_probe.py --check` PASS.
- Npm wrapper: `cmd.exe /c npm run test:ghidra-safeside-shutdown-wave542` PASS.
- Queue refresh: `py -3 tools\ghidra_static_reaudit_queue_probe.py --check --json` PASS after refreshing the live quality snapshot.
- Backup: `G:\GhidraBackups\BEA_20260518-093637_post_wave542_safeside_shutdown_verified`, `19` files, `159320967` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

## Queue Snapshot

Fresh queue telemetry after Wave542:

| Metric | Value |
| --- | ---: |
| Function objects | `6089` |
| Commented functions | `2648` |
| Commentless functions | `3441` |
| Exact-undefined signatures | `1535` |
| `param_N` signatures | `1293` |
| Comment-backed proxy | `2648/6089 = 43.49%` |
| Strict comment-plus-clean-signature proxy | `2594/6089 = 42.60%` |

This is telemetry only, not a completion milestone.

## Not Proven

- Runtime faction-anchor behavior.
- Exact `CSafeSide` source identity or concrete list/object layout.
- Broader SafeSide, Sentinel, or faction-anchor subsystem behavior.
- BEA launch, executable patching, and rebuild parity.
