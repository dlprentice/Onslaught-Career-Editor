# Released frontend assets

This directory owns the ignored, locally materialized retail inputs used by the
bounded startup → main menu → Level 100 → terminal-handoff path. Run
`npm run prepare:rebuild-assets` to verify a user-provided Steam installation
and reproduce these exact files. The payloads remain outside Git and release
packages and remain copyright of their respective rights holders;
`rebuild/LICENSE` covers reconstruction code only.

The path intentionally begins at the released click-to-start page. Steam's
`-skipfmv` path skips the startup movie but retains this page, so no startup,
briefing, or outro video is copied or simulated. New Game and Quit are the only
working main-menu actions. Continue, Load Game, Multiplayer, Goodies, and
Options remain visible but explicitly unavailable. Level select exposes only
`1.00 - Training Level` (world 100).

The current gameplay slice does not yet reach Level 100's full `LevelWon` or
`LevelLostString` conditions. The frontend therefore accepts only the
mission-owned `Level100MissionSnapshot` terminal handoff without inventing a
trigger, result vocabulary, or compositor. The mission/HUD owner is responsible
for the released in-game terminal overlay; the later CFEPDebriefing surface is
also outside this lane. Explicit retry constructs a
fresh deterministic Level 100 session, while Exit Level discards it and returns
to the bounded shell. There are no frontend result buttons or default result
selection.

## Materialized inputs

| Local file | Released source or derivation | SHA-256 |
| --- | --- | --- |
| `Backgrounds/click-to-start.texture.aya` | `FrontEnd%v2%fe_splash1.tga(0)A8R8G8B8.aya` | `46AB45168875B5B686E3534B3F66AB65B5A5B5512F697E5A98B03DD12708731A` |
| `Backgrounds/rock.texture.aya` | `FrontEnd%v2%FE_Rock_Background.tga(0)A8R8G8B8.aya` | `89213B441332F060ACDB3E55AA28C290FA0E530983C16A57B8CE1A7413E9E86D` |
| `title-logo.texture.aya` | `FrontEnd%v3%FE_BEA_Title2.tga(0)A8R8G8B8.aya` | `5AE9B300836D27BD13462A53E3455B649BB46BF8F48C8C326FD8F4F0C18C7EC7` |
| `title-bracket-01.texture.aya` | `FrontEnd%v3%FE_BEA_title_bracket01.tga(0)A8R8G8B8.aya` | `679B5FA6220B3EB54AEEF1D970890C35BE5DF264530226F5D08B22A63AD75064` |
| `title-bracket-02.texture.aya` | `FrontEnd%v3%FE_BEA_title_bracket02.tga(0)A8R8G8B8.aya` | `79F05E8C64B6E25F038C5B7C37DDADFD31EE9376E92FC5DA505B6C427ED9C74F` |
| `title-text-box.texture.aya` | `FrontEnd%v3%FE_BEA_title_text_box.tga(0)A8R8G8B8.aya` | `C007742E1FE9B93E988D198F8A2A4E741E546843FD36218D9015AB2EE6627B9C` |
| `symbol-bracket-01.texture.aya` | `FrontEnd%v3%FE_BEA_title_symbol_bracket01.tga(0)A8R8G8B8.aya` | `3243E641E9AD45CD8B80C4ABEBAA1E6F73B5ED774E0B4DBA1AFBCBBAF81A49A8` |
| `symbol-bracket-02.texture.aya` | `FrontEnd%v3%FE_BEA_title_symbol_bracket02.tga(0)A8R8G8B8.aya` | `92739AF94BEC154D898AFB5E59432694A789BB3F2C37242EB65272684DAEB687` |
| `Icons/new-game.texture.aya` | Released v3 New Game symbol | `D3FF62FBC8193E15BF250C82088F5088B17C667277DBB5FFF92F2980CC3DEB70` |
| `Icons/continue-game.texture.aya` | Released v3 Continue Game symbol | `83C9FA4D7E786AE4353D1F639C75B007BC0C65F1412B447D68967D9E5B4CCA0E` |
| `Icons/load-game.texture.aya` | Released v3 Load Game symbol | `9D1BB0D9EFC450FC2BCE244E01A2975468F07CF785BF6854A5BC9495FFFDC001` |
| `Icons/multiplayer.texture.aya` | Released v3 Multiplayer symbol | `8A7D7DBA563B153B314E04DAAAD4FFA2D0969B65A0603DE043027EAF5B4DF031` |
| `Icons/goodies.texture.aya` | Released v3 Goodies symbol | `EFA9EC1D2317E3CDF2ED9A90CC8B6CB391E6ED1099740DDAEB2C808B49F33358` |
| `Icons/options.texture.aya` | Released v3 Options symbol | `0824D66ACEC9DAD5037BE8BFC2B863201F94404D21795EAC4FAD82D8C4DA2ABA` |
| `Icons/quit.texture.aya` | Released v3 Quit symbol | `7096F573FF30302B5D5DAD8F56EBD633E51F2BD70613D5349B974DADA17B7A93` |
| `level-bracket-01.texture.aya` | Released v3 level-select bracket 1 | `560DB1621169C1B5787FC9C4691F4BEDE1AF292674F84D4D43BE11CA05166AA5` |
| `level-bracket-02.texture.aya` | Released v3 level-select bracket 2 | `7AD21E2A6E64F61998F7A43E92FE92D69AC013B169FD8107B648B1FA69877B27` |
| `level-ring-01.texture.aya` | Released v3 level-select ring 1 | `687EAF0945B701B622BDEBDE805E88CAC394734A4B4420155379993EF9F74E1C` |
| `level-ring-02.texture.aya` | Released v3 level-select ring 2 | `620900D34C153E722B6D78A9FBECAB2D69B8E81ABCDBDA084B0F90EB96142DFF` |
| `title-font.texture.aya` | `mustbe_TitleFont.tga(0)A8R8G8B8.aya` | `1941E28A5665665FB7F8F733E7A4854C60DEF33E1D4F1CB9CAA979BC204D0707` |
| `loading-screen.texture.aya` | `LoadingScreen.tga(0)X8R8G8B8.aya` | `E4AD32FEE41A31477E97D4F6F0B280F33C360756E3ABA27BF23746038443FC2C` |
| `SoundEffects/move.wav` | Exact 44.1 kHz PCM decode of XAP record 42, `Front End\N_FE_move`; consumed by the integrating audio lane, not this flow | `76B2458E9C5854DAF7237EA81B4F288AE09963BC10E7651E81E858FDB68CE83B` |
| `SoundEffects/select.wav` | Exact 44.1 kHz PCM decode of XAP record 43, `Front End\N_FE_select`; consumed by the integrating audio lane, not this flow | `F84144C80405FE9F745B8CF4BD352D7FA4F8C0A8BA481C770C2C7C0A9053ADE1` |
| `SoundEffects/back.wav` | Exact 44.1 kHz PCM decode of XAP record 41, `Front End\N_FE_back`; consumed by the integrating audio lane, not this flow | `133B78E813C6B393BE4DBA1D263F69513958B0AB827D6603F952D6E0A82BA02B` |
| `english.json` | Ten menu/launch and thirteen result/loss strings decoded from English `english.dat` SHA-256 `789ECFF619D077092769DF281C540D138A25FCC74D70023466A604888E59371A` | `417621F3CCC82F6B738D5D4F1C2C2A5D95984D88D82DB3846E8F073AED367C12` |

## Evidence boundary

- Steam Ghidra: startup handlers `0x0051B660`/`0x0051B6B0`, prompt render
  entry `0x0051B840`, main page vtable `0x005DBAE4`, level-select input/render
  `0x004606B0`/`0x00460B40`, loading renderer `0x0042C810`, and debrief
  vtable `0x005DB9C0` (`Initialize` `0x00456780`, `ButtonPressed`
  `0x004568A0`, `Process` `0x00456930`, `Render` `0x00456DD0`).
- Stuart source: `FrontEnd.cpp` establishes first-run intro, title return,
  debrief return, and initial selected world 100; `PCFrontend.cpp` names the
  move/select records; `game.cpp` establishes the distinct in-game result
  overlay. This lane does not compose that overlay or CFEPDebriefing.
- Shipped Level 100 `LevelScript.msl` defines four primary objectives,
  `LevelWon()`, and its only `LevelLostString(LOSE_TUTORIAL_BROKE)` reason.
- Startup/main/level placement, widescreen composition, and unavailable-item
  dimming are reconstruction-owned adaptations. The exact loading image and
  text are retained, but no exact layout, timing, control-hint, pixel-parity,
  terminal-overlay, or complete-debriefing claim is made.
