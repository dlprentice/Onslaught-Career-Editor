# `CWorldPhysicsManager::CreateExplosion` caller family

Status: active, bounded static contract
Last updated: 2026-08-10
Evidence: MEASURED — pristine direct-call xrefs, exact function bodies,
configuration-field adapters, and strict RTTI/vtable owners; UNKNOWN — runtime
reachability and downstream effects outside the bounded callers.
Verdict: `0x0050FF10` is the explosion factory, and all 24 direct calls are
accounted for without retaining the disproved pickup interpretation.
Specimen: pristine Steam `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Result

The correction of `0x0050FF10` from the historical
`CWorldPhysicsManager__CreatePickup` label to
`CWorldPhysicsManager__CreateExplosion` has a larger semantic consequence:
every one of its direct callers is an explosion path, not a pickup path.

The exact xref census contains 24 direct calls. Two lie in the recovered
`CRound::ProcessImpactExplosionAndEffects` switch body at `0x004DA521` and
`0x004DA6EA`; the other 22 belong to bounded functions. Strict RTTI resolves
the virtual owners/slots, while three tiny configuration adapters identify the
shared `CUnit` profile fields:

| Adapter | Profile field | Meaning |
|---:|---:|---|
| `0x00433D50` | `+0xE8` | `CUnitExplosion` |
| `0x00433D60` | `+0xEC` | `CUnitSmallExplosion` |
| `0x00433D70` | `+0xF0` | `CUnitStompExplosion` |

The callers recover as follows. Names describe only the visible bounded role;
they do not claim original source spelling.

| VA | Bounded name | Explosion source / visible role |
|---:|---|---|
| `0x0040DFB0` | `CGeneralVolume__SpawnExplosionAndDispatch` | Resolves a configured explosion name, creates it, and dispatches its initializer. |
| `0x00415450` | `CBoat__VFunc96_SpawnConfiguredSmallExplosion` | `CBoat` slot 96; uses `CUnitSmallExplosion` with boat-specific position logic. |
| `0x00417A40` | `CBuilding__VFunc50_HandleDeathAndSpawnUnitExplosion` | `CBuilding` death path; uses `CUnitExplosion`. |
| `0x00428110` | `CComponent__UpdateActivationStateAndSpawnGillClawExplosion` | `CComponent`/`CGillMHead` slot 66; activation path resolves the literal `Gill-M Claw Hit`. |
| `0x00442710` | `CDestroyableSegment__SpawnConfiguredExplosion` | Uses the segment's configured explosion definition. |
| `0x00447120` | `CDropship__VFunc66_ProcessDoorThrustersChildrenAndSmallExplosions` | `CDropship` slot 66; door/child processing includes `CUnitSmallExplosion`. |
| `0x0044CDB0` | `CFeature__VFunc14_ShutdownAndSpawnExplosion` | `CFeature` slot 14; shutdown path creates the feature-data explosion. |
| `0x0044CEE0` | `CFeature__MaybeSpawnRandomExplosionFromData` | Randomized transformed spawn from the feature-data explosion ordinal. |
| `0x0044E300` | `ExplosionSpawn__MaybeSpawnAttachedSmallExplosionFromFrame` | Frame/height-gated attached `CUnitSmallExplosion`. |
| `0x00480340` | `CHiveBoss__VFunc95_BuildSmallExplosionContextAndDispatch` | `CHiveBoss` slot 95; builds and dispatches a `CUnitSmallExplosion` context. |
| `0x00489B40` | `CInfantryUnit__VFunc50_HandleDeathExplosionAndEffects` | `CInfantryUnit` death path; uses `CUnitExplosion`. |
| `0x0049FC10` | `CMechWarspite__VFunc66_UpdateVerticalDriftAndSpawnStompExplosion` | Shared `CMech`/`CWarspite` slot 66; uses `CUnitStompExplosion`. |
| `0x004BA7F0` | `CMine__VFunc117_ReleaseChildrenAndSpawnUnitExplosion` | Releases child/script state and creates `CUnitExplosion`. |
| `0x004D7E60` | `CRocket__VFunc14_ShutdownAndSpawnBigRocketExplosion` | `CRocket` shutdown path resolves literal `Big Rocket Explosion`. |
| `0x004DEEC0` | `CSentinel__VFunc95_BuildSmallExplosionContextAndDispatch` | `CSentinel` slot 95; range/height-gated `CUnitSmallExplosion`. |
| `0x004DFAA0` | `CSimpleBuilding__VFunc66_UpdateMotionAndSpawnSmallExplosion` | Strict RTTI resolves `CSimpleBuilding` slot 66; motion/height path uses `CUnitSmallExplosion`. |
| `0x004F09B0` | `CTentacle__VFunc66_UpdateMotionAndSpawnSmallExplosion` | `CTentacle` slot 66; model/bone motion path uses `CUnitSmallExplosion`. |
| `0x004F1050` | `CTentacle__VFunc50_HandleDeathAndSpawnUnitExplosion` | `CTentacle` death path; uses `CUnitExplosion`. |
| `0x004F4920` | `CThunderHead__VFunc66_UpdateAimYawFlamethrowerAndSpawnStompExplosion` | `CThunderHead` slot 66; the long update includes `CUnitStompExplosion`. |
| `0x004F9260` | `SharedUnit__VFunc95_SpawnConfiguredSmallExplosionNearWater` | Shared slot 95 across the unit hierarchy; context/range/height-gated `CUnitSmallExplosion`. |
| `0x004F9490` | `SharedUnit__VFunc96_SpawnConfiguredSmallExplosionIfAboveWater` | Shared slot 96 across the unit hierarchy; above-water `CUnitSmallExplosion`. |
| `0x004FD230` | `CUnit__SpawnProfileUnitExplosion` | Direct helper using `CUnitExplosion` and the unit's current position/allegiance context. |

## What this corrects

Older names and review prose described these routines as pickup creation,
drop-pickup behavior, or generic dispatch because the shared callee was
misidentified. The factory body instead allocates a `0x94`-byte object and
installs the strict `CExplosion` vtables. Its callers then invoke virtual slot
9, which strict RTTI identifies as `CExplosion::Init`. The registered
definition list used around these calls is the same explosion-definition list
joined to `CRoundExplosion`.

This is enough to advance the 21 newly corrected caller rows to bounded C1 in
the tracked evidence register; `CDestroyableSegment::SpawnConfiguredExplosion`
was already corrected by the preceding round/explosion batch. Historical
full-pass reports remain dated artifacts and may retain the old pickup names.

## Boundary and reproduction

The static result proves exact direct calls, configuration-field use, virtual
owner/slot placement where listed, creation of a `CExplosion`, and the visible
initializer dispatch. It does not prove that every branch is reachable in a
released mission, which named explosion definition each authored unit selects,
the later collision targets, damage recipients, audiovisual result, or rebuild
parity.

The ignored reproduction owner is
`local-lab/cexplosion-factory-callers-20260810-v1/`. Its 24-row `xrefs.tsv` is
SHA-256
`d8dbf296bddfd882c13429d8c0f7af5003c68d6bd674a4e39e8645a6cee656d8`.
The owner contains the exact 22 caller decompiles and the three configuration
adapter bodies used by this join.
