# Level 100 opening assets

These are the released heightfield, macro terrain inputs, cube-25 sky, and two
facility meshes consumed by the current Level 100 opening slice. The project
owner has permission to use, modify, and distribute the original game assets.
They remain copyright of their original rights holders; `rebuild/LICENSE`
covers reconstruction code and does not relicense the assets.

The two source mesh archives came from the released PC game's
`data/resources/meshes` directory. The deterministic OBJ outputs retain static
geometry, normals, UVs, and base part transforms.

| File | Role | SHA-256 |
| --- | --- | --- |
| `Source/level100-heightfield.hfld.bin` | Exact released `HFLD` chunk consumed by Godot | `7A4C7C5B9400E2C8D2325CECB5C44701CD8A6E6F8609CBC8BC31D449C0620F5D` |
| `Source/level100-mixer-set-10.mapt.bin` | Exact largest `MAPT` mip selected by the Level 100 `CHFD` mixer-set value | `C21576AE7EA75FA800AB4117C1479AEB70359A1ACC84EDD9508895EB339612F1` |
| `Source/level100-mixer-map.mmap.bin` | Exact released `MMAP` material-weight and lighting-mask payload | `45045D248E27366080614C1AD26FC9E711BC9656F4F79210EAC63D2A20938361` |
| `Source/m_fb_control_tower.msh.aya` | Released Control Tower CMSH archive | `86AF67E09DC2FD21C7023ACD53EBCB4171F3BF396F836DA85ECFDDA516588D91` |
| `level100-control-tower.obj` | Static intact geometry and base-material groups consumed by Godot | `9A2B9C287BFF21DD7E3B560EE36CC7D7CAFB99399B3003BF2E81A832FBD6F6BA` |
| `Source/m_fb_tank_factory.msh.aya` | Released Tank Factory CMSH archive | `A507AFDA7B5C6B6B8BED275D442A53B28043BB9D5B65F9EA5BD6F5FF754BF6DE` |
| `level100-tank-factory.obj` | Static intact geometry and base-material groups consumed by Godot | `895813A6D8FD6938934957E934F23B58EC5C059E6CE8F8F9472BC4438B49D53C` |
| `Textures/facility-hanger-more-bits-lit.texture.aya` | Released 512×512 `meshtex%A8_FB_hangermorebits_lit.tga(0)A8R8G8B8.aya` base texture | `F04B96E9E2A121F74729F63194B01FAC58384B150F476B5E03D17B03B6DCC6E3` |
| `Textures/facility-hanger-bits.texture.aya` | Released 512×512 `meshtex%FB_hangerbits.tga(0)A1R5G5B5.aya` base texture | `8E73098EAEB3C961B7CD63C3FBDF2338B22EFBE191BF956034DB9A69E71C041A` |
| `Textures/facility-hanger-top-01.texture.aya` | Released 512×512 `meshtex%FB_hangertop01.tga(0)A1R5G5B5.aya` base texture | `54ADEB37D60FBC8209DBB75EB61FD39898B3F07E808E05C408DC740FF4647FD4` |
| `Textures/facility-hanger-top-02.texture.aya` | Released 512×512 `meshtex%FB_hangertop02.tga(0)A1R5G5B5.aya` base texture | `E09455015CC79439AA33C5FB6B4A70B75DE9F2D5392AA7CD08BBF42D8FC6F78F` |
| `Sky/cube25-cent.texture.aya` | Released 512×512 cube-25 center DXT1 texture | `1AAD6CC8F85B6BB7CCBB8D2C7B0E6AA31722A9ADBDE5A3F19B248430CA83469E` |
| `Sky/cube25-up.texture.aya` | Released 512×512 cube-25 up DXT1 texture | `419E2424BCFD698058D72111FFA7D84FDC9022E03815DB7C0DA28403F4925F3C` |
| `Sky/cube25-right.texture.aya` | Released 512×512 cube-25 right DXT1 texture | `830C9B965C76A4023C2415B7C8924CA32590562C850CC84E92C003E173263D11` |
| `Sky/cube25-down.texture.aya` | Released 512×512 cube-25 down DXT1 texture | `4770829BA631E93FBC33DB2012754DA75A06BFCCC2FB2B36875E92032E22D19D` |
| `Sky/cube25-left.texture.aya` | Released 512×512 cube-25 left DXT1 texture | `D7CBCE30E51473DDC89ED0C44326E598DAC4D2682F64EF20C19237AFD2CEBE14` |

Regenerate into an empty local output directory with:

```powershell
py -3 rebuild/tools/cmsh_static_preview.py `
  --checkout . `
  --input rebuild/OnslaughtRebuild.Godot/Assets/Level100/Source `
  --output local-lab/rebuild-godot/generated/level100 `
  --vertex-attributes `
  --primary-material-groups
```

Sorted outputs `candidate-0001.obj` and `candidate-0002.obj` correspond to the
Control Tower and Tank Factory respectively and must match the hashes above
before promotion.

## Heightfield consumed by the slice

The retained `HFLD` is the smallest exact terrain input used by the client. It
comes from `100_res_PC.aya` → `ERES` → `ENGN` → `MAP!` and contains a
5,084-byte `CHFD` metadata block followed by 663,552 bytes of signed 16-bit
`HFDT` samples. The released loader at `0x0047F750` reads 64×64 tiles of 9×9
samples. The released low-resolution vertex builder at `0x00544FC0` samples a
65×65 grid at eight-unit intervals and multiplies heights by the `CHFD`
scale `0.0009155832231044769`; the Godot client follows that exact coarse
sampling pattern.

The terrain mesh is translated so the authored player-one start
`(288.6875, 243.25, -10)` is the reconstruction origin. The client samples the
same retained heightfield to place presentation objects on the surface. This
does not yet put terrain elevation or collision into deterministic Core.

## Terrain appearance and environment consumed by the slice

The retained `MAPT` and `MMAP` are exact chunks from the same released Level
100 `ERES`. The client requires mixer set 10, six 256×256 indexed material
textures and palettes, all 4,096 `MCEL` material/weight records, and the 512×512
`MSHD` lighting mask. It follows the released blend and RGB565 lighting path at
`0x0047EFF0` to create the 512×512 macro landscape texture at load time.

The `CHFD` also selects cube 25 and supplies the fog color/density, sun,
anti-sun and ambient colors, and sun vector. The five exact DXT1 cube textures
use the released formatter order `cent`, `up`, `right`, `down`, `left` and the
20 released sky vertices. The sky is camera-centered and excluded from scene
fog, matching the released no-depth world backdrop rather than treating it as
distant terrain.

This establishes the authored macro material layout and environment inputs,
not pixel parity. The released repeating terrain-detail and cloud-shadow
stages, overlay tile updates, separate visible-sun particle, trees, and distant
props are not implemented.

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

The presentation consumes the four exact layer-zero facility textures and
preserves their mesh-group assignments. The shared `Chrome3.tga` layer-two
reference is not interpreted as a base texture or a guessed metallic map. The
two retained render meshes represent the intact facilities; their released
damage and destruction states are not implemented. Terrain collision and
movement response, retail detail passes, facility animation, complete world
population, and complete Level 100 mission behavior are not established by
this slice.
