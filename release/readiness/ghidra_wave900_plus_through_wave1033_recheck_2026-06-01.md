# Ghidra Wave900+ Through Wave1033 Recheck

Status: validation passed; later static closeout supersession verified by Wave1220
Date: 2026-06-01
Scope: `wave900-plus-through-wave1033-recheck`

This note extends the Wave900+ static re-audit recheck through Wave1033. It validates the Wave1033 focused probe/readiness/evidence/backup extension plus the prior Wave900-Wave1032 gate and current live queue closure at `6238/6238 = 100.00%`.

Command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1033-recheck
```

Coverage anchors:

- Wave900-Wave981 remain covered by the earlier focused-probe sweep and evidence audit.
- Wave982-Wave1033 focused probes are rerun directly by `tools/ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1033 --check`.
- Wave910 and Wave911 remain queue/planning records rather than saved mutation/review records with per-wave backup notes.
- Wave1033 readiness/evidence anchor: `cdxengine-render-resource-review-wave1033`, `0x0044a640 CDXEngine__SetOverlaySlotVisibilityByPlayerView`, `0x0053d3a0 CDXEngine__ReleaseDefaultTextureAndMeshRefs`, `0x00542a50 CDXEngine__BuildDirectionalSampleRing`, `0x00544040 CDXEngine__ClearKempyCubeTextureSlots`, `0x00544060 CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer`, `CTexture__DecrementRefCountFromNameField`, supersedes older `CHud__DecrementCounter9C` wording, `635/1408 = 45.10%`, `864/1493 = 57.87%`, `500/500 = 100.00%`, `G:\GhidraBackups\BEA_20260601-051834_post_wave1033_cdxengine_render_resource_review_verified`, two comment/tag corrections.
- Plain probe anchor: supersedes older CHud__DecrementCounter9C wording.

Boundary:

- This recheck validates static evidence structure, backups, apply/read-only logs, focused probe classifications, and current queue closure.
- It does not prove runtime behavior, exact source-layout identity, gameplay outcomes, BEA patching, or rebuild parity.

Probe token anchor: Wave1033; wave900-plus-through-wave1033-recheck; cdxengine-render-resource-review-wave1033; 0x0053d3a0 CDXEngine__ReleaseDefaultTextureAndMeshRefs; 0x00544060 CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer; 635/1408 = 45.10%; 864/1493 = 57.87%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260601-051834_post_wave1033_cdxengine_render_resource_review_verified.
