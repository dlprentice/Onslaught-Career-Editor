# Wave1189 MissionScript Bytecode / IScript Current-Risk Readiness Note

Status: complete static current-risk comment/tag normalization; historical artifact committed
Date: 2026-06-06
Scope: `wave1189-missionscript-bytecode-iscript-current-risk-review`

Wave1189 accounts for `7 MissionScript bytecode/IScript current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator:

- `0x0052e180 CInstructionOP_PLUS__VFunc_00_0052e180`
- `0x0052e1d0 CInstructionOP_MINUS__VFunc_00_0052e1d0`
- `0x0052e220 CInstructionOP_MULTIPLY__VFunc_00_0052e220`
- `0x0052e270 CInstructionOP_DIVIDE__VFunc_00_0052e270`
- `0x0052e330 CInstructionOP_CMP__VFunc_00_0052e330`
- `0x005333b0 IScript__Constructor`
- `0x00539f30 CMissionScriptObjectCode__ClearFields_Thunk`

The saved Ghidra names/signatures were already bounded. The pass normalized saved comments and tags only; it made no rename, no signature change, no function-boundary change, and no executable-byte change.

Evidence:

- Ghidra dry/apply/final-dry: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 tags_added=63 missing=0 bad=0`, then `updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 tags_added=63 missing=0 bad=0`, then `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Fresh exports after apply: `7` metadata rows, `7` tag rows, `7 xref rows`, `208 instruction rows`, and `7` decompile rows.
- Queue refresh after apply: `6411` total functions, `6411` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N` signatures.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-164704_post_wave1189_missionscript_bytecode_iscript_current_risk_review_verified`, `19` files, `176196487` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Accounting: `808/1179 = 68.53%`, current focused candidates: 1169, live regenerated current focused candidates: 1169, remaining active focused work: 371, current risk candidates: 6166.

Static contract:

The arithmetic operator vfuncs bind the MissionScript bytecode VM operator dispatch for PLUS, MINUS, MULTIPLY, DIVIDE, and CMP through DATA dispatch/vtable refs `0x005e4d30`, `0x005e4d20`, `0x005e4d10`, `0x005e4d00`, and `0x005e4c50`. PLUS/MINUS/MULTIPLY/DIVIDE pop two datatype operands from the shared data stack, call datatype slots `+0x04`, `+0x08`, `+0x0c`, or `+0x10`, release operands through datatype slot `+0` with flag `1`, and push the result. CMP reads the top two operands through `CScriptObjectCode__GetTop(data_stack,0/1)`, calls datatype slot `+0x18`, and sets/clears bit 0 of `script_state+0x218` without popping. `IScript__Constructor` binds the script object instance link from `CComplexThing__SetScript` to vtable `0x005e4f08`, owner fields, `script_object_code+0x68`, and local listener/state initialization. `CMissionScriptObjectCode__ClearFields_Thunk` binds the HUD shutdown bridge to `CMissionScriptObjectCode__ClearFields`.

Two Codex read-only consults were used. Helmholtz recommended the MissionScript bytecode/IScript cluster; Sagan corrected the cluster by excluding already-accounted `0x0052d3d0 CAsmInstruction__SpawnFromOpcode`, leaving the seven active current-risk rows. No Cursor/Composer was used.

Mutation boundary:

- Comment/tag normalization only.
- No rename.
- No signature change.
- No function-boundary change.
- No executable-byte change.
- No BEA launch, installed-game mutation, save mutation, or runtime-file mutation.

Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference from the original game.

Not proven here: exact operand order naming, exact MissionScript VM/data-stack/datatype/IScript/field-block concrete layouts, runtime MissionScript behavior, runtime HUD/script teardown behavior, exact source-body identity, BEA patching behavior, gameplay/visual outcomes, rebuild parity, or no-noticeable-difference parity.

Probe token anchor: Wave1189; wave1189-missionscript-bytecode-iscript-current-risk-review; 808/1179 = 68.53%; 7 MissionScript bytecode/IScript current-risk rows; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 371; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=7 skipped=0; comment_only_updated=7; tags_added=63; final dry updated=0 skipped=7; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; CAsmInstruction__SpawnFromOpcode already accounted by Wave1120; CInstructionOP_PLUS__VFunc_00_0052e180; CInstructionOP_MINUS__VFunc_00_0052e1d0; CInstructionOP_MULTIPLY__VFunc_00_0052e220; CInstructionOP_DIVIDE__VFunc_00_0052e270; CInstructionOP_CMP__VFunc_00_0052e330; IScript__Constructor; CMissionScriptObjectCode__ClearFields_Thunk; CScriptObjectCode__GetTop; CComplexThing__SetScript; CHud__ShutDown; datatype vtable slot +0x04; datatype vtable slot +0x08; datatype vtable slot +0x0c; datatype vtable slot +0x10; datatype vtable slot +0x18; script_state+0x218; script_object_code+0x68; vtable 0x005e4f08; 0 / 0 / 0; 6411/6411 = 100.00%; 7 xref rows; 208 instruction rows; 7 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-164704_post_wave1189_missionscript_bytecode_iscript_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.
