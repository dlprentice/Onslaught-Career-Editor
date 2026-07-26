# Level 100 pause assets

This directory retains no retail payload. The local materializer copies four
hash-gated inputs from a user-provided Steam installation to ignored paths.

| Local file | Released source | SHA-256 |
| --- | --- | --- |
| `blank.texture.aya` | `data/resources/dxtntextures/FrontEnd%v2%FE_Blank.tga(0)A8R8G8B8.aya` | `01D55E16E994DEC02191E6F62ADCB5A82A1F0CA3B5629E489C9E5C82884FE7E9` |
| `circle-01.texture.aya` | `data/resources/dxtntextures/pausemenu%pause_circle01.tga(0)A8R8G8B8.aya` | `01622D0E442AEF1CCD5D5971CAD5B4C06D2B15D1980DD07A1DDF95A7BC7472C7` |
| `circle-02.texture.aya` | `data/resources/dxtntextures/pausemenu%pause_circle02.tga(0)A8R8G8B8.aya` | `4CD5E553A8A093D3A895F3639136FB6548267371C28914B00D3CCBB3C153516F` |
| `endcurve.texture.aya` | `data/resources/dxtntextures/MessageLog%endcurve.tga(0)A8R8G8B8.aya` | `843DEFB41F22782E01C037D36A1B03B3AB8BA6C81624B9AD6E0B6E61E2568635` |

## `endcurve.texture.aya` — the confirmation panel's corner cell

`CMessageLog__RenderPanelFrame` (`0x004B9010`) holds this texture at `this+0x08`
and draws it into the four 32×32 corner cells of the panel frame, with
`FrontEnd%v2%FE_Blank.tga` filling the four stretched edges and the centre.

Decoded from the 291-byte source above (one AYA zlib record, 1152-byte `DDS `
payload): **32×32, `DXT2` FourCC, no mip chain**, 1024 bytes of block data =
exactly 64 4×4 blocks for a single 32×32 level. The 32×32 read in the panel
frame is therefore the texture's native size, and matches the measured corner
scalar `_DAT_005DB2B8` = 32.0.

Alpha content, from the decoded 1024 texels: 753 fully opaque (255), 208 fully
transparent (0), 63 intermediate spread evenly across the 4-bit ramp — a soft
one-texel antialiased edge. The shape is a filled quarter disc, opaque toward
the lower-left and clear toward the upper-right, so retail flips it per corner.
RGB is effectively white (246..255 on every opaque texel; 36 distinct RGB
triples total), which is consistent with the frame being drawn as a pure alpha
mask under the measured `RGB 0, alpha 192` tint. As with every other DXT2 asset
here the label is a retail toolchain mislabel: alpha is **straight**, not
premultiplied — 31 of the 63 semi-transparent texels already have RGB above
their own alpha, which premultiplied data cannot.

The renderer reuses the existing ignored `Hud/font-22.texture.aya` and
`Hud/font-13ps.texture.aya`. Tracked Steam function summaries for
`PauseMenu__Init` (`0x004CDE60`), `CPauseMenu__Render` (`0x004D11D0`), and
the menu-range/item renderers identify the root, confirmation, render, and
input/action owners. Localized root and confirmation text was checked against
shipped English table SHA-256
`789ECFF619D077092769DF281C540D138A25FCC74D70023466A604888E59371A`;
the three option-root labels also exist as literal Steam strings.

The current renderer's 640×480 coordinate space, placement, fade timing,
circle motion, colors, and row hit regions are bounded reconstruction choices;
the tracked evidence does not establish pixel or runtime presentation parity.
Only the evidenced root and Retry/Quit confirmation flow belong to this
renderer. Message Log, Briefing, Controller Options, Sound Options, and Video
Options remain visibly disabled because the current rebuild has no canonical
integrated panel or live settings-mutation owner for those rows. Continue
resumes the same deterministic session; Retry replaces it through the existing
frontend Loading seam; Quit returns to the existing Main Menu. No pause subpage
or parallel mission/frontend state is inferred.
