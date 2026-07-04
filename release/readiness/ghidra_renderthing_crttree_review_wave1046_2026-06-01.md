# Ghidra RenderThing / CRTTree Review Wave1046

Status: complete static read-only evidence
Date: 2026-06-01
Scope: `renderthing-crttree-review-wave1046`

Wave1046 re-read eight `CRenderThing` / `CRTTree` render-object lifecycle/helper rows originally recovered by Wave489 and Wave497. Fresh metadata, tag, xref, instruction, decompile, vtable-slot, and context exports agree with the saved names, signatures, comments, and tags. No Ghidra mutation, rename, signature change, comment change, tag change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation was needed.

Reviewed rows:

| Address | Saved row | Evidence |
| --- | --- | --- |
| `0x004db880` | `CRenderThing__ForwardSlot26ToChildSlot68` | Vtable DATA refs from `0x005dea28`, `0x005deaa0`, `0x005deb14`, `0x005deb84`, and `0x005dec04`; forwards through the child pointer at `this+0x10` to child vtable slot `+0x68`. |
| `0x004dbb80` | `CRenderThing__VFunc_07_ClearRenderOutputs` | Vtable DATA refs from `0x005dea54`, `0x005deac8`, and `0x005debb8`; clears output dwords and copies the `0x0083ccd8` 0x30-byte matrix/global block. |
| `0x004dbbe0` | `CRenderThing__VFunc_08_ClearVec3` | Vtable DATA refs from `0x005dea58`, `0x005deacc`, and `0x005debbc`; clears the caller-provided three-dword vector output. |
| `0x004dbd20` | `CRenderThing__dtor` | Called by unwind rows `0x005d4a30`, `0x005d4a80`, and `0x005d4aa0`; remains destructor evidence, not constructor evidence. |
| `0x004dbd50` | `CRenderThing__scalar_deleting_dtor` | CRenderThing vtable DATA ref `0x005deaac`; destroys the child pointer and optionally calls `CDXMemoryManager__Free(&DAT_009c3df0, this)`. |
| `0x004dd960` | `CRTTree__VFuncSlot02_BuildRenderOutputs` | CRTTree vtable DATA ref `0x005deba4`; uses camera/context transforms, `DAT_0083cd58`, `CDXEngine__SetWorldMatrixElements`, `Vec3__AssignXYZ`, `MathMatrix3x4__AssignFromEightScalars`, and `CSphere__RenderAnimatedRecursive`. |
| `0x004de050` | `CRTTree__VFuncSlot06_GetResourceScalar164` | CRTTree vtable DATA ref `0x005debb4`; returns the float at `*(this+0x14)+0x164`. |
| `0x004de060` | `SharedVFunc__ReturnResourceField150_004de060` | Shared CRTMesh/CRTTree vtable DATA refs `0x005deb2c` and `0x005debac`; returns `*(this+0x14)+0x150`. |

Read-back evidence:

- Primary exports verified `8` metadata rows, `8` tag rows, `19` xref rows, `429` function-body instruction rows, `8` decompile rows, and `144` vtable-slot rows.
- Context exports verified `20` metadata rows, `20` tag rows, `1087` xref rows, `1090` function-body instruction rows, and `20` decompile rows.
- Reviewed vtables include `0x005dea38` RTCutscene, `0x005deaac` CRenderThing, `0x005deb1c` CRTMesh, and `0x005deb9c` CRTTree.
- Queue closure remains `6246/6246 = 100.00%`, with `0` commentless rows, `0` exact-undefined signatures, and `0` `param_N` signatures.
- Wave1046 targets are outside the Wave911 focused TSV, so Wave911 focused progress remains `735/1408 = 52.20%`; expanded static surface progress advances to `993/1509 = 65.81%`; top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-120449_post_wave1046_renderthing_crttree_review_verified`, 19 files, 174590855 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The eight reviewed rows still exist as saved Ghidra function objects in the loaded database.
- The saved names, signatures, comments, and tags read back coherently with fresh xref, vtable, instruction, and decompile evidence.
- The old Wave489/Wave497 render-object decisions remain static-coherent; no stale constructor/helper owner wording was reintroduced.

What remains separate proof:

- Runtime cutscene, tree, vegetation, falling-tree, or render-output behavior.
- Exact `CRenderThing`, `CRTCutscene`, `CRTTree`, `CRTMesh`, tree-resource, and output-record layouts.
- Exact source virtual names and exact source-body identity.
- `CSphere__RenderAnimatedRecursive` signature/layout review.
- BEA patching behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1046; renderthing-crttree-review-wave1046; 0x004db880 CRenderThing__ForwardSlot26ToChildSlot68; 0x004dbb80 CRenderThing__VFunc_07_ClearRenderOutputs; 0x004dbbe0 CRenderThing__VFunc_08_ClearVec3; 0x004dbd20 CRenderThing__dtor; 0x004dbd50 CRenderThing__scalar_deleting_dtor; 0x004dd960 CRTTree__VFuncSlot02_BuildRenderOutputs; 0x004de050 CRTTree__VFuncSlot06_GetResourceScalar164; 0x004de060 SharedVFunc__ReturnResourceField150_004de060; 0x005dea38; 0x005deaac; 0x005deb1c; 0x005deb9c; DAT_0083cd58; 0x0083ccd8; 0x004b6260 CSphere__RenderAnimatedRecursive; 735/1408 = 52.20%; 993/1509 = 65.81%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-120449_post_wave1046_renderthing_crttree_review_verified; no mutation.
