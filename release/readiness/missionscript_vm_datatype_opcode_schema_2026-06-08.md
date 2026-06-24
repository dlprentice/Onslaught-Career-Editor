# MissionScript VM / Datatype / Opcode Schema Proof

Status: static VM/datatype/opcode schema proof complete, not runtime proof
Date: 2026-06-08
Scope: `missionscript-vm-datatype-opcode-schema`

The MissionScript VM/datatype/opcode schema proof adds `missionscript-vm-datatype-opcode-schema.v1.json`, `missionscript-vm-datatype-opcode-schema-proof.md`, lore mirrors, and `tools/missionscript_vm_datatype_opcode_schema_probe.py`. It uses saved Wave573, Wave574, Wave575, Wave587, and Wave1189 static Ghidra evidence only.

Static closeout remains unchanged: `6411/6411 = 100.00%`, static debt `0 / 0 / 0`, expanded post-100 static surface `1560/1560 = 100.00%`, active current-risk focused accounting `1179/1179 = 100.00%`, remaining active focused work `0`, and latest verified Ghidra backup `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Representative anchors:

| Anchor | Evidence |
| --- | --- |
| `0x0052d3d0 CAsmInstruction__SpawnFromOpcode` | `27` opcode cases, `0x00..0x1a`, `0x0c`-byte instruction allocation, unknown-opcode fatal path. |
| `0x0052ec60 CDataType__CreateFromType` | `6` datatype ids, `1..6`, for int, float, string, bool, thing pointer, and position factory cases. |
| `0x00539b00 CScriptObjectCode__Run` | Dispatches instruction vtable slot 0, reads opcode through slot `+0x08`, checks opcode `0x17`, and enforces the `10000` instruction limit. |
| `0x0052ea40 CAsmInstruction__ExecuteCall` | Bridges to descriptor table `0x0064ce50`, stride `0x40`, and scratch argument array `0x0089c300`. |
| `script_state+0x218` / `script_object_code+0x68` | Static state/back-pointer anchors retained for clean-room planning only. |

What this proves:

- The finite opcode factory and datatype factory cases are captured in a generated schema.
- Proven opcode executor rows, shared no-op rows, and unknown/unpromoted opcode cases are separated.
- VM run-loop and CALL descriptor bridge roles are recorded without claiming exact concrete layouts.
- The schema is public-safe and machine-checkable from tracked saved evidence.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime opcode behavior.
- Exact VM/datatype/opcode/instruction-object/descriptor field layouts.
- Exact source identity.
- BEA patching behavior.
- Visual QA, Godot parity, rebuild parity, and no-noticeable-difference parity.
