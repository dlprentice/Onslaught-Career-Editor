# CHeightField__DeserializeMapAndInitResources

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Wave / A06 / terrain-shade text is **not** this proof.

> Address: `0x00491060`

## Contract

`thiscall`. One stack arg (chunk reader). `ECX`→`ESI`. The arg is
loaded after two pushes as `[esp+0x30]` → `EDI`. One `ret 4`
(`c2 04 00`) at `0x00491153`. Body `0x00491060`–`0x00491155` is 246
bytes, SHA-256
`7377f161771bebefd54a56f3360b7d57a178dbff7f2a1a4aba9be07e385bd192`.
Thirteen `E8`, zero `E9`.

One inbound `.text` `E8`, zero `E9`: `0x0044a72f` inside
`CEngine__Deserialize` (`0x0044a6e0`–`0x0044a739`):

```
pop  edi
push ebx
mov  ecx, 0x006fadc8
call 0x00491060
```

So this is the already-pinned BSS this. File `0x0004a72a` is
`b9 c8 ad 6f 00 e8 2c 69 04 00`.

Shipped strings (quoted, not authored names):

| VA | bytes |
| --- | --- |
| `0x0062da84` | `Deserializing map` |
| `0x0062da6c` | `Deserializing map %d\n` |

Order:

1. `push 0x0062da84` / `mov ecx, 0x00663498` / `call 0x0042b500`
   (table label `CConsole__Status`).
2. `ecx = edi` / `call 0x00423910` (table label
   `CChunkReader__GetNext`). Body not claimed.
3. `CChunkReader__Read` (`0x00423960`) copies 4 bytes (`push 1; push 4;
   dest = first local`) from the reader. That dword is `sprintf`'d
   (`0x0055de9b`) with `Deserializing map %d\n` and
   `DebugTrace` (`0x0040c640`) prints the buffer. After Trace returns
   and before `add esp, 4`, `[esp+0xc]` is still that dword;
   `[this+0x93dc] =` it.
4. `[this+0x93e4] = 1` then `[this+0x93e0] = 1`.
5. `push edi` / `ecx = esi` / `call 0x0047f750`
   (`CHeightField__Load`). Load first gates stay on that note.
6. `push edi` / `mov ecx, 0x0089bd80` / `call 0x005232b0`
   (table label `CMixerMap__Init`). Body not claimed.
7. Overlay bytes, after Load, forwarded as one stack byte each:

   | src | this | call |
   | --- | --- | --- |
   | `[this+0x1090]` | `0x0089c9a0` | `0x0044a2a0` |
   | `[this+0x1091]` | `0x0089c9a0` | `0x00452b60` (`c2 04 00`; the byte is discarded) |
   | `[this+0x1030]` | `0x0089c9a0` | `0x0044a1f0` |
   | `[this+0x1094]` | cdecl | `0x0048dec0` then `add esp, 4` |
   | `[this+0x1095]` | `0x0089c9a0` | `0x0044a2c0` |

8. `push 1` / `push 0x0062da84` / `mov ecx, 0x00663498` /
   `call 0x0042b800` (table label `CConsole__StatusDone`).

`+0x93dc` / `+0x93e0` / `+0x93e4` sit **past** the 0x13dc Load
overlay. Authored names for those slots, the 4-byte dword, the mixer
object, and the `0x0089c9a0` helpers are **not** claimed.

Cheapest falsifier: file `0x00091060` is not `83 ec 24 56 8b f1 57`,
**or** `0x00091153` is not `c2 04 00`, **or** body SHA-256 is not
`7377f161…d192`, **or** `tools/call_xref_scan.py` on `0x00491060` is
not exactly `E8` at `0x0044a72f`, **or** `0x0004a72a` is not
`b9 c8 ad 6f 00 e8 2c 69 04 00`, **or** `0x0009109a` is not
`68 6c da 62 00`, **or** `0x000910b9` is not `89 8e dc 93 00 00`,
**or** `0x000910d6` is not `e8 75 e6 fe ff`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00491060` | `CHeightField__DeserializeMapAndInitResources` | `83ec24 56 8bf1 57 6884da6200 … 8986dc930000 … e875e6feff … c20400` | thiscall; ret 4; this=`0x006fadc8`; dword → `+0x93dc`; flags `+0x93e0`/`+0x93e4`=1; then Load. HIGH on ABI, inbound, strings, those three stores, Load site. **Not** on authored names or callee bodies. |
