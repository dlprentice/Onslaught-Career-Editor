# Wave1191 CPDSimpleSprite Render Residual Current-Risk Review

Status: complete static read-back evidence pending artifact commit
Date: 2026-06-06
Tag: `wave1191-cpdsimplesprite-render-residual-current-risk-review`

Wave1191 accounts for `7 CPDSimpleSprite render residual current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator. This is a static render-contract review for the CPDSimpleSprite atlas, vector, curve, and quad-emission helpers; it is meant to make the clean-room rebuild specification more concrete, not to claim runtime or visual particle parity.

Targets:

| Address | Function | Static contract |
| --- | --- | --- |
| `0x004c0940` | `CPDSimpleSprite__SetUVFromTileIndex` | Computes UV rectangles from packed tile-index/grid state and writes the rectangle at `this+0xb8..this+0xc4`, with fallback full `0..1` UVs. |
| `0x004c5280` | `CPDSimpleSprite__CopyTransformMatrix` | Copies observed simple-sprite basis/transform fields into a caller output matrix while preserving the conservative unused-context signature. |
| `0x004c5c50` | `CPDSimpleSprite__BuildUvAtlasBuckets` | Initializes five tile-grid bucket families under `DAT_00829e58` and marks one-shot completion through `DAT_0082b39c`. |
| `0x004c5d50` | `CPDSimpleSprite__ProcessAndRenderSpriteList` | Walks active sprite particles, evaluates scale/colour/orientation paths, calls the CPDSimpleSprite render helpers, emits quad vertices through `CVBufTexture__GetVertexPtrAt`, and writes six indices through `DXParticleTexture__GetIndexBuffer`. |
| `0x004c78b0` | `CPDSimpleSprite__ScaleVec3InPlace` | Scales three consecutive float components in place; render-list calls are at `0x004c745f`, `0x004c7689`, and `0x004c7697`. |
| `0x004c78d0` | `CPDSimpleSprite__ReciprocalVec3Magnitude` | Computes `1.0 / sqrt(x*x + y*y + z*z)` for a three-float vector; no zero-length guard is visible in the retail helper. |
| `0x004c7950` | `CPDSimpleSprite__EvaluateCurveDrivenScale` | Evaluates recursive expression nodes with observed pow/exp/sin/cos/inv/log/rand-style cases plus clamp/wrap output modes. |

Read-back evidence:

| Item | Result |
| --- | --- |
| Pre/post rows | `7` metadata rows, `7` tag rows, `9 xref rows`, `2369 instruction rows`, and `7 decompile rows` |
| Dry run | `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 tags_added=100 missing=0 bad=0` |
| Apply | `updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 tags_added=100 missing=0 bad=0`; `REPORT: Save succeeded` |
| Final dry | `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0` |
| Backup | `G:\GhidraBackups\BEA_20260606-175052_post_wave1191_cpdsimplesprite_render_residual_current_risk_review_verified` |

No rename, no signature change, no function-boundary change, and no executable-byte change occurred. Codex read-only consults used; no Cursor/Composer.

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt. Expanded static surface remains `1560/1560 = 100.00%`. Wave1108 current focused accounting is now `826/1179 = 70.06%`; current risk candidates: 6166; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 353; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference. Exact CPDSimpleSprite/descriptor/particle/CVBufTexture/DXParticleTexture/global-atlas layouts, runtime particle ordering/culling/rendering behavior, visual parity, exact source-body identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Probe token anchor: Wave1191; wave1191-cpdsimplesprite-render-residual-current-risk-review; 826/1179 = 70.06%; 7 CPDSimpleSprite render residual current-risk rows; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 353; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=7 skipped=0; comment_only_updated=7; tags_added=100; final dry updated=0 skipped=7; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; CPDSimpleSprite__SetUVFromTileIndex; CPDSimpleSprite__CopyTransformMatrix; CPDSimpleSprite__BuildUvAtlasBuckets; CPDSimpleSprite__ProcessAndRenderSpriteList; CPDSimpleSprite__ScaleVec3InPlace; CPDSimpleSprite__ReciprocalVec3Magnitude; CPDSimpleSprite__EvaluateCurveDrivenScale; CVBufTexture__GetVertexPtrAt; DXParticleTexture__GetIndexBuffer; DAT_00829e58; DAT_0082b39c; 0 / 0 / 0; 6411/6411 = 100.00%; 9 xref rows; 2369 instruction rows; 7 decompile rows; G:\GhidraBackups\BEA_20260606-175052_post_wave1191_cpdsimplesprite_render_residual_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.
