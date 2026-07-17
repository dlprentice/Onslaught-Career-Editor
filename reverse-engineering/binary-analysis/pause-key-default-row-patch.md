# Pause-key default-row patch

Status: experimental copied-profile patch with one bounded pause/resume observation.

`pause_o_scan_initializer_experiment` changes the retail default single-binding initializer for `BUTTON_PAUSE` in a copied executable.

## Byte contract

| Item | Value |
| --- | --- |
| Retail function | `0x00514210 OptionsEntries__InitDefaultSingleBindingsTable` |
| Runtime table row | `DAT_00889718`, button `0x38` |
| Patch VA / file offset | `0x005144CD` / `0x1144CD` |
| Original / patched byte | `01` / `18` |

The surrounding clean bytes are:

```text
6A 00 6A 01 6A 08 6A 38 6A 00 B9 18 97 88 00 E8 ...
```

The patch changes only the `6A 01` immediate payload to DirectInput scan-code candidate `0x18` (`O`), consistent with the pinned source mapping hypothesis.

## Bounded observation

An exact-PID copied-profile session observed:

- the copied byte at `0x005144CD` as `0x18`;
- live mapping row `34` with `entryId=56`, `pushType=8`, and `keyArg=0x18`;
- an ordered scoped `O` query and button-`56` dispatch;
- `CGame__Pause` and pause-menu initialization in the first input window;
- pause-menu resume and `CGame__UnPause` after `ENTER` in the second window.

The session used the clean-backup-derived copied executable with only `resolution_gate`, `force_windowed`, and this experiment. Free-camera flags remained off. A separate second-`O` attempt did not prove normal-gameplay unpause, so the supported statement is specifically `O` to open and `ENTER` to resume in the observed context.

## Boundary

The patch does not modify `defaultoptions.bea`, saves, configurable options rows, the installed executable, or the clean backup. The persisted options model covers 16 configurable UI rows and does not contain `BUTTON_PAUSE`; this experiment must not be folded into that format.

It does not prove broad pause/menu safety, every controller configuration, long-session behavior, online behavior, rendering parity, or rebuild parity. The row remains custom-only, outside default presets, and restricted to app-owned copied profiles.
