# CMixerMap__DestroySlot

Status: active static function note
Last updated: 2026-08-19
Source File: MixerMap.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup` after
`t_85668d63`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. `0x00549220` body is **not** this proof.

> Address: `0x00523210`

## Contract

`thiscall`. `ECX`→`ESI`. Zero stack args. One bare `ret` (`c3`) at
`0x0052322d`. Body `0x00523210`–`0x0052322d` is 30 bytes, SHA-256
`d21080cc346354829c5d9b6e9efa3541cea0b12e7a121703d6b9de4515420707`.
One `E8` (`0x00523220` → `0x00549220`), zero `E9`.

Zero inbound `.text` `E8`/`E9`. Image encodings of imm
`10 32 52 00` are exactly three, each a `push`:

| site | next |
| --- | --- |
| `0x00523273` | already-pinned Destroy → `0x0055db0a` |
| `0x005232d7` | same four-arg shape into `0x0055db0a` (inside Init) |
| `0x00523321` | `push 0x00523210` / `push 0x00523200` (Init; helper not claimed) |

If `[this+4]` is live: `push` it, `mov ecx, 0x009c3df0`,
`call 0x00549220`, then `[this+4] = 0`. Else skip to `pop esi` /
`ret`. `EAX` is not contracted. Authored names are **not** claimed.

Cheapest falsifier: file `0x00123210` is not
`56 8b f1 8b 46 04 85 c0`, **or** `0x0012322d` is not `c3`, **or**
body SHA-256 is not `d21080cc…0707`, **or**
`tools/call_xref_scan.py` on `0x00523210` is not `total: 0`, **or**
`0x00123273` is not `68 10 32 52 00`, **or** `0x0012321b` is not
`b9 f0 3d 9c 00`, **or** `0x00123225` is not
`c7 46 04 00 00 00 00`, **or** the image contains a fourth
`10 32 52 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00523210` | `CMixerMap__DestroySlot` | `568bf1 8b4604 85c0 7412 50 b9f03d9c00 e8fb5f0200 c7460400000000 5e c3` | thiscall; bare ret; 0 inbound E8/E9; three `push` sites; Free `[+4]` via `0x009c3df0` then store 0. HIGH on ABI, inbound-empty, those three pushes, that slot. **Not** on Free body or authored names. |
