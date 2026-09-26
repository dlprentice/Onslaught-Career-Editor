# init_D3DXMatrixMultiplyTranspose

Status: active static function note; identity proven 2026-09-26 (linked library code)
Last updated: 2026-09-26
Source File: unlabeled (first gates only; do not read this as
a pin of `CScriptObjectCode.cpp.md` / sibling
`FUN_00576b4d` / neighbour `FUN_00576bc7` /
already-pinned `FUN_00576b4d`)
||||||||||| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is a research label. This wake landed `34c0bc31`
FUN_00576b4d — not redone. Reviewer cycle 78 accepted
through `b36986c9`. Already-pinned
FUN_00576b4d / FUN_00576904 / `CScriptObjectCode.cpp.md`
were **not** rewritten. Did not adopt C1
`Push1InitJmpSlot656f40`.

> Address: `0x00576bba`

## Identity (RE record audit, 2026-09-26)

Proven: `init_D3DXMatrixMultiplyTranspose`. Linked library code: struct D3DXMATRIX * __stdcall init_D3DXMatrixMultiplyTranspose(struct D3DXMATRIX *, struct D3DXMATRIX const *, struct D3DXMATRIX const *), from the static library DirectX 9.0 SDK d3dx9.lib (SHA-256 a22ca24c92fd61912f7601f00a049f98a439763370726c724ce617020fa6526d), member obj\i386\d3dxmath.obj. The pristine bytes equal the library's object code apart from its relocation fields, and every relocation resolves consistently with the rest of the match (`tools/re_lib_match.py`; decision `relocations`). The Ghidra cohort `library-d3dx-20260926` applied the name ([Ghidra README](../../../../reverse-engineering/ghidra/README.md#re-audit-d3dx-library-names--september-26)). Everything below predates the identification: its byte facts stand, and the labels it quotes are the labels saved before that cohort.

## Contract

Not incoming-ECX `thiscall`. First insn `push 1`. Zero
stack args. No `ret`. Body `0x00576bba`–`0x00576bc6` is
13 bytes, SHA-256
`0a694b1852767265359be6653cdc58638a4c241041233152674c25f3d86f8007`.
One `E8`, zero `E9`. Neighbour table `FUN_00576bc7`
starts at `0x00576bc7` and is not claimed. Preceding
table `FUN_00576b4d` ends at `0x00576bb9` and is not
rewritten.

The body:

1. `push 1` / `E8` table
   `CFastVB__InitDispatchTableByCpuFeature`
   `0x0058926b`.
2. `jmp dword [0x00656f40]`.

That callee body and the runtime value of
`[0x00656f40]` are **not** this proof.

One body `E8` site: `0x00576bbc` `0x0058926b`.

Zero inbound `.text` `E8`/`E9`. One image encoding of
imm `ba 6b 57 00`: file `0x00256f40` / VA `0x00656f40`
in `.data` (the dword this body tails through;
neighbouring dwords are **not** this proof).

Cheapest falsifier: file `0x00176bba` is not `6a 01`,
**or** `0x00176bc1` is not `ff 25 40 6f 65 00`, **or**
`0x00176bbc` is not `e8 aa 26 01 00`, **or** body
SHA-256 is not `0a694b18…8007`, **or**
`tools/call_xref_scan.py` on `0x00576bba` is not
empty, **or** `0x00256f40` is not `ba 6b 57 00`,
**or** a second encoding of that imm exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00576bba` | `init_D3DXMatrixMultiplyTranspose` | `6a01 e8aa260100 ff25406f6500` (13 B) | not incoming-ECX; no ret; 13 B; 1 E8 / 0 E9; 0 inbound. HIGH on ABI, unique imm at `0x00656f40`, tail `jmp dword`. **Not** on the callee. |
