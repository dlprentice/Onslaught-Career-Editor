# Ghidra CComplexThing SetVar Review Wave958 Readiness Note

Status: read-only static review
Date: 2026-05-28
Scope: `ccomplexthing-setvar-review-wave958`

Wave958 re-reviewed the base `CComplexThing::SetVar` fallback after fresh serialized headless Ghidra exports. No mutation was needed in Ghidra; anchor phrase: no mutation. The prior Wave517 owner/signature/comment/tag correction still matches the current saved database.

Primary Wave911 target:

| Address | Result |
| --- | --- |
| `0x004f45e0 CComplexThing__SetVar` | Still reads as `void __stdcall CComplexThing__SetVar(void * var_name, void * data)`. Instruction evidence loads `var_name` from `[ESP+4]`, calls the `var_name` vtable slot `+0x38`, pushes warning format string `0x006331ec`, calls `0x00441740 CConsole__Printf`, and returns at `0x004f45fc` with `RET 0x8`. The optimized retail body ignores `ECX` and the `data` stack argument, so the saved two-stack-argument signature remains the most honest static ABI label. |

Context anchors:

- `references/Onslaught/thing.cpp:827-829` contains the source fallback `CComplexThing::SetVar(CStringDataType* name, CDataType* data)` that logs `Warning: Uknown var '%s' in call to SetVar`.
- `0x006331c0` dumps to `[maintainer-local-source-export-root]\thing.cpp`.
- `0x006331ec` dumps to `Warning: Uknown var '%s' in call to SetVar`.
- `0x004804c0 CHiveBoss__SetVar` remains the derived `hb_*` config handler and falls back to `CComplexThing__SetVar` at `0x00480685`.
- `0x004f4230 CComplexThing__SetScript`, `0x004f44a0 CComplexThing__SetAnimMode`, and `0x004f45a0 CComplexThing__FinishedPlayingCurrentAnimation` remain the adjacent CComplexThing script/animation context.
- `0x00441740 CConsole__Printf` is the variadic warning sink; `0x0042a7b0 CConsole__SetVariableByName` is a separate console-variable command path, not the mission-script virtual fallback.

Read-back evidence:

- Exports: 7 metadata rows, 7 tag rows, 528 xref rows, 259 instruction rows, and 7 decompile-index rows.
- String dumps: `0x006331c0` and `0x006331ec`.
- Cursor Composer 2.5 fast consult was advisory and agreed the likely outcome was read-only/no mutation.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-114016_post_wave958_ccomplexthing_setvar_review_verified`, 19 files, 173542279 bytes, `DiffCount=0`.
- Static function-quality closure remains `6151/6151 = 100.00%`.
- Wave911 focused re-audit progress after Wave958 is `293/1408 = 20.81%`.

What this proves:

- The saved Ghidra function row for `CComplexThing__SetVar` remains coherent with fresh metadata, tags, xrefs, instruction, decompile, source-string, and source-reference evidence.
- The Wave517 correction away from old `CExplosionInitThing` / `CUnit` ownership remains valid.
- The `CHiveBoss__SetVar` derived override still falls back to the base `CComplexThing__SetVar` warning path.

What remains unproven:

- Runtime mission-script variable behavior.
- Exact `CStringDataType` or `CDataType` concrete layouts.
- Exact virtual dispatch target identity beyond observed slot offsets.
- Runtime console output behavior for this warning.
- BEA patching behavior.
- Rebuild parity.
