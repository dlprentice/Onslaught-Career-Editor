# CChunkReader__Read

Status: active static function note
Last updated: 2026-08-27
Source File: `references/Onslaught/chunker.cpp`, SHA-256
`3eb76bf2628c4c4aeaa8ce32a33a06ecc5dc3c8cb47d5528acea641f530c6135`
| Binary: BEA.exe, SHA-256
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
call's `EAX` equals `ESI`, else 0. The Stuart source independently
identifies the class, method, fields (`ReadSinceChunk` and `pFile`),
and exact-length Boolean return contract.

Cheapest falsifier: file `0x00023960` is not
`56 8b 74 24 0c 0f af 74 24 10`, **or** `0x0002398a` is not
`c2 0c 00`, **or** body SHA-256 is not `13db647b…5843`, **or**
`tools/call_xref_scan.py` on `0x00423960` is not `total: 164` all
`E8`, **or** `0x00023974` is not `89 51 08`, **or** `0x0002397b`
is not `e8 f0 4b 12 00`.

## PS2 correspondence

The released PS2 executables retain the same source-level contract. Each body
was independently streamed from its named pristine image/archive on
2026-08-27; relocation-normalized instruction streams share SHA-256
`e888405e22a9847257b5bf3de2e943bd60a6beb34db9118747520684263209e9`.

| Build | Virtual range | Bytes | Raw body SHA-256 |
| --- | --- | ---: | --- |
| Official demo | `[0x00131fb0,0x00131ff8)` | 72 | `3b931164dbce68a1d3cfdf41baf74dcf242b858d388c6c5582ff533307c1d0a6f` |
| Europe retail | `[0x00131fb0,0x00131ff8)` | 72 | `128da49b47bd3b136ce52bfb1720a2b4384bcecec645e80eff066220a64470ae9` |
| USA retail | `[0x00132100,0x00132148)` | 72 | `39f38eb1fa293bc942dfed2bca0bef20fd457f0f7d61645b72ee99fa425522d2` |

All three multiply `size * count`, add that byte count to
`ReadSinceChunk` before issuing the read, and return true only when the
underlying read supplies exactly that many bytes. The released bodies omit the
source build's diagnostic `ASSERT` without changing the data or return
contract.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00423960` | `CChunkReader__Read` | `56 8b74240c 0faf742410 8b5108 … 895108 8b4904 e8f04b1200 … c20c00` | thiscall; ret 0xc; EAX in {0,1}; size=`A*B`; `[+8]+=size`; stream this=`[+4]`; 164 inbound E8. HIGH on ABI, inbound count, those two slots, EAX polarity. **Not** on the 160 unlist inbound or authored names. |
