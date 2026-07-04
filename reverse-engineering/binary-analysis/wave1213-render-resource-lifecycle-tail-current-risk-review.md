# Wave1213 Render Resource Lifecycle Tail Current-Risk Review

Status: complete static current-risk read-only review; later validation passed by current-risk closeout gates
Date: 2026-06-07
Tag: `wave1213-render-resource-lifecycle-tail-current-risk-review`

Wave1213 re-read `6 render-resource lifecycle tail current-risk rows` from the `wave1108-current-risk-rank` continuity denominator with fresh Ghidra export evidence. This is a read-only review with no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt. Active current-risk progress is `1125/1179 = 95.42%`; remaining active focused work: 54. The legacy additive counter is deprecated (`1156/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1127; live regenerated current focused candidates: 1127; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction.

## Targets

| Address | Function | Static evidence |
| --- | --- | --- |
| `0x00488330` | `CIBuffer__CreateConfigured` | CALL xrefs `0x00500887` from `CVBufTexture__ResizeIndexBuffer` and `0x00544c52` from `CDXLandscape__Init`; stores size/usage/index-format/buffer-type at `+0x0c/+0x10/+0x14/+0x18`, dispatches dynamic/static vtable slots, and returns with `RET 0x10`. |
| `0x004885e0` | `CIBuffer__LockDirect` | CALL xrefs from `CVBufTexture__ResizeIndexBuffer`, `CVBufTexture__AddIndices`, `CVBufTexture__GetIndexPtr`, and `CDXLandscape__UpdateLOD`; locks the D3D index-buffer pointer at `+0x08` and selects `0x2800` or `0x800` lock flags from usage bit `0x200`. |
| `0x004f2790` | `CDXSurf__UnlinkNodeFromGlobalList` | CALL xrefs from `CDXSurf__dtor` and two unwind rows; walks `DAT_0083d9b0` through `node+0xa0`, compares against `texture_base-0x08` or null, and unlinks the matching global texture/surface node. |
| `0x0053a140` | `CDXBattleLine__DestructorThunk` | CALL xref `0x0053a123` from `CDXBattleLine__scalar_deleting_dtor`; instruction export is a one-instruction `JMP 0x00556d90` thunk to `CDXSurf__dtor`. The decompiler follows the thunk and shows the base destructor body, so the thunk boundary remains intentional. |
| `0x00544a60` | `CDXLandscape__Destructor` | CALL xref `0x00544a43` from `CDXLandscape__ScalarDeletingDestructor`; reinstalls vtable `0x005e50d0`, unlinks render-object lists, releases shader/interface/device-object state, and releases the mixer-detail texture reference. |
| `0x00544eb0` | `CDXLandscape__ReleaseBuffers` | DATA xref `0x005e50e0` vtable slot `+0x10`; releases and clears resource pointers at `+0x08/+0x10/+0x0c/+0x14`, releases interface pointer `+0x1c`, and returns `0`. |

Context exports covered `CIBuffer__Constructor`, `CIBuffer__Destructor`, `CIBuffer__Create`, `CIBuffer__Lock`, `CVBufTexture__ResizeIndexBuffer`, `CVBufTexture__AddIndices`, `CVBufTexture__GetIndexPtr`, `CDXSurf__dtor`, `CDXBattleLine__scalar_deleting_dtor`, `CDXBattleLine__LoadTextures`, `CDXLandscape__Constructor`, `CDXLandscape__ScalarDeletingDestructor`, `CDXLandscape__Init`, `CDXLandscape__Shutdown`, and `CDXLandscape__UpdateLOD`.

Fresh Ghidra export counts: `6` metadata rows, `6` tag rows, `13 xref rows`, `152 instruction rows`, and `6 decompile rows`. Context export counts: `15` metadata rows, `15` tag rows, `41 context xref rows`, `1369 context instruction rows`, and `15 context decompile rows`.

Codex read-only consults used; no Cursor/Composer. The central accounting paths are `static-reaudit-current-risk-ledger.json`, `static-reaudit-measurement-register.md`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, `mesh-resource-render-static-contract.md`, and `wave1108-current-risk-rank`.

Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-074242_post_wave1213_render_resource_lifecycle_tail_current_risk_review_verified` (`19` files, `176425863` bytes, `DiffCount=0`, `HashDiffCount=0`).

Boundary: this wave strengthens rebuild-grade static contracts and the rebuild-grade specification aiming at no noticeable difference for index-buffer creation/locking, global texture/surface-list unlink, battleline base-destruction thunking, and landscape resource teardown. Runtime Direct3D behavior, runtime terrain/HUD output, runtime lost-device behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.
