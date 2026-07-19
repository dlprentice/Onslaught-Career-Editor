# Aquila render and cockpit meshes

This directory contains the original Federation Aquila render meshes and
walker cockpit now used by the handling client. The project owner has
permission to use, modify, and distribute the original game assets. These
assets remain copyright of their original rights holders; `rebuild/LICENSE`
covers the reconstruction code and does not relicense the assets.

The source files came from the released PC game's
`data/resources/meshes` directory. Stuart Gillam's pinned source independently
names `f_be1.msh` and `f_be2.msh` as the Federation walker and jet render
meshes in `references/Onslaught/BattleEngine.cpp`.

| File | Role | SHA-256 |
| --- | --- | --- |
| `Source/m_f_be1.msh.aya` | Released walker CMSH archive consumed directly by Godot | `D4C8FA752229AF4111B31EFA5FF5928C892736FAA6A807915412767F3CD3C6B2` |
| `Source/m_f_be2.msh.aya` | Released jet CMSH archive | `35AADA1313C3CBB796BA75DB071321035F7005096DA7C148A7514944F4772B4C` |
| `Source/m_cockpit2.msh.aya` | Released walker first-person cockpit CMSH archive | `008B9292C59A5564BA3696F65D5BD51030D3E57250BC792D9D2B7F01292CDD4A` |
| `aquila-jet.obj` | Static geometry and base-material groups consumed by Godot | `92A3495E278884B63649E114EDDB7373B04AF2AA92AAB25C3F7184DD1140D821` |
| `aquila-walker-cockpit.obj` | Authored walker cockpit pose with ten material groups merged into two loaded surfaces | `0E81A2B48AB2202620B3C0DCCD08FE2FFBD76B5D668318D21F0FF72551DD5BD9` |
| `Textures/cockpit.texture.aya` | Released 512×512 `meshtex%cockpit.tga(0)A1R5G5B5.aya` base texture | `C62D0C668226F056DB7455C8A5A8FA7D55AB7621ADE1E58392D6AAAD3C00F0CC` |
| `Textures/bluegun-light.texture.aya` | Released 64×64 `meshtex%A8_bluegunlight_LIT.tga(0)A8R8G8B8.aya` cockpit-light texture | `85858E7809A974B74F3DB5A169E081FC9DD506558F1CA99FA47C7832D8552FC5` |
| `Textures/be-tex-a.texture.aya` | Released 512×512 `meshtex%BE_texA.tga(0)A1R5G5B5.aya` base texture | `86F9F54AE97BA4E3782C65909D1D93B86566228B1132829EBB93816EB5A4705B` |
| `Textures/be-tex-b.texture.aya` | Released 1024×1024 `meshtex%BE_texB.tga(0)A1R5G5B5.aya` base texture | `EA01431A4023ABD517DAF5A27066EB7EDF706100FB3991566726FB4530490B60` |

The jet OBJ is a deterministic output of the existing bounded CMSH profile:

```powershell
py -3 rebuild/tools/cmsh_static_preview.py `
  --checkout . `
  --input rebuild/OnslaughtRebuild.Godot/Assets/Aquila/Source `
  --output local-lab/rebuild-godot/generated/aquila `
  --vertex-attributes `
  --primary-material-groups
```

The cockpit uses the same bounded converter with the clean retail walk pose:

```powershell
py -3 rebuild/tools/cmsh_static_preview.py `
  --checkout . `
  --input rebuild/OnslaughtRebuild.Godot/Assets/Aquila/Source `
  --output local-lab/rebuild-godot/generated/aquila-frame25 `
  --vertex-attributes `
  --primary-material-groups `
  --hierarchy-frame 25
```

The sorted outputs `candidate-0001.obj` and `candidate-0003.obj` correspond to
the cockpit and jet. The cockpit must match the frame-25 hash above; the jet has
one authored hierarchy frame and matches either invocation. The
walker no longer uses the flattened `candidate-0002.obj`; the client validates
and loads the exact retained AYA,
preserving its 63-part parent/reference hierarchy and 54 layer-zero material
surfaces. Steam
`CMeshRenderer__RenderMeshWithLayerPasses` establishes six ordered texture
passes, and the pinned `AyaModelImporter.cs` also assigns primitives from
`TEXR[0]`; the client therefore consumes only that unambiguous base layer. The
shared `Chrome3.tga` reference occurs at layer two and remains intentionally
unimplemented until its released blend semantics are established.

The cockpit archive has 21 composed parts and seven geometry-owning parts. Its
zero-group reference PMVB records contain no vertex stream; unused profile
words in those records are not interpreted. Clean copied-retail Level 100,
Steam's first-person camera path, and Stuart's `cockpit2.msh` selection establish
the asset's current role. Its `CAMD` table maps the selected runtime `walk`
animation to authored frame 25. Godot consumes seven `cockpit.tga` groups and
three blue-light groups, merged by texture into two surfaces. The shared
`Chrome3.tga` secondary pass remains
outside this bounded layer-zero rendering.

The released `LegMotion` table supplies the movement-driven 101-frame gait.
One fresh copied-retail Level 100 run supplies the stable no-input local pose
for the twenty leg-chain parts that the retail mech controller adjusts at the
authored start; two read-only samples 100 ms apart had the same complete pose
hash. This establishes the opening stance and a bounded authored gait, not the
retail controller's procedural terrain IK, arbitrary-slope foot placement,
transform animation, or damage states. The client consumes both retained meshes
at scale `1.0`; copied-runtime framing independently agrees with the raw
retail-unit dimensions.
