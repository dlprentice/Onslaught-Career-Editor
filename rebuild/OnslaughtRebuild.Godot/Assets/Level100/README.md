# Level 100 opening assets

These are the two released facility meshes consumed by the current Level 100
opening slice. The project owner has permission to use, modify, and distribute
the original game assets. They remain copyright of their original rights
holders; `rebuild/LICENSE` covers reconstruction code and does not relicense
the assets.

The source archives came from the released PC game's
`data/resources/meshes` directory. The deterministic OBJ outputs retain static
geometry, normals, UVs, and base part transforms.

| File | Role | SHA-256 |
| --- | --- | --- |
| `Source/m_fb_control_tower.msh.aya` | Released Control Tower CMSH archive | `86AF67E09DC2FD21C7023ACD53EBCB4171F3BF396F836DA85ECFDDA516588D91` |
| `level100-control-tower.obj` | Static geometry consumed by Godot | `C9CBB5B1BB5C1215F5FED1EC4706CA77B99F6FB2DB740A28C012989EAD0D8C9A` |
| `Source/m_fb_tank_factory.msh.aya` | Released Tank Factory CMSH archive | `A507AFDA7B5C6B6B8BED275D442A53B28043BB9D5B65F9EA5BD6F5FF754BF6DE` |
| `level100-tank-factory.obj` | Static geometry consumed by Godot | `50F797AD955EDDE4EB37709BCF692F9DFE8ABD600A7D0CBD6A617B29E1AE7D22` |

Regenerate into an empty local output directory with:

```powershell
py -3 rebuild/tools/cmsh_static_preview.py `
  --checkout . `
  --input rebuild/OnslaughtRebuild.Godot/Assets/Level100/Source `
  --output local-lab/rebuild-godot/generated/level100 `
  --vertex-attributes
```

Sorted outputs `candidate-0001.obj` and `candidate-0002.obj` correspond to the
Control Tower and Tank Factory respectively and must match the hashes above
before promotion.

## Authored placement consumed by the slice

The released `data/resources/100_res_PC.aya` archive has SHA-256
`ED6350C0E214D00AB1BF6A7BD137FBA3E77D0AFE19A6DC4C0607F56AC037496A`.
Its `WRES/WRLD` payload has SHA-256
`137F3FBD67907EFCC15DF8803B156D7F2A1A863A2EB0646E3480A0404C661C8A`.
The retail world loader and pinned `CInitThing::Load` implementation establish
the serialized position, yaw, script, name, and trigger-radius fields used
here.

The Core origin is the released player-one start `(288.6875, 243.25)` in the
world's horizontal X/Y plane. The current slice consumes:

| Thing | Relative X/Y | Retail yaw or radius |
| --- | --- | --- |
| Player-one start | `(0, 0)` | yaw `0.509829998` |
| Control Tower | `(-13.289886, 5.603271)` | yaw `0` |
| Tank Factory | `(10.125, 22.375)` | yaw `1.789433718` |
| Target Zone 1 | `(-43.1875, 33.5)` | radius `5` |
| Firing Range | `(-69.6875, 72.75)` | radius `5` |

`TargetZone1.msl` and `FiringRange.msl` each wait 0.5 seconds before posting
their event. `LevelScript.msl` activates Target Zone 1 first, then makes the
Firing Range the objective after `Reached Target Zone 1`.

The presentation currently uses a flat plane and neutral materials. Retail
terrain elevation, collision, textures/material slots, authored lighting,
facility animation, handedness validation, and complete Level 100 mission
behavior are not established by this slice.
