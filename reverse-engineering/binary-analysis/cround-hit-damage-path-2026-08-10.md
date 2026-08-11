# `CRound::Hit`, configured explosion creation, and `CExplosion::Hit`

Status: active, bounded semantic contract
Last updated: 2026-08-11
Evidence: MEASURED — pristine retail bytes, strict RTTI/vtables, exact data
records, dated static exports, replicated runtime carriers, and independent
PC-demo normalized bodies; SOURCE — pinned `CThing`/init layouts and virtual
order; UNKNOWN — the narrowed gates listed below.
Verdict: the conditional direct-round plus synchronous small-explosion damage
chain is closed through the same receiver; exact second-call mesh part,
expanding-radius timing, and rebuild parity remain open.
Specimen: pristine Steam `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Result

Retail function `0x004D8AE0` is `CRound::Hit`:

```cpp
void __thiscall CRound::Hit(
    CRound *this,
    CThing *otherThing,
    CCollisionReport *collisionReport);
```

The name and ABI are a joined result, not a decompiler guess. The exact
`734`-byte body (`0x004D8AE0..0x004D8DBD`) has SHA-256
`9a2fe166433abc1836ff6e628b89ae88f6475f10582a2e1117659afba2205393`
and decodes gaplessly to 228 x86 instructions. Strict RTTI places it at slot
39 in both `CRound` and `CMissile`; the inheritance census proves
`CMissile -> CRound -> CActor`. `CBattleEngine`'s independently known `Hit`
occupies the same slot. The pinned `CThing` source declares `Hit(CThing*,
CCollisionReport*)` immediately before slot-40 `Damage(float,CThing*,BOOL,int)`,
and both exits use `RET 8`.

## Direct contract recovered from the retail body

The routine first calls `CComplexThing::Hit(this, otherThing,
collisionReport)` at `0x004D8AF2`. It then applies a preliminary gate composed
of:

- round state bit `this+0x2C & 4` being clear;
- a report/target condition involving `report+0xCC`,
  `CRoundPassiveCollision` (`roundData+0x64`), and target type bit
  `0x01000000`;
- reentrancy guard `this+0x124` being zero;
- non-negative `CRoundDamage` (`roundData+0x1C`), unless the target is the
  reader at `this+0xE8`;
- `CRoundSmart` (`roundData+0x78`) being clear, or the target owner/value at
  `otherThing+0x138` differing from `this+0x11C`.

The first report branch permits a null pointer, but this is not a valid proved
damage path: `0x004D8CBC` unconditionally reads `[collisionReport]` before the
virtual call. The dispatch below is therefore bounded to the observed
valid-target, non-null-report path.

At `0x004D8CE0..0x004D8CEF`, the function invokes `otherThing` virtual slot 40
(`+0xA0`) with:

1. `roundData+0x1C` — independently identified by RTTI/apply-body evidence as
   `CRoundDamage`;
2. the `CRound *` projectile;
3. immediate `TRUE` for the damage-shields argument;
4. collision mesh-part number, or `-1`.

The same raw field table identifies `roundData+0x20` as `CRoundRearm`, `+0x50`
as `CRoundBeam`, `+0x60` as `CRoundFire`, `+0x64` as
`CRoundPassiveCollision`, and `+0x78` as `CRoundSmart`.

Direct writes and ordered consequences visible in this body are:

- conditional adjustment of projectile position `this+0x1C/+0x20/+0x24` on
  the beam path;
- set/clear of the `this+0x124` processing guard;
- a conditional increment of `[owner+0x574]+0x38`;
- target `Damage`, followed by `CBattleEngine::Rearm` for Battle Engine
  targets;
- an optional owner callback when the target newly enters its shutdown bit;
- impact-material sound and
  `CRound::ProcessImpactExplosionAndEffects(...,3,...)`;
- for `CRoundBeam`, set `this+0x2C` bit 4 and schedule event `2000` at current
  time plus `0.05`; otherwise, when `CRoundFire` is clear, dispatch projectile
  virtual slot 50 (the existing `StartDieProcess` family).

The function returns `void`. Register contents at either `RET 8` are residue,
not a typed result.

## Runtime join

The existing replicated Level-521 call-context proof records the call at
`0x004D8CEF` in both replicas. The raw arguments are damage bits `0x3D4CCCCD`
(`0.05f`), the projectile pointer, `TRUE`, and mesh part `-1`. A second
slot-39 invocation in the same bounded evidence does not contain the selected
Damage call. Therefore this document proves a conditional damage path, not
that every `CRound::Hit` invocation damages.

## Independent PC-demo corroboration

The distinct PC-demo executable (SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`)
has the same strict RTTI structure as retail: 667 types, 724 vtables, 11,777
slots, and 2,127 distinct virtual targets. Structural vtable pairing maps
retail `CRound::Hit` `0x004D8AE0` to demo `0x004D89C0`. Both functions are
734 bytes and 228 instructions. After normalizing relocated calls, globals,
and strings, their instruction sequences have zero differences. The mapped
`CBattleEngine::Hit`, `CBattleEngine::Damage`, and `CUnit::ApplyDamage` bodies
in this chain likewise have zero normalized instruction differences. This is
independent-build evidence that the retail result is not an isolated
address-label fit.

## The separate `CExplosion::Hit` damage producer

Strict RTTI places retail `0x0044BF10` at virtual slot 39 of `CExplosion`.
Its exact 479-byte body has SHA-256
`39e060a24fb364ff853e91d4825136bf8859bce85dea28d03a48c7e0928d7872`
and decodes to 152 instructions. The corresponding demo function is
`0x0044BF90`; it has the same range size, instruction boundaries, mnemonics,
register forms, 21 branches, and call topology after relocation normalization.

`CExplosion::Hit` is a second concrete slot-39/slot-40 damage path. It:

- requires a positive current radius at `this+0x7C`;
- applies the `CExplosionSmart` (`config+0x44`) allegiance/type filter;
- calls `CComplexThing::Hit`;
- computes center distance minus the target's virtual radius and clamps it to
  zero;
- optionally iterates collision-report part records and adjusts the effective
  distance for each part;
- damages a part/body only when effective distance is within the current
  radius; and
- optionally notifies the linked creator at virtual offset `+0x194` when the
  target newly shuts down.

The joined instance/config fields are:

| Instance field | Meaning | Source of join |
|---|---|---|
| `this+0x7C` | current radius | initializer plus update body |
| `this+0x80` | maximum/effective radius | configured or target radius in initializer |
| `this+0x84` | explosion configuration pointer | initializer and config reads |
| `this+0x8C` | allegiance | copied from the init payload |
| `this+0x90` | linked creator/owner reader | generic-reader init/destructor |

For effective distance `d`, maximum radius `R`, configured
`CExplosionDamage D`, and configured integer `CExplosionTime T`, the two
retail damage arms are:

```text
R <= 3:  damage = ((R - d) * D) / R
R >  3:  damage = ((R - d) * (D / T)) / R
```

Both call target virtual slot 40 with the `CExplosion*`, `TRUE`, and the
selected mesh part (or `-1`). `0x0044C0F0` advances current radius by
`R / T`, invokes the inherited shutdown slot when it reaches `R`, otherwise
queues event `3000` for the next frame. Its demo twin `0x0044C170` is also
instruction-identical after a single relocated global reference.

The existing function named `CWorldPhysicsManager__CreatePickup` at
`0x0050FF10` is not a pickup factory. Its success path allocates exactly
`0x94` bytes, calls `CComplexThing`'s base constructor, clears `+0x90`, and
installs the strict `CExplosion` vtables `0x005E4454` and `0x005E43DC`.
The bounded semantic name is therefore `CWorldPhysicsManager__CreateExplosion`.

## Exact round-to-explosion creation edge

The creation edge is now recovered. `CRound::Hit` calls
`CRound::ProcessImpactExplosionAndEffects` at `0x004D8D4E` with impact mode
`3`. The pristine four-entry jump table at `0x004DAA04` is:

| Mode | Target |
|---:|---:|
| 0 | `0x004DA6B9` |
| 1 | `0x004DA4BE` |
| 2 | `0x004DA502` |
| 3 | `0x004DA502` |

Thus the exact mode used by `CRound::Hit` reaches the factory arm. That arm:

1. reads the configured `CRoundExplosion` name from `roundData+0x08`;
2. calls `ExplosionDefinition::FindIndexByName` at `0x004DAA20`, which scans
   the registered explosion-definition list `DAT_008553F8` by record name at
   `+0x30` and returns its ordinal or `-1`;
3. passes that ordinal to `CWorldPhysicsManager::CreateExplosion` at
   `0x004DA521`;
4. derives a position/direction and creator/allegiance payload from the round,
   collision report, and owner state; and
5. invokes the new object's virtual slot 9 at `0x004DA670`, which strict RTTI
   resolves to `CExplosion::Init`.

Mode 1 performs one preliminary impact-grid call and then falls through to the
same mode-2/3 arm. Mode 0 contains a second guarded call to the same name
resolver, factory, and slot-9 initializer at `0x004DA6E4`, `0x004DA6EA`, and
`0x004DA83D`.

This proves that the valid non-null collision arm of a configured direct round
hit creates and initializes its named `CExplosion`; it is no longer merely a
numeric-fit hypothesis.

## Collision registration and synchronous same-receiver path

The formerly missing collision edge is now recovered for the small,
immediate-radius case used by the tutorial pulse. The mode-3 arm constructs the
source-shaped `CExplosionInitThing` retained in `InitThing.h`. Exact stack-field
writes show:

- `mBehaviour` is the resolved `CRoundExplosion` definition;
- `mColType` receives mode `3`, which the pinned `ECollisionType` enumeration
  names `kCollideThing`;
- `mAttachedTo` remains null and `mUseAttachedRadius` remains false;
- `mOriginator` receives the round's `this+0xEC` owner; and
- `targetOrOwner` affects the transform calculation, not `mAttachedTo` or the
  collision ignore pointer.

`CExplosion::Init @ 0x0044B930` then copies `mAttachedTo` to
`CInitCSThing::mIgnoreThing`, adds only `0x01000000` to
`mNotSeekCollisionWithBF`, takes the configured radius from `config+0x34`, and
copies allegiance. Its collision payload retains desired
`ECL_APPROX_GEOMETRY_SHAPES` and minimum `ECL_OUTER_SPHERE`, sets maximum
`ECL_APPROX_GEOMETRY_SHAPES`, response `ECR_PASSIVE`,
`mStartCollideOnNextFrame = FALSE`, and `mDoOBBForMeshCol = TRUE`. For `R <= 3`
it places the full configured radius in the live instance before calling
`CComplexThing::Init`.

That inherited initializer ends in `CThing::Init`, whose `CExplosion` slot 35
is exactly `CThing::InitCollisionSeekingThing @ 0x004F39C0`. It allocates a
`0x38`-byte `CCSPersistentThing`, installs vtable `0x005DF6D8`, stores the
explosion as `mForThing`, and dispatches slot 3. Strict RTTI fixes the relevant
persistent-component slots:

| Slot | Retail target | Recovered contract |
|---:|---:|---|
| 0 | `0x00426A20` | `CCSPersistentThing::HandleEvent`; event 3000 restores ready bit `0x400` |
| 3 | `0x004269B0` | `CCSPersistentThing::Init` |
| 5 | `0x00426A00` | previous/current MapWho-sector sweep bridge |
| 6 | `0x004264A0` | shared collision response and owner `Hit` dispatch |
| 8 | `0x00426900` | mutual thing-flag filter |

The base init at `0x00426150` encodes the response fields and sets ready bit
`0x400`. Because this explosion explicitly clears
`mStartCollideOnNextFrame`, `CCSPersistentThing::Init` does not clear that bit
or schedule delayed event `3000`; it immediately calls
`CHLCollisionDetector::ScanNeighborSectorsAndDispatchCollisions @ 0x00480A30`.
The detector scans the surrounding 3x3 MapWho sectors, excludes the component
itself, applies both slot-8 masks, and sends each surviving pair to
`DispatchCollisionEventForPair @ 0x00480ED0`. An already-overlapping pair is
handled synchronously by `HandleCollisionEnter @ 0x00480C90`, which invokes
the current component's slot 6. The shared slot-6 body requires ready bit
`0x400`, resolves the collision volumes, and terminally calls owner slot 39
(`Hit`) on both participating `CThing` objects. One of those owners is the new
`CExplosion`, so its side is exactly `CExplosion::Hit`.

The alternate lifecycle is now bounded as well. When
`mStartCollideOnNextFrame` is true, `CCSPersistentThing::Init` clears bit
`0x400` and schedules event number 3000 after the initializer's
`mTimeBeforeStart` (`NEXT_FRAME`, `-1.0f`, by default in the pinned source).
`CCSPersistentThing::HandleEvent @ 0x00426A20` restores the bit only for that
event number. Its slot-5 bridge at `0x00426A00` forwards subsequent
previous/current sector changes to `CHLCollisionDetector::ProcessMapWhoCollisionSweep`,
which visits only newly entered 3x3 MapWho cells across descending layers and
uses the same mutual-filter/pair-dispatch machinery. This closes the static
immediate-versus-delayed readiness design without claiming an exact observed
runtime event cadence.

For `Mech Pulse Hit Medium`, authored `R = 0.5` is already live during that
scan. Its radius accessor returns the configured maximum radius at
`this+0x80`; after subtracting the struck target's radius,
`CExplosion::Hit` clamps the impact-surface effective distance to zero. A
surviving, registered target that passes the two explicit flag/allegiance gates
therefore receives the full `CExplosionDamage = 1.0`. The tutorial Target Drone
has life `1.0`, so the preceding direct `CRoundDamage = 0.8` does not remove it
before this scan. Joined with the previously measured direct `1.8` loss, the
retail chain is the conditional same-receiver composition `0.8 + 1.0 = 1.8`,
not two disconnected arithmetic candidates. The exact mesh-part selected by
the second call is still a narrower open question.

## Remaining evidence boundary

Still unresolved are the source names of instance fields `this+0xE8`, `+0xEC`,
`+0x11C`, and `+0x124`; which exact gate rejected the contrasting runtime
invocation; the precise per-part collision-record layout and second-call mesh
part; targets rejected by the explicit flag/smart/allegiance gates; expanding
`R > 3` timing; behavior outside the captured runtime window; and rebuild
parity. A copied-runtime trace of both slot-40 calls would corroborate the now
closed static order, but is no longer required to discover the dispatch path.
The pinned
Stuart source is architectural/name evidence, not proof that its full body is
byte-equivalent to the retail PC implementation.

Reproduction owner:
`local-lab/cround-hit-semantic-proof-20260810-v1/`. Final `result.json` is
5,605 bytes, SHA-256
`64344240ba844ad0dbf57aefcdd8d30ef4b386db43ec6f9fc84afd438ff32615`.
Its verifier reads the pristine body, raw field-map TSV, strict RTTI/vtable and
inheritance tables, pinned source declarations, W007 exports, and both runtime
replicas; it does not consume this narrative document.

The factory-chain supplement is
`local-lab/cround-explosion-semantic-20260810-v1/`. Its 257-row pristine switch
arm dump is 10,789 bytes, SHA-256
`e919a49cc98e2a4654af593d46eeb4fa63e5d322a674d7fe35c4c1ebccda6981`;
the mode table itself is read directly from the hash-verified pristine PE.
