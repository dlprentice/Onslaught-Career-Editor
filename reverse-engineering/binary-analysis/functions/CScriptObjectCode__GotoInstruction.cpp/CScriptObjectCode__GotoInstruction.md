# CScriptObjectCode__GotoInstruction

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
name is a research label. Callee body `0x00539b00` and
`CScriptObjectCode.cpp.md` / `IScript.cpp.md` /
`CScriptEventNB.cpp.md` / the RestoreSavedState folder /
both CallEvent folders were **not** written.

> Address: `0x00539ae0`

## Contract

`thiscall`. First insn `mov eax, [esp+4]` then
`mov [ecx+0x214], eax` (incoming ECX is `this`; not saved).
One stack dword. One `ret 4` at `0x00539aef`. Body
`0x00539ae0`–`0x00539af1` is 18 bytes, SHA-256
`9f139e635c2dfc955e3e9333ca12b2f122e9f3ae0487e41bbc29a11904340ad1`.
One `E8`, zero `E9`. Fourteen `nop`s after the `ret 4` are
**not** in the body (neighbour `CScriptObjectCode__Run`
starts at `0x00539b00`).

The body writes PC `[this+0x214] = arg0` and `E8`s table
`CScriptObjectCode__Run` `0x00539b00` (`0x00539aea`). That
callee body is **not** this proof.

Three inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x00533898` | already-pinned `IScript__RestoreSavedStateAndGotoInstruction` |
| `0x00538572` | table `CScriptEventNB__UpdateWaypointFollowing` |
| `0x0053868f` | table `IScript__HandleMessage` |

Each host plants `push eax` / `ecx = 0x0089c5e0` before the
`E8`. Zero image encodings of imm `e0 9a 53 00`. Those
hosts are **not** claimed.

Cheapest falsifier: file `0x00139ae0` is not `8b 44 24 04`,
**or** `0x00139aef` is not `c2 04 00`, **or** body SHA-256
is not `9f139e63…0ad1`, **or** `tools/call_xref_scan.py` on
`0x00539ae0` is not the three `E8` above, **or**
`0x00139ae4` is not `89 81 14 02 00 00`, **or**
`0x00139aea` is not `e8 11 00 00 00`, **or** a fourth
inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00539ae0` | `CScriptObjectCode__GotoInstruction` | `8b442404 898114020000 e811000000 c20400` | thiscall; ret 4; 18 B; 1 E8 Run `0x00539b00`; 0 E9; 3 inbound E8. HIGH on ABI, inbound set, `PC = arg; Run()`. **Not** on Run or the hosts. |
