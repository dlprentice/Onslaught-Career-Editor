# Ghidra DXCompass Signature Correction - 2026-05-12

Status: public-safe static reverse-engineering evidence.

## Scope

Wave 323 revisited the DXCompass HUD/render/resource helper cluster and one broad allocator wrapper after fresh metadata, decompile, xref, instruction, and callsite review. This wave saved eight Ghidra signatures/comments with no renames and no new function boundaries.

The live Ghidra project was backed up before continuing this work to `[maintainer-local-ghidra-backup-root]\BEA_20260511_234324_user_safety_verified`. The backup verification reported `19` files, `151456647` bytes, and `DiffCount=0`.

## Saved Corrections

| Address | Saved signature |
| --- | --- |
| `0x00426fd0` | `void * __cdecl OID__AllocObject_DefaultTag_00662b2c(int sizeBytes)` |
| `0x004270e0` | `void __fastcall CDXCompass__InitMarkerArrays(void * this)` |
| `0x00427110` | `void __fastcall CDXCompass__LoadTextures(void * this)` |
| `0x00427190` | `void __fastcall CDXCompass__DestroyTextures(void * this)` |
| `0x00427200` | `void __fastcall CDXCompass__Reset(void * this)` |
| `0x00427210` | `void __thiscall CDXCompass__Render(void * this, void * battleEngineContext)` |
| `0x0053be40` | `void __fastcall CDXCompass__Init(void * this)` |
| `0x0053c1d0` | `void __cdecl CDXCompass__BuildRingGeometry(void * vertices, int textureWidth, int textureHeight, int segmentCount, int thicknessPercent, float uvScale)` |

`0x00426fd0` remains a broad allocation wrapper with xrefs across rendering, texture, mesh, and parser helpers. It is not DXCompass-specific ownership proof.

## Validation

| Check | Result |
| --- | --- |
| `ApplyDXCompassSignatureCorrection.java dry` | `updated=0 skipped=8 renamed=0 missing=0 bad=0`; `REPORT: Save succeeded` |
| `ApplyDXCompassSignatureCorrection.java apply` | `updated=8 skipped=0 renamed=0 missing=0 bad=0`; `REPORT: Save succeeded` |
| Metadata read-back | `10/10` targets, including the eight wave targets and two existing tracked-position getters |
| Decompile read-back | `10/10` targets |
| Xref read-back | `218` xref rows |
| Instruction read-back | `10` targets, `0` missing |
| Quality queue | `5884` total functions, `751` commented, `5133` commentless, `1997` undefined signatures, `2306` `param_N` signatures |
| Focused probe | `PASS`, schema `ghidra-dxcompass-signature-correction.v1` |

## What This Proves

- The saved Ghidra project now has hardened signatures and comments for eight DXCompass-adjacent render/resource helpers.
- `CDXCompass__Render` is modeled as `__thiscall` with the compass object in `ECX` and a battle-engine/render-context stack argument.
- `CDXCompass__BuildRingGeometry` is modeled as a plain `__cdecl` helper taking locked vertices and ring geometry parameters, not as a class method.

## What This Does Not Prove

- Runtime HUD rendering behavior or visual parity.
- Exact source-body identity, because `DXCompass.cpp` is not present in the available Stuart source snapshot.
- Concrete object layouts, tags, local variable names, structure types, or rebuild parity.
- Any mutation or execution of `BEA.exe`.

## Public/Private Boundary

This note includes only repo-relative paths, public addresses, saved names/signatures, aggregate counts, and public-safe summaries. Raw decompile exports, instruction dumps, private project backups, and generated probe JSON remain outside public release scope.
