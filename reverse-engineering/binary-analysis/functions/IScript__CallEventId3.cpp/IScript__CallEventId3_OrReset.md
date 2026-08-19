# IScript__CallEventId3_OrReset

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
`IScript.cpp.md` were **not** written. Siblings `0x00533660`
and `0x005335a0` are already pinned and were **not** re-done.

> Address: `0x005337e0`

## Contract

`thiscall`. Reads `[ecx+0xc]`. Zero stack args. Bare `ret` at
`0x0053380a`. Body `0x005337e0`–`0x0053380a` is 43 bytes,
SHA-256
`dc66713395ee0c3d95db18fe193a7fe88e8dfd7cfc474d052772f3cd04a65cf6`.
One `E9` (`0x005337ee` → table `CScriptObjectCode__Reset`
`0x00539980`) when `[0x008a9ac0] == 4`. One `E8`
(`0x00533805` → table `CScriptObjectCode__CallEvent`
`0x00539990`) after `push 0`, `push 0x0089c528`, `push 3`,
`push [this+0xc]`, `ecx = 0x0089c5e0`. Those callee bodies
and the authored event name are **not** this proof.

Five inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x0040c02f` | table `CBattleEngine__StartDieProcess` |
| `0x00417e06` | table `SharedUnitVFunc__HandleType1388Field74Resource_00417df0` |
| `0x004ba810` | table `CMine__VFunc_117_004ba7f0` |
| `0x004f43e1` | table `CComplexThing__AddShutdownEvent` |
| `0x004fd0e9` | table `CUnit__ResetDeploymentGraphAndScheduleEvent` |

Zero image encodings of imm `e0 37 53 00`. Those hosts are
**not** claimed.

Cheapest falsifier: file `0x001337e0` is not
`83 3d c0 9a 8a 00 04`, **or** `0x0013380a` is not `c3`,
**or** body SHA-256 is not `dc667133…5cf6`, **or**
`tools/call_xref_scan.py` on `0x005337e0` is not the five
`E8` above, **or** `0x001337fd` is not `6a 03`, **or**
`0x001337ee` is not `e9 8d 61 00 00`, **or** a sixth
inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x005337e0` | `IScript__CallEventId3_OrReset` | `833dc09a8a0004 750a b9e0c58900 e98d610000 8b410c 6a00 6828c58900 6a03 … e886610000 c3` | thiscall; bare ret; 43 B; 1 E9 Reset `0x00539980` if `[0x008a9ac0]==4`; 1 E8 CallEvent `0x00539990` with imm 3; 5 inbound E8. HIGH on ABI, inbound set, that cmp, that push 3. **Not** on callee bodies or authored event name. |
