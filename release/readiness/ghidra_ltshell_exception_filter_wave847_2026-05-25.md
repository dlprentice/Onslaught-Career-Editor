# Ghidra LTShell Exception Filter Wave847 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `ltshell-exception-filter-wave847`

Wave847 LTShell exception filter corrected the loaded Ghidra row at `0x00512040` from stale `CLTShell__InitUnhandledExceptionLogFile` metadata to:

```cpp
int __stdcall CLTShell__UnhandledExceptionFilter(void * exception_pointers);
```

The pass saved one name/signature/comment/tag correction and made no function-boundary changes and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00512040 CLTShell__UnhandledExceptionFilter` | WinMain passes this address to `SetUnhandledExceptionFilter` at `0x0051213c`; the callback calls `SetUnhandledExceptionFilter(NULL)`, opens `OnslaughtException.txt` with mode string `0x0063dc88`, returns `1`/`EXCEPTION_EXECUTE_HANDLER`, and exits with `RET 0x4`. |
| `references/Onslaught/ltshell.cpp:172` | Stuart source has the fuller PC `LONG __stdcall ExceptionHandler(EXCEPTION_POINTERS *info)` reference shape. The saved retail claim remains bounded to the observed compact retail Ghidra body. |

Read-back evidence:

- `ApplyLTShellExceptionFilterWave847.java dry`: `updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=1 missing=0 bad=0`
- `ApplyLTShellExceptionFilterWave847.java apply`: `updated=1 skipped=0 renamed=1 would_rename=1 signature_updated=1 comment_only_updated=1 missing=0 bad=0`
- `ApplyLTShellExceptionFilterWave847.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 1 xref row, 285 instruction-window rows, 37 WinMain callsite instruction rows, and 2 context decompile rows.
- Queue after Wave847: 6098 total, 5674 commented, 424 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5674/6098 = 93.05%`, strict clean-signature proxy `5674/6098 = 93.05%`.
- Next raw commentless row: `0x00513120 PlatformInput__InitDirectInput`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-063403_post_wave847_ltshell_exception_filter_verified`, 19 files, 171871111 bytes, `DiffCount=0`.

What this proves:

- The target function row exists in the saved Ghidra project.
- The saved name/signature is `int __stdcall CLTShell__UnhandledExceptionFilter(void * exception_pointers)`.
- The saved comment and tags include `ltshell-exception-filter-wave847` and `wave847-readback-verified`.
- The observed retail callback shape is tied to WinMain's `SetUnhandledExceptionFilter` callsite and the compact `OnslaughtException.txt` open/return body.

What remains unproven:

- Full debug-symbol dump behavior from Stuart's source handler.
- Runtime crash handling behavior.
- Exact source-body parity.
- BEA patching behavior.
- Rebuild parity.
