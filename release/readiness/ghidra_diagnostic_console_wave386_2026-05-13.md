# Ghidra Diagnostic / Fatal / Console Correction Tranche - 2026-05-13

Status: public-safe static RE evidence

## Summary

Wave 386 saved Ghidra signature/comment/tag metadata for five diagnostic, fatal-error, and console-print targets after metadata, decompile, xref, instruction, and tag read-back. The pass does not rename the targets; it hardens the saved signatures and comments for the retail diagnostic trace stub, fatal exit path, localized fatal wrapper, and two variadic console print sinks.

This is static Ghidra evidence only. It does not prove runtime console output, fatal-error display behavior, exact class layouts, concrete local types, BEA launch, game patching, or rebuild parity.

## Saved Targets

| Address | Saved name | Saved signature | Evidence boundary |
| --- | --- | --- | --- |
| `0x0040c640` | `DebugTrace` | `void __cdecl DebugTrace(char * message)` | Retail body is a `RET` stub/no-op, but it remains a high-fan-in diagnostic call target with `323` xrefs. |
| `0x0042cfa0` | `FatalError__ExitProcess` | `noreturn void __cdecl FatalError__ExitProcess(char * message, int code)` | Prints through `CConsole__Printf`, shuts down mouse input, formats localized fatal text, normalizes separators, invokes the fallback path helper, and calls `ExitProcess(1)`. |
| `0x0042d080` | `FatalError_LocalizedStringId` | `void __stdcall FatalError_LocalizedStringId(char gate, int stringId, int code)` | Guard-gated localized fatal wrapper that calls the fatal exit path only when the gate byte is clear. |
| `0x00441740` | `CConsole__Printf` | `void __cdecl CConsole__Printf(void * console, char * format, ...)` | Variadic console print sink: formats through a stack buffer, mirrors through `DebugTrace`, writes/appends the console file path when enabled, updates the 30-slot status-history ring, and refreshes timestamps. |
| `0x004418a0` | `CConsole__PrintfNoNewline` | `void __cdecl CConsole__PrintfNoNewline(void * console, char * format, ...)` | Variadic no-newline console print sink sharing the file/history/timestamp path without the `DebugTrace` newline mirror. |

## Validation

| Check | Result |
| --- | --- |
| Headless `ApplyDiagnosticConsoleWave386.java` dry run | PASS: `updated=0 skipped=5 renamed=0 varargs=0 noreturn=0 missing=0 bad=0`, `REPORT: Save succeeded`. |
| Headless `ApplyDiagnosticConsoleWave386.java` apply | PASS: `updated=5 skipped=0 renamed=0 varargs=2 noreturn=1 missing=0 bad=0`, `REPORT: Save succeeded`. |
| Post-apply read-back exports | PASS: `5` metadata rows, `5` decompile exports, `757` xref rows, `605` instruction rows, and `5` tag rows. |
| `py -3 tools\ghidra_diagnostic_console_wave386_probe_test.py` | PASS: `2/2` tests. |
| `cmd.exe /c npm run test:ghidra-diagnostic-console-wave386` | PASS: `status=PASS`, `targets=5`, `instruction_hits=11`. |
| `py -3 -m py_compile tools\ghidra_diagnostic_console_wave386_probe.py tools\ghidra_diagnostic_console_wave386_probe_test.py` | PASS. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS after refreshing `ExportFunctionQualitySnapshot.java`: `6027` functions, `1435` commented functions, `4592` commentless functions, `1935` undefined signatures, and `1913` `param_N` signatures. |
| Actual Ghidra project backup | PASS: copied `BEA.gpr` and `BEA.rep` to `[maintainer-local-ghidra-backup-root]\BEA_20260513_190726_post_wave386_diagnostic_console_verified`; verified `19` files, `153914247` bytes, `HashDiffCount=0`. |

The current broad comment-backed proxy is `1435/6027 = 23.81%`. The stricter comment-plus-no-`undefined`-or-`param_N` proxy is `1373/6027 = 22.78%`. These values are telemetry only, not completion milestones.

## Not Proven

- Runtime console, debug-trace, or fatal-error display behavior.
- Exact source identity for every branch in the fatal and console paths.
- Exact `CConsole` layout recovery.
- Concrete local variable names/types for every decompiler temporary.
- BEA launch, game patching, or runtime proof.
- Rebuild parity or gameplay behavior.
