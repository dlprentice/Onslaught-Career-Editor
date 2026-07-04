# MissionScript Command Descriptor Schema Proof

Status: static descriptor schema proof complete, not runtime proof
Last updated: 2026-06-08
Scope: `missionscript-command-descriptor-schema`

This proof converts the saved `0x0052ff30 ScriptCommandRegistry__InitBuiltins` decompile into a machine-checkable command descriptor inventory at `missionscript-command-descriptor-schema.v1.json`. It is the completed command-descriptor child lane after `missionscript-iscript-static-contract.md`, `world-thing-spawn-object-reference-proof-plan.md`, and `world-thing-spawn-copied-corpus-schema-proof.md`.

Static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

## Schema Result

The descriptor schema rebuilds from the saved Wave864/Wave903 decompile evidence, not from runtime execution:

| Field | Value |
| --- | --- |
| Source function | `0x0052ff30 ScriptCommandRegistry__InitBuiltins` |
| Schema artifact | `missionscript-command-descriptor-schema.v1.json` |
| Descriptor start | `0x0064ce50` |
| Declared slots | `144` |
| Stride | `0x40` bytes |
| Last declared slot address | `0x0064f210` |
| Slots with observed assignments | `144` |
| Observed name-field assignments | `143` |
| First observed name | `FollowWaypointWait` |
| Last observed name | `IsOverWater` |

The final declared slot at `0x0064f210` is retained as an assigned descriptor slot with no observed name-field write in this decompile. This is intentionally represented as `nameStatus: not-written-in-decompile` rather than filled with a guessed command name.

Selected descriptor examples preserved in the schema include `SpawnThing`, `PostEvent`, `LevelWon`, `Goto3PointPanCamera`, `SetGoodieState`, `GetGoodieState`, `SetSlot`, `SetSlotSave`, `ToggleCockpit`, and `SetStealth`.

## Why This Matters

This closes the finite command descriptor inventory needed before a clean-room MissionScript VM or command-dispatch prototype can be scoped. The next sibling lane should be the VM/datatype/opcode schema around `CAsmInstruction__ExecuteCall`, `CAsmInstruction__SpawnFromOpcode`, `CScriptObjectCode__Run`, datatype ids, datatype vtables, and stack/state offsets.

## Claim Boundary

This proves static descriptor-slot accounting from saved retail Ghidra evidence. It does not prove exact descriptor field layout, exact command arity, exact argument type schema, runtime command dispatch, runtime command effects, runtime MissionScript execution, full command semantics, exact VM/datatype/opcode layout, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.
