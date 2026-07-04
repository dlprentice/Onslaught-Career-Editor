# Wave1207 D3D Render Resource Lifecycle Current-Risk Review

Status: complete static read-only review; later validation passed by current-risk closeout gates
Date: 2026-06-07
Tag: `wave1207-d3d-render-resource-lifecycle-current-risk-review`

Wave1207 measured anchor: unique-address accounting governs active current-risk progress. Wave1207 (`wave1207-d3d-render-resource-lifecycle-current-risk-review`) accounts for `6 D3D/render-resource lifecycle current-risk rows` from the `wave1108-current-risk-rank` continuity denominator with fresh Ghidra export evidence. This read-only review made no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change. Codex read-only consults used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`; active current-risk progress is `1089/1179 = 92.37%`; remaining active focused work: 90; legacy additive counter is deprecated (`1120/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1141; live regenerated current focused candidates: 1141; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `36 xref rows`, `260 instruction rows`, and `6 decompile rows`. Anchors: `CVertexShader__scalar_deleting_dtor`, `CVertexShader__VFunc_02_00501a10`, `DeviceObject__dtor_body`, `DeviceObject__scalar_deleting_dtor`, `CDXMeshVB__scalar_deleting_dtor`, and `CDXMeshVB__dtor_base`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-033229_post_wave1207_d3d_render_resource_lifecycle_current_risk_review_verified`. Active measurement files: `static-reaudit-current-risk-ledger.json`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md`, and `reverse-engineering/binary-analysis/wave1108-current-risk-rank.md`. Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`. Static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Runtime Direct3D behavior, runtime shader behavior, runtime render-resource behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

## Reviewed Rows

| Address | Function | Static evidence |
| --- | --- | --- |
| `0x00501890` | `CVertexShader__scalar_deleting_dtor` | Vtable/destructor wrapper evidence; calls `CVertexShader__dtor`, then frees via `CDXMemoryManager__Free` when the delete flag is set. |
| `0x00501a10` | `CVertexShader__VFunc_02_00501a10` | Vertex-shader vtable slot-2 path through `CEngine__SetVertexShadersEnabled`, `CEngine__DeviceCall16C_CreateVertexShaderLike`, and `CVertexShader__LoadCompiledShaderBlobFromVSOFile`; retains the `0x80004005`, `0xfffe0101`, and `DAT_00854e6c` static boundaries. |
| `0x00512d50` | `DeviceObject__dtor_body` | Base device-object cleanup body; unlinks global render/device-object list state around `DAT_00889074` and `DAT_00889078`. |
| `0x00512dc0` | `DeviceObject__scalar_deleting_dtor` | DeviceObject vtable slot-0 scalar deleting destructor wrapper; reaches the same render/device-object list cleanup and memory-manager free path. |
| `0x0054bff0` | `CDXMeshVB__scalar_deleting_dtor` | Mesh vertex-buffer scalar deleting destructor wrapper; calls `CDXMeshVB__dtor_base`, then frees when `flags&1` is set. |
| `0x0054c010` | `CDXMeshVB__dtor_base` | Calls `CDXMeshVB__ReleaseResources`, clears the name/resource field near `+0x124`, and then reaches `DeviceObject__dtor_body`. |

## Evidence Counts

- `pre-metadata.tsv`: 6 rows.
- `pre-tags.tsv`: 6 rows.
- `pre-xrefs.tsv`: 36 xref rows.
- `pre-instructions.tsv`: 260 instruction rows.
- `pre-decompile/index.tsv`: 6 decompile rows.
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-033229_post_wave1207_d3d_render_resource_lifecycle_current_risk_review_verified`, 18 files, 176425863 bytes, `DiffCount=0`, `HashDiffCount=0`.

## Accounting

- Static function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Active current-risk progress: `1089/1179 = 92.37%`.
- Remaining active focused work: 90.
- Current risk candidates: 6166.
- Current focused candidates: 1141.
- Live regenerated current focused candidates: 1141.
- Legacy additive counter is deprecated at `1120/1179`.
- Corrected duplicate-address overcount: 26 duplicate-address overcount.
- Wave1145 arithmetic overcount: 5.

## Boundary

This wave is static retail Ghidra metadata/tag/xref/instruction/decompile evidence only. It improves the D3D/render-resource lifecycle map for rebuild-grade static contracts, but runtime Direct3D behavior, runtime shader behavior, runtime render-resource behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.
