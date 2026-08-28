# WorldPhysicsManager.cpp Functions

Status: active static function map
Last updated: 2026-08-28
Source File: `C:\dev\ONSLAUGHT2\WorldPhysicsManager.cpp` (named by the shipped image; absent from `references/Onslaught/`) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

This file holds the game's **central object factory**. The 26-way unit-shell
factory occupies source lines 75–99 (with no selector-11 case/source line 84),
then eight `Create*` entry points sit at source lines 145–292, followed by the
list initialiser at 301–309 — the spawn spine laid out in definition order.

Rows are **measured** only: entry address, current or independently corrected
identity, body size,
callee-popped byte count from `ret imm`, the compiler's own
`__FILE__`/`__LINE__` coordinates, and the constructor each factory invokes. No
purpose is inferred from source coordinates alone. The `0x0050FF10` row now
matches the separately gated live-Ghidra explosion identity; see
[`cexplosion-factory-callers-2026-08-10.md`](../cexplosion-factory-callers-2026-08-10.md).

The `0x00510060` and `0x00510150` rows carried `CreateEffect` and
`CreateTrigger` until 2026-08-17, when the name cohort recorded in
[`name-cohort-promotion-manifest-2026-08-17.tsv`](../name-cohort-promotion-manifest-2026-08-17.tsv)
replaced both suffixes with the product class each factory actually builds.
`0x00510060` installs vtable `0x005E45E0`, whose COL at `0x006184C0` names
`.?AVCFeature@@`, and that vtable's slot 7 returns the shipped literal
`CFeature` at `0x0063DA28`. `0x00510150` installs vtable `0x005E477C`, COL
`0x00618538` naming `.?AVCHazard@@`, slot 7 returning the shipped literal
`CHazard` at `0x0063DA50`. No `CTrigger` or `CreateTrigger` string exists
anywhere in the image. The `CWorldPhysicsManager` prefix itself has no RTTI and
rests only on the alloc-site path `C:\dev\ONSLAUGHT2\WorldPhysicsManager.cpp`.

| Address | Current or corrected identity | Bytes | `ret imm` bytes | Source lines | Constructs via |
| --- | --- | ---: | ---: | --- | --- |
| `0x0050DF80` | `CWorldPhysicsManager__CreateThingByType` | 2,164 | 0 | 75–99 | definition ordinal → row `+0xE0` selector → one of 25 concrete unit shells; selector 11 returns null |
| `0x0050F4B0` | `CWorldPhysicsManager__CreateSquad` | 268 | 0 | 145–149 | `CDXMemoryManager__Alloc` ×2 |
| `0x0050F6D0` | `CWorldPhysicsManager__CreateWeaponByIndex` | 200 | 0 | 196 | `CWeapon__ctor_base` |
| `0x0050F7A0` | `CWorldPhysicsManager__CreateProjectile` | 230 | 0 | 211–213 | `CRound__ctor` ×2 |
| `0x0050F970` | `CWorldPhysicsManager__CreateSpawner` | 200 | 0 | 230 | `CSpawnerThng__Constructor` |
| `0x0050FA40` | `CWorldPhysicsManager__CreateCharacter` | 590 | 0 | 247–251 | `CUnit__ctor_base` ×3 |
| `0x0050FF10` | `CWorldPhysicsManager__CreateExplosion` | 152 | 0 | 265 | `CComplexThing__ctor_base`, then strict `CExplosion` vtables |
| `0x00510060` | `CWorldPhysicsManager__CreateFeature` | 140 | 0 | 278 | `CComplexThing__ctor_base` |
| `0x00510150` | `CWorldPhysicsManager__CreateHazard` | 165 | 0 | 292 | `CComplexThing__ctor_base` |
| `0x005102A0` | `CWorldPhysicsManager__InitializeLists` | 626 | 0 | 301–309 | `CDXMemoryManager__Alloc` ×9, `CSPtrSet__Init` ×9 |

## What the shape shows

`CreateThingByType` consumes a definition **ordinal**, walks the ordered
registry, reads the selected row's raw class selector at `+0xE0`, and dispatches
selectors `0..25` with selector `11` absent. Its exact selector,
RTTI class, and separate squad/size-policy matrix is owned by
[`spawner-squad-cycle.md`](../../game-mechanics/spawner-squad-cycle.md). The
factory returns a constructed class shell; its caller owns the later definition
initializer and world/squad publication.

Three tiers are visible in the constructor column, and they cost nothing to read:

- **`CRound__ctor` ×2** for projectiles and **`CUnit__ctor_base` ×3** for
  characters — multiple constructor calls in one factory, so these branch on a
  subtype before constructing.
- **`CComplexThing__ctor_base`** shared by explosions, features and hazards —
  three factory paths built from one base class, each in a small body of
  140–165 bytes. All three now carry a product-class anchor: the explosion row
  has the strict-RTTI/vtable proof cited above, and the feature and hazard rows
  have the COL-plus-shipped-literal pair recorded above. What none of the three
  establishes is a complete construction contract; only the class each factory
  returns is measured.
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

- Complete behaviour and failure paths remain open. A zero `ret imm` means the
  callee pops no argument bytes; it does **not** mean a caller-cleaned cdecl has
  no arguments. All 24 direct callers of `0x0050FF10` push one dword and clean
  four bytes after the call, and two round callers pass the result of
  `ExplosionDefinition::FindIndexByName`. That supports the bounded signature
  `void * __cdecl CWorldPhysicsManager__CreateExplosion(int
  explosion_definition_index)`; it does not establish the other factories'
  argument contracts.
- What the nine pointer sets in `InitializeLists` correspond to.
- Whether the multi-constructor factories branch on a type enum, and where it
  comes from.
