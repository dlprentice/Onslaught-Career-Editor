# `CRound::Hit`, configured explosion creation, and `CExplosion::Hit`

Status: active, bounded semantic contract
Last updated: 2026-09-08
Evidence: MEASURED — pristine retail bytes, strict RTTI/vtables, exact data
records, dated static exports, replicated runtime carriers, and independent
PC-demo normalized bodies; SOURCE — pinned `CThing`/init layouts and virtual
order; UNKNOWN — the narrowed gates listed below.
Verdict: direct-round damage byte-provably precedes the synchronous small-
explosion neighbor scan, but the explosion is spatial rather than bound to the
original receiver. Its configured damage is a radial maximum, not an
unconditional second call. The PC MapWho traversal/filter chain, four modeled
Level 100 serialized geometry inputs, Warehouse's ordered segmented report, and
the terminal Target Tank's continued eligibility with part `-1` have bounded
static contracts. Live resource selection,
receiver order, per-shot falloff bits, expanding-radius timing, and broader parity remain open.
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
- computes center distance minus the target's virtual radius for the ordinary
  part-`-1` path;
- for a controller-bearing unit with a valid positive-count collision report,
  replaces that distance with maximum radius plus each stored part distance;
- clamps the selected distance to zero;
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

### Retained-trace slot-40 carrier proof (2026-08-12)

Three independent retained TTD call-context sessions now join the two pristine
internal call sites to ten concrete target dispatches. Eight small-arm calls
leave `0x0044C08E`; two large-arm calls leave `0x0044C061`. The receivers are
six `CUnit`, two `CTree`, and two `CBattleEngine` instances. In every observed
call, the source stack argument equals the current `CExplosion*`,
`applyShields=1`, and `meshPartIndex=-1`. Eight callee returns validate; the two
large-arm returns remain raw orphans. The small arm carries float bits
`0x3F000000`; the two observed large-arm values are `0x3C9429EE` and
`0x3BD92866`.

Six `CUnit` observations pair a preceding direct round call with the explosion
call on the same receiver. Their direct mesh parts are `8, 0, 1, 0, 0, 8`,
while all six explosion calls carry `-1`. That refutes reuse of the direct-hit
part for these pairs. A deliberately poisoned replay changed only the expected
`CUnit` count from six to seven: it preserved the event projection, exited 10,
failed its expectations/pairing/collector gates, and published no READY. This
is the negative instrument control, not positive carrier evidence.

The exact proof is
`local-lab/cexplosion-hit-existing-trace-20260812-v1/proof-v1/proof.ready.json`
(25,043 bytes, SHA-256
`ec7c4bcec3f11357de5afb8482179f67e030623bce38374be0afe8bf82620b66`).
Generation 20 admits the result as `C2_BOUNDED_RUNTIME` only after a 16-rule
probe refuter survived. Its canonical READY is
`13326fed25845e2351a2c68b57afe1bf2593786d2feb5f9e7d045fb7120a44ea`;
the full-replay selector is 15,037 bytes / SHA-256
`268b13a12de25fe5d6a648f17dd72699a441f968d8fef1d3d632c79b8edfccf1`.
The campaign keeps the address-suffixed
`CExplosion__VFunc_39_0044bf10` name and a `PARTIAL_CONTRACT` rebuild mapping.

This is a bounded internal-call carrier proof, not a complete
`CExplosion::Hit` envelope. It does not observe the function entry, its return,
owned writes, a nonnegative explosion part, a controller-bearing segmented
receiver, or the Level 100 Warehouse. The multi-gigabyte traces are bound by
their retained wrapper hashes and current sizes rather than rehashed by this
proof. No game, trace, Ghidra project, or executable was mutated.

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

## Collision registration and synchronous spatial-scan path

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

### Exact MapWho traversal and candidate gates

The immediate collision scan is not the public radius-query API. The
radius-`0.5f` explosion is inserted at MapWho level 4 (8-unit cells), then the
detector visits the valid 3-by-3 X/Y neighborhood at levels 4 through 0, with X
outermost and ascending and Y innermost and ascending. At the starting level,
finer descendants are visited depth-first in child-index order before the
cell's normal linked list. Normal lists are walked head-to-tail; insertion is
at the head, and the released sorter can move selected owners toward the tail.
There is no distance, definition-name, or authored-order result sort.

Each enumerated owner must expose a persistent collision component, differ
from the explosion component, and pass both components' type masks. The pair
dispatcher then applies its outer-radius/time path, cell-distance gate, strict
3-D outer-sphere overlap, readiness, cross-ignore, invisibility, conditional
dying/type, collision-level negotiation, and selected shape predicate. A shape
success calls `CExplosion::Hit(candidate, report)` first and
`candidate->Hit(explosion, report)` second with the same report; scanning then
continues. No generic active/life/dead, creator, or allegiance test exists in
the broadphase. Allegiance is a later `CExplosion::Hit` smart filter. The
`Mech Pulse Hit Medium` record omits field 11 and the record constructor
initializes its smart field to zero, so that filter is disabled for this exact
definition.

This distinction preserves two equality rules: the pair dispatcher's immediate
outer-overlap comparison is strict, while the selected `CSphere` predicate and
the later radial-damage test admit equality. Enumeration or mutual-mask success
alone therefore proves neither a collision callback nor damage.

### Serialized geometry and terminal Target Tank behavior

The September 8 materializer review corrected this section's previous claim of
exact normal-live radii. Its August 27 input note had recomputed geometry from
part corners through the alternate `CMesh::Load` path and explicitly left live
returned words open. Those static estimates differ by one float step from some
stored CMSH words; they are not observed instance values. The raw inputs are:

| Definition | BBOX origin X / Y / Z words | BBOX radius word | Mesh render-radius word |
|---|---|---|---|
| Target Tank | `3D30CB70 / BE24C554 / BEC4D063` | `3FAB28C8` | `3FC487A7` |
| Target Truck | `BB8D5D80 / BD4D6660 / BEF307E4` | `3FCFD61C` | `3FE83ED3` |
| Target Drone | `BBA22500 / 3EA56398 / BCD78710` | `3FC26850` | `3FE9F832` |
| Warehouse | `3CF5E900 / 400739E3 / BFF19379` | `40F2BEF5` | `41088DDE` |

The serialized-resource path at `0x004AAB90` reads the CMSH header and global
BBOX, while `0x004DC370` copies resource `+0x164` into renderer `+0x20` with
integer stores at `0x004DC571/0x004DC579`. The four-byte getter
`[0x004DCAF0,0x004DCAF4)` returns that field unchanged (body SHA-256
`c1585f87b231917fb748c8cb8dc459d10a157139bd48fb142b516af0fef2c3ae`).
The distinct slot-17 path at `0x004F3940` reads BBOX radius through `0x004DE060`.
The inherited GroundUnit sphere installer `[0x0047C8E0,0x0047C964)` stores that
returned float, multiplies by stored `0.8f` (`3F4CCCCD` at `0x005D85F8`), then
stores the sphere radius; body SHA-256
`555aa25b26f25bf13d9f563aa6362576330a6b077f0b152c6550b11429db0304`.
Plane and Building use the base sphere without that multiplier. This is the
checked initialization path, not a new live resource-selection observation.

The contact catalog preserves these raw words and the separate class scale in
`Level100ContactDefinition.FloatGeometry`. Instance position/basis and centre
rounding remain separate work. The primary sphere controls collision admission;
the ordinary part-`-1` falloff uses owner-position distance minus the distinct
virtual render radius. The segmented-report arm below uses its own distances.
Reconstructing either from quantized parts or copying the old estimate table
would discard the original input.

A direct Target Tank hit that first crosses life below zero sets `TF_DYING`
and queues delayed shutdown for manager time plus exact `0.5f`; it does not
remove MapWho/collision ownership, clear readiness, set invisibility, or bypass
the subsequent mode-3 helper. The tank lacks the dying/type veto bit and the
explosion mask bit, retains vulnerability, and normally has no segment
controller (`unit+0x178 == 0`). If its primary sphere and radial gate accept
the new explosion, it therefore receives part `-1` damage even while dying.
The second call can lower stored life again but cannot dispatch death twice.
The scanner also continues to other eligible receivers; the original target is
neither guaranteed first nor unique.

### Warehouse segmented explosion report

The September 8 pristine review closes the static carrier but not any particular
shot's selected parts. `CBuilding::Init` at `0x00417190` writes collision minimum
and maximum level 2 at `0x004171b7/0x004171ba`. The shared resolver's OBB flag
sets the selected Warehouse mesh-volume `+0x18` at `0x004265fd`. Mesh/sphere
dispatch reaches `0x004ac6e0`, whose bounds arm calls `0x004ac140` for each
eligible part in ascending native order. Passive bounds testing calls
`Geometry__DistanceOutsideAabb` at `0x00479770`, subtracts the effective sphere
radius and stores the accepted signed distance at report `+0xc4`.

The append block `[0x004aca40,0x004acada)` (SHA-256
`f9b60939e01e50726de01de7e5f107c6314a7a9e18f552161edd276e0d321f28`)
copies the selected part-context `+0x88` into `report+0x68[i]`, copies that
signed distance into `report+0xac[i]`, and stops at six contacts. Referenced
geometry does not replace the selected part's identity. This is an ordered
multi-part report, not the direct projectile's single selected triangle/part.

The segmented `CExplosion::Hit` block `[0x0044bfd3,0x0044bfef)` (SHA-256
`1690f50a8e02b7fd17600eb6def858e6f138d1ff50c847ce9203bb5a077a98f9`)
selects the report part and stores `maximumRadius + report.distance[i]` as a
float32 before the shared zero clamp and radius gate. It applies the configured
falloff separately to each row in stored order. Owner-centre/render-radius
distance belongs to the other arm and must not replace these part distances.

Warehouse's damage override `[0x004179a0,0x00417a1f)` (SHA-256
`8c5b53ba2103a1e649299af8ebb3634e9ada49f4b3a75a6cccf11220e0bf5ead`)
forwards unchanged damage arguments to `0x004f9a90` when its segment controller
exists, even while dying. That controller's `[0x00444030,0x00444063)` entry
(SHA-256 `581e797a9ab59bdbc2fb24c0ce3de629e9c003b3335196b728c8c3a49d9d5667`)
sends part `-1` past segment damage and destruction evaluation to the later
threshold check. Part `-1` therefore cannot stand in for aggregate Warehouse
damage. The current combined Pulse amount assigned to one direct-hit part is
still an approximation that this separate report operation must replace.

The selected Warehouse mesh has 28 parts, including six geometry references.
All parts have one HPOS/HORI hierarchy frame and 101 zero VHFM entries, but only
ten have a CORI cache record. Contact schema v6 preserves all these original
records separately from the resolved, quantized preview. An absent CORI is not
an identity matrix. The normal collision path uses the animation-aware runtime
pose cache: collision-volume `+0x1c` is the ignore-animation flag, distinct from
the fixed-transform flag at `+0x20`. `SetPartBounds` selects `0x004b4de0`, whose
normal-cache branch evaluates the hierarchy through `0x004b5330` and then applies
the owner pose. It does not simply read the serialized CPOS/CORI values.

The original [mesh pose arithmetic](../../rebuild/OnslaughtRebuild.Core/RetailMeshPartPose.cs)
implements the bounded, single-frame normal-cache composition under an explicit
53-bit round-to-nearest assumption. Hierarchy and owner matrix products have
different accumulation orders. Both retain the X position dot through
translation, while Y/Z dots receive float32 stores first. Initial interpolation
still adds positive zero and can normalize negative zero. The half-open pins are
`[0x004b554b,0x004b55d0)` HPOS SHA-256
`931f404a8737a66e9d9af59af89e208077d0a2c967d2fee047942a0df4a1944c`,
`[0x004b55d0,0x004b57ae)` HORI SHA-256
`615dac697ae79717071e3bbbd811c9bf084a8f74c1bb348432dfbe46ab7ff27e`,
`[0x004b57ef,0x004b59af)` hierarchy composition SHA-256
`6c58928375da8cec09558da332bded657c28eb1d37a53b4ecaaf6af8c41c0d7e`,
and `[0x004b4ef2,0x004b50bb)` owner tail SHA-256
`dbc94feb51aeda7dffdaabb87bb69215c1f0e6b3b5b0d9a2969b7f410e993caf`.
All actual Warehouse hierarchy parents have identity orientation; rotated leaves
do not provide a rotated-parent runtime sample. The focused tests combine raw
Warehouse inputs and explicitly synthetic cancellation/store discriminators.
This arithmetic is not yet connected to a runtime explosion scan. Cache refresh,
controller-modified poses, early-tick equivalence and live FPU state remain open.

Actual row count, part IDs and distance words depend on explosion position,
pose-cache transforms, activity and shape selection. A useful copied-runtime
check records report `+0x80`, six `+0x68/+0xac` pairs and the outgoing damage
arguments through `0x004179a0 -> 0x004f9a90 -> 0x00444030`; the retained
centreline hit count does not establish those values.

## Remaining `CExplosion` virtual tail

The two short virtuals adjacent to `GetRadius`, `Hit`, and `Move` are now
resolved at the same bounded static level:

- slot 67 `0x0044C170` is `CExplosion::GetConfiguredDamage`. Its complete
  10-byte/three-instruction body loads the configuration pointer at
  `this+0x84`, returns the float at `config+0x38`, and performs no write or
  call. The raw explosion field table independently identifies `+0x38` as
  `CExplosionDamage`. The body SHA-256 is
  `31b08b4ea68950894c92bf97bbba0b87722e6d2e32de1fd0dbe321c064f457cc`.
- inherited slot 38 `0x0044C180` is `CExplosion::SetThingType`. The pinned
  `CThing` source fixes slot 38 as `SetThingType(ULONG)`, while strict RTTI
  places this override at that slot in `CExplosion`. The complete 54-byte,
  14-instruction body ORs the caller mask with `0x01000000`; when the joined
  configured damage is strictly greater than `3.0f`, it also ORs
  `0x00200000` (`THING_TYPE_CAN_DESTROY_TREES`), then stores the inherited
  base mask `0x80000001` plus those bits at `this+0x34`. The
  `0x01000000` bit is also the exact type excluded from an explosion's
  collision-seeking mask, and the tree collision body tests the same bit on
  its other thing; its source enum token remains unclaimed. The body SHA-256
  is `fb5debd84f7db05a5b16dcb80da7b33143b8a2a22f18d5d253d4f2c8e139a531`.

This closes the visible accessor/type-classification contracts without
claiming an original declaration for the class-specific slot 67 name or a
runtime observation of the greater-than-three tree-destruction branch.

For `Mech Pulse Hit Medium`, authored `R = 0.5` is already live during that
scan. The original direct-hit target is used as an impact-orientation input;
it is not installed as an exclusive explosion receiver. Each surviving
MapWho candidate is independently dispatched. `CExplosion::Hit` subtracts the
candidate's virtual `GetRadius`, clamps negative effective distance `d` to
zero, admits `d <= R`, and for this small blast computes
`((R-d) * 1.0) / R`. Full `1.0` therefore requires `d=0`; equality at `d=0.5`
produces zero damage. Existing traces prove six direct-then-explosion
same-receiver `CUnit` pairs with explosion part `-1`; static Target Tank
construction now closes that part and continued terminal eligibility, but a
natural Level 100 trace is still required for actual receiver order and
per-shot damage bits.

## Bounded reconstruction mapping

The pre-mapping Core path passed aggregate `PulseDamageBits = 1.8` through one
`ApplyRoundHit` call. That reproduced the final Target Tank life but erased the
proved intermediate store: a first hit went directly from `6.0` to `4.2`
instead of retaining the retail-ordered `6.0 -> 5.2 -> 4.2`. The focused
falsifier `PulseHitPreservesDirectThenExplosionDamageOrder` failed against that
collapsed model with one `SegmentDamaged` event where two were required.

`rebuild/OnslaughtRebuild.Core/Level100Destruction.cs` currently owns a bounded
aggregate approximation:

- `PulseDirectDamageBits = 0x3F4CCCCD` and
  `PulseExplosionDamageBits = 0x3F800000` remain separate;
- `ApplyPulseHit` sends those values in retail order to the same whole-body
  Target Tank or Target Drone selected by the direct mesh hit;
- this retains the two-call store shape for known full-damage examples, but it
  does not perform the released explosion-position backoff, neighbor scan,
  approximate-volume negotiation, or radial falloff; and
- `Simulation.UpdateProjectiles` routes `MechPulseBoltMedium` through that
  pulse-specific owner rather than the generic one-damage round path.

The tests that pin an unconditional first/terminal pair are approximation
tests, not retail parity proof. The contact catalog carries the original
global BBOX origin/radius, class scale and render-radius bits into each target
definition. The remaining runtime correction needs a distinct synchronous explosion at
`round.position - normalize(velocity)*0.1`, primary-volume admission, and
per-candidate falloff after the direct `0.8` call. Target Tank is proven
nonsegmented on this path. Warehouse keeps the aggregate fallback until the
separately admitted per-part bounds report above is implemented and checked;
that fallback must not be generalized to whole-body actors.

The September 8 Large correction separately reads the `Mech Pulse Bolt Large`
record `[0xacda,0xad9b)` from the same pinned physics input (193 bytes, SHA-256
`834147fb4e48235c950ae189c0bd2002567c267705d65e81e5496ee6d91c71e6`).
Its speed/life/contact radius/direct damage are `20 / 7 / 0.20 / 8`.
Simulation projects those values through its existing millimeter motion and
swept contact owner. It applies one direct `8.0f` store, without the Medium
second stage or an unconditional Large `4.0f` addition. Production contact
checks distinguish 70 mm and 200 mm terrain clearance and observe target life
`6 -> -2` with one direct damage stage. The separate Large explosion has radius
1 and maximum damage 4; its spatial application, sound/effects, float motion
and strict expiry remain open.

The `Charged 2` weapon record `[0x135b3,0x1368a)` (215 bytes, SHA-256
`6c603aa0e6654cdf6b8ed78dd377ef351a0378a3d10941138ae36860acad5234`)
sets inaccuracy field 1 at `0x135df` to positive zero. The apply body at
`0x00435cd0` places it in mode `+0x34`. The burst body still calls the shared
random stream at `0x00506e0a` and `0x00506e3e` before multiplying by this field;
there is no zero-value bypass. Its complete `[0x005069f0,0x005078ac)` body
SHA-256 is `124b166f80acecc01ae2bf18b876c7c1202015aea1ba2b8303414fde973f8e5d`.
Simulation now passes zero through the existing two-draw scatter owner. A
charged-launch regression rejected the former Medium scatter and checks both
the resulting direction and stream state. This does not establish every
constructor/effect draw or the full game's random-stream phase.

## Remaining evidence boundary

Still unresolved are the source names of instance fields `this+0xE8`, `+0xEC`,
`+0x11C`, and `+0x124`; which exact gate rejected the contrasting runtime
invocation; the natural Level 100 explosion candidate order, live positions,
and per-shot falloff bits; Warehouse cache/controller execution and selected
segmented contacts; targets rejected by the explicit flag/smart/allegiance gates; expanding
`R > 3` timing; behavior outside the captured runtime window; and general
reconstruction parity. The retained traces prove bounded internal
source/shield/part carriers at both slot-40 call sites; they do not close the
entry/return/write envelope or bind a particular Level 100 receiver. The pinned
Stuart source is architectural/name evidence, not proof that its full body is
byte-equivalent to the retail PC implementation.

The 2026-08-28 static closure reports are:

- `local-lab/continuous-20260827/lane-pc-level100-explosion-candidate-radii.md`
  (18,899 bytes, SHA-256
  `a83a7a7b37d4fa0b198de3d89e8962bf646e66e94765cbcea9ac45698d4bb9bd`);
- `local-lab/continuous-20260827/lane-pc-small-explosion-mapwho-filters.md`
  (23,831 bytes, SHA-256
  `f9e6ca60e584b340e539232ee3cad3df731ee78ce5d22f27d1043ea1daa38691`);
  and
- `local-lab/continuous-20260827/lane-pc-pulse-explosion-terminal-order.md`
  (28,970 bytes, SHA-256
  `a37a671defea44715eee67ebff95abb5297bbce8114242ef5e75bfe41e461022`).

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
