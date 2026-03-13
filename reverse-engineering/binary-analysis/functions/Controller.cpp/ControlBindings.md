# Control Bindings (Options Entries)

This documents the **0x20-byte “options entries”** block in `.bes` / `defaultoptions.bea` and the BEA.exe code that reads/writes it.

The key finding is that these “options entries” are not generic settings blobs; they are **persisted control bindings** (two slots per action) plus a small remap state machine.

Related save-file doc: `reverse-engineering/save-file/save-format.md` (Region 3: Options Block + Tail).

## File Layout Summary

- Options entries start at file offset `0x24BE`.
- Steam build (retail) observed fixed **16 entries** (`N=16`) and a fixed file size of `0x2714` (10,004 bytes).
  - Internally the size logic is `0x2514 + 0x20*N`, but this project does **not** resize save files.
- Tail begins at `0x24BE + 0x20*16` (file offset `0x26BE`) and contains `g_ControlSchemeIndex` (tail + `0x08`).

## Control Scheme Nuance (Important)

`g_ControlSchemeIndex` determines how the game interprets the two binding slots in each entry:

- `0` = **Custom**: no preset is applied (see `Controls__ApplyPreset(0)` early-return). Tooling should prefer this mode when patching bindings directly.
- `>= 1` = **Preset scheme**: `Controls__ApplyPreset(scheme)` applies `scheme` layers from the preset table (base `DAT_00677af0`) and can rewrite entry slot fields based on the selected scheme.
  - Observed in retail saves: scheme values are not limited to `1` (we have seen `1`, `3`, `4`, etc).
  - Retail UI rendering still reads slot columns directly: `ControlsUI__RenderBindingsList` (`0x00455010`) indexes entries as `slot = param_2 / 2` (left column => slot0, right column => slot1), with no `g_ControlSchemeIndex` branch on slot orientation.

Implication for tooling:
- If you patch keybinds directly, **force `g_ControlSchemeIndex = 0`** so edits map predictably to in-game columns.

## When These Bindings Apply (Steam Build)

This trips up testing if you only patch a `.bes` save:

- `CCareer::Load(source, flag)` at `0x00421200`:
  - `flag == 0` (boot path for `defaultoptions.bea`): copies options entries (`0x24BE`) into the in-memory options table and calls `OptionsTail_Read` on the tail pointer, applying keybinds + tail globals.
  - `flag != 0` (career save load): **skips** applying options entries + tail snapshot to runtime.
- The frontend load path `CFEPLoadGame__DoLoad` at `0x00461e20` calls `CCareer::Load(..., flag=1)` and may write `defaultoptions.bea` from the loaded save buffer (load-path condition: `DAT_0082b5b0 == 0`) via `CFEPOptions__WriteDefaultOptionsFile(source, size)`.
  - Result: a patched `.bes` can update `defaultoptions.bea` for the **next boot**, but keybind changes generally won’t take effect until restart.

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
| 0x00514210 | `OptionsEntries__InitDefaultSingleBindingsTable` | Initializes default single-binding options-entry table at `DAT_008892d8` using `OptionsEntries__InitSingleBindingEntry` (+ sentinel) |
| 0x00453970 | `CControllerDefinition__InitDefaults` | Initializes control-definition defaults/vtable for remap lifecycle helper object |
| 0x004539b0 | `CControllerDefinition__scalar_deleting_dtor` | Scalar deleting dtor wrapper for control-definition helper (`dtor` + optional free by flag) |
| 0x004539d0 | `CControllerDefinition__dtor` | Control-definition destructor body (key-sink reset gate + owned pointer cleanup) |
| 0x00453780 | `Controls__ApplyPreset` | Applies preset; updates `g_ControlSchemeIndex` and entry contents |
| 0x00453f50 | `Controls__DispatchRemap` | Maps `action_code` to `(entry_id, binding_type)` pairs and calls a callback |
| 0x004541e0 | `Controls__RemapKey` | High-level remap logic; sets globals used by callbacks |
| 0x00454e90 | `Controls__ClearDuplicateBinding` | Clears duplicates across entries/slots |
| 0x00455010 | `ControlsUI__RenderBindingsList` | Renders the bindings list and triggers remap capture on click |
| 0x00456080 | `Controls__BeginRemapCapture` | Begins input capture for a remap (snapshots baseline, schedules callback) |
| 0x00456060 | *(code label)* | `Controls__DispatchRemap` callback: sets current `entry_id` / `binding_type` for UI rendering |
| 0x004565d0 | `OptionsEntries__SetBindingSlot` | Writes one slot `(field0, device_code, scan, vk)` into an entry |
| 0x004540c0 | *(code label)* | Remap write-callback (plate comment in Ghidra) |
| 0x00456190 | *(code label)* | Remap capture state machine callback (plate comment in Ghidra) |

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
