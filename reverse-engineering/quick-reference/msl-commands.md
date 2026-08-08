Status: active quick reference
Last updated: 2026-07-29
Source: user-owned retail MissionScript corpus and current tracked RE contracts.
Summary: MSL command and mission scripting verb lookup.
# MSL Command Reference

This file is a syntax and verb lookup over the authored MissionScript corpus.
Current static owners are the
[`MissionScript / IScript contract`](../binary-analysis/missionscript-iscript-static-contract.md),
the retained [`VM/datatype/opcode schema`](../binary-analysis/missionscript-vm-datatype-opcode-schema.v1.json),
and the exact
[`144-entry native registry`](../ghidra-functions.md#appendix-a-complete-144-entry-missionscript-native-registry).
A registry binding or corpus occurrence does not by itself prove runtime effects,
resource selection, or rebuild parity.

## Contents
- [Mission Outcome](#mission-outcome)
- [Object References](#object-references)
- [Entity Control](#entity-control)
- [Spawning](#spawning)
- [Dialog](#dialog)
- [Career Integration](#career-integration)
- [Distance/Position](#distanceposition)
- [Timing](#timing)
- [Control Flow](#control-flow)
- [Events](#events)
- [Thing Types](#thing-types)

## Mission Outcome

```msl
LevelWon();
LevelLostString(TEXT_CONSTANT);
PrimaryObjectiveComplete(num, TEXT);
PrimaryObjectiveFailed(num, TEXT);
SecondaryObjectiveComplete(num, TEXT);
SecondaryObjectiveFailed(num, TEXT);
```

## Object References

```msl
player = GetPlayer(1);
thing = GetThingRef("Object Name");
component = GetComponent(index);
```

## Entity Control

```msl
thing.Activate();
thing.Deactivate();
thing.Shutdown();
thing.SetVulnerable(TRUE/FALSE);
thing.SetObjective();
thing.UnsetObjective();
thing.EnableWeapon("Weapon Name");
thing.DisableWeapon("Weapon Name");
thing.EnableFlightMode();
thing.DisableFlightMode();
health = thing.GetHealth();
thing.SetHealth(value);
SetAIState(AI_OFF/AI_ON/AI_NORMAL/AI_DEFENSIVE);
```

## Spawning

```msl
thing.SpawnThing("Unit Type", "Spawner", count, "Name");
```

## Dialog

```msl
PlayCharMessage(CHARACTER, MSG, delay);
PlayCharMessageWait(CHARACTER, MSG, delay);
AddHelpMessage(HELP_CONSTANT);
```

## Characters

| Constant | Character |
|----------|-----------|
| P_TATIANA | Tatiana |
| P_KRAMER | Commander |
| P_RADAR | Radar op |
| P_TECHNICIAN | Tech |
| P_SURT | Surt |
| P_CARVER | Carver |

## Career Integration

```msl
GetSlot(SLOT_CONSTANT)         // Returns bool
SetSlot(SLOT, TRUE);           // Session only
SetSlotSave(SLOT, TRUE);       // Persists
GetGoodieState(id);
SetGoodieState(id, GOODIE_NEW);
AddScore(points);
```

## Tech Slots

| Slot | Constant |
|------|----------|
| 61 | SLOT_500_ROCKET |
| 62 | SLOT_500_SUB |
| 63-66 | SLOT_TUTORIAL_1-4 |

## Distance/Position

```msl
dist = thing1.GetDistToObj(thing2);
pos = CreatePosition(x, y, z);
thing.Teleport(position);
```

## Timing

```msl
Pause(seconds);
GameTime();
```

## Counting

```msl
count = GetNumUnits(BEHAVIOUR, ALLEGIANCE);
ratio = GetRatioBattleLineNodes(ALLEGIANCE);
// Note: FRIENDLY_ALLIGENCE (typo preserved)
```

## Control Flow

```msl
if (cond) { } else { }
switch(var) { case 0: { } }
while(cond) { }
for(n = 1; n <= 10; n = n + 1) { }
do_once { }  // Execute once only
```

## Events

```msl
event("Event Name") { }
PostEvent("Event Name");
```

## Thing Types

| Constant | Value |
|----------|-------|
| THING_TYPE_BATTLE_ENGINE | 8 |
| THING_TYPE_UNIT | 16 |
| THING_TYPE_MECH | 2049 |
| THING_TYPE_INFANTRY | 16384 |
| THING_TYPE_NAVAL | 32768 |
