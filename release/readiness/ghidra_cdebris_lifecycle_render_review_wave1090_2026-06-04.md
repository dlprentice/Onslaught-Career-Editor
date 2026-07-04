# Ghidra CDebris Lifecycle/Render Review Wave1090

Status: complete read-only static review
Date: 2026-06-04
Scope: `cdebris-lifecycle-render-review-wave1090`

Wave1090 re-read the seven saved `CDebris` lifecycle, metadata, render, and imposter-render rows after the post-100 re-audit selected the debris surface as a remaining expanded static-surface cluster. No mutation was needed: the saved Wave347 names, signatures, comments, and tags remain coherent with fresh metadata, tag, xref, instruction, decompile, and vtable-slot evidence.

The wave made no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Reviewed rows:

| Address | Saved row | Fresh static evidence |
| --- | --- | --- |
| `0x004411a0 CDebris__Init` | `void __thiscall CDebris__Init(void * this, void * init)` | DATA vtable xref `0x005daf34`; builds a `grs_tuft1.MSH` resource descriptor, calls `PCRTID__CreateObject(1)`, stores the render object at `this+0x30`, marks init `+0x70`, calls `CComplexThing__Init`, registers `cg_debrisarea`, `cg_debrisfadestart`, and `cg_debrisfadeend`, and links into global list `DAT_0066eb78`. |
| `0x00441320 CDebris__dtor_base` | `void __fastcall CDebris__dtor_base(void * this)` | Called from `0x00441383 CDebris__scalar_deleting_dtor`; restores vtable context, unlinks this from `DAT_0066eb78` through `this+0x7c`, then calls `CComplexThing__dtor_base`. |
| `0x00441360 CDebris__GetClassName` | `char * __cdecl CDebris__GetClassName(void)` | DATA vtable xref `0x005daf2c`; returns class-name string `CDebris` at `0x006283e0`. |
| `0x00441370 CDebris__GetClassId` | `int __cdecl CDebris__GetClassId(void)` | DATA vtable xref `0x005daf30`; returns class/OID id constant `0x1f`. |
| `0x00441380 CDebris__scalar_deleting_dtor` | `void * __thiscall CDebris__scalar_deleting_dtor(void * this, int flags)` | DATA vtable xref `0x005daf14`; calls `CDebris__dtor_base`, conditionally frees through `OID__FreeObject` when flags bit 0 is set, and returns `this`. |
| `0x004413a0 CDebris__Render` | `void __thiscall CDebris__Render(void * this, int renderFlags)` | DATA vtable xref `0x005dafa0`; checks visibility/render flags and `this+0x30`, computes fade alpha from `this+0x80` against `cg_debrisfadestart` / `cg_debrisfadeend`, writes temporary render alpha state `DAT_0063012c`, dispatches the render-object flags path, then restores alpha to `0xff`. |
| `0x00441420 CDebris__RenderImposter` | `void __fastcall CDebris__RenderImposter(void * this)` | DATA vtable xref `0x005dafa4`; checks `this+0x30` and `TF_DONT_RENDER`, computes the same fade alpha, dispatches the render-object imposter path, then restores `DAT_0063012c` to `0xff`. |

Vtable evidence:

- `0x005daf14` exported `48` vtable slots, all `OK`.
- Key `CDebris` slots are slot `0` scalar deleting destructor, slot `6` class name, slot `7` class id, slot `8` init, slot `35` render, and slot `36` render imposter.
- Inherited context slots include `CComplexThing__Shutdown`, `CThing__GetRenderPos`, `CComplexThing__GetRenderOrientation`, and `CThing__InitRenderThing`.

Evidence counts:

- Primary exports: `7` metadata rows, `7` tag rows, `7` xref rows, `202` function-body instruction rows, and `7` decompile rows.
- Context exports: `11` metadata rows, `11` tag rows, `1263` xref rows, `460` function-body instruction rows, and `11` decompile rows.
- Vtable export: `48` slot rows, all `OK`.
- Queue closure remains `6410/6410 = 100.00%`, with `0` commentless rows, `0` exact-undefined signatures, and `0` `param_N` signatures.
- Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface progress advances to `1534/1560 = 98.33%`; top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-135715_post_wave1090_cdebris_lifecycle_render_review_verified`, 19 files, 175541127 bytes, `DiffCount=0`.

What this proves:

- The saved `CDebris` function objects still exist in the loaded Ghidra database with the prior bounded Wave347 names, signatures, comments, and tags.
- The reviewed static evidence coheres across metadata, tags, xrefs, instruction bodies, decompile output, vtable slots, context helpers, and a verified project backup.
- The static `CDebris` lifecycle/render surface is materially rechecked for the post-100 audit, with no new correction needed.

What remains separate proof:

- Runtime debris rendering or imposter-render behavior.
- Concrete `CDebris` layout recovery beyond observed offsets.
- Exact source-body identity for an absent full `debris.cpp` implementation body.
- BEA patching behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1090; cdebris-lifecycle-render-review-wave1090; 0x004411a0 CDebris__Init; 0x00441320 CDebris__dtor_base; 0x004413a0 CDebris__Render; 0x00441420 CDebris__RenderImposter; 0x005daf14; grs_tuft1.MSH; DAT_0066eb78; DAT_0063012c; 1534/1560 = 98.33%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260604-135715_post_wave1090_cdebris_lifecycle_render_review_verified; no mutation.
