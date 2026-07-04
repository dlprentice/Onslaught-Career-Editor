# Ghidra CLTShell Runtime Wave514 Readiness

Status: static read-back complete
Date: 2026-05-17

## Scope

Wave514 saved signature/comment/tag hardening for 4 CLTShell runtime helpers:

- `0x004efb10` `CLTShell__InitializeRuntimeAndLoadCoreResources`
- `0x004f00e0` `CLTShell__ShutdownRuntimeAndReleaseResources`
- `0x004f0200` `CLTShell__RunStressTestLevelLoop`
- `0x004f0330` `CLTShell__RunFrontEndAndGameLoop`

No rename was applied in this wave; the pass hardens the existing names with read-back signatures, bounded comments, and tags.

## Evidence

- Pre-state exports: `subagents/ghidra-static-reaudit/wave514-ltshell-runtime-004efb10/pre_*`.
- Caller/context export: `CLTShell__WinMain` under the same ignored evidence folder.
- Mutation script: `tools/ApplyLTShellRuntimeWave514.java`.
- Dry run: `updated=0 skipped=4 missing=0 bad=0`.
- Apply run: `updated=4 skipped=0 missing=0 bad=0`.
- Verify dry run: `updated=0 skipped=4 missing=0 bad=0`.
- Post read-back: `4` metadata rows, `4` tag rows, `5` xref rows, `1380` instruction rows, and `4` decompile exports.
- Focused probe: `tools/ghidra_ltshell_runtime_wave514_probe.py --check`.
- Queue refresh after Wave514: `6078` functions, `2404` commented, `3674` commentless, `1614` exact-undefined signatures, and `1428` `param_N` signatures.
- Current whole-project telemetry proxy: comment-backed `2404/6078 = 39.55%`; strict comment-plus-clean-signature proxy `2350/6078 = 38.66%`.
- Backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260517-204514_post_wave514_ltshell_runtime_verified` with `19` files, `158436231` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Claim Boundary

This is static Ghidra metadata evidence only. It improves CLTShell runtime initialization, shutdown, stress-test loop, and frontend/game loop readability. It does not prove runtime launch behavior, runtime frontend/game behavior, stress-test behavior, exact CLTShell/global shell-state layout, BEA patching, or rebuild parity.
