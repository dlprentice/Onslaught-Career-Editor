# Ghidra IScript SetThing Command Bridge Wave1064 Readiness Note

Status: complete static read-only evidence
Date: 2026-06-01
Scope: `iscript-setthing-command-bridge-wave1064`

Wave1064 re-read the IScript mission-command bridge that writes script-provided values into selected thing/engine/unit state. Fresh exports confirmed the saved Wave582/Wave527/Wave528 names, signatures, comments, and tags remain coherent, so the wave made no Ghidra mutation.

The pass made no rename, no signature change, no comment change, no tag change, no function-boundary change, no executable-byte change, and did not launch BEA or mutate runtime/game files.

Primary anchors:

| Address | Static evidence |
| --- | --- |
| `0x00534fb0 IScript__SetThingValueViaVFunc198_FromArg` | DATA-registered by `ScriptCommandRegistry__InitBuiltins` at `0x0053223c`; gates on `context+0x34 & 0x10`, reads arg getter slot `+0x38`, dispatches selected thing vtable slot `+0x198`, and returns with `RET 0x0c`. |
| `0x00534fe0 IScript__SetThingValueViaVFunc19C_FromArg` | DATA-registered by `ScriptCommandRegistry__InitBuiltins` at `0x0053225b`; same integer/thing-value bridge pattern, dispatching selected thing vtable slot `+0x19c`. |
| `0x00535010 IScript__SetThingValueViaEngineHelper4FE390_FromArg` | DATA-registered by `ScriptCommandRegistry__InitBuiltins` at `0x005331a6`; calls `CEngine__EnableThingByNameFlag` after arg getter slot `+0x38`. |
| `0x00535040 IScript__SetThingValueViaEngineHelper4FE3F0_FromArg` | DATA-registered by `ScriptCommandRegistry__InitBuiltins` at `0x005331b9`; calls `CEngine__DisableThingByNameFlag` after arg getter slot `+0x38`. |
| `0x00535530 IScript__SetThingFloatViaVFunc1C8_FromArg` | DATA-registered by `ScriptCommandRegistry__InitBuiltins` at `0x00533193`; reads float arg getter slot `+0x34`, stores the float on stack, and dispatches selected thing vtable slot `+0x1c8`. |
| `0x00535560 IScript__SetThingRefViaCUnitHelper4FD830_FromArg` | DATA-registered by `ScriptCommandRegistry__InitBuiltins` at `0x00530d3a`; reads integer/faction-like arg getter slot `+0x30` and calls `CUnit__SetFactionForHierarchy`. |

Context anchors:

- `0x004fd830 CUnit__SetFactionForHierarchy`
- `0x004fe390 CEngine__EnableThingByNameFlag`
- `0x004fe3f0 CEngine__DisableThingByNameFlag`
- `0x0052ff30 ScriptCommandRegistry__InitBuiltins`
- `0x005333b0 IScript__Constructor`
- `0x00533450 IScript__Destructor`
- `0x00533500 IScript__CallEvent0AndRegisterNestedListeners`
- `0x00533840 IScript__RestoreSavedStateAndGotoInstruction`
- `0x005343e0 IScript__PrimaryObjectiveComplete`
- `0x00534410 IScript__SecondaryObjectiveComplete`
- `0x00534440 IScript__PrimaryObjectiveFailed`
- `0x00534470 IScript__SecondaryObjectiveFailed`

Read-back evidence:

- Primary exports: `6` metadata rows, `6` tag rows, `6` xref rows, `94` function-body instruction rows, and `6` decompile rows.
- Context exports: `12` metadata rows, `12` tag rows, `14` xref rows, `2856` function-body instruction rows, and `12` decompile rows.
- No `LockException`, missing, bad, failed, or unresolved rows were observed in the Wave1064 export logs.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1199/1560 = 76.86%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-225655_post_wave1064_iscript_setthing_command_bridge_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The eighteen target rows exist in the saved Ghidra project with expected names and signatures.
- The six primary IScript command handlers remain coherently DATA-registered through `ScriptCommandRegistry__InitBuiltins`.
- The saved comments match fresh retail instruction/decompile evidence for argument getter slots, flag guard, indirect thing vtable slots, engine helper calls, and unit faction helper dispatch.

What remains unproven:

- Runtime mission-script dispatch behavior.
- Complete mission-script corpus coverage.
- Exact command descriptor schema.
- Exact thing/engine/unit concrete layouts.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Next candidate note: continue with the next expanded static re-audit cluster; prefer read-only review first and mutate only when fresh evidence proves a correction or normalization need.

Probe token anchor: Wave1064; iscript-setthing-command-bridge-wave1064; 0x00534fb0 IScript__SetThingValueViaVFunc198_FromArg; 0x00534fe0 IScript__SetThingValueViaVFunc19C_FromArg; 0x00535010 IScript__SetThingValueViaEngineHelper4FE390_FromArg; 0x00535040 IScript__SetThingValueViaEngineHelper4FE3F0_FromArg; 0x00535530 IScript__SetThingFloatViaVFunc1C8_FromArg; 0x00535560 IScript__SetThingRefViaCUnitHelper4FD830_FromArg; 0x004fd830 CUnit__SetFactionForHierarchy; 0x004fe390 CEngine__EnableThingByNameFlag; 0x004fe3f0 CEngine__DisableThingByNameFlag; 812/1408 = 57.67%; 1199/1560 = 76.86%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-225655_post_wave1064_iscript_setthing_command_bridge_verified; no mutation.
