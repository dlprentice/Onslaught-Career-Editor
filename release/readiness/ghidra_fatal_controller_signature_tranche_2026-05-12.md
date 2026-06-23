# Ghidra Fatal / Controller Signature Tranche - 2026-05-12

Status: public-safe evidence summary.

## Scope

This note records a serialized saved-Ghidra correction pass over seven retail fatal-error, controller, input, and vibration functions from `0x0042c750` through `0x0042e750`. The wave corrects clear owner/name drift where the current saved labels had over-fit callers instead of source/body ownership, then hardens signatures, proof-boundary comments, and tags.

## Evidence

- `0x0042d780` was renamed from `CController__VFunc_00_0042d780` to `CController__scalar_deleting_dtor`; the body calls `CController__dtor`, conditionally frees `this`, and is a compiler wrapper rather than a gameplay virtual behavior body.
- `0x0042d7d0` was renamed from `CFrontEnd__SetLoadingTransitionGate` to `CController__SetNonInteractiveSection` based on source-parity with `references/Onslaught/Controller.cpp`.
- `0x0042da00` was renamed from `CGame__UpdateCursorCenterWithWindowScale` to `Input__UpdateCursorCenterWithWindowScale` because the body is a retail input/cursor-center helper called by CGame paths, not a proven `CGame` method body.
- `0x0042e750` was renamed from `CGame__DispatchVibrationWithCareerGate` to `CController__SetVibration` based on source-parity with `references/Onslaught/Controller.cpp`.
- `0x0042c750` and `0x0042d0b0` were kept as localized fatal-error wrappers but had their stack signatures separated: variant A pops caller message plus a second context/status argument, while variant B is the single-message variant.
- Final read-back verified `7/7` metadata rows, `7/7` decompile exports, `42` xref rows, `735` instruction rows, `7/7` tag rows, and focused probe status `PASS`.
- The refreshed whole-database quality queue reports `5884` functions, `796` commented functions, `5088` commentless functions, `1989` undefined signatures, and `2269` signatures still using `param_N` names.

## Claim Boundary

This is saved static Ghidra name/signature/comment/tag evidence only. It does not prove runtime fatal, input, inactivity, cursor, or force-feedback behavior; exact source identity for every selected body; concrete class/global layouts; local-variable/type recovery; BEA launch behavior; game patching; or rebuild parity.

No private paths, raw decompile excerpts, screenshots, copied executables, runtime logs, or Ghidra project files are included in this public-safe summary.
