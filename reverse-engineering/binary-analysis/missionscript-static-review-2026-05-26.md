# MissionScript / IScript Static Review

Status: static-coherent system review slice
Date: 2026-05-26
Scope: `missionscript-static-review-wave903`

Wave903 is the second concrete post-100 system review after Wave900 closed the loaded Ghidra function-quality queue. It reviews the MissionScript / IScript core across saved Ghidra function-quality evidence, prior read-back waves, loose MSL asset indexes, command-reference docs, and source-mapping constraints.

Probe token anchor: Wave903; `missionscript-static-review-wave903`; static-coherent MissionScript/IScript core; `6113/6113 = 100.00%`; `ScriptCommandRegistry__InitBuiltins`; `144` command descriptor records; `0x0064ce50`; `0x0064f210`; `IScript__ScheduleEvent`; `IScript__SetSlotSave`; `IScript__LevelWon`; `CScriptObjectCode__Run`; `CScriptEventNB__PostEvent`; `CMissionScriptObjectCode__LoadAsync`; `795` loose MSL event names; `[maintainer-local-ghidra-backup-root]\BEA_20260526-095411_post_wave903_missionscript_static_review_verified`.

## Classification

MissionScript / IScript is now a static-coherent core system. The command registry, VM/datatype/opcode families, IScript handler family, event listener/object-code call-chain anchors, and loose MSL public indexes are static-reviewed and machine-checked. This is stronger than the pre-100 "strong island" wording, but it is not a full static-closed claim for every command semantic and concrete runtime layout.

| Area | Static review evidence | Boundary |
| --- | --- | --- |
| Command registry | `ScriptCommandRegistry__InitBuiltins` writes `144` contiguous `0x40`-byte command descriptor records from `0x0064ce50` through `0x0064f210`; name fields run from `s_FollowWaypointWait_0064fa14` through `s_IsOverWater_0064f234`. | Exact descriptor field schema remains bounded, not fully layout-proven. |
| IScript handlers | Current snapshot has `49` `IScript__*` functions, all commented and signature-clean, covering slot/goodie, camera/objective, vector/range, thing-value, object/audio, level/event, and schedule-event handlers. | Runtime command argument behavior and all command effects remain runtime-proof candidates. |
| VM/datatype/opcode core | Current snapshot has `37` datatype rows and `19` instruction/opcode rows, all commented and signature-clean, with Wave573/Wave574/Wave863 read-back evidence for data operations, boolean/comparison flow, and arithmetic operator dispatch. | Exact VM, data-stack, instruction, datatype object, and opcode enum layouts remain partially bounded. |
| Event/object-code runtime core | Current snapshot has `22` `CScriptObjectCode`, `13` `CScriptEventNB`, `7` `CMissionScriptObjectCode`, and `5` `CEventFunction` rows, all commented and signature-clean. These cover symbol/stack/event call helpers, listener registration/posting, async mission-script object-code loading, and callback execution anchors. | Exact object-code, event-listener, message, payload, and async-cache layouts remain partially bounded. |
| Loose MSL asset indexes | Public loose-MSL indexes cover `95` level rows, `74` rows with events, `795` event-name counts, `115` primary-complete calls, `42` secondary-complete calls, `102` primary-failed calls, `79` level-won calls, and `13` level-lost calls, plus slot and thing-reference indexes. | Loose scripts are asset/source-reference evidence unless a runtime asset-loading proof ties a specific loose file to live execution. |

## Evidence Inputs

- Queue closure: `subagents/ghidra-static-reaudit/queue/current/static-reaudit-queue.json`
- Function snapshot: `subagents/ghidra-static-reaudit/queue/current/functions_quality.tsv`
- Wave903 evidence:
  - `subagents/ghidra-static-reaudit/wave903-missionscript-static-review/missionscript-static-review-baseline.json`
  - `subagents/ghidra-static-reaudit/wave903-missionscript-static-review/missionscript-family-summary.tsv`
  - `subagents/ghidra-static-reaudit/wave903-missionscript-static-review/missionscript-function-anchors.tsv`
  - `subagents/ghidra-static-reaudit/wave903-missionscript-static-review/backup-summary.json`
- Prior saved read-back waves:
  - Wave573 datatype head
  - Wave574 opcode/bool head
  - Wave578 IScript head
  - Wave579 slot/goodie handlers
  - Wave580 camera/objective handlers
  - Wave581 vector/range handlers
  - Wave582 thing-value handlers
  - Wave584 object/audio handlers
  - Wave585 level/event handlers
  - Wave586 `CScriptEventNB`
  - Wave587 `CScriptObjectCode`
  - Wave588 `CMissionScriptObjectCode`
  - Wave863 script operator vfuncs
  - Wave864 script command registry
- Canonical docs:
  - `reverse-engineering/game-assets/msl-scripting.md`
  - `reverse-engineering/quick-reference/msl-commands.md`
  - `reverse-engineering/game-assets/mission-events-index.md`
  - `reverse-engineering/game-assets/mission-slot-usage.md`
  - `reverse-engineering/game-assets/mission-thing-usage.md`
  - `reverse-engineering/binary-analysis/functions/Script.cpp/_index.md`
- Verified read-only Ghidra project backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-095411_post_wave903_missionscript_static_review_verified`

## Function-Family Inventory

Wave903 checks 169 saved Ghidra rows from the current function-quality snapshot. Every row in the selected MissionScript/IScript family inventory has a non-empty comment, a non-`undefined` signature, and no `param_N` debt.

| Family | Rows | Static role |
| --- | ---: | --- |
| `IScript` | 49 | Command handlers and IScript object helpers. |
| `CScriptObjectCode` | 22 | VM object-code construction, stack, symbol, event-call, and run-loop helpers. |
| `CMissionScriptObjectCode` | 7 | Mission script async loader and HUD/script object-code field helpers. |
| `CScriptEventNB` | 13 | Event listener registration, event posting, event message dispatch, and cleanup. |
| `CEventFunction` | 5 | Event callback construction, clone, execute, and cleanup. |
| `CDataType` and concrete datatype families | 37 | Datatype vtables, arithmetic/comparison/assignment, and factory support. |
| `CAsmInstruction` / `CInstructionOP` | 19 | Bytecode instruction factory and opcode executors. |
| `ScriptCommandRegistry` | 1 | Built-in command registry initializer. |
| `CStatementChain` | 1 | Script statement-chain helper. |
| Slot helpers | 3 | `CCareer__SetSlot`, `CGame__SetSlot`, and `CGame__GetSlot` bridge script slots to game/career state. |
| `CEventManager` | 12 | Timed/scheduled event manager helpers used by broader event scheduling paths. |

## Practical Result

MissionScript / IScript can now be treated as a static-coherent core system for documentation, command lookup, and planning runtime probes. The next proof step is not more queue burn-down; it is targeted runtime/corpus proof for specific command effects, descriptor fields, and mission-event outcomes when those claims matter.

Static-to-proof planning now lives at `missionscript-iscript-proof-plan.md`, with the implementation-facing child contract at `missionscript-iscript-static-contract.md` and the selected object-reference child lane at `world-thing-spawn-object-reference-proof-plan.md`. The plan turns this Wave903 review plus Wave1189 bytecode/IScript and Wave1208 bool datatype evidence into bounded child lanes for command descriptor schema, IScript command effects, VM/datatype/opcode behavior, event/object-code lifecycle, loose MSL corpus linkage, mission outcome/event paths, slot/goodie/career bridges, thing/spawn/object-reference bridges, and message/objective/HUD commands. The static contract extracts the command registry, IScript handlers, VM/datatype/opcode core, event/object-code lifecycle, game/career bridge, thing/spawn/object-reference bridge, and loose MSL corpus boundaries for clean-room planning. The World / Thing / Spawn / Object-Reference Bridge Proof Plan maps MissionScript `GetThingRef` / `SpawnThing` into saved world-load, factory, thing, Unit/BattleEngine, spawner, and mesh/resource anchors. It is not runtime MissionScript proof, live loose-MSL loading proof, exact layout proof, rebuild parity, or no-noticeable-difference parity.

## What Remains Open

- Runtime MissionScript execution behavior.
- Exact `144`-record command descriptor field schema.
- Exact VM, datatype, instruction, stack, symbol-table, event-listener, message, payload, async-cache, and object-code layouts.
- Live loose-MSL loading proof for specific mission files.
- Full source-body identity and rebuild parity.
