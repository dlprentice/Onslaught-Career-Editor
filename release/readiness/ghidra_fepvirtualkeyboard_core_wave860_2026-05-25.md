# Ghidra CFEPVirtualKeyboard Core Wave860 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `fepvirtualkeyboard-core-wave860`

Wave860 CFEPVirtualKeyboard core saved comments/tags/signatures for eight important frontend/virtual-keyboard connective infrastructure rows from `0x0051ff90 CFEPVirtualKeyboard__Init` through `0x005214d0 CFEPVirtualKeyboard__IsSpecialKeyBlocked`. The pass corrected stale `0x0051fff0 CFEPOptions__EnumerateSaveFiles` to `CFEPVirtualKeyboard__SeedUniqueDefaultSaveName`, corrected the shutdown calling convention to `__fastcall`, and made no function-boundary changes or executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0051ff90 CFEPVirtualKeyboard__Init` | Vtable `0x005db830` slot 0; seeds weighted-column state `this+0x6f4` to `0.5`, clears edit/cursor/page fields, calls `CFEPVirtualKeyboard__InitKeyboardLayout`, and returns `1`. |
| `0x0051ffd0 CFEPVirtualKeyboard__Shutdown` | Vtable slot 1; clears key sink `DAT_0051feb0` through `PlatformInput__SetKeySinkCore` when active; stale cdecl storage corrected to object-method `__fastcall`. |
| `0x0051fff0 CFEPVirtualKeyboard__SeedUniqueDefaultSaveName` | Supersedes stale `CFEPOptions__EnumerateSaveFiles`; writes a `BEA` plus ` %d` default save name, enumerates existing savegames through `EnumerateSaveFiles_1/2`, avoids duplicates up to cap `0x1001`, clamps `this+0x44`, and sets `this+0x48`. |
| `0x00520130 CFEPVirtualKeyboard__TransitionNotification` | Vtable slot 6; from pages `0`, `9`, or `0xe` can reseed the default save name and resets page/row/column fields `this+0x6e4..0x6ec` plus `this+0x6f4`. |
| `0x005202d0 CFEPVirtualKeyboard__Process` | Vtable slot 2; refreshes the shared save list, installs/clears the virtual-keyboard key sink, polls storage through `PCPlatform__GetStorageDeviceInfo`, and shows `CFEPSaveGame__RemovedMUWhinge(0x3c)` on missing storage. |
| `0x00520370 CFEPVirtualKeyboard__ButtonPressed` | Vtable slot 3; handles row movement, accept/cancel, key-token dispatch through `CFEPVirtualKeyboard__HandleKeyToken`, and column cycling while skipping blocked special keys. |
| `0x00521100 CFEPVirtualKeyboard__Render` | Vtable slot 5; renders/polls `CFEPDirectory__RenderSaveFileList`, copies selected save-name rows into the edit buffer, draws prompt/title/overlay paths, and calls `CFEPVirtualKeyboard__DrawPanel`. |
| `0x005214d0 CFEPVirtualKeyboard__IsSpecialKeyBlocked` | Blocks special tokens `4` and `5` on keyboard page `1`, and blocks token `9` when the edit buffer is empty or only spaces. |

Read-back evidence:

- `ApplyFEPVirtualKeyboardCoreWave860.java dry`: `updated=8 skipped=0 renamed=0 would_rename=1 signature_updated=2 comment_only_updated=6 missing=0 bad=0`
- `ApplyFEPVirtualKeyboardCoreWave860.java apply`: `updated=8 skipped=0 renamed=1 would_rename=1 signature_updated=2 comment_only_updated=6 missing=0 bad=0`
- `ApplyFEPVirtualKeyboardCoreWave860.java final dry`: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 8 metadata rows, 8 tag rows, 11 xref rows, 648 instruction rows, 8 decompile rows, 13 context metadata rows, 13 context decompile rows, 18 vtable slots, 74 callsite instruction rows, and three RTTI/save-name string dumps.
- Queue after Wave860: 6105 total, 5792 commented, 313 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5792/6105 = 94.87%`, strict clean-signature proxy `5792/6105 = 94.87%`.
- Next raw commentless row: `0x00523a70 CDXEngine__RenderMouseCursorSprite`.
- Commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `G:\GhidraBackups\BEA_20260525-134150_post_wave860_fepvirtualkeyboard_core_verified`, 19 files, 172231559 bytes, `DiffCount=0`.

What this proves:

- The eight target function rows exist in the saved Ghidra project.
- The saved function comments and tags include `fepvirtualkeyboard-core-wave860` and `wave860-readback-verified`.
- `0x0051fff0` is saved as `CFEPVirtualKeyboard__SeedUniqueDefaultSaveName`, not stale `CFEPOptions__EnumerateSaveFiles`.
- The observed bodies are static retail Ghidra evidence tied to vtable slots, xrefs, decompile/instruction exports, context helpers, and strings `.?AVCFEPVirtualKeyboard@@`, `BEA`, and ` %d`.

What remains unproven:

- Exact `CFEPVirtualKeyboard` layout.
- Exact key-token enum identity.
- Runtime virtual-keyboard input/render behavior.
- Runtime save-name or filesystem behavior.
- BEA patching behavior.
- Rebuild parity.
