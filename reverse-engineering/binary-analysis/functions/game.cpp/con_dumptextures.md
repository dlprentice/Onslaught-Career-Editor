# con_dumptextures

> Address: 0x0046bea0 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes (free function)
- **Signature Set:** Yes
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:109`)

## Purpose

Console command: `DumpTextures` dumps dynamic/interesting textures to disk.

## Notes (Binary Evidence)

- Prints `Dumping textures to TextureDump directory...\n` (`0x0062bb2c`).
- Calls `CTEXTURE::DumpInterestingTextures()` at `0x00558870`.
- Prints `...done!\n` (`0x00625304`).

## Related

- Registered in `CGame::InitRestartLoop()` (`CGame__InitRestartLoop`, `0x0046c430`):
  - Name `DumpTextures` at `0x0062be24`
  - Description `Dumps all the dynamic textures to disc` at `0x0062be34`
