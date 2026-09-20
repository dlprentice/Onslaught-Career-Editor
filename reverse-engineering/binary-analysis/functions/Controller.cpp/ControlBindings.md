# Control Bindings (Options Entries)

Status: active bounded contract; complete remap/input acceptance pending
Last updated: 2026-09-19
Summary: original preset execution establishes initialized-table replacement, enabled-device fallback and the boundary between saved bindings and runtime bindings.
Source File: binary-derived contract; no exact partial-source body asserted. Binary: pristine `BEA.exe.original.backup`.
Evidence: MEASURED — selected pristine instructions and 20 isolated preset controls; historical remap/UI mappings below remain subject to recheck.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

This documents the **0x20-byte “options entries”** block in `.bes` / `defaultoptions.bea` and the BEA.exe code that reads/writes it.

The key finding is that these “options entries” are not generic settings blobs; they are **persisted control bindings** (two slots per action) plus a small remap state machine.

Related save-file doc: `reverse-engineering/save-file/save-format.md` (Region 3: Options Block + Tail).

## File Layout Summary

- Options entries start at file offset `0x24BE`.
- Steam build (retail) observed fixed **16 entries** (`N=16`) and a fixed file size of `0x2714` (10,004 bytes).
  - Internally the size logic is `0x2514 + 0x20*N`, but this project does **not** resize save files.
- Tail begins at `0x24BE + 0x20*16` (file offset `0x26BE`) and contains `g_ControlSchemeIndex` (tail + `0x08`).

## Independently rechecked preset behavior — September 19

`Controls__ApplyPreset` at `00453780` writes its full argument to `00677d70`,
then may replace binding records. It does not merely change how two immutable
saved slots are interpreted. The earlier description of distinct "scheme
layers" was insufficient for the actual initialized retail tables.

Original `00453460` creates one 16-record preset group at `00677af0` followed
by two sentinels. Original `00453630` creates a 16-record joystick fallback
table at `006778d0` followed by one sentinel; `006778d4` is its ID column,
not its record base. Original `00514210` creates 47 runtime records at
`008892d8`: 16 active and 31 inactive, then a sentinel. The initializers write
the active byte and leave padding bytes untouched; ordinary BSS supplies zero
padding. Neither table is recovered by reading these BSS addresses from disk.

| Scheme and initialized inputs | Rechecked result |
| --- | --- |
| `0` | Stores the scheme; preserves the runtime table and preset cursor. |
| `1` | Copies all 32 bytes of each preset row into the first matching runtime ID, including active/padding, ID and both slots. Ordinary matching rows already have a secondary slot, so enabled devices do not replace them on this path. |
| Positive `>=2`, no enabled detected device | Repeats the same group; the initialized table does not contain separate groups for schemes 2, 3 or 4. Selected cases 2 and 4 have the same final bindings as scheme 1. |
| Positive `>=2`, enabled detected devices | After the first group, substitutes fallback bindings using the first two enabled device indices and returns. Cases 2, 3 and 65535 have the same binding result with the same supplied hardware state. |
| Negative direct argument | Executes one group through the signed loop condition. This direct-call control is not a value produced by TailRead's zero-extended 16-bit field. |

The hardware predicate uses detected count `00888ff8` and nonzero **enable
flags** at `00889024 + index`. These bytes are user-toggleable: the rechecked
handler at `004d0420/004d0423` toggles one, clears eligible disabled-device
slots, then calls ApplyPreset at `004d0484`. They are not simply presence bits.
Counts in the isolated controls are explicitly bounded to `0..4`; ApplyPreset
itself has no such admission check.

The first enabled device replaces slot 0 (`+08..+13`) from the fallback row
and writes its index at `+08`. A second enabled device similarly replaces
slot 1 (`+14..+1f`). If only one exists, the original code writes **only
`+14 = -1` across all 47 runtime entries**, including inactive entries; the
remaining secondary-slot bytes survive. Disabled indices are skipped, and a
third enabled device is unused by this selection.

FindById ignores active status, chooses the first match and stops at ID `-1`.
Controlled missing, duplicate, inactive and early-sentinel IDs demonstrate
those effects and resulting size changes. A separate authored preset with
all secondary slots absent exercises the general secondary-slot fallback;
that is not the untouched shipped preset table.

The ordinary pause-menu selector has a count virtual returning 2
(`005de66c + 40 -> 004059c0`), with the generic selector clamping to `0..1`.
This is a freshly inspected static UI limit, not a file-format admission limit.
Older reports of real saves containing 3 or 4 remain inherited observations;
these controls derive higher scheme values privately from the real fixture.

The 20 direct controls retain nine unchanged bodies and have no intercepted
callees. They use original initializers and copy the real fixture's binding
rows into runtime memory with an explicitly authored setup; they **do not**
execute the career loader. Complete selected tables, guards and source
immutability are compared. A separate control populates all 31 inactive
secondary slots before execution and observes their field0 clearing while
the adjacent eight bytes remain intact. Commands and exact pins are in
[VALIDATION.md](../../../../VALIDATION.md#original-control-preset-behavior--september-19).
Actual device enumeration, physical input and the full startup-to-preset
composition remain separate boundaries.

For tooling, custom scheme 0 preserves admitted manual bindings through this
preset helper. Selecting it is a deliberate settings change, not permission
to silently alter an unrelated saved scheme.

## When these bindings apply in the selected retail body

This trips up testing if you only patch a `.bes` save:

- `CCareer::Load(source, flag)` at `0x00421200`:
  - Low flag byte zero (boot path for `defaultoptions.bea`): copies options entries (`0x24BE`) into the in-memory options table and calls `OptionsTail_Read`, which calls ApplyPreset after reading the tail scheme.
  - Low flag byte nonzero (career save load): **skips** options entries and the tail snapshot.
- The frontend load path `CFEPLoadGame__DoLoad` at `0x00461e20` calls `CCareer::Load(..., flag=1)` and may forward the original save buffer to `CFEPOptions__WriteDefaultOptionsFile(source, size)` when the post-page-call low byte at `0082b5b0` is zero.
  - Result: a patched `.bes` can update `defaultoptions.bea` for the **next boot**, but keybind changes generally won’t take effect until restart.

The independently executed [menu-to-startup handoff](../../save-options-static-review-2026-05-26.md#original-menu-load-and-next-startup-composition)
demonstrates this distinction with supplied successful file operations. It does
not establish actual storage durability or real input remapping. The layout and
historical mapping sections below retain their earlier evidence; they are not
all newly reverified by these controls.

## Per-Entry Layout (0x20 bytes)

Each entry is 8 dwords:

| Offset | Type | Meaning |
|--------|------|---------|
| +0x00 | u32 | `active` flag in low byte (non-zero => entry is enabled/serialized) |
| +0x04 | s32 | `entry_id` (sentinel `-1` terminates in-memory table scanned by `OptionsEntries__FindById`) |
| +0x08 | u32 | slot0.field0 (often `0` for keyboard) |
| +0x0C | u32 | slot0.device_code (category enum used by UI formatting) |
| +0x10 | u32 | slot0.packed_key = `(vk<<16)|scan` |
| +0x14 | u32 | slot1.field0 |
| +0x18 | u32 | slot1.device_code |
| +0x1C | u32 | slot1.packed_key |

Notes:
- In BEA.exe UI, `scan` (low-16) is used with `GetKeyNameTextA(scan<<16, ...)` to render key names.
- For letter keys, `vk` often matches ASCII/VK (e.g. `W` is `0x57`) and `scan` is a DIK/scan-like code (e.g. `0x11`).
- Arrow keys often appear as `vk=0`, `scan` set (e.g. `scan=0xCB` for left).

## Key Functions (BEA.exe)

| Address | Name | Notes |
|---------|------|------|
| 0x0042db10 | `OptionsEntries__FindById` | Returns pointer to 0x20-byte entry by `entry_id` (sentinel `-1`) |
| 0x00453460 | `OptionsEntries__InitDefaultDualBindingsTable` | Initializes default dual-binding options-entry table at `DAT_00677af0` using `OptionsEntries__InitDualBindingEntry` (+ sentinels) |
| 0x00453630 | `FUN_00453630` (current saved name) | Rechecked initializer for joystick fallback records at `006778d0`; no Ghidra rename applied in this tranche |
| 0x00514210 | `OptionsEntries__InitDefaultSingleBindingsTable` | Initializes default single-binding options-entry table at `DAT_008892d8` using `OptionsEntries__InitSingleBindingEntry` (+ sentinel) |
| 0x00453970 | `CControllerDefinition__InitDefaults` | Initializes control-definition defaults/vtable for remap lifecycle helper object |
| 0x004539b0 | `CControllerDefinition__scalar_deleting_dtor` | Scalar deleting dtor wrapper for control-definition helper (`dtor` + optional free by flag) |
| 0x004539d0 | `CControllerDefinition__dtor` | Control-definition destructor body (key-sink reset gate + owned pointer cleanup) |
| 0x00453ac0 | `SharedVFunc__NoOp_Ret0C` | Shared zero-body `RET 0x0c` vtable target; not controller-specific because refs include unrelated script/datatype tables |
| 0x00453ad0 | `CControllerDefinition__RenderBindingsAndPollRemapInput` | Control-definition render/poll helper that calls `ControlsUI__RenderBindingsList` |
| 0x00453780 | `Controls__ApplyPreset` | Applies preset; updates `g_ControlSchemeIndex` and entry contents |
| 0x00453f50 | `Controls__DispatchRemap` | Maps `action_code` to `(entry_id, binding_type)` pairs and calls a callback |
| 0x004541e0 | `Controls__RemapKey` | High-level remap logic; sets globals used by callbacks |
| 0x00454e90 | `Controls__ClearDuplicateBinding` | Clears duplicates across entries/slots |
| 0x00455010 | `ControlsUI__RenderBindingsList` | Thiscall binding-list renderer; indexes persisted slots, formats key names, and triggers remap capture on click |
| 0x00456080 | `Controls__BeginRemapCapture` | Begins input capture for a remap (snapshots baseline, schedules callback) |
| 0x00456060 | *(code label)* | `Controls__DispatchRemap` callback: sets current `entry_id` / `binding_type` for UI rendering |
| 0x004565d0 | `OptionsEntries__SetBindingSlot` | Writes one slot `(field0, device_code, scan, vk)` into an entry |
| 0x00456610 | `CControllerDefinition__GetWidth` | Control-definition getter with saved `this` signature |
| 0x00456620 | `CControllerDefinition__GetRowHeight` | Control-definition getter with saved `this` signature |
| 0x00456630 | `CControllerDefinition__GetFlag1C` | Reads the control-definition byte flag at `this+0x1c` |
| 0x00456640 | `CControllerDefinition__ClearFlag1C` | Clears the control-definition byte flag at `this+0x1c` |
| 0x004540c0 | *(code label)* | Remap write-callback (plate comment in Ghidra) |
| 0x00456190 | `Controls__RemapCaptureKeySink` *(descriptive identity; live Ghidra remains unchanged)* | Installed by `Controls__BeginRemapCapture`; handles remap events, duplicate clearing, and binding writes. A frontend Options trace observed 694 of 1,056 body bytes, so the exact callback ABI and unobserved branches remain open. |

## Wave 370 Saved-Ghidra Frontend Controls Corrections (2026-05-13)

Serialized headless dry/apply/read-back hardened the saved Ghidra names, signatures, comments, and tags for `13` frontend controls/control-binding targets. This is static retail Ghidra evidence only; it does not prove runtime remap input behavior, concrete controller/control-definition layouts, local variable/type recovery, BEA launch, game patching, or rebuild parity.

Key corrections:

- `0x00453ac0` is now `SharedVFunc__NoOp_Ret0C`, not a `CControllerDefinition`-specific vfunc. The body is `RET 0x0c`, and data/vtable refs include unrelated script/datatype tables.
- `0x00455010` is saved as `void __thiscall ControlsUI__RenderBindingsList(void * this, int columnIndex, float unusedRowOffset, float listY, int interactive)`.
- `0x00456080` is saved as `void __fastcall Controls__BeginRemapCapture(void * controllerDefinition)`.
- `0x004565d0` is saved as `void __cdecl OptionsEntries__SetBindingSlot(int slotIndex, int entryId, int field0, int deviceCode, short scan, short vk)`.
- Four compact `CControllerDefinition` helpers at `0x00456610`, `0x00456620`, `0x00456630`, and `0x00456640` now have proof-boundary signatures/comments.

Validation: dry/apply both reported `targets=13 changed_or_would_change=13 failed=0` with `REPORT: Save succeeded`; read-back verified `13` metadata rows, `13` decompile exports, `26` xref rows, `2145` instruction rows, `13` tag rows, `64` vtable-slot rows, `252` callsite-instruction rows, and `1251` full `ControlsUI__RenderBindingsList` instruction rows. The focused package probe passes, and the live Ghidra backup is verified at `[maintainer-local-ghidra-backup-root]\BEA_20260513_100816_post_wave370_frontend_controls_verified`.

## Controls__DispatchRemap Table

`Controls__DispatchRemap(action_code, key_or_value, callback)` maps a UI-level `action_code` to one or more `(entry_id, binding_type)` pairs and calls:
`callback(key_or_value, entry_id, binding_type)`.

Observed mapping in BEA.exe:

| action_code | entry_id(s) | binding_type |
|------------:|-------------|-------------:|
| 0x3B | 0x1F | 9 |
| 0x3C | 0x20 | 9 |
| 0x3D | 0x1D | 9 |
| 0x3E | 0x1E | 9 |
| 0x40 | 0x1A | 9 |
| 0x41 | 0x1C | 9 |
| 0x42 | 0x19 | 9 |
| 0x43 | 0x1B | 9 |
| 0x45 | 0x10 | 9 |
| 0x46 | 0x11 | 9 |
| 0x48 | 0x12 and 0x13 | 10 and 9 |
| 0x49 | 0x14 | 10 |
| 0x4A | 0x21 | 8 |
| 0x4B | 0x15 | 9 |
| 0x4C | 0x3B | 8 |

## Remap Globals (BEA.exe)

These were renamed in Ghidra as part of the remap pipeline:

| Address | Name | Notes |
|---------|------|------|
| 0x00677868 | `g_ControlRemapSlotIndex` | Slot index `0/1` being edited |
| 0x0067786c | `g_ControlRemapActionCode` | UI action code (drives dispatch table in remap callback) |
| 0x00677870 | `g_ControlRemapBindingType` | Binding type/category (4/5 etc) used to map device_code |
| 0x00677874 | `g_ControlRemapVkScanPacked` | Packed key state used during capture/write-back |
| 0x00677878 | `g_ControlRemapCurrentBindingType` | UI renderer: binding type for the current row (set by callback at `0x00456060`) |
| 0x0067787c | `g_ControlRemapCurrentEntryId` | Current entry ID used by the UI renderer |
| 0x00677d74 | `g_ControlRemapArmed` | Capture state flag (byte) |
| 0x006290b4 | `g_ControlRemapActive` | UI “remap active” flag (byte) |

## Notes / Open Questions

- Mapping `entry_id` to “semantic actions” is confirmed from the retail UI code path: `ControlsUI__RenderBindingsList` (`0x00455010`) assigns `action_code = rowIndex + 0x37` and renders labels via `Localization__GetStringById(action_code)`, and `Controls__DispatchRemap` maps that `action_code` to the persisted `entry_id` values shown above.
- MCP `functions_create` can fail on code-label entrypoints (notably `0x00456190`) when the address is not a valid entrypoint; plate comments are in place and manual function creation in the UI is straightforward.
