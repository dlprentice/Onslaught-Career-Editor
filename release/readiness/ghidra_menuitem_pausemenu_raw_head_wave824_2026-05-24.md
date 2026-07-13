# Ghidra MenuItem/PauseMenu Raw Head Wave824 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x004cf050` → `CMenuItem__Destructor_Thunk` (was `CMenuItem__Destructor`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `menuitem-pausemenu-raw-head-wave824`

Wave824 MenuItem/PauseMenu raw-head hardening saved names, signatures, comments, and tags for four raw-commentless UI/control-binding helpers:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x004cf050 CMenuItem__Destructor_Thunk` | `void __thiscall CMenuItem__Destructor_Thunk(void * this)` | Single-instruction jump thunk to `0x004a3730 CMenuItem__Destructor`; xref from `0x004cf030 CMouseSensitivityMenuItem__scalar_deleting_dtor`. |
| `0x004d04d0 CPauseMenu__ReloadSharedBlankTexture` | `void __cdecl CPauseMenu__ReloadSharedBlankTexture(void)` | Releases cached `DAT_0082b490` through `CTexture__DecrementRefCountFromNameField(DAT_0082b490+8)`, then reloads `FrontEnd_v2/FE_Blank.tga` through `CTexture__FindTexture(name,4,0,1,0,1)`. |
| `0x004d05c0 CMenuItemRange__IsBindingActive` | `int __thiscall CMenuItemRange__IsBindingActive(void * this)` | Returns 1 only when the binding/range context pointer at `this+0x08` exists and byte `context+0x08` is non-zero; xrefs from `CMenuItemRange__Render`. |
| `0x004d0de0 CPauseMenu__GetBindingCapacityWarningText` | `short * __cdecl CPauseMenu__GetBindingCapacityWarningText(void)` | Checks `Controls__FindFirstFreeBindingSlot(0)` and returns `Localization__GetStringById(0xe8)` when full; multiplayer branch also checks slot 1 and returns `Localization__GetStringById(0xe9)` when full. |

Read-back evidence:

- `ApplyMenuItemPauseMenuRawHeadWave824.java dry`: `updated=0 skipped=4 renamed=0 would_rename=2 signature_updated=3 comment_only_updated=1 missing=0 bad=0`
- `ApplyMenuItemPauseMenuRawHeadWave824.java apply`: `updated=4 skipped=0 renamed=2 would_rename=0 signature_updated=2 comment_only_updated=2 missing=0 bad=0`
- `ApplyMenuItemPauseMenuRawHeadWave824.java final dry`: `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 4 metadata rows, 4 tag rows, 5 xref rows, 964 target instruction rows, 4 target decompile rows, 9 helper metadata rows, 1629 helper instruction rows, 4 caller decompile rows, and 684 caller instruction rows.
- Queue after Wave824: 6098 total, 5632 commented, 466 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5632/6098 = 92.36%`, strict clean-signature proxy `5632/6098 = 92.36%`.
- Next raw commentless row: `0x004d6240 StrCopyN`.
- Commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-190751_post_wave824_menuitem_pausemenu_raw_head_verified`, 19 files, 171576199 bytes, `DiffCount=0`.

What this proves:

- The four target function rows exist in the saved Ghidra project.
- The saved names/signatures/comments/tags include `menuitem-pausemenu-raw-head-wave824` and `wave824-readback-verified`.
- The observed behaviors are static retail Ghidra evidence tied to post-export metadata, xrefs, instructions, helper metadata, caller decompiles, and read-back logs.

What remains unproven:

- Exact concrete UI/control-binding layouts.
- Exact source-body identity.
- Runtime frontend/pause-menu rendering or input behavior.
- Runtime controller remapping behavior.
- BEA patching behavior.
- Rebuild parity.
