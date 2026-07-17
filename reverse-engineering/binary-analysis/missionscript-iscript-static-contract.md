# MissionScript / IScript static contract

Status: bounded static evidence; not runtime script proof
Last updated: 2026-07-16

This document is the implementation-facing owner for retail MissionScript and
IScript static evidence. Historical fixture plans and command-effect rollups are
available in Git history; the retained schemas and corpus indexes below are the
current sources.

## Evidence owners

- [`missionscript-command-descriptor-schema.v1.json`](missionscript-command-descriptor-schema.v1.json)
  records the finite command descriptor table: 144 declared slots and 143
  observed name-field assignments, including the `FollowWaypointWait` /
  `IsOverWater` boundary.
- [`missionscript-vm-datatype-opcode-schema.v1.json`](missionscript-vm-datatype-opcode-schema.v1.json)
  records the bounded opcode, datatype, and VM inventory.
- [`functions/IScript.cpp.md`](functions/IScript.cpp.md),
  [`functions/ScriptObjectCode.cpp.md`](functions/ScriptObjectCode.cpp.md), and
  [`functions/EventFunction.cpp.md`](functions/EventFunction.cpp.md) retain
  function-level identities and call relationships.
- [`../game-assets/mission-scripts-index.md`](../game-assets/mission-scripts-index.md),
  [`../game-assets/mission-events-index.md`](../game-assets/mission-events-index.md),
  [`../game-assets/mission-slot-usage.md`](../game-assets/mission-slot-usage.md),
  [`../game-assets/mission-thing-usage.md`](../game-assets/mission-thing-usage.md),
  and [`../game-assets/mission-message-usage.md`](../game-assets/mission-message-usage.md)
  are aggregate copied-corpus indexes. They do not publish raw mission scripts.

## Static surfaces

| Surface | Bounded static contract |
| --- | --- |
| Command registry | `ScriptCommandRegistry__InitBuiltins` associates known command names with descriptor slots and handler entries. Exact descriptor field layout and arity remain incomplete. |
| VM dispatch | `CAsmInstruction__SpawnFromOpcode` creates instruction families; `CDataType__CreateFromType` creates datatype families; `CScriptObjectCode__Run` and `CAsmInstruction__ExecuteCall` form the interpreter/call spine. |
| Event lifecycle | `IScript__ScheduleEvent` → `CScriptEventNB__PostEvent` → `CEventFunction__Execute` → `CScriptObjectCode__CallEventDirect` is the static event path. |
| Script loading | `CMissionScriptObjectCode__StartLoadAsync` and `CMissionScriptObjectCode__LoadAsync` load script object code through a `CDXMemBuffer`; packed-versus-loose source selection remains a runtime question. |
| Object bridge | `GetThingRef` and `SpawnThing` bridge scripts to world/thing/spawner systems; corpus name matches do not prove runtime object identity or spawning. |
| Save bridge | `SetGoodieState` / `GetGoodieState` use one-based script indices. For supported displayable entries, `save_index = script_index - 1` and the true-view dword offset is `0x1F46 + 4 * save_index`. Reserved Goodie rows remain preserve-only. |
| Player/HUD/audio commands | Static handler/name evidence exists for score, stealth, cockpit, objective, message, audio, HUD, variable, camera, vector/range, and thing-value families. It does not prove visible/audible effects. |

Representative descriptor families include slot operations, objective outcome,
message/audio, Goodie state, camera/position, vector/range helpers, thing-value
helpers, HUD/variable display, and player-state/score. Duplicate descriptor
boundaries exist for `HighlightHudPart`, `UnHighlightHudPart`, `AddScore`, and
`LevelLostString`; consumers must use the schema rather than assuming command
names are unique handler identities.

## Corpus use

Copied mission inputs are allowed only as ignored local evidence. Public files
retain aggregate command/event/name usage and case-sensitive tokens. Corpus
presence establishes that a token occurs in a copied sample; it does not prove
which resource the retail runtime selects or what the command does at runtime.

## Claim boundary

This contract supports parsers, schema work, save-index disambiguation, and
scoped reconstruction planning. It does not prove runtime MissionScript
execution, command effects, event outcomes, mission win/loss behavior, visible
HUD/camera output, audio playback, live loose-script selection, exact concrete
layouts, source-body identity, executable patch behavior, or rebuild parity.
