# Ghidra FromWCHAR String Conversion Wave834 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `fromwchar-string-conversion-wave834`

Wave834 FromWCHAR string conversion saved comment/tag metadata for `0x004f7d30 FromWCHAR` after serialized headless dry/apply/read-back. The pass preserved the already clean `char * __cdecl FromWCHAR(short * wstr)` signature, made no rename, made no function-boundary change, and made no executable-byte change.

This is important shared string/path infrastructure: the helper bridges 16-bit input slots into a rotating narrow scratch buffer used by fatal-error/localized text, cheat-name checks, message-box text/portrait paths, save-file paths, level-lost text, and frontend options.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x004f7d30 FromWCHAR` | Calls `WcsLen(wstr)`, rotates `g_FromWCHAR_RingIndex` at `0x00854d4c` modulo four, selects `0x00840d40+(slot*0x1000)`, copies the low byte from each 16-bit input slot while advancing the source pointer by two bytes, NUL-terminates the selected slot, and returns the selected scratch buffer. |
| `0x0042d098` / `0x0042cfdf` / `0x0042d009` / `0x0042d0c4` / `0x0042c764` | Fatal-error/localized text callers. |
| `0x004654f8` | Cheat text compare caller in `IsCheatActive`. |
| `0x004b7b28` / `0x004b7fdf` | Message-box portrait/text paths. |
| `0x00514c33` / `0x00514fb7` / `0x005150b7` / `0x00514ef7` | Save-file enumeration/write/read/delete path helpers. |
| `0x004f7bf0` / `0x004f7c70` / `0x004f7cd0` | Adjacent string scratch helpers with the same four-slot scratch-buffer pattern. |

Read-back evidence:

- `ApplyFromWcharStringConversionWave834.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0`
- `ApplyFromWcharStringConversionWave834.java apply`: `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0`
- `ApplyFromWcharStringConversionWave834.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 14 xref rows, 101 target instruction-window rows, 81 full target instruction rows, 1 target decompile row, 9 context metadata rows, 9 context decompile rows, and 406 xref-site instruction rows.
- Queue after Wave834: 6098 total, 5656 commented, 442 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5656/6098 = 92.75%`, strict clean-signature proxy `5656/6098 = 92.75%`.
- Next raw commentless row: `0x004f9a90 CUnit__ApplyDamage`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `G:\GhidraBackups\BEA_20260525-000436_post_wave834_fromwchar_string_conversion_verified`, 19 files, 171805575 bytes, `DiffCount=0`.

What this proves:

- The saved Ghidra project contains the target function row with the preserved clean signature.
- The saved comment and tags include `fromwchar-string-conversion-wave834` and `wave834-readback-verified`.
- The observed conversion body and caller fan-in are static retail Ghidra evidence from metadata, decompile, instruction-window, xref, and context exports.

What remains unproven:

- Exact source body identity.
- Exact encoding/codepage policy.
- Unicode lossiness beyond observed low-byte copying.
- Caller scratch-buffer lifetime contract.
- Runtime path/UI behavior.
- BEA patching behavior.
- Rebuild parity.
