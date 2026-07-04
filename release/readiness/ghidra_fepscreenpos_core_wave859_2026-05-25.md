# Ghidra FEPScreenPos Core Wave859 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `fepscreenpos-core-wave859`

Wave859 CFEPScreenPos core saved comments/tags for five important frontend/screen-position connective rows and corrected two stale render signatures after serialized headless dry/apply/read-back/final dry with the `fepscreenpos-core-wave859` and `wave859-readback-verified` tags. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0051f9f0 CFEPScreenPos__Init` | CFEPScreenPos vtable `0x005db858` slot 0; clears calibration/page fields at `this+0x04` and `this+0x08`; returns `1`. |
| `0x0051fa00 CFEPScreenPos__ButtonPressed` | Vtable slot 3; buttons `0x2a/0x2b` adjust `this+0x08` and persist through `CCareer__SetKillCounterTopByte_23F8`; buttons `0x36/0x37` adjust `this+0x04` and persist through `CCareer__SetKillCounterTopByte_23F4`; buttons `0x2c/0x2e` accept/restore page flow through `CFrontEnd__SetPage` and `CFEPOptions__SetKillCounterTopBytes_23F4_23F8`. |
| `0x0051fb60 CFEPScreenPos__RenderPreCommon` | Vtable slot 4; corrected to `void __stdcall CFEPScreenPos__RenderPreCommon(float transition, int dest)` because raw instructions read only `[ESP+4]` / `[ESP+8]` and return with `RET 0x8`; calls `CFrontEnd__RenderPreCommonFade` when transition is `1.0`. |
| `0x0051fb90 CFEPScreenPos__Render` | Vtable slot 5; corrected to `void __stdcall CFEPScreenPos__Render(float transition, int dest)`; draws the screen-position instructional strings at `0x0063fcf0`, `0x0063fcc8`, and title `0x0063fcb0` (`Adjust Screen Position`), plus context help prompts `5` and `6`. |
| `0x0051fd50 CFEPScreenPos__TransitionNotification` | Vtable slot 6; records `PLATFORM__GetSysTimeFloat()+delay`, snapshots the career top-byte pair through `CFEPOptions__GetKillCounterTopBytes_23F4_23F8`, then copies `this+0x10/0x14` into active fields `this+0x04/0x08`. |

Read-back evidence:

- `ApplyFEPScreenPosCoreWave859.java dry`: `updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=3 missing=0 bad=0`
- `ApplyFEPScreenPosCoreWave859.java apply`: `updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=3 missing=0 bad=0`
- `ApplyFEPScreenPosCoreWave859.java final dry`: `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 5 metadata rows, 5 tag rows, 5 xref rows, 225 instruction rows, 5 decompile rows, 13 context metadata rows, 13 context decompile rows, 18 vtable rows, and four screen-position/RTTI string dumps.
- Queue after Wave859: `6105` total functions, `5784` commented, `321` commentless, `0` exact-undefined signatures, `0` `param_N` signatures, comment-backed proxy `5784/6105 = 94.74%`, strict proxy `5784/6105 = 94.74%`.
- Next raw commentless row: `0x0051ff90 CFEPVirtualKeyboard__Init`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-131538_post_wave859_fepscreenpos_core_verified`, 19 files, 172198791 bytes, `DiffCount=0`.

What this proves:

- The five target function rows exist in the saved Ghidra project.
- The saved signatures/comments/tags include `fepscreenpos-core-wave859` and `wave859-readback-verified`.
- The two render slots no longer carry the stale extra first parameter.
- The observed bodies are static retail Ghidra evidence tied to vtable DATA xrefs, decompile/instruction exports, and string dumps.

What remains unproven:

- Exact `CFEPScreenPos` layout.
- Exact screen-axis semantics.
- Runtime screen-position calibration behavior.
- Runtime frontend/render/input behavior.
- BEA patching behavior.
- Rebuild parity.
