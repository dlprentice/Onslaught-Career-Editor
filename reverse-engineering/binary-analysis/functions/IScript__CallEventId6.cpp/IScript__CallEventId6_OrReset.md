# IScript__CallEventId6_OrReset

Status: active static function note
Last updated: 2026-08-19
Source File: MissionScript / IScript (wrapper only; do not
read this as a pin of `IScript.cpp.md`) | Binary: BEA.exe,
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Callee bodies `0x00539980` / `0x00539990` and
`IScript.cpp.md` were **not** written. Sibling `0x00533660`
is already pinned and was **not** re-done.

> Address: `0x005335a0`

## Contract

`thiscall`. Reads `[ecx+0xc]`. Zero stack args. Bare `ret` at
`0x005335ca`. Body `0x005335a0`–`0x005335ca` is 43 bytes,
SHA-256
`e931fcc0af944df4291c9737ab3b4c88154fdce73e40b97d900aa7d35511654d`.
One `E9` (`0x005335ae` → table `CScriptObjectCode__Reset`
`0x00539980`) when `[0x008a9ac0] == 4`. One `E8`
(`0x005335c5` → table `CScriptObjectCode__CallEvent`
`0x00539990`) after `push 0`, `push 0x0089c528`, `push 6`,
`push [this+0xc]`, `ecx = 0x0089c5e0`. Those callee bodies
and the authored event name are **not** this proof.

One inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x004f4348` | table `CComplexThing__HandleEvent` |

Zero image encodings of imm `a0 35 53 00`. That host is
**not** claimed.

Cheapest falsifier: file `0x001335a0` is not
`83 3d c0 9a 8a 00 04`, **or** `0x001335ca` is not `c3`,
**or** body SHA-256 is not `e931fcc0…654d`, **or**
`tools/call_xref_scan.py` on `0x005335a0` is not the one
`E8` above, **or** `0x001335bd` is not `6a 06`, **or**
`0x001335ae` is not `e9 cd 63 00 00`, **or** a second
inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x005335a0` | `IScript__CallEventId6_OrReset` | `833dc09a8a0004 750a b9e0c58900 e9cd630000 8b410c 6a00 6828c58900 6a06 … e8c6630000 c3` | thiscall; bare ret; 43 B; 1 E9 Reset `0x00539980` if `[0x008a9ac0]==4`; 1 E8 CallEvent `0x00539990` with imm 6; 1 inbound E8. HIGH on ABI, inbound, that cmp, that push 6. **Not** on callee bodies or authored event name. |
