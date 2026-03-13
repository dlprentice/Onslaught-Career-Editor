# Version Overlay Patch

> Companion patch note for the shipped `V1.00 - PATCHED` watermark behavior

## Scope

The Binary Patches UI ships two stable companion patches that adjust the bottom-left version watermark when any selected binary patch is applied.

## Patch Pair

| Patch Id | File Offset | Purpose |
|---|---:|---|
| `version_overlay_use_patched_format_pointer` | `0x06416F` | Redirect the version-format pointer to a cave-hosted patched string |
| `version_overlay_patched_format_cave_string` | `0x1AA444` | Install the string payload `V%1d.%02d - PATCHED` in the code cave |

## Behavior

- Retail watermark format is redirected to a cave string.
- When the overlay is shown in game, the text becomes `V1.00 - PATCHED` instead of the stock version-only display.
- These two patches are shipped as stable companion patches and are applied automatically alongside the selected user-facing binary patches.

## Safety Model

- Both patches are byte-verified before write.
- Both patches are restored through the normal `BEA.exe.original.backup` rollback path.
- They do not change gameplay logic; they only affect the visible version overlay string path.

## Evidence

- `patches/catalog/patches.v2.json`
- `BinaryPatchEngine.cs`
- `patches/README.md`

## Notes

- This is not a standalone user toggle in the UI; it is a companion marker so patched binaries visibly identify themselves at runtime.
- If the base retail binary does not display the version watermark, these bytes remain harmless until that code path is exercised.
