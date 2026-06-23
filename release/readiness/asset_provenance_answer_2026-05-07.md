# Asset Provenance Answer - 2026-05-07

Status: public-safe provenance summary over existing private full-install extraction evidence

## Question Answered

Are the WinUI Asset Library and Goodies surfaces using things actually extracted from the retail PC game install, or are they only showing developer/source-tree sample assets?

Current answer: the strongest current catalog/export proof is based on the user's installed PC game resources. The exported texture, mesh, video, language, and Goodies catalog rows are generated from the shipped PC resource files and loose media, with raw extracted outputs kept private under ignored `subagents/` paths.

## Proven Install-Backed Extraction

The strongest current full-install evidence is `release/readiness/real_asset_full_install_export_2026-05-07.md`.

Public-safe counts from that run:

| Area | Proven count |
| --- | ---: |
| Loose textures exported to PNG | `847 / 847` |
| Loose meshes exported to FBX | `213 / 213` |
| Embedded packed mesh bodies exported to FBX | `139 / 139` |
| Model rows with readable metadata | `352 / 352` |
| Model rows with wireframe preview data | `352 / 352` |
| Loose Bink videos inventoried | `66` |
| Language rows exported | `2571` |
| Generated catalog rows | `4050` |

Packed-reference resolution from the same evidence:

| Reference family | Resolved | Total |
| --- | ---: | ---: |
| `TEXT` texture refs | `601` | `601` |
| Reference mesh refs | `209` | `209` |
| `GDIE` texture refs | `206` | `206` |
| `GDIE` mesh refs | `42` | `42` |

This proves the supported extraction/catalog path is not merely a UI stub or developer-source sample path.

## Goodies Provenance

Goodies-specific proof is recorded in `release/readiness/goodies_asset_matrix_2026-05-07.md` and `release/readiness/goodies_catalog_linkage_2026-05-07.md`.

Current public-safe Goodies summary:

| Family | Count | Current meaning |
| --- | ---: | --- |
| Artwork / texture rows | `149` | Texture-bearing shipped Goodie archives with exported preview linkage. |
| Model rows | `45` | Mesh-bearing shipped Goodie archives with exported model linkage. |
| Video rows | `34` | Goodies tied to media handoff/video catalog behavior. |
| Level rows | `5` | Metadata/unlock-oriented Goodie rows. |

The Goodies evidence also records that shipped Goodie archives `71-73` exist and resolve to texture previews, while current source-grid/runtime visibility remains a separate open question.

## What The WinUI App Currently Shows

- Asset Library rows are backed by the generated catalog when a real catalog is configured.
- Representative native WinUI smoke has loaded the fresh full-install catalog and cycled real texture, loose-model, embedded-model, and Goodies rows.
- In-app model preview currently means bounded metadata plus wireframe geometry from exported FBX rows.
- Video Goodies hand off to Media rather than pretending the Goodie row itself plays the Bink file.

## Still Not Proven

- Final textured, material-aware, animated native 3D model viewing.
- Skeletons, animation playback, lighting, UV/material display, or renderer parity.
- Runtime Goodies unlock criteria, wall animation, and in-game model-viewer behavior.
- Row-by-row native visual proof for every extracted media/model/texture row.
- Public redistribution rights for extracted assets.
- A rebuildable open-source game runtime.

## Operating Rule

Future UI and docs must distinguish:

- extracted from shipped retail install,
- linked through generated catalog,
- shown as in-app wireframe/metadata,
- previewed as texture/video,
- source/reference-only,
- sample/demo-only,
- runtime-proven in BEA.

Those are different proof levels and should not be collapsed into "working asset extraction" or "rebuild-ready."
