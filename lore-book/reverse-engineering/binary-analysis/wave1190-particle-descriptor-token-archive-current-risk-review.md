# Wave1190 Particle Descriptor / TokenArchive Current-Risk Review

Status: complete static read-back evidence pending artifact commit
Date: 2026-06-06
Tag: `wave1190-particle-descriptor-token-archive-current-risk-review`

Wave1190 accounts for `11 particle descriptor token-writer/TokenArchive current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator. This is a static serialization-contract review for the particle descriptor token-writer spine and `CTokenArchive__BindIndexedFieldPointer`; it is meant to make the clean-room rebuild specification more concrete, not to claim runtime particle parity.

Targets:

| Address | Function | Static contract |
| --- | --- | --- |
| `0x004c07f0` | `CPDSimpleSprite__WriteTokenFields` | Slot-7 writer emits tokens 6 through 0x1b through `CTokenArchive__Write*`; vtable DATA xref `0x005ddf7c`. |
| `0x004c1970` | `CPDEmitter__WriteTokenFields` | Slot-7 writer emits tokens 0x1a through 0x28; vtable DATA xref `0x005ddf14`. |
| `0x004c2220` | `CPDSelector__WriteTokenFields` | Slot-7 writer emits tokens 0x29 through 0x30; vtable DATA xref `0x005dde44`. |
| `0x004c2400` | `CPDColourRange__WriteTokenFields` | Slot-7 writer emits tokens 0x31 through 0x3c; vtable DATA xref `0x005ddddc`. |
| `0x004c2ca0` | `CPDShape__WriteTokenFields` | Slot-7 writer emits tokens 0x3f through 0x46 plus token 6; vtable DATA xref `0x005ddd0c`. |
| `0x004c3440` | `CPDTrail__WriteTokenFields` | Slot-7 writer emits tokens 0x47 through 0x54; vtable DATA xref `0x005ddca4`. |
| `0x004c4920` | `CPDFunction__WriteTokenFields` | Slot-7 writer emits tokens 0x5c through 0x64; vtable DATA xref `0x005ddbd4`. |
| `0x004c4c70` | `CPDMesh__WriteTokenFields` | Slot-7 writer emits tokens 0x65 through 0x68; vtable DATA xref `0x005ddb58`. |
| `0x004c53b0` | `CPDFoR__WriteTokenFields` | Slot-7 writer emits tokens 0x69, 0x6a, and 0x28; vtable DATA xref `0x005ddfe4`. |
| `0x004c59e0` | `CPDPMesh__WriteTokenFields` | Slot-7 writer emits tokens 0x6b through 0x7b; vtable DATA xref `0x005de04c`. |
| `0x004f5b70` | `CTokenArchive__BindIndexedFieldPointer` | Stores `field_ptr` at `this+0x0c+(slot_index*4)` and returns with `RET 0x8`; `CParticleDescriptor__Load` and adjacent token-load callsites feed field pointers into it. |

Read-back evidence:

| Item | Result |
| --- | --- |
| Pre/post rows | `11` metadata rows, `11` tag rows, `25 xref rows`, `733 instruction rows`, and `11 decompile rows` |
| Dry run | `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=11 tags_added=123 missing=0 bad=0` |
| Apply | `updated=11 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=11 tags_added=123 missing=0 bad=0`; `REPORT: Save succeeded` |
| Final dry | `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0` |
| Backup | `[maintainer-local-ghidra-backup-root]\BEA_20260606-173000_post_wave1190_particle_descriptor_token_archive_current_risk_review_verified` |

No rename, no signature change, no function-boundary change, and no executable-byte change occurred. Codex read-only consults used; no Cursor/Composer.

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt. Expanded static surface remains `1560/1560 = 100.00%`. Wave1108 current focused accounting is now `819/1179 = 69.47%`; current risk candidates: 6166; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 360; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference. Exact descriptor/TokenArchive layouts, exact source virtual/source-body identity, runtime particle loading/parsing/rendering/linking behavior, BEA patching behavior, gameplay/visual outcomes, rebuild parity, and no-noticeable-difference parity remain separate proof.

Probe token anchor: Wave1190; wave1190-particle-descriptor-token-archive-current-risk-review; 819/1179 = 69.47%; 11 particle descriptor token-writer/TokenArchive current-risk rows; current focused candidates: 1169; live regenerated current focused candidates: 1169; remaining active focused work: 360; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=11 skipped=0; comment_only_updated=11; tags_added=123; final dry updated=0 skipped=11; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; CPDSimpleSprite__WriteTokenFields; CPDEmitter__WriteTokenFields; CPDSelector__WriteTokenFields; CPDColourRange__WriteTokenFields; CPDShape__WriteTokenFields; CPDTrail__WriteTokenFields; CPDFunction__WriteTokenFields; CPDMesh__WriteTokenFields; CPDFoR__WriteTokenFields; CPDPMesh__WriteTokenFields; CTokenArchive__BindIndexedFieldPointer; CParticleDescriptor__Load; 0 / 0 / 0; 6411/6411 = 100.00%; 25 xref rows; 733 instruction rows; 11 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-173000_post_wave1190_particle_descriptor_token_archive_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.
