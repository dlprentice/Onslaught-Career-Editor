# MissionScript VM / Datatype / Opcode Schema Proof

Status: static VM/datatype/opcode schema proof complete, not runtime proof
Last updated: 2026-06-08
Scope: `missionscript-vm-datatype-opcode-schema`

This proof converts saved retail Ghidra evidence from Wave573, Wave574, Wave575, Wave587, and Wave1189 into a machine-checkable MissionScript VM/datatype/opcode inventory at `missionscript-vm-datatype-opcode-schema.v1.json`. It is the sibling static schema lane after `missionscript-command-descriptor-schema-proof.md` and uses that completed descriptor table only as a bounded CALL bridge dependency.

Static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

## Schema Result

| Surface | Static result |
| --- | --- |
| Opcode factory | `0x0052d3d0 CAsmInstruction__SpawnFromOpcode` has `27` serialized opcode cases, `0x00..0x1a`, and allocates `0x0c`-byte instruction records with an observed attribute dword at instruction `+0x04`. |
| Proven opcode executors | `19` opcode cases have observed executor rows or shared no-op rows, including PLUS, MINUS, MULTIPLY, DIVIDE, PUSH, OR, AND, comparisons, CMP, JMPFALSE, POP/stop, and CALL. |
| Unknown opcode cases | `8` factory cases keep `UNPROMOTED_*` labels because the factory vtable pointer is observed but the exported pointer is not a proven function entry. |
| Datatype factory | `0x0052ec60 CDataType__CreateFromType` has `6` serialized datatype ids, `1..6`: int, float, string, bool, thing pointer, and position. |
| VM run loop | `0x00539b00 CScriptObjectCode__Run` calls instruction vtable slot 0, reads opcode via vtable slot `+0x08`, treats opcode `0x17` as the stop candidate when call depth is not positive, and enforces a `10000` instruction limit. |
| CALL bridge | `0x0052ea40 CAsmInstruction__ExecuteCall` bridges opcode execution to descriptor table `0x0064ce50`, descriptor stride `0x40`, and scratch argument array `0x0089c300`. |

Evidence rows consumed by the schema:

| Evidence | Count |
| --- | ---: |
| Wave573 metadata rows | `14` |
| Wave574 metadata rows | `15` |
| Wave574 dispatch-slot rows | `112` |
| Wave575 metadata rows | `12` |
| Wave575 datatype-vtable rows | `384` |
| Wave587 metadata rows | `22` |
| Wave587 vtable rows | `64` |
| Wave1189 metadata rows | `7` |

Observed VM/state anchors preserved in the schema include `script_state+0x218`, `script_object_code+0x68`, `runtime_state+0x0c`, `runtime_state+0x20c`, `runtime_state+0x210`, `runtime_state+0x214`, `runtime_state+0x220`, and `runtime_state+0x224`. Stack helpers from the same Wave587 family preserve the static stack-count role at `stack+0x200` and the 0x80-entry bound observed by the push helper.

## Why This Matters

This gives a clean-room interpreter planner a finite static inventory instead of scattered wave notes: opcode ids, datatype ids, selected vtable/operator slots, VM dispatch shape, state offset roles, and the CALL-to-command-descriptor bridge. Unknown opcode cases and adjacent vtable spillover stay explicit so later runtime or source-parity work can target real gaps instead of inheriting guessed names.

## Claim Boundary

This proves static VM/datatype/opcode accounting from saved retail Ghidra evidence. It does not prove runtime MissionScript execution, runtime command effects, runtime opcode behavior, exact VM layout, exact datatype layout, exact opcode layout, exact instruction object layout, exact descriptor field layout, exact source identity, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.
