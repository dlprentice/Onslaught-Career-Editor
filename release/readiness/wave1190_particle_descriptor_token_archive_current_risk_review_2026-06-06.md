# Wave1190 Particle Descriptor / TokenArchive Current-Risk Review

Status: complete static read-back evidence pending artifact commit
Date: 2026-06-06
Tag: `wave1190-particle-descriptor-token-archive-current-risk-review`

Wave1190 accounts for `11 particle descriptor token-writer/TokenArchive current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence and saved comment/tag normalization. The rows are `CPDSimpleSprite__WriteTokenFields`, `CPDEmitter__WriteTokenFields`, `CPDSelector__WriteTokenFields`, `CPDColourRange__WriteTokenFields`, `CPDShape__WriteTokenFields`, `CPDTrail__WriteTokenFields`, `CPDFunction__WriteTokenFields`, `CPDMesh__WriteTokenFields`, `CPDFoR__WriteTokenFields`, `CPDPMesh__WriteTokenFields`, and `CTokenArchive__BindIndexedFieldPointer`; xrefs include `CParticleDescriptor__Load`.

Evidence:

| Item | Result |
| --- | --- |
| Dry run | `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=11 tags_added=123 missing=0 bad=0` |
| Apply | `updated=11 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=11 tags_added=123 missing=0 bad=0` |
| Final dry | `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0` |
| Post exports | `11` metadata rows, `11` tag rows, `25 xref rows`, `733 instruction rows`, and `11 decompile rows` |
| Backup | `[maintainer-local-ghidra-backup-root]\BEA_20260606-173000_post_wave1190_particle_descriptor_token_archive_current_risk_review_verified` |

No rename, no signature change, no function-boundary change, and no executable-byte change occurred. Codex read-only consults used; no Cursor/Composer.

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt. Wave1108 current focused accounting is now `819/1179 = 69.47%`; current risk candidates: 6166; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 360; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference. Exact descriptor/TokenArchive layouts, exact source virtual/source-body identity, runtime particle loading/parsing/rendering/linking behavior, BEA patching behavior, gameplay/visual outcomes, rebuild parity, and no-noticeable-difference parity remain separate proof.

Probe token anchor: Wave1190; wave1190-particle-descriptor-token-archive-current-risk-review; 819/1179 = 69.47%; 11 particle descriptor token-writer/TokenArchive current-risk rows; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 360; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=11 skipped=0; comment_only_updated=11; tags_added=123; final dry updated=0 skipped=11; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; CPDSimpleSprite__WriteTokenFields; CPDEmitter__WriteTokenFields; CPDSelector__WriteTokenFields; CPDColourRange__WriteTokenFields; CPDShape__WriteTokenFields; CPDTrail__WriteTokenFields; CPDFunction__WriteTokenFields; CPDMesh__WriteTokenFields; CPDFoR__WriteTokenFields; CPDPMesh__WriteTokenFields; CTokenArchive__BindIndexedFieldPointer; CParticleDescriptor__Load; 0 / 0 / 0; 6411/6411 = 100.00%; 25 xref rows; 733 instruction rows; 11 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-173000_post_wave1190_particle_descriptor_token_archive_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.
