# Ghidra Console Signature Tranche - 2026-05-12

Status: public-safe evidence summary.

## Scope

This note records a serialized saved-Ghidra correction pass over the retail console-system cluster from `0x00429bc0` through `0x0042c440`. The wave focused on existing named `CConsole`, `CConsoleVar`, and adjacent `CConsoleMenu` functions whose signatures, proof-boundary comments, and tags still carried whole-database static re-audit debt.

## Evidence

- Headless `ApplyConsoleSignatureTranche.java` dry mode completed with `updated=0 skipped=16 renamed=0 missing=0 bad=0` and `REPORT: Save succeeded`.
- Headless apply mode completed with `updated=16 skipped=0 renamed=1 missing=0 bad=0` and `REPORT: Save succeeded`.
- Fresh read-back verified `16/16` metadata rows, `16/16` decompile exports, `118` xref rows, `1680` instruction rows, and `16` tag rows.
- `0x0042c440` was renamed from the generic `VFuncSlot_05_0042c440` label to `CConsoleMenu__LinkChildAtHead` based on decompile/instruction behavior: parent pointer write, old-head link, parent first-child update, and child-count increment.
- The focused probe reports `targetCount=16`, `renamedTargetCount=1`, and `undefinedFixedTargetCount=4`.
- The refreshed quality queue reports `5884` total functions, `789` commented functions, `5095` commentless functions, `1989` undefined signatures, and `2276` `param_N` signatures.

## Claim Boundary

This is saved static Ghidra name/signature/comment/tag evidence only. It does not prove runtime console/menu behavior, exact source-body identity for all functions, concrete `CConsole` / `CConsoleVar` / `CConsoleMenu` layouts, local-variable/type recovery, full source parity, BEA launch behavior, game patching, or rebuild parity.

No private paths, raw decompile excerpts, screenshots, copied executables, runtime logs, or Ghidra project files are included in this public-safe summary.
