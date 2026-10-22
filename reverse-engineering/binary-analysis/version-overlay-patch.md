# Version Overlay Patch

Status: historical — the patch pair belonged to the retired WinUI app's patch catalog, applied through AppCore; both were removed on 2026-10-22
Last updated: 2026-10-22 (Scope, Safety Model and Notes put in the past tense: these rows were the WinUI app's, through AppCore)
Summary: the two byte patches that drew `V1.00 - PATCHED` in the title/menu version overlay, how the WinUI app offered them, and the one copied-game run that showed the marker.

> Patch note for the opt-in `V1.00 - PATCHED` marker bytes

## Scope

The retired WinUI app's Binary Patches page, which applied AppCore's patch catalog, shipped one visible stable row that redirected the bottom-left version-format pointer when the user explicitly selected the marker. A hidden cave-string payload row was selected with that visible marker only. A bounded copied-game title/menu runtime smoke confirmed the visible `V1.00 - PATCHED` marker in one local run; this document does not claim broader overlay, gameplay, or parity behavior.

The WinUI app's Windowed & Mods page also exposed Proof quick-pick controls named
`Add PATCHED marker` and `Clear PATCHED marker`. They only selected or cleared the
existing visible `version_overlay_use_patched_format_pointer` row; AppCore's catalog
dependency handling added the hidden `version_overlay_patched_format_cave_string`
payload when a copied profile was prepared. The companion never offered or applied
these patches.

## Patch Pair

| Patch Id | File Offset | Purpose |
|---|---:|---|
| `version_overlay_use_patched_format_pointer` | `0x06416F` | Redirect the version-format pointer to a cave-hosted patched string |
| `version_overlay_patched_format_cave_string` | `0x1AA444` | Install the string payload `V%1d.%02d - PATCHED` in the code cave |

## Behavior

- Retail version-format pointer is redirected to a cave string.
- When the title/menu overlay path was exercised with version `1.00` in one copied-game run, the patched format rendered as `V1.00 - PATCHED` instead of the stock version-only display.
- These two patch rows were paired, but they were not applied automatically alongside unrelated patch selections.
- The visible `version_overlay_use_patched_format_pointer` row brought in the hidden `version_overlay_patched_format_cave_string` payload row.

## Safety Model

- AppCore byte-verified both patches before writing them.
- AppCore restored both through its normal `BEA.exe.original.backup` rollback path.
- They do not change gameplay logic; they only affect the version overlay string path when that path is exercised.

## Evidence

- The retired patch catalog (`patches/catalog/patches.v2.json` and `patches/README.md`) and the apply engine that
  used it, both removed on 2026-10-22; Git keeps them (commit `86d1af7` is the last that has them).
- Copied-game runtime smoke artifact: retained in ignored local evidence storage.
- First captured title/menu frame: retained in ignored local evidence storage; public summary is only that the frame showed `V1.00 - PATCHED` in one local run.

## Notes

- In the WinUI app this was a standalone opt-in visible marker row.
- The only visible proof is one copied-game title/menu run. Other overlay paths, gameplay paths, version-cheat paths, long sessions, rebuild parity, and no-noticeable-difference parity remain separate proof.
