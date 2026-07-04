# Wave1189 MissionScript Bytecode / IScript Current-Risk Review

Status: complete static current-risk comment/tag normalization; historical artifact committed
Date: 2026-06-06
Scope tag: `wave1189-missionscript-bytecode-iscript-current-risk-review`

Wave1189 accounts for `7 MissionScript bytecode/IScript current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh serialized Ghidra evidence:

- `0x0052e180 CInstructionOP_PLUS__VFunc_00_0052e180`
- `0x0052e1d0 CInstructionOP_MINUS__VFunc_00_0052e1d0`
- `0x0052e220 CInstructionOP_MULTIPLY__VFunc_00_0052e220`
- `0x0052e270 CInstructionOP_DIVIDE__VFunc_00_0052e270`
- `0x0052e330 CInstructionOP_CMP__VFunc_00_0052e330`
- `0x005333b0 IScript__Constructor`
- `0x00539f30 CMissionScriptObjectCode__ClearFields_Thunk`

The saved Ghidra names and signatures were already bounded. This wave normalized saved comments and tags only, adding rebuild-grade static-contract anchors and explicit no-noticeable-difference boundary tags. `0x0052d3d0 CAsmInstruction__SpawnFromOpcode` was reviewed as context but excluded from Wave1189 accounting because it was already accounted by Wave1120.

Two Codex read-only consults were used. Helmholtz recommended the MissionScript bytecode/IScript cluster; Sagan corrected the active counted target list by excluding the already-accounted factory row. No Cursor/Composer was used.

Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `808/1179 = 68.53%`; current risk candidates: 6166; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 371; focused threshold `15`; not Wave911 reconstruction.

Fresh exports verified `7` metadata rows, `7` tag rows, `7 xref rows`, `208 instruction rows`, and `7` decompile rows. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-164704_post_wave1189_missionscript_bytecode_iscript_current_risk_review_verified`, `19` files, `176196487` bytes, `DiffCount=0`, `HashDiffCount=0`.

## Reviewed Rows

| Address | Name | Evidence |
| --- | --- | --- |
| `0x0052e180` | `CInstructionOP_PLUS__VFunc_00_0052e180` | DATA dispatch/vtable ref `0x005e4d30`; pops two datatype operands from `data_stack`, calls datatype vtable slot `+0x04`, releases both operands through datatype slot `+0` with flag `1`, and pushes the produced datatype result. |
| `0x0052e1d0` | `CInstructionOP_MINUS__VFunc_00_0052e1d0` | DATA dispatch/vtable ref `0x005e4d20`; same operator shape through datatype vtable slot `+0x08`. |
| `0x0052e220` | `CInstructionOP_MULTIPLY__VFunc_00_0052e220` | DATA dispatch/vtable ref `0x005e4d10`; same operator shape through datatype vtable slot `+0x0c`. |
| `0x0052e270` | `CInstructionOP_DIVIDE__VFunc_00_0052e270` | DATA dispatch/vtable ref `0x005e4d00`; same operator shape through datatype vtable slot `+0x10`. |
| `0x0052e330` | `CInstructionOP_CMP__VFunc_00_0052e330` | DATA dispatch/vtable ref `0x005e4c50`; reads top two operands with `CScriptObjectCode__GetTop(data_stack,0)` and `CScriptObjectCode__GetTop(data_stack,1)`, calls datatype vtable slot `+0x18`, and sets/clears bit 0 of `script_state+0x218` without popping operands. |
| `0x005333b0` | `IScript__Constructor` | Called by `CComplexThing__SetScript` at `0x004f42a8` after a `0x3c`-byte mission-script object allocation; RET `0x8` proves ECX=this plus `owner_complex_thing` and `script_object_code`; installs vtable `0x005e4f08`, stores owner/script pointers, writes `script_object_code+0x68`, and clears local listener/state slots through `this+0x38`. |
| `0x00539f30` | `CMissionScriptObjectCode__ClearFields_Thunk` | Called by `CHud__ShutDown` at `0x00481b44`; one-instruction JMP thunk forwarding ECX `field_block` to `CMissionScriptObjectCode__ClearFields` at `0x00539f40`, so this remains a HUD script-field-block teardown bridge rather than a second ClearFields body. |

## Mutation Summary

The wave saved comment/tag normalization only: dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 tags_added=63 missing=0 bad=0`, then `updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 tags_added=63 missing=0 bad=0`, then `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.

No rename, signature change, function-boundary change, executable-byte change, BEA launch, installed-game mutation, save mutation, or runtime-file mutation occurred.

## Boundary

This wave strengthens the MissionScript bytecode/IScript static contract needed for a rebuild-grade specification and a future clean-room implementation aiming at no noticeable difference from the original game. It does not prove exact operand order naming, exact MissionScript VM/data-stack/datatype/IScript/field-block concrete layouts, runtime MissionScript behavior, runtime HUD/script teardown behavior, exact source-body identity, BEA patching behavior, gameplay/visual outcomes, rebuild parity, or no-noticeable-difference parity.

Probe token anchor: Wave1189; wave1189-missionscript-bytecode-iscript-current-risk-review; 808/1179 = 68.53%; 7 MissionScript bytecode/IScript current-risk rows; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 371; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=7 skipped=0; comment_only_updated=7; tags_added=63; final dry updated=0 skipped=7; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; CAsmInstruction__SpawnFromOpcode already accounted by Wave1120; CInstructionOP_PLUS__VFunc_00_0052e180; CInstructionOP_MINUS__VFunc_00_0052e1d0; CInstructionOP_MULTIPLY__VFunc_00_0052e220; CInstructionOP_DIVIDE__VFunc_00_0052e270; CInstructionOP_CMP__VFunc_00_0052e330; IScript__Constructor; CMissionScriptObjectCode__ClearFields_Thunk; CScriptObjectCode__GetTop; CComplexThing__SetScript; CHud__ShutDown; datatype vtable slot +0x04; datatype vtable slot +0x08; datatype vtable slot +0x0c; datatype vtable slot +0x10; datatype vtable slot +0x18; script_state+0x218; script_object_code+0x68; vtable 0x005e4f08; 0 / 0 / 0; 6411/6411 = 100.00%; 7 xref rows; 208 instruction rows; 7 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-164704_post_wave1189_missionscript_bytecode_iscript_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.
