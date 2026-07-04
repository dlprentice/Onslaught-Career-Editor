# Ghidra Game Slot Helpers Wave803 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `game-slot-helpers-wave803`

Wave803 saved Ghidra comments and tags for the two CGame runtime slot-bit helper rows at `0x0046d3a0 CGame__SetSlot` and `0x0046d410 CGame__GetSlot`. The pass made no renames, no signature changes, no function-boundary changes, and no executable-byte changes.

Probe anchors: Wave803 game slot helpers; 0 param_N.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0046d3a0 CGame__SetSlot` | Range-checks slot `0..255`, prints the SetSlot out-of-range string at `0x0062434c`, computes `slot >> 5` and `1 << (slot & 31)`, then sets `this+0x308[index]` when `val == 1` and clears it otherwise. Xrefs are `IScript__SetSlot` and `IScript__SetSlotSave`. |
| `0x0046d410 CGame__GetSlot` | Range-checks slot `0..255`, returns the bit test from `this+0x308[(slot >> 5)]`, and prints the GetSlot out-of-range string at `0x00624318` before returning false. Xref is `IScript__GetSlotBitValue`. |

Read-back evidence:

- `ApplyGameSlotHelpersWave803.java dry`: `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=2 missing=0 bad=0`
- `ApplyGameSlotHelpersWave803.java apply`: `updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=2 missing=0 bad=0`, with `REPORT: Save succeeded`.
- `ApplyGameSlotHelpersWave803.java final dry`: `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 2 metadata rows, 2 tag rows, 3 xref rows, 170 instruction rows, and 2 decompile rows.
- Queue after Wave803: 6098 total, 5574 commented, 524 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5574/6098 = 91.41%`, strict clean-signature proxy `5574/6098 = 91.41%`.
- Next raw commentless row is `0x00472e50 CVBufTexture__DrawSpriteWithDefaultTextureFallback`; commentless high-signal, signature, and name-confidence queues are empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-084656_post_wave803_game_slot_helpers_verified`, 19 files, 171314055 bytes, `DiffCount=0`.

What this proves:

- The two target rows exist in the saved Ghidra project.
- Saved names/signatures remain `void __thiscall CGame__SetSlot(void * this, int slot, int val)` and `bool __thiscall CGame__GetSlot(void * this, int slot)`.
- Saved comments and tags include `game-slot-helpers-wave803` and `wave803-readback-verified`.
- Observed static retail behavior matches source `CGame::SetSlot` / `CGame::GetSlot` slot-bit logic and the existing IScript slot handler xrefs.

What remains unproven:

- Exact CGame layout beyond the stated `this+0x308` slot-bit array.
- Runtime mission-script behavior.
- Runtime save/update behavior.
- BEA patching behavior.
- Rebuild parity.
