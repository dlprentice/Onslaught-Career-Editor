Status: active quick reference
Last updated: 2026-04-29
Source: migrated from archived Codex Onslaught skills during the skill clean-slate pass.
Summary: Source class hierarchy and thing-type lookup.
# Class Hierarchies

## Core Object Chain

```
CMonitor (observer pattern)
  └── CThing (base game object)
        └── CComplexThing (rotation, animation)
              └── CActor (movement, physics)
                    └── CUnit (health, damage)
                          └── CBattleEngine (player mech)
```

## Engine Chain

```
CEngine (abstract)
    ├── CDXEngine (DirectX 8)
    │     └── CPCEngine (PC)
    └── CPS2Engine (PS2)
```

## Frontend Chain

```
CFrontEnd : IController
    ├── CDXFrontEnd
    │     └── CPCFrontEnd
    └── CPS2FrontEnd
```

## Storage Chain

```
CMemoryCard (abstract)
    ├── CPCMemoryCard (STUB!)
    ├── CXBoxMemoryCard (full)
    └── CPS2MemoryCard
```

## Thing Type Checking

```cpp
// Virtual method using bitmask
virtual BOOL IsA(ULONG type) {
    return (mThingType & type) != 0;
}
```

## Thing Type Flags → Kill Categories

| Flag | Kill Category |
|------|---------------|
| THING_TYPE_AIR_UNIT | TK_AIRCRAFT |
| THING_TYPE_VEHICLE | TK_VEHICLES |
| THING_TYPE_INFANTRY | TK_INFANTY |
| THING_TYPE_MECH | TK_MECHS |
| THING_TYPE_EMPLACEMENT | TK_EMPLACEMENTS |
