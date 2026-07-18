# Aquila render meshes

This directory contains the two original Federation Aquila render meshes now
used by the handling client. The project owner has permission to use, modify,
and distribute the original game assets. These assets remain copyright of
their original rights holders; `rebuild/LICENSE` covers the reconstruction
code and does not relicense the assets.

The source files came from the released PC game's
`data/resources/meshes` directory. Stuart Gillam's pinned source independently
names `f_be1.msh` and `f_be2.msh` as the Federation walker and jet render
meshes in `references/Onslaught/BattleEngine.cpp`.

| File | Role | SHA-256 |
| --- | --- | --- |
| `Source/m_f_be1.msh.aya` | Released walker CMSH archive | `D4C8FA752229AF4111B31EFA5FF5928C892736FAA6A807915412767F3CD3C6B2` |
| `aquila-walker.obj` | Static geometry and base-material groups consumed by Godot | `ED05DFC93BF9DDA27CE0E0966A261A60F8105AE2966724187557F010C40AB49B` |
| `Source/m_f_be2.msh.aya` | Released jet CMSH archive | `35AADA1313C3CBB796BA75DB071321035F7005096DA7C148A7514944F4772B4C` |
| `aquila-jet.obj` | Static geometry and base-material groups consumed by Godot | `92A3495E278884B63649E114EDDB7373B04AF2AA92AAB25C3F7184DD1140D821` |
| `Textures/cockpit.texture.aya` | Released 512×512 `meshtex%cockpit.tga(0)A1R5G5B5.aya` base texture | `C62D0C668226F056DB7455C8A5A8FA7D55AB7621ADE1E58392D6AAAD3C00F0CC` |
| `Textures/be-tex-a.texture.aya` | Released 512×512 `meshtex%BE_texA.tga(0)A1R5G5B5.aya` base texture | `86F9F54AE97BA4E3782C65909D1D93B86566228B1132829EBB93816EB5A4705B` |
| `Textures/be-tex-b.texture.aya` | Released 1024×1024 `meshtex%BE_texB.tga(0)A1R5G5B5.aya` base texture | `EA01431A4023ABD517DAF5A27066EB7EDF706100FB3991566726FB4530490B60` |

The OBJ files are deterministic outputs of the existing bounded CMSH profile:

```powershell
py -3 rebuild/tools/cmsh_static_preview.py `
  --checkout . `
  --input rebuild/OnslaughtRebuild.Godot/Assets/Aquila/Source `
  --output local-lab/rebuild-godot/generated/aquila `
  --vertex-attributes `
  --primary-material-groups
```

The sorted outputs `candidate-0001.obj` and `candidate-0002.obj` correspond to
the walker and jet respectively and must match the hashes above before being
promoted. The current profile retains static geometry, normals, UVs, base part
transforms, and each mesh group's layer-zero `TEXR` assignment. Steam
`CMeshRenderer__RenderMeshWithLayerPasses` establishes six ordered texture
passes, and the pinned `AyaModelImporter.cs` also assigns primitives from
`TEXR[0]`; the client therefore consumes only that unambiguous base layer. The
shared `Chrome3.tga` reference occurs at layer two and remains intentionally
unimplemented until its released blend semantics are established. Animation,
runtime part articulation, and transform-animation fidelity remain outside this
slice. The client consumes both retained meshes at scale `1.0` and grounds them
from their exact lower bounds; copied-runtime framing independently agrees with
the raw retail-unit dimensions.
