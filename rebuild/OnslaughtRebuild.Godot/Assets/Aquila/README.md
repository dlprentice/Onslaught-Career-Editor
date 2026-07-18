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
| `aquila-walker.obj` | Static geometry consumed by Godot | `6CD8840A251561D07D5B51850C3DDAA78702998BC5978AAE1BB4537DFCBC753F` |
| `Source/m_f_be2.msh.aya` | Released jet CMSH archive | `35AADA1313C3CBB796BA75DB071321035F7005096DA7C148A7514944F4772B4C` |
| `aquila-jet.obj` | Static geometry consumed by Godot | `075DEB202B805C3C9F08F5C51E8C54277F76AE118DABEF9BDEAEDE787A7E1BD3` |

The OBJ files are deterministic outputs of the existing bounded CMSH profile:

```powershell
py -3 rebuild/tools/cmsh_static_preview.py `
  --checkout . `
  --input rebuild/OnslaughtRebuild.Godot/Assets/Aquila/Source `
  --output local-lab/rebuild-godot/generated/aquila `
  --vertex-attributes
```

The sorted outputs `candidate-0001.obj` and `candidate-0002.obj` correspond to
the walker and jet respectively and must match the hashes above before being
promoted. The current profile retains static geometry, normals, UVs, and base
part transforms. It does not establish material-slot semantics, textures,
animation, runtime part articulation, retail scale, or transform-animation
fidelity.
