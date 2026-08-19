# CScriptObjectCode__Reset

Status: active static function note
Last updated: 2026-08-19
Source File: MissionScript / CScriptObjectCode (first gates
only; do not read this as a pin of `CScriptObjectCode.cpp.md`)
| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is a research label. Already-pinned `ClearStack` /
`CScriptObjectCode.cpp.md` / the IScript wrapper folders
were **not** written.

> Address: `0x00539980`

## Contract

`thiscall`. First insn `add ecx, 0xc` then `jmp`
already-pinned `CScriptObjectCode__ClearStack`
`0x005393e0` (`0x00539983`). Zero stack args. No `ret`
of its own. Body `0x00539980`–`0x00539987` is 8 bytes,
SHA-256
`9c0cf18a25557f21b80f654b7f85978d590f2903cbd3a6e46847bd4d704cbfc9`.
Zero `E8`, one `E9`. Eight `nop`s after the jmp are
**not** in the body (already-pinned neighbour
`CScriptObjectCode__CallEvent` starts at `0x00539990`).

Incoming ECX is the VM; the tail is
`ClearStack(this+0xc)`. That callee body is **not**
re-proven here.

Twelve inbound `.text` sites (8 `E8` + 4 `E9`), zero
image encodings of imm `80 99 53 00`:

`0x0046caa7` `0x00533514` `0x005335ae` `0x00533633`
`0x0053366e` `0x00533791` `0x005337ee` `0x0053381e`
`0x0053388b` `0x00538561` `0x0053861c` `0x0053867f`.

Already-pinned fire-path wrappers among those:
`0x00533514` CallEvent0, `0x005335ae` Id6, `0x00533633`
CreateThingRef, `0x0053366e` Id5, `0x00533791`
CreateThingRefWithSquad, `0x005337ee` Id3, `0x0053381e`
VFunc_2, `0x0053388b` RestoreSavedState. The remaining
four hosts are **not** claimed.

Cheapest falsifier: file `0x00139980` is not `83 c1 0c`,
**or** `0x00139983` is not `e9 58 fa ff ff`, **or** body
SHA-256 is not `9c0cf18a…bfc9`, **or**
`tools/call_xref_scan.py` on `0x00539980` is not the
twelve sites above, **or** a thirteenth inbound `E8`/`E9`
exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00539980` | `CScriptObjectCode__Reset` | `83c10c e958faffff` | thiscall tail; 8 B; 0 E8 / 1 E9 ClearStack; 12 inbound (8 E8 + 4 E9). HIGH on ABI, inbound set, `ecx+=0xc` then ClearStack. **Not** on ClearStack internals or the four unpinned hosts. |
