# Ghidra DX Font Head Wave595 Readiness Note

Date: 2026-05-19
Status: static saved-Ghidra evidence only

Wave595 hardened the DX bitmap/font queue head: the CDXBitmapFont constructor/resource/init helpers and the first CDXFont create/draw rows.

Saved rows:

| Address | Function |
| --- | --- |
| `0x0053f730` | `CDXBitmapFont__ctor_base` |
| `0x0053f770` | `CDXBitmapFont__ReleaseFontResources` |
| `0x0053f7d0` | `CDXBitmapFont__InitNamedFontSlot` |
| `0x0053f830` | `CDXBitmapFont__InitTextureFontSlot` |
| `0x0053f880` | `CDXFont__CreateFromTexture` |
| `0x0053fb00` | `CDXFont__CreateGDIFont` |
| `0x00540010` | `CDXFont__DrawTextScaled` |
| `0x00540640` | `CDXFont__DrawText` |

What is proven:

- Ghidra now records clean signatures, function comments, and `dxfont-head-wave595` tags for all eight rows.
- `CDXBitmapFont__ctor_base` is called by `PCPlatform__LoadFonts` and `PCPlatform__DeserializeFontsAndAssets` after allocating CDXBitmapFont-sized objects; it zeroes fields at `this+0x168/+0x16c/+0x170/+0x174/+0x178`, installs vtable `0x005e504c`, calls `CDXBitmapFont__BuildGlyphRemapTables`, and returns `this`.
- `CDXBitmapFont__ReleaseFontResources` is called by `CPCPlatform__UnloadFonts` and `PCPlatform__DeserializeFontsAndAssets`; it reinstalls vtable `0x005e504c`, releases/clears cached fields at `this+0x170/+0x174/+0x178`, and returns without freeing the object.
- `CDXBitmapFont__InitNamedFontSlot` is the Terminal/debug GDI font-slot initializer. `RET 0xc` proves three stack arguments after `this`; the body copies the font face into `this+4`, stores font size/style at `this+0x54/+0x58`, clears `this+0x170`, and marks `this+0x15c` as the GDI/font-face path.
- `CDXBitmapFont__InitTextureFontSlot` is the main/small/title texture-font slot initializer. `RET 0x8` proves two stack arguments after `this`; the body copies the texture name into `this+0x5c`, clears the GDI flag at `this+0x15c`, stores glyph cell width at `this+0x54`, and clears `this+0x170`.
- `CDXFont__CreateFromTexture` lazily loads the texture named at `this+0x5c`, records atlas dimensions at `this+0x160/+0x164`, and builds glyph UV/width metrics from alpha coverage.
- `CDXFont__CreateGDIFont` lazily builds a DIB-backed Windows font texture from the face/style fields, rasterizes printable characters, writes glyph metrics, and labels the generated texture `SystemFont`.
- `CDXFont__DrawTextScaled` is a high-fan-in UTF-16 text renderer with `RET 0x24`; it lazily creates font resources, optionally scales normalized coordinates by window size, locks CFastVB quads, applies packed or per-character color, renders the cached texture, restores render state, and returns `0`.
- `CDXFont__DrawText` is the `RET 0x1c` convenience wrapper that forwards unscaled text drawing into `CDXFont__DrawTextScaled` with x/y scale `1.0`.
- Post-save read-back verified 8 metadata rows, 8 tag rows, 84 xref rows, 392 instruction rows, and 10 decompile rows.
- The queue refresh reports `6093` total functions, `3046` commented, `3047` commentless, `1343` exact-undefined signatures, and `1091` `param_N` signatures.
- Comment-backed proxy is `3046/6093 = 49.99%`; strict clean-signature proxy is `3001/6093 = 49.25%`.
- The next high-signal queue head is `0x00540840 PCPlatform__ReadHeaderPairAndResetByteCount`.
- The live Ghidra project backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260519-151349_post_wave595_dxfont_head_verified` with 19 files, 161057671 bytes, `DiffCount=0`, and manifest hash `e07246471f4c0b1390ed79adae1b1649c1f31e25b5e8c555709e87ca289a529c`.

What is not proven:

- Runtime font loading, text rendering, GDI font creation, texture atlas behavior, UI/HUD text behavior, and resource teardown remain unproven.
- Exact `CDXBitmapFont`, `CDXFont`, `CTexture`, `CVBufTexture`, `CFastVB`, GDI, and PCPlatform layouts remain unproven beyond the observed fields documented in the read-back notes.
- Exact source identity remains unproven because the current tracked Stuart source snapshot does not include matching `DXFont.cpp` implementation bodies.
- BEA patching, gameplay behavior, packaged release behavior, and rebuild parity remain unproven.
