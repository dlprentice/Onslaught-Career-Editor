# FUN_00598bdc

Status: active static function note
Last updated: 2026-08-19
Source File: unlabeled (first gates only; do not read this as
a pin of `CScriptObjectCode.cpp.md` / sibling
`FUN_00598b08` / neighbour `FUN_00598c85` /
already-pinned `FUN_00598b08`)
|||||||||||| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is a research label. This wake landed `9b3189bc`
FUN_00598b08 — not redone. Reviewer cycle 86 accepted
through `8082f221`. Already-pinned
FUN_00598b08 / FUN_00598ac8 / `CScriptObjectCode.cpp.md`
were **not** rewritten. Named
`CFastVB__InitNodeType10` /
`CFastVB__NodeType10_dtor` were skipped as labeled.
Did not adopt C1 `FormatThenFiveMatchThenRepeCmpsb`.

> Address: `0x00598bdc`

## Contract

Incoming-ECX `thiscall`. First insn `push esi`. One
stack dword (`ret 0x4` at `0x00598c82`). Body
`0x00598bdc`–`0x00598c84` is 169 bytes, SHA-256
`7b8b832d39f287ac8e9d59c9e45466ecb029fd46aaf6af1bc16df9f61a439c93`.
Six `E8`, zero `E9`. Neighbour table `FUN_00598c85`
starts at `0x00598c85` and is not claimed. Preceding
table `CFastVB__NodeType10_dtor` ends at
`0x00598bdb` and is not rewritten.

The body:

1. `push esi` / `push edi` / `EDI = [esp+0xc]` /
   `mov esi, ecx`.
2. Six `E8` sites: first `0x00598be5` → table
   `CTexture__HasSameFormatClassId` `0x00598749`;
   five later sites → table
   `CTexture__NodePayloadMatchesTypeOrNullIsZero`
   `0x0059877f`.
3. `ret 0x4`.

Those field meanings and the callee bodies are **not**
this proof.

Zero inbound `.text` `E8`/`E9`. One image encoding of
imm `dc 8b 59 00`: file `0x001ef264` / VA `0x005ef264`
(neighbouring dwords are **not** this proof).

Cheapest falsifier: file `0x00198bdc` is not `56`,
**or** `0x00198c82` is not `c2 04 00`, **or**
`0x00198be5` is not `e8 5f fb ff ff`, **or**
`0x00198c24` is not `e8 56 fb ff ff`, **or** body
SHA-256 is not `7b8b832d…9c93`, **or**
`tools/call_xref_scan.py` on `0x00598bdc` is not
empty, **or** `0x001ef264` is not `dc 8b 59 00`,
**or** a second encoding of that imm exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00598bdc` | `FUN_00598bdc` | `56 57 8b7c240c 8bf1 e85ffbffff … e856fbffff … c20400` (169 B) | incoming-ECX thiscall; ret 0x4; 169 B; 6 E8 `CTexture__HasSameFormatClassId` + 5× `CTexture__NodePayloadMatchesTypeOrNullIsZero` / 0 E9; 0 inbound. HIGH on ABI, unique imm at `0x005ef264`. **Not** on field meaning or the callees. |
