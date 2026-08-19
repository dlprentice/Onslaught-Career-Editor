# CMissionScriptObjectCode__ClearFields_Thunk

Status: active static function note
Last updated: 2026-08-19
Source File: MissionScript / CScriptObjectCode (first gates
only; do not read this as a pin of `CScriptObjectCode.cpp.md`
/ `ScriptObjectCode.cpp.md` / already-pinned
`CMissionScriptObjectCode__ClearFields`)
||| Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches (2506752 equal). The Ghidra database was not opened. Table
name is a research label. Already-pinned ClearFields `0x00539f40`
(`91dcfad8`) / LoadAsync / FUN_00539e10 (`6fb79dad`) /
FUN_00539e30 (`562fda84`) / `CScriptObjectCode.cpp.md` /
children `t_e0fcea14` / `t_d14c8488` were **not** written.
Did not steal those cards.

> Address: `0x00539f30`

## Contract

One instruction. First insn `jmp 0x00539f40` (`e9 0b 00 00 00`).
No `ret` of its own. Body `0x00539f30`–`0x00539f34` is 5
bytes, SHA-256
`ec7d2aa54ab353ae3e298f2752ca2bce4eae1ebdb8c1ddeefde03cd044576859`.
Zero `E8`, one `E9`. Eleven nops after the `jmp` are **not**
in the body (already-pinned neighbour ClearFields starts at
`0x00539f40`). Eleven nops after table `InitFields` `ret`
(`0x00539f24`) through `0x00539f2f` are **not** in the body.

The `E9` target is already-pinned `CMissionScriptObjectCode__ClearFields`
`0x00539f40`. That callee body is **not** this proof. This
body does not write memory.

One inbound `.text` `E8` and zero inbound `E9`: `0x00481b44`
(host does `ecx = [esi+0x30]`, null skips; table
`CHud__ShutDown` `0x00481b00`–`0x00481f3b` is **not**
claimed). Zero image encodings of imm `30 9f 53 00`.

Cheapest falsifier: file `0x00139f30` is not `e9 0b 00 00 00`,
**or** body SHA-256 is not `ec7d2aa5…6859`, **or**
`tools/call_xref_scan.py` on `0x00539f30` is not the one
`E8` at `0x00481b44`, **or** `0x00081b44` is not
`e8 e7 83 0b 00`, **or** a second inbound `E8` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00539f30` | `CMissionScriptObjectCode__ClearFields_Thunk` | `e90b000000` | tail; 5 B; 0 E8 / 1 E9 already-pinned ClearFields; 1 inbound E8. HIGH on ABI, inbound set, `jmp 0x00539f40`. **Not** on ClearFields or CHud. |
