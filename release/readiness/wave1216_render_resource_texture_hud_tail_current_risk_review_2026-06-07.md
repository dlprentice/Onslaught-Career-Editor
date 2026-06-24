# Wave1216 Render Resource Texture HUD Tail Current-Risk Review Readiness Note

Wave1216 measured anchor: unique-address accounting governs active current-risk progress. Probe token anchor: Wave1216; wave1216-render-resource-texture-hud-tail-current-risk-review; 1145/1179 = 97.12%; 7 render/resource/texture/HUD tail current-risk rows; CThing__InitRenderThingFromInitMeshName; CPDMesh__dtor_base; CWaterRenderSystem__ResetAndMarkSourceFlag; CAtmosphericsProfile__ResetAndInitSnowResources; CHudComponent__RenderPassEntry; CTexture__NodeType11_Ctor_WithDescriptorCopy; CTexture__NodeType12_Ctor_WithStackScalars; CTexture__NodeType11_Dtor_DeleteOnFlag_Body; CTexture__NodeType11_Dtor_DeleteOnFlag; 6411/6411 = 100.00%; 0 / 0 / 0; 12 xref rows; 962 instruction rows; 7 decompile rows; 28 context xref rows; 1015 context instruction rows; 9 context decompile rows; 6 texture-context xref rows; 111 texture-context instruction rows; 6 texture-context decompile rows; 13 data-xref rows; current focused candidates: 1127; live regenerated current focused candidates: 1127; remaining active focused work: 34; current risk candidates: 6166; fresh Ghidra export; texture label correction; 4 renamed; 4 comments updated; 25 tags added; no signature change; no function-boundary change; no executable-byte change; unique-address accounting; Codex read-only consults used; no Cursor/Composer; legacy additive counter is deprecated (`1176/1179`); 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; Wave911 is historical-retired/non-reconstructable at 812/1408 = 57.67%; 1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence; static-reaudit-current-risk-ledger.json; static-reaudit-measurement-register.md; mesh-resource-render-static-contract.md; texture-resource-decode-static-contract.md; continuity denominator; G:\GhidraBackups\BEA_20260607-101007_post_wave1216_render_resource_texture_hud_tail_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.

Status: complete static current-risk texture label correction; validation passed; artifact/state commits pushed
Date: 2026-06-07
Scope: `wave1216-render-resource-texture-hud-tail-current-risk-review`

Wave1216 re-read `7 render/resource/texture/HUD tail current-risk rows` with fresh Ghidra export evidence and corrected four stale texture node labels. The pass renamed `CTexture__NodeType11_Ctor_WithDescriptorCopy`, `CTexture__NodeType11_Dtor_DeleteOnFlag_Body`, `CTexture__NodeType11_Dtor_DeleteOnFlag`, and `CTexture__NodeType12_Ctor_WithStackScalars`; updated four comments; added 25 tags; and made no signature change, no function-boundary change, and no executable-byte change.

Evidence:

- Fresh Ghidra export: `12 xref rows`, `962 instruction rows`, and `7 decompile rows`.
- Context export: `28 context xref rows`, `1015 context instruction rows`, and `9 context decompile rows`.
- Texture context export: `6 texture-context xref rows`, `111 texture-context instruction rows`, and `6 texture-context decompile rows`.
- Data evidence: `13 data-xref rows` tying the corrected texture rows to node vtables and the water reset row to `DAT_00854dd8`.
- Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`.
- Active current-risk progress uses unique-address accounting and is `1145/1179 = 97.12%`; remaining active focused work: 34.
- legacy additive counter is deprecated (`1176/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5.
- current risk candidates: 6166; current focused candidates: 1127; live regenerated current focused candidates: 1127.
- Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; this is not Wave911 reconstruction.
- current-risk denominator, continuity denominator, focused threshold `15`, and `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence` remain the active measured lane.
- Codex read-only consults used; no Cursor/Composer.
- Verified backup: `G:\GhidraBackups\BEA_20260607-101007_post_wave1216_render_resource_texture_hud_tail_current_risk_review_verified`.

Mutation status: texture label correction only; `4 renamed`, `4 comments updated`, `25 tags added`, no signature change, no function-boundary change, and no executable-byte change.

Accounting paths: `static-reaudit-current-risk-ledger.json`, `static-reaudit-measurement-register.md`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, `mesh-resource-render-static-contract.md`, `texture-resource-decode-static-contract.md`, and `wave1108-current-risk-rank`.

Boundary: this is static Ghidra evidence for rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Runtime render behavior, runtime texture behavior, runtime HUD behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.
