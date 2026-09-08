# World 110 serialized initial-object seed admission

Status: accepted authored-data and bounded Unit static admission; runtime construction remains open
Date: 2026-09-07
Verdict: Core admits all 40 exact World-110 RLWD initial-object rows as one
immutable ordered seed projection with closed type-specific tails. These are
serialized constructor inputs, not 40 actors, a registry, or a session. The
September 7 extension records ordered Unit/child initialization and prepares the
four landing-craft turret inputs from the measured attachment calculation. It
also retains both explicit-tree tables and constructs the base pine prefix
with owned spatial membership and readiness events under explicit FP/seed assumptions.
Evidence: MEASURED serialized data plus SOURCE-INFORMED field semantics — the
hash-pinned retail archive and RLWD reproduce every offset, record digest, raw
word, common field, and tail; pinned `InitThing` source names the version-50
field order and derived records. The Unit extension uses bounded pristine-byte
and retained-instruction comparisons. No runtime construction was observed.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
authored input `data/resources/110_res_PC.aya`, 1,294,300 bytes, SHA-256
`4e041c758b9d41ba18311b1fadeacb95fc31af51320861480b97033bc24e3c2b`;
RLWD 76,600 bytes, SHA-256
`fb56249deac8faf0033f4d4b67688ff72e12d922291c880d75b10599fc739837`.

## Exact serialized envelope

The version-50 preamble is words `(3, 41, 110)`, one name `Aquila Prototype`,
trailing words `(0, 0, 0, 0, 1)`, and the 13 independently hash-pinned compiled
scripts. The initial-object header starts at RLWD offset 15,709 and is
`(2, 0, 40)`. Its first record starts at 15,719; the rows occupy exactly 2,608
bytes through offset 18,327. The following six bytes are the tree-group header
`(uint16 0, int32 2)`, independently closing the table boundary.

| Thing type | Rows | Closed retained tail |
| ---: | ---: | --- |
| 8 | 10 | `string8 definition; int32 trailer`, exact trailer `-1` |
| 15 | 1 | `int32 planeMode; int32 playerNumber` |
| 18 | 19 | explicit waypoint tail with no fields |
| 19 | 1 | amount, three raw delay words, squad size, unit, distinct spawner spawn script |
| 27 | 3 | explicit script-carrier tail with no fields |
| 28 | 5 | amount, mode, definition, exact trailer `-1` |
| 36 | 1 | raw finite radius word |

Every common and tail float remains its raw IEEE-754 word. All float words are
finite, and the serialized `active` and `attachScriptsToUnits` dwords are
required to be exactly zero or one. Object identity is derived only from exact
serialized order as `wres:rlwd:NNNN`; record offsets must remain contiguous,
and every record length and SHA-256 is retained.

## Load-bearing rows

The type-15 row is ordinal 1, 59 bytes, SHA-256
`850de203b32b967064f3a9bacca24bebd783af68760a8b4c056ea242a2b47dfc`.
Its position words are `(0x43846000, 0x43816800, 0x80000000)`, so authored Z
remains negative zero. Its orientation is `(0xbf04fd8b, 0, 0)`, plane mode is
zero, and player number is one. The new projection converts this row losslessly
to the separately accepted player-start owner; it does not replace that owner.

The five type-28 rows are ordinals `(14, 16, 17, 18, 19)`. Their amounts are
`(5, 5, 3, 5, 4)`, their modes are all zero, and the amount sum is 22. They
remain five squad seeds. The amount is multiplicity input, not a proved set of
22 member poses, actor identities, or publication order.

The sole type-19 row is ordinal 5 and is serialized inactive. Its amount is
three; delay and squad-delay bits are both `0x40a00000`; initial delay is zero;
squad size is one; and the unit is `Muspell Fighter`. Its common
`spawnScript` is `MuspellFighter2`, while its type-specific
`spawnerSpawnScript` is empty. Those fields are distinct. Cold seed admission
does not create the three configured fighters.

The sole type-36 radius word is `0x42480000` (50.0). It is retained as a raw
word, not interpreted as a collision volume or converted coordinate.

## Materializer and Core boundary

[`materialize_retail_assets.py`](../../rebuild/tools/materialize_retail_assets.py)
now retains all seven tail cases during its one table walk. A supported retail
materialization writes deterministic compact JSON to the ignored local path
`rebuild/OnslaughtRebuild.Core/Assets/Level110/level110-initial-object-seeds.json`.
The schema is `onslaught.world110-initial-object-seeds.v1`; the exact 21,651
output bytes have SHA-256
`51e51f5e1d3f7bce52ce99297711b1f299494271af3129828959e726aed04e5a`.
The payload remains user-local retail-derived evidence and is neither tracked
nor distributed.

[`RetailWorldInitialObjectSeedAdmission`](../../rebuild/OnslaughtRebuild.Core/RetailWorldInitialObjectSeedAdmission.cs)
loads only that embedded local payload. It verifies the output hash before JSON
interpretation, rejects unknown, duplicate, missing, null, reordered, or
unsupported shapes, validates the exact envelope and census, snapshots every
row, and exposes read-only typed views over the same row instances. There is no
public arbitrary-world or caller-supplied-row admission.

The 16 definition-bearing RLWD seeds join exactly to the existing RLWD subset
of `RetailWorld110LevelActors.AuthoredDefinitions`. Its 33 shared-BSWD
definitions remain separately owned and are not fabricated as rows in this
RLWD projection. Existing player-start, height-clamp, script/HFLD admission,
direct mission execution, and World-100 canonical-hash outputs remain unchanged.

## Explicit-tree inputs and initialization order

The byte-checked [world loader](../binary-analysis/functions/World.cpp/CWorld__LoadWorld.md)
allocates ordinary objects before its explicit trees, but calls ordinary Init
after the tree loop. The recursive BSWD load completes before outer RLWD
allocation/Init. The 35 BSWD ordinary rows include the 33 current actor inputs
and two type-37 SafeSides; their career-existence gate is separate from trees.

| Table/group | Group header | Record interval | Records | Tree Init branch |
| --- | ---: | --- | ---: | --- |
| BSWD fernsnow | 2715 | `[2728,11764)` | 753 | skipped by name prefix |
| BSWD pinesnow | 11764 | `[11777,29549)` | 1481 | eligible, serialized order |
| RLWD fernsnow | 18333 | `[18346,27382)` | 753 | skipped because a base is present |
| RLWD pinesnow | 27382 | `[27395,45167)` | 1481 | skipped because a base is present |

The base payload is 54,669 bytes, SHA-256
`04c5a3838548a2c50819f46dc1f1746f7c20ec4aa34678bd23c8bcd2186010f4`.
Both full tree regions, BSWD `[2709,29549)` and RLWD `[18327,45167)`, are
identical 26,840-byte tables, SHA-256
`26d874c61ed827db550feb27e57e3c076440d58b432ad0788e2a379b08db82a9`.
Their fern record stream hashes to
`c6b83ebfacf563f04294decfd1d5879726895bbd33fb23f2164b01c391117372`;
their pine stream hashes to
`c4308e46dad3b687051eb9c6e4650f923133d713f92401f3db997a6fa28bae59`.
Each record is raw float X, raw float Y and integer variant, with no serialized
Z. Actual variants are 0–3. Table endpoints are not payload endpoints.

The existing `level110-initial-actors.json` includes both tables and four
exact mesh input records under `onslaught.world110-initial-actors.v4`:
157,121 bytes, SHA-256
`ab47754b2fc547ae88685477b5408907d7598c45f117a05ffa367ae19809e9c8`.
The materializer shares one ordered tree reader with Level100's render/shadow
projection and waypoint parser, and one global-BBOX reader with its pine renderer.
Core retains read-only groups, raw XY, variants, record digests and offsets.
`CallsTreeInit` marks the retail branch; the plain `Create()` stage leaves
1,481 unconstructed trees. `CreateWithBaseTrees(randomSeedAtFirstTree)` constructs
those pines once and reduces that count to zero. The repeated RLWD table never
creates another grove.

### Connected base-tree prefix and numerical limits

`RetailWorld110Tree` owns CThing state, exact retail XYZ, its mesh fields,
MapWho entry and persistent collision listener. `ThingBaseState` shares flags
and type composition with the existing Actor owner without giving trees Actor
lineage, old pose, movement or contact timestamps. Ordinary actor states remain
allocated but uninitialized during this tree prefix. World identities, collision
listeners and subsequent detached player/reader shells use one allocator; the
43 dense actor IDs remain a separate explicitly mapped domain, not retail thing
numbers. This does not reproduce complete retail allocation order.

The successful explicit-name path performs one shared RNG draw per tree,
rounds `(draw % 65536)/2048` through FISTP, and stores the result. Nearest rounding
can produce 32. It skips the second draw used for unspecified mesh variants.
Terrain samples the actual World110 HFLD and stores float Z, then clamps to water.
Its biased-float coordinate conversion agrees with `floor(XY*256)` for all
2,962 admitted pine coordinates under nearest float stores. The repeated ground
comparison can take a same-float Teleport; the concrete Tree movement callback
adds no RNG, event or matrix query.

MapWho insertion precedes collision initialization. Each tree gets cylinder
radius `0x3e4ccccd`, squared radius `0x3d23d70b`, half-height equal to half its
CMSH header radius, mask `0x20` and maximum collision kind 1. Its persistent
collision component queues event **ID 3000** at relative time −1, priority 0,
with null data/reuse, then scans actual current sector lists. Earlier trees fail
mask `0x20`; the scan is not supplied an empty candidate list. Renderability is
added afterward and world membership is inserted at the head. Final tree type
is `0x02800021`; flags are 2. Dispatching the owned event only sets readiness;
it performs no scan, reschedule or RNG draw. The implemented prefix therefore
consumes 1,481 draws and creates 1,481 events, resolved to those same tree objects.
Full collision response/geometry, falling, destruction and ordinary actor Init
are not provided by this prefix.

The four exact `m_pinesnow{0,1,2,3}.MSH.aya` inputs are 22,486 / 14,290 /
20,023 / 20,214 bytes; their complete existing source hashes remain in
`PINE_MESH_SHA256`. The CMSH header radius at inflated file `0x16c` is respectively
`4005575c`, `4007f5c1`, `400cea52`, `40054422`. It is distinct from the final
40-byte global BBOX's radius. The materializer retains all ten BBOX words,
including padding; spatial radius uses unrotated center/half-extents XY only.
All four select layer 4, so no initial pine enters the separate big-object list.

`RetailMapWho` owns five layers with cell widths 128/64/32/16/8 and grids
4/8/16/32/64. Radius selection stores float32(radius × float32(2.01)) before
comparison; equality selects the finer layer. Insertion is at the head;
same-sector updates preserve order and changed-sector updates reinsert at the
head without recalculating radius. Removal preserves the removed links, layer
and shared cursor. Initial scans visit descending layers, X-outer/Y-inner 3×3
neighbors, with child slots (0,0),(1,0),(0,1),(1,1) recursively visited before
parent entries only at the starting layer. Every list uses the shared cursor
and reads its successor after the callback. Nested queries or list mutations
therefore affect continuation; a captured array is not equivalent.

The later PostLoad call at `0x46d23a` reaches Sort `0x4926e0` after player Init.
`RetailMapWho.SortAfterLoad()` now implements that separate operation: layers
4 down to 1, X-outer/Y-inner, leaving layer 0 untouched. Each sector's original
tail is an excluded stop marker. Preceding entries with type bit `0x02000000`
move to the current tail, continuing through their captured old successor.
An all-tree `[A,B,C]` therefore becomes `[C,A,B]`; calling again rotates again.
The operation preserves entries, registration, counts and the shared query
cursor. It is not called during the incomplete tree-construction prefix.
Radius/line queries and movement collision effects remain open.

**Numerical admission:** the factory takes the incoming shared RNG state
explicitly and currently selects binary64 arithmetic, nearest float32 stores
and nearest-even FISTP. These are reconstruction assumptions, not a measured
retail load environment. The live load's control word and incoming seed remain
open. MapWho contains no local rounding-control instruction; at layer 4, 336
actual placements differ among floor/nearest/ceiling. The first pine maps to
(41,31) under nearest versus (41,30) under floor. The standalone index's
integer-rounding parameter tests that particular law; it is not a complete
alternative x87 environment. Capture the control word and seed at the first
Tree Init when desktop/runtime work is available.

The startup path now narrows those unknowns. `CGame::InitRestartLoop` calls
the seed setter with 123456 at `0x46c7eb`, then publishes the stream at
`Game+0x304` (`0x8a9d9c`) at `0x46c80d`. The setter writes both current state
`+0` and reset seed `+4`. This is **not** proof of 123456 at the first pine:
first entry subsequently loads resources and initializes resource consumers;
retries skip that one-off phase but still initialize restart textures. Both
routes pass loading-screen callbacks that can pump Windows messages. The
transitive resource/cache and message/device-reset leaves remain unclosed.
The 35 ordinary BSWD allocations do not call their class Init at this point;
the procedural-tree draws use a separate stack-local stream and World110's
procedural count is zero. Message-box portrait draws also use a separate stream.

CRT startup requests precision 53 through `0x560cb1`, passing
`(0x10000,0x30000)` to `0x56947e`; its mask preserves incoming rounding control.
The compiled executable then uses **Direct3D9**, despite the pinned source's
D3D8 names: `0x5290ba` passes SDK version 31 to imported `Direct3DCreate9`.
Device mode flags are `0x50/0x40/0x80/0x20`, with only optional `0x100` added
before CreateDevice at `0x52b2d6`; `FPU_PRESERVE` is absent. Microsoft's
[device-creation contract](https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dcreate)
specifies single precision and nearest rounding without that flag. That API
contract makes carrying the CRT's precision forward unjustified; it does not
measure this installation's Proton/device behavior. CreateDevice and Reset
(`0x52b28d`, resize `0x52b781`) remain external boundaries. The inspected
application load path does not reassert a standing control word. Temporary CRT
conversion/math and texture-parser changes restore their caller's state.

The decisive future witness is the first BSWD pine at `0x4f6080`, reached from
the explicit-tree call `0x50ced8` (return `0x50cedb`): capture the raw x87 control
word and current RNG state: first read the stream pointer stored at
`0x8a9d9c`, then the signed dword at that pointer. At entry ECX is the Tree and
`[ESP+4]` its initializer. Recheck the current stream immediately before the
draw at `0x4f61a2`; stream `+4` is only the original seed. No such runtime
capture was taken in this pass.

The random selector also does **not** establish final standing yaw. Init leaves
the matrix cache dirty. The first normal matrix query replaces the selector
using `((treeAddress >> 4) & 3)`, float π/2 and global `0x67a680`, then copies
one table entry. The prefix does not query or invent that matrix. Native address
phase, later render angle and transition/reset ownership remain unadmitted.

The following bounded bodies were read from the pristine specimen named above;
their exact hashes were measured directly. Retained exports under
`local-lab/ghidra-fullpass-2026-07-23/exports/` informed the same analysis.
No Ghidra database or retail process was opened.

| Half-open body | Bytes | SHA-256 |
| --- | ---: | --- |
| Tree Init `[0x4f6080,0x4f63b1)` | 817 | `01f4285f653b2bbedab55d89fe94ba654425aae198ba02f74eab0834ada0607f` |
| Tree collision Init `[0x4f6480,0x4f6534)` | 180 | `a4921ce0934191a263740e6d5c5eb7a6cc9786044b5c9f2550b373097ef8db7e` |
| MapWho Init `[0x4919b0,0x491c4b)` | 667 | `633606b81f640cd5c00a308dfa8f73ebf0d7b81cdd2b7dc90c3116b4505e9288` |
| Radius layer `[0x491c50,0x491ccf)` | 127 | `162737eb8441c675a372b5e8a8659b03e7dc5155a2f1699ad08d52c28bf621a9` |
| World-to-sector `[0x492670,0x4926dd)` | 109 | `dbda2072298393de6f225842734bc10876e06f635994f1db94e6cb82c98b6ea8` |
| PostLoad sort `[0x4926e0,0x49285f)` | 383 | `c8ced3c72ed01dc9539205197a096397950ea4cb3f58f757698c01b61fd63c37` |
| Entry Init `[0x492ba0,0x492c58)` | 184 | `1f4a1f596520e4f7d5e42e5bac52cb848cde7c91a42e5a5bbf8450a5779ce7ec` |
| Persistent Init `[0x4269b0,0x4269f6)` | 70 | `bd4cf3f803c5d5a661b2d81ef96d1c2753a6ba4be722a4d1c6673ea96dedddd4` |
| Readiness handler `[0x426a20,0x426a38)` | 24 | `0cf29c9c31fba213a38f5dfb2e4dbb21d7526f4d19fdbbcd5a64dca9ab82ea9b` |
| Normal dirty matrix prefix `[0x4f6560,0x4f660c)` | 172 | `58de33539f7bf79083e77324ef79faf75bcb2310b4f60dd27e1fd63ac5501fa5` |
| Restart seed/publication `[0x46c7e4,0x46c813)` | 47 | `f5ce72eafe33d332c4dde6ec0d9ca9489e4e61455ea507320ea9cc7ac0e7de58` |
| Seed setter `[0x4de8c0,0x4de8ce)` | 14 | `7a4a171d93d770e2cafccfdbab191902d861d6ec69da0155ef41d121b426448d` |
| Startup precision request `[0x560cb1,0x560cc3)` | 18 | `38dcf78aa3dab9d5e661a8e7fbaabcbab0399decb645b9d088bed196a65eef42` |
| Device environment `[0x52af00,0x52b754)` | 2,132 | `bf98f3c6884486a9f4d40fed2a60d1b21641ea622fa85eb2aaeddc99a1a60379` |

Pinned GPL source `thing.cpp:27-89`, `InitThing.cpp:68-86`,
`InitThing.h:76-109,360-369`, and `engine.h:22` supply the base lifecycle,
initializer defaults and big-list threshold; Tree and MapWho sources are absent.

The former test-only World110 `Simulation` route ran Level100's Setup against
relabeled Level100 definitions. It now fails explicitly before initialization.
Direct World110 mission-program tests remain supported; schema-43 hash checks
use explicit synthetic envelopes. They do not establish a second-world session.

## Falsifier and hard ceiling

A controlled production mutation swapped the decoded type-28 amount and mode.
The exact squad fact failed with expected amounts `(5, 5, 3, 5, 4)` and actual
`(0, 0, 0, 0, 0)`. Byte-for-byte restoration returned the same fact and the
adjacent 66-test World-110/start/height/session/hash gate to green.
The ignored machine-local receipt is
`local-lab/rebuild-world110-all40-initial-object-seed-mutation-kill-20260830/RECEIPT.md`,
SHA-256
`fe300ff9fdfc13522922bdd81e860ecece1e54b521f719aeafec535d1b82e382`.

The serialized admission above does not establish coordinate conversion, physics or runtime
class enrichment, mesh/life/contact state, squad-member formation or poses,
spawner initialization, path construction, script startup, `CStart::Init`, a
Battle Engine or player, actor IDs, registry/world-list publication, nested
construction failure policy, state hashing, `Simulation`, `InteractiveSession`,
Godot ownership, or campaign 100-to-110 play. P7 remains open.

## Ordered Unit initialization: bounded static admission

The September 7 read-only check used
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, 2,506,752 bytes,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
PE section mapping was checked before comparing retained instruction bytes.
The ranges below are **half-open**; the function-name table's end column is
inclusive. Every selected retained instruction, including the complete final
`RET`, matched the specimen. These are static contracts, not observed runtime
values, completed constructors or a new campaign promotion.

| Owner and export wave | Pristine range | Bytes | Raw SHA-256 |
| --- | --- | ---: | --- |
| Unit constructor, W007 | `[0x004f7e90,0x004f8133)` | 675 | `2cab5cde89e806bd13d6a24f625f47bf2a532aa2ea367ef0ae5d4253d12a80f6` |
| Weapon constructor, W008 | `[0x00505e00,0x00505f61)` | 353 | `13bb0ee57dc0d0c3fa34baa3b2f8dd18af2c041fbda58673a697dea0c44ad048` |
| Weapon's shared Init slot, W003 | `[0x0044a830,0x0044a848)` | 24 | `f6ee4512a39314c5f69effe255c5a64d8d957845a0b3afe94b11afbd4d1b08a7` |
| Attached-spawner constructor, W007 | `[0x004e37f0,0x004e39e6)` | 502 | `f1571f003e3cce18a002afcc109d48864fc6371d4d4d4c97668907392aa4930b` |
| Unit-profile defaults, W002 | `[0x0042efd0,0x0042f219)` | 585 | `88bf8da7dd8127b968e62e7400a299a13ae8d1fa4041cb7311dea8d95e9e21e7` |
| BasedOn profile copy, W002 | `[0x00433390,0x00433cd4)` | 2,372 | `f41c3a1dd0d000032b4868bbdda3a3d5811ba94be54fa4c23250ce3669193cb5` |

Exports are under `local-lab/ghidra-fullpass-2026-07-23/exports/`, in the named
wave's `decompile/` and `instructions.tsv`. The Unit Init owner carries that
body and fire-control evidence. The pinned GPL source remains
`5352a81cdb838b145a57f7febc5d9fc4b0129ebb`; it contains `InitThing.h`,
`InitThing.cpp` and `actor.cpp`, but no `Unit.cpp` or `Unit.h`. Source describes
common initializer fields; it does not supply the missing Unit implementation.
The independently owned base contract is
[`Actor.cpp.md`](../binary-analysis/functions/Actor.cpp.md).

### Profile and object state are distinct

[Unit Init](../binary-analysis/functions/Unit.cpp/CUnit__Init.md) owns the
initializer/profile field mapping. The materialized actor projection supplies
selected authored fields, not the resolved retail profile and its child lists.

The exact physics input remains `data/default physics.dat`, 175,603 bytes,
SHA-256 `e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14`.
Its Unit value IDs 7, 18 and 27 feed the three ordered lists; repeated fields
must survive decoding. ID 3 writes profile `+0xc0`; ID 47 writes `+0xbc`.
The 43 direct World110 actors include Unit rows with 17 weapon uses, nine
attached-spawner uses and four component uses. These counts exclude squad
members, spawned output and recursively created components. All four component
uses name `Dropship Gun Turret`: three landing craft and one empty landing craft.

Profile application is ordered. In particular, `BasedOn` calls the shared
copy body above; it is not a dictionary merge. Non-null source strings replace
their destination, selected scalars copy, and components append. The weapon
loop allocates/copies tuples without appending them to the destination. The
inherited-spawner loop has an additional invalid source-read path:

- The weapon traversal leaves `ESI == 0`, either directly at `0x00433bbb` or
  on normal loop exit at `0x00433bfe`. The spawner traversal loads its actual
  element into `EDI` at `0x00433c14`.
- For a non-null spawner element, after a normal allocator return at
  `0x00433c2b`, tuple words 0/1 are read through `ESI` at `0x00433c30/34`:
  addresses zero and four. Only word 2 uses the actual element, `[EDI+8]`
  at `0x00433c3a`. There is no allocation-result guard before these reads,
  and no destination append in this loop.

Independent review and direct pristine-byte readback confirmed those
instructions and predecessor register assignments. This establishes a static
null-read path under the normal calling convention, not a witnessed runtime
crash or proof that retail content reaches it. The World110 fighters' `Base
Air Unit` source has only behavior and explosion fields, so it contributes no
such list entries. General inherited-list behavior must preserve this boundary
rather than silently applying conventional inheritance. Reproducing the path
with a controlled profile in a disposable runtime copy remains a future check.

### Shared initializer contract

The complete call order and conditional fire-control draw now live in
[the Unit Init owner](../binary-analysis/functions/Unit.cpp/CUnit__Init.md).
That owner distinguishes the attached-spawner copy from standalone Init,
recursive child publication, Thing versus Unit list publication, and the
unconditional final event 4003. These laws are still required when connecting
World110's actual profile and mesh inputs to its spatial/event/RNG owners.

The Unit constructor explicitly initializes readers, lists and many scalar
fields, but it does not establish zero for every byte of the object. In
particular, fourth vector words copied through temporary storage into
`+0x158/+0x204` are not admitted as zero. These findings do not upgrade the
existing direct-actor projection to completed Unit instances. The connected
Component-input calculation below stops before child Init.

### First three Buildings and the following Features

The first three BSWD rows are Control Tower (active 1, life 100), Forseti
Pulse Tank Factory (active 0, life 150) and Forseti Repair Pad (active 1,
life 80), all allegiance 0. Their authored active flag is separate from the
career-existence gate. Row 3 is a cannon, and rows 4–9 are the six icebergs.
The [Feature Init owner](../binary-analysis/functions/CFeature.cpp/CFeature__Init.md)
now records the iceberg profiles, actual mesh/collision bounds and occupancy
contract. It does not claim those six can initialize before earlier eligible rows.

The normal Building wrapper is primary-table `0x5d8eb4` slot 9,
`CBuilding__VFunc_9_00417190`. It sets initializer collision kinds to 2 and
ORs mask `0x08000020`; `init+0x8c` receives `(profile+0x13c == 0)`. It creates
the destructible-segment controller at Building `+0x178` and its motion
controller at Thing `+0x70`, then calls shared Unit Init at `0x41727d`.
After Unit returns, a **core count** of zero destroys and clears those controllers.
The measured counts are 8, 5 and 2, so all three retain them.
The subsequent order is:

1. Look up `closed`, calling SetAnimMode(index,1,1) only when the result is not -1.
2. Set `+0x254=3`, `+0x25c=0`; look up `notshut`, again conditionally set
   animation, and set `+0x260` to whether that lookup succeeded.
3. Set `+0x264=3`, `+0x268=-100.0f`; call virtual `+0x48 → 0x4dfd10`.
4. Create AI through `0x417390` and store it at `+0x13c`. The exact profile
   name `Forseti Repair Pad` selects the repair-pad subtype; the other two
   use the shared Unit AI constructor. This stage is not an inline AI tick.
5. Look up `Idle`, then call SetAnimMode(index,1,1) **even when the index is -1**.
   Finally add occupancy through `0x50b010` before returning.

These profiles use Unit render selector 7. That arm defers render creation to
the class-specific hook in Thing Init; it does not supply an empty mesh.
Building's hook at `0x4176c0` formats profile `+0x2c/+0x30` using `%s.msh`
and creates type 4, CRTBuilding (`0x5de9c0`). It never reads meshNumber.
Field ID 9 supplies the primary name; the secondary default is the literal
`m-b-rubble`. These three profiles have no BasedOn entry. The fields containing
`FB Idle` and `FB Health Pad Idle` are sound names, not animation names.

The pinned World110 archive has external MESH records at inflated offsets
928476, 928809 and 929142 for health pad, tank factory and control tower.
Each MESH payload is 325 bytes (excluding its eight-byte header), with nested
PMSH/PMS2, a 300-byte name buffer, resource IDs 321/322/323, zero skip word and
trailing byte 1. Their payload SHA-256 values in that order are
`3cebda1b624516a6c347e9a14af6359a0ebb2addd1756c4f52d63895f30fb7b3`,
`eb1f150346e846cff132ef71a7aad94d69789522b414d7f8fba2ddd56b3fe320`,
and `0b06574f593d5426aa92920b766ccd5979a73a462e0467c12c4732729953e7d0`.
The exact resolved loose inputs were read under Steam's installed
`data/resources/meshes/`:

| Primary mesh | Bytes | Parts | SHA-256 |
| --- | ---: | ---: | --- |
| `m_fb_control_tower.msh.aya` | 100,554 | 39 | `86af67e09dc2fd21c7023acd53ebcb4171f3bf396f836da85ecfdda516588d91` |
| `m_fb_tank_factory.msh.aya` | 85,819 | 29 | `a507afda7b5c6b6b8bed275d442a53b28043bb9d5b65f9ea5bd6f5ff754bf6de` |
| `m_fb_health_pad.msh.aya` | 29,608 | 20 | `4ec6cb1d589c866acfa292232ca4f850967faea899c2f082329bff78e647ab44` |

All three CMSH headers contain zero animation entries. CRTBuilding's animation
getter selects its primary mesh `+0x14`, not the separate rubble mesh `+0x54`.
For this resolved state, `closed`, `notshut` and `Idle` each return -1.
The two guarded calls are skipped and `+0x260` becomes zero. The final Idle
call still enters the animation wrapper: index/mode -1, frame 0, force-loop 1,
fallback increment 1.0f. The preceding collision, segment and AI paths below
create no animation owner, so this call allocates one and requests its own
3000 event at -1 on the admitted successful path.

#### Collision, movement and AI

The concrete Building/Unit type chain produces `0xc0100133`, then renderability
adds `0x00800000`. Its initial persistent collision mask is `0x08000020`;
every preceding pine (`0x02800021`) and Building (`0xc0900133`) intersects it.
The persistent filter at `0x426900` rejects those pairs before readiness or
narrowphase. The immediate scan still traverses the real spatial owners.
Desired/minimum/maximum kinds are 1/2/2, response 2, fixed-transform/delayed flags
are `0x0a9` after clearing readiness. Collision readiness uses the **relative**
`AddEventTimeFromNow(-1,3000,collision)` overload.

Under the declared nearest/53-bit arithmetic, Tower, factory and repair pad
occupy sectors `(17,15,3)`, `(9,8,2)`, `(14,15,3)`. Their prior candidate sets
contain 15 pines, 647 pines plus Tower, and 24 pines respectively. Authored Z is
clamped to ground words `0xc1199926`, `0xc1223a09`, `0xc116679a`; none then hits
the water clamp. The later virtual `0x4dfd10` invokes Actor/Thing ground seating
again and copies **position only** to old position. It leaves the old basis
alone. These are calculated input-specific values, not a captured game run.

Actor's multiplier is 1 for these Buildings. Each still takes one shared RNG
draw, stores remainder zero, and schedules MOVE 3000 at -1 with countdown 1.
Their Unit fire-control gate remains zero, so the unconditional helper call
adds no 4001 or draw. Inactive factory status does not imply shutdown. Its
attached Sabre spawner is an owned template, not a spawned Sabre, and creates
no immediate spatial entry, event or draw.

Shared AI `0x4fe710` stores a direct Unit owner and creates three null active
reader cells (`+0x0c/+0x24/+0x28`). Serialized target -1 is normalized to null;
spawned-by is null. State becomes 1 and AI requests 3000 at the current time.
Empty scripts suppress owner event 2003; profile `+0x19c=0` suppresses four
jitter draws. Thus the selected Tower Core path requests five events in order:
collision 3000, Actor 3000, Unit 4003, AI 3000, animation 3000. At fresh time
zero, AI's timestamp is zero and the other four store `0.0001f`. Immediate
bucket dispatch is **FIFO**, not a sort by those timestamps. No frame delivery
is implied by this census.

#### Destructible geometry and resource boundary

Controller Init `0x444660` walks source mesh children in serialized DFS order.
Eligible type-1 geometry with original `+0xa4=0` creates a segment. Names whose
first four bytes are exactly `core` or `CORE` create cores; otherwise positive
`+0xa0` selects the swap variant, exact `x1`/`X1` selects kind 3, and the remaining
eligible nodes create extras. Global segment publication precedes head insertion
into the parent child list. Core ordinals count construction order, not digits
in the name.

Tower has **29 segments: eight cores and 21 extras**; factory has 19 (five cores
and 14 extras); repair pad has 16 (two cores, two swaps and 12 extras). Repair
pad's two NMIC references alias existing segment owners, so its 18 non-null
part-array cells do not mean 18 allocations. Tower's array has 40 cells,
including the extra null sentinel after its 39 source parts; ten emitter parts
remain null. No segment Init creates a gameplay event, RNG draw or animation.

A segment's weight is the largest XYZ bounding-box half-extent. Non-root weights
accumulate with a float store after each addition; the root weight is excluded.
Scaling divides weight by total, multiplies by profile life, then by five for
cores other than ordinal 1; the first core receives zero. Intermediate arithmetic
stays wide until the final float store. Health summation follows the reversed
child-list order, storing float after each addition. Tower's total weight is
`0x425e25dc`; cached subtree health is `0x433a4938`. Tests carry the independently
calculated per-part scale words, graph order and shared-owner assertions.

CRTMesh Init on an existing named mesh prepares pose-cache allocations and ten
`_Fenrir Flame Effect` descriptor slots. CEMT's ten record IDs are all zero and
reference parts `7,26,27,28,29,34,35,36,37,38`. Lookup may find a particle
catalog entry or null; it starts no emission. The three pose arrays are
**unwritten**, while the fourth 39-word array contains -1. The header has
integer -9999 and float word `0xc7c34f80` sentinels. Building's concrete render
interface takes the imposter-cache branch; a successful result allocates an
unwritten byte. CRTBuilding resolves the separate rubble mesh and overwrites
render `+4` with 1.0f. Console registration and these admitted cache/allocation
paths request no gameplay event or shared draw. A mesh cache miss's resource
load is outside this closure; preloaded metadata alone does not prove a live
cache hit. Core retains the actual geometry/emitter inputs but does not yet
allocate or execute those renderer/resource caches.

#### Fresh world state and implemented Tower

World construction (`0x50a9c0`) and shutdown (`0x50ada0`) clear two 26-dword
counter arrays at `world+0x130/+0x198`. A plain LoadWorld call does not. The
Tower increments side 0 selector 7; zero is justified only by the fresh
lifecycle boundary, not assumed at arbitrary BSWD entry. World constructor
also initializes its lists. The primary effect link is a distinct owned node,
inserted into the process-global effect list with null payload; it emits nothing.

The outer load initializes three occupancy bitplanes before BSWD recursion.
Each has 8,192 bytes of `0xff` and a stored radians threshold for 35, 45 or 60
degrees. Activation is zero. The first Tower's `0x50b010 → 0x4bc480` only
prepends it to the occupancy candidate list, then exits before any geometry,
terrain, bit change or shadow test. Activation and rasterization belong to the
later non-base load tail. Candidate-list emptiness follows fresh startup or
proper prior disposal, not the allocation helper alone.

The definition-usage catalog is also empty on the admitted cleared **resource**
route. RunLevel loads resources first; `0x4d7379` records the resource level at
`0x6317cc`, and `0x46ce24` sets the current game level before LoadWorldFile.
`0x472650` compares them, causing definition Add's branch at `0x50da05` to
return without catalog insertion. `0x50dc20` uses exact-name lookup and only
marks an existing entry. `Control Tower` therefore misses; it must not create
a used-name entry. An alternate non-resource route requires the entire ordered
parse/recursive definition catalog, not a synthetic singleton.

`RetailWorld110InitialConstruction.CreateWithControlTower(seed)` now constructs
the first Tower's bounded Core state after the actual 1,481 pines. It uses the
existing registry Actor owner with exact float current/old poses and movement
scheduling state, the live spatial index, shared RNG and event pool, actual
segment/AI reader owners, and distinct named, all-Thing, Unit, faction, effect
and occupancy memberships. The factory explicitly selects the fresh successful
resource route and preloaded materialized geometry. Renderer/cache allocation,
remaining Building/Feature initialization, damage, frame delivery, world reset
and playable session construction remain open. Legacy registry mutation,
restore and canonical hashing reject this incomplete state before silently
losing the added owners or float words. No retail runtime or full parity claim
follows from the focused Core tests.

The following bodies were independently read from the pristine executable:

| Half-open body | SHA-256 |
| --- | --- |
| Building Init `[0x417190,0x41738f)` | `65207cd6b266935d9e926acdbbcb642497c6af05b0fff94107c1acb9a89a4f0e` |
| Building AI factory `[0x417390,0x417477)` | `fb90d2ee6c9d523b076a24a232bb095077f9f979415ca6028a88a97292baa51f` |
| Building render hook `[0x4176c0,0x417861)` | `05910be7ad16f846d9b221f9c1d2bd63ea58427eeae9628e96e8810ee789cbc9` |
| CRTBuilding Init `[0x4db8f0,0x4db952)` | `df1435dbcc29251451d2918ee1a2e586718d31d47fd3a64f210b6de73cc0191a` |
| Animation-name lookup `[0x4aa630,0x4aa673)` | `43c4d775c8ec52976fcc9489baeea2e90773313c36f42f6ea873aa3133b0d149` |
| Thing animation wrapper `[0x4f44a0,0x4f4528)` | `ebebf118cf20136f6ef013d2e2592771c9a6f4b13174bd766acb9033388ddab1` |
| Animation SetAnim `[0x404860,0x4048ba)` | `e643d3cc227058c6ae6a12af074b84a832da215fa2454b763a42dd2deb8019d7` |
| Segment controller Init `[0x444660,0x44493c)` | `132b3b463a23a4472c75b311b1a0f4be4f7c12bf2c3d9071cb633e6a9faaa877` |
| Segment node traversal `[0x444c10,0x444ef8)` | `323510d8d9dd2d27a2df360948b09c92302dc2a3ebe09b30f0a1f50b4a86e29b` |
| Segment creation `[0x4449c0,0x444bcd)` | `f538fc0c2e48a0b7fc25af510334b178def1b758608dc072b36e957ad0bfeefa` |
| Segment scale `[0x442870,0x442884)` | `1a6ed815a122f0cf6945e94930bfda6cc696820b4f96d3c2c30cead0bce5f41e` |
| Core scale `[0x443590,0x4435bb)` | `566fe30c70e8b9db39d7ad1a541dd62f1f8255185f64d9d111a55d5cf6790464` |
| Subtree health `[0x442900,0x44295b)` | `d04a75d129e94c85f4f9017fd0b37e9d1d32eec7f755bb1e7c9f6ea6d632a96e` |
| Shared AI `[0x4fe710,0x4fea24)` | `2eadfbd3a63747b453291d5b7584cb973c6b5bc239e755cfa329ccf3b16dfd1d` |
| CRTMesh Init `[0x4dc370,0x4dc94e)` | `2bbe733893b0700b92657f7ff7573febd365e1699a45b0de2489933bd3fff99e` |
| Ground-seat wrapper `[0x4dfd10,0x4dfd3f)` | `8a224c880eeda14c2d1cc976c56bef647c920003f2aa1e3f656005c8ca4647aa` |
| Occupancy insertion/gate `[0x4bc480,0x4bc506)` | `f5b0cd6f44378e7f8be4fccef80cb6f94166e41a32270cca717f4bb98e90fc0e` |
| Grid Init `[0x4bc260,0x4bc2ce)` | `abb98c31ee861738a1eefc084949f42870f91b65dca3d911758a5e65bd5d3a6f` |
| World construction `[0x50a9c0,0x50ab5f)` | `2d698e3eb59a2375e2ec376d90777361d06cafa7083d49cbe0d5dbd693192d84` |
| World shutdown `[0x50ada0,0x50af6d)` | `e1789c52f92f7a0a5a02e82150269a8363aeee822fc7c4e850f1d24d680d8281` |
| Catalog MarkUsed `[0x50dc20,0x50dca1)` | `30d10d0e220e0d4c288ff9ea6c6f2d7d15040f261a87b996b9b964fd54a644ac` |
| Resource-level equality `[0x472650,0x472662)` | `f6f7faa01acf005fbc37835f9e581515749f9e0d029cd0f33cb414e902cbb6a5` |

### Four landing-craft turret children

The same pristine specimen and byte-comparison method close the normal-allocation
Component route for the four `Dropship Gun Turret` uses above. W002 retained
instructions match all 95 Init and 35 parent-binding rows, including their final returns:

| Body | Half-open range | Bytes | Raw SHA-256 |
| --- | --- | ---: | --- |
| Component Init | `[0x00427b80,0x00427cc4)` | 324 | `2ae05f1f3aee48c9fc31e136413d8e82812a261bfd55e5b3e76c7f9a0ed3735d` |
| Parent binding | `[0x00428b50,0x00428bb9)` | 105 | `cd0c7c91ac94288b40878afa39dd8cadfec8b5ef9fc7e58ed35f7b7fc20c2aa3` |

The exact physics file identified above supplies component record type 7, mesh
`hiveturret.msh`, life 6, range 260 and one `Hive Machine Gun`/`GunA` tuple with
raw flags `0x00024400`. There is no `BasedOn`, child or attached-spawner tuple.
Defaults plus this record leave profile `+0x12c/+0x198/+0x19c/+0xbc/+0x18/+0x1c`
zero: normal Component allocation, no ground-clipping predicate, no AI jitter
branch, no Unit barrel-inspection/fire-control gate, and no Dust/Vent enumeration.
Field ID 22 writes `+0x114`, not the factory selector `+0x12c`.

The selected local mesh is `data/resources/meshes/m_hiveturret.msh.aya`, 3,710 bytes,
SHA-256 `101fec6c868347b039164121f1b0b146e410b02d79f984d20f67acd1d1ce2219`;
its 9,928 inflated bytes hash to `b12e8d0c36f9ba1ca674c4e2f0b3a4fd243b889c98a178c890db005c0916a753`.
It has zero animation entries, radius word `0x3f132175`, parts `hiveturret` and
`Emit01`, and a `GunA` emitter. The parent mesh `m_m_dropship.msh.aya` is 53,538
bytes, SHA-256 `f586cc84f577e441eba425d5c95dbca3e057d063229bf5c2999227157704424b`;
its 201,676 inflated bytes hash to `22a97848a2476ee3abf2136c2855aacfc29dca5157018d489efc4737332d7cfc`.
Its `Component` emitter references part 31, `Emit08`, under `mainbody`.

1. Parent Unit allocates and binds its owned reader to the new child **before**
   child Init. It requests attachment tag 20/index 1 and creates a fresh initializer:
   profile, transformed position, allegiance 1, active 1, empty script/name/spawn
   script, and null target/spawned-by. Because the parent initializer uses Euler
   mode, `0x004f8c99..0x004f8cc9` converts the attachment matrix to three Euler
   words before child Init; the matrix itself is not the initialized child basis.
   Active/attach-script words and spawn script are copied from the parent input.
   This does not supply an AI parent reader.
2. Component Init clears its independent parent reader `+0x26c`, tag `+0x270`
   and scalars `+0x250/+0x254`; creates its motion controller at `+0x70`, bound
   to the child with both cached angles -999; then writes initializer collision
   minimum/maximum `+0x7c/+0x80 = 2` and mask `+0x70 = 0x40100020` before Unit Init.
3. The shared Unit/base transaction above initializes the mesh and gun, publishes
   the child and queues its events before returning. Component then selects
   `Normal` when child `+0x214 == 0`, otherwise `Activated`, and records the
   corresponding `+0x264` state. Both lookups return -1 for this exact mesh.
   The animation wrapper still allocates an owner and queues its event 3000 at
   -1; SetAnim(-1, 1, 1) leaves frame 0, mode/index -1 and fallback increment 1.
4. The default AI factory calls shared constructor `0x004fe710`: null target
   and spawned-by readers select state 1 and queue AI event 3000 at current time.
   Profile `+0x19c == 0` eliminates its four-draw jitter branch; unwritten jitter
   fields are not initialized zeroes. After the constructor, the factory clears
   AI `+0x14`. The guide is then created with child owner and its four-word pose;
   Component sets `+0x278 = 99999` and clears `+0xf4/+0x268/+0x260/+0x274/+0x2bc`.
5. Only after child Init returns does `0x00428b50` bind child `+0x26c` to the
   parent and store attachment index 1. `RET 8` proves two explicit arguments.
   It queries the attachment again, stores relative yaw, propagates parent flag
   `0x100000` when set, and neither teleports nor directly schedules an event.
   Parent Unit then appends its already-bound child reader to its owned list.

The child Unit's event 4003 precedes the animation request, which precedes the
AI request; parent binding follows them. Delivery uses the existing
[event-manager contract](../binary-analysis/functions/CEventManager.cpp.md).
The four initial attachment calculations now have a connected implementation in
`RetailWorld110InitialConstruction.ComponentInitInputs`. The existing actor asset
materializes the shared local mesh pose once and its four ordered owner uses.
Core retains actual float positions, computes the attachment with measured store
order, then converts to child Euler inputs. The
[Unit transform owner](../binary-analysis/functions/Unit.cpp/CUnit__UpdateTransform.md)
records cache eligibility, the constant part chain, inverse-trig correction and
native arithmetic probe. This prepares incoming arguments; it creates no child
or event and does not complete Unit Init.

### Parent origin and initial collision boundary

All four origins are above both surfaces in retail's down-positive Z convention:

| RLWD row | Authored XYZ | Ground Z, approximately |
| --- | --- | ---: |
| 0008 | 215, 422, -20 | 1.160044 |
| 0012 | 205.125, 327.125, -25 | -10.599707 |
| 0013 | 237.5, 340, -30 | -10.458707 |
| 0020 | 170, 505, -25 | 1.160044 |

The admitted HFLD is SHA-256
`fd4d076a2926fbc473b7d364703bdbc0c8a0f7a638b0ab71b6f319374da033c2`;
water Z is `-8.84000015`. Existing Core terrain sampling independently checks
the four clamp decisions. This is origin clearance, not whole-volume clearance.

Fresh initializer collision fields retain delayed-start 1 and delay -1. Copy
does not replace those destination defaults. Dropship Init
`[0x00446d70,0x00447040)`, SHA-256
`3bace4c1afb0fdd62a7de7a35ae40c884e7f5610d96ad3b7d6ffc182374d984a`,
sets minimum/maximum levels 2 and ORs mask `0x0a400140`. The child separately
sets mask `0x40100020`. Both persistent components clear readiness before their
initial neighbor scan. The shared response consequently exits before narrowphase,
pose correction or owner Hit. No empty-neighbor assumption is needed for that
gate. Real peers still affect filters and detector event 2000 scheduling.

The child's actual outer BBOX radius is `0x3f07ff7f` (0.531242311), distinct from
render radius `0x3f132175`. Its XY enclosing extent selects MapWho level 4 and
no big-set append; the parent's extent selects level 2 and big-set publication.
Before its parent reader is bound, child speed lookup returns 142.0. The child
is inserted at the MapWho sector head before collision Init; world-list head
publication follows the scan, with Unit/faction publication later. Those ordered
publications, real peers and scheduled readiness/detector events still require
implementation. Full collision responses are needed once readiness is restored.

These bounded conditions close the initial pose dependency. They do not establish
the complete world's event/RNG state or replace the remaining child motion,
animation, AI, guide and reader lifecycle.

## First landing craft: actual prior collision peers

A further bounded static review covers the first parent, RLWD0008, and its
child, before event delivery. The superset of prior ordinary BSWD objects is
35; career bits may omit their Init. Base pines initialize before those objects.
RLWD rows 0–7 then initialize LevelScript, Start/engine, Setup, two waypoints,
the inactive spawner, and two more waypoints. Later squad Init and the final
SpawnInitialThings pass have not run. Actual BSWD profiles contain no nested
Component or BasedOn entries; their three attached spawners and destructible
segment objects do not publish additional MapWho Things during Init.

| Prior peer | Parent mask `0x0a400140` | Child mask `0x40100020` |
| --- | --- | --- |
| Pines | rejected by `0x02000000` | rejected by `0x20` |
| Six iceberg features | rejected by `0x00400000` | rejected by `0x00100000` / `0x20` |
| Ordinary/simple buildings | rejected by `0x100` | rejected by `0x40000000` |
| BSWD cannons 3, 10, 11, 12 | mutual masks pass; outside searched sectors | rejected by `0x40000000` |
| Start-created walker | mutual masks pass; outside searched sectors | mutual masks pass; outside searched sectors |
| Scripts and waypoints | no persistent collision component | same |
| Start, SafeSides, standalone spawner | MapWho flag cleared | same |
| Parent lander | self excluded | rejected by `0x40000000` |

Relevant type setters are pine `0x004bfa90`, feature `0x00510110`, building
`0x00417660`, cannon `0x0050ea20` and engine `0x00405f00`. Unit's shared
setter `0x004fcdc0` adds `0x80000013`, plus conditional `0x00200000`.
Collision-mask writes are tree `0x004f650c`, feature `0x0044ca64/0x0044ca6c`,
building `0x004171c6/0x004171ce`, simple building `0x004dfa50/0x004dfa5f`,
cannon `0x0041b1c3`, and the fresh zero-mask initializer at `0x0048dd4c`.
The legacy Core registry's ammunition/engine-only type projection cannot
substitute for these full type words.

The actual mesh files below were read from Steam's installed
`data/resources/meshes/`; their framed outer BBOX records were decoded without
tag scanning. The XY extent uses `sqrt((abs(originX)+axisX)^2 +
(abs(originY)+axisY)^2)` at `0x00492ba0`; level selection is `0x00491c50`.

| Mesh | Source SHA-256 | XY extent, approximately |
| --- | --- | ---: |
| `m_ft_sam.msh.aya` | `9a82f27454863c19c05a8cdedcc99cc05300aed75b8e54467a980c94bf5ba4a2` | 1.727473 |
| `m_ft_blaster.msh.aya` | `9833cd459e00b1c2068f9db6be34ee0e6a3f2d0b01d780946a338d5682abb4cb` | 1.727118 |
| `m_ft_pulse.msh.aya` | `1cc399936cdd171c44297dcbc6ef2ff2e187319de707d0f4c564e338a9770b9c` | 1.727834 |
| `m_f_be1.msh.aya` | `d4c8fa752229af4111b31efa5ff5928c892736faa6a807915412767f3cd3c6b2` | 2.134792 |

These peers occupy level 4, whose cells are eight units wide. Cannon Y values
are 240–282; engine Y is 258.8125. The parent's level-2 descendant search spans
Y `[384,480)`; the child's level-4 neighbors span `[400,424)`. Coarser passes
inspect objects stored at their own levels and cannot reintroduce those level-4
peers. Under normal successful initialization, no eligible collision pair
therefore reaches either first scan. This derives an empty result from actual
nonempty membership; it does not justify an empty-world adapter. Other landers,
later events and ready-on collision remain outside this result.

CPlayer itself is allocated after World.Load returns, as pinned
`game.cpp:700–718` and retail call/store sites `0x0046cea9/0x0046cf2d` show.
PostLoadProcess later assigns the engine and runs Player Init. A separate
physical Player Thing must not be invented beside the Start-created engine.

## Initial scheduled listeners remain distinct

Unit 4003 targets the child Unit. Its
[handler](../binary-analysis/functions/Unit.cpp/CUnit__HandleEvent.md) reads the
delivery-time current cameras and consumes one shared random result after
both slots; constructor engine coordinates are not a replacement.

Animation 3000 targets the separate animation object, vtable `0x005d87c8`.
Wrapper `[0x00404750,0x00404784)` has SHA-256
`5a854456bc7fcb9390d6ce819e2369bfc8ab09dc1218370565630b72dca37ab9`;
Process `[0x00404790,0x0040485e)` has SHA-256
`3125c3d82888672476e77e548dc2eb35c5dd7d0ac5f8e5c0f8648f11fb2b5714`.
If mode remains `-1` at delivery, Process copies frame `+8` to previous frame
`+0xc`, without frame advance or RNG. The wrapper requeues 3000 at `-1.0f`,
priority zero, null data, reusing the incoming event. Earlier callbacks could
change the mode before delivery.

AI 3000 targets the separate AI object. Its `0x005d8d1c` vtable resolves slot
zero to `0x004ff330`, `+0x24` to `0x004fec60`, `+0xc` to `0x004fef40`,
`+0x10` to `0x004ff4f0`, and `+0x2c` to `0x004ff710`. The actual empty
attached-spawner list skips the all-squad spawning probe, but target selection
still scans the opponent list. A null constructor target does not prove an
idle first update. The existing Core UnitAI transactions own bounded laws;
they do not yet execute live peers, selected weapon/ballistic helpers or
reader lifetime effects. A world owner must execute those calls in order and
acquire RNG only after earlier effects. No live scheduler/UnitAI integration is
claimed by the new tree inputs or this static event closure.
