# Ghidra Script Text Console Boundary Wave1074 Readiness Note

Status: complete static mutation/read-back evidence
Date: 2026-06-02
Scope: `script-text-console-boundary-wave1074`

Wave1074 recovered and saved one previously missing Ghidra function boundary at `0x00537c40 IScript__PrintText`. The pass created the function object, saved the bounded `void __stdcall IScript__PrintText(void * script_args, void * unused_state, void * out_result)` signature, saved comments/tags, and made no executable-byte change, BEA launch, runtime/game-file mutation, or installed-game mutation.

Evidence summary:

| Address | Evidence |
| --- | --- |
| `0x00537c40 IScript__PrintText` | `ScriptCommandRegistry__InitBuiltins` writes command descriptor `0x0064d220 s_PrintText_0064f984`; handler field `0x0064d250` DATA-xrefs to `0x00537c40`. |
| `0x00537c40` body | Pre-state was `INSTRUCTION_NO_FUNCTION`; prior raw command returns at `0x00537c25 RET 0xc`; this body reads `script_args[0]` through vtable slot `+0x30`, calls `CText__GetStringById`, calls `CConsole__Printf`, and returns at `0x00537c69 RET 0xc`. |
| `0x00537c70` boundary | Apply-script read-back explicitly verified the new function body did not absorb the next raw command at `0x00537c70`. |
| `0x0064fda4` | Direct string dump is `%w`, used as the `CConsole__Printf` format string. |

Read-back evidence:

- Pre exports: listing state `INSTRUCTION_NO_FUNCTION`, `1` missing metadata row, `1` DATA xref row, `228` instruction-window rows, and `1` missing decompile row.
- Context exports: `5` metadata rows, `704` xref rows, `185` instruction-window rows, and `5` decompile rows for `ScriptCommandRegistry__InitBuiltins`, `IScript__GetTextWidth`, `IScript__PlaySound`, `CText__GetStringById`, and `CConsole__Printf`.
- Apply dry: `updated=1 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=1 missing=0 bad=0`.
- Apply: `updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`.
- Final dry: `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports: `1` metadata row, `1` tag row, `1` xref row, `13` function-body instruction rows, and `1` decompile row.
- Queue closure is now `6247/6247 = 100.00%`, with `0` commentless functions, `0` exact-undefined signatures, and `0` `param_N` signatures.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1358/1560 = 87.05%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-052830_post_wave1074_script_text_console_boundary_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The loaded Ghidra project now has a saved function object at `0x00537c40`.
- The saved name, signature, comment, and tags read back for `IScript__PrintText`.
- The function is tied to the `PrintText` mission-script command descriptor by fresh DATA xref evidence.
- The observed body is a bounded static text-id-to-console-print helper using `CText__GetStringById` and `CConsole__Printf("%w", ...)`.

What remains separate proof:

- Runtime MissionScript dispatch behavior.
- Runtime console/log behavior.
- Exact command descriptor schema.
- Exact source-body identity.
- Exact script datatype/object layouts.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Next candidate note: continue with read-only review first. The next raw-boundary candidate from Wave1073 remains `0x004dfa47`, but it is mixed CUnit/init-context code and should not be mutated until fresh owner/call-context evidence is strong enough.

Probe token anchor: Wave1074; script-text-console-boundary-wave1074; 0x00537c40 IScript__PrintText; s_PrintText_0064f984; 0x0064d220; 0x0064d250; 0x00537c69; 0x00537c70; CText__GetStringById; CConsole__Printf; %w; 812/1408 = 57.67%; 1358/1560 = 87.05%; 500/500 = 100.00%; 6247/6247 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-052830_post_wave1074_script_text_console_boundary_verified; boundary recovery.
