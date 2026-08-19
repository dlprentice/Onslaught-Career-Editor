# CChunkReader__GetNext

Status: active static function note
Last updated: 2026-08-19
Source File: ChunkReader.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. `0x00548570` body is **not** this proof.

> Address: `0x00423910`

## Contract

`thiscall`. `ECX`→`ESI`. Zero stack args. Two bare `ret` (`c3`) at
`0x00423933` (short first read) and `0x00423950`. Body
`0x00423910`–`0x00423950` is 65 bytes, SHA-256
`341f30201e4e65fa758a3a8cd664409d9384e71803663781a36c929c801529bb`.
Two `E8`, both `0x00548570` (table label `CDXMemBuffer__Read`),
zero `E9`.

`tools/call_xref_scan.py` reports 107 inbound `.text` `E8`, zero
`E9`. Already-pinned mixer sites among them:
`0x0052319a` / `0x005231a1` / `0x005231bb` (InitSlot) and
`0x00523373` / `0x00523393` (Init). The other 102 are **not**
listed.

`[this+8] = 0`. Then `ECX = [this+4]`, read 4 bytes into a scratch
dword. If that call returns `< 4`: `EAX = 0`. Else a second 4-byte
read onto `this` itself; `EAX` is that dword, forced to 0 when the
second call returns `< 4`. Authored tag names are **not** claimed.

Cheapest falsifier: file `0x00023910` is not
`51 56 8b f1 8d 44 24 04 6a 04`, **or** `0x00023950` is not `c3`,
**or** body SHA-256 is not `341f3020…29bb`, **or**
`tools/call_xref_scan.py` on `0x00423910` is not `total: 107` all
`E8`, **or** `0x0002391e` is not `c7 46 08 00 00 00 00`, **or**
`0x00023925` is not `e8 46 4c 12 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00423910` | `CChunkReader__GetNext` | `5156 8bf1 … c7460800000000 e8464c1200 … 0f9cc1 49 23c1 59 c3` | thiscall; bare ret ×2; EAX 0 or 4-byte tag; `[+8]=0`; stream this=`[+4]`; 107 inbound E8. HIGH on ABI, both rets, those two slots, both E8 targets, inbound count. **Not** on the 102 unlist inbound or tag names. |
