# WorldPhysicsManager.cpp Functions

Status: active static function map
Last updated: 2026-08-12
Source File: `C:\dev\ONSLAUGHT2\WorldPhysicsManager.cpp` (named by the shipped image; absent from `references/Onslaught/`) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

This file holds the game's **central object factory**. Eight `Create*` entry
points sit at consecutive source lines 145–292, followed by the list
initialiser at 301–309 — the spawn spine laid out in definition order.

Rows are **measured** only: entry address, current Ghidra name, body size,
callee-popped argument count from `ret imm`, the compiler's own
`__FILE__`/`__LINE__` coordinates, and the constructor each factory invokes. No
purpose is invented; the existing names already describe these and the evidence
is consistent with them.

| Address | Current name | Bytes | Args | Source lines | Constructs via |
| --- | --- | ---: | ---: | --- | --- |
| `0x0050F4B0` | `CWorldPhysicsManager__CreateSquad` | 268 | 0 | 145–149 | `CDXMemoryManager__Alloc` ×2 |
| `0x0050F6D0` | `CWorldPhysicsManager__CreateWeaponByIndex` | 200 | 0 | 196 | `CWeapon__ctor_base` |
| `0x0050F7A0` | `CWorldPhysicsManager__CreateProjectile` | 230 | 0 | 211–213 | `CRound__ctor` ×2 |
| `0x0050F970` | `CWorldPhysicsManager__CreateSpawner` | 200 | 0 | 230 | `CSpawnerThng__Constructor` |
| `0x0050FA40` | `CWorldPhysicsManager__CreateCharacter` | 590 | 0 | 247–251 | `CUnit__ctor_base` ×3 |
| `0x0050FF10` | `CWorldPhysicsManager__CreatePickup` | 152 | 0 | 265 | `CComplexThing__ctor_base` |
| `0x00510060` | `CWorldPhysicsManager__CreateEffect` | 140 | 0 | 278 | `CComplexThing__ctor_base` |
| `0x00510150` | `CWorldPhysicsManager__CreateTrigger` | 165 | 0 | 292 | `CComplexThing__ctor_base` |
| `0x005102A0` | `CWorldPhysicsManager__InitializeLists` | 626 | 0 | 301–309 | `CDXMemoryManager__Alloc` ×9, `CSPtrSet__Init` ×9 |

## What the shape shows

Three tiers are visible in the constructor column, and they cost nothing to read:

- **`CRound__ctor` ×2** for projectiles and **`CUnit__ctor_base` ×3** for
  characters — multiple constructor calls in one factory, so these branch on a
  subtype before constructing.
- **`CComplexThing__ctor_base`** shared by pickups, effects and triggers — three
  distinct game concepts built from one base class, each in a small body of
  140–165 bytes. They are thin wrappers over a common thing.
- **`CWeapon__ctor_base`** and **`CSpawnerThng__Constructor`** each used once.

`InitializeLists` performs nine allocations paired with nine `CSPtrSet__Init`
calls, so the manager owns **nine pointer sets** — one plausible reading is one
per spawnable category, but the mapping is not established here.

This connects directly to promoted work: `CRound__ctor` is the constructor for
the `CRound` family whose slot-0 and slot-66 runtime contracts are admitted in
Generations 21–23, and `CComplexThing` is the base the collision-component
identities sit under.

## Counting note

The per-file ranking in
[the coordinate report](../pc-native-source-coordinates-2026-08-12.md) counts
coordinate rows, not functions: this file shows 21 there and 55
coordinate-carrying functions in total, of which these nine were undocumented.
See that report's factory-bias section for why allocation sites select for
factories.

## Open

- No behaviour, no argument contracts, no failure paths. The factories all take
  zero stack arguments, so their inputs arrive through `this` or globals and are
  unread here.
- What the nine pointer sets in `InitializeLists` correspond to.
- Whether the multi-constructor factories branch on a type enum, and where it
  comes from.
