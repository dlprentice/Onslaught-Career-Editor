# Render/resource static bridge

This bridge routes AYA `MESH` and `TEXT` vocabulary into the retained static
mesh, texture, and render evidence. It does not prove runtime GPU behavior or
visual output.

| Bridge | Canonical evidence | Boundary |
| --- | --- | --- |
| AYA tags | [`../game-assets/aya-resource-tag-family-static-contract.md`](../game-assets/aya-resource-tag-family-static-contract.md) | loader vocabulary only |
| Mesh/resource path | [`mesh-resource-render-static-contract.md`](mesh-resource-render-static-contract.md) | static deserialize, resource, buffer, and renderer relationships |
| Texture/decode path | [`texture-resource-decode-static-contract.md`](texture-resource-decode-static-contract.md) | static lookup/decode/resource relationships |
| Source renderer architecture | [`../source-code/core/engine-system.md`](../source-code/core/engine-system.md) | source-reference architecture, not retail identity |
| Asset extraction | [`../game-assets/extraction-pipeline.md`](../game-assets/extraction-pipeline.md) | guarded local inputs and outputs only |

`MESH` may be used to connect archive parsing to `CMesh`, `CMeshPart`, and
`CDXMeshVB` evidence. `TEXT` may be used to connect archive parsing to
`CTexture` and `CDXTexture` evidence. Exact payloads, animation/skinning,
collision, decoded pixels, GPU upload, material appearance, render ordering,
and rebuild parity remain separate proof.
