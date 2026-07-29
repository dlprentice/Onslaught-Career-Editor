Status: active quick reference
Last updated: 2026-04-29
Source: migrated from archived Onslaught skills during the skill clean-slate pass.
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
    ├── CDXEngine (DirectX 8)     -- DXEngine.h:22
    └── CPCEngine (PC)            -- PCEngine.h:19
```

**CORRECTED 2026-07-28 — CPCEngine is a sibling of CDXEngine, not its child.**
This tree previously drew `CPCEngine (PC)` nested one level under
`CDXEngine (DirectX 8)`. That nesting is false in the pinned source:
`references/Onslaught/PCEngine.h:19` is `class CPCEngine : public CEngine` and
`references/Onslaught/DXEngine.h:22` is `class CDXEngine : public CEngine`. An
exhaustive sweep of `class C… : public …` over `references/Onslaught/*.h` finds no
derivation of `CPCEngine` from any DX class anywhere in the corpus.

Two things the corrected tree deliberately does **not** say:

- `CPCEngine` is not the engine the pinned drop selects for PC. Selection is
  compile-time at `references/Onslaught/engine.h:229-239`, and the `_DIRECTX` arm
  picks `CDXEngine` (`extern class CDXEngine ENGINE;`). `CPCEngine` is referenced
  by no other file in the corpus.
- `CPS2Engine` is **INFERRED, not SOURCE.** It appears once, as
  `extern class CPS2Engine ENGINE;` at `engine.h:237`; `PS2Engine.h` is not in the
  pinned drop, so its base class is not established here.

## Frontend Chain

```
CFrontEnd : IController          -- Frontend.h:100
    ├── CDXFrontEnd               -- DXFrontend.h:9
    └── CPCFrontEnd               -- PCFrontend.h:11
```

**CORRECTED 2026-07-28 — CPCFrontEnd is a sibling of CDXFrontEnd, not its child.**
This tree previously drew `CPCFrontEnd` nested one level under `CDXFrontEnd`.
`references/Onslaught/PCFrontend.h:11` is `class CPCFrontEnd : public CFrontEnd`
and `references/Onslaught/DXFrontend.h:9` is
`class CDXFrontEnd : public CFrontEnd`; both derive from the abstract base
declared at `references/Onslaught/Frontend.h:100`.

`CPS2FrontEnd` is **INFERRED and weaker even than CPS2Engine**: the identifier
appears nowhere in the pinned corpus. All that exists is
`#include "PS2Frontend.h"` under the `TARGET == PS2` arm at `Frontend.h:299-301`,
and that header is not in the drop.

## Storage Chain

```
CMemoryCard (abstract)            -- MemoryCard.h:27
    ├── CPCMemoryCard (STUB!)     -- PCMemoryCard.h:8
    └── CXBoxMemoryCard (full)    -- XBoxMemoryCard.h:15
```

Note added 2026-07-28: `CPS2MemoryCard` is **INFERRED**, not SOURCE — the
identifier does not appear anywhere in `references/Onslaught/`. The two PC/Xbox
leaves above it are source-backed at the lines cited.

## Thing Type Checking

```cpp
// references/Onslaught/thing.h:174 — the sole declaration in the pinned corpus
const BOOL IsA(EThingType type) const { return (type & mThingType); }
```

**CORRECTED 2026-07-28 — `IsA` is not virtual, and that was the whole point of
citing it.** This block previously read:

```cpp
// Virtual method using bitmask
virtual BOOL IsA(ULONG type) {
    return (mThingType & type) != 0;
}
```

Four things in that were wrong, all against `references/Onslaught/thing.h:174`:

| Was shown | Pinned source |
| --- | --- |
| `virtual` | non-virtual — `grep -rn 'virtual.*IsA' references/Onslaught/` finds only `BattleEngine.h:250 virtual BOOL IsAThreat()` |
| no `const` | `const` return **and** const-qualified member |
| `ULONG type` | `EThingType type` |
| `!= 0`, normalised to 0/1 | returns the raw masked value |

It is declared exactly once, on `CThing`, and is **not** created by
`DECLARE_THING_CLASS` — that macro has three use sites in the drop
(`thing.h:257`, `actor.h:13`, `BattleEngine.h:72`) and no `#define` anywhere, so
its body is outside the pinned corpus. See
[`../source-code/core/thing-system.md`](../source-code/core/thing-system.md),
corrected the same day.

## Thing Type Flags → Kill Categories

| Flag | Kill Category |
|------|---------------|
| THING_TYPE_AIR_UNIT | TK_AIRCRAFT |
| THING_TYPE_VEHICLE | TK_VEHICLES |
| THING_TYPE_INFANTRY | TK_INFANTY |
| THING_TYPE_MECH | TK_MECHS |
| THING_TYPE_EMPLACEMENT | TK_EMPLACEMENTS |
