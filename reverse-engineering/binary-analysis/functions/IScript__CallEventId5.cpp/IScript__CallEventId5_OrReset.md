# IScript__CallEventId5_OrReset

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
`IScript.cpp.md` / `CComplexThing.cpp.md` /
`CScriptObjectCode.cpp.md` were **not** written.

> Address: `0x00533660`

## Contract

`thiscall`. Reads `[ecx+0xc]`. Zero stack args. Bare `ret` at
`0x0053368a`. Body `0x00533660`–`0x0053368a` is 43 bytes,
SHA-256
`f7aad3433a7d1e634ddb0cd1cc243225a1e3567e7adf89122a6341093e5c3ca7`.
One `E9` (`0x0053366e` → table `CScriptObjectCode__Reset`
`0x00539980`) when `[0x008a9ac0] == 4`. One `E8`
(`0x00533685` → table `CScriptObjectCode__CallEvent`
`0x00539990`) after `push 0`, `push 0x0089c528`, `push 5`,
`push [this+0xc]`, `ecx = 0x0089c5e0`. Those callee bodies
and the authored event name are **not** this proof. Five
`nop`s after the `ret` are **not** in the body.

Three inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x0044cd98` | table `CFeature__VFunc_50_0044cd80` |
| `0x004f444d` | table `CComplexThing__StartDieProcess` |
| `0x004fd1e8` | table `CUnit__MarkDestroyedAndCleanupLinks` |

Zero image encodings of imm `60 36 53 00`. Those hosts are
**not** claimed. Zero `.text` `E8`/`E9` land on the inner
`0x00533685` call site.

Cheapest falsifier: file `0x00133660` is not
`83 3d c0 9a 8a 00 04`, **or** `0x0013368a` is not `c3`,
**or** body SHA-256 is not `f7aad343…3ca7`, **or**
`tools/call_xref_scan.py` on `0x00533660` is not the three
`E8` above, **or** `0x0013367d` is not `6a 05`, **or**
`0x0013366e` is not `e9 0d 63 00 00`, **or** a fourth
inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00533660` | `IScript__CallEventId5_OrReset` | `833dc09a8a0004 750a b9e0c58900 e90d630000 8b410c 6a00 6828c58900 6a05 … e806630000 c3` | thiscall; bare ret; 43 B; 1 E9 Reset `0x00539980` if `[0x008a9ac0]==4`; 1 E8 CallEvent `0x00539990` with imm 5; 3 inbound E8. HIGH on ABI, inbound set, that cmp, that push 5. **Not** on callee bodies or authored event name. |
