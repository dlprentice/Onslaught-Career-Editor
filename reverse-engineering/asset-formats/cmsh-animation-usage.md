# CMSH stores pose lanes; LVLR, WRES, physics, and MSL expose bounded usage

Status: active bounded animation, position-skinning, and authored-usage contract
Date: 2026-08-23
Verdict: the 213 loose CMSH meshes contain 3,774 part tracks; 64 meshes and 659
parts have non-trivial `VHFM` maps, exactly seven meshes carry one `BONE` array,
and exactly 17 camera parts carry one `HFOV` value. Across the 66 numeric LVLR
archives, 3,432 of 3,485 `MESH` rows join by authored name to 205 loose meshes;
the other 53 rows each own an anonymous embedded CMSH. The WRES/physics join now
connects 4,090 definition-bearing placements to exactly one named level row and
one loose CMSH. The 733 loose MSL files contain 56 active `PlayAnimation*`
calls in 15 files; 22 sites join through script strings on three WRES instances.
The focused matrix-palette pass additionally closes the seven-file released
position blend. These remain storage and authored-reference contracts, not proof
that every named track is scheduled or rendered.
Evidence: MEASURED — `tools/cmsh_animation_usage_census.py` parsed and
hash-verified 213 meshes, 66 numeric LVLR archives, 733 MSL files, and
`default physics.dat` (1,013 inputs) against
`G:\bea-asset-mirror\INDEX.jsonl`; the focused 17-test gate reproduces the
counts, names, joins, and can-fail controls. Retail consumer VAs come from the
cited pristine-binary notes and remain static evidence.
Specimen: `G:\bea-asset-mirror\INDEX.jsonl`, SHA-256
`c45722aeed52e77788c7886cb30b813900d3516b1c387983c442d2b02d4fe4b9`;
retail VAs cite `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Scope and identity

The selected 1,013 files match the mirror index row-for-row by SHA-256:

| Input lane | Files | Role in this contract |
| --- | ---: | --- |
| `resources/meshes/*.msh.aya` | 213 | loose CMSH pose, hierarchy, camera, and skinning census |
| numeric `resources/NNN_res_PC.aya` | 66 | LVLR `MESH` authored-name membership |
| `MissionScripts/**/*.msl` | 733 | authored `PlayAnimation` / `PlayAnimationWait` call sites |
| `default physics.dat` | 1 | Unit/Feature definition-to-mesh fields used by WRES records |

The AYA outer envelope remains owned by [aya-container.md](aya-container.md),
the CMSH stream by [cmsh-mesh.md](cmsh-mesh.md), and the LVLR stream by
[lvlr-archive.md](lvlr-archive.md). This pass read the pristine safe-copy data
and the mirror index only. It launched no executable, modified no retail file,
and tracks no asset or extracted payload.

The wider parser gate still accounts for **367** CMSH streams: 213 loose, 15
reachable through loose post-body siblings, and 139 embedded in numeric LVLR
archives. The detailed counts below deliberately use the 213 loose files, where
one stable source filename, one internal CMSH name, and one mirror hash identify
each authored mesh without treating a nested copy as another independent asset.

## Pose and frame properties

Every loose part has one bounded local-pose lane:

| Field/chunk | Measured layout and role |
| --- | --- |
| `CMSP+0xB8` | `vFrames`, the length of `VHFM` |
| `CMSP+0xBC` | `hFrames`, the number of authored `HORI`/`HPOS` poses |
| `VHFM` | `vFrames` bytes; each byte is in `[0,hFrames)` and selects one hierarchy pose |
| `HORI` | `hFrames × 48`; three basis rows of three floats plus one carried word per row |
| `HPOS` | `hFrames × 16`; three position floats plus one carried word |
| `CPOS` / `CORI` | per-virtual-frame composed model-space caches, sometimes collapsed to one static record |
| `HFOV` | when present, one float per hierarchy pose on a camera part |

Across 3,774 parts, the largest `vFrames` is **501** and the largest `hFrames`
is **250**. Exactly **659 parts in 64 meshes** use more than one `VHFM` value.
Classifying only the byte-map shape gives:

| Loose-mesh class | Meshes | What the classification says |
| --- | ---: | --- |
| no non-trivial frame map | 149 | every part selects one hierarchy-pose index, even when `vFrames > 1` |
| every moving map closes on its first index | 15 | each moving part has `VHFM[0] == VHFM[-1]` |
| no moving map closes on its first index | 37 | each moving part ends on a different index |
| mixed closing/non-closing maps | 12 | both shapes occur in one mesh |

Closure is a byte property, not a universal playback instruction. Level 100 is
the strongest scheduling cross-field result: the three running WRES facilities
`FB_Docks`, `FB_radar_station`, and `FB_Solar_Pod` have cyclic maps, while the
three inactive turret placements `ft_blaster`, `ft_pulse`, and `ft_sam` have
saturating maps. That join is pinned independently by
`Level100StaticWorldAnimationTests`. The all-world
[WRES instance join](wres-instance-join.md) now proves placement/active fields:
all 129 all-closing placements are active, but so are 1,142 non-closing and
2,758 static placements. Active state alone therefore does not generalize the
Level 100 playback decision.

`CMSP+0xB4` (`aFrames`) remains unnamed. Its complete value population is
**0=1,987, 1=1,760, 2=27**. Twenty-six of the 27 value-2 parts are in meshes with
no non-trivial `VHFM` map, so the field is not safely describable as the number
of visible key poses or named clips.

The format still stores no frame rate. A downstream 20 Hz playback decision is
engine evidence, not a value read from CMSH.

## Camera lane

Exactly 17 meshes carry `HFOV`, always on a part named `Camera01`, and every one
contains one finite float:

| Stored value | Camera parts |
| ---: | ---: |
| `180.0` | 2 |
| `90.0` | 13 |
| `75.78888702392578` | 1 |
| `34.70261001586914` | 1 |

`CMeshPart__LoadFromStream @ 0x004B27A0` loads the positional
`HORI`/`HPOS`/`HFOV` sequence. The only proved post-load `HFOV` reader is in
`CRTCutscene__BuildCurrentFrameOutputs`: it maps a virtual frame through `VHFM`
and returns that hierarchy pose's FOV parameter. The player cockpit does not use
its `Camera01` `HFOV`; the complete bounded path is
[player-camera-attach-and-mesh-hfov-2026-07-26.md](../binary-analysis/player-camera-attach-and-mesh-hfov-2026-07-26.md).

## Skeleton and skinning lane

There is no separate loose skeleton family. In each of the seven skinned CMSH
files, exactly **part 1** owns one `BONE` array. Each `BONE` element is a part
index in the same mesh; the indexed part's 32-byte CMSP name is the bone name.

| Mesh | Bones | Naming contract | Numeric LVLR membership |
| --- | ---: | --- | ---: |
| `m_f_dtroop.msh.aya` | 18 | `Bip01` humanoid parts | 6 archives |
| `m_ftrooper.msh.aya` | 18 | `Bip01` humanoid parts | 43 archives |
| `m_mcommando.msh.aya` | 18 | `Bip01` humanoid parts | 9 archives |
| `m_mfiredude.msh.aya` | 19 | `Bip01` humanoid parts, including left/right clavicle | 23 archives |
| `m_mgrunt.msh.aya` | 19 | `Bip01` humanoid parts, including left/right clavicle | 39 archives |
| `m_Sentinel Arm Big.msh.aya` | 14 | `Bone01`…`Bone14`; serialized slot order places `Bone12` before `Bone11` | 1 archive (`800`) |
| `m_Sentinel Arm Small.msh.aya` | 14 | `Bone01`…`Bone14` in numeric order | 1 archive (`800`) |

The 48-byte skinned vertex form has three float words at `+0x0C`. All 9,609
shipped slot words are exact non-negative multiples of three; division by three
produces an in-range index into that part's `BONE` array. Every declared bone
slot is used by at least one vertex in each of the seven meshes. The dedicated
[matrix-palette contract](cmsh-matrix-palette-skinning.md) proves the GPU
consumer, c10 palette, renderer-owned binary32 one-third pre-scale, and
released position coefficients `(0, 2s, s)` for
`s = float32(0x3EAAAAAB)`. Its focused
[typed-order/normal successor](cmsh-matrix-normal-deformation.md) closes the
row-vector bind/current product as `T_bind^-1 * R_bind^-1 * R_current *
T_current` and proves that the normal-bearing linked shader lights serialized
`v3` directly with zero c10 palette rows, slot weights, translation, or normal
normalization.

The runtime also uses semantic part names outside this serialized skinning
array. `CMCTentacle__Init @ 0x0049CC40` searches names such as `tentacle`,
`tether`, `head`, `tethercp`, `headcp`, and the `bone` prefix for a separate
spline/controller path. That static consumer is documented in
[MCTentacle.cpp.md](../binary-analysis/functions/MCTentacle.cpp.md); name matching
does not turn every similarly named part into a `BONE` entry.

## LVLR authored mesh membership

The 66 numeric LVLR archives contain **3,485** top-level `MESH` chunks. The
validated logical-name route is `PMSH/PMS2:name@0x10` when the inner wrapper is
present, otherwise `PMSH:name@0x08`. Prefixing the authored name with the loose
shelf's `m_` convention joins:

- **3,432 occurrences** to **205 distinct loose meshes**;
- **53 occurrences** whose authored name is empty;
- zero non-empty unresolved names.

Eight loose meshes are absent from numeric-LVLR `MESH` membership:
`m_be_trans`, `m_be_transm`, `m_default`, `m_f_truck`, `m_m_battleship`,
`m_m_truck`, `m_panorama`, and `m_PS2_Normal_Logo3` (suffixes omitted here for
readability). Absence from this one membership set does not prove an asset is
unused: base/frontend loading, executable defaults, another container, and
dormant content remain separate routes.

The all-301 LVLR top-level census contains 3,492 `MESH` chunks. The difference
is seven Goodie-archive mesh rows; this document's 3,485 denominator is the
numeric-world slice, not a correction to [lvlr-archive.md](lvlr-archive.md).
`MESH` membership alone proves only that a resource is packed with a level. The
dedicated [WRES instance contract](wres-instance-join.md) closes 4,090
definition-bearing Unit/Feature placements through physics mesh fields. Other
WRES types, dynamic spawns, rendering, and animation scheduling remain separate.

## Authored MSL animation calls

The 733 loose MSL files contain **56 active call sites in 15 files across nine
level directories** after stripping `//` comments:

| Command | Sites |
| --- | ---: |
| `PlayAnimation` | 32 |
| `PlayAnimationWait` | 24 |

The exact authored token spellings are `open` 12, `opening` 12, `closed` 10,
`closing` 8, `Idle` 8, `Hit` 2, and one each of `Activate`, `Activated`,
`Opening`, and `Open`. Case variants are retained because they are authored
bytes; the retail name lookup itself uses `stricmp`.

The two argument-word combinations are `(FALSE,FALSE)` 2, `(FALSE,TRUE)` 8,
`(TRUE,FALSE)` 22, and `(TRUE,TRUE)` 24. Their friendly meanings remain open.
`IScript__PlayAnimationWait @ 0x005351D0` proves only that both are byte-masked,
that the name is resolved through `CMesh__FindAnimationIndexByName`, and that
completion resumes a saved VM snapshot. See
[IScript__PlayAnimationWait.md](../binary-analysis/functions/IScript.cpp/IScript__PlayAnimationWait.md).

The WRES pass joins **22 sites in three files** directly to three placements:
Level 500 Rocket Base and Level 521/522 Hive Boss. The other 34 sites in 12
files include component `SetScript` routes (`MainGun`, `GillM*`, and `Vent`) and
Level 530 scripts with no numeric resource archive. A component index is not a
proved component-definition/mesh edge, so those calls remain explicit rather
than being attached to the parent CMSH by guesswork.

## Retail consumer anchors

| VA | Static identity | Bounded contribution |
| --- | --- | --- |
| `0x004B27A0` | `CMeshPart__LoadFromStream` | positional `VHFM`/`HORI`/`HPOS`/`HFOV` and cache load |
| `0x004AA630` | `CMesh__FindAnimationIndexByName` | case-insensitive search of count `+0x14`, table `+0x18`, stride `0x24`; returns the record's `+0x10` value or `-1` |
| `0x00404790` | `CAnimation__Process` | advances animation state and calls owner vtable `+0xEC` on the observed completion path |
| `0x00404860` | `CAnimation__SetAnimMode` | mode/reset/force-looped setup through the render-frame increment path |
| `0x004F44A0` | `CComplexThing__SetAnimMode` | lazy `CAnimation` allocation and forwarding |
| `0x005351D0` | `IScript__PlayAnimationWait` | name lookup, play dispatch, VM stop, completion-resume contract |
| `0x0054C920` | `CDXMeshVB__BuildSkeletalVB` | skeletal vertex-buffer construction route |
| `0x00549570` | `CMeshRenderer__RenderMeshCore` | samples each BONE part at frame zero/current pose, constructs the palette, scales all 16 matrix elements by `[0x005D8608]`, and copies it to `0x009C69D4` |
| `0x00502920` | `CVertexShader__ApplyCustomRenderStateShaderConstants` | uploads a separate c7-c9 one-third diagonal, then reads/transposes and uploads the already-scaled global palette to c10+ |
| `0x0049CC40` | `CMCTentacle__Init` | semantic part-name scan and controller-owned bone/spline buffers |

These anchors demonstrate consumers and call shapes. They do not prove that the
CMSH frame chunks themselves contain the runtime table of named clips. This pass
found no bounded named-clip field in `VHFM`/`HORI`/`HPOS`; the origin and complete
layout of the `CMesh+0x14/+0x18` table remain open.

## Reproduce

The tracked scanner accepts an explicit user-supplied data root, verifies every
selected file against the optional mirror index, and refuses to publish outside
an ignored `local-lab` or `.artifacts` path:

```bash
python ./tools/cmsh_animation_usage_census.py \
  --data-root "<safe-copy>/data" \
  --mirror-index "<asset-mirror>/INDEX.jsonl" \
  --json-out "local-lab/cmsh-animation-usage/census.json"
```

Focused gate with the local corpus enabled:

```bash
export ONSLAUGHT_GAME_DATA="<safe-copy>/data"
export ONSLAUGHT_ASSET_INDEX="<asset-mirror>/INDEX.jsonl"
python ./tools/cmsh_animation_usage_census_tests.py
```

A clean clone runs seven synthetic can-fail tests and skips the nine
specimen-bound tests when those two inputs are absent.

## Open questions and cheapest falsifiers

- **Named clips and frame ranges:** trace every write to `CMesh+0x14/+0x18`
  during one mesh load, then join each 0x24-byte record to the frame interval the
  render-frame path selects. A name lookup alone does not locate the table's
  serialized owner.
- **`aFrames`:** join `CMSP+0xB4` to the exact `CMeshPart__LoadFromStream` branch
  and one downstream reader; its current distribution refutes a simple visible-
  key-count label.
- **Remaining skinning:** obtain a raw 48-byte runtime VB comparison and observe
  one infantry draw. Position weights, typed palette order, released normal
  dataflow, and the two Sentinel runtime instances are closed by the two focused
  skinning contracts.
- **Other WRES/component edges:** the type-8/type-35 definition family is now
  closed across all 66 numeric worlds. Sequentially frame the remaining record
  types and join component `SetScript` indices through component definitions
  before assigning the other 34 MSL call sites to meshes.
- **Scheduling:** compare a closing-map and a non-closing-map mesh under one
  copied-runtime trace before generalizing the Level 100 active/loop relation.
- **Nested identity:** normalize the 15 loose-nested and 139 embedded CMSH
  streams onto loose names/hashes before counting them as variants or copies.
- **Malformed hierarchy behavior:** use only a disposable copied profile for a
  cycle, out-of-range `BONE`, or out-of-range `VHFM` test.

## Claim boundary

Pose-table dimensions, frame-map range/shape, bone-to-part names, palette-slot
indices, released position weights/blending, typed frame-zero/current palette
order, released normal dataflow, camera-lane values, numeric-LVLR membership,
4,090 definition-bearing world-instance joins, 53 anonymous embedded bodies,
and loose-MSL call sites are bounded. Named-clip serialization, interpolation,
other WRES/component/dynamic-spawn joins, general
scheduling, malformed-input behavior, wider runtime rendering, and parity remain
open.
