# Ghidra Script Operator Vfuncs Wave863 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `script-operator-vfuncs-wave863`

Wave863 script operator vfuncs saved comments/tags/signatures for five important MissionScript bytecode VM operator rows: `0x0052e180 CInstructionOP_PLUS__VFunc_00_0052e180`, `0x0052e1d0 CInstructionOP_MINUS__VFunc_00_0052e1d0`, `0x0052e220 CInstructionOP_MULTIPLY__VFunc_00_0052e220`, `0x0052e270 CInstructionOP_DIVIDE__VFunc_00_0052e270`, and `0x0052e330 CInstructionOP_CMP__VFunc_00_0052e330`. The pass corrected all five to the adjacent opcode-executor ABI, made no renames, made no function-boundary changes, and made no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0052e180 CInstructionOP_PLUS__VFunc_00_0052e180` | Corrected to `void __thiscall CInstructionOP_PLUS__VFunc_00_0052e180(void * this, void * script_state, void * data_stack, void * object_code)`. DATA dispatch-table/vtable ref `0x005e4d30`; pops two datatype operands from `data_stack`, calls datatype vtable slot `+0x04`, releases both operands, and pushes the result. |
| `0x0052e1d0 CInstructionOP_MINUS__VFunc_00_0052e1d0` | DATA ref `0x005e4d20`; same two-pop/release/push operator shape through datatype vtable slot `+0x08`. |
| `0x0052e220 CInstructionOP_MULTIPLY__VFunc_00_0052e220` | DATA ref `0x005e4d10`; same two-pop/release/push operator shape through datatype vtable slot `+0x0c`. |
| `0x0052e270 CInstructionOP_DIVIDE__VFunc_00_0052e270` | DATA ref `0x005e4d00`; same two-pop/release/push operator shape through datatype vtable slot `+0x10`. |
| `0x0052e330 CInstructionOP_CMP__VFunc_00_0052e330` | DATA ref `0x005e4c50`; reads top two datatype operands through `CScriptObjectCode__GetTop(data_stack,0/1)`, calls datatype vtable slot `+0x18`, then sets or clears bit 0 of `script_state+0x218` without popping the operands. |

Read-back evidence:

- `ApplyScriptOperatorVfuncsWave863.java dry`: `updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=0 missing=0 bad=0`.
- `ApplyScriptOperatorVfuncsWave863.java apply`: `updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=0 missing=0 bad=0`, with five `READBACK_OK` rows.
- `ApplyScriptOperatorVfuncsWave863.java final dry`: `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports: 5 metadata rows, 5 tag rows, 5 xref rows, 2205 instruction rows, and 5 decompile rows.
- Queue after Wave863: 6105 total, 5809 commented, 296 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5809/6105 = 95.15%`, strict clean-signature proxy `5809/6105 = 95.15%`.
- Next raw commentless row: `0x0052ff30 ScriptCommandRegistry__InitBuiltins`.
- Commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-150621_post_wave863_script_operator_vfuncs_verified`, 19 files, 172264327 bytes, `DiffCount=0`.

What this proves:

- The five target function rows exist in the saved Ghidra project.
- The saved signatures use the adjacent opcode-executor ABI: `void __thiscall ...(void * this, void * script_state, void * data_stack, void * object_code)`.
- The saved function comments and tags include `script-operator-vfuncs-wave863` and `wave863-readback-verified`.
- The observed bodies are static retail Ghidra evidence tied to DATA refs, decompile exports, instruction exports, and adjacent Wave573/Wave574 MissionScript opcode/datatype context.

What remains unproven:

- Exact operand order naming.
- Exact VM/data-stack/datatype layouts.
- Runtime MissionScript behavior.
- Source identity.
- BEA patching behavior.
- Rebuild parity.
