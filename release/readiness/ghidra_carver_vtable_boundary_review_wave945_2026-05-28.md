# Ghidra Carver Vtable Boundary Review Wave945

Status: complete static read-back evidence
Date: 2026-05-28
Scope: `carver-vtable-boundary-wave945`

Wave945 re-reviewed the CCarver init/combat/wing cluster and recovered three CCarver-local vtable-backed function boundaries that were still `NO_FUNCTION_AT_POINTER` entries in the CCarver vtable export. The pass created function objects, names, signatures, comments, and tags for slots 35, 63, and 104. It made no executable-byte changes and did not launch BEA.

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x00422750 CCarver__Thunk_CallGuideVFunc08` | `void __fastcall CCarver__Thunk_CallGuideVFunc08(void * this)` | CCarver vtable `0x005e0d90` slot 63; three-instruction thunk loads the guide/controller pointer from `this+0x208` and tail-jumps through that object's vtable byte offset `+0x20` (slot 8). |
| `0x004228b0 CCarver__VFunc35_RenderWithFadeGlobal` | `void __thiscall CCarver__VFunc35_RenderWithFadeGlobal(void * this, uint render_flags)` | CCarver vtable slot 35; compares `this+0x280` against constant `0x005d856c`, wraps `CThing__Render(this, render_flags | 0x40)` with global `0x0063012c`, then restores it to `0xff`; `RET 0x4`. |
| `0x00422910 CCarver__VFunc104_IsWingBlendAboveThreshold` | `int __fastcall CCarver__VFunc104_IsWingBlendAboveThreshold(void * this)` | CCarver vtable slot 104; compact predicate compares `this+0x280` against `0x005d856c` and returns `1` on the above-threshold path or `0` otherwise. |

Read-back evidence:

- Composer 2.5 consult agreed all three entries were CCarver vtable-backed local code bodies; it recommended the slot-104 polarity name used here.
- `ApplyCarverVtableBoundaryWave945.java dry`: `updated=0 skipped=0 created=0 would_create=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- `ApplyCarverVtableBoundaryWave945.java apply`: `updated=3 skipped=0 created=3 would_create=0 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=0 missing=0 bad=0`.
- `ApplyCarverVtableBoundaryWave945.java final dry`: `updated=0 skipped=3 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports: 3 metadata rows, 3 tag rows, 4 xref rows, 33 instruction rows, 3 decompile rows, and 128 post vtable rows.
- Queue after Wave945: `6116` total functions, `6116` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N`; export-contract function-quality closure remains `6116/6116 = 100.00%`.
- Wave911 focused re-audit progress after Wave945: `206/1408 = 14.63%`.
- Verified backup: `G:\GhidraBackups\BEA_20260528-054358_post_wave945_carver_vtable_boundary_review_verified`, 19 files, 173312903 bytes, `DiffCount=0`.

What this proves:

- The three target function objects exist in the saved Ghidra project at the intended entries.
- The saved names, signatures, comments, and tags were read back after apply.
- The CCarver vtable no longer reports `NO_FUNCTION_AT_POINTER` for slots 35, 63, and 104.

What remains unproven:

- Exact source virtual names.
- Exact CCarver/guide/layout field names.
- Runtime wing, guide, render, attack, or predicate behavior.
- BEA patching behavior.
- Rebuild parity.
