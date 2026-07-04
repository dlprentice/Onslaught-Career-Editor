# Ghidra Wave900+ Through Wave1028 Recheck

Status: complete structural static evidence recheck
Date: 2026-06-01
Scope: `wave900-plus-through-wave1028-recheck`

This note extends the Wave900+ static re-audit recheck through Wave1028. It validates the Wave1028 focused probe/readiness/evidence/backup extension plus the prior Wave900-Wave1027 gate and current live queue closure at `6238/6238 = 100.00%`.

Validation command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1028-recheck
```

Expected coverage:

- Wave900-Wave981 remain covered by the prior focused-probe sweep and evidence audit.
- Wave982-Wave1028 focused probes are rerun directly by `tools/ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1028 --check`.
- Wave910 and Wave911 remain queue/planning records without per-wave backup notes.
- Current queue closure remains `6238/6238 = 100.00%`, with 0 commentless, 0 exact-undefined signatures, and 0 `param_N`.
- Wave1028 readiness/evidence anchor: `cdx-render-resource-lifecycle-review-wave1028`, `0x0054bff0 CDXMeshVB__scalar_deleting_dtor`, `0x0054c010 CDXMeshVB__dtor_base`, `0x00547d70 CDXMemBuffer__ctor`, `0x004f2790 CDXSurf__UnlinkNodeFromGlobalList`, `0x00527de0 CWaterRenderSystem__ResetAndMarkSourceFlag`, `605/1408 = 42.97%`, `834/1493 = 55.86%`, `500/500 = 100.00%`, `[maintainer-local-ghidra-backup-root]\BEA_20260601-021726_post_wave1028_cdx_render_resource_lifecycle_review_verified`, no mutation.

This is structural static evidence validation only. It does not prove runtime D3D/render-resource lifetime behavior, visible render output, exact source-layout identity, BEA patch behavior, gameplay outcomes, or rebuild parity.
