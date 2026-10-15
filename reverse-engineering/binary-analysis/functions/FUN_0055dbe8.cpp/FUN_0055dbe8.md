# FUN_0055dbe8

Status: active static function note
Last updated: 2026-08-19
Source File: unlabeled (first gates only; do not read this as
a pin of `CScriptObjectCode.cpp.md` / sibling `_rand`
/ table `CDXTexture__InvokeTlsCleanupCallbackAndFinalize`
/ already-pinned `FUN_0055b0d0`)
||||||||| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is a research label. This wake landed `19c6e435`
FUN_0055b0d0 — not redone. Reviewer cycle 69 accepted
through `2777aef4` — not redone. Already-pinned
FUN_0055b0d0 / FUN_0055b0b0 / `CScriptObjectCode.cpp.md`
were **not** rewritten. Did not adopt C1
`CxxEhFilter`.

> Address: `0x0055dbe8`

## Contract

Not incoming-ECX `thiscall`. First insn
`mov eax, dword [esp+4]`. One stack arg. One bare `ret`
(`0x0055dbf8`). Body `0x0055dbe8`–`0x0055dbfd` is 22 bytes,
SHA-256
`9d553e507340a030bb4097bb4cd854c224de655d8c42af1c588ff4f7fc12ddb0`.
Zero `E8`, one `E9`. Neighbour `_rand` starts at
`0x0055dbfe` and is not claimed.

The body:

1. Loads `[esp+4]` then `[[esp+4]]` into `EAX`.
2. `cmp dword [eax], 0xe06d7363`.
3. If unequal: `xor eax, eax` / bare `ret`.
4. If equal: `E9` table
   `CDXTexture__InvokeTlsCleanupCallbackAndFinalize`
   `0x00560bfa` (not claimed).

`EAX` on the mismatch path is `0`. The `0x00560bfa` body
and the meaning of `0xe06d7363` as a named exception code
are **not** this proof.

Two inbound `.text` `E8`: `0x0055dbc9` (inside table
`eh_vector_destructor_iterator`, `push [ebp-0x14]` then
`call` / `pop ecx`) and `0x00560691` (inside table
`CRT__SehUnwindToTargetState`, same `push [ebp-0x14]` /
`call` / `pop ecx` / `ret`). Those caller bodies are
cited, not claimed. Zero inbound `E9`.

The four-byte sequence `e8 db 55 00` also occurs at
`0x005588bb` as the start of `e8 db 55 00 00` (`call`
`0x0055de9b` inside table
`CDXTexture__DumpAllTexturesToTga`). That is **not** an
encoding of this function's address.

Cheapest falsifier: file `0x0015dbe8` is not `8b 44 24 04`,
**or** `0x0015dbf8` is not `c3`, **or** `0x0015dbee` is not
`81 38 63 73 6d e0`, **or** `0x0015dbf9` is not
`e9 fc 2f 00 00`, **or** body SHA-256 is not
`9d553e50…ddb0`, **or** `tools/call_xref_scan.py` on
`0x0055dbe8` is not exactly the two `E8` sites above.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0055dbe8` | `FUN_0055dbe8` | `8b442404 8b00 813863736de0 7403 33c0 c3 e9fc2f0000` | not incoming-ECX; 1 stack arg; bare ret ×1; 22 B; 0 E8 / 1 E9 table `CDXTexture__InvokeTlsCleanupCallbackAndFinalize`; 2 inbound E8. HIGH on ABI, compare imm, inbound sites. **Not** on `0x00560bfa` or `_rand`. |
