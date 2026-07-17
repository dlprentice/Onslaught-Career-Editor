# Frontend clear-screen color patches

Status: cataloged copied-executable presets with bounded title-screen and navigated-menu observations.

These mutually exclusive rows change the immediate passed to the DirectX frontend clear-screen path. The patch catalog owns the exact byte definitions.

| Item | Value |
| --- | --- |
| Function | `0x00540F70 CDXFrontEnd__RenderStart` |
| Source anchor | `references/Onslaught/DXFrontend.cpp` |
| VA / file offset | `0x00540F88` / `0x140F88` |
| Original | `3F 1F 1F 00` (`0x001F1F3F`) |
| Dark red | `1F 1F BF 00` (`0x00BF1F1F`) |
| Dark green | `1F BF 1F 00` (`0x001FBF1F`) |
| Black | `00 00 00 00` |

Controlled copied-profile runs reached both the title screen and a navigated Goodies menu for each color. The observed margins stayed in the selected red, green, or black family after frontend shading. Each run launched only the copied executable, used scoped input, stopped the managed process, and left installed/source executable and source save/options hashes unchanged.

WinUI exposes the three rows as normal patches and as equivalent quick picks. The quick picks select or clear the same mutually exclusive catalog entries; they do not introduce a second patch format.

## Boundary

This changes a clear-screen background immediate, not textures, menu art, fonts, HUD colors, mission UI, or gameplay rendering. It does not prove every frontend state, every machine, or rebuild parity. The rows are valid only for app-owned copied executables.
