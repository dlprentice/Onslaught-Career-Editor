# Ghidra CDXBattleLine Core Wave589 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x0053a140` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Date: 2026-05-19
Status: static saved-Ghidra evidence only

Wave589 hardened 13 adjacent `CDXBattleLine` constructor/render rows from `0x0053a050` through `0x0053b5f0`.

Saved rows:

| Address | Function |
| --- | --- |
| `0x0053a050` | `CDXBattleLine__Constructor` |
| `0x0053a120` | `CDXBattleLine__scalar_deleting_dtor` |
| `0x0053a140` | `CDXBattleLine__DestructorThunk` |
| `0x0053a150` | `CDXBattleLine__LoadTextures` |
| `0x0053a280` | `CDXBattleLine__Setup` |
| `0x0053a390` | `CDXBattleLine__UpdateHeightmap` |
| `0x0053a5e0` | `CDXBattleLine__BuildMesh` |
| `0x0053a930` | `CDXBattleLine__InitMipLevels` |
| `0x0053aa40` | `CDXBattleLine__UpdateVertexBuffer` |
| `0x0053ab40` | `CDXBattleLine__SetupVertex` |
| `0x0053abe0` | `CDXBattleLine__Render` |
| `0x0053b470` | `CDXBattleLine__RenderTriOverlayPass` |
| `0x0053b5f0` | `CDXBattleLine__AppendOverlayVertex` |

What is proven:

- Ghidra now records clean signatures, comments, and `battleline-core-wave589` tags for all 13 rows.
- `0x0053a140` was renamed from a stale duplicate `CDXSurf__dtor` label to `CDXBattleLine__DestructorThunk`; instruction read-back proves it is a one-instruction `JMP 0x00556d90` thunk into the real `CDXSurf__dtor`.
- `CDXBattleLine__Constructor` is a `__thiscall` field-block initializer with `RET 0x8`; `CHud__Init` pushes `0xe` and `-0x7`, moves the allocated block into `ECX`, and calls `0x0053a050`.
- Vtable evidence is bounded: slot `0x005e4f64[0]` points to `CDXBattleLine__scalar_deleting_dtor`; slot 1 remains a raw target with no function object at the pointer.
- `CDXBattleLine__LoadTextures`, `Setup`, `UpdateHeightmap`, `BuildMesh`, `InitMipLevels`, `Render`, and `RenderTriOverlayPass` are ECX-only `__fastcall` rows with comments tied to texture setup, terrain sampling, mesh setup, mip fill, and overlay draw behavior.
- `CDXBattleLine__UpdateVertexBuffer` is `__thiscall` with `hud_y` and `use_unit_marker_offsets`; `RET 0x8` plus two render callsites prove the two stack arguments.
- `CDXBattleLine__SetupVertex` is cdecl; two caller sites push seven arguments and clean `ESP` with `add ESP,0x1c`.
- `CDXBattleLine__AppendOverlayVertex` is `__thiscall` with `world_x`, `world_y`, and `color_rgb`; `RET 0xc` plus caller pushes for `0xffff00` and `0xff0808` prove the stack shape.
- Post-save read-back verified 13 metadata rows, 13 tag rows, 18 xref rows, 2405 instruction rows, 13 decompile rows, 64 vtable rows, 270 callsite instruction rows, and 181 append-helper instruction rows.
- The queue refresh reports `6093` total functions, `3019` commented, `3074` commentless, `1347` exact-undefined signatures, and `1114` `param_N` signatures.
- Comment-backed proxy is `3019/6093 = 49.55%`; strict clean-signature proxy is `2971/6093 = 48.76%`.
- The next high-signal queue head is `0x0053b900 CClouds__ctor_like_0053b900`.
- The live Ghidra project backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260519-114822_post_wave589_battleline_core_verified` with 19 files, 160926599 bytes, `DiffCount=0`, and manifest hash `af1567751e713aaac69b5115e81bef5c3821f60b7d92fe27c6ac58173b1b1ee6`.

What is not proven:

- Runtime HUD battleline, marker, overlay, terrain-following, or split-screen rendering behavior remains unproven.
- Exact source identity remains unproven because no matching tracked Stuart source implementation body was found for this wave.
- Exact `CDXBattleLine`, `CDXSurf`, texture, dynamic-vertex-buffer, list, and field-block layouts remain unproven beyond the observed fields documented in the read-back notes.
- The full vtable/class boundary remains unproven beyond observed slot `0x005e4f64[0]` and the recorded raw slots.
- BEA patching, gameplay behavior, and rebuild parity remain unproven.
