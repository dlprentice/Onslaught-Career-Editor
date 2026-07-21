# First-person HUD assets

This directory owns the ignored local PC HUD textures consumed by the current
Level 100 first-person slice. Run `npm run prepare:rebuild-assets` to
materialize the exact supported files from a user-provided retail installation.
The payloads are not tracked in the current source tree or included in release
packages and remain copyright of their respective rights holders;
`rebuild/LICENSE` covers reconstruction code only.

The source files came from the released game's `data/resources/dxtntextures`
directory. Their names are direct literals in the canonical Steam executable.
A clean app-owned Level 100 run and the released HUD render paths establish the
bounded opening composition: generated threat circle plus v3 crosshair layers,
the lower-left scanner/weapon assembly, the lower-right battleline and portrait,
and the conditional lower-center message treatment.

| Curated file | Released source name | SHA-256 |
| --- | --- | --- |
| `bar-line.texture.aya` | `hud%v2%BarLine.tga(0)X8R8G8B8.aya` | `16796E3A8ACFEC3529E03C29AFBEFBE28C92FFCCD5B05574F992E8F31976704D` |
| `battleline-outline.texture.aya` | `hud%v2%BattleLineOutline.tga(0)X8R8G8B8.aya` | `B1C097B29DD81E2A0493F72A157CCD5AD249B5ABF758224C75DF4F93973D0405` |
| `circle-darkener.texture.aya` | `hud%v2%CircleDarkener.tga(0)A8R8G8B8.aya` | `7BD18594757165DCDD8DADB618EA99EB500ED105DBE2D6A6F66BBCBC31C323A3` |
| `circle-mask.texture.aya` | `hud%v2%CircleMask.tga(0)A8R8G8B8.aya` | `14D809F9B45F5153F82FA1F80152690B554710D83F91B8CBE203DE5CF18A9DFA` |
| `radar-outline.texture.aya` | `hud%v2%RadarOutline.tga(0)X8R8G8B8.aya` | `507D465248F7321F2332413B2C6F461F3B3C45D87C52D86C38C43104043D7DC7` |
| `compass-objective-marker.texture.aya` | `hud%v2%CompassObjectiveMarker.tga(0)A8R8G8B8.aya` | `E24FCA83DE34646A7328C313E7B89AC02C6BC4B04A69A74BF3EE81B3D57283DF` |
| `crosshair-dot.texture.aya` | `hud%v3%hud_crosshair_dot.tga(0)A8R8G8B8.aya` | `19E1B35B885A36230E5A1D47A9910164B0CA177746649A15C146CEFCA29651DD` |
| `crosshair-primary.texture.aya` | `hud%v3%hud_crosshair_primary.tga(0)A8R8G8B8.aya` | `310DAE2F7DD976F6CC724604737726885AFF96AB6BC507E41F90DCA60D134B17` |
| `crosshair-secondary.texture.aya` | `hud%v3%hud_crosshair_secondary.tga(0)A8R8G8B8.aya` | `7B078344E64D1E78EF64A8E21BDD3787E059B628C6A442634E9D13BA7D3A0487` |
| `message-noise.texture.aya` | `MessageBox%noisebig.tga(0)X8R8G8B8.aya` | `F5C43C330394DB9EB7C1E782F3F30FE847DE01D7CE9335D2C7F9FD24BABB1825` |
| `radio-view.texture.aya` | `hud%v2%RadioView.tga(0)A8R8G8B8.aya` | `888D5A70AB812E23F75DB76AB2ED71CD2CCE04191EE282D525C86E337CC01778` |
| `radio-north.texture.aya` | `hud%v2%RadioNorth.tga(0)A8R8G8B8.aya` | `E5DFD8DB4DD73E9AEEFFBB009FCA68D889572C996987BCE365B0B5B4D0A7ED85` |
| `scanner-blob-small.texture.aya` | `hud%ScannerBlobSmall.tga(0)A8R8G8B8.aya` | `D7E9D287536F23E67BF35F678EC75D1A349353AE1D9D00B87CE09F6BD03641E4` |
| `weapon-fill.texture.aya` | `hud%v2%WeaponFill.tga(0)A8R8G8B8.aya` | `E639910D70AE10B044423CD5025C300C61CB8A9B5765890FD1A011C7D4499C0D` |
| `weapon-outline.texture.aya` | `hud%v2%WeaponOutline.tga(0)X8R8G8B8.aya` | `2E2DA786DB82C8FD76DE36D8D71FE744DDDDD364247467CBA1BFB9A95E52D62B` |
| `objective-inner-centre.texture.aya` | `hud%v2%ObjectiveInnerCentre.tga(0)A8R8G8B8.aya` | `FC42774E8C4F4534B65009807BFDB333443A9F5202C6A2C59DFF0DDDBED4F55B` |
| `objective-inner-left.texture.aya` | `hud%v2%ObjectiveInnerLeft.tga(0)A8R8G8B8.aya` | `70030AACE505E8E3D7F56DDE0B9C6A929F3D2C61912FC03AC816746B6D8A96BD` |
| `objective-inner-right.texture.aya` | `hud%v2%ObjectiveInnerRight.tga(0)A8R8G8B8.aya` | `7C85B0293FC7A524978A21E7CDC06B1DD3308E9A595AADCA054B51CD9A6AA113` |
| `objective-left.texture.aya` | `hud%v2%ObjectiveLeft.tga(0)A8R8G8B8.aya` | `0AE835780D1AF6C01F0272A50AFDA141ABCA70EAA5C23D74E7FC3968B6D9194F` |
| `objective-right.texture.aya` | `hud%v2%ObjectiveRight.tga(0)A8R8G8B8.aya` | `581F10446DB76ECE7AA7044B4C02F0431A79A7D606225D5C69A412C17F85078B` |
| `font-13ps.texture.aya` | `mustbe_Font13PS.tga(0)A8R8G8B8.aya` | `7ACC088B75E729CBDC2782E239A7D18BA0EC409E1BC890109AA1020F5EE81DC0` |
| `tatiana-portrait-oo.texture.aya` | `MessageBox%tat_oo.tga(0)A8R8G8B8.aya` | `39F40088069A8C68584A5A0CDA9E5AE7D4E4E5A248A12F0D0A240B8D3668621E` |
| `tatiana-portrait-ee.texture.aya` | `MessageBox%tat_ee.tga(0)A8R8G8B8.aya` | `4A4A17B72BBAFAE2B324E3A0A1C847226A288FEAA7C4273C45AA2DE8AEA3F99A` |
| `tatiana-portrait-mm.texture.aya` | `MessageBox%tat_mm.tga(0)A8R8G8B8.aya` | `802D8E22D8D304E12589A547F22AC2F2D5771B96AEA47306B3B2BBF752730DE5` |
| `tatiana-portrait.texture.aya` | `MessageBox%tat_aa.tga(0)A8R8G8B8.aya` | `34D451A6FC31E399B99032230413A60F146B41A0FEA65E61561A37D8EC757CFD` |
| `technician-portrait-oo.texture.aya` | `MessageBox%technic_oo.tga(0)A8R8G8B8.aya` | `B28A3818B8EF37DECFD8779D7ACAE74C657B5D510EDD2332587864F2A1E58A2C` |
| `technician-portrait-ee.texture.aya` | `MessageBox%technic_ee.tga(0)A8R8G8B8.aya` | `05326C603E8C9224C5BAB488A32AB9E9E19CA5B3FB424BC700AF97AE71C2527F` |
| `technician-portrait-mm.texture.aya` | `MessageBox%technic_mm.tga(0)A8R8G8B8.aya` | `263A2C107D6463A717DDEF20CC113CADFB585BD8ECBB1DB479F049843DCF3636` |
| `technician-portrait.texture.aya` | `MessageBox%technic_aa.tga(0)A8R8G8B8.aya` | `C4C1B11F4DDFB960AFC1C1D2A04020FADF997795ECCF651C07314141652F9603` |

The renderer uses the source alpha for DXT2 layers and additive composition for
the X8 outline, bar, and message-noise layers, matching their visible
black-background sprite semantics. The released font loader scans alpha within
each 16×16 Font13PS cell to derive proportional glyph widths; the client follows
that path rather than imposing a fixed advance. The eight 128×128 portraits are
the released `oo`, `ee`, `mm`, and `aa` frames for Tatiana and the technician.
The client uses their released order and 8/12/40/40 selection weights at a
deterministic presentation cadence; it does not claim audio-phoneme lip sync or
byte-identical retail RNG phase.

The released scanner path rotates contacts by Battle Engine yaw and clamps them
at 46 HUD units. The north sprite follows the released 45-unit heading circle.
The target-marker pass draws the three released v3 crosshair textures at their
native 64/128-pixel sizes. A separate bounded compass approximation supplies
the outer ring, exact north bar, and objective sprites; it does not reproduce
Steam's dynamic ring texture byte-for-byte.

The retained CircleMask is the released black-outside/transparent-centre layer
used to bound the portrait frames. The message bar uses Steam's native 120-pixel
pieces, bottom-centre anchors, `0x90000000` inner tint, and five-line layout.
This slice does not claim complete HUD behavior. Steam's full multi-stage mask
render state, other speakers and video portraits, general tactical contacts,
weapon selection, damage flashes, target prediction, influence-map battleline,
split-screen composition, and later mission HUD states remain absent. Because
Level 100 has a live influence map, the rebuild leaves the no-message
battleline interior empty rather than showing Steam's unrelated empty-map
Forseti fallback.
