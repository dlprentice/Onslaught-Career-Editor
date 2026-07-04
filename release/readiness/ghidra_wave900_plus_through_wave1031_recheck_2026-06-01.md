# Ghidra Wave900+ Through Wave1031 Recheck

Status: validation passed; later static closeout supersession verified by Wave1220
Date: 2026-06-01
Scope: `wave900-plus-through-wave1031-recheck`

This note extends the Wave900+ static re-audit recheck through Wave1031. It validates the Wave1031 focused probe/readiness/evidence/backup extension plus the prior Wave900-Wave1030 gate and current live queue closure at `6238/6238 = 100.00%`.

Command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1031-recheck
```

Coverage anchors:

- Wave900-Wave981 remain covered by the earlier focused-probe sweep and evidence audit.
- Wave982-Wave1031 focused probes are rerun directly by `tools/ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1031 --check`.
- Wave910 and Wave911 remain queue/planning records rather than saved mutation/review records with per-wave backup notes.
- Wave1031 readiness/evidence anchor: `particle-cpdsimplesprite-runtime-transform-review-wave1031`, `0x004f5b70 CTokenArchive__BindIndexedFieldPointer`, `0x004c0150 CParticle__ApplyParentTransformOrStoreLink`, `0x004c0940 CPDSimpleSprite__SetUVFromTileIndex`, `0x004c5280 CPDSimpleSprite__CopyTransformMatrix`, `0x004c5410 CParticleDescriptor__Update`, `0x004f5b80 CTokenArchive__RegisterReferenceFixup`, `626/1408 = 44.46%`, `855/1493 = 57.27%`, `500/500 = 100.00%`, `[maintainer-local-ghidra-backup-root]\BEA_20260601-040508_post_wave1031_particle_cpdsimplesprite_runtime_transform_review_verified`, one rename/signature/comment correction.

Boundary:

- This recheck validates static evidence structure, backups, apply logs, focused probe classifications, and current queue closure.
- It does not prove runtime behavior, exact source-layout identity, gameplay outcomes, BEA patching, or rebuild parity.

Probe token anchor: Wave1031; wave900-plus-through-wave1031-recheck; particle-cpdsimplesprite-runtime-transform-review-wave1031; 0x004f5b70 CTokenArchive__BindIndexedFieldPointer; 626/1408 = 44.46%; 855/1493 = 57.27%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-040508_post_wave1031_particle_cpdsimplesprite_runtime_transform_review_verified.
