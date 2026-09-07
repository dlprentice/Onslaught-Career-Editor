# World 110 serialized initial-object seed admission

Status: accepted authored-data and bounded Unit static admission; runtime construction remains open
Date: 2026-09-07
Verdict: Core admits all 40 exact World-110 RLWD initial-object rows as one
immutable ordered seed projection with closed type-specific tails. These are
serialized constructor inputs, not 40 actors, a registry, or a session. The
September 7 extension records ordered Unit/child initialization and prepares the
four landing-craft turret inputs from the measured attachment calculation.
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
bounded session, and World-100 canonical-hash outputs remain unchanged.

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
| Unit Init, W007 | `[0x004f86d0,0x004f91f2)` | 2,850 | `dc3c02ae147e701c9840db77698dd0277501cab30f94f897179c06c762f7b7fd` |
| Unit fire-control refresh, W008 | `[0x004fb280,0x004fb3cd)` | 333 | `5b5e4bf168556d656135d5fb780e330347a7df11c1c953d2e969f4193ceb1f85` |
| Weapon constructor, W008 | `[0x00505e00,0x00505f61)` | 353 | `13bb0ee57dc0d0c3fa34baa3b2f8dd18af2c041fbda58673a697dea0c44ad048` |
| Weapon's shared Init slot, W003 | `[0x0044a830,0x0044a848)` | 24 | `f6ee4512a39314c5f69effe255c5a64d8d957845a0b3afe94b11afbd4d1b08a7` |
| Attached-spawner constructor, W007 | `[0x004e37f0,0x004e39e6)` | 502 | `f1571f003e3cce18a002afcc109d48864fc6371d4d4d4c97668907392aa4930b` |
| Unit-profile defaults, W002 | `[0x0042efd0,0x0042f219)` | 585 | `88bf8da7dd8127b968e62e7400a299a13ae8d1fa4041cb7311dea8d95e9e21e7` |
| BasedOn profile copy, W002 | `[0x00433390,0x00433cd4)` | 2,372 | `f41c3a1dd0d000032b4868bbdda3a3d5811ba94be54fa4c23250ce3669193cb5` |

Exports are under `local-lab/ghidra-fullpass-2026-07-23/exports/`, in the named
wave's `decompile/` and `instructions.tsv`. The full Unit Init and fire-control
bodies account for 914 matching instruction rows. The pinned GPL source remains
`5352a81cdb838b145a57f7febc5d9fc4b0129ebb`; it contains `InitThing.h`,
`InitThing.cpp` and `actor.cpp`, but no `Unit.cpp` or `Unit.h`. Source describes
common initializer fields; it does not supply the missing Unit implementation.
The independently owned base contract is
[`Actor.cpp.md`](../binary-analysis/functions/Actor.cpp.md).

### Profile and object state are distinct

Unit Init begins by copying initializer `+0x3b4` (`mSpawnedBy`) into its
collision initializer `+0x6c`, copying initializer `+0x3bc` into Unit `+0x164`
(profile), and clearing Unit `+0x224` (the later fire-control gate). It does
not build a profile from the actor's display name or its numeric class ID.

| Profile field | Input consumed by Unit Init |
| --- | --- |
| `+0x2c`, `+0xe0` | Mesh name and internal behavior selector; selector 7 skips this body's mesh creation, relying on the calling class's render state. |
| `+0x3c` | Ordered weapon tuples: definition index, raw creation flags, mapped gun tag. |
| `+0x4c` | Ordered attached-spawner tuples: definition index, raw creation flags, mapped spawner tag. |
| `+0x5c` | Ordered component tuples: component-definition index and attachment index. |
| `+0xc0` | Raw life word copied to Unit `+0xf8` before Actor Init. |
| `+0xbc` | Turret-turn scalar; strictly greater than zero enables weapon-part inspection. |
| `+0x18`, `+0x1c` | Non-null gates for enumerating `Dust` and `Vent` attachment positions and allocating effect links. |

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

### Actual call and publication order

1. With a profile and selector other than 7, create render type 1 and initialize
   it from the profile mesh name. Then walk weapon uses in list order.
   `CreateWeaponByIndex` (`0x0050f6d0`) creates a plain `CWeapon`, whose table
   `0x005dfc94` slot `+0x0c` points to the 24-byte shared initializer above.
   That initializer copies owner Unit, literal 1, and gun tag into weapon
   `+0x08/+0x0c/+0x10`; Unit also writes tag `+0xac`. The weapon constructor
   selects mode zero through the real weapon/mode definition lists. When mesh
   and positive turret-turn scalar permit, inspect the selected `GunA` through
   `GunI` part chain: turret markers set weapon `+0x94`; barrel markers set
   weapon `+0x98`, Unit `+0x224`, barrel pointer `+0x220`, and reference angle
   `+0xf4`. Append each created weapon to Unit `+0x17c` only after these steps.
2. Walk attached spawners. The factory at `0x0050f970` allocates a `0x3f8`
   object using the attached-spawner constructor above. At Unit call
   `0x004f8a74`, embedded initializer `object+0x10` invokes Copy
   (`0x0048dbe0`), **not** standalone `CSpawnerThing::Init`. Override the
   copied initializer's target `+0xa4`, orientation type `+0x60` and roll
   `+0x4c` to zero; set active `+0x3ac` to one; clear script and name; retain
   copied spawn script. Set owner `object+0x3d4` and tag `+0x3e8`, then append
   to Unit `+0x18c`. This creates no immediate output unit. The constructor
   also resolves the spawn definition and can force its shared definition
   field `+0x10` to one when `IsSpawnTypeAllowed` rejects the selected class.
3. Copy profile life, then call Actor Init at `0x004f8b38`. Base initialization
   can publish, bind scripts, construct collision state and change pose
   before returning. Its movement scheduling consumes the shared RNG before
   the remaining Unit work. Script binding queues `INIT_SCRIPT` 2001; it does
   not execute the script's Init/Ready body inline. If initializer orientation
   type is Euler, Unit
   then copies its three authored angles into both `+0x114..+0x11c` and
   `+0x120..+0x128`; do not substitute these for the base's final pose.
4. Walk component uses. Create the actual component class through
   `0x0050fa40`, allocate a distinct reader and bind it to that child, obtain
   attachment position/orientation through owner virtual `+0x160`, then build
   a fresh component initializer with the selected profile, allegiance,
   active/attach words and spawn script. Call child virtual Init at
   `0x004f8d6c` before linking child back to its parent through `0x00428b50`
   and appending the reader to Unit `+0x19c`. This is recursive initialization,
   not an extra authored World110 row or a mere child-ID assignment.
5. With a profile, allocate the primary effect link and enumerate nonzero
   `Dust`/`Vent` attachment positions under their profile gates. Then insert
   this Unit at the head of global list `0x008550d0` (`0x004f8fad`), and only
   afterward copy allegiance to Unit `+0x138`. This Unit-specific publication
   is separate from the earlier base Thing publication.
6. Scan mesh parts. An exact lowercase `turret` match causes a four-word copy
   from **mesh part index 2**, regardless of which index matched, into Unit
   `+0x1f8..+0x204` (`0x004f9037` proves the fixed index). Notify an existing
   squad reader via virtual `+0x110`; initialize an existing destructible
   segments controller (`0x00444660`); mark the profile name used; increment
   the counter indexed by profile behavior for allegiance 0 or 1 only.
7. Call fire-control refresh at `0x004f90ce`, then scan all non-null mesh parts
   case-insensitively for `nexus` and `weakpoint`, setting `+0x228/+0x22c`.
   Clear `+0x230/+0x234/+0x238/+0x23c/+0x240/+0x244/+0x248`. If the squad
   reader is null, append allegiance 1 or 6 to list `0x008550c0`, then allegiance
   0 or 6 to `0x008550b0`. Finally request event 4003 at `-1.0f`, priority zero,
   null data and null reusable event (`0x004f91d8`). No active-state test
   guards this final request. Actual delivery belongs to the event manager.

### Conditional draw and completion barrier

Unit Init contains no direct RNG call. Its fire-control helper runs only when
Unit `+0x224 != 0` and flags `+0x2c` bit `0x04` is clear. With no AI target,
it restores angle `+0xec` from `+0xf4` only when deadline `+0x20c < now`.
With a target, an eligible weapon profile can invoke the ballistic solver;
the target arm sets that deadline to `now + 10.0f`. For finite angles the
clamp is **-pi/2 to +pi**, with bits `0xbfc90fdb` and `0x40490fdb`; the stale
export comment claiming symmetric bounds is not the contract.

The enabled helper takes one shared RNG draw, uses the signed remainder by
65,536, multiplies by float word `0x35cccccd` (`0.1f / 65536`), adds the current
event time, and stores the resulting absolute time to float32 at
`0x004fb3bd` before calling `AddEvent_AtTime` for event 4001. Init passes null
reuse. Disabled gates take neither draw nor event. Actor, child initialization
and callbacks happen earlier, so this is not a total per-unit RNG count.

The next connected step needs four concrete dependencies: real profile and
weapon-mode resolution preserving ordered repeated values; the actual mesh
part/attachment and render state; the base Actor/Thing script, collision and
world-publication transaction; and actual child-component Init plus any
present destructible-segments controller. Those results feed the Unit tail,
faction lists and shared scheduler in the order above. A headless leaf test
can falsify tuple order, raw flags, life/angle transfers and conditional event
arguments; it cannot establish the initial world's complete actor/RNG state.

The Unit constructor explicitly initializes readers, lists and many scalar
fields, but it does not establish zero for every byte of the object. In
particular, fourth vector words copied through temporary storage into
`+0x158/+0x204` are not admitted as zero. These findings do not upgrade the
existing direct-actor projection to completed Unit instances. The connected
Component-input calculation below stops before child Init.

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
