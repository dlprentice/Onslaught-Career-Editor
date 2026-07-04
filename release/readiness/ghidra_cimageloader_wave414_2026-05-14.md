# Ghidra CImageLoader / CIBuffer Direct-Lock Wave414

Status: public-safe static RE evidence
Date: 2026-05-14

This note records a serialized headless Ghidra dry/apply/read-back pass for the CImageLoader vtable and an adjacent CIBuffer direct-lock helper. It is public-safe: it contains addresses, saved names/signatures, command summaries, counts, and claim boundaries, but not raw decompile excerpts, private paths, screenshots, frames, copied executables, saves, or private runtime proof.

## Saved Ghidra Corrections

| Address | Saved name | Saved signature | Result |
| --- | --- | --- | --- |
| `0x004885e0` | `CIBuffer__LockDirect` | `int __thiscall CIBuffer__LockDirect(void * this, void * * out_data)` | Corrected stale `CVBufTexture__SetTextureStageFilterByFlag200` owner label to direct CIBuffer D3D index-buffer lock behavior. |
| `0x00488620` | `CImageLoader__Constructor` | `void * __thiscall CImageLoader__Constructor(void * this, char * filename)` | Hardened constructor signature/comment. |
| `0x00488670` | `CImageLoader__GetFilenamePtr` | `char * __thiscall CImageLoader__GetFilenamePtr(void * this)` | Created missing vtable-slot function boundary. |
| `0x00488680` | `CImageLoader__GetWidth` | `int __thiscall CImageLoader__GetWidth(void * this)` | Created missing vtable-slot function boundary. |
| `0x00488690` | `CImageLoader__GetHeight` | `int __thiscall CImageLoader__GetHeight(void * this)` | Created missing vtable-slot function boundary. |
| `0x004886a0` | `CImageLoader__ScalarDeletingDestructor` | `void * __thiscall CImageLoader__ScalarDeletingDestructor(void * this, byte flags)` | Hardened scalar-deleting destructor signature/comment. |
| `0x00488700` | `CImageLoader__Destructor` | `void __thiscall CImageLoader__Destructor(void * this)` | Hardened destructor signature/comment. |
| `0x00488740` | `CImageLoader__FreeWidthBuffer` | `void __thiscall CImageLoader__FreeWidthBuffer(void * this)` | Hardened width-buffer free signature/comment. |
| `0x00488760` | `CImageLoader__FreeHeightBuffer` | `void __thiscall CImageLoader__FreeHeightBuffer(void * this)` | Hardened height-buffer free signature/comment. |
| `0x00488780` | `CImageLoader__LoadWidthBuffer` | `bool __thiscall CImageLoader__LoadWidthBuffer(void * this, void * alloc_context)` | Hardened width-buffer allocation signature/comment. |
| `0x004887c0` | `CImageLoader__LoadHeightBuffer` | `bool __thiscall CImageLoader__LoadHeightBuffer(void * this, void * alloc_context)` | Hardened height-buffer allocation signature/comment. |
| `0x0052f540` | `SharedVFunc__ReturnField04_0052f540` | `void * __thiscall SharedVFunc__ReturnField04_0052f540(void * this)` | Created missing shared vtable getter boundary. |
| `0x004de070` | `SharedVFunc__ReturnField14_004de070` | `void * __thiscall SharedVFunc__ReturnField14_004de070(void * this)` | Created missing shared vtable getter boundary. |

## Evidence Summary

- The available Stuart source snapshot does not include the `imageloader.cpp`, `ibuffer.cpp`, or `vbuftexture.cpp` bodies, so this tranche is retail-static/debug-path evidence rather than exact source-body confirmation.
- The `0x004885e0` helper is now bounded as `CIBuffer__LockDirect`: callers pass a CIBuffer receiver from CVBufTexture index-buffer and CDXLandscape contexts, test the returned HRESULT, and the body locks the D3D index-buffer pointer at observed offset `+0x08` using flags chosen from observed usage field `+0x10`.
- The current ImageLoader vtable at `0x005dbedc` resolves slots `0`, `2`, `3`, `4`, `5`, `7`, and `9` through `12` to named functions. Slots `13` and `14` are not ImageLoader function evidence under the current read-back.
- The Wave414 function-count increase is expected: five real vtable targets that were previously raw addresses are now Ghidra function objects.
- Refreshed whole-project queue telemetry reports `6035` total functions, `1602` commented functions, `4433` commentless functions, `1893` undefined signatures, and `1838` `param_N` signatures. Current confirmation proxies are comment-backed `1602/6035 = 26.55%` and strict clean-signature `1539/6035 = 25.50%`; both are telemetry only, not milestones.

## Validation

- Expected red focused test before implementation: `py -3 tools\ghidra_cimageloader_wave414_probe_test.py` failed with `ModuleNotFoundError`.
- Focused tests: `py -3 tools\ghidra_cimageloader_wave414_probe_test.py` passed `2/2`.
- Python compile: `py -3 -m py_compile tools\ghidra_cimageloader_wave414_probe.py tools\ghidra_cimageloader_wave414_probe_test.py` passed.
- Headless dry run: `ApplyCImageLoaderWave414.java dry` reported `updated=0 skipped=8 created=0 would_create=5 renamed=0 would_rename=1 missing=0 bad=0` with `REPORT: Save succeeded`.
- Headless apply run: `ApplyCImageLoaderWave414.java apply` reported `updated=13 skipped=0 created=5 would_create=0 renamed=1 would_rename=0 missing=0 bad=0` with `REPORT: Save succeeded`.
- Read-back exports verified `13` metadata rows, `13` tag rows, ImageLoader vtable rows, xrefs, `13` decompile exports, and target instruction evidence.
- Package wrapper: `cmd.exe /c npm run test:ghidra-cimageloader-wave414` passed with focused probe status `PASS`.
- Queue refresh: headless `ExportFunctionQualitySnapshot.java` and `cmd.exe /c npm run test:ghidra-static-reaudit-queue` passed with the `6035`-function telemetry above.
- Actual Ghidra project backup: copied `BEA.gpr` and `BEA.rep` to `[maintainer-local-ghidra-backup-root]\BEA_20260514_113511_post_wave414_cimageloader_verified` and verified `19` files, `154897287` bytes, and `HashDiffCount=0`.

## Not Proven

This tranche does not prove runtime image loading, runtime rendering behavior, exact source-body identity, complete CImageLoader/CIBuffer/CTGALoader/CRTMesh layouts, local variable/type recovery, BEA launch behavior, game patching, packaged app behavior, or rebuild parity.
