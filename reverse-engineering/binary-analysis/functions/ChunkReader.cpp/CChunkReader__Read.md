# CChunkReader__Read

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

> Address: `0x00423960`

## Contract

`thiscall`. `ECX` is this for the `[+8]` / `[+4]` loads. Three
stack dwords (`ret 0xc` at `0x0042398a`): dest, factor A, factor
B. Body `0x00423960`–`0x0042398c` is 45 bytes, SHA-256
`13db647b2a9c73143036aa35282131cdf777541b2aaa94cce3d92f8f19765843`.
One `E8` (`0x00548570`, table label `CDXMemBuffer__Read`), zero
`E9`.

`tools/call_xref_scan.py` reports 164 inbound `.text` `E8`, zero
`E9`. Already-pinned sites among them: `0x0047f7dc` (Load
`0x13dc` overlay), `0x005231ad` / `0x005231f0` (InitSlot),
`0x005233a5` (Init `0x40000` at mixer`[+4]`). The other 160 are
**not** listed.

`ESI = A * B`. Then `[this+8] += ESI`, `ECX = [this+4]`,
`push ESI` / `push dest` / `call 0x00548570`. `EAX` is 1 iff that
call's `EAX` equals `ESI`, else 0. Authored names are **not**
claimed.

Cheapest falsifier: file `0x00023960` is not
`56 8b 74 24 0c 0f af 74 24 10`, **or** `0x0002398a` is not
`c2 0c 00`, **or** body SHA-256 is not `13db647b…5843`, **or**
`tools/call_xref_scan.py` on `0x00423960` is not `total: 164` all
`E8`, **or** `0x00023974` is not `89 51 08`, **or** `0x0002397b`
is not `e8 f0 4b 12 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00423960` | `CChunkReader__Read` | `56 8b74240c 0faf742410 8b5108 … 895108 8b4904 e8f04b1200 … c20c00` | thiscall; ret 0xc; EAX in {0,1}; size=`A*B`; `[+8]+=size`; stream this=`[+4]`; 164 inbound E8. HIGH on ABI, inbound count, those two slots, EAX polarity. **Not** on the 160 unlist inbound or authored names. |
