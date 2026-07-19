# First-person HUD assets

These are the exact released PC HUD textures consumed by the current Level 100
first-person slice. The project owner has permission to use, modify, and
distribute the original game assets. They remain copyright of their original
rights holders; `rebuild/LICENSE` covers reconstruction code and does not
relicense the assets.

The source files came from the released game's `data/resources/dxtntextures`
directory. Their names are direct literals in the canonical Steam executable,
and a clean app-owned Level 100 run establishes the opening composition:
central weapon/crosshair layers, lower-left radar, lower-right radio view, and
the lower-center message/objective treatment.

| Curated file | Released source name | SHA-256 |
| --- | --- | --- |
| `crosshair-outline.texture.aya` | `hud%Crosshair Outline.tga(0)A8R8G8B8.aya` | `1E27B9771F3D0416C07EFF9AEDE6863CA6F081386C86259F635E3D9A02ADE5B2` |
| `circle-darkener.texture.aya` | `hud%v2%CircleDarkener.tga(0)A8R8G8B8.aya` | `7BD18594757165DCDD8DADB618EA99EB500ED105DBE2D6A6F66BBCBC31C323A3` |
| `radar-outline.texture.aya` | `hud%v2%RadarOutline.tga(0)X8R8G8B8.aya` | `507D465248F7321F2332413B2C6F461F3B3C45D87C52D86C38C43104043D7DC7` |
| `radio-view.texture.aya` | `hud%v2%RadioView.tga(0)A8R8G8B8.aya` | `888D5A70AB812E23F75DB76AB2ED71CD2CCE04191EE282D525C86E337CC01778` |
| `weapon-fill.texture.aya` | `hud%v2%WeaponFill.tga(0)A8R8G8B8.aya` | `E639910D70AE10B044423CD5025C300C61CB8A9B5765890FD1A011C7D4499C0D` |
| `weapon-outline.texture.aya` | `hud%v2%WeaponOutline.tga(0)X8R8G8B8.aya` | `2E2DA786DB82C8FD76DE36D8D71FE744DDDDD364247467CBA1BFB9A95E52D62B` |
| `objective-inner-centre.texture.aya` | `hud%v2%ObjectiveInnerCentre.tga(0)A8R8G8B8.aya` | `FC42774E8C4F4534B65009807BFDB333443A9F5202C6A2C59DFF0DDDBED4F55B` |
| `objective-inner-left.texture.aya` | `hud%v2%ObjectiveInnerLeft.tga(0)A8R8G8B8.aya` | `70030AACE505E8E3D7F56DDE0B9C6A929F3D2C61912FC03AC816746B6D8A96BD` |
| `objective-inner-right.texture.aya` | `hud%v2%ObjectiveInnerRight.tga(0)A8R8G8B8.aya` | `7C85B0293FC7A524978A21E7CDC06B1DD3308E9A595AADCA054B51CD9A6AA113` |
| `objective-left.texture.aya` | `hud%v2%ObjectiveLeft.tga(0)A8R8G8B8.aya` | `0AE835780D1AF6C01F0272A50AFDA141ABCA70EAA5C23D74E7FC3968B6D9194F` |
| `objective-right.texture.aya` | `hud%v2%ObjectiveRight.tga(0)A8R8G8B8.aya` | `581F10446DB76ECE7AA7044B4C02F0431A79A7D606225D5C69A412C17F85078B` |
| `font-13ps.texture.aya` | `mustbe_Font13PS.tga(0)A8R8G8B8.aya` | `7ACC088B75E729CBDC2782E239A7D18BA0EC409E1BC890109AA1020F5EE81DC0` |
| `tatiana-portrait.texture.aya` | `MessageBox%tat_aa.tga(0)A8R8G8B8.aya` | `34D451A6FC31E399B99032230413A60F146B41A0FEA65E61561A37D8EC757CFD` |
| `technician-portrait.texture.aya` | `MessageBox%technic_aa.tga(0)A8R8G8B8.aya` | `C4C1B11F4DDFB960AFC1C1D2A04020FADF997795ECCF651C07314141652F9603` |

The renderer uses the source alpha for DXT2 layers and additive composition for
the two X8 outline layers, matching their visible black-background sprite
semantics. The 256×256 uncompressed Font13PS atlas contains the fixed 16×16
ASCII cells used for the current objective line. The two 128×128 DXT2 portraits
are the exact released static `aa` frames selected for Tatiana's and the
technician's opening messages; no lip movement is synthesized.

This slice does not claim complete HUD behavior. Animated portrait/video frames,
tactical contacts, weapon selection, damage states, target prediction,
battleline rendering, split-screen composition, and later tutorial/mission HUD
states remain absent.
