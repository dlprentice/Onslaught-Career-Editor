# WRES definition instances join world placement to named CMSH resources

Status: active bounded world-instance and resource-linkage contract
Date: 2026-08-28
Verdict: across all 66 numeric LVLR archives, 4,090 definition-bearing WRES
records join without ambiguity through `default physics.dat` to exactly one named
LVLR `MESH` row and one loose CMSH file in the same level. The join covers 2,731
`BSWD` records and 1,359 `RLWD` records, 134 definitions, and 115 loose meshes.
It closes position/orientation, active state, names, and direct script coordinates
for this Unit/Feature record family; it does not make every WRES record, spawn,
component, named animation range, or render schedule understood.
Evidence: MEASURED — `tools/cmsh_animation_usage_census.py` hash-verified 213
loose CMSH archives, 66 numeric LVLR archives, 733 loose MSL files, and
`default physics.dat` (1,013 inputs) against `G:\bea-asset-mirror\INDEX.jsonl`.
The focused 17-test gate reproduces every count and the synthetic can-fail
controls. Static consumer identities come from the cited pristine-binary notes.
Specimen: `G:\bea-asset-mirror\INDEX.jsonl`, SHA-256
`c45722aeed52e77788c7886cb30b813900d3516b1c387983c442d2b02d4fe4b9`;
`default physics.dat`, SHA-256
`e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14`;
retail VAs cite `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Scope and evidence separation

The AYA envelope remains owned by [aya-container.md](aya-container.md), LVLR
framing and population by [lvlr-archive.md](lvlr-archive.md), and CMSH storage by
[cmsh-mesh.md](cmsh-mesh.md). This contract adds the missing instance edge:

```text
numeric LVLR archive
  WRES / WRLD / {BSWD,RLWD} definition-bearing record
    definition name + placement/state/script strings
      -> default physics.dat definition mesh field
        -> same archive's named MESH logical row
          -> loose resources/meshes/m_<name>.aya
            -> parsed CMSH pose/skeleton properties
```

The scanner reads only the pristine safe-copy data and mirror index. It emits
names, coordinates, hashes, counts, and source-relative positions; no retail
payload is tracked. A generated JSON report is allowed only below ignored
`local-lab/` or `.artifacts/`.

This is deliberately not one undifferentiated “WRES schema.” It proves one
repeated record family by a four-leg agreement: record framing, physics owner,
same-level named membership, and loose CMSH identity. Other WRES object types
remain separate.

## Definition-bearing record layout

The validated record body is:

| Relative field | Stored form | Bounded role |
| --- | --- | --- |
| `+0x00` | `i32` | WRES thing type: `8` Unit or `35` Feature in this family |
| `+0x04` | `float32[3]` | authored position triple |
| `+0x10` | `float32[3]` | authored orientation triple; universal Euler order is not claimed |
| `+0x1C` | `i32` | serialized mesh-number word; **0 in all 4,090 joined records** |
| `+0x20` | `i32` | allegiance word |
| `+0x24` | `i32` | target/reference word |
| `+0x28` | NUL strings | script, instance name, then spawn-script name |
| after strings | `i32`, `i32` | active and attach-scripts booleans, each exactly 0 or 1 |
| after flags | `u8 + ASCII` | physics definition name |
| terminal | `i32 -1` | record-family trailer |

The 4,090 mesh-number words being zero refute the tempting interpretation that
this word indexes the level's `MESH` rows. The concrete mesh is selected through
the definition registry instead:

| WRES type | Physics record | Mesh field | Static/corpus basis |
| ---: | ---: | ---: | --- |
| `8` | `1` (Unit) | field id `9` | `CUnitMesh` RTTI vocabulary plus 3,578 exact same-level/loose joins |
| `35` | `8` (Feature) | field id `2` | `CFeatureMesh__ApplyToFeatureByName @ 0x0043BE10` plus 512 exact joins |

Every accepted record has finite position/orientation values, a matching
physics owner, exactly one same-level named `MESH` row, and exactly one loose
mesh. There are zero unresolved or multiply resolved instances.

The complete scan sees 5,178 length-prefixed physics-name marker candidates.
Record framing, owner type, and boolean/trailer checks reject 1,088. The
remaining 4,090 have unique record offsets and then pass both resource joins;
marker text alone is therefore never counted as an instance.

## Population and placement state

| Population | Count |
| --- | ---: |
| Joined WRES definition instances | 4,090 |
| `BSWD` / `RLWD` | 2,731 / 1,359 |
| Unit type `8` / Feature type `35` | 3,578 / 512 |
| Active / inactive | 4,029 / 61 |
| Unique physics definitions | 134 |
| Unique loose CMSH meshes | 115 |
| Direct WRES script strings resolving to loose MSL | 730 |
| Non-empty WRES script strings not resolving to a loose same-level MSL | 85 |

Level 100 independently cross-checks the general scanner: it yields exactly 38
records, split 33 `BSWD` and five `RLWD`, matching the established specialized
materializer. That agreement is a control, not permission to generalize
Level-100-only gameplay or rendering.

### Unit behaviour reach by released selector

The 3,578 type-8 rows now retain the exact zero-based Unit-definition ordinal,
field-8 serialized behaviour type, Type-12 slot-1 selector, and concrete member
shell. Ordinal and type come from the ordered physics row; the Type-12 leaf maps
that type to the selector, and the central factory maps the selector to the
shell. None is inferred from the mesh name. The join reaches 105 of 160 Unit
definitions in 65 of the 66 numeric archives. Level 857 is the only archive with no type-8 Unit
row; its joined definition-bearing rows are Features. Of the 55 Unit
definitions without this direct WRES edge, 54 still name a mesh and one
(`Base Air Unit`) is a meshless base definition.

| Selector | Member shell | Authored definitions | Directly placed definitions | WRES placements | Levels | `BSWD` / `RLWD` |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `0` | `CMech` | 6 | 0 | 0 | 0 | 0 / 0 |
| `1` | `CPlane` | 0 | 0 | 0 | 0 | 0 / 0 |
| `2` | `CGroundVehicle` | 20 | 2 | 17 | 11 | 0 / 17 |
| `3` | `CInfantryUnit` | 8 | 0 | 0 | 0 | 0 / 0 |
| `4` | `CCannon` | 11 | 10 | 751 | 51 | 527 / 224 |
| `5` | `CBoat` | 9 | 8 | 127 | 36 | 0 / 127 |
| `6` | `CCarrier` | 3 | 3 | 8 | 8 | 0 / 8 |
| `7` | `CBuilding` | 58 | 46 | 987 | 50 | 918 / 69 |
| `8` | `CPlane` | 11 | 9 | 346 | 46 | 0 / 346 |
| `9` | `CBomber` | 5 | 5 | 59 | 21 | 0 / 59 |
| `10` | `CGroundAttackAircraft` | 2 | 1 | 1 | 1 | 0 / 1 |
| `11` | null | 0 | 0 | 0 | 0 | 0 / 0 |
| `12` | `CDropship` | 5 | 5 | 88 | 19 | 0 / 88 |
| `13` | `CMine` | 2 | 2 | 214 | 7 | 0 / 214 |
| `14` | `CHiveBoss` | 1 | 1 | 2 | 2 | 0 / 2 |
| `15` | `CSubmarine` | 1 | 1 | 4 | 4 | 0 / 4 |
| `16` | `CDiveBomber` | 3 | 3 | 34 | 12 | 0 / 34 |
| `17` | `CThunderHead` | 1 | 1 | 2 | 2 | 0 / 2 |
| `18` | `CCarver` | 2 | 1 | 2 | 2 | 0 / 2 |
| `19` | `CGillM` | 1 | 0 | 0 | 0 | 0 / 0 |
| `20` | `CSentinel` | 1 | 1 | 1 | 1 | 0 / 1 |
| `21` | `CWarspite` | 1 | 0 | 0 | 0 | 0 / 0 |
| `22` | `CFenrir` | 3 | 1 | 2 | 2 | 0 / 2 |
| `23` | `CWarspiteDome` | 1 | 1 | 5 | 5 | 5 / 0 |
| `24` | `CPod` | 1 | 0 | 0 | 0 | 0 / 0 |
| `25` | `CSimpleBuilding` | 4 | 4 | 928 | 32 | 874 / 54 |
|  | **Total** | **160** | **105** | **3,578** | **65 unique** | **2,324 / 1,254** |

Nineteen selectors have a direct placement. `BSWD` contributes only selectors
`4`, `7`, `23`, and `25`; all other placed selectors occur only in `RLWD` in
this record family. Conversely, selector `0` Mechs, selector `3` Infantry,
`Gill-M`, `Warspite`, and `Sub Pod` have no direct type-8 placement despite
having authored definitions. This is strong evidence that direct WRES rows are
not the whole population pipeline: dynamic spawns, player/startup ownership,
components, and other record families remain distinct routes. Zero here means
“no direct type-8 definition-bearing WRES row,” not “unused by the game.”

The joined loose CMSH motion classes, counted per placement, are:

| CMSH byte-map class | WRES instances |
| --- | ---: |
| every moving map closes | 129 |
| mixed closing/non-closing | 1 |
| no moving map closes | 1,182 |
| no non-trivial frame map | 2,778 |

All 129 all-closing placements are active, but so are 1,142 non-closing and
2,758 static placements. `active` is therefore not a general animation-loop
selector. It remains valid to use the stronger Level 100 six-mesh agreement in
its bounded owner; this all-world result forbids widening that decision from
`active` alone.

## Animation, script, and skeleton boundaries

The 733 loose MSL files still contain 56 `PlayAnimation*` sites in 15 files.
The direct serialized WRES script-string edge closes only this exact subset:

- 22 sites in three files are connected by serialized script string to three
  joined WRES instances: the Level 500 Rocket Base and the Level 521/522 Hive
  Boss placements;
- 34 sites in 12 files are not direct WRES-script edges.

The unjoined set includes component assignment such as
`GetComponent(...).SetScript("MainGun")`, `GillM*`, and `Vent`, plus Level 530
scripts for which no numeric resource archive exists. Those authored relations
are real, but a component index is not a proved component-definition/mesh edge.
They remain explicit rather than being attached to a parent CMSH by guesswork.
Named call tokens also remain requests to the runtime name table; they are not
invented frame ranges inside `VHFM`/`HORI`/`HPOS`.

None of the 4,090 definition-bearing instances selects one of the seven loose
`BONE` meshes. Their numeric-LVLR membership is still proved, but their initial
spawn/component owner is not this WRES family. Conversely, 41 anonymous
embedded rows below carry one `BONE` array; anonymity prevents assigning those
bones to a named WRES definition.

## The 53 empty LVLR names

The 53 empty logical `MESH` names are no longer just blank membership rows. Each
is structurally a `PMSH/PMS2` owner with one direct CMSH stream at `PMS2+309`:

| Property | Result |
| --- | ---: |
| Empty logical names / empty CMSH internal names | 53 / 53 |
| Unique whole-stream SHA-256 values | 53 |
| Unique primary-core SHA-256 values | 52 |
| Exact normalized-primary-core matches to a loose CMSH | 0 |
| One `BONE` carrier + mixed map closure | 41 |
| One-part, no non-trivial frame map | 12 |

Part counts are `1×12`, `23×19`, `25×17`, `27×3`, and `28×2`. This closes their
container/body identity and refutes silently treating an empty logical name as
“no mesh.” It does **not** close a name: both serialized name fields are empty,
and zero bodies match a loose CMSH after normalizing only the CMSH name buffer.
No WRES/physics key directly names them. They remain 53 anonymous embedded
resources, not 53 guessed aliases.

## The eight loose meshes outside named numeric membership

The eight previously listed loose meshes still have zero named numeric-LVLR
membership, and now also have zero definition-bearing WRES placements:

`m_be_trans`, `m_be_transm`, `m_default`, `m_f_truck`, `m_m_battleship`,
`m_m_truck`, `m_panorama`, and `m_PS2_Normal_Logo3` (suffixes omitted here).

This rules out this exact WRES/physics/named-membership route. It does not prove
unused content: frontend/base loading, defaults, dynamic spawns, other record
families, and dormant assets remain possible.

## Retail consumer anchors

| VA | Static identity | Bounded contribution |
| --- | --- | --- |
| `0x0050B9C0` | `CWorld__LoadWorld` | version-gated world read; named mesh load and Unit/Feature creation fan-out |
| `0x0050D9E0` | `CWorldMeshList__Add` | named mesh-list insertion path reached by world loading |
| `0x0043BE10` | `CFeatureMesh__ApplyToFeatureByName` | resolves a feature definition by name and replaces its owned mesh string |
| `0x004AA630` | `CMesh__FindAnimationIndexByName` | runtime case-insensitive animation-name lookup; serialized owner/ranges remain open |
| `0x005351D0` | `IScript__PlayAnimationWait` | dispatches a resolved animation and resumes saved VM state on completion |

`CWorld__LoadWorld` also calls `CEngine__LoadAllNamedMeshes` and
`CWorldPhysicsManager__CreateThingByType`; see its function note for the bounded
call chain. These are static consumer anchors. They do not prove that all 4,090
records execute in one playthrough, that every active object renders, or that a
specific animation token reaches pixels.

## Reproduce

```bash
python ./tools/cmsh_animation_usage_census.py \
  --data-root "<safe-copy>/data" \
  --mirror-index "<asset-mirror>/INDEX.jsonl" \
  --json-out "local-lab/wres-instance-join/census.json"
```

Focused gate with the local corpus enabled:

```bash
export ONSLAUGHT_GAME_DATA="<safe-copy>/data"
export ONSLAUGHT_ASSET_INDEX="<asset-mirror>/INDEX.jsonl"
python ./tools/cmsh_animation_usage_census_tests.py
```

A clean clone runs seven synthetic can-fail tests and skips the nine
specimen-bound tests when the two external inputs are absent.

## Open questions and cheapest falsifiers

- **Other WRES records:** frame the type `15`, `18`, `19`, `27`, `28`, `36`,
  `37`, `39`, and other owner-specific tails sequentially, then require the same
  physics/resource/name agreement before calling any of them mesh instances.
- **Anonymous embedded identity:** find a serialized WRES/header/configuration
  key that selects one of the 53 `PMS2+309` streams. One-to-one co-occurrence or
  similar skeleton shape is not an identity key.
- **Component scripts:** join each `GetComponent(n).SetScript(name)` through the
  component-definition registry and component mesh field. A parent mesh and an
  integer slot alone are insufficient.
- **Dynamic spawns:** join MSL `SpawnThing`, spawner records, ERES/physics
  definitions, and created runtime objects before assigning the seven loose
  skinned meshes to placements.
- **Scheduling/rendering:** trace one all-closing active instance and one active
  non-closing instance through `CAnimation__Process` and draw submission on a
  disposable copied runtime.
- **Orientation semantics:** prove the three-float order on one non-yaw record
  before naming it a universal Euler convention.

## Claim boundary

WRES/WRLD nesting, the type-8/type-35 definition-record shape, physics mesh
owners, 4,090 exact same-level/loose CMSH joins, transforms/state/name strings,
the ordinal/type/selector/member identity of all 3,578 direct Unit placements,
730 direct MSL-coordinate edges, 22 direct animation call sites, and the 53
anonymous embedded CMSH bodies are bounded. Other WRES record schemas,
alternate population routes for the 55 directly unplaced Unit definitions,
anonymous names, component/dynamic-spawn mesh ownership, named clip
serialization, universal scheduling, execution, rendering, malformed retail
behavior, and parity remain open.
