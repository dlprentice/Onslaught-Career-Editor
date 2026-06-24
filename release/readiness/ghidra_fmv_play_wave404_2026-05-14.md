# Ghidra FMV Play Console Command Hardening - 2026-05-14

Status: public-safe static Ghidra evidence note

Wave404 hardened the saved Ghidra metadata for the `fmv_play <filename>` console command handler at `0x004655d0`. This is a serialized static Ghidra correction/read-back wave only.

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x004655d0` | `void __cdecl con_fmv_play(char * command_line)` | Preserved the current name and hardened the saved signature/comment/tags. Read-back validates the command-line length check for the 9-byte prefix, mirrors `DAT_006630cc` into `DAT_0089d69c`, enters the controller noninteractive gate through `CController__SetNonInteractiveSection`, calls the frontend video object pointer at `0x0089d690` through vtable slot `+0x2c` using the filename suffix and flag arguments, leaves the noninteractive gate, and prints the syntax string through `CConsole__AddString` on short input. |

## Command Table Context

Fresh xref read-back records one command-table-style DATA xref from `0x004656b5` to `con_fmv_play`. The reviewed instruction window includes the `0x0089d69c` write, `0x0089d690` object load, slot `+0x2c` computed call, and syntax-string push.

## Source Boundary

Stuart source remains useful architecture context for normal frontend FMV paths such as `FMV.PlayFullscreen`, but no direct `con_fmv_play` source body was identified in the current snapshot. The saved signature/comment/tag state above is therefore based on retail Ghidra read-back, not source-body identity.

## Validation

- Focused probe test was written first and failed as expected before the probe module existed.
- `py -3 tools\ghidra_fmv_play_wave404_probe_test.py` passed with `3/3` tests.
- `ApplyFmvPlayWave404.java` dry run passed with `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`.
- `ApplyFmvPlayWave404.java` apply run passed with `updated=1 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0` and `REPORT: Save succeeded`.
- Read-back verified `1` metadata row, `1` decompile export, `1` DATA xref at `0x004656b5`, `1` tag row, selected instruction tokens, and focused probe status `PASS`.
- Refreshed queue telemetry reports `6028` functions, `1557` commented functions, `4471` commentless functions, `1910` undefined signatures, and `1858` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1557/6028 = 25.83%`, strict clean-signature `1495/6028 = 24.80%`.
- The actual live Ghidra project backup is verified at `G:\GhidraBackups\BEA_20260514_060316_post_wave404_fmv_play_verified` with `19` files, `154798983` bytes, and `HashDiffCount=0`.

## Claim Boundary

This note does not prove runtime playback behavior, does not prove exact frontend video object type/layout, does not prove exact source identity, does not prove rebuild parity, and does not involve launching or patching `BEA.exe`.
