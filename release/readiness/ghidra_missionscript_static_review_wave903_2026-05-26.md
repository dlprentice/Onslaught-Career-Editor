# Ghidra MissionScript / IScript Static Review Wave903 Readiness Note

Status: complete read-only static review evidence
Date: 2026-05-26
Scope: `missionscript-static-review-wave903`

Wave903 reviewed the MissionScript / IScript core after the loaded Ghidra function-quality queue reached `6113/6113 = 100.00%`. The pass records a static-coherent MissionScript/IScript core system: command registry shape, IScript handler coverage, VM/datatype/opcode families, event/object-code call-chain anchors, and loose MSL public indexes are reviewed together. It made no Ghidra metadata mutation, no executable-byte change, no save mutation, and no BEA launch.

Representative anchors:

| Area | Evidence |
| --- | --- |
| Registry | `ScriptCommandRegistry__InitBuiltins`, `144` command descriptor records, `0x40` bytes each, range `0x0064ce50` through `0x0064f210`. |
| IScript handlers | `49` current `IScript__*` rows, including `IScript__SetSlotSave`, `IScript__LevelWon`, and `IScript__ScheduleEvent`, all comment-backed and signature-clean. |
| VM/datatype/opcode | `37` datatype rows and `19` instruction/opcode rows, including Wave573/Wave574/Wave863 read-back anchors. |
| Events/object code | `CScriptObjectCode__Run`, `CScriptEventNB__PostEvent`, `CMissionScriptObjectCode__LoadAsync`, and related callback/listener/object-code families. |
| Loose MSL indexes | `795` event-name counts across the public loose-MSL event index, with slot, thing-reference, message, and text usage docs remaining asset/source-reference evidence. |

Read-only evidence:

- Queue remains closed: `6113` total, `6113` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N`.
- Function-family export: 169 MissionScript/IScript-related rows, all comment-backed and signature-clean.
- Baseline evidence: `subagents/ghidra-static-reaudit/wave903-missionscript-static-review/missionscript-static-review-baseline.json`.
- Function anchors: `subagents/ghidra-static-reaudit/wave903-missionscript-static-review/missionscript-function-anchors.tsv`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-095411_post_wave903_missionscript_static_review_verified`, 19 files, 173247367 bytes, `DiffCount=0`.

What this proves:

- MissionScript / IScript is static-coherent at the core dispatch-system level under the current evidence set.
- The static binary rows, prior read-back waves, command registry evidence, and loose MSL public indexes can be reviewed as one system rather than isolated islands.

What remains unproven:

- Runtime MissionScript execution behavior.
- Exact `144`-record command descriptor field schema.
- Exact VM/object/datatype/event/listener layouts.
- Live loose-MSL asset loading for specific mission files.
- Rebuild parity.
