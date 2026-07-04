# Ghidra D3D Runtime Tail Wave739 Readiness Note

Status: passed
Date: 2026-05-22

Wave739 D3D runtime tail saved comments/tags/signatures for `0x005be622 Direct3DCreate9` and `0x005be628 HResultToString` with the `d3d-runtime-tail-wave739` and `wave739-readback-verified` tags. The pass hardened two signatures, made no renames, made no function-boundary changes, and made no executable-byte changes.

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x005be622 Direct3DCreate9` | `void * __stdcall Direct3DCreate9(uint sdk_version)` | Import thunk evidence: instruction export shows a six-byte `JMP` through IAT pointer `0x005d8348`; caller `0x005290bc` in `CD3DApplication__Create` pushes SDK version `0x1f` and stores returned EAX at `CD3DApplication +0x32e9c`. |
| `0x005be628 HResultToString` | `char * __stdcall HResultToString(int hresult)` | HRESULT string mapper evidence: 22 call sites push one HRESULT and use returned EAX as a log/message string; full instruction export shows a single `RET 0x4` at `0x005c9c66`; sampled return target `0x0060bc44` resolves to `E_ABORT`. |

Validation evidence:

- Dry/apply/final dry reported `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=0`, then `updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=0`, then final dry `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post exports verified `2` metadata rows, `2` tag rows, `22` xref rows, `210` target instruction rows, and `2` decompile-index rows. `Direct3DCreate9` decompiled successfully; `HResultToString` decompile timed out on the large mapper and is backed by instruction/xref/string evidence instead.
- Read-only context exports verified `902` xref-site instruction rows, `17343` HResultToString full-instruction rows, and the `E_ABORT` sample string.
- Queue refresh passed with `6098` total functions, `4351` commented, `1747` commentless, `1215` exact-undefined signatures, `36` `param_N` signatures, comment-backed proxy `4351/6098 = 71.35%`, and strict clean-signature proxy `4293/6098 = 70.40%`.
- Earliest raw commentless row is `0x0042f220 CSPtrSet__Clear`; next commentless high-signal row is `0x005d04e0 DirectInput8Create`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-135016_post_wave739_d3d_runtime_tail_verified`, `19` files, `166988679` bytes, `DiffCount=0`.

Scope boundary: this wave proves saved static retail Ghidra metadata only. Imported `d3d9.dll` behavior, runtime graphics behavior, runtime error-reporting behavior, exact HRESULT table completeness, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave739 D3D runtime tail`, `d3d-runtime-tail-wave739`, `0x005be622 Direct3DCreate9`, `0x005be628 HResultToString`, `0x005d04e0 DirectInput8Create`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-135016_post_wave739_d3d_runtime_tail_verified`.
