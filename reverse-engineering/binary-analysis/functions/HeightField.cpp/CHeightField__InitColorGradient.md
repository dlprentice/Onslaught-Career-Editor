# CHeightField__InitColorGradient

Status: active static function note
Last updated: 2026-08-19
Source File: HeightField.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` after
`t_a5b7e97a`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Wave394 `xShift` / `colorMod` / `fog` names are **not** this
proof.

> Address: `0x0047e8e0`

## Contract

`thiscall`. Zero stack args. `ECX`→`ESI`. `EDX` is not live-in
(`mov edx, 1` at `0x0047e8f4`). One bare `ret` (`c3`) at
`0x0047ea18`. EAX is the last copied dword from `[this+0x13cc]`;
treat as void. Body `0x0047e8e0`–`0x0047ea18` is 313 bytes, SHA-256
`8ab3e564d7011b4796d48d1146f37bb87899000de865a1d5edb6c1069265e022`.
Zero instruction-aligned `E8`, zero `E9`.

One inbound `.text` `E8`, zero `E9`: `0x0047f7ea` inside
`CHeightField__Load`. File `0x0007f7e8` is `8b cf e8 f1 f0 ff ff`
(`mov ecx, edi` / `call`). Load's `EDI` is the already-pinned BSS
this `0x006fadc8`.

Reads (offsets only): `[+0x1038]`, `[+0x103c]`, `[+0x108c]`,
`[+0x107c]`.

Writes (offsets only):

| slot | bytes |
| --- | --- |
| `[+0x10bc]` | `1 << [+0x1038]` |
| `[+0x10c4]` | `[+0x10bc] - 1` |
| `[+0x10c0]` | `1 << [+0x103c]` |
| `[+0x10c8]` | `[+0x10c0] - 1` |
| `[+0x10cc]` | `[+0x10c8] << [+0x1038]` |
| `[+0x10d0]` … `[+0x13cc]` | 0x40 triples, stride `0x0c` |
| `[+0x13d0]` / `[+0x13d4]` / `[+0x13d8]` | copy of the last triple |

Trip count is the immediate `0x40` at `0x0047e965`. After the loop,
`add esi, 0x13d0` at `0x0047e9fb` then copies the last triple.
Authored color / fog / dimension names are **not** claimed.

Cheapest falsifier: file `0x0007e8e0` is not `83 ec 0c 53 55 56 8b f1 57`,
**or** `0x0007ea18` is not `c3`, **or** body SHA-256 is not
`8ab3e564…e022`, **or** `tools/call_xref_scan.py` on `0x0047e8e0` is
not exactly `E8` at `0x0047f7ea`, **or** `0x0007f7e8` is not
`8b cf e8 f1 f0 ff ff`, **or** `0x0007e965` is not
`c7 44 24 10 40 00 00 00`, **or** `0x0007e9fb` is not
`81 c6 d0 13 00 00`, **or** `0x0007e911` is not `89 86 bc 10 00 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0047e8e0` | `CHeightField__InitColorGradient` | `83ec0c 535556 8bf1 57 … 8986bc100000 … c744241040000000 … c3` | thiscall; bare ret; 0 E8/E9; 1 inbound Load `mov ecx,edi`; writes `1<<` into `+0x10bc`/`+0x10c0` and 0x40 triples at `+0x10d0`. HIGH on ABI, inbound, those stores. **Not** on authored names. |
