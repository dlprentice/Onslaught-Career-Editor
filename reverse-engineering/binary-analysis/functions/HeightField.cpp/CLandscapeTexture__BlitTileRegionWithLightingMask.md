# CLandscapeTexture__BlitTileRegionWithLightingMask

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Tile / 8.8 lighting algebra is **not** this proof.

> Address: `0x0047eff0`

## Contract

`thiscall`. Parks `ECX` at `[esp+0x10]` after one `push ebx`
(`89 4c 24 10` at `0x0047effe`). Ten stack dwords (`ret 0x28` at
`0x0047f741`). Body `0x0047eff0`–`0x0047f743` is 1876 bytes,
SHA-256
`49b182175aa80f17fbd510b389f66d4d1fd7bf316b41039bbb27bf93ec1fd0b0`.
Zero instruction-aligned `E8`. Two `E9`, both internal
(`0x0047f3ec` → `0x0047f346`, `0x0047f5f1` → `0x0047f69c`). One
`ret`.

Three inbound `.text` `E8`, zero `E9`. Every site loads the
already-pinned BSS this first:

```
mov  ecx, 0x006fadc8
call 0x0047eff0
```

| site | owner (table label) | file bytes |
| --- | --- | --- |
| `0x0048eb5e` | `CLandscapeTexture__UpdateTile` | `b9 c8 ad 6f 00 e8 8d 04 ff ff` |
| `0x0048ecee` | `CLandscapeTexture__UpdateTile` | `b9 c8 ad 6f 00 e8 fd 02 ff ff` |
| `0x0048f01d` | `CLandscapeTexture__UpdateTileRange` | `b9 c8 ad 6f 00 e8 ce ff fe ff` |

Caller bodies are **not** claimed. After the later `push ebp` /
`push esi` / `push edi`, the parked this is `[esp+0x1c]`.

Last unclaimed image encoding of imm `80 bd 89 00` is this body's
load at `0x0047f0db` (`8b 15 80 bd 89 00`). Then
`lea eax, [ecx+ecx*4]` / `lea eax, [edx+eax*4]` (stride `0x14`)
and `mov eax, [eax+4]`. Image encodings of imm `84 bd 89 00` are
exactly one: `0x0047f170` (`8b 0d 84 bd 89 00`). Those two
absolute this slots are the mixer dword already zeroed by
`FUN_00523180` and its `+4` plane pointer.

Parked this is the object for the already-pinned gradient:
`mov ecx, [esp+0x1c]` then `[ecx+edx*4+0x10d8]` /
`[ecx+edx*4+0x10d0]` at `0x0047f579` / `0x0047f581` and again at
`0x0047f63f` / `0x0047f647`. Lighting formula is **not** claimed.

Cheapest falsifier: file `0x0007eff0` is not
`81 ec 80 00 00 00 8b 84 24 88 00 00 00 53 89 4c 24 10`, **or**
`0x0007f741` is not `c2 28 00`, **or** body SHA-256 is not
`49b18217…d0b0`, **or** `tools/call_xref_scan.py` on `0x0047eff0`
is not exactly `E8` at `0x0048eb5e` / `0x0048ecee` / `0x0048f01d`,
**or** those three sites are not `b9 c8 ad 6f 00 e8 …`, **or**
`0x0007f0db` is not `8b 15 80 bd 89 00`, **or** `0x0007f170` is
not `8b 0d 84 bd 89 00`, **or** the image contains a second
`84 bd 89 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0047eff0` | `CLandscapeTexture__BlitTileRegionWithLightingMask` | `81ec80000000 … 894c2410 … 8b1580bd8900 … 8b0d84bd8900 … 8b4c241c … d8100000 … c22800` | thiscall; ret 0x28; 0 E8 / 2 internal E9; 3 inbound `mov ecx,0x006fadc8`; mixer `[0x0089bd80]` + unique `[0x0089bd84]`; parked this `+0x10d0`/`+0x10d8`. HIGH on ABI, inbound set, those two abs loads, those two gradient slots. **Not** on tile algebra or authored names. |
