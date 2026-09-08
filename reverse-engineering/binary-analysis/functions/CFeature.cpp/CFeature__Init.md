# CFeature__Init

> Address: `0x0044ca30`

Status: active static construction contract
Last updated: 2026-09-07
Summary: Feature initialization, its Actor lineage, three distinct mesh radii,
collision/publication order and the actual World110 iceberg inputs. The six
icebergs now have bounded Core initialization after the preceding Buildings and
SAT Cannon; they are not an independent or playable load prefix.
Evidence: MEASURED — pristine body/vtable/RTTI reads, retained instruction
comparisons and four exact mesh reads; no Ghidra or game process was opened.
`CFeature.cpp` is absent from the pinned GPL source drop.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, 2,506,752 bytes,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: CFeature.cpp (absent from the pinned GPL source) | Binary: BEA.exe.original.backup

## Initialization order

The complete body is `[0x0044ca30,0x0044cbd9)`, 425 bytes, ending in `RET 4`:
ECX is the Feature, with one initializer argument. RTTI at COL `0x6184c0`
(CHD `0x6184b0`, base array `0x618488`) confirms the relevant chain
**CFeature → CActor → CComplexThing → CThing**. It is not a direct CThing tree.
On the normal allocation/resource-success route:

1. OR initializer collision mask `+0x70` with `0x20`; set minimum and maximum
   kinds `+0x7c/+0x80` to 2. Copy profile `init+0x3bc` to Feature `+0xe4`.
2. Build a resource descriptor from profile mesh name `+0` and the render
   interface `this+8`. Create render type 1 at `0x44caf7` and store it at
   `this+0x30`, then call its Init. The concrete product is CRTMesh, table
   `0x5deb1c`, Init `0x4dc370`; its nonempty-name path resolves the mesh through
   `0x4aa6e0`. A descriptor or mesh name alone is not completed render state.
3. Call [Actor Init](../Actor.cpp.md) at `0x44cb18`. This includes script binding,
   pose/clamp policy, MapWho/big-list publication, actual collision peers and
   Actor movement scheduling. The Feature multiplier is exactly 1, but Actor
   still consumes its shared RNG draw. Without declared shutdown, Actor requests
   event 3000 at −1 after collision initialization. The event manager must still
   admit each request; successful object/resource allocation does not prove that.
4. Set `+0xf0=0`, copy allegiance `init+0xa0 → +0xec` and
   `profile+0x18 → +0xe0`. Add occupancy membership through `0x50b010` at
   `0x44cb44`, with the conditional update law below.
5. Set `+0xe8 = (currentZ < water)` for finite operands; equality produces zero.
   If profile noise `+4` is non-null, call sound creation `0x4e1940`.
   Destroy the temporary descriptor and return.

The concrete Feature table `0x5e45e0` binds type setter `0x510110` to
`suppliedMask | 0x80500023`; successful base render publication adds `0x00800000`,
so the final initialized mask is `0x80d00023`. Ground predicate `0x44d1d0`
returns true unless Dying and `+0xe8==0`; underwater predicate `0x415a90`
returns the Dying bit. Initially non-Dying icebergs therefore take the shared
absolute ground/water clamps. Activate and Deactivate are no-ops here.

## Geometry and collision ownership

These three quantities are different; do not substitute an OBJ bound or one
radius for all of them:

- `GetRadius` (`0x401440`) calls CRTMesh `+0x18 → 0x4dcaf0` and returns the
  mesh-header radius.
- `GetBoundingRadius` (`0x4f3940`) reads global BBOX word 9 through CRTMesh
  `+0x10 → 0x4de060`. Common collision Init uses this for the default sphere.
- MapWho derives its radius from global BBOX XY center/half-extents, then applies
  its stored `2.01f` inflation and layer selection.

Feature's type takes the ordinary no-bit-8 arm of `CThing::GetCentrePos`
(`0x4f3ac0`): `(currentX, currentY, float(currentZ + bbox.centerZ))`.
BBOX center X/Y and orientation are deliberately ignored on this branch.
The collision component then subtracts current position and stores the offset.
Keep both rounding stages; raw `bbox.centerZ` is not a general substitute.
The fourth temporary vector word is not established as zero.

Feature uses common persistent collision initialization `0x4f39c0`.
`CCollisionSeekingThing::Init` (`0x426150`) creates/adopts the primary sphere
and, with maximum kind 2, creates a secondary mesh collision volume bound to
its renderer. Persistent Init (`0x4269b0`) requests readiness event 3000 when
the initializer specifies delayed start, then scans actual MapWho neighbors.
Pines and earlier Features fail the `0x20`
exclusion mask; ordinary peers require their actual types and collision owners.
[The existing collision owner](../collisionseekingthing.cpp.md) describes the
shared component. There is no complete Feature collision adapter in Core yet.

## Actual World110 iceberg inputs

The [World110 owner](../../../game-mechanics/world-110-initial-constructor-seeds.md)
places the six Features at BSWD ordinals 4–9, in variant order **1,2,3,4,2,4**.
The loader traverses objects 0–3 first, initializing those allowed by career
existence bits. Constructing these six in an otherwise tree-only world would
skip preceding eligible initialization, RNG, publications and callbacks.

The actual type-8 records in `data/default physics.dat` (175,603 bytes,
SHA-256 `e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14`)
contain only ID 2, `icebergN.msh`, and ID 4, float 1. The profile constructor
clears EBP at `0x431386`, then zeroes `+0x18/+0x10` with stores
`89 6b 18 89 6b 10`; ID 4 is
applied at `0x43bd1b` and sets `+0x10` to one. Thus
[the damage override](CFeature__DecayEngagementMetricAndMaybeTriggerVFunc200.md)
returns immediately. No authored life, noise or explosion overrides exist;
profile `+0x18` stays zero. These are Feature profiles, without Unit weapons,
AI, components or attached spawners. The current actor projection's generic
`initialHealth=0` is not this invincibility behavior.

The following exact files are under
`local-lab/safe-copy-bea-pristine/data/resources/meshes/`:

| File | Bytes | SHA-256 | Header / BBOX / spatial radius float words |
| --- | ---: | --- | --- |
| `m_iceberg1.msh.aya` | 21,780 | `fdbbd6d91748a7130b3a0137e417fb5e984266e046f6731c6b9beb4ac222c7c5` | `4126b4a5 / 4113ab60 / 410cb804` |
| `m_iceberg2.msh.aya` | 21,097 | `4824acec58949d555fed44caaaff238b29ee7ef44e1b4d23469bce50224b5d1e` | `41193657 / 4107bd9f / 41016852` |
| `m_iceberg3.msh.aya` | 19,080 | `6148c199d29e39e7bfa971eabdf8c837a787c6bcf004def3a3fd032f7a1f3530` | `4129de5a / 410773ff / 410dc227` |
| `m_iceberg4.msh.aya` | 20,304 | `3add5f0cb80a954e029016a1f9a9825888f3e88b0d049260216e3a1231408347` | `410763cf / 40e05d73 / 40cf05ef` |

The spatial words use the reconstruction's stated nearest/53-bit arithmetic.
They select layers 2/2/2/3, so variants 1–3 also enter the big-object list.
Each mesh has one rigid part with a nonzero local translation, 101 virtual
frame entries selecting one hierarchy pose, and no parent/REFR/CEMT. Preserve
its actual CPOS/CORI and geometry in the mesh collision volume. Iceberg3's
BBOX center X is approximately −1.0905; its Feature center calculation still
ignores that X offset.

## Occupancy and remaining boundary

The 14-byte wrapper `0x50b010` calls `0x4bc480`, which always inserts the
object at the head of membership `0x809588`. It only calls rasterization
`0x4bd5c0` and shadow-volume rebuilding `0x4bd9e0` when both readiness
`0x809598` and bitplane pointer `0x855290` are nonzero.

Fresh world setup `0x50d580` calls the three bitplane initializers `0x4bc260`,
which clear readiness. Final occupancy rebuild follows ordinary Init. A
fresh construction prefix can retain real membership with readiness false,
provided preceding constructors/callbacks are shown not to activate it.
This is not permission to omit the eventual occupancy/shadow effects.

`RetailWorld110Feature` now uses the shared `RetailWorld110Actor` owner in
`CreateThroughInitialIcebergs(seed)`, following all four preceding ordinary
objects and the real 1,481 pines. The v7 actor input admits the four profiles,
mesh bounds and full CPOS/CORI word arrays. All six actual terrain samples
are `0x3f947c52`, above authored zero, so the ground teleport does not run.
The common water clamp changes **current** Z to `0xc10d70a4`, while old Z
remains its authored signed zero:

| BSWD ordinal | Variant | Old Z | MapWho sector | Rejected prior peers |
| ---: | ---: | --- | --- | ---: |
| 4 | 1 | `80000000` | `(7,4,2)` | 94 pines |
| 5 | 2 | `80000000` | `(11,5,2)` | 0 |
| 6 | 3 | `00000000` | `(10,5,2)` | 1: Feature 5 |
| 7 | 4 | `00000000` | `(23,10,3)` | 2: Features 6 then 5 |
| 8 | 2 | `80000000` | `(3,9,2)` | 0 |
| 9 | 4 | `80000000` | `(9,22,3)` | 0 |

Every visited prior peer fails the Feature's own `0x20` mask before mutual
filtering or pair dispatch. Each Actor consumes one shared draw and requests
one 3000 event after its collision owner's relative readiness request.
All twelve requests remain undelivered. No Unit membership, weapon/effect,
AI, animation or sound owner is created. Occupancy is prepended but inactive.
Current and old XY/bases survive; direct Euler retains negative zero in
row0Y and row2X. These are input-specific static calculations, checked by
`RetailWorld110CannonFeatureConstructionTests`, under the stated nearest/53-bit
and fresh/preloaded-resource assumptions.

| Variant | Sphere radius² | Initial centre Z | Stored owner-relative Z |
| ---: | --- | --- | --- |
| 1 | `42aa5c86` | `c13a0cba` | `c0327058` |
| 2 | `428ff314` | `c1367be7` | `c0242d0c` |
| 3 | `428f5717` | `c13c35da` | `c03b14d8` |
| 4 | `4244a3ab` | `c1392ace` | `c02ee8a8` |

Stored offsets for variants 1/2/4 differ from raw BBOX centre Z because both
rounding stages matter. The common collision state retains flags `0xa9`, the
sphere and its mesh binding; actual renderer caches and secondary geometry
evaluation remain unfinished. CRTMesh's complete resource/pose/imposter effects
and later Feature movement/death remain open. `0x44cc10` first delegates movement
to Actor; Feature's Dying-only transition differs from the common shutdown
transition and is not supported by the current Actor snapshot invariant.
Static invincibility does not establish generic Feature lifecycle parity.

## Byte pins

All spans are half-open in the pristine executable named above. Retained
exports under `local-lab/ghidra-fullpass-2026-07-23/exports/` informed the analysis;
the body identities below were also read directly from that specimen.

| Span | SHA-256 |
| --- | --- |
| Init `[0x44ca30,0x44cbd9)` | `58b0f15b4b04b3c3e150c45c1b527f9a3b282e458302c886258727b2132749a4` |
| Ground predicate `[0x44d1d0,0x44d1e9)` | `5c99e678b7b4b3aab75037d28d993726f668020b575b9d318c75b5dc4d228ca6` |
| Underwater predicate `[0x415a90,0x415a9b)` | `415a278e9b770cd676001c5045ec23eae80eade0cafae62122635e8827602c85` |
| Common collision Init `[0x426150,0x4262d5)` | `43029935f903d983eb6dbefee073f84f651a89790f9f13307ad1e20c08cf5c3c` |
| Center calculation `[0x4f3ac0,0x4f3c4a)` | `e2c40c5f3d055e4fe205c461a79fe8147122666a5d4fc8c6b1c8bb30f6b4284b` |
| Occupancy add `[0x4bc480,0x4bc506)` | `f5b0cd6f44378e7f8be4fccef80cb6f94166e41a32270cca717f4bb98e90fc0e` |
| Occupancy initialization `[0x4bc260,0x4bc2ce)` | `abb98c31ee861738a1eefc084949f42870f91b65dca3d911758a5e65bd5d3a6f` |
