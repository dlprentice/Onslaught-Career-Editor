# Ghidra OptionsTail Wave499 Readiness Note

Date: 2026-05-17

## Scope

Wave499 saved static Ghidra signature/comment/tag hardening for the fixed `0x56`-byte save/options tail pair:

| Address | Saved state |
| --- | --- |
| `0x00420b10` | `byte * __stdcall OptionsTail_Write(byte * tail)` |
| `0x00420d70` | `byte * __stdcall OptionsTail_Read(byte * tail)` |

## Evidence

- Apply script: `tools/ApplyOptionsTailWave499.java`
- Probe: `tools/ghidra_options_tail_wave499_probe.py`
- Scratch artifacts: `subagents/ghidra-static-reaudit/wave499-options-tail-00420b10/`
- Dry/apply/verify:
  - Dry: `updated=0 skipped=2 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
  - Apply: `updated=2 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
  - Final verify dry: `updated=0 skipped=2 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post-readback verified `2` metadata rows, `2` tag rows, `3` xref rows, and `2` decompile exports.
- Xrefs: `OptionsTail_Write` is called from `CCareer__Save` and `CCareer__SaveWithFlag`; `OptionsTail_Read` is called from `CCareer__Load`.
- Focused probe: `py -3 tools\ghidra_options_tail_wave499_probe.py --check` PASS.
- NPM probe: `cmd.exe /c npm run test:ghidra-options-tail-wave499` PASS.
- Queue refresh: `6078` total functions, `2267` commented, `3811` commentless, `1655` undefined signatures, `1514` `param_N`; strict comment-plus-clean-signature proxy `2213/6078 = 36.41%`.
- Verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260517-122449_post_wave499_options_tail_verified` with `19` files, `157780871` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Public Boundary

This note is public-safe static RE accounting. It does not include private game assets, installed-game mutation, runtime launch proof, raw decompile bodies, or private media.

## Not Proven

- Exact tail struct/layout naming.
- Runtime option persistence behavior across boot/load/save flows.
- BEA launch behavior, game patching, and rebuild parity.
