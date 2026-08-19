# IScript__RestoreSavedStateAndGotoInstruction

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
label. Callee bodies `0x00539910` / `0x004e5bd0` / `0x00539980`
/ `0x00539ae0` and `IScript.cpp.md` / `CComplexThing.cpp.md`
were **not** written. Already-pinned neighbour `0x00533810` was
**not** re-done.

> Address: `0x00533840`

## Contract

`thiscall`. First insn `push esi` / `mov esi, ecx`. Zero
stack args. Two bare `ret` sites (`0x00533891` after Reset,
`0x0053389e` after GotoInstruction / the early-out). Body
`0x00533840`–`0x0053389e` is 95 bytes, SHA-256
`5cade34e885e556a01d56412e61e9d9c80a98d54740830ee66db6a926d61cb7c`.
Four `E8`, zero `E9`. One `nop` after the last `ret` is
**not** in the body (neighbour `IScript__SetPlayerLives`
starts at `0x005338a0`).

If `[esi+0x38] == 0`, the body jumps to `0x0053389d`
(`pop esi; ret`) with no calls. Otherwise it `push`es that
dword, sets `ecx = 0x0089c5e0`, and `E8`s table
`CScriptObjectCode__CopyState` `0x00539910` (`0x00533850`).
Then `lea ecx, [esi+0x28]`, `push [esi+0x38]`, `E8` table
`CSPtrSet__Remove` `0x004e5bd0` (`0x0053385c`). If
`[esi+0x38]` is still live, `push 1` / `call [vtable+4]`.
Then `[esi+0x38] = 0`.

If `[0x008a9ac0] == 4`, `ecx = 0x0089c5e0` and `E8` table
`CScriptObjectCode__Reset` `0x00539980` (`0x0053388b`).
Else `push [0x0089c7f4]`, `ecx = 0x0089c5e0`, `E8` table
`CScriptObjectCode__GotoInstruction` `0x00539ae0`
(`0x00533898`). Those callee bodies are **not** this proof.

One inbound `.text` `E8`, zero `E9`:

| site | host (label only) |
| --- | --- |
| `0x004f45a7` | table `CComplexThing__FinishedPlayingCurrentAnimation` |

The host plants `ecx = [this+0x74]` then `test ecx` /
`je` / `E8`, and returns `EAX = 1`. Zero image encodings of
imm `40 38 53 00`. That host is **not** claimed.

Cheapest falsifier: file `0x00133840` is not `56 8b f1`,
**or** `0x0013389e` is not `c3`, **or** body SHA-256 is not
`5cade34e…cb7c`, **or** `tools/call_xref_scan.py` on
`0x00533840` is not the one `E8` above, **or**
`0x00133843` is not `8b 46 38`, **or** `0x00133850` is not
`e8 bb 60 00 00`, **or** `0x0013385c` is not
`e8 6f 23 fb ff`, **or** `0x0013386f` is not
`c7 46 38 00 00 00 00`, **or** `0x0013388b` is not
`e8 f0 60 00 00`, **or** `0x00133898` is not
`e8 43 62 00 00`, **or** a second inbound `E8`/`E9` exists.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00533840` | `IScript__RestoreSavedStateAndGotoInstruction` | `56 8bf1 8b4638 85c0 7453 50 b9e0c58900 e8bb600000 … e86f23fbff … c7463800000000 … e8f0600000 c3 / e843620000 c3` | thiscall; bare ret ×2; 95 B; 4 E8 CopyState `0x00539910` / Remove `0x004e5bd0` / Reset `0x00539980` / GotoInstruction `0x00539ae0`; 0 E9; 1 inbound E8. HIGH on ABI, inbound set, `[+0x38]` early-out and store-0, cmp-4 split. **Not** on callee bodies or the host. |
