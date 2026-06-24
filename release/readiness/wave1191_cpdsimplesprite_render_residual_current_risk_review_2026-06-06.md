# Wave1191 CPDSimpleSprite Render Residual Current-Risk Review

Status: complete static read-back evidence pending artifact commit
Date: 2026-06-06
Tag: `wave1191-cpdsimplesprite-render-residual-current-risk-review`

Wave1191 accounts for `7 CPDSimpleSprite render residual current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence and saved comment/tag normalization. The rows are `CPDSimpleSprite__SetUVFromTileIndex`, `CPDSimpleSprite__CopyTransformMatrix`, `CPDSimpleSprite__BuildUvAtlasBuckets`, `CPDSimpleSprite__ProcessAndRenderSpriteList`, `CPDSimpleSprite__ScaleVec3InPlace`, `CPDSimpleSprite__ReciprocalVec3Magnitude`, and `CPDSimpleSprite__EvaluateCurveDrivenScale`.

Evidence:

| Item | Result |
| --- | --- |
| Dry run | `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 tags_added=100 missing=0 bad=0` |
| Apply | `updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 tags_added=100 missing=0 bad=0` |
| Final dry | `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0` |
| Post exports | `7` metadata rows, `7` tag rows, `9 xref rows`, `2369 instruction rows`, and `7 decompile rows` |
| Backup | `G:\GhidraBackups\BEA_20260606-175052_post_wave1191_cpdsimplesprite_render_residual_current_risk_review_verified` |

No rename, no signature change, no function-boundary change, and no executable-byte change occurred. Codex read-only consults used; no Cursor/Composer.

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt. Wave1108 current focused accounting is now `826/1179 = 70.06%`; current risk candidates: 6166; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 353; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Static rebuild anchors include `CVBufTexture__GetVertexPtrAt`, `DXParticleTexture__GetIndexBuffer`, `DAT_00829e58`, and `DAT_0082b39c`. Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference. Exact CPDSimpleSprite/descriptor/particle/CVBufTexture/DXParticleTexture/global-atlas layouts, runtime particle ordering/culling/rendering behavior, visual parity, exact source-body identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Probe token anchor: Wave1191; wave1191-cpdsimplesprite-render-residual-current-risk-review; 826/1179 = 70.06%; 7 CPDSimpleSprite render residual current-risk rows; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 353; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=7 skipped=0; comment_only_updated=7; tags_added=100; final dry updated=0 skipped=7; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; CPDSimpleSprite__SetUVFromTileIndex; CPDSimpleSprite__CopyTransformMatrix; CPDSimpleSprite__BuildUvAtlasBuckets; CPDSimpleSprite__ProcessAndRenderSpriteList; CPDSimpleSprite__ScaleVec3InPlace; CPDSimpleSprite__ReciprocalVec3Magnitude; CPDSimpleSprite__EvaluateCurveDrivenScale; CVBufTexture__GetVertexPtrAt; DXParticleTexture__GetIndexBuffer; DAT_00829e58; DAT_0082b39c; 0 / 0 / 0; 6411/6411 = 100.00%; 9 xref rows; 2369 instruction rows; 7 decompile rows; G:\GhidraBackups\BEA_20260606-175052_post_wave1191_cpdsimplesprite_render_residual_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.
