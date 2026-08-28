# `CRound::Hit`, configured explosion creation, and `CExplosion::Hit`

Status: active, bounded semantic contract
Last updated: 2026-08-28
Evidence: MEASURED — pristine retail bytes, strict RTTI/vtables, exact data
records, dated static exports, replicated runtime carriers, and independent
PC-demo normalized bodies; SOURCE — pinned `CThing`/init layouts and virtual
order; UNKNOWN — the narrowed gates listed below.
Verdict: direct-round damage byte-provably precedes the synchronous small-
explosion neighbor scan, but the explosion is spatial rather than bound to the
original receiver. Its configured damage is a radial maximum, not an
unconditional second call. The PC MapWho traversal/filter chain, four modeled
Level 100 target geometries, and the terminal Target Tank's continued
eligibility with part `-1` are now statically closed. Natural receiver order,
per-shot falloff bits, expanding-radius timing, and broader parity remain open.
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

### Exact modeled target radii and terminal Target Tank behavior

For normal live renders, retained Level 100 CMSH streams and pristine dispatch
close both geometries used by the four modeled destructibles. The primary
sphere controls collision admission; the distinct render radius is returned by
virtual `GetRadius` and is subtracted from owner-position distance for damage:

| Definition | Primary centre rule | Primary radius bits/value | Render radius bits/value |
|---|---|---:|---:|
| Target Tank | owner-relative Z `0xBEC4D062`, X/Y zero | `0x3F88ED6D` / 1.069745660 | `0x3FC487A7` / 1.535389781 |
| Target Truck | owner-relative Z `0xBEF307E4`, X/Y zero | `0x3FA644E3` / 1.298977256 | `0x3FE83ED3` / 1.814417243 |
| Target Drone | owner-relative Z `0xBCD78710`, X/Y zero | `0x3FC2684F` / 1.518808246 | `0x3FE9F831` / 1.827886701 |
| Warehouse | actor-basis-rotated full BBOX origin | `0x40F2BEF5` / 7.585810184 | `0x41088DDF` / 8.534636498 |

Ground Vehicle multiplies the loaded BBOX radius by exact `0.8f`; Plane and
Building retain the full BBOX radius. Falloff never substitutes that primary
radius: it uses target owner position and the rightmost render value. The
current quantized contact catalog does not carry these definition-level float
bits and cannot reconstruct them exactly from quantized parts.

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
tests, not retail parity proof. The smallest supported correction begins in
the existing retail-asset materializer: carry the exact global BBOX origin,
class-selected primary radius, and render-radius bits into each target
definition instead of deriving them from quantized parts. Runtime then owns a
distinct synchronous explosion at
`round.position - normalize(velocity)*0.1`, primary-volume admission, and
per-candidate falloff after the direct `0.8` call. Target Tank is proven
nonsegmented on this path. Warehouse keeps the independently observed aggregate
fallback until its controller/report behavior is closed; that fallback must
not be generalized to whole-body actors.

## Remaining evidence boundary

Still unresolved are the source names of instance fields `this+0xE8`, `+0xEC`,
`+0x11C`, and `+0x124`; which exact gate rejected the contrasting runtime
invocation; the natural Level 100 explosion candidate order, live positions,
and per-shot falloff bits; Warehouse and other controller-bearing segmented
parts; targets rejected by the explicit flag/smart/allegiance gates; expanding
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
