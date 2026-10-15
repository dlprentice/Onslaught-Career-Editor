# CLandscapeTexture__UpdateTileRange

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp / LandscapeTexture.cpp (absent from the
pinned GPL `references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` after
`t_35528622`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Tile / lighting algebra and callee bodies are **not** this
proof.

> Address: `0x0048ef00`

## Contract

`thiscall`. `ECX`→`EDI` at `0x0048ef16` (`8b f9`). Four stack
dwords (`ret 0x10` at `0x0048f152`). After `sub esp, 0x38` they
sit at `[esp+0x3c]` / `[esp+0x40]` / `[esp+0x44]` / `[esp+0x48]`.
Body `0x0048ef00`–`0x0048f17c` is 637 bytes, SHA-256
`0dd0d0d26c1b8b093b02831be28830959d18b33a69d54c7551af2d570f708a0a`.
Three instruction-aligned `E8`, two internal `E9` that bounce back
from cold tails after the `ret`. One `ret`. `EAX` is not
contracted. Three `90` after the last `jmp` are outside the body
hash.

Three inbound `.text` `E8`, zero `E9`:

| site | file bytes | this plant |
| --- | --- | --- |
| `0x0048e65e` | `6a 3f 6a 3f 6a 00 6a 00 8b ce e8 9d 08 00 00` | `mov ecx, esi` (Reset) |
| `0x0048f1af` | `6a 3f 6a 3f 6a 00 6a 00 e8 4c fd ff ff` | entry `ECX` of neighbour `0x0048f180` |
| `0x005475bf` | `8b 49 30 56 53 50 52 e8 3c 79 f4 ff` | `[caller_ecx+0x30]` |

Do not collapse those to one BSS object. Caller bodies are **not**
claimed. File offsets are `0x0008e654` / `0x0008f1a7` /
`0x001475b8`.

This-reads only: `+8`, `+0x30`, `+0x34`. **No** this-write. The
already-pinned blit plant is `0x0048f018`
`b9 c8 ad 6f 00 e8 ce ff fe ff` (`mov ecx, 0x006fadc8` /
`call 0x0047eff0`). Other `E8` dests are `0x0048ee00` and
`0x0048e950`. Callee bodies stay on their own notes. A raw `E9`
byte at `0x0048efcc` is the ModRM of `sub ebp, ecx` (`2b e9`);
Capstone does not agree it is a jmp.

Cheapest falsifier: file `0x0008ef00` is not
`83 ec 38 8b 44 24 3c`, **or** `0x0008f152` is not `c2 10 00`,
**or** `0x0008f178` is not `e9 05 fe ff ff`, **or** body SHA-256
is not `0dd0d0d2…8a0a`, **or** `tools/call_xref_scan.py` on
`0x0048ef00` is not exactly `E8` at `0x0048e65e` / `0x0048f1af` /
`0x005475bf`, **or** `0x0008e654` is not
`6a 3f 6a 3f 6a 00 6a 00 8b ce e8 9d 08 00 00`, **or**
`0x0008f1a7` is not `6a 3f 6a 3f 6a 00 6a 00 e8 4c fd ff ff`,
**or** `0x001475b8` is not `8b 49 30 56 53 50 52 e8 3c 79 f4 ff`,
**or** `0x0008ef16` is not `8b f9`, **or** `0x0008f018` is not
`b9 c8 ad 6f 00 e8 ce ff fe ff`, **or** `0x0008efcb` is not
`2b e9`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0048ef00` | `CLandscapeTexture__UpdateTileRange` | `83ec38 8b44243c … 8bf9 … b9c8ad6f00 e8cefffefe … c21000 … e905feffff` | thiscall; ret 0x10; 637 B; 3 E8 / 2 internal E9; 3 inbound; no this-write; blit plant `mov ecx,0x006fadc8`. HIGH on ABI, inbound set, those three slots, that plant. **Not** on tile algebra, authored names, or callee bodies. |
